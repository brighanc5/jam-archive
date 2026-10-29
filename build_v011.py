#!/usr/bin/env python3
"""Curated primary-source research dossiers. No scraping or network access during build.

These claims are editorial summaries of source pages; a citation means a record's
source is linked, not that every URL was rechecked during each deployment.
"""
from html import escape
from pathlib import Path
from urllib.parse import urlsplit
from collections import Counter
import json, os, re, subprocess, sys, xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
subprocess.run([sys.executable, str(ROOT/'build_v010.py')], cwd=ROOT, check=True)
SITE = ROOT/'site'
origin = os.environ['JAM_ARCHIVE_ORIGIN'].rstrip('/')
data = json.loads((ROOT/'data/research_dossiers.json').read_text(encoding='utf-8'))
cat = json.loads((SITE/'assets/catalog.json').read_text(encoding='utf-8'))
assert data['version'] == '0.11'
assert data['reviewed_on'] == '2026-10-29'
entity_ids = {e['id'] for e in cat['entities']}
show_ids = {s['id'] for s in cat['historical_shows']}
source_ids = set(data['sources'])
assert len(source_ids) == len(data['sources']) and len(source_ids) >= 25
for sid, source in data['sources'].items():
    url = urlsplit(source['url'])
    assert url.scheme == 'https' and url.netloc and not source['url'].startswith(origin), (sid, source)
    assert source['classification'] in {'artist-official','label-official','community-archive','archived-interview'}
seen = set()
for dossier in data['dossiers']:
    key = (dossier['kind'], dossier['id'])
    assert key not in seen, key
    seen.add(key)
    assert dossier['kind'] in {'artist','show'}
    assert dossier['id'] in (entity_ids if dossier['kind']=='artist' else show_ids), key
    assert len(dossier['facts']) >= 4 and dossier['open_questions']
    for f in dossier['facts']:
        assert f['text'] and f['period'] and f['topic']
        assert f['source_ids'] and all(sid in source_ids for sid in f['source_ids']), (key, f)
assert sum(d['kind']=='artist' for d in data['dossiers']) == 10
assert sum(d['kind']=='show' for d in data['dossiers']) == 12
assert sum(len(d['facts']) for d in data['dossiers']) == 110

css = (ROOT/'deep_archive.css').read_text(encoding='utf-8')
js = (ROOT/'deep_archive.js').read_text(encoding='utf-8')
(SITE/'assets/deep-archive.css').write_text(css,encoding='utf-8')
(SITE/'assets/deep-archive.js').write_text(js,encoding='utf-8')
(SITE/'assets/deep-archive.json').write_text(json.dumps(data, ensure_ascii=False, separators=(',',':'))+'\n', encoding='utf-8')

def e(s): return escape(str(s),quote=True)
def link(href,txt):return '<a href="'+e(href)+'">'+e(txt)+'</a>'
def page(title,head,body,rel='..'):
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{e(head)}"><meta property="og:title" content="{e(title)} · The Jam Archive"><meta property="og:type" content="website"><title>{e(title)} · The Jam Archive</title><link rel="stylesheet" href="/assets/detail.css"><link rel="stylesheet" href="/assets/deep-archive.css"><script src="/assets/deep-archive.js" defer></script></head><body><header><a href="/">THE <span>JAM</span> ARCHIVE</a><nav><a href="/">Discover</a><a href="/deep-archive/">Deep Archive</a><a href="/connections/">Family Tree</a><a href="/time-machine/">Time Machine</a><a href="/recordings/">Recordings</a><a href="/contribute/">Contribute</a></nav></header><main>{body}<footer>THE JAM ARCHIVE · Independent, noncommercial fan research · No concert audio hosted · Sources remain with original publishers · Research edition 2026-10-29.</footer></main></body></html>'''

def source_links(ids):
    return '<div class="da-sources">' + ''.join('<a href="'+e(data['sources'][sid]['url'])+'" target="_blank" rel="noopener noreferrer" title="'+e(data['sources'][sid]['title'])+'">'+e(data['sources'][sid]['title'].split(' · ')[-1])+' ↗</a>' for sid in ids) + '</div>'

def dossier_path(d): return 'deep-archive/'+ ('artists' if d['kind']=='artist' else 'shows')+'/'+d['id']+'/index.html'

