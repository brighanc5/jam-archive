"""v0.10: relationship provenance, routes, and graph accuracy tests."""
from pathlib import Path
from collections import defaultdict, deque
from html.parser import HTMLParser
from urllib.parse import urlsplit
import json
import re
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'


class FamilyTreeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cat = json.loads((SITE / 'assets/catalog.json').read_text(encoding='utf-8'))
        cls.graph = json.loads((SITE / 'assets/connections.json').read_text(encoding='utf-8'))
        cls.html = (SITE / 'connections/index.html').read_text(encoding='utf-8')
        cls.nodes = {n['id']: n for n in cls.graph['nodes']}
        cls.adj = defaultdict(set)
        for edge in cls.graph['edges']:
            cls.adj[edge['from']].add(edge['to'])
            cls.adj[edge['to']].add(edge['from'])

    def test_graph_only_contains_verified_source_relationships(self):
        src = {(r['from'], r['to'], r['type'], r['source_url']) for r in self.cat['relationships'] if r['verification'] == 'verified'}
        out = {(r['from'], r['to'], r['type'], r['source_url']) for r in self.graph['edges']}
        self.assertEqual(src, out)
        self.assertEqual(len(out), 52)

    def test_pending_relationships_never_leak_into_graph(self):
        src = {(r['from'], r['to'], r['type']) for r in self.cat['relationships'] if r['verification'] != 'verified'}
        out = {(r['from'], r['to'], r['type']) for r in self.graph['edges']}
        self.assertFalse(src.intersection(out))
        self.assertNotIn('needs_review', (SITE / 'assets/connections.json').read_text(encoding='utf-8'))
        self.assertEqual(len(src), 25)

    def test_source_links_are_safe_https_urls(self):
        for r in self.graph['edges']:
            p = urlsplit(r['source_url'])
            self.assertEqual(p.scheme, 'https')
            self.assertTrue(p.netloc)
            self.assertNotIn('@', p.netloc)

    def test_all_endpoints_and_profiles_exist(self):
        for r in self.graph['edges']:
            for k in ('from','to'):
                self.assertIn(r[k], self.nodes)
                self.assertTrue((SITE / 'artists' / r[k] / 'index.html').is_file())

    def test_verified_component_sizes(self):
        self.assertEqual(len(self.nodes), 55)
        self.assertEqual(sorted([c['size'] for c in self.graph['components']], reverse=True), [21,15,5,4,3,3,2,2])
        for comp in self.graph['components']:
            self.assertEqual(comp['size'], len(comp['members']))
            for node in comp['members']:
                self.assertEqual(self.nodes[node]['component'], comp['id'])

    def test_sample_connections_are_truly_reachable(self):
        for start, end in [('trey-anastasio','les-claypool'),('derek-trucks','warren-haynes'),('joe-russo','leo-kottke'),('oteil-burbridge','john-mayer')]:
            seen = {start}; q = deque([start])
            while q:
                for node in self.adj[q.popleft()]:
                    if node not in seen:
                        seen.add(node);q.append(node)
            self.assertIn(end, seen)

    def test_unconnected_groups_are_not_silently_bridged(self):
        self.assertNotEqual(self.nodes['trey-anastasio']['component'], self.nodes['derek-trucks']['component'])
        self.assertIn('different verified network groups', (ROOT / 'connections.js').read_text())

    def test_no_claim_that_paths_prove_collaboration(self):
        self.assertIn('does <strong>not</strong> prove musicians met', self.html)
        self.assertIn('not proven sit-ins', self.graph['scope'])
        self.assertIn('source_url', json.dumps(self.graph))

    def test_server_rendered_source_ledger_is_complete(self):
        self.assertEqual(self.html.count('class="cx-ledger-item"'), 52)
        self.assertEqual(self.html.count('class="cx-cite"'), 52)
        self.assertIn('id="cx-ledger-search"', self.html)
        self.assertIn('id="cx-network"', self.html)
        self.assertIn('id="cx-path"', self.html)
        self.assertIn('id="cx-data"', self.html)

    def test_script_data_matches_public_export(self):
        embedded = re.search(r'<script id="cx-data" type="application/json">(.*?)</script>', self.html, flags=re.S)
        self.assertIsNotNone(embedded)
        self.assertEqual(json.loads(embedded.group(1)), self.graph)
        self.assertNotIn('<script src="https://', self.html)

    def test_navigation_home_and_artist_profiles(self):
        for rel in ('index.html','song-paths/index.html','time-machine/index.html','recordings/index.html'):
            self.assertIn('connections/index.html', (SITE / rel).read_text(encoding='utf-8'))
        for artist in self.cat['entities']:
            file = SITE / 'artists' / artist['id'] / 'index.html'
            text = file.read_text(encoding='utf-8')
            if artist['id'] in self.nodes:
                self.assertIn('connections/index.html?artist='+artist['id'], text)
            else:
                self.assertIn('connections/index.html', text)
                self.assertNotIn('connections/index.html?artist=', text)

    def test_nested_404_navigation_is_root_absolute(self):
        content = (SITE / '404.html').read_text(encoding='utf-8')
        self.assertIn('href="/assets/detail.css"', content)
        self.assertIn('href="/connections/"', content)
        self.assertNotIn('href="index.html"', content)
        self.assertNotIn('href="contribute/index.html"', content)
        self.assertIn('content="noindex"', content)

    def test_sitemap_report_and_release_marker(self):
        report = json.loads((SITE / 'assets/build_report.json').read_text(encoding='utf-8'))
        self.assertEqual(report['version'], '0.11')
        self.assertEqual(report['verified_relationships'], 52)
        self.assertEqual(report['graph_entities'], 55)
        self.assertEqual(report['graph_components'], 8)
        self.assertEqual(report['unverified_relationships_excluded'], 25)
        self.assertIn('v0.11', (ROOT / 'RELEASE_VERSION.txt').read_text())
        ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        locs = [x.text for x in ET.parse(SITE / 'sitemap.xml').findall('s:url/s:loc',ns)]
        self.assertEqual(len([x for x in locs if x.endswith('/connections/')]), 1)


if __name__ == '__main__':
    unittest.main()
