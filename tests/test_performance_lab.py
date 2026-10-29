"""v0.12: cited performance sequences, provenance and page-quality audit."""
import json
import re
import unittest
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'site'

class PerformanceLabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/'data/performance_evidence.json').read_text(encoding='utf-8'))
        cls.release=json.loads((SITE/'assets/performance-lab.json').read_text(encoding='utf-8'))
        cls.cat=json.loads((SITE/'assets/catalog.json').read_text(encoding='utf-8'))
        cls.seqs=cls.data['sequences']

    def test_reviewed_provenance_data_matches_public_source(self):
        self.assertEqual(self.data,self.release)
        self.assertEqual(self.data['version'],'0.12')
        self.assertEqual(self.data['reviewed_on'],'2026-10-29')
        self.assertEqual(len(self.seqs),12)
        self.assertEqual(len(self.data['sources']),4)

    def test_every_study_uses_valid_existing_show_and_cited_source(self):
        shows={h['id'] for h in self.cat['historical_shows']}
        sources=self.data['sources']
        self.assertEqual(len(set(s['id'] for s in self.seqs)),12)
        for s in self.seqs:
            self.assertIn(s['show_id'],shows)
            self.assertIn(s['evidence_scope'],{'release_excerpt','setlist_excerpt'})
            self.assertTrue(s['source_ids'])
            self.assertTrue(all(i in sources for i in s['source_ids']))
            self.assertTrue(s['editorial_note'])

    def test_citations_are_trustworthy_url_shapes(self):
        for name,src in self.data['sources'].items():
            url=urlsplit(src['url'])
            self.assertEqual(url.scheme,'https',name)
            self.assertTrue(url.hostname)
            self.assertNotIn('@',url.netloc)
            self.assertIn(src['type'],{'artist_official_discography','label_official_release','community_curated_setlist','artist_official_release'})

    def test_track_positions_and_marker_notation(self):
        self.assertEqual(sum(len(s['entries']) for s in self.seqs),62)
        self.assertEqual(sum(bool(t['source_transition_after']) for s in self.seqs for t in s['entries']),18)
        for s in self.seqs:
            self.assertEqual([t['order'] for t in s['entries']],list(range(1,len(s['entries'])+1)))
            self.assertIsNone(s['entries'][-1]['source_transition_after'])
            self.assertTrue(all(t['source_transition_after'] in ('>','->',None) for t in s['entries']))

    def test_cornell_stephen_reprise_preserved_as_distinct_track_positions(self):
        seq=next(s for s in self.seqs if s['id']=='gd-1977-05-08-stephen')
        self.assertEqual([x['song_title'] for x in seq['entries']],['St. Stephen','Not Fade Away','St. Stephen','Morning Dew'])
        self.assertEqual(sum(x['song_title']=='St. Stephen' for x in seq['entries']),2)

    def test_cornell_scarlet_fire_transition_cited(self):
        seq=next(s for s in self.seqs if s['id']=='gd-1977-05-08-scarlet')
        self.assertEqual([x['song_title'] for x in seq['entries']],['Scarlet Begonias','Fire on the Mountain'])
        self.assertEqual(seq['entries'][0]['source_transition_after'],'>')
        self.assertEqual(seq['source_ids'],['rhino_2017'])

    def test_phish_differentiates_arrow_notation(self):
        seq=next(s for s in self.seqs if s['id']=='phish-1995-12-31-delay')
        self.assertEqual(seq['entries'][0]['source_transition_after'],'->')
        self.assertEqual(seq['entries'][1]['song_title'],'Digital Delay Loop Jam')

    def test_guests_are_per_song_and_not_global_lineups(self):
        guests=[(s,g) for s in self.seqs for g in s['documented_guests']]
        self.assertEqual(len(guests),2)
        self.assertEqual({g['name'] for _,g in guests},{'Elvin Bishop','Tom Marshall'})
        for s,g in guests:
            self.assertIn(g['on_song'],[x['song_title'] for x in s['entries']])
            self.assertTrue(all(x in self.data['sources'] for x in g['source_ids']))

    def test_recording_lineage_is_separate_from_recording_reference(self):
        chains=self.data['recording_lineages']
        self.assertEqual(len(chains),2)
        self.assertGreaterEqual(len(chains[1]['steps']),5)
        self.assertIn('Plangent',str(chains[1]['steps']))
        self.assertIn('not every circulating tape',chains[1]['limitations'].lower())

    def test_all_studies_are_rendered_and_link_to_canonical_show(self):
        for s in self.seqs:
            html=(SITE/'performance-lab'/s['id']/'index.html').read_text(encoding='utf-8')
            self.assertIn('href="/shows/'+s['show_id']+'/',html)
            self.assertIn(s['source_ids'][0],self.data['sources'])
            self.assertEqual(html.count('class="pl-tracklist"'),1)
            self.assertEqual(html.count('class="pl-transition"'),sum(bool(e['source_transition_after']) for e in s['entries']))

    def test_original_concert_dossiers_include_performance_lab_links(self):
        for s in self.seqs:
            html=(SITE/'shows'/s['show_id']/'index.html').read_text(encoding='utf-8')
            self.assertIn('/performance-lab/'+s['id']+'/',html)

    def test_index_cards_work_without_javascript(self):
        html=(SITE/'performance-lab/index.html').read_text(encoding='utf-8')
        self.assertEqual(html.count('class="pl-card"'),12)
        self.assertIn('id="pl-search"',html)
        self.assertIn('id="pl-count" aria-live="polite"',html)
        self.assertIn('source-backed',html)

    def test_global_site_navigation_and_404_are_corrected(self):
        for f in SITE.rglob('*.html'):
            h=f.read_text(encoding='utf-8')
            self.assertIn('href="#ja-main"',h,str(f))
            self.assertIn('id="ja-main"',h,str(f))
            if f!=SITE/'index.html':
                self.assertIn('aria-label="Archive sections"',h,str(f))
                self.assertIn('href="/performance-lab/"',h,str(f))
        page=(SITE/'404.html').read_text(encoding='utf-8')
        self.assertIn('name="robots" content="noindex"',page)
        self.assertIn('href="/"',page)

    def test_public_report_and_audit_show_clean_build(self):
        report=json.loads((SITE/'assets/build_report.json').read_text())
        audit=json.loads((SITE/'assets/site_audit.json').read_text())
        self.assertEqual(report['version'],'0.13')
        self.assertEqual(report['performance_sequences'],12)
        self.assertEqual(audit['issues'],0)
        self.assertGreaterEqual(audit['html_pages_inspected'],673)
        self.assertTrue(audit['audit_limitations'])

    def test_no_unsupported_media_or_review_queue_leaks(self):
        self.assertFalse(list(SITE.rglob('*.mp3')))
        self.assertFalse(list(SITE.rglob('*.flac')))
        self.assertFalse(list(SITE.rglob('*.sqlite')))
        self.assertFalse(list(SITE.rglob('research_queue.json')))
        self.assertNotIn('synthetic:',json.dumps(self.release))

if __name__=='__main__':unittest.main()
