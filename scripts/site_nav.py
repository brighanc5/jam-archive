#!/usr/bin/env python3
"""Site-wide finishing pass: one menu everywhere + Family Tree cards on artist pages.

Runs after scripts/presentation_fixes.py. Idempotent, offline.

1. Every inner page gets the same short header menu (root-absolute links),
   replacing the 5+ differently ordered menus earlier layers wrote.
2. Every artist/band page in the Family Tree gets a "Family Tree" card:
   bandmates (or bands that share a musician) and one-tap paths to a few
   landmark bands.
"""
from collections import defaultdict, deque
from html import escape
from pathlib import Path
import json, re

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'

# (label, href, path prefix used for aria-current)
MAIN = [
    ('Family Tree', '/connections/', '/connections/'),
    ('Shows', '/era-atlas/', '/era-atlas/'),
    ('Show Studies', '/show-depth/', '/show-depth/'),
    ('Songs', '/repertoire/', '/repertoire/'),
    ('Recordings', '/recordings/', '/recordings/'),
    ('Stories', '/deep-archive/', '/deep-archive/'),
    ('Contribute', '/contribute/', '/contribute/'),
]
MORE = [
    ('Search everything', '/#discover', None),
    ('Story trails', '/trails/', '/trails/'),
    ('Time Machine', '/time-machine/', '/time-machine/'),
    ('Song Paths', '/song-paths/', '/song-paths/'),
    ('Performance Lab', '/performance-lab/', '/performance-lab/'),
    ('Research gaps', '/research-gaps/', '/research-gaps/'),
    ('About', '/about/', '/about/'),
]
HEADER_RE = re.compile(r'<header>(?:(?!</header>).)*?aria-label="Archive sections"(?:(?!</header>).)*?</header>', re.S)
E = lambda s: escape(str(s), quote=True)


def header_for(route):
    def item(label, href, prefix):
        cur = ' aria-current="page"' if prefix and route.startswith(prefix) else ''
        return '<a href="' + href + '"' + cur + '>' + E(label) + '</a>'
    more_open = any(p and route.startswith(p) for _, _, p in MORE)
    return ('<header class="ja-header"><a class="ja-brand" href="/">THE <span>JAM</span> ARCHIVE</a>'
            '<nav aria-label="Archive sections">' + ''.join(item(*m) for m in MAIN) +
            '<details class="ja-more"' + (' data-current' if more_open else '') + '><summary><span class="ja-d">More</span><span class="ja-m">Menu</span></summary><div>' +
            ''.join(item(*m).replace('<a ', '<a class="ja-m" ', 1) for m in MAIN) +
            ''.join(item(*m) for m in MORE) + '</div></details></nav></header>')


pages = 0
for f in sorted(SITE.rglob('*.html')):
    if f == SITE / 'index.html':
        continue
    route = '/' + str(f.parent.relative_to(SITE)).replace('\\', '/').strip('.') + '/'
    route = route.replace('//', '/')
    html = f.read_text(encoding='utf-8')
    if 'class="ja-header"' in html:
        html = re.sub(r'<header class="ja-header">.*?</header>', lambda _: header_for(route), html, count=1, flags=re.S)
    else:
        html, n = HEADER_RE.subn(lambda _: header_for(route), html, count=1)
        assert n == 1, f'site_nav: no standard header in {f.relative_to(SITE)}'
    f.write_text(html, encoding='utf-8')
    pages += 1

# ---- Family Tree card on artist pages ----
graph = json.loads((SITE / 'assets/connections.json').read_text(encoding='utf-8'))
nodes = {n['id']: n for n in graph['nodes']}
adj = defaultdict(set)
for edge in graph['edges']:
    adj[edge['from']].add(edge['to']); adj[edge['to']].add(edge['from'])
is_person = lambda i: nodes[i]['type'] == 'person'


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


