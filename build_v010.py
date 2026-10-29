#!/usr/bin/env python3
"""v0.10: source-backed musician/project connections, no inferred edges.

All public graph edges must be explicitly verified, cite an HTTPS source, and
point to indexed entities. Never treat co-membership as a documented sit-in.
"""
from collections import defaultdict, Counter, deque
from html import escape
from pathlib import Path
from urllib.parse import urlsplit
import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
subprocess.run([sys.executable, str(ROOT / 'build_v09.py')], check=True, cwd=ROOT)
SITE = ROOT / 'site'
cat = json.loads((SITE / 'assets/catalog.json').read_text(encoding='utf-8'))
entities = {e['id']: e for e in cat['entities']}
reviewed = cat['relationships']
assert len(reviewed) == 77, 'Catalog relationship coverage changed; re-review before publishing'
verified = [r for r in reviewed if r['verification'] == 'verified']
assert len(verified) == 52, 'Verified source set changed; re-review before publishing'
assert {r['verification'] for r in reviewed} <= {'verified', 'needs_review'}
assert all(r['from'] in entities and r['to'] in entities and r['from'] != r['to'] for r in verified)
assert all(urlsplit(r.get('source_url', '')).scheme == 'https' and urlsplit(r['source_url']).netloc for r in verified)
assert all(r['type'] in {'member_of', 'collaboration_with'} for r in verified)
assert len({(r['from'], r['to'], r['type']) for r in verified}) == len(verified)

def e(text):
    return escape(str(text), quote=True)

nodes = {v for r in verified for v in (r['from'], r['to'])}
adj = defaultdict(list)
for r in verified:
    adj[r['from']].append(r['to'])
    adj[r['to']].append(r['from'])
components = []
seen = set()
for node in sorted(nodes):
    if node in seen:
        continue
    group = set([node])
    q = deque([node])
    seen.add(node)
    while q:
        for other in adj[q.popleft()]:
            if other not in seen:
                seen.add(other)
                group.add(other)
                q.append(other)
    components.append(sorted(group))
components.sort(key=lambda grp: (-len(grp), entities[grp[0]]['name']))
component_id = {node: i for i, grp in enumerate(components) for node in grp}
assert len(nodes) == 55 and len(components) == 8

