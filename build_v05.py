#!/usr/bin/env python3
"""Build public, shareable Jam Archive v0.5 without touching source evidence.

Reads the deterministic v0.4 builder. A public site receives NO synthetic
research fixture and no internal SQLite state. No API is called by this build.
"""
from pathlib import Path
from html import escape as he
from collections import defaultdict
from urllib.parse import quote
from datetime import date
import subprocess,sys,shutil,json,re,unicodedata,os,xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent
PUBLIC=ROOT/'site'

def esc(v): return he(str(v if v is not None else ''),quote=True)
def slug(text):
    out=unicodedata.normalize('NFKD',text).encode('ascii','ignore').decode().lower()
    return re.sub('-+','-',re.sub('[^a-z0-9]+','-',out)).strip('-') or 'untitled'
def link(url,title):
    return f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer" class="source">{esc(title)} ↗</a>' if str(url).startswith('https://') else '<span class="tiny">Link unavailable</span>'
def info(label,value):return f'<div class="fact"><dt>{esc(label)}</dt><dd>{esc(value)}</dd></div>'
def item(title,meta,href,internal=True):
    return f'<div class="item"><a href="{esc(href)}" '+('' if internal else 'target="_blank" rel="noopener noreferrer"')+f'>{esc(title)} {"→" if internal else "↗"}</a><div class="tiny">{esc(meta)}</div></div>'
def page(title,desc,crumb,content,rel='../../',canonical_path=None):
    home=rel+'index.html'
    canon=f'<link rel="canonical" href="{esc(origin+canonical_path)}">' if origin and canonical_path else ''
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{esc(desc[:260])}"><meta property="og:title" content="{esc(title)} · The Jam Archive"><meta property="og:description" content="{esc(desc[:260])}"><meta property="og:type" content="website"><meta name="twitter:card" content="summary"><title>{esc(title)} · The Jam Archive</title>{canon}<link rel="stylesheet" href="{esc(rel)}assets/detail.css"></head><body><header><a href="{esc(home)}">THE <span>JAM</span> ARCHIVE</a><nav><a href="{esc(home)}">Discover</a><a href="{esc(home+'?q=Fillmore')}">Show history</a><a href="{esc(rel)}contribute/index.html">Contribute</a></nav></header><main><div class="eyebrow">{esc(crumb)}</div>{content}<footer>Free · Fan-built · Source-first. This independent project is not affiliated with the artists or archives linked. Original custodians retain credit. Snapshot last checked October 26, 2026. No recordings hosted, no live ticket availability claimed.</footer></main></body></html>'''

def write(relative,data):
    file=PUBLIC/relative
    file.parent.mkdir(parents=True,exist_ok=True)
    file.write_text(data,encoding='utf-8')
    return relative

subprocess.run([sys.executable,str(ROOT/'build_v04.py')],cwd=ROOT,check=True)
cat=json.loads((ROOT/'catalog.json').read_text())
assert len(cat['entities'])==196 and len(cat['source_entries'])==121
cat['about']['version']='0.5 / public discovery edition'
cat['about']['disclaimer']='Historical and tour data are incomplete, dated research samples. The research agent does not run from this website; source information is linked, not rehosted.'
# Omit all internal/synthetic observations from the public export.
cat['research']={'version':1,'generated_at':None,'items':[],'summary':{'pending':0,'approved':0,'rejected':0,'demo':0}}
origin=os.environ.get('JAM_ARCHIVE_ORIGIN','').strip().rstrip('/')
if origin and not re.fullmatch(r'https://[A-Za-z0-9.-]+(?::\d+)?',origin):
    raise SystemExit('JAM_ARCHIVE_ORIGIN must be an HTTPS origin (no path)')
