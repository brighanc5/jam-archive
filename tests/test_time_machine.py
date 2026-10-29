"""v0.8: source provenance, historical honesty, and Time Machine integration."""
import json
import sys
import unittest
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from history_seed import H, R

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'site'

class TimelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cat=json.loads((SITE/'assets/catalog.json').read_text(encoding='utf-8'))
        cls.shows={x['id']:x for x in cls.cat['historical_shows']}
        cls.sources={x['id']:x for x in cls.cat['recording_sources']}
        cls.page=(SITE/'time-machine/index.html').read_text(encoding='utf-8')

    def test_dataset_counts_and_identity(self):
        self.assertEqual(len(self.shows),25)
        self.assertGreaterEqual(len(self.sources),17)
        self.assertEqual(len([x for x in self.shows.values() if x['artist']=='The Allman Brothers Band']),16)
        self.assertEqual(len([x for x in self.shows.values() if x['artist']=='Grateful Dead']),7)
        self.assertEqual(len(set(self.shows)),25)

    def test_no_inferred_setlists(self):
        missing=[x for x in self.shows.values() if not x['songs']]
        self.assertEqual(len(missing),5)
        for row in missing:
            self.assertIn('Setlist not established',row['setlist_scope'])
            html=(SITE/'shows'/row['id']/'index.html').read_text(encoding='utf-8')
            self.assertIn('No source-confirmed songs indexed',html)

    def test_contested_dates_disclosed_publicly(self):
        for id, phrase in [('abb-1970-04-04','April 11'),('abb-1970-07-05','July 6')]:
            self.assertIn(phrase,self.shows[id]['notes'])
            self.assertIn(phrase,(SITE/'shows'/id/'index.html').read_text(encoding='utf-8'))

    def test_all_external_show_sources_are_official(self):
        for row in self.shows.values():
            host=urlsplit(row['source_url']).hostname
            if row['id'] in {x['id'] for x in H[9:]}:
                self.assertIn(host,{'allmanbrothersband.com','www.dead.net'})

    def test_recordings_are_distinct_from_show_sources(self):
        for record in self.sources.values():
            self.assertIn(record['show_id'],self.shows)
            self.assertTrue(record['source_url'].startswith('https://'))
            self.assertIn(record['source_verified'].split('_')[0],{'page','editorially'})
        self.assertEqual(len([x for x in self.sources.values() if x['id'].startswith('gd-get-shown-the-light')]),4)
        self.assertTrue(all(self.sources[x]['source_verified']=='page_link_checked_2026-10-28' for x in self.sources if x.startswith(('abb-ludlow-1970','abb-atlanta-pop-','abb-last-duane-show-','gd-get-shown-the-light-'))))

    def test_time_machine_cards_and_source_links(self):
        self.assertEqual(self.page.count('class="tm-show"'),22)
        self.assertIn('href="../shows/abb-1970-07-05/index.html"',self.page)
        self.assertIn('href="../shows/gd-1977-05-08/index.html"',self.page)
        self.assertIn('data-sources="0"',self.page)
        self.assertIn('Setlist not established',self.page)
        self.assertIn('id="tm-artist"',self.page)
        self.assertIn('id="tm-recorded"',self.page)

    def test_navigation_and_assets(self):
        self.assertIn('time-machine/index.html',(SITE/'index.html').read_text(encoding='utf-8'))
        self.assertIn('href="/time-machine/"',(SITE/'recordings/index.html').read_text(encoding='utf-8'))
        self.assertTrue((SITE/'assets/time-machine.js').is_file())
        self.assertTrue((SITE/'assets/time-machine.css').is_file())
        self.assertTrue((SITE/'time-machine/index.html').is_file())

    def test_no_copyright_media_in_public_site(self):
        self.assertFalse([p for p in SITE.rglob('*') if p.suffix.lower() in ('.mp3','.wav','.flac','.mp4')])

if __name__=='__main__':unittest.main()