public = {
    'version': '0.10',
    'scope': 'Only explicitly source-verified musician/project links. Paths are graph connections, not proven sit-ins, encounters, simultaneous lineups, or musical influence.',
    'nodes': [
        {'id': id_, 'name': entities[id_]['name'], 'type': entities[id_]['type'],
         'component': component_id[id_], 'degree': len(adj[id_])}
        for id_ in sorted(nodes, key=lambda k: entities[k]['name'].casefold())
    ],
    'edges': [
        {'from': r['from'], 'to': r['to'], 'type': r['type'],
         'note': r.get('note', ''), 'source_url': r['source_url']}
        for r in verified
    ],
    'components': [{'id': i, 'size': len(group), 'members': group} for i, group in enumerate(components)],
}
assets = SITE / 'assets'
(assets / 'connections.json').write_text(json.dumps(public, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
(assets / 'connections.css').write_text((ROOT / 'connections.css').read_text(encoding='utf-8'), encoding='utf-8')
(assets / 'connections.js').write_text((ROOT / 'connections.js').read_text(encoding='utf-8'), encoding='utf-8')

choices = ''.join('<option value="' + e(n['id']) + '">' + e(n['name']) + '</option>' for n in public['nodes'])

# Real paths verified from the graph, not hand-entered claims.
def shortest(a, b):
    q = deque([[a]])
    seen = {a}
    while q:
        path = q.popleft()
        if path[-1] == b:
            return path
        for nxt in adj[path[-1]]:
            if nxt not in seen:
                seen.add(nxt)
                q.append(path + [nxt])
    return None

examples = [('trey-anastasio', 'les-claypool'),
            ('derek-trucks', 'warren-haynes'),
            ('joe-russo', 'leo-kottke'),
            ('oteil-burbridge', 'john-mayer')]
example_markup = ''
for start, end in examples:
    path = shortest(start, end)
    assert path and len(path) >= 3, (start, end)
    example_markup += ('<button class="cx-example" data-start="' + e(start) + '" data-end="' + e(end) + '">' +
                       e(entities[start]['name']) + ' <span>↔</span> ' + e(entities[end]['name']) +
                       '<small>' + str(len(path) - 1) + ' documented links</small></button>')

edges_by_project = defaultdict(list)
for r in verified:
    edges_by_project[r['to']].append(r)
# The full source ledger is rendered into HTML, usable with JS disabled.
ledger = []
for r in sorted(verified, key=lambda r: (entities[r['from']]['name'], entities[r['to']]['name'])):
    typ = 'Documented membership' if r['type'] == 'member_of' else 'Documented collaboration'
    note = (' <span class="cx-edge-note">' + e(r['note']) + '</span>') if r.get('note') else ''
    ledger.append('<li class="cx-ledger-item" data-names="' + e((entities[r['from']]['name'] + ' ' + entities[r['to']]['name']).casefold()) + '">' +
                  '<div><a href="../artists/' + e(r['from']) + '/index.html">' + e(entities[r['from']]['name']) + '</a>' +
                  ' <span aria-hidden="true">→</span> <a href="../artists/' + e(r['to']) + '/index.html">' + e(entities[r['to']]['name']) + '</a>' +
                  '<div class="cx-ledger-detail">' + typ + note + '</div></div>' +
                  '<a class="cx-cite" href="' + e(r['source_url']) + '" target="_blank" rel="noopener noreferrer">Evidence ↗</a></li>')

html = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Explore 52 source-verified links among musicians and projects, follow documented membership paths, and read the original evidence in The Jam Archive.">
<meta property="og:title" content="The Family Tree · The Jam Archive"><meta property="og:type" content="website"><title>The Family Tree · The Jam Archive</title>
<link rel="canonical" href="''' + e(os.environ['JAM_ARCHIVE_ORIGIN'].rstrip('/')) + '''/connections/"><link rel="stylesheet" href="../assets/detail.css"><link rel="stylesheet" href="../assets/connections.css"><script src="../assets/connections.js" defer></script></head><body>
<header><a href="../index.html">THE <span>JAM</span> ARCHIVE</a><nav><a href="../index.html">Discover</a><a href="../song-paths/index.html">Song Paths</a><a href="../time-machine/index.html">Time Machine</a><a href="../recordings/index.html">Recordings</a><a href="../contribute/index.html">Contribute</a></nav></header><main>
<section class="cx-hero"><div class="eyebrow">THE FAMILY TREE · v0.10</div><h1>Everyone's connected.<br><em>Prove it.</em></h1><p class="lead">Trace how improvisational musicians cross paths through documented bands and projects. Every link in this explorer points back to its original evidence. If we can't establish a connection from our reviewed records, we won't manufacture one.</p><div class="cx-metrics"><div><b>''' + str(len(verified)) + '''</b><span>Verified links</span></div><div><b>''' + str(len(nodes)) + '''</b><span>Connected musicians &amp; projects</span></div><div><b>''' + str(len(components)) + '''</b><span>Documented network groups</span></div></div><p class="cx-small">''' + str(len(reviewed)-len(verified)) + ''' additional relationship leads await verification and are excluded from all paths.</p></section>
<div class="warning"><strong>How to read this:</strong> A path proves only that this catalog has a chain of separately sourced relationships. It does <strong>not</strong> prove musicians met, played together, toured at the same time, influenced each other, or appeared on the same recording. Membership links can be historical. The network is intentionally incomplete.</div>
<section class="cx-panel" aria-label="Explore a musician and their direct connections"><div class="cx-panel-heading"><div class="eyebrow">01 / FOCUS THE NETWORK</div><h2>Pick a musician. Follow the branches.</h2><p>Select any indexed musician or project, then explore only its directly verified neighbors.</p></div><label for="cx-focus">Focus on<select id="cx-focus">''' + choices + '''</select></label><div class="cx-layout"><div class="cx-visual"><svg id="cx-network" viewBox="0 0 760 470" role="img" aria-label="Direct verified relationships for the selected artist, available in the adjacent accessible list"><text x="380" y="220" text-anchor="middle" fill="#abc0b4">Loading diagram…</text></svg></div><div class="cx-aside"><h3 id="cx-focus-title">Direct relationships</h3><p id="cx-focus-note" class="cx-small">Select a node or use the list.</p><ul id="cx-neighbors" class="cx-neighbors"><li>Loading verified relationships…</li></ul><a id="cx-profile" href="../artists/trey-anastasio/index.html" class="cx-profile">Open artist / project profile →</a></div></div></section>
<section class="cx-panel" aria-label="Find a documented relationship path"><div class="eyebrow">02 / SIX DEGREES OF JAM</div><h2>Can you connect these artists?</h2><p>Choose two entries. We'll calculate the shortest available chain using only verified, cited relationships.</p><div class="cx-controls"><label for="cx-from">From<select id="cx-from">''' + choices + '''</select></label><label for="cx-to">To<select id="cx-to">''' + choices + '''</select></label><button type="button" id="cx-find" class="cx-find">Find the connection →</button></div><div id="cx-path" class="cx-path" role="status" aria-live="polite"><p>Choose a pair to begin.</p></div><div class="cx-presets"><strong>Try a route:</strong>''' + example_markup + '''</div></section>
<section class="cx-panel" aria-label="Verified relationship ledger"><div class="eyebrow">03 / SOURCE LEDGER</div><h2>Every edge has evidence.</h2><p>Browse all ''' + str(len(verified)) + ''' reviewed relationships. These links remain visible and usable even if JavaScript is disabled.</p><label for="cx-ledger-search">Filter musician or project<input id="cx-ledger-search" type="search" placeholder="Try Allman Brothers, Oysterhead, Goose…"></label><p id="cx-ledger-count" class="cx-small">''' + str(len(verified)) + ''' verified relationships</p><ol class="cx-ledger">''' + ''.join(ledger) + '''</ol></section>
<div class="card"><h2>Who belongs in the tree next?</h2><p>Many musicians are not connected by the evidence we've reviewed yet. Rather than infer their histories, we're inviting source-backed corrections, accurate personnel credits, and links to original project documentation.</p><a class="button" href="../contribute/index.html">Help document a connection →</a><a class="button alt" href="../research-gaps/index.html">See research gaps →</a></div><footer>THE JAM ARCHIVE · Independent fan research · No audio hosted · Evidence belongs to original publishers · Editorial snapshot: October 29, 2026.</footer></main></body></html>'''
page = SITE / 'connections/index.html'
page.parent.mkdir(parents=True, exist_ok=True)
embedded = json.dumps(public, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
html = html.replace('</body>', '<script id="cx-data" type="application/json">' + embedded + '</script></body>', 1)
page.write_text(html, encoding='utf-8')

# Homepage CTA: avoid overwriting the existing data-driven application.
home = SITE / 'index.html'
s = home.read_text(encoding='utf-8')
marker = '<a class="outlink" href="song-paths/index.html">Follow a song through history →</a>'
assert s.count(marker) == 1, 'Homepage changed; review the CTA placement'
s = s.replace(marker, '<a class="outlink" href="connections/index.html">Explore the musician family tree →</a><div class="divider"></div>' + marker, 1)
s = s.replace('PUBLIC BETA · v0.9', 'PUBLIC BETA · v0.10')
home.write_text(s, encoding='utf-8')
# Connect every existing artist/project dossier to the new graph.
for artist_id in entities:
    p = SITE / 'artists' / artist_id / 'index.html'
    s = p.read_text(encoding='utf-8')
    marker = '<div class="eyebrow">ARTIST / PROJECT PROFILE</div>'
    assert s.count(marker) == 1, f'Artist template changed: {artist_id}'
    if artist_id in nodes:
        target = '../../connections/index.html?artist=' + e(artist_id)
        label = 'Explore verified connections for this entry'
    else:
        target = '../../connections/index.html'
        label = 'Explore the musician network (no verified links indexed here yet)'
    s = s.replace(marker, '<p class="tiny"><a href="' + target + '">' + label + ' →</a></p>' + marker, 1)
    p.write_text(s, encoding='utf-8')
# Cross-navigation from exploration features.
for rel in ('song-paths/index.html', 'time-machine/index.html', 'recordings/index.html'):
    p = SITE / rel
    s = p.read_text(encoding='utf-8')
    marker = '<a href="../contribute/index.html">Contribute</a>'
    assert s.count(marker) == 1, f'Unexpected navigation: {rel}'
    s = s.replace(marker, '<a href="../connections/index.html">Family Tree</a>' + marker, 1)
    p.write_text(s, encoding='utf-8')
# Avoid known Cloudflare nested-404 relative links. All 404 routes use root absolute links.
notfound = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>Page not found · The Jam Archive</title><link rel="stylesheet" href="/assets/detail.css"></head><body><header><a href="/">THE <span>JAM</span> ARCHIVE</a><nav><a href="/">Discover</a><a href="/connections/">Family Tree</a><a href="/time-machine/">Show history</a><a href="/contribute/">Contribute</a></nav></header><main><div class="eyebrow">ARCHIVE / NOT FOUND</div><h1>We haven't indexed this page.</h1><p class="lead">This link may be outdated, or the record isn't in our archive yet.</p><p><a class="button" href="/">Search the archive →</a><a class="button alt" href="/song-paths/">Explore Song Paths →</a></p><footer>Free · Fan-built · Source-first · No concert audio hosted.</footer></main></body></html>'''
(SITE / '404.html').write_text(notfound, encoding='utf-8')
# Sitemaps are assembled in builder order. Add the final route exactly once.
ET.register_namespace('', 'http://www.sitemaps.org/schemas/sitemap/0.9')
ns = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
tree = ET.parse(SITE / 'sitemap.xml')
locs = {x.text for x in tree.getroot().iter(ns+'loc')}
url = os.environ['JAM_ARCHIVE_ORIGIN'].rstrip('/') + '/connections/'
assert url not in locs
ET.SubElement(ET.SubElement(tree.getroot(), ns+'url'), ns+'loc').text = url
tree.write(SITE / 'sitemap.xml', encoding='unicode', xml_declaration=True)
reportfile = SITE / 'assets/build_report.json'
report = json.loads(reportfile.read_text(encoding='utf-8'))
report.update(version='0.10', family_tree=True, verified_relationships=len(verified),
              graph_entities=len(nodes), graph_components=len(components),
              unverified_relationships_excluded=len(reviewed)-len(verified),
              site_files=sum(p.is_file() for p in SITE.rglob('*')))
reportfile.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(f'v0.10 Family Tree: {len(verified)} verified edges / {len(nodes)} connected entries / {len(components)} disconnected source groups')