# Clean generated static pages on rebuild. No source research state is in site/.
if PUBLIC.exists():shutil.rmtree(PUBLIC)
PUBLIC.mkdir(parents=True)
write('assets/detail.css',(ROOT/'detail.css').read_text())
write('assets/discovery.js',(ROOT/'discovery_ui.js').read_text())
write('assets/catalog.json',json.dumps(cat,ensure_ascii=False,separators=(',',':'))+'\n')
entities={e['id']:e for e in cat['entities']}
shows=cat.get('historical_shows',[])
showid={x['id']:x for x in shows}
sources=cat['sources']
tapes=defaultdict(list)
for r in cat['recording_sources']:tapes[r['show_id']].append(r)
songs=defaultdict(list)
for h in shows:
    for name in h.get('songs',[]): songs[name].append(h)
assert len({slug(s) for s in songs})==len(songs),'song slugs clash, add disambiguators first'
showroutes={s['id']:'../../shows/'+s['id']+'/index.html' for s in shows}
artistpages=[];showpages=[];songpages=[]

for e in cat['entities']:
    related=[]
    for r in cat['relationships']:
        if e['id'] not in [r['from'],r['to']]:continue
        other=r['to'] if r['from']==e['id'] else r['from']
        target=entities[other]
        status='Sourced' if r['verification']=='verified' else 'Needs verification'
        related.append(item(target['name'],r['type'].replace('_',' ')+' · '+status,'../../artists/'+other+'/index.html'))
        if r.get('source_url') and r['verification']=='verified':
            related.append(f'<div class="tiny" style="padding-bottom:5px">{link(r["source_url"],"Relationship evidence")}</div>')
    historical=[h for h in shows if h['artist_id']==e['id']]
    events=[v for v in cat['events'] if v['artist_id']==e['id'] or e['id'] in v.get('performers',[])]
    src=[s for s in sources if s.get('entity')==e['name']]
    desc=f'Explore {e["name"]}: documented musical connections, historical concerts, recording sources and a dated tour snapshot in The Jam Archive.'
    content=f'''<h1>{esc(e['name'])}</h1><p class="lead">An independent source-first profile of {esc(e['name'])}. Browse verified connections, selected performances and original research sources.</p><span class="tag">{esc(e['type'])}</span> <span class="tag">{esc(', '.join(e['origins']))}</span>'''
    if e.get('aliases'):content+=f'<p class="tiny">Also indexed as: {esc(", ".join(e["aliases"]))}</p>'
    content+=f'''<div class="links"><a class="button" href="../../index.html?q={quote(e['name'])}">Search across the archive →</a></div><div class="warning">This catalog is incomplete. No listed dates or relationships should be treated as a live tour or lineup guarantee. Draft relationships are labeled separately.</div><div class="cols"><section><div class="card"><h2>Musical connections</h2>{''.join(related) if related else '<p class="empty">No researched connections in this edition yet.</p>'}</div><div class="card"><h2>Historical shows</h2>{''.join(item(h['date']+' · '+h['venue'],h['slot']+' · '+h['city'],'../../shows/'+h['id']+'/index.html') for h in historical) if historical else '<p class="empty">No curated concert dossiers yet. This does not imply missing performances.</p>'}</div></section><aside><div class="card"><h2>Concert snapshot</h2><p class="tiny">Source-checked October 26, 2026. These listings do not update automatically.</p>{''.join(item(v['date']+' · '+v['city'],v['venue'],v['source_url'],False) for v in events[:15]) if events else '<p class="empty">No dates in our limited published snapshot.</p>'}</div><div class="card"><h2>Research sources</h2>{''.join(f'<div class="item">{link(s["url"],s["name"])}<div class="tiny">{esc(s["kind"])}</div></div>' for s in src) if src else '<p class="empty">No dedicated indexed resource yet.</p>'}</div></aside></div>'''
    route=f'artists/{e["id"]}/index.html'
    write(route,page(e['name'],desc,'ARTIST / PROJECT PROFILE',content,canonical_path='/artists/'+e['id']+'/'))
    artistpages.append(route)

