#!/usr/bin/env python3
"""Jam Archive v0.7: reproducible Recording Explorer on top of safe static v0.6.1.

All content is derived from curated seed plus version-controlled approved data.
No network requests, live feeds, hosting audio, or autonomous publication.
"""
from collections import Counter
from html import escape
from pathlib import Path
import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
subprocess.run([sys.executable, str(ROOT / 'build_v061.py')], cwd=ROOT, check=True)
site = ROOT / 'site'
cat = json.loads((site / 'assets/catalog.json').read_text(encoding='utf-8'))
shows = {s['id']: s for s in cat['historical_shows']}
if not all(r['show_id'] in shows for r in cat['recording_sources']):
    raise SystemExit('One or more recordings reference a nonexistent show')
rows = []
for r in cat['recording_sources']:
    h = shows[r['show_id']]
    rows.append({
        'id': r['id'], 'show_id': h['id'], 'artist': h['artist'],
        'date': h['date'], 'year': int(h['date'][:4]), 'venue': h['venue'],
        'city': h['city'], 'region': h['region'], 'slot': h['slot'],
        'title': r['title'], 'kind': r['kind'], 'provider': r['provider'],
        'description': r.get('description', ''), 'access': r['access'],
        'source_url': r['source_url'], 'source_verified': r['source_verified'],
        'show_url': '../shows/' + h['id'] + '/index.html',
    })
