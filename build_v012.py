#!/usr/bin/env python3
"""v0.12: evidence-first track studies and whole-site quality improvements.

No external fetch during build. All claims come from editorially reviewed records.
"""
from collections import Counter
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import urlsplit
import json, os, re, subprocess, sys, xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent
subprocess.run([sys.executable,str(ROOT/'build_v011.py')],cwd=ROOT,check=True)
SITE=ROOT/'site'
origin=os.environ['JAM_ARCHIVE_ORIGIN'].rstrip('/')
assert origin.startswith('https://')
meta=json.loads((ROOT/'data/performance_evidence.json').read_text(encoding='utf-8'))
cat=json.loads((SITE/'assets/catalog.json').read_text(encoding='utf-8'))
assert meta['version']=='0.12'
assert meta['reviewed_on']=='2026-10-29'
shows={x['id']:x for x in cat['historical_shows']}
assert len(meta['sequences'])==12 and len(meta['recording_lineages'])==2
assert len(meta['sources'])==4
assert len({x['id'] for x in meta['sequences']})==12
for sid,src in meta['sources'].items():
 u=urlsplit(src['url']); assert u.scheme=='https' and u.netloc and '@' not in u.netloc,(sid,u)
for s in meta['sequences']:
 assert s['show_id'] in shows and s['source_ids'] and s['entries']
 assert all(i in meta['sources'] for i in s['source_ids'])
 assert s['entries'][-1]['source_transition_after'] is None
 assert [e['order'] for e in s['entries']]==list(range(1,len(s['entries'])+1))
 assert all(e['source_transition_after'] in (None,'>','->') and e['song_title'] for e in s['entries'])
 assert s['evidence_scope'] in {'release_excerpt','setlist_excerpt'}
 for guest in s['documented_guests']:
  assert any(e['song_title']==guest['on_song'] for e in s['entries'])
  assert guest['source_ids'] and all(x in meta['sources'] for x in guest['source_ids'])
for chain in meta['recording_lineages']:
 assert all(s in shows for s in chain['show_ids'])
 assert all(src in meta['sources'] for src in chain['source_ids'])

def e(s):return escape(str(s),quote=True)
def route(s):return 'performance-lab/'+s['id']+'/index.html'
def link(href,content):return '<a href="'+e(href)+'">'+e(content)+'</a>'
def source_links(ids):return ' · '.join('<a class="pl-source" target="_blank" rel="noopener noreferrer" href="'+e(meta['sources'][sid]['url'])+'">'+e(meta['sources'][sid]['title'])+' ↗</a>' for sid in ids)

def html_page(title,desc,body,url):
 return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="'+e(desc[:260])+'"><meta property="og:title" content="'+e(title)+' · The Jam Archive"><meta property="og:description" content="'+e(desc[:260])+'"><meta property="og:type" content="website"><title>'+e(title)+' · The Jam Archive</title><link rel="canonical" href="'+e(origin+url)+'"><link rel="stylesheet" href="/assets/detail.css"><link rel="stylesheet" href="/assets/performance-lab.css"><script src="/assets/performance-lab.js" defer></script></head><body><header><a href="/">THE <span>JAM</span> ARCHIVE</a><nav><a href="/">Discover</a><a href="/deep-archive/">Deep Archive</a></nav></header><main>'+body+'<footer>THE JAM ARCHIVE · Independent fan research · Last editorial review '+e(meta['reviewed_on'])+' · Sources credited, no concert audio hosted</footer></main></body></html>'

