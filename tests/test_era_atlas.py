"""v0.13 Archive Atlas: source provenance, claim bounds, route and build fidelity."""
from collections import Counter
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import json,re,unittest
ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'site'
DATA=json.loads((ROOT/'data/era_index.json').read_text(encoding='utf-8'))
ATLAS=json.loads((SITE/'assets/era-atlas.json').read_text(encoding='utf-8'))
CAT=json.loads((SITE/'assets/catalog.json').read_text(encoding='utf-8'))

class EraAtlasTest(unittest.TestCase):
 def test_version_and_counts(self):
  self.assertEqual(DATA['version'],'0.13')
  self.assertEqual(ATLAS['version'],'0.13')
  self.assertIn('v0.13',(ROOT/'RELEASE_VERSION.txt').read_text())
  self.assertEqual(len(DATA['indexed_events']),352)
  self.assertEqual(ATLAS['counts']['unique_records'],361)
  self.assertEqual(ATLAS['counts']['indexed_new_source_pointers'],336)
  self.assertEqual(ATLAS['counts']['founding_researched_dossiers'],25)
  self.assertEqual(ATLAS['counts']['selected_spotlights'],20)
  self.assertEqual(len(ATLAS['events']),361)
  self.assertEqual(Counter(x['artist'] for x in DATA['indexed_events']),{'The Allman Brothers Band':181,'Phish':104,'Goose':37,'Grateful Dead':30})
 def test_source_links_have_real_https_shapes(self):
  self.assertGreaterEqual(len(DATA['sources']),12)
  for key,x in DATA['sources'].items():
   self.assertEqual(urlsplit(x['url']).scheme,'https',key)
   self.assertTrue(urlsplit(x['url']).hostname,key)
   self.assertNotIn('@',urlsplit(x['url']).netloc,key)
 def test_all_events_are_supported_and_distinct(self):
  ids=set();artists={e['id'] for e in CAT['entities']}
  for x in DATA['indexed_events']:
   self.assertNotIn(x['id'],ids);ids.add(x['id'])
   self.assertIn(x['artist_id'],artists)
   self.assertLessEqual(date.fromisoformat(x['date']),date(2026,10,29))
   self.assertTrue(x['source_ids']);self.assertTrue(set(x['source_ids'])<=set(DATA['sources']))
   self.assertEqual(x['evidence_scope'],'concert_date_venue')
   self.assertEqual(x['recording_status'],'not_investigated')
   self.assertEqual(x['lineup_status'],'not_investigated')
   self.assertEqual(x['songs'],[])
 def test_dedupe_canonical_not_shadowed(self):
  base={(x['artist_id'],x['date']) for x in CAT['historical_shows']}
  new=[x for x in DATA['indexed_events'] if (x['artist_id'],x['date']) not in base]
  self.assertEqual(len(new),336)
  for x in DATA['indexed_events']:
   if (x['artist_id'],x['date']) in base:
    self.assertFalse((SITE/'era-atlas/shows'/x['id']/'index.html').exists())
   else:
    self.assertTrue((SITE/'era-atlas/shows'/x['id']/'index.html').is_file())
 def test_new_pages_explicitly_disclaim_unknown_metadata(self):
  for x in DATA['indexed_events']:
   p=SITE/'era-atlas/shows'/x['id']/'index.html'
   if not p.is_file():continue
   h=p.read_text(encoding='utf-8')
   self.assertIn('not a full concert dossier',h)
   self.assertIn('not independently established a complete setlist',h)
   self.assertIn('recording',h)
   self.assertIn('href="/contribute/"',h)
   self.assertIn('rel="noopener noreferrer"',h)
   for sid in x['source_ids']:self.assertIn(DATA['sources'][sid]['url'].replace('&','&amp;'),h)
 def test_spotlights_are_exactly_twenty_with_secondary_citations(self):
  spotlight=[x for x in DATA['indexed_events'] if x.get('spotlight')]
  self.assertEqual(len(spotlight),20)
  for x in spotlight:
   note=x['spotlight']
   self.assertTrue(note['title'] and note['summary'] and note['source_ids'])
   self.assertTrue(set(note['source_ids'])<=set(x['source_ids']))
 def test_chapter_pages_have_source_links(self):
  chapter=list((SITE/'era-atlas/chapters').glob('*/index.html'))
  self.assertEqual(len(chapter),12)
  for p in chapter:
   text=p.read_text(encoding='utf-8')
   self.assertIn('Research foundation',text)
   self.assertIn('Indexed performances',text)
 def test_existing_abb_and_other_dossiers_remain(self):
  self.assertEqual(len(list((SITE/'shows').glob('*/index.html'))),25)
  self.assertIn('abb-1971-03-12-early', {x['id'] for x in CAT['historical_shows']})
  self.assertIn('href="/shows/abb-1971-03-12-early/"',(SITE/'era-atlas/index.html').read_text())
 def test_index_filters_are_progressive(self):
  html=(SITE/'era-atlas/index.html').read_text(encoding='utf-8')
  self.assertEqual(html.count('class="ea-card"'),361)
  for name in ('ea-search','ea-artist','ea-year','ea-kind','ea-results'):
   self.assertIn('id="'+name+'"',html)
  self.assertIn('.ea-card[hidden]',(SITE/'assets/era-atlas.css').read_text())
  self.assertIn('URLSearchParams',(SITE/'assets/era-atlas.js').read_text())
 def test_website_integration(self):
  self.assertIn('Archive Atlas: explore',(SITE/'index.html').read_text())
  for artist in ('phish','grateful-dead','goose','the-allman-brothers-band'):
   page=(SITE/'artists'/artist/'index.html').read_text(encoding='utf-8')
   self.assertIn('ARCHIVE ATLAS · v0.13',page)
   self.assertIn('/era-atlas/?artist='+artist,page)
 def test_reports_and_public_json(self):
  report=json.loads((SITE/'assets/build_report.json').read_text())
  self.assertEqual(report['version'],'0.13')
  self.assertEqual(report['era_atlas_records'],361)
  self.assertEqual(report['era_atlas_new_source_pointers'],336)
  self.assertNotIn('private_key',json.dumps(ATLAS))
  self.assertNotIn('review_queue',json.dumps(ATLAS))
  self.assertFalse(list(SITE.rglob('*.sqlite')))
  self.assertFalse(list(SITE.rglob('*.flac')))
 def test_global_audit_includes_new_routes(self):
  result=json.loads((SITE/'assets/site_audit.json').read_text())
  self.assertEqual(result['issues'],0)
  self.assertEqual(result['html_pages_inspected'],673)
  self.assertEqual(result['version'],'0.13')
if __name__=='__main__':unittest.main()
