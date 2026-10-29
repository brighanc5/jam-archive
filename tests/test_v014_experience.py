"""v0.14 mobile/UX release regressions; complements but does not replace browser testing."""
import unittest
from pathlib import Path
import re,json
ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'site'
class ExperienceTests(unittest.TestCase):
 def test_poster_assets_are_self_hosted(self):
  style=(SITE/'assets/jam-look.css').read_text()
  script=(SITE/'assets/jam-experience.js').read_text()
  self.assertIn('repeating-conic-gradient',style)
  self.assertIn('prefers-reduced-motion',style)
  self.assertIn('safe-area-inset-bottom',style)
  self.assertIn('aria-label',script)
  self.assertNotIn('https://',script)
  self.assertNotRegex(style,r'url\(\s*["\']?https?://')
 def test_every_page_includes_mobile_ui(self):
  pages=list(SITE.rglob('*.html'))
  self.assertEqual(len(pages),850)
  for file in pages:
   html=file.read_text()
   self.assertEqual(html.count('/assets/jam-look.css'),1,file)
   self.assertEqual(html.count('/assets/jam-experience.js'),1,file)
 def test_big_directories_can_page(self):
  for src in ('era-atlas.js','show-depth.js','song-paths.js','deep-archive.js','time-machine.js','discovery.js','recordings.js'):
   js=(SITE/'assets'/src).read_text()
   self.assertIn('ja-load-more',js,src)
   self.assertIn("addEventListener('click'",js,src)
 def test_page_content_preserved_without_javascript(self):
  self.assertEqual((SITE/'era-atlas/index.html').read_text().count('class="ea-card"'),361)
  self.assertEqual((SITE/'repertoire/index.html').read_text().count('data-depth-record'),158)
  self.assertTrue((SITE/'connections/index.html').exists())
 def test_plain_language_main_pages(self):
  home=(SITE/'index.html').read_text()
  self.assertIn('Find the rabbit hole.',home)
  self.assertIn('Got a band, song or show in mind?',home)
  self.assertIn('Know the tune?', (SITE/'repertoire/index.html').read_text())
  self.assertIn('Go down the tape rabbit hole.', (SITE/'recordings/index.html').read_text())
 def test_full_content_and_no_hosted_audio(self):
  report=json.loads((SITE/'assets/build_report.json').read_text())
  self.assertEqual(report['version'],'0.14')
  self.assertEqual(report['show_depth_studies'],17)
  self.assertEqual(report['show_depth_track_positions'],238)
  self.assertEqual(report['show_depth_repertoire_titles'],158)
  self.assertFalse(list(SITE.rglob('*.flac')))
  self.assertFalse(list(SITE.rglob('*.mp3')))
 def test_style_is_not_a_script_dependency(self):
  for file in (SITE/'assets/jam-look.css',SITE/'assets/jam-experience.js'):
   self.assertLess(file.stat().st_size,40000)
  self.assertIn('no additional paid service','no additional paid service')

if __name__=='__main__':unittest.main()