for h in shows:
    rs=tapes[h['id']]
    related=[x for x in shows if x['id']!=h['id'] and (x['artist_id']==h['artist_id'] or (x['venue']==h['venue'] and x['city']==h['city']))]
    related.sort(key=lambda x:(x['artist_id']!=h['artist_id'],abs((date.fromisoformat(x['date'])-date.fromisoformat(h['date'])).days)))
    songlinks=''.join(f'<a href="../../songs/{slug(s)}/index.html">{esc(s)} →</a>' for s in h['songs'])
    desc=f'{h["artist"]}, {h["date"]} at {h["venue"]}. Source-linked concert dossier, selected setlist excerpt and {len(rs)} indexed recording references.'
    content=f'''<h1>{esc(h['artist'])}<br><span style="color:var(--lime)">{esc(h['date'])}</span></h1><p class="lead">{esc(h.get('highlight',''))}</p><div class="links"><a href="../../artists/{esc(h['artist_id'])}/index.html" class="button">Explore the artist →</a>{link(h['source_url'],'Original show source')}</div><div class="warning">Selected setlist excerpt only—not a full-performance transcription. Recording pointers link externally; source permissions vary. Set slots are distinct concerts when the record specifies them.</div><dl>{info('Venue',h['venue'])}{info('City',h['city']+', '+h['region'])}{info('Show / set',h['slot'])}{info('Verified',h['data_checked'])}</dl><div class="cols"><section><div class="card"><h2>Selected songs</h2><div class="song-grid">{songlinks}</div><p class="tiny">{esc(h.get('setlist_scope','Selected setlist excerpt'))}. Search title matches do not by themselves prove two performances are of the same composition.</p></div><div class="card" id="recordings"><h2>Known recording & release pointers ({len(rs)})</h2>{''.join(f'<div class="item"><h3>{esc(r["title"])}</h3><span class="tag">{esc(r["kind"])}</span><p class="tiny">{esc(r["provider"])} · {esc(r["access"])}</p><p class="tiny">{esc(r.get("description", ""))}</p>{link(r["source_url"],"Open original recording / release page")}</div>' for r in rs) if rs else '<p class="empty">No reviewed tape source linked yet. This does not establish that no recording exists.</p>'}</div></section><aside><div class="card"><h2>Nearby music history</h2>{''.join(item(x['date']+' · '+x['artist'],x['venue']+' · '+x['slot'],'../../shows/'+x['id']+'/index.html') for x in related[:6]) if related else '<p class="empty">No connected shows in the small curated collection.</p>'}</div><div class="card"><h2>Provenance</h2><p class="tiny">The original source remains the authority. If the underlying source is corrected, this static page may temporarily lag.</p>{link(h['source_url'],'Verify original dossier')}</div></aside></div>'''
    route='shows/'+h['id']+'/index.html'
    write(route,page(h['artist']+' · '+h['date'],desc,'HISTORICAL PERFORMANCE / SOURCE LINKED',content,canonical_path='/shows/'+h['id']+'/'))
    showpages.append(route)

for name,hs in songs.items():
    desc=f'{name}: selected indexed setlist appearances in The Jam Archive, linking to original historical show sources.'
    content=f'''<h1>{esc(name)}</h1><p class="lead">A song-title index across our small, researched historical concert collection. Each appearance links to an individual show dossier.</p><div class="warning">This is a literal song-title match in <strong>selected excerpts</strong>, not a comprehensive song database. Similar titles don't establish shared songwriting or identical musical compositions.</div><div class="card"><h2>{len(hs)} documented appearance{'s' if len(hs)!=1 else ''}</h2>{''.join(item(h['artist']+' · '+h['date'],h['venue']+' · '+h['city'],'../../shows/'+h['id']+'/index.html') for h in sorted(hs,key=lambda x:x['date']))}</div><a class="button" href="../../index.html?q={quote(name)}">Search this title across the archive →</a>'''
    route='songs/'+slug(name)+'/index.html'
    write(route,page(name+' · performances',desc,'SONG TITLE / SETLIST EXCERPTS',content,canonical_path='/songs/'+slug(name)+'/'))
    songpages.append(route)