rows.sort(key=lambda r: (r['date'], r['artist'], r['title']))
(site / 'assets/recordings.json').write_text(json.dumps({
    'version': 1,
    'notice': 'Small, manually reviewed directory. These are external source links, not hosted audio or a complete tape census.',
    'items': rows
}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
(site / 'assets/recordings.js').write_text((ROOT / 'recordings_ui.js').read_text(encoding='utf-8'), encoding='utf-8')
(site / 'assets/recordings.css').write_text((ROOT / 'recordings.css').read_text(encoding='utf-8'), encoding='utf-8')
recordings_dir = site / 'recordings'
recordings_dir.mkdir(exist_ok=True)
origin = os.environ.get('JAM_ARCHIVE_ORIGIN', '').rstrip('/')
canonical = '<link rel="canonical" href="' + escape(origin + '/recordings/', quote=True) + '">' if origin else ''
artists = Counter(x['artist'] for x in rows)
options = ''.join('<option value="' + escape(a, quote=True) + '">' + escape(a) + '</option>' for a in sorted(artists))
html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Explore source-linked audience recordings, soundboard sources, matrices, and official live releases indexed by The Jam Archive."><meta property="og:title" content="Recording Explorer · The Jam Archive"><title>Recording Explorer · The Jam Archive</title>{canonical}<link rel="stylesheet" href="../assets/detail.css"><link rel="stylesheet" href="../assets/recordings.css"><script src="../assets/recordings.js" defer></script></head><body><header><a href="../index.html">THE <span>JAM</span> ARCHIVE</a><nav><a href="../index.html">Discover</a><a href="../trails/index.html">Listening trails</a><a href="../contribute/index.html">Contribute</a><a href="../about/index.html">About</a></nav></header><main>
<div class="eyebrow">THE LISTENING LIBRARY / SOURCE-FIRST</div>
<h1>Follow the tape.</h1>
<p class="lead">Explore the documented recording sources behind landmark live performances. Every reference links back to its original archive, taper project, or authorized release. This is a curated starting point—not a comprehensive catalog of recordings.</p>
<div class="stats" aria-label="Archive summary"><div class="stat"><strong>{len(rows)}</strong><span>Reviewed source links</span></div><div class="stat"><strong>{len(artists)}</strong><span>Artists represented</span></div><div class="stat"><strong>{len(set(r['show_id'] for r in rows))}</strong><span>Documented shows</span></div></div>
<section class="card explorer" aria-label="Browse recordings"><div class="eyebrow">DISCOVER / FILTER / LISTEN AT SOURCE</div><div class="filter-grid">
<label>Search tapes and performances<input id="recording-search" type="search" placeholder="Try Cornell, matrix, Fillmore..." autocomplete="off"></label>
<label>Artist<select id="recording-artist"><option value="">All artists</option>{options}</select></label>
<label>Source type<select id="recording-kind"><option value="">All source types</option></select></label>
<label>Order<select id="recording-sort"><option value="oldest">Oldest first</option><option value="newest">Newest first</option><option value="title">Source title</option></select></label></div>
<div class="result-heading"><h2>Recording references</h2><p id="recording-count" role="status" aria-live="polite">Loading source index…</p></div><div id="recording-results" class="recording-results"></div>
</section>
<div class="warning">A concert may have several independent audience tapes, soundboard transfers, matrices, and commercial releases. Listing a recording does not indicate rights to reproduce it, guarantee availability, or imply that an unindexed concert has no tape.</div>
<div class="cols"><div class="card"><h2>Know a tape we're missing?</h2><p>Original source pages, lineage details, taper credits and early/late-show identification help make the archive reliable.</p><a class="button" href="../contribute/index.html">Submit a source for review →</a></div><div class="card"><h2>Why these references?</h2><p>We distinguish performances from recordings. Sources are reviewed before inclusion; new research leads never become public facts automatically.</p><a href="../about/index.html">Read the editorial standards →</a></div></div>
<footer>Independent fan research. No recording files hosted. Linked custodians retain their rights. Existing entries reflect documented research, not a real-time archive feed.</footer></main></body></html>'''
(recordings_dir / 'index.html').write_text(html, encoding='utf-8')
# Contextual directory links on the existing homepage and show dossiers.
index = site / 'index.html'
s = index.read_text(encoding='utf-8')
marker = '<a class="outlink" href="trails/index.html">Explore listening trails →</a>'
if s.count(marker) != 1:
    raise SystemExit('Homepage navigation marker changed; do not silently skip explorer link')
s = s.replace(marker, '<a class="outlink" href="recordings/index.html">Explore recording sources →</a><div class="divider"></div>' + marker)
s = s.replace('PUBLIC BETA · v0.6', 'PUBLIC BETA · v0.7')
index.write_text(s, encoding='utf-8')
for path in (site / 'shows').glob('*/index.html'):
    s = path.read_text(encoding='utf-8')
    # Main show dossiers share one stable recording section marker.
    needle = '<div class="card" id="recordings"><h2>'
    if needle not in s:
        raise SystemExit('Missing show recording section: ' + str(path))
    s = s.replace(needle, '<div class="card" id="recordings"><p class="tiny"><a href="../../recordings/index.html">Browse the entire recording directory →</a></p><h2>', 1)
    path.write_text(s, encoding='utf-8')
# Keep the public About count synchronized when approved records are added.
about = site / 'about/index.html'
about_html = about.read_text(encoding='utf-8')
about_html = about_html.replace('9 recording-source references', f'{len(rows)} reviewed recording-source references')
about.write_text(about_html, encoding='utf-8')
# Add precisely one sitemap entry; never regenerate source lists from the web.
ET.register_namespace('', 'http://www.sitemaps.org/schemas/sitemap/0.9')
sitemap = site / 'sitemap.xml'
tree = ET.parse(sitemap)
ns = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
locs = {loc.text for loc in tree.getroot().iter(ns + 'loc')}
new = origin + '/recordings/'
if new in locs:
    raise SystemExit('Recording explorer route unexpectedly exists already')
el = ET.SubElement(tree.getroot(), ns + 'url')
ET.SubElement(el, ns + 'loc').text = new
tree.write(sitemap, encoding='unicode', xml_declaration=True)
report_path = site / 'assets/build_report.json'
report = json.loads(report_path.read_text(encoding='utf-8'))
report.update(version='0.7', recording_references=len(rows), recording_explorer=True,
              approved_recordings=len(rows)-9, site_files=sum(f.is_file() for f in site.rglob('*')))
report_path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print('v0.7 Recording Explorer:', len(rows), 'reviewed source links;',
      len(rows)-9, 'additional approved links; one new indexed route')
