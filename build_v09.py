#!/usr/bin/env python3
"""Build v0.9: song-to-show connections inferred ONLY from source-listed song excerpts.

This generates a static index; it does not claim complete setlists, analyze audio,
identify motifs, or imply a performance segue. No network connection is made.
"""
from collections import Counter, defaultdict
from html import escape
from pathlib import Path
from urllib.parse import urlsplit
import json
import os
import re
import subprocess
import sys
import unicodedata
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
subprocess.run([sys.executable, str(ROOT / 'build_v08.py')], cwd=ROOT, check=True)
site = ROOT / 'site'
cat = json.loads((site / 'assets/catalog.json').read_text(encoding='utf-8'))
shows = cat['historical_shows']
records = cat['recording_sources']
origin = os.environ['JAM_ARCHIVE_ORIGIN'].rstrip('/')
assert origin.startswith('https://')

def e(v):
    return escape(str(v), quote=True)

def slug(text):
    out = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode().lower()
    return re.sub('-+', '-', re.sub('[^a-z0-9]+', '-', out)).strip('-') or 'untitled'

by_title = defaultdict(list)
recorded_ids = {r['show_id'] for r in records}
for h in shows:
    assert urlsplit(h['source_url']).scheme == 'https', f'Unsafe show source: {h["id"]}'
    assert len(h.get('songs', [])) == len(set(h.get('songs', []))), f'Duplicate song title per performance: {h["id"]}'
    for name in h.get('songs', []):
        by_title[name].append(h)
assert len(by_title) == 53 and sum(map(len, by_title.values())) == 106, 'Source-linked founding excerpt changed; review historical evidence before altering snapshot'
assert len({slug(title) for title in by_title}) == len(by_title), 'Song URLs collided; add disambiguation before release'

entries = []
cards = []
for name, occurrences in sorted(by_title.items(), key=lambda p: (-len(p[1]), p[0].casefold())):
    occurrences = sorted(occurrences, key=lambda h: (h['date'], h['artist'], h['id']))
    counts = Counter()
    for h in occurrences:
        counts.update(s for s in h['songs'] if s != name)
    related = [(other, number) for other, number in counts.most_common(4) if number >= 2]
    artists = sorted({h['artist'] for h in occurrences})
    shows_count = len(occurrences)
    listitems = ''.join(
        '<li><a href="../shows/' + e(h['id']) + '/index.html">' + e(h['date']) +
        ' · ' + e(h['artist']) + '</a><span>' + e(h['venue']) +
        (' · recording reference indexed' if h['id'] in recorded_ids else ' · no reviewed recording reference indexed') +
        '</span></li>' for h in occurrences
    )
    connections = ' · '.join('<a href="../songs/' + e(slug(other)) + '/index.html">' +
        e(other) + ' (' + str(c) + ')</a>' for other, c in related)
    detail = '<div class="sp-related"><b>Also indexed in these same performances:</b> ' + connections + '</div>' if connections else ''
    card = ('<article class="sp-card" data-song="' + e(name.casefold()) + '" data-count="' +
            str(shows_count) + '" data-artists="' + e('|'.join(artists)) + '">' +
            '<div class="sp-card-top"><span class="sp-badge">' + str(shows_count) +
            ' documented appearance' + ('s' if shows_count != 1 else '') + '</span><span>' +
            e(occurrences[0]['date'][:4]) + '–' + e(occurrences[-1]['date'][:4]) + '</span></div>' +
            '<h2>' + e(name) + '</h2><p class="sp-artists">' + e(' · '.join(artists)) + '</p>' +
            '<details><summary>View ' + str(shows_count) + ' indexed performances</summary><ol>' + listitems +
            '</ol></details>' + detail + '<a class="sp-detail" href="../songs/' +
            e(slug(name)) + '/index.html">Song dossier →</a></article>')
    cards.append(card)
    entries.append({
        'title': name, 'slug': slug(name), 'artist_names': artists,
        'documented_appearances': shows_count,
        'show_ids': [h['id'] for h in occurrences],
        'co_indexed_titles': [{'title': other, 'shared_shows': c} for other, c in related],
    })

artist_opts = ''.join('<option value="' + e(artist) + '">' + e(artist) + '</option>'
                     for artist in sorted({h['artist'] for h in shows if h['songs']}))