for d in data['dossiers']:
    main_subject = '/artists/'+d['id']+'/' if d['kind']=='artist' else '/shows/'+d['id']+'/'
    claims = ''.join('<li class="da-claim"><div class="da-period">'+e(f['period'])+'</div><div><div class="da-topic">'+e(f['topic'])+'</div><p>'+e(f['text'])+'</p>'+source_links(f['source_ids'])+'</div></li>' for f in d['facts'])
    unique_source_ids = sorted({sid for f in d['facts'] for sid in f['source_ids']})
    references=''.join('<li><a href="'+e(data['sources'][sid]['url'])+'" target="_blank" rel="noopener noreferrer">'+e(data['sources'][sid]['title'])+' ↗</a><small>'+e(data['sources'][sid]['classification'].replace('-',' '))+'</small></li>' for sid in unique_source_ids)
    questions=''.join('<li>'+e(q)+'</li>' for q in d['open_questions'])
    body = f'''<div class="da-top"><div class="eyebrow">DEEP ARCHIVE / {e(d['kind'])} / RESEARCH DOSSIER</div><h1>{e(d['name'])}</h1><p class="lead">{e(d['summary'])}</p><div class="da-nav">{link('/deep-archive/','← All research dossiers')}{link(main_subject,'Original archive record →')}{link('/connections/','Explore Family Tree →')}</div><p class="tiny">{e(d['angle'])} · Last editorial source review {e(data['reviewed_on'])}</p></div><div class="da-explain"><strong>Source-backed, not exhaustive.</strong> This is a curated selection of facts and unresolved research questions. Source links show the supporting publication; they are not proof that an external page has stayed unchanged since our last review. Artist rosters are historical or explicitly date-stamped. We do not host recordings.</div><section class="da-section"><h2>{len(d['facts'])} documented research notes</h2><ol class="da-claims">{claims}</ol></section><section class="da-section"><h2>Questions still open</h2><ul class="da-questions">{questions}</ul></section><section class="da-section"><h2>Source bibliography · {len(unique_source_ids)} references</h2><ul class="da-reference-list">{references}</ul></section>'''
    path=SITE/dossier_path(d);path.parent.mkdir(parents=True,exist_ok=True)
    rendered=page(d['name']+' · research dossier',d['summary'],body)
    rendered=rendered.replace('</head>','<link rel="canonical" href="'+e(origin+'/'+dossier_path(d).removesuffix('index.html'))+'"></head>')
    path.write_text(rendered,encoding='utf-8')
    # Add an evidence teaser into the *existing* canonical artist/show page.
    original=SITE/('artists' if d['kind']=='artist' else 'shows')/d['id']/'index.html'
    old=original.read_text(encoding='utf-8')
    assert old.count('<footer>')==1, original
    teaser=''.join('<li><span class="tiny">'+e(f['period'])+'</span> '+e(f['text'])+'</li>' for f in d['facts'][:3])
    module='<section class="card"><div class="eyebrow">NEW / RESEARCHED CONTEXT · v0.11</div><h2>Go deeper: '+e(d['name'])+'</h2><p class="tiny">'+e(d['summary'])+'</p><ul>'+teaser+'</ul><a class="button" href="/deep-archive/'+('artists' if d['kind']=='artist' else 'shows')+'/'+e(d['id'])+'/">Read '+str(len(d['facts']))+' sourced notes and bibliography →</a></section>'
    original.write_text(old.replace('<footer>',module+'<footer>',1),encoding='utf-8')

cards=[]
for d in data['dossiers']:
    kind='Artists & projects' if d['kind']=='artist' else 'Concerts & recordings'
    cards.append('<a class="da-tile" data-search="'+e((d['name']+' '+d['angle']+' '+d['summary']).casefold())+'" data-kind="'+e(d['kind'])+'" href="/'+e(dossier_path(d).removesuffix('index.html'))+'"><small>'+e(kind)+' · '+str(len(d['facts']))+' source-backed notes</small><h3>'+e(d['name'])+'</h3><p>'+e(d['angle'])+'</p><p>'+e(d['summary'][:145])+'</p></a>')