(SITE/'assets/performance-lab.css').write_text((ROOT/'performance_lab.css').read_text(encoding='utf-8'),encoding='utf-8')
(SITE/'assets/performance-lab.js').write_text((ROOT/'performance_lab.js').read_text(encoding='utf-8'),encoding='utf-8')
(SITE/'assets/performance-lab.json').write_text(json.dumps(meta,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
for s in meta['sequences']:
 show=shows[s['show_id']]
 tracks=''.join('<li><b>'+e(t['song_title'])+'</b>'+('<span class="pl-transition" aria-label="Source notation '+e(t['source_transition_after'])+'">'+e(t['source_transition_after'])+'</span>' if t['source_transition_after'] else '<span></span>')+'</li>' for t in s['entries'])
 guests=''.join('<div class="pl-guest"><strong>'+e(g['name'])+'</strong> · '+e(g['role'])+' on <em>'+e(g['on_song'])+'</em><div class="pl-note">'+source_links(g['source_ids'])+'</div></div>' for g in s['documented_guests'])
 chain=next((x for x in meta['recording_lineages'] if s['show_id'] in x['show_ids']),None)
 body='<p class="pl-back">'+link('/performance-lab/','← All evidence studies')+'</p><section class="pl-hero"><div class="eyebrow">PERFORMANCE LAB / RESEARCHED EXCERPT</div><h1>'+e(s['title'])+'</h1><p class="lead">'+e(show['artist']+' · '+show['date']+' · '+show['venue'])+'</p></section><div class="pl-linkstrip">'+link('/shows/'+e(s['show_id'])+'/','Open concert dossier →')+link(show['source_url'],'Original concert listing →')+'</div><div class="pl-explain"><strong>Evidence scope:</strong> '+('Official release running order' if s['source_ids'][0] in ('abb_1971_box','rhino_2017') else 'Community-curated setlist excerpt')+'. These are not independently transcribed complete setlists. The source may use a <strong>&gt;</strong> or <strong>-&gt;</strong> marker, reproduced verbatim; no additional transitions, tempos, durations, motifs or musician credits are inferred.</div><section class="card"><div class="eyebrow">'+e(s['section'])+'</div><h2>'+str(len(s['entries']))+' documented track positions</h2><ol class="pl-tracklist">'+tracks+'</ol><p class="pl-note">'+e(s['editorial_note'])+'</p><p class="pl-note"><strong>Release context:</strong> '+e(s['release_context'])+'</p><p class="pl-note"><strong>Original evidence:</strong> '+source_links(s['source_ids'])+'</p></section>'
 if guests:body+='<section class="card"><h2>Documented guest credits</h2>'+guests+'</section>'
 if chain:body+='<section class="card"><h2>Recorded source lineage</h2><p>'+link('/performance-lab/lineages/#'+chain['id'],chain['title']+' →')+'</p><p class="pl-note">'+e(chain['limitations'])+'</p></section>'
 body+='<section class="card"><h2>What remains unknown</h2><p class="pl-readme">A cited track order cannot establish every improvisational detail. Timing, exact segue boundaries, personnel for each number, master generation, tape completeness, and competing circulating versions require separately reviewed evidence.</p></section>'
 target=SITE/route(s);target.parent.mkdir(parents=True,exist_ok=True)
 target.write_text(html_page(s['title'],show['artist']+' '+show['date']+' — documented track sequence, guest notes and original sources.',body,'/'+route(s).removesuffix('index.html')),encoding='utf-8')

# Lineage index stays separate from the performance and the recording pointer.
chain_sections=[]
for chain in meta['recording_lineages']:
 steps=''.join('<li><strong>'+e(step['stage'])+'</strong><p>'+e(step['detail'])+'</p></li>' for step in chain['steps'])
 concerts=' · '.join(link('/shows/'+sid+'/',shows[sid]['date']+' · '+shows[sid]['venue']) for sid in chain['show_ids'])
 chain_sections.append('<section id="'+e(chain['id'])+'" class="card"><h2>'+e(chain['title'])+'</h2><p class="pl-note">Concerts: '+concerts+'</p><ol class="pl-provenance">'+steps+'</ol><p class="pl-explain"><strong>Limit of evidence:</strong> '+e(chain['limitations'])+'</p><p><strong>Source:</strong> '+source_links(chain['source_ids'])+'</p></section>')
lineage_html='<div class="eyebrow">PERFORMANCE LAB / PROVENANCE</div><h1>How a concert becomes a recording.</h1><p class="lead">One event can generate many recordings, transfers and commercial releases. These two chains document only what their named publishers actually establish.</p><div class="pl-linkstrip">'+link('/performance-lab/','← Performance Lab')+'</div>'+''.join(chain_sections)
target=SITE/'performance-lab/lineages/index.html';target.parent.mkdir(parents=True,exist_ok=True)
target.write_text(html_page('Recording lineages','A source-grounded look at concert recordings, tapes, transfers, mastering and official editions.',lineage_html,'/performance-lab/lineages/'),encoding='utf-8')

cards=[]
for s in meta['sequences']:
 show=shows[s['show_id']]
 lookup=(s['title']+' '+show['artist']+' '+show['venue']+' '+s['section']+' '+show['date']+' '+' '.join(t['song_title'] for t in s['entries'])).casefold()
 ntrans=sum(bool(t['source_transition_after']) for t in s['entries'])
 cards.append('<article class="pl-card" data-search="'+e(lookup)+'" data-artist="'+e(show['artist'])+'"><small class="pl-meta">'+e(show['artist'])+' · '+e(show['date'])+'</small><h2>'+e(s['title'])+'</h2><p>'+e(show['venue'])+' · '+str(len(s['entries']))+' tracks · '+str(ntrans)+' source-marked transitions</p><p class="pl-note">'+e(s['section'])+'</p>'+link('/'+route(s).removesuffix('index.html'),'Explore the documented sequence →')+'</article>')
options=''.join('<option value="'+e(a)+'">'+e(a)+'</option>' for a in sorted({shows[s['show_id']]['artist'] for s in meta['sequences']}))
count_tracks=sum(len(x['entries']) for x in meta['sequences'])
count_trans=sum(bool(q['source_transition_after']) for x in meta['sequences'] for q in x['entries'])
count_guests=sum(len(s['documented_guests']) for s in meta['sequences'])
body='<section class="pl-hero"><div class="eyebrow">PERFORMANCE LAB / v0.12</div><h1>Find the moments.<br><em>Follow the evidence.</em></h1><p class="lead">Go beyond the concert date: explore source-documented track order, printed segue notation, guest appearances and the documented history of the recordings themselves.</p><div class="pl-kpis"><div><strong>'+str(len(cards))+'</strong><span>Reviewed sequence studies</span></div><div><strong>'+str(count_tracks)+'</strong><span>Track positions</span></div><div><strong>'+str(count_trans)+'</strong><span>Source-marked transitions</span></div><div><strong>'+str(count_guests)+'</strong><span>Guest credits</span></div></div></section><div class="pl-explain"><strong>What this is:</strong> small, source-backed excerpts of performances or official release track lists, not comprehensive show setlists. Only source-printed transition markers are shown. No audio is hosted. Edition notes and gaps are explicit.</div><div class="pl-linkstrip">'+link('/performance-lab/lineages/','Explore tape and release lineages →')+link('/deep-archive/','Read historical research →')+link('/song-paths/','Follow song titles →')+'</div><section class="pl-controls" aria-label="Filter performance studies"><label for="pl-search">Search songs, shows, venues<input id="pl-search" type="search" placeholder="Try Scarlet, Fillmore, Tom Marshall…" autocomplete="off"></label><label for="pl-artist">Artist<select id="pl-artist"><option value="">All artists</option>'+options+'</select></label></section><p id="pl-count" aria-live="polite" role="status" class="tiny">'+str(len(cards))+' evidence studies shown</p><section class="pl-cards" aria-label="Performance evidence studies">'+''.join(cards)+'</section><p class="pl-readme">These studies do not prove the absence of other tape sources, guest players or segues. Research additions must provide a traceable citation and specify what the source actually verifies.</p>'
idx=SITE/'performance-lab/index.html';idx.parent.mkdir(parents=True,exist_ok=True)
idx.write_text(html_page('Performance Lab','Evidence-first sequences, guest appearances, transitions and tape lineages for historical jam concerts.',body,'/performance-lab/'),encoding='utf-8')

# Embed evidence links on canonical show dossiers. Never erase the original setlist excerpt or links.
byshow={}
for s in meta['sequences']:byshow.setdefault(s['show_id'],[]).append(s)
for sid,seqs in byshow.items():
 p=SITE/'shows'/sid/'index.html';html=p.read_text(encoding='utf-8')
 panel='<section class="card"><div class="eyebrow">NEW / PERFORMANCE EVIDENCE · v0.12</div><h2>Trace documented musical moments</h2><p class="tiny">Release track order or cited setlist excerpt; no unverified segues or guest credits implied.</p><ul>'+''.join('<li>'+link('/'+route(s).removesuffix('index.html'),s['title']+' · '+str(len(s['entries']))+' positions')+'</li>' for s in seqs)+'</ul></section>'
 assert html.count('<footer>')==1
 p.write_text(html.replace('<footer>',panel+'<footer>',1),encoding='utf-8')

# Homepage discovery links and conservative dated listings label.
home=SITE/'index.html';h=home.read_text(encoding='utf-8')
marker='<a class="outlink" href="deep-archive/index.html">Deep Archive: the stories behind the shows →</a>'
assert h.count(marker)==1
h=h.replace(marker,'<a class="outlink" href="performance-lab/">Performance Lab: trace the actual musical moments →</a><div class="divider"></div>'+marker,1)
h=h.replace('Upcoming performances</h2>','Tour snapshot · October 26, 2026</h2>',1)
# Never imply past entries are still upcoming: filter expired snapshot dates in the homepage UI.
old_render='let result=db.events.filter(e=>'
new_render=('let now=new Date();let today=[now.getFullYear(),String(now.getMonth()+1).padStart(2,\'0\'),String(now.getDate()).padStart(2,\'0\')].join(\'-\');'
            'let result=db.events.filter(e=>(e.date_end||e.date)>=today).filter(e=>')
assert h.count(old_render)==1
h=h.replace(old_render,new_render,1)
h=h.replace('Snapshot as of October 26, 2026.`','Snapshot as of October 26, 2026; past dates hidden.`')
h=h.replace('PUBLIC BETA · v0.11','PUBLIC BETA · v0.12')
h=h.replace('A living map of the bands, players, side projects, and performances that make up the jam-music universe.','A growing, source-backed guide to bands, musicians, historical performances, tapes and releases—still incomplete and checked on specific dates.')
home.write_text(h,encoding='utf-8')

# Existing section navigation was inconsistent; normalize the header for all 309+ detail routes.
nav=[('Discover','/'),('Deep Archive','/deep-archive/'),('Time Machine','/time-machine/'),('Song Paths','/song-paths/'),('Recordings','/recordings/'),('Family Tree','/connections/'),('Performance Lab','/performance-lab/'),('Contribute','/contribute/')]
css=(ROOT/'site_quality.css').read_text(encoding='utf-8')
(SITE/'assets/site-quality.css').write_text(css,encoding='utf-8')
count_pages=0
for path in SITE.rglob('*.html'):
 html=path.read_text(encoding='utf-8')
 routepath='/' + str(path.relative_to(SITE)).replace('index.html','')
 if path==SITE/'index.html':
  # Homepage SPA has a bespoke sidebar and no header. Only enhance its keyboard navigation.
  assert '<main' in html
  html=html.replace('<body>','<body><a class="ja-skip" href="#ja-main">Skip to main content</a>',1)
 else:
  pattern=r'(<header><a [^>]+>THE <span>JAM</span> ARCHIVE</a>)<nav>.*?</nav>(</header>)'
  current=lambda href:routepath==href or href!='/' and routepath.startswith(href)
  replacement='<nav aria-label="Archive sections">'+''.join('<a href="'+href+'"'+(' aria-current="page"' if current(href) else '')+'>'+text+'</a>' for text,href in nav)+'</nav>'
  html,n=re.subn(pattern,lambda m:m.group(1)+replacement+m.group(2),html,count=1,flags=re.S)
  assert n==1,path
  html=html.replace('<body>','<body><a class="ja-skip" href="#ja-main">Skip to main content</a>',1)
 assert html.count('<main')==1,path
 html=html.replace('<main','<main id="ja-main"',1)
 html=html.replace('</head>','<link rel="stylesheet" href="/assets/site-quality.css"></head>',1)
 if path==SITE/'404.html':
  html=html.replace('<title>Page not found', '<meta name="description" content="This Jam Archive page is not indexed. Try our music research directory or search the archive."><title>Page not found',1)
 # Missing accessible labels on a small number of older controls, with no behavior changes.
 if path==SITE/'index.html':
  for id,title in [('show-query','Filter concert snapshot'),('archive-query','Search historical performances'),('archive-artist','Filter historical performances by artist'),('import-passport','Import saved show passport JSON')]:
   pat=r'(<(?:input|select)\b[^>]*\bid="'+id+r'"[^>]*)(>)'
   html,n=re.subn(pat,lambda m:m.group(1)+' aria-label="'+title+'"'+m.group(2),html,count=1)
   assert n==1,(id,path)
 if path==SITE/'recordings/index.html':
  for id,title in [('recording-search','Search recording sources'),('recording-artist','Filter recording by artist'),('recording-kind','Filter recording kind'),('recording-sort','Sort recording sources')]:
   pat=r'(<(?:input|select)\b[^>]*\bid="'+id+r'"[^>]*)(>)'
   html,n=re.subn(pat,lambda m:m.group(1)+' aria-label="'+title+'"'+m.group(2),html,count=1)
   assert n==1,(id,path)
 if path==SITE/'song-paths/index.html':
  html=html.replace('id="sp-repeats" type="checkbox"','id="sp-repeats" type="checkbox" aria-label="Only songs indexed at multiple shows"')
 if path==SITE/'contribute/index.html':
  # Existing input fields appear inside wrapping label elements; do not mislabel these.
  pass
 path.write_text(html,encoding='utf-8')
 count_pages+=1

# Add all new indexed routes to sitemap, without indexing 404.
ET.register_namespace('','http://www.sitemaps.org/schemas/sitemap/0.9')
ns='{http://www.sitemaps.org/schemas/sitemap/0.9}'
sp=SITE/'sitemap.xml';tree=ET.parse(sp)
newroutes=['performance-lab/','performance-lab/lineages/']+[route(s).removesuffix('index.html') for s in meta['sequences']]
for r in newroutes:ET.SubElement(ET.SubElement(tree.getroot(),ns+'url'),ns+'loc').text=origin+'/'+r
sp.write_text(ET.tostring(tree.getroot(),encoding='unicode',xml_declaration=True),encoding='utf-8')
report_path=SITE/'assets/build_report.json';report=json.loads(report_path.read_text(encoding='utf-8'))
report.update(version='0.12',performance_sequences=len(meta['sequences']),performance_track_positions=count_tracks,source_marked_transitions=count_trans,documented_guest_credits=count_guests,documented_release_lineages=len(meta['recording_lineages']),site_files=sum(f.is_file() for f in SITE.rglob('*')))
report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('v0.12 Performance Lab:',len(meta['sequences']),'sequences,',count_tracks,'track positions,',count_trans,'source-marked transitions,',count_guests,'guest credits;',count_pages,'HTML pages enriched')
