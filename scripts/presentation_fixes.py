#!/usr/bin/env python3
"""First-impression fixes for the public homepage.

Runs after scripts/polish_site.py. Idempotent, offline, no new data.

What it does:
  * Removes builder/maintainer notes from the public UI (runner status,
    importer instructions, an always-empty research queue).
  * Hides tour-snapshot listings whose date has already passed, in the
    visitor's browser, so the "Live shows" tab never advertises old gigs.
  * Lets a dated homepage feature expire into an evergreen one.
  * Fixes the stale footer version and the hero graph's black fill.
"""
from pathlib import Path
import json, re

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
INDEX = SITE / 'index.html'
VERSION = re.search(r'v(\d+\.\d+)', (ROOT / 'RELEASE_VERSION.txt').read_text(encoding='utf-8')).group(1)

html = INDEX.read_text(encoding='utf-8')


def swap(old, new, required=True):
    """Replace once; tolerate a second run (idempotent) but fail loudly on drift."""
    global html
    if old in html:
        html = html.replace(old, new, 1)
    elif required and new not in html:
        raise SystemExit(f'presentation_fixes: expected markup not found: {old[:70]!r}')


# 1. Maintainer notes do not belong in the public sidebar.
swap('Data checked October 26, 2026.<br>Automated collection requires a configured runner. No email alerts yet.<br><br>',
     'Data checked October 26, 2026.<br><br>')

# 2. Footer carried a v0.6 label from an early build layer.
html = re.sub(r'THE JAM ARCHIVE · v0\.\d+ · Public static preview · Data checked 2026-10-26 · Open-source-ready architecture\. ',
              f'THE JAM ARCHIVE · v{VERSION} · Data checked 2026-10-26. ', html)

# 3. The hero network drawing: an unfilled path renders as black triangles.
swap('<g stroke="#77947c" stroke-opacity=".45" stroke-width="1.5"><path',
     '<g fill="none" stroke="#77947c" stroke-opacity=".45" stroke-width="1.5"><path')

swap('<text x="76" y="197">Roots</text>', '<text x="74" y="180">Roots</text>')  # clear the caption

# The old second example has no path in the reviewed graph (different
# network groups), so it showed a dead end. Use a pair that resolves.
swap('<h3>Oysterhead → Grateful Dead</h3><p class="note">How many degrees separate one experimental supergroup from the Dead? The graph can answer only using its documented connections.</p><button class="linkbtn" data-example="oysterhead|grateful-dead">',
     '<h3>Primus → Phish</h3><p class="note">From Claypool\'s day job to Trey\'s, by way of one very strange supergroup.</p><button class="linkbtn" data-example="primus|phish">')

# 4. Recordings tab: describe what fans can do, not how to run the importer.
swap('<p>This tab covers optionally imported Internet Archive item metadata. Our first 9 hand-verified external recording and release pointers are attached to specific performances in <strong>Show History</strong>. No recordings are hosted here.</p>',
     '<p>Our hand-checked tape and release pointers live with each performance in <strong>Show History</strong>, so a tape is never confused with the night it came from. Want to hear something now? Search the Live Music Archive directly. Nothing is hosted here.</p>')
swap('<div class="divider"></div><div class="eyebrow">Search the optional Archive metadata index</div>',
     '<div class="ja-hidden-index" hidden><div class="eyebrow">Search the optional Archive metadata index</div>')
swap('<div id="archive-results"></div><div class="divider"></div>',
     '<div id="archive-results"></div></div><div class="divider"></div>')
html = re.sub(r'<div class="card"><h3>How the recording index grows</h3>.*?</div>(?=<div class="card"><h3>What deserves preservation)', '', html, count=1, flags=re.S)

# 5. Metric label now reflects only upcoming listings (see filter below).
swap('<span>Tour snapshot (not live)</span>', '<span>Upcoming shows on the radar</span>')

# 6. Drop past-dated tour listings at page load. db is a plain object literal.
marker = '<script>const db='
start = html.find(marker)
assert start >= 0, 'homepage database not found'
_, end = json.JSONDecoder().raw_decode(html, start + len(marker))
# Also expires dated homepage features (step 7). Kept inside this existing
# script because validate.py pins the homepage to four inline scripts.
FILTER = (';(()=>{const d=new Date(),t=[d.getFullYear(),String(d.getMonth()+1).padStart(2,"0"),String(d.getDate()).padStart(2,"0")].join("-");'
          'db.events=db.events.filter(e=>!e.date||e.date>=t);'
          'let gone=0;document.querySelectorAll("[data-until]").forEach(el=>{if(el.dataset.until<t){el.hidden=true;gone++}});'
          'if(gone)document.querySelectorAll("[data-evergreen]").forEach(el=>el.hidden=false)})()')
if not html[end:].startswith(FILTER):
    assert html[end:end + 10] == ';</script>', 'unexpected markup after homepage database'
    html = html[:end] + FILTER + html[end:]

# 7. Dated homepage feature: hide it after its last night, show an evergreen one.
swap('<section class="view active" id="view-universe"><div class="callout">',
     '<section class="view active" id="view-universe"><div class="callout" data-until="2026-11-21">')
EVERGREEN = ('<div class="callout" data-evergreen hidden><div class="eyebrow">Six degrees of jam</div>'
             '<h3>How is Primus connected to Phish?</h3>'
             '<p>Pick any two musicians or bands and the Family Tree finds the shortest chain of documented bandmates between them, with a source for every link.</p>'
             '<div class="callout-actions"><a class="primary" href="connections/index.html?from=primus&amp;to=phish">Trace the path →</a></div></div>')
if 'data-evergreen hidden' not in html:
    i = html.find('data-until="2026-11-21"')
    close = html.find('</div></div>', html.find('callout-actions', i)) + len('</div></div>')
    html = html[:close] + EVERGREEN + html[close:]
# 8. Research desk is a maintainer tool with an always-empty public queue.
CSS = ('<style id="ja-presentation">[hidden]{display:none!important}[data-nav="research"],#view-research{display:none!important}'
       '#recording-count{display:none}'
       '.callout .primary{display:inline-flex;align-items:center;text-decoration:none}'
       '@media(max-width:760px){.app{grid-template-columns:minmax(0,1fr)!important}'
       '.sidebar,.main{min-width:0}.sidebar .nav{overflow-x:auto}}</style>')
if 'id="ja-presentation"' not in html:
    html = html.replace('</head>', CSS + '</head>', 1)

INDEX.write_text(html, encoding='utf-8')
print(f'PRESENTATION PASS: homepage cleaned for v{VERSION}; past listings and dated features expire client-side')