body=f'''<section class="da-top"><div class="eyebrow">DEEP ARCHIVE · THE JAM ARCHIVE v0.11</div><h1>The stories behind the shows.<br><em>With the receipts.</em></h1><p class="lead">Artist histories, concert context, release provenance, and the documentary ambiguities that matter. Every research note links directly to a published source.</p><div class="da-kpis"><div class="da-kpi"><b>{len(data['dossiers'])}</b><small>Research dossiers</small></div><div class="da-kpi"><b>{sum(len(d['facts']) for d in data['dossiers'])}</b><small>Sourced assertions</small></div><div class="da-kpi"><b>{len(data['sources'])}</b><small>External references</small></div><div class="da-kpi"><b>{sum(len(d['open_questions']) for d in data['dossiers'])}</b><small>Open research questions</small></div></div><div class="da-nav">{link('/connections/','Musician Family Tree →')}{link('/time-machine/','Time Machine →')}{link('/recordings/','Recording Explorer →')}</div></section><div class="da-explain"><strong>Editorial method:</strong> Dates of shows, recordings and releases are distinct. We separate source assertions from commentary, and note disagreements instead of forcing certainty. Every note is a short original paraphrase linked to its original publication. Research is a dated snapshot, not continuously rechecked.</div><div class="da-controls"><input id="da-query" type="search" placeholder="Search Duane, Cornell, Magnaball…" aria-label="Search dossiers"><select id="da-filter" aria-label="Filter dossier type"><option value="all">All dossiers</option><option value="artist">Artists & projects</option><option value="show">Concerts & recordings</option></select></div><p id="da-match-count" class="tiny">{len(cards)} research dossiers shown</p><div class="da-cards">{''.join(cards)}</div><section class="da-section"><h2>What we're still establishing</h2><p class="lead">The strongest archive is willing to say what it does not yet know.</p><ul class="da-questions"><li>Whether a tape documents a whole concert, a set, or only part of it.</li><li>Which recording lineage, mix, transfer, or release a link represents.</li><li>Whether contradictory calendar dates indicate a late-night performance or a metadata error.</li><li>Who played at each specific show, rather than assuming a timeless band roster.</li><li>Which claims originate with the artists, record labels, researchers, or fans.</li></ul></section>'''
index=SITE/'deep-archive/index.html';index.parent.mkdir(parents=True,exist_ok=True)
index.write_text(page('Deep Archive','Source-backed historical dossiers for jam bands, concerts, recordings, musicians and lineups.',body).replace('</head>','<link rel="canonical" href="'+e(origin+'/deep-archive/')+'"></head>'),encoding='utf-8')

# Preserve all existing discovery UI while adding editorial navigation.
home=SITE/'index.html';html=home.read_text(encoding='utf-8')
needle='<a class="outlink" href="connections/index.html">Explore the musician family tree →</a>'
assert html.count(needle)==1, 'Homepage discovery links changed, review manually'
html=html.replace(needle,'<a class="outlink" href="deep-archive/index.html">Deep Archive: the stories behind the shows →</a><div class="divider"></div>'+needle,1)
home.write_text(html.replace('PUBLIC BETA · v0.10','PUBLIC BETA · v0.11'),encoding='utf-8')

# Cross-link the three other explorer pages at stable navigation location.
for pathname in ('connections/index.html','recordings/index.html','time-machine/index.html','song-paths/index.html'):
    p=SITE/pathname;h=p.read_text(encoding='utf-8')
    insert='<a href="/deep-archive/">Deep Archive</a>'
    assert h.count('</nav>')>=1, pathname
    h=h.replace('</nav>',insert+'</nav>',1)
    p.write_text(h,encoding='utf-8')

# Add the pages to the full sitemap and report.
ET.register_namespace('', 'http://www.sitemaps.org/schemas/sitemap/0.9')
ns='{http://www.sitemaps.org/schemas/sitemap/0.9}'
sp=SITE/'sitemap.xml';tree=ET.parse(sp)
locs={el.text for el in tree.getroot().iter(ns+'loc')}
paths=['deep-archive/']+[dossier_path(d).removesuffix('index.html') for d in data['dossiers']]
for path in paths:
    url=origin+'/'+path
    assert url not in locs, url
    ET.SubElement(ET.SubElement(tree.getroot(),ns+'url'),ns+'loc').text=url
sp.write_text(ET.tostring(tree.getroot(),encoding='unicode',xml_declaration=True),encoding='utf-8')
report_path=SITE/'assets/build_report.json';report=json.loads(report_path.read_text(encoding='utf-8'))
report.update(version='0.11',deep_archive_dossiers=len(data['dossiers']),deep_archive_assertions=sum(len(d['facts']) for d in data['dossiers']),deep_archive_sources=len(data['sources']),deep_archive_open_questions=sum(len(d['open_questions']) for d in data['dossiers']),site_files=sum(f.is_file() for f in SITE.rglob('*')))
report_path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('v0.11 Deep Archive:',len(data['dossiers']),'dossiers,',report['deep_archive_assertions'],'cited facts,',len(data['sources']),'references')