LANDMARKS = ['grateful-dead', 'phish', 'the-allman-brothers-band', 'goose']
MARKER = '<div class="card"><h2>Historical shows</h2>'
cards = 0
for aid, node in nodes.items():
    page = SITE / 'artists' / aid / 'index.html'
    if not page.exists():
        continue
    html = page.read_text(encoding='utf-8')
    html = re.sub(r'<div class="card ja-tree-card">.*?</div><!--/ja-tree-card-->', '', html, flags=re.S)
    assert html.count(MARKER) == 1, f'site_nav: artist page layout changed for {aid}'
    if is_person(aid):
        groups = {g for g in adj[aid] if not is_person(g)}
        related = sorted({p for g in groups for p in adj[g] if is_person(p) and p != aid}, key=lambda i: nodes[i]['name'])
        title = 'Bandmates'
        blurb = 'Musicians who shared at least one band or project with ' + node['name'] + '.'
    else:
        members = {p for p in adj[aid] if is_person(p)}
        related = sorted({g for p in members for g in adj[p] if not is_person(g) and g != aid}, key=lambda i: nodes[i]['name'])
        title = 'Related bands'
        blurb = 'Bands and projects that share at least one musician with ' + node['name'] + '.'
    chips = ''.join('<a class="ja-chip" href="/artists/' + E(r) + '/">' + E(nodes[r]['name']) + '</a>' for r in related[:40])
    paths = []
    for target in LANDMARKS:
        if target == aid or target not in nodes:
            continue
        n = hops(aid, target)
        if n:
            paths.append('<a class="ja-path-link" href="/connections/?from=' + E(aid) + '&amp;to=' + E(target) + '">' +
                         E(node['name']) + ' &gt; ' + E(nodes[target]['name']) + ' <span>' + str(n) + (' link' if n == 1 else ' links') + '</span></a>')
    if not related and not paths:
        continue
    card = ('<div class="card ja-tree-card"><div class="eyebrow">FAMILY TREE</div><h2>' + title + '</h2>' +
            ('<p class="tiny">' + E(blurb) + '</p><div class="ja-chips">' + chips + '</div>' if related else '') +
            ('<h3>How do they connect?</h3><div class="ja-paths">' + ''.join(paths) + '</div>' if paths else '') +
            '<p class="tiny"><a href="/connections/?artist=' + E(aid) + '">Open ' + E(node['name']) + ' in the Family Tree →</a></p>'
            '</div><!--/ja-tree-card-->')
    html = html.replace(MARKER, card + MARKER, 1)
    page.write_text(html, encoding='utf-8')
    cards += 1

# ---- Site icon (stops a 404 on every browser visit) + unique titles ----
import shutil
ICON_TAGS = ('<link rel="icon" href="/favicon.ico" sizes="any">'
             '<link rel="apple-touch-icon" href="/apple-touch-icon.png">')
for asset in (ROOT / 'static').iterdir():
    if asset.is_dir():
        continue  # fonts are shipped by house_style.py
    shutil.copyfile(asset, SITE / asset.name)
titles = defaultdict(list)
for f in SITE.rglob('*.html'):
    html = f.read_text(encoding='utf-8')
    if 'rel="apple-touch-icon"' not in html:
        assert '</head>' in html, f'site_nav: no </head> in {f}'
        html = html.replace('</head>', ICON_TAGS + '</head>', 1)
        f.write_text(html, encoding='utf-8')
    m = re.search(r'<title>(.*?)</title>', html, re.S)
    if m:
        titles[m.group(1)].append(f)
renamed = 0
for title, files in titles.items():
    if len(files) < 2:
        continue
    for f in files:
        slot = next((w for w in ('early', 'late') if f.parent.name.endswith('-' + w)), None)
        if not slot:
            continue
        html = f.read_text(encoding='utf-8')
        html = html.replace('<title>' + title + '</title>', '<title>' + title.replace(' · The Jam Archive', ' (' + slot + ' show) · The Jam Archive') + '</title>', 1)
        f.write_text(html, encoding='utf-8')
        renamed += 1

print(f'SITE NAV PASS: one menu on {pages} pages; Family Tree cards on {cards} artist pages; icon on every page; {renamed} duplicate titles disambiguated')
