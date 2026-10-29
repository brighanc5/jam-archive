"""Test release completeness, music claims, and Song Paths navigation."""
from pathlib import Path
from collections import Counter
import json
import re
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'

class SongPathTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cat = json.loads((SITE / 'assets/catalog.json').read_text(encoding='utf-8'))
        cls.path_data = json.loads((SITE / 'assets/song-paths.json').read_text(encoding='utf-8'))
        cls.html = (SITE / 'song-paths/index.html').read_text(encoding='utf-8')
        cls.shows = {h['id']: h for h in cls.cat['historical_shows']}

    def test_release_is_complete(self):
        self.assertIn('v0.14', (ROOT / 'RELEASE_VERSION.txt').read_text())
        for file in ('build_v09.py', 'song_paths.css', 'song_paths.js',
                     'scripts/doctor.py', '.github/workflows/verify-static.yml'):
            self.assertTrue((ROOT / file).is_file(), file)

    def test_song_counts_are_derived_from_documented_excerpts(self):
        counts = Counter(s for h in self.shows.values() for s in h['songs'])
        self.assertEqual((len(counts), sum(counts.values())), (53, 106))
        self.assertEqual(len(self.path_data['songs']), len(counts))
        for s in self.path_data['songs']:
            self.assertEqual(s['documented_appearances'], counts[s['title']])

    def test_no_dangling_shows_or_song_pages(self):
        for s in self.path_data['songs']:
            self.assertTrue((SITE / 'songs' / s['slug'] / 'index.html').is_file())
            for show_id in s['show_ids']:
                self.assertIn(show_id, self.shows)
                self.assertIn(s['title'], self.shows[show_id]['songs'])
                self.assertTrue((SITE / 'shows' / show_id / 'index.html').is_file())

    def test_co_indexed_songs_share_show_ids(self):
        songs = {x['title']: x for x in self.path_data['songs']}
        for s in songs.values():
            for other in s['co_indexed_titles']:
                self.assertIn(other['title'], songs)
                common = len(set(s['show_ids']) & set(songs[other['title']]['show_ids']))
                self.assertEqual(common, other['shared_shows'])
                self.assertGreaterEqual(common, 2)

    def test_known_coverage_gaps_remain_honest(self):
        self.assertEqual(len([h for h in self.shows.values() if not h['songs']]), 5)
        self.assertNotIn('inferred segues', self.html.lower().replace('no invented segues', ''))
        self.assertIn('does not establish a segue', self.html)
        self.assertIn('not complete setlists', self.path_data['scope'])

    def test_all_song_cards_server_rendered(self):
        self.assertEqual(self.html.count('class="sp-card"'), 53)
        self.assertEqual(self.html.count('class="sp-badge"'), 53)
        self.assertIn('id="sp-search"', self.html)
        self.assertIn('id="sp-repeats"', self.html)
        self.assertIn('id="sp-sort"', self.html)
        self.assertIn('sp-card[hidden]', (SITE / 'assets/song-paths.css').read_text())

    def test_song_pages_link_back_to_pathways(self):
        for s in self.path_data['songs']:
            html = (SITE / 'songs' / s['slug'] / 'index.html').read_text()
            self.assertIn('../../song-paths/index.html', html)

    def test_home_and_other_explorers_link_to_song_paths(self):
        for page in ('index.html','time-machine/index.html','recordings/index.html'):
            self.assertTrue('song-paths/index.html' in (SITE / page).read_text() or 'href="/song-paths/"' in (SITE / page).read_text(), page)
        self.assertTrue((SITE / 'assets/song-paths.js').is_file())

    def test_published_json_does_not_contain_internal_review_data(self):
        text = (SITE / 'assets/song-paths.json').read_text()
        for banned in ('research_queue','review_note','credentials','private_key'):
            self.assertNotIn(banned, text)
        self.assertNotIn('<script src="https://', self.html)

    def test_release_report_and_sitemap(self):
        report = json.loads((SITE / 'assets/build_report.json').read_text())
        self.assertEqual(report['version'], '0.14')
        self.assertEqual(report['song_documented_appearances'], 106)
        self.assertEqual(report['song_titles_indexed'], 53)
        ns = {'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
        locs = [x.text for x in ET.parse(SITE / 'sitemap.xml').findall('s:url/s:loc', ns)]
        self.assertEqual(sum(u.endswith('/song-paths/') for u in locs), 1)

if __name__ == '__main__':
    unittest.main()
