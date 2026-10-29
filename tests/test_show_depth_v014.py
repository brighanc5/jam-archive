"""v0.14 show-study source boundaries, evidence fidelity, and route regression tests."""
from pathlib import Path
from urllib.parse import urlsplit
from collections import Counter
import json,re,unittest

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'site'
DATA=json.loads((ROOT/'data/show_depth_v014.json').read_text(encoding='utf-8'))
CAT=json.loads((SITE/'assets/catalog.json').read_text(encoding='utf-8'))
R=json.loads((SITE/'assets/build_report.json').read_text(encoding='utf-8'))
STUDIES=DATA['studies']

class ShowDepthTests(unittest.TestCase):
 def test_release_data_and_aggregate_counts(self):
  self.assertEqual(DATA['version'],'0.14')
  self.assertEqual(len(STUDIES),17)
  self.assertEqual(len(DATA['sources']),13)
  self.assertEqual(R['show_depth_studies'],17)
  self.assertEqual(R['show_depth_track_positions'],238)
  self.assertEqual(R['show_depth_repertoire_titles'],158)
  self.assertEqual(R['show_depth_source_transitions'],60)
  self.assertEqual(R['show_depth_guest_credits'],3)
  self.assertEqual(R['version'],'0.14')
 def test_all_sources_are_https_and_declared(self):
  for id,source in DATA['sources'].items():
   parsed=urlsplit(source['url'])
   self.assertEqual(parsed.scheme,'https',id)
   self.assertTrue(parsed.hostname,id)
   self.assertNotIn('@',parsed.netloc)
  for s in STUDIES:
   self.assertTrue(s['source_ids'])
   self.assertTrue(set(s['source_ids']) <= set(DATA['sources']))
 def test_four_artist_eras_represented(self):
  self.assertEqual(Counter(s['artist_id'] for s in STUDIES),{'the-allman-brothers-band':5,'grateful-dead':4,'phish':4,'goose':4})
 def test_set_positions_are_sequential_and_transition_is_source_notation(self):
  for s in STUDIES:
   for section in s['sections']:
    tracks=section['tracks']
    self.assertEqual([e['position'] for e in tracks],list(range(1,len(tracks)+1)))
    self.assertIsNone(tracks[-1]['transition_after'])
    for track in tracks:
     self.assertTrue(track['title'])
     self.assertIn(track['transition_after'],(None,'>','->'))
 def test_guest_credits_explicitly_song_scoped(self):
  by_id={s['id']:s for s in STUDIES}
  abb=by_id['abb-1971-03-13-late']
  self.assertEqual([(g['name'],g['on_title']) for g in abb['documented_guests']],[('Elvin Bishop','Drunken Hearted Boy')])
  phish=by_id['phish-1997-11-16']
  self.assertEqual({g['on_title'] for g in phish['documented_guests']},{'Scent of a Mule','Poor Heart'})
  self.assertTrue(all(not s['documented_guests'] for s in STUDIES if s['id'] not in (abb['id'],phish['id'])))
 def test_every_guest_has_title_in_that_show_and_original_source(self):
  for s in STUDIES:
   titles={t['title'] for section in s['sections'] for t in section['tracks']}
   for guest in s['documented_guests']:
    self.assertIn(guest['on_title'],titles)
    self.assertTrue(set(guest['source_ids']) <= set(s['source_ids']))
 def test_allman_four_march_performances_are_distinct(self):
  ids={s['id'] for s in STUDIES}
  self.assertTrue({'abb-1971-03-12-early','abb-1971-03-12-late','abb-1971-03-13-early','abb-1971-03-13-late','abb-1971-06-27'}<=ids)
  late=next(s for s in STUDIES if s['id']=='abb-1971-03-13-late')
  self.assertIn('discs 4 and 5',late['context'])
 def test_goose_original_band_issued_references(self):
  for s in STUDIES:
   if s['artist_id']!='goose':continue
   self.assertEqual(s['evidence_scope'],'artist_official_setlist_and_release')
   self.assertTrue(s['official_recording'])
   url=DATA['sources'][s['official_recording']['source_id']]['url']
   self.assertTrue(url.startswith('https://goosetheband.bandcamp.com/album/'))
 def test_cornell_repeated_song_not_deduplicated(self):
  show=next(s for s in STUDIES if s['id']=='gd-1977-05-08')
  titles=[t['title'] for sec in show['sections'] for t in sec['tracks']]
  self.assertEqual(titles.count('St. Stephen'),2)
 def test_dayton_repeated_song_not_deduplicated(self):
  show=next(s for s in STUDIES if s['id']=='phish-1997-12-07')
  titles=[t['title'] for sec in show['sections'] for t in sec['tracks']]
  self.assertEqual(titles.count('It’s Ice'),2)
 def test_study_pages_and_canonical_metadata(self):
  for s in STUDIES:
   p=SITE/'show-depth'/s['id']/'index.html'
   self.assertTrue(p.exists(),s['id'])
   html=p.read_text(encoding='utf-8')
   self.assertIn('https://thejamarchive.org/show-depth/'+s['id']+'/',html)
   self.assertIn(DATA['sources'][s['source_ids'][0]]['url'].replace('&','&amp;'),html)
   self.assertIn('Transition markers are reproduced',html)
   self.assertIn('/repertoire/',html)
 def test_title_pages_link_to_sources_and_concerts(self):
  self.assertEqual(len(list((SITE/'repertoire/songs').glob('*/index.html'))),158)
  h=(SITE/'repertoire/songs/st-stephen/index.html').read_text(encoding='utf-8')
  self.assertIn('gd-1977-05-08',h)
  self.assertIn('Exact title only',h)
 def test_navigation_to_research_from_original_era_atlas(self):
  h=(SITE/'era-atlas/shows/phish-1997-11-17/index.html').read_text(encoding='utf-8')
  self.assertIn('show-depth/phish-1997-11-17/',h)
  h=(SITE/'shows/gd-1977-05-08/index.html').read_text(encoding='utf-8')
  self.assertIn('show-depth/gd-1977-05-08/',h)
 def test_release_retains_all_previous_era_atlas_records(self):
  report=json.loads((SITE/'assets/era-atlas.json').read_text())
  self.assertEqual(report['counts']['unique_records'],361)
  self.assertEqual(len(list((SITE/'era-atlas/shows').glob('*/index.html'))),336)
 def test_legacy_studies_remain(self):
  self.assertTrue((SITE/'performance-lab/index.html').exists())
  self.assertTrue((SITE/'deep-archive/index.html').exists())
  self.assertTrue((SITE/'connections/index.html').exists())
  self.assertTrue((SITE/'recordings/index.html').exists())
  self.assertEqual(len(list((SITE/'shows').glob('*/index.html'))),25)
 def test_no_private_or_copyright_media_generated(self):
  for suffix in ('*.sqlite','*.flac','*.mp3','*.wav'):
   self.assertFalse(list(SITE.rglob(suffix)),suffix)
  self.assertFalse(list(SITE.rglob('research_queue.json')))
 def test_new_scripts_have_no_external_dependencies(self):
  content=(SITE/'show-depth/index.html').read_text()
  self.assertIn('/assets/show-depth.js',content)
  self.assertNotRegex(content,r'<script[^>]+src="https?://')
 def test_public_build_reports_sitemap_and_audit(self):
  audit=json.loads((SITE/'assets/site_audit.json').read_text())
  self.assertEqual(audit['issues'],0)
  self.assertEqual(audit['html_pages_inspected'],850)
  self.assertEqual(audit['version'],'0.14')
  self.assertEqual(R['show_depth_new_routes'],177)

if __name__=='__main__':unittest.main()