index_html = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Follow 53 song titles across 106 documented setlist-excerpt appearances in the Jam Archive. Explore song-to-show pathways with original sources and transparent coverage limits."><meta property="og:title" content="Song Paths · The Jam Archive"><meta property="og:description" content="Trace documented song appearances through source-linked Allman Brothers, Grateful Dead, and Phish performances."><meta property="og:type" content="website"><meta name="twitter:card" content="summary"><title>Song Paths · The Jam Archive</title><link rel="canonical" href="'''+e(origin)+'''/song-paths/"><link rel="stylesheet" href="../assets/detail.css"><link rel="stylesheet" href="../assets/song-paths.css"><script src="../assets/song-paths.js" defer></script></head><body>
<header><a href="../index.html">THE <span>JAM</span> ARCHIVE</a><nav><a href="../index.html">Discover</a><a href="../time-machine/index.html">Time Machine</a><a href="../recordings/index.html">Recordings</a><a href="../contribute/index.html">Contribute</a></nav></header><main>
<section class="sp-hero"><div class="eyebrow">SONG PATHS · v0.9</div><h1>Every song has<br><em>a history.</em></h1><p class="lead">Start with a song. Find its documented performances, jump into the original concert record, then follow other songs indexed at those same shows. This is our first source-backed layer of musical connections—no invented segues or audio analysis.</p><div class="sp-stats"><div><b>'''+str(len(by_title))+'''</b><span>Indexed song titles</span></div><div><b>'''+str(sum(map(len,by_title.values())))+'''</b><span>Documented appearances</span></div><div><b>'''+str(sum(bool(h['songs']) for h in shows))+'''</b><span>Shows with setlist excerpts</span></div></div><p class="sp-inline"><a href="../time-machine/index.html">Explore concert timelines →</a> <a href="../recordings/index.html">Find recording sources →</a></p></section>
<div class="warning"><strong>Important:</strong> These numbers describe only the source-documented setlist excerpts already in our small catalog—not a band's full repertoire, total plays, complete setlists or confirmed song transitions. “Also indexed” means two titles appear in the same documented show excerpt; it does not establish a segue or even adjacent performance. An indexed recording link is not a promise of freely available audio.</div>
<section class="sp-filter" aria-label="Search documented song pathways"><div class="eyebrow">FIND YOUR WAY IN</div><div class="sp-controls"><label for="sp-search">Song, venue, or date<input id="sp-search" type="search" placeholder="Try Whipping Post, Cornell, 1977…" autocomplete="off"></label><label for="sp-artist">Performer<select id="sp-artist"><option value="">All artists</option>'''+artist_opts+'''</select></label><label for="sp-sort">Sort by<select id="sp-sort"><option value="most">Most documented appearances</option><option value="alpha">Song title A–Z</option></select></label><label class="sp-checkline"><input id="sp-repeats" type="checkbox"> Only titles indexed at multiple shows</label></div><p id="sp-count" aria-live="polite" role="status">'''+str(len(by_title))+''' song titles</p></section>
<section id="sp-grid" class="sp-grid" aria-label="Song directory">'''+''.join(cards)+'''</section><p id="sp-empty" class="sp-empty" hidden>No titles match this search. Try a different performer or turn off the repeated-appearances filter.</p>
<div class="card"><h2>Help connect the music, carefully.</h2><p>Our next milestone is to increase the number of genuinely source-verified show excerpts, tapes and performance links—especially historical Allman Brothers, Grateful Dead, Phish and Goose recordings. Song relationships will automatically grow as approved performances are published.</p><a href="../contribute/index.html" class="button">Submit a correction or recording source →</a></div><footer>The Jam Archive is an independent fan research project. Links stay with original custodians. No music hosted, no real-time tour claims. Editorial snapshot: October 28, 2026.</footer></main></body></html>'''
p = site / 'song-paths/index.html'
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text(index_html, encoding='utf-8')
(site / 'assets/song-paths.css').write_text((ROOT / 'song_paths.css').read_text(encoding='utf-8'), encoding='utf-8')
(site / 'assets/song-paths.js').write_text((ROOT / 'song_paths.js').read_text(encoding='utf-8'), encoding='utf-8')
(site / 'assets/song-paths.json').write_text(json.dumps({'version': '0.9', 'scope': 'selected documented show excerpts, not complete setlists', 'songs': entries}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# Make Song Paths discoverable from important routes and all 53 underlying song dossiers.
index = site / 'index.html'
s = index.read_text(encoding='utf-8')
marker = '<a class="outlink" href="time-machine/index.html">Step into the Time Machine →</a>'
assert s.count(marker) == 1, 'Homepage structure changed: check new navigation manually'
s = s.replace(marker, '<a class="outlink" href="song-paths/index.html">Follow a song through history →</a><div class="divider"></div>' + marker)
s = s.replace('PUBLIC BETA · v0.8', 'PUBLIC BETA · v0.9')
index.write_text(s, encoding='utf-8')

for rel in ('time-machine/index.html', 'recordings/index.html'):
    p = site / rel
    s = p.read_text(encoding='utf-8')
    marker = '<a href="../contribute/index.html">Contribute</a>'
    assert s.count(marker) == 1, f'Missing navigation marker: {rel}'
    s = s.replace(marker, '<a href="../song-paths/index.html">Song Paths</a>' + marker)
    p.write_text(s, encoding='utf-8')

for path in (site / 'songs').glob('*/index.html'):
    s = path.read_text(encoding='utf-8')
    marker = '<div class="eyebrow">SONG TITLE / SETLIST EXCERPTS</div>'
    assert s.count(marker) == 1, f'Missing song dossier marker {path}'
    s = s.replace(marker, '<p class="tiny"><a href="../../song-paths/index.html">← Back to Song Paths</a></p>' + marker)
    path.write_text(s, encoding='utf-8')

ET.register_namespace('', 'http://www.sitemaps.org/schemas/sitemap/0.9')
ns = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
tree = ET.parse(site / 'sitemap.xml')
url = origin + '/song-paths/'
assert url not in {v.text for v in tree.getroot().iter(ns + 'loc')}
ET.SubElement(ET.SubElement(tree.getroot(), ns + 'url'), ns + 'loc').text = url
tree.write(site / 'sitemap.xml', encoding='unicode', xml_declaration=True)

reportp = site / 'assets/build_report.json'
report = json.loads(reportp.read_text(encoding='utf-8'))
report.update(version='0.9', song_paths=True, song_titles_indexed=len(by_title),
              song_documented_appearances=sum(map(len, by_title.values())),
              site_files=sum(p.is_file() for p in site.rglob('*')))
reportp.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(f'v0.9 Song Paths: {len(by_title)} titles / {sum(map(len, by_title.values()))} selected documented appearances / {len(cards)} server-rendered cards')