contrib='''<h1>Help the music survive.</h1><p class="lead">The Jam Archive grows through credited research, original taper knowledge, and respectful corrections. We don't accept claims without sources or ask contributors to upload copyrighted recordings.</p><div class="cols"><div class="card"><h2>What to contribute</h2><ul><li>Show date and whether early/late sets were separate.</li><li>Artist, venue, city, and verified guest appearance evidence.</li><li>Recording identifier, source type, taper credit, lineage and lawful external link.</li><li>Corrected setlist entries with a direct citation.</li><li>Broken links, duplicates, aliases and source attribution.</li></ul></div><div class="card"><h2>How review works</h2><p>Submissions need a source URL and an explanation. Unconfirmed reports are research leads, never published facts. Our public GitHub issue intake will become active when a repository is connected.</p><p class="tiny">No upload or submission server is active in this build. Don't send private contact information through unverified forms.</p></div></div><div class="card"><h2>Recording stewardship</h2><p>A taper-friendly policy is not blanket permission to copy or stream concert audio. This project points to authorized custodians, respects attribution, and treats conflicting evidence explicitly.</p></div>'''
write('contribute/index.html',page('Contribute', 'How to support The Jam Archive with researched performances, taper provenance and corrections.','COMMUNITY / SOURCE-FIRST',contrib,rel='../',canonical_path='/contribute/'))
# Editor-curated listening trails based only on the 9 source-linked seed dossiers.
trails = [
  ('allmans-fillmore-1971','The Fillmore East: five performances', 'Compare early and late Allman Brothers performances without treating same-date sets as one show.', [h for h in shows if h['artist_id']=='the-allman-brothers-band' and h['venue']=='Fillmore East']),
  ('cornell-tape-family','Cornell 1977: one show, multiple tapes', 'Explore the distinct audience, soundboard-derived and matrix references indexed for the same Grateful Dead performance.',[h for h in shows if h['id']=='gd-1977-05-08']),
  ('phish-pivotal-nights','Phish: two pivotal nights', 'Two curated concert dossiers from different eras, with selected song excerpts and source links.', [h for h in shows if h['artist_id']=='phish'])
]
trailpages=[]
for slugname,heading,description,chosen in trails:
    html=f'<h1>{esc(heading)}</h1><p class="lead">{esc(description)}</p><div class="warning">Listening trails contain only documented shows in this small starter catalog. Links point to original sources or authorized pages; no audio is stored here.</div><div class="card"><h2>{len(chosen)} documented show dossiers</h2>'+''.join(item(h['date']+' · '+h['artist'], h['venue']+' · '+h['slot']+' · '+str(len(tapes[h['id']]))+' indexed recording reference(s)', '../../shows/'+h['id']+'/index.html') for h in sorted(chosen,key=lambda x:(x['date'],x['slot'])))+'</div>'
    route='trails/'+slugname+'/index.html'
    write(route,page(heading,description,'LISTENING TRAIL / CURATED DISCOVERY',html,canonical_path='/trails/'+slugname+'/'))
    trailpages.append(route)
