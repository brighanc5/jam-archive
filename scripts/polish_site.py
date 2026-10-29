#!/usr/bin/env python3
"""Apply our original, mobile-first print identity to generated pages.

Run after the deterministic v0.14 content builder; idempotent. No network calls.
"""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'site'
assert (SITE/'index.html').exists()
assert (SITE/'show-depth/index.html').exists()
(SITE/'assets/jam-look.css').write_bytes((ROOT/'jam_look.css').read_bytes())
(SITE/'assets/jam-experience.js').write_bytes((ROOT/'jam_experience.js').read_bytes())
style='<link rel="stylesheet" href="/assets/jam-look.css">'
script='<script src="/assets/jam-experience.js" defer></script>'
count=0
for file in SITE.rglob('*.html'):
    html=file.read_text(encoding='utf-8')
    if style not in html:
        assert '</head>' in html,file
        html=html.replace('</head>',style+'</head>',1)
    if script not in html:
        assert '</body>' in html,file
        html=html.replace('</body>',script+'</body>',1)
    if file == SITE/'index.html':
        html=html.replace('PUBLIC BETA · v0.13','PUBLIC BETA · v0.14')
        html=html.replace('THE IMPROVISATIONAL MUSIC UNIVERSE','A LONG, STRANGE RABBIT HOLE')
        html=html.replace('Every show.<br>Every connection.<br><em>One place.</em>','Follow the music.<br>Find the rabbit hole.<br><em>Keep digging.</em>')
        html=html.replace('Find the music, not just the band.','Got a band, song or show in mind?')
        html=html.replace('Explore the universe','Start digging')
        html=html.replace('Click a name to see its musicians, projects, source links, and scheduled performances.','Pick a band or player. See who they played with, where they played, and what we can back up.')
        html=html.replace('Tour snapshot · October 26, 2026','Shows on the radar · checked October 26, 2026')
        html=html.replace('Discovery engine / the whole archive','FIND YOUR NEXT RABBIT HOLE')
        html=html.replace('The artist network','WHO PLAYED WITH WHO')
        html=html.replace('Follow the connections','Follow the bandmates')
        html=html.replace('THE JAM ARCHIVE · v0.13','THE JAM ARCHIVE · v0.14')
        html=html.replace('Source-backed','Source-linked')
    if file == SITE/'show-depth/index.html':
        html=html.replace('Beyond the show date.<br>Inside the performance.','What actually went down<br>that night?')
        html=html.replace('Find a researched concert','Pick a show and dig in')
    if file == SITE/'era-atlas/index.html':
        html=html.replace('A sourced entryway to the concerts around the classics.', 'Find the gigs around the legendary nights. Dates and venues first; more detail where we have solid sources.')
        html=html.replace('Browse all indexed nights','Dig through the shows')
    if file == SITE/'performance-lab/index.html':
        html=html.replace('Find the moments. Follow the evidence.','Find the good parts. See the proof.')
        html=html.replace('Go beyond the concert date: explore source-documented track order, printed segue notation, guest appearances and the documented history of the recordings themselves.', 'Follow songs from one night to the next, see who sat in, and find out where the tapes came from. We link our notes to the original setlists and releases.')
    if file == SITE/'deep-archive/index.html':
        html=html.replace('Artist histories, concert context, release provenance, and the documentary ambiguities that matter. Every research note links directly to a published source.', 'The people, shows, stories, and recordings behind the music. Each note links to somewhere you can check it yourself.')
    if file == SITE/'connections/index.html':
        html=html.replace('Trace how improvisational musicians cross paths through documented bands and projects.', 'Find out who played with who, and which bands brought them together.')
        html=html.replace('Every link in this explorer points back to its original evidence.', 'We link each connection to where we found it.')
    if file == SITE/'recordings/index.html':
        html=html.replace('Explore the documented recording sources behind landmark live performances.', 'Go down the tape rabbit hole. Find the recordings and releases we know about.')
        html=html.replace('This is a curated starting point—not a comprehensive catalog.', 'We are just getting started; there are plenty more tapes to track down.')
    if file == SITE/'song-paths/index.html':
        html=html.replace('Every song has a history.','Every tune has a story.')
    if file == SITE/'repertoire/index.html':
        html=html.replace('Find the song.<br>Find the night.','Know the tune?<br>Find the show.')
        html=html.replace('Browse 158 source-backed titles','Dig through 158 song titles')
    file.write_text(html,encoding='utf-8')
    count+=1
print(f'JAM LOOK PASS: original psychedelic styling and mobile navigation on {count} HTML pages')
