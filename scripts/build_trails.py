#!/usr/bin/env python3
"""Editorial story trails from data/trails/*.json -> /trails/<slug>/.

Runs after presentation_fixes.py and BEFORE site_nav.py (which normalizes the
header this script writes). Idempotent, offline.

Each section must cite at least one https source, and every Family Tree path
it links to must exist in the verified graph, or the build fails.
"""
from collections import defaultdict, deque
from html import escape
from pathlib import Path
from urllib.parse import urlsplit
import json, os, re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
ORIGIN = os.environ.get('JAM_ARCHIVE_ORIGIN', 'https://thejamarchive.org').rstrip('/')
E = lambda s: escape(str(s), quote=True)

graph = json.loads((SITE / 'assets/connections.json').read_text(encoding='utf-8'))
names = {n['id']: n['name'] for n in graph['nodes']}
adj = defaultdict(set)
for edge in graph['edges']:
    adj[edge['from']].add(edge['to']); adj[edge['to']].add(edge['from'])


def hops(a, b):
    seen = {a: 0}; q = deque([a])
    while q:
        x = q.popleft()
        if x == b:
            return seen[x]
        for y in adj[x]:
            if y not in seen:
                seen[y] = seen[x] + 1; q.append(y)
    return None


def link(title, url):
    assert urlsplit(url).scheme == 'https', f'build_trails: non-https source {url}'
    return '<a href="' + E(url) + '" target="_blank" rel="noopener noreferrer">' + E(title) + ' ↗</a>'


trails = []
for spec_file in sorted((ROOT / 'data/trails').glob('*.json')):
    t = json.loads(spec_file.read_text(encoding='utf-8'))
    slug = t['slug']
    assert re.fullmatch(r'[a-z0-9-]+', slug), slug
    body = []
    for n, sec in enumerate(t['sections'], 1):
        assert sec.get('sources'), f'build_trails: {slug} section {n} has no source'
        path_html = ''
        if sec.get('path'):
            a, b = sec['path']
            assert a in names and b in names, f'build_trails: {slug} section {n} names unknown ids {a}, {b}'
            k = hops(a, b)
            assert k, f'build_trails: no verified path {a} -> {b} ({slug} section {n})'
            path_html = ('<a class="ja-path-link" href="/connections/?from=' + E(a) + '&amp;to=' + E(b) + '">' +
                         E(names[a]) + ' &gt; ' + E(names[b]) + ' <span>' + str(k) + (' link' if k == 1 else ' links') + '</span></a>')
        body.append('<section class="card ja-trail-step"><div class="eyebrow">STOP ' + str(n) + '</div><h2>' + E(sec['heading']) + '</h2>'
                    '<p>' + E(sec['text']) + '</p>' + path_html +
                    '<p class="tiny">Sources: ' + ' · '.join(link(*s) for s in sec['sources']) + '</p></section>')
    listening = ''
    if t.get('listening'):
        listening = ('<section class="card"><div class="eyebrow">LISTEN</div><h2>Where to hear it</h2><ul>' +
                     ''.join('<li>' + link(*x) + '</li>' for x in t['listening']) +
                     '</ul><p class="tiny">Links go to the artists and labels. Nothing is hosted here.</p></section>')
    route = '/trails/' + slug + '/'
    page = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta name="description" content="' + E(t['description']) + '"><meta property="og:title" content="' + E(t['title']) + ' · The Jam Archive">'
            '<meta property="og:description" content="' + E(t['deck']) + '"><meta property="og:type" content="article">'
            '<title>' + E(t['title']) + ' · The Jam Archive</title><link rel="canonical" href="' + E(ORIGIN + route) + '">'
            '<link rel="stylesheet" href="/assets/detail.css"><link rel="stylesheet" href="/assets/site-quality.css"><link rel="stylesheet" href="/assets/jam-look.css"></head><body>'
            '<a class="ja-skip" href="#ja-main">Skip to main content</a><header><a href="/">THE <span>JAM</span> ARCHIVE</a><nav aria-label="Archive sections"><a href="/connections/">Family Tree</a></nav></header>'
            '<main id="ja-main"><div class="eyebrow">STORY TRAIL</div><h1>' + E(t['title']) + '</h1><p class="lead">' + E(t['deck']) + '</p>' +
            ''.join(body) + listening +
            '<p class="tiny">' + E(t['credits']) + ' Spotted an error? <a href="/contribute/">Tell us</a>.</p>'
            '<p><a class="button" href="/trails/">More trails →</a> <a class="button alt" href="/connections/">Open the Family Tree →</a></p>'
            '<footer>Free · Fan-built · Source-first. Not affiliated with the artists or archives linked. No recordings hosted.</footer></main><script src="/assets/jam-experience.js" defer></script></body></html>')
    out = SITE / 'trails' / slug / 'index.html'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding='utf-8')
    trails.append((t, route))

# List story trails first on /trails/.
index = SITE / 'trails/index.html'
html = index.read_text(encoding='utf-8')
html = re.sub(r'<div class="card ja-story-trails">.*?</div><!--/ja-story-trails-->', '', html, flags=re.S)
marker = '<div class="card"><div class="item"><a href="allmans-fillmore-1971/index.html"'
assert html.count(marker) == 1, 'build_trails: trails index layout changed'
cards = ''.join('<div class="item"><a href="' + E(route) + '">' + E(t['title']) + ' →</a><div class="tiny">' + E(t['deck']) + '</div></div>' for t, route in trails)
html = html.replace(marker, '<div class="card ja-story-trails"><div class="eyebrow">STORY TRAILS</div>' + cards + '</div><!--/ja-story-trails-->' + marker, 1)
index.write_text(html, encoding='utf-8')

# Sitemap must list every public route exactly once.
ns = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
ET.register_namespace('', ns[1:-1])
tree = ET.parse(SITE / 'sitemap.xml')
locs = {x.text for x in tree.getroot().iter(ns + 'loc')}
for _, route in trails:
    if ORIGIN + route not in locs:
        ET.SubElement(ET.SubElement(tree.getroot(), ns + 'url'), ns + 'loc').text = ORIGIN + route
tree.write(SITE / 'sitemap.xml', encoding='unicode', xml_declaration=True)
print(f'TRAILS PASS: {len(trails)} story trail(s), every section sourced, every path verified')