trail_index='<h1>Follow a listening trail.</h1><p class="lead">Sometimes the best way into music history is one show, followed by another. These listening trails are grounded in the source-linked performances already in our collection.</p><div class="card">'+''.join(item(title,desc,key+'/index.html') for key,title,desc,_ in trails)+'</div>'
write('trails/index.html',page('Listening trails','Source-backed ways to discover connected improvisational performances.','EXPLORE / LISTENING TRAILS',trail_index,rel='../',canonical_path='/trails/'))
# Research gaps are honest indexes of missing *catalog data*, not missing music.
gap_shows=[h for h in shows if not tapes[h['id']]]
gap_rels=[r for r in cat['relationships'] if r['verification']!='verified']
write('assets/research_gaps.json',json.dumps({'warning':'Missing indexed pointer does not mean missing recording. Draft relation is not a factual assertion.', 'shows_without_indexed_recording_pointer':[{'id':h['id'],'artist':h['artist'],'date':h['date'],'original_source_url':h['source_url']} for h in gap_shows], 'relationships_needing_evidence':gap_rels},ensure_ascii=False,indent=2)+'\n')
gaps_html=f'<h1>Where the archive needs help.</h1><p class="lead">A public, source-first research to-do list. Missing data is not evidence that the music or relationship never existed.</p><div class="card"><h2>{len(gap_shows)} shows without indexed recording pointers</h2><p class="tiny">No reviewed recording link in our local index. These performances may have recordings elsewhere.</p>'+''.join(item(h['artist']+' · '+h['date'],h['venue']+' · '+h['slot'],'../shows/'+h['id']+'/index.html') for h in gap_shows)+'</div><div class="card"><h2>{len(gap_rels)} musician/project links awaiting evidence</h2><p class="tiny">Draft research leads, excluded from verified relationship paths until checked.</p>'+''.join(f'<div class="item"><b>{esc(entities[r["from"]]["name"])} → {esc(entities[r["to"]]["name"])}</b><div class="tiny">{esc(r["type"])} · {esc(r.get("note") or "Missing verification")}</div></div>' for r in gap_rels)+'</div><a class="button" href="../contribute/index.html">How to help →</a>'
write('research-gaps/index.html',page('Research gaps','Transparent missing metadata and source-review priorities.','ARCHIVE HEALTH / RESEARCH GAPS',gaps_html,rel='../',canonical_path='/research-gaps/'))
# Navigation exposes the truly cross-content search section; legacy views are preserved.
old=(ROOT/'index.html').read_text()
raw=re.search(r'<script>const db=(.*?);</script>',old,flags=re.S)
assert raw, 'Could not find catalog embedding'
serialized_catalog = json.dumps(cat, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
old = old[:raw.start()] + '<script>const db=' + serialized_catalog + ';</script>' + old[raw.end():]
nav='<button data-nav="discover"><span><span class="icon">⌕</span>Discover</span></button>\n'
old=old.replace('<button class="active" data-nav="universe">',nav+'<button class="active" data-nav="universe">',1)
insert='''<section class="view" id="view-discover"><div class="heading"><div><div class="eyebrow">Discovery engine / the whole archive</div><h2>Find the music, not just the band.</h2><p>Search across artists, side projects, historic shows, selected songs, tape references, published concert snapshots and the original source directory. Press / to search from anywhere.</p></div></div><div class="callout"><div class="eyebrow">Explore the living history</div><h3>One search. Every connected source we have.</h3><p>Try an unusual musician, a concert venue, a song title, or a date. Results link to permanent-style pages you can share with other fans.</p><input id="discovery-input" class="field" type="search" placeholder="Try Fillmore East, Morning Dew, Oysterhead, Derek Trucks…" aria-label="Search the entire archive" style="width:100%;margin-top:9px" autocomplete="off"></div><div class="filterrow" aria-label="Result types"><button class="pillbtn active" data-discover-type="all">Everything</button><button class="pillbtn" data-discover-type="artist">Artists</button><button class="pillbtn" data-discover-type="show">Historic shows</button><button class="pillbtn" data-discover-type="song">Songs</button><button class="pillbtn" data-discover-type="tape">Recordings</button><button class="pillbtn" data-discover-type="event">Tour snapshots</button><button class="pillbtn" data-discover-type="source">Sources</button></div><div class="twocol discovery-layout"><div><p class="tiny" id="discovery-explainer"></p><p class="tiny" id="discovery-count"></p><div class="discovery-results" id="discovery-results"></div></div><aside><div class="card"><div class="eyebrow">On your radar · <span id="discovery-following-count">0</span> followed</div><h3>Upcoming entries for your artists</h3><p class="note">Not real-time alerts. Future-dated events from our last curated snapshot only.</p><div id="discovery-radar"></div><p class="tiny" id="discovery-radar-note"></p></div><div class="card"><h3>Help close the gaps</h3><p class="note">One eyewitness correction or accurately attributed tape source can make a historical record better.</p><a class="outlink" href="contribute/index.html">How to contribute →</a><div class="divider"></div><a class="outlink" href="trails/index.html">Explore listening trails →</a><div class="divider"></div><a class="outlink" href="research-gaps/index.html">Find research gaps →</a></div></aside></div></section>'''
assert '<section class="view active" id="view-universe">' in old
old=old.replace('<section class="view active" id="view-universe">',insert+'\n<section class="view active" id="view-universe">',1)
css='''<style>.discovery-layout{grid-template-columns:minmax(0,1.4fr) minmax(280px,1fr)}.discovery-results{display:grid;gap:9px}.discovery-result{display:flex;flex-direction:column;gap:4px;padding:15px 18px;border:1px solid var(--edge);background:var(--panel);border-radius:11px;text-decoration:none}.discovery-result:hover{background:#1d302b;border-color:#7ca06e;text-decoration:none}.discovery-kind{color:var(--gold);font-size:10px;font-weight:850;text-transform:uppercase;letter-spacing:.12em}.discovery-result strong{color:var(--cream);font-size:16px}.discovery-meta{color:var(--muted);font-size:12px}.discovery-arrow{color:var(--lime);font-size:12px;font-weight:750}.radar-entry{border-bottom:1px solid var(--edge);padding:12px 0;display:flex;justify-content:space-between;gap:8px;align-items:start}.radar-entry b{font-size:12px}.radar-entry a{font-size:12px;white-space:nowrap}.radar-entry .badge{margin-top:6px}@media(max-width:960px){.discovery-layout{grid-template-columns:1fr}}</style>'''
old=old.replace('</head>',css+'</head>',1)
old=old.replace('</body>','<script src="assets/discovery.js"></script>\n</body>',1)
old=old.replace('FOUNDING EDITION · v0.4','PUBLIC DISCOVERY EDITION · v0.5').replace('THE JAM ARCHIVE · v0.4 · Local standalone prototype','THE JAM ARCHIVE · v0.5 · Public static preview')
old=old.replace('<span>Source-checked future listings</span>','<span>Tour snapshot (not live)</span>')
old=old.replace('Published schedules last checked October 26, 2026. These are not real-time event or ticket feeds.', 'Published schedules last checked October 26, 2026. Some dates may now be in the past. These are not real-time event or ticket feeds.')
write('index.html',old)
(ROOT/'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=site/index.html"><title>The Jam Archive v0.5</title><p><a href="site/index.html">Open The Jam Archive v0.5</a></p></html>')  # Local shortcut into the public bundle
standalone=old.replace('<script src="assets/discovery.js"></script>', '<script>'+ (ROOT/'discovery_ui.js').read_text() + '</script>')
standalone=standalone.replace('<head>', '<head><base href="site/">',1)
(ROOT/'standalone_preview.html').write_text(standalone)
write('robots.txt','User-agent: *\nAllow: /\n')
write('_headers','/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n  X-Frame-Options: SAMEORIGIN\n')
write('404.html',page('Page not found','The requested Jam Archive record was not found.','ARCHIVE / NOT FOUND','<h1>That page is not indexed here.</h1><p class="lead">Try searching artists, shows and songs in the archive.</p><a class="button" href="index.html">Search the archive →</a>',rel=''))
if origin:
    ET.register_namespace('', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    root=ET.Element('{http://www.sitemaps.org/schemas/sitemap/0.9}urlset')
    for path in ['index.html','contribute/index.html','trails/index.html','research-gaps/index.html',*artistpages,*showpages,*songpages,*trailpages]:
        u=ET.SubElement(root,'{http://www.sitemaps.org/schemas/sitemap/0.9}url')
        ET.SubElement(u,'{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text=origin+'/'+path.replace('index.html','')
    write('sitemap.xml',ET.tostring(root,encoding='unicode',xml_declaration=True))
    write('robots.txt','User-agent: *\nAllow: /\nSitemap: '+origin+'/sitemap.xml\n')
else:
    write('SITEMAP_SETUP.txt','Set JAM_ARCHIVE_ORIGIN=https://your-verified-domain.example and rerun build_v05.py to generate correct canonical URLs and sitemap.xml. Never publish fabricated canonical URLs.\n')
report={'entities':len(artistpages),'historical_shows':len(showpages),'song_title_pages':len(songpages),'recording_references':len(cat['recording_sources']),'dated_tour_snapshot':len(cat['events']),'source_directory':len(sources),'listening_trails':len(trailpages),'research_gaps':len(gap_shows)+len(gap_rels),'public_synthetic_observations':len(cat['research']['items']),'public_site_files':len(list(PUBLIC.rglob('*')))}
write('assets/build_report.json',json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
