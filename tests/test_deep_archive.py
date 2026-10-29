"""v0.11 editorial quality, source traceability and cross-feature integrity."""
from pathlib import Path
import json
import os
import re
import unittest
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'site'

class DeepArchiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc=json.loads((ROOT/'data/research_dossiers.json').read_text())
        cls.public=json.loads((SITE/'assets/deep-archive.json').read_text())
        cls.dossiers=cls.doc['dossiers']
        cls.sources=cls.doc['sources']
        cls.catalog=json.loads((SITE/'assets/catalog.json').read_text())

    def test_researched_dossiers_are_complete_and_public(self):
        self.assertEqual(self.doc,self.public)
        self.assertEqual(len(self.dossiers),22)
        self.assertEqual(sum(d['kind']=='artist' for d in self.dossiers),10)
        self.assertEqual(sum(d['kind']=='show' for d in self.dossiers),12)
        self.assertEqual(sum(len(d['facts']) for d in self.dossiers),110)

    def test_every_fact_has_explicit_named_source(self):
        for d in self.dossiers:
            for fact in d['facts']:
                self.assertTrue(fact['source_ids'])
                self.assertTrue(all(sid in self.sources for sid in fact['source_ids']))
                self.assertTrue(fact['period'] and fact['topic'] and fact['text'])
                self.assertNotIn('<',fact['text'])

    def test_all_citation_links_https_no_unknown_fields(self):
        for sid,s in self.sources.items():
            url=urlsplit(s['url'])
            self.assertEqual(url.scheme,'https',sid)
            self.assertTrue(url.netloc)
            self.assertNotIn('@',url.netloc)
            self.assertTrue(s['title'])
            self.assertIn(s['classification'],{'artist-official','label-official','community-archive','archived-interview'})

    def test_known_catalog_keys_only(self):
        entities={e['id'] for e in self.catalog['entities']}
        shows={h['id'] for h in self.catalog['historical_shows']}
        keys=[(d['kind'],d['id']) for d in self.dossiers]
        self.assertEqual(len(keys),len(set(keys)))
        for d in self.dossiers:
            self.assertIn(d['id'],entities if d['kind']=='artist' else shows)

    def test_each_dossier_has_original_record_and_bibliography(self):
        for d in self.dossiers:
            sub='artists' if d['kind']=='artist' else 'shows'
            html=(SITE/'deep-archive'/sub/d['id']/'index.html').read_text()
            self.assertIn('Source bibliography',html)
            self.assertIn('Questions still open',html)
            self.assertIn('href="/'+sub+'/'+d['id']+'/',html)
            self.assertEqual(html.count('class="da-claim"'),len(d['facts']))
            for f in d['facts']:
                self.assertIn(f['text'].replace('&','&amp;').replace('’','’')[:28],html)

    def test_canonical_artist_show_pages_have_approved_teaser(self):
        for d in self.dossiers:
            sub='artists' if d['kind']=='artist' else 'shows'
            html=(SITE/sub/d['id']/'index.html').read_text()
            self.assertIn('RESEARCHED CONTEXT',html)
            self.assertIn('/deep-archive/'+sub+'/'+d['id']+'/',html)

    def test_source_metadata_uncertainties_explicit(self):
        by_id={d['id']:d for d in self.dossiers}
        l=' '.join(f['text'] for f in by_id['abb-1970-04-04']['facts'])
        self.assertIn('April 11',l)
        self.assertIn('1990',l)
        atl=' '.join(f['text'] for f in by_id['abb-1970-07-05']['facts'])
        self.assertIn('July 6',atl)
        self.assertIn('3:50',atl)

    def test_no_synthetic_research_or_private_queue_in_public_site(self):
        self.assertFalse(list(SITE.rglob('*.sqlite')))
        self.assertFalse(list(SITE.rglob('research_queue.json')))
        self.assertFalse(list(SITE.rglob('*.py')))
        self.assertNotIn('synthetic:',json.dumps(self.public))

    def test_sitemap_contains_all_new_pages_and_no_duplicates(self):
        ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
        loc=[x.text for x in ET.parse(SITE/'sitemap.xml').findall('s:url/s:loc',ns)]
        self.assertEqual(len(loc),len(set(loc)))
        origin=os.environ.get('JAM_ARCHIVE_ORIGIN','https://thejamarchive.org').rstrip('/')
        self.assertIn(origin+'/deep-archive/',loc)
        for d in self.dossiers:
            sub='artists' if d['kind']=='artist' else 'shows'
            self.assertIn(origin+'/deep-archive/'+sub+'/'+d['id']+'/',loc)

    def test_four_added_release_pointers_are_specific_and_reviewed(self):
        r=json.loads((ROOT/'data/approved_recordings.json').read_text())['recordings']
        self.assertEqual(len(r),4)
        for x in r:
            self.assertEqual(x['reviewed_at'],'2026-10-29')
            self.assertTrue(len(x['review_note'])>30)
            self.assertTrue(x['source_url'].startswith('https://'))
        exported=json.loads((SITE/'assets/recordings.json').read_text())['items']
        self.assertEqual(len(exported),21)
        self.assertTrue(any(x['show_id']=='abb-1971-03-12-early' for x in exported))

    def test_site_navigation_exposes_editorial_archive(self):
        self.assertIn('deep-archive/index.html',(SITE/'index.html').read_text())
        for path in ('connections/index.html','recordings/index.html','song-paths/index.html','time-machine/index.html'):
            self.assertIn('href="/deep-archive/"',(SITE/path).read_text())

    def test_index_usability_without_javascript(self):
        html=(SITE/'deep-archive/index.html').read_text()
        self.assertEqual(html.count('class="da-tile"'),22)
        self.assertIn('id="da-query"',html)
        self.assertIn('id="da-filter"',html)
        self.assertIn('class="da-cards"',html)
        self.assertIn('.da-tile[hidden]{display:none}',(SITE/'assets/deep-archive.css').read_text())

    def test_meta_report_counts_match(self):
        report=json.loads((SITE/'assets/build_report.json').read_text())
        self.assertEqual(report['version'],'0.13')
        self.assertEqual(report['deep_archive_assertions'],110)
        self.assertEqual(report['deep_archive_dossiers'],22)
        self.assertEqual(report['deep_archive_sources'],31)
        self.assertEqual(report['recording_references'],21)

    def test_build_no_external_calls(self):
        code=(ROOT/'build_v011.py').read_text()
        for phrase in ('requests.get(', 'urlopen(', 'urllib.request', 'http.client', 'subprocess.run([\'curl\''):
            self.assertNotIn(phrase,code)
