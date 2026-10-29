#!/usr/bin/env python3
"""v0.13: source-indexed Archive Atlas, preserving canonical fully researched shows.

Build makes no network requests; pointers refer only to explicitly reviewed source indices.
No claims of complete setlists, guest personnel, tape availability, or full coverage.
"""
from collections import Counter, defaultdict
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import urlsplit
import json, os, re, subprocess, sys, xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent
subprocess.run([sys.executable, str(ROOT/'build_v012.py')],cwd=ROOT,check=True)
SITE=ROOT/'site'
ORIGIN=os.environ['JAM_ARCHIVE_ORIGIN'].rstrip('/')
raw=json.loads((ROOT/'data/era_index.json').read_text(encoding='utf-8'))
cat=json.loads((SITE/'assets/catalog.json').read_text(encoding='utf-8'))
assert raw['version']=='0.13' and raw['reviewed_on']=='2026-10-29'
assert len(raw['indexed_events'])>=350
artists={x['id']:x for x in cat['entities']}
old=cat['historical_shows']
old_by_artist_date=defaultdict(list)
for s in old:old_by_artist_date[(s['artist_id'],s['date'])].append(s)
assert len(raw['sources'])>=12
for key,source in raw['sources'].items():
 u=urlsplit(source['url']);assert u.scheme=='https' and u.netloc and '@' not in u.netloc,key
 assert source['category'] in {'community_tour_calendar','artist_official_show_index','community_derived_concert_index','community_setlist','community_event_history','artist_official_show'}
seen=set();enriched=0;canonical_count=0
for event in raw['indexed_events']:
 assert event['id'] not in seen and re.fullmatch(r'[a-z0-9-]+',event['id']);seen.add(event['id'])
 assert event['artist_id'] in artists
 assert date.fromisoformat(event['date']) <= date(2026,10,29)
 assert event['source_ids'] and all(x in raw['sources'] for x in event['source_ids'])
 assert event['record_status']=='source_indexed' and event['evidence_scope']=='concert_date_venue'
 assert not event['songs'] and event['recording_status']=='not_investigated' and event['lineup_status']=='not_investigated'
 matches=old_by_artist_date[(event['artist_id'],event['date'])]
 if matches:
  # Use the current canonical source-detailed show record instead of creating a duplicate.
  event['canonical_ids']=[s['id'] for s in matches]
  event['route']='/shows/'+matches[0]['id']+'/'
  canonical_count+=1
 else:
  event['canonical_ids']=[]
  event['route']='/era-atlas/shows/'+event['id']+'/'
 if event.get('spotlight'):
  enriched+=1
  assert event['spotlight']['source_ids'] and all(s in raw['sources'] for s in event['spotlight']['source_ids'])
assert canonical_count>=15 and enriched==raw['spotlight_count']

# Our founding Allmans & other curated concerts remain first-class records, not flattened into superficial source pointers.
existing=[]
for s in old:
 existing.append({'id':s['id'],'artist':s['artist'],'artist_id':s['artist_id'],'date':s['date'],'venue':s['venue'],'place':s['city']+', '+s['region'],'era':'Founding curated dossiers','route':'/shows/'+s['id']+'/', 'kind':'researched_dossier','highlight':s.get('highlight',''), 'source_url':s['source_url']})
index=[{'id':x['id'],'artist':x['artist'],'artist_id':x['artist_id'],'date':x['date'],'venue':x['venue'],'place':x['place'],'era':x['era'],'route':x['route'],'kind':'researched_dossier' if x['canonical_ids'] else 'source_index_only','spotlight':x.get('spotlight'),'source_ids':x['source_ids']} for x in raw['indexed_events'] if not x['canonical_ids']]
index+=existing
index.sort(key=lambda x:(x['date'],x['artist'],x['id']))
assert len({x['id'] for x in index})==len(index)
source_index_count=sum(x['kind']=='source_index_only' for x in index)
assert source_index_count==len(raw['indexed_events'])-canonical_count
unique_performance_count=len(index)

# Sidecar public data is thin: only cited public source pointers, never review database state.
export={'version':'0.13','reviewed_on':raw['reviewed_on'],'scope':raw['method'],'sources':raw['sources'],'events':index,'counts':{'indexed_new_source_pointers':source_index_count,'founding_researched_dossiers':len(old),'unique_records':unique_performance_count,'selected_spotlights':enriched}}
(SITE/'assets/era-atlas.json').write_text(json.dumps(export,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
(SITE/'assets/era-atlas.css').write_text((ROOT/'era_atlas.css').read_text(encoding='utf-8'),encoding='utf-8')
(SITE/'assets/era-atlas.js').write_text((ROOT/'era_atlas.js').read_text(encoding='utf-8'),encoding='utf-8')

def e(x):return escape(str(x),quote=True)
def a(url,txt):return '<a href="'+e(url)+'">'+e(txt)+'</a>'
nav=[('Discover','/'),('Archive Atlas','/era-atlas/'),('Deep Archive','/deep-archive/'),('Time Machine','/time-machine/'),('Song Paths','/song-paths/'),('Recordings','/recordings/'),('Family Tree','/connections/'),('Performance Lab','/performance-lab/'),('Contribute','/contribute/')]
def page(title,description,route,content):
 links=''.join('<a href="'+href+'"'+(' aria-current="page"' if route==href else '')+'>'+e(label)+'</a>' for label,href in nav)
 return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="'+e(description[:260])+'"><meta property="og:title" content="'+e(title)+' · The Jam Archive"><meta property="og:type" content="website"><title>'+e(title)+' · The Jam Archive</title><link rel="canonical" href="'+e(ORIGIN+route)+'"><link rel="stylesheet" href="/assets/detail.css"><link rel="stylesheet" href="/assets/site-quality.css"><link rel="stylesheet" href="/assets/era-atlas.css"><script defer src="/assets/era-atlas.js"></script></head><body><a class="ja-skip" href="#ja-main">Skip to main content</a><header><a href="/">THE <span>JAM</span> ARCHIVE</a><nav aria-label="Archive sections">'+links+'</nav></header><main id="ja-main">'+content+'<footer>THE JAM ARCHIVE · Independent, source-first, not affiliated · Research reviewed '+e(raw['reviewed_on'])+' · No audio hosted</footer></main></body></html>'
def source_link(ids):
 return ''.join('<li><a href="'+e(raw['sources'][sid]['url'])+'" target="_blank" rel="noopener noreferrer">'+e(raw['sources'][sid]['title'])+' ↗</a> <span class="ea-small">('+e(raw['sources'][sid]['scope'].replace('_',' '))+')</span></li>' for sid in ids)

# Index-only event pages, visibly different from full editorial show dossiers.
for s in raw['indexed_events']:
 if s['canonical_ids']:continue
 heading=s['artist']+' · '+s['date']
 spotlight=s.get('spotlight')
 prose='<div class="ea-story"><strong>'+e(spotlight['title'])+'</strong><p>'+e(spotlight['summary'])+'</p><p class="ea-small">Research note attributed to: '+', '.join(e(raw['sources'][key]['title']) for key in spotlight['source_ids'])+'</p></div>' if spotlight else ''
 note='<div class="ea-notice"><strong>Index-level record, not a full concert dossier.</strong> The cited index supports the date and venue. We have not independently established a complete setlist, lineup, guest list, performance duration or surviving tape for this date. <a href="/contribute/">Help research this show →</a></div>'
 if s.get('editorial_warning'):note+='<p class="ea-story">'+e(s['editorial_warning'])+'</p>'
 body='<p>'+a('/era-atlas/','← Return to Archive Atlas')+'</p><section class="ea-hero"><div class="eyebrow">ARCHIVE ATLAS / SOURCE-INDEXED DATE</div><h1>'+e(heading)+'</h1><p class="lead">'+e(s['venue']+' · '+s['place'])+'</p><span class="ea-tag ea-tag--light">Basic date and venue documented</span></section>'+prose+'<section class="ea-panel"><h2>What the indexed source establishes</h2><div class="ea-facts"><div><small>Band / project</small><strong>'+e(s['artist'])+'</strong></div><div><small>Show date</small><strong>'+e(s['date'])+'</strong></div><div><small>Venue</small><strong>'+e(s['venue'])+'</strong></div><div><small>Location</small><strong>'+e(s['place'])+'</strong></div></div></section>'+note+'<section class="ea-panel"><h2>Research references</h2><ul class="ea-source-list">'+source_link(s['source_ids'])+'</ul><p class="ea-small">Fan-maintained databases may be updated; this snapshot does not automatically recheck external pages.</p></section><p class="ea-nav">'+a('/artists/'+s['artist_id']+'/','Artist profile →')+a('/deep-archive/','Historical context →')+a('/recordings/','Recording-source directory →')+'</p>'
 path=SITE/'era-atlas/shows'/s['id']/'index.html';path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(page(heading,heading+' at '+s['venue']+', indexed from cited show/tour records; setlist and tapes not yet researched.',s['route'],body),encoding='utf-8')

# Provide a sourced index of 11 chapters; each grounded in an explicitly cited official or fan archive.
chapters=[
 ('allmans','Allman Brothers: researched show dossiers','1969–1971 and the band’s later farewell','Founding curated dossiers','the-allman-brothers-band',None),
 ('abb-1969','Allman Brothers: 1969 origins','Sourced dates from the official 1969 show database','1969 beginnings','the-allman-brothers-band',None),
 ('abb-1970','Allman Brothers: 1970 on the road','Sourced dates from the official 1970 show database','1970 tour','the-allman-brothers-band',None),
 ('abb-1971','Allman Brothers: 1971 before October','Sourced dates from the official 1971 show database','1971 before October','the-allman-brothers-band',None),
 ('dead-spring-1977','Grateful Dead: spring 1977','The May run, with source-indexed date/venue references','1977 spring','grateful-dead',None),
 ('dead-later-1977','Grateful Dead: later in 1977','Winterland and later verified dates','1977 later','grateful-dead',None),
 ('phish-1997-europe','Phish: 1997 in Europe','Festival and club dates across Europe','1997 Europe','phish',None),
 ('phish-1997-summer','Phish: summer 1997','U.S. tour and The Great Went','1997 U.S. summer','phish',None),
 ('phish-1997-fall','Phish: fall 1997','The tour popularly called Phish Destroys America','1997 fall','phish',None),
 ('phish-1998-summer','Phish: summer 1998','The U.S. tour and Lemonwheel dates','1998 U.S. summer','phish',None),
 ('phish-1998-fall','Phish: fall 1998','Halloween, Hampton and the autumn tour','1998 fall','phish',None),
 ('goose-2024','Goose: selected 2024 dates','Documented performances and appearances, not a complete band history','2024 tour and appearances','goose',None),
]
def chapter_items(era,artist):
 if era=='Founding curated dossiers':return [x for x in index if x['artist_id']==artist and x['kind']=='researched_dossier']
 return [x for x in index if x['era']==era and x['artist_id']==artist]
for slug,title,description,era,artist,_ in chapters:
 items=chapter_items(era,artist)
 assert items,(slug,era)
 refs=sorted({x for s in raw['indexed_events'] if s['era']==era for x in s['source_ids']})
 cards=''.join('<li>'+a(s['route'],s['date']+' · '+s['venue']+' · '+s['place'])+' <span class="ea-small">('+('researched dossier' if s['kind']=='researched_dossier' else 'source-indexed')+')</span></li>' for s in items)
 body='<p>'+a('/era-atlas/','← All Archive Atlas chapters')+'</p><section class="ea-hero"><div class="eyebrow">HISTORICAL TOUR / SOURCE DIRECTORY</div><h1>'+e(title)+'</h1><p class="lead">'+e(description)+'</p><div class="ea-metrics"><div><b>'+str(len(items))+'</b><small>Indexed performance records</small></div></div></section><div class="ea-notice">This chapter is a selected, source-indexed sequence, not a complete biography, setlist archive or recording census. Links marked “researched dossier” contain deeper editorial evidence. All others document only the date, venue and location.</div><section class="ea-panel"><h2>Indexed performances</h2><ol>'+cards+'</ol></section><section class="ea-panel"><h2>Research foundation</h2>'+('<ul>'+source_link(refs)+'</ul>' if refs else '<p>Each founding dossier links directly to its own primary record.</p>')+'</section>'
 route='/era-atlas/chapters/'+slug+'/'
 path=SITE/'era-atlas/chapters'/slug/'index.html';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(page(title,description,route,body),encoding='utf-8')

# One discoverable index includes both 164 new pointers and the 25 original full dossiers.
def card(s):
 spotlight=s.get('spotlight')
 search=' '.join([s['artist'],s['date'],s['venue'],s['place'],s['era'],(spotlight or {}).get('title',''),(spotlight or {}).get('summary','')]).casefold()
 return '<a class="ea-card" data-artist="'+e(s['artist_id'])+'" data-year="'+e(s['date'][:4])+'" data-kind="'+e(s['kind'])+'" data-search="'+e(search)+'" href="'+e(s['route'])+'"><span class="ea-tag'+(' ea-tag--light' if s['kind']=='source_index_only' else '')+'">'+('Date & venue only' if s['kind']=='source_index_only' else 'Researched dossier')+'</span><h3>'+e(s['date']+' · '+s['artist'])+'</h3><p>'+e(s['venue']+' · '+s['place'])+'</p>'+('<p class="ea-small">'+e(spotlight['title'])+'</p>' if spotlight else '')+'<p class="ea-small">'+e(s['era'])+'</p></a>'
chapter_links=''.join('<li>'+a('/era-atlas/chapters/'+slug+'/',title+' →')+'</li>' for slug,title,_,_,_,_ in chapters)
years=sorted({x['date'][:4] for x in index})
body='<section class="ea-hero"><div class="eyebrow">THE JAM ARCHIVE / v0.13 SOURCE INDEX</div><h1>History is bigger<br>than the <em>legendary nights.</em></h1><p class="lead">A sourced entryway to the concerts around the classics. Explore the Allmans’ 1969–71 dates, the Grateful Dead in 1977, Phish’s 1997–98 tours, and Goose’s 2024 performances. The earliest Allmans shows remain especially dependent on the official historical database. Every record tells you how much we actually know.</p><div class="ea-metrics"><div><b>'+str(unique_performance_count)+'</b><small>Distinct indexed records</small></div><div><b>'+str(source_index_count)+'</b><small>New date / venue pointers</small></div><div><b>'+str(len(old))+'</b><small>Original concert dossiers</small></div><div><b>'+str(enriched)+'</b><small>New spotlight notes</small></div></div></section><div class="ea-notice"><strong>Two evidence levels:</strong> “Researched dossier” links to our existing editorial concert pages. “Date & venue only” means the cited show or tour index substantiates that basic listing; it does not establish a setlist, lineup, guest appearance, surviving recording or completeness. <strong>Not an automatic scrape.</strong> All records were editorially selected and date-stamped.</div><div class="ea-nav">'+a('/time-machine/','Original Time Machine →')+a('/deep-archive/','Deep Archive →')+a('/performance-lab/','Performance Lab →')+a('/contribute/','Contribute a correction →')+'</div><section class="ea-panel"><h2>Follow a historical chapter</h2><ul>'+chapter_links+'</ul></section><section aria-label="Explore performances"><h2>Browse all indexed nights</h2><div class="ea-controls"><label for="ea-search">Search date, venue or city<input id="ea-search" type="search" autocomplete="off" placeholder="Try 1997 Denver, Winterland, Goose…"></label><label for="ea-artist">Artist<select id="ea-artist"><option value="">All artists</option>'+''.join('<option value="'+k+'">'+v+'</option>' for k,v in [('the-allman-brothers-band','Allman Brothers Band'),('grateful-dead','Grateful Dead'),('phish','Phish'),('goose','Goose')])+'</select></label><label for="ea-year">Year<select id="ea-year"><option value="">Every year</option>'+''.join('<option value="'+e(y)+'">'+e(y)+'</option>' for y in years)+'</select></label><label for="ea-kind">Evidence level<select id="ea-kind"><option value="">Both levels</option><option value="researched_dossier">Detailed dossier</option><option value="source_index_only">Date/venue pointer</option></select></label></div><p id="ea-results" role="status" aria-live="polite" class="ea-small">'+str(unique_performance_count)+' indexed performances.</p><div class="ea-grid">'+''.join(card(s) for s in sorted(index,key=lambda s:(s['date'],s['id']),reverse=True))+'</div></section>'
p=SITE/'era-atlas/index.html';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(page('Archive Atlas', 'Evidence-graded directory of '+str(unique_performance_count)+' concerts by the Allman Brothers, Grateful Dead, Phish and Goose.', '/era-atlas/', body),encoding='utf-8')

# Integrate navigational link globally, including the top of original 324 HTML routes.
for file in SITE.rglob('*.html'):
 if file.is_relative_to(SITE/'era-atlas'):continue
 html=file.read_text(encoding='utf-8')
 if '<nav aria-label="Archive sections">' in html:
  html=html.replace('<nav aria-label="Archive sections">','<nav aria-label="Archive sections"><a href="/era-atlas/">Archive Atlas</a>',1)
 elif file==SITE/'index.html':
  marker='<a class="outlink" href="performance-lab/">Performance Lab: trace the actual musical moments →</a>'
  if marker in html:html=html.replace(marker,'<a class="outlink" href="era-atlas/">Archive Atlas: explore '+str(unique_performance_count)+' indexed concerts →</a><div class="divider"></div>'+marker,1)
 # Cross-link the four artist pages with source grounded record counts.
 for artist in ('the-allman-brothers-band','grateful-dead','phish','goose'):
  if file==SITE/'artists'/artist/'index.html':
   n=sum(x['artist_id']==artist for x in index)
   panel='<section class="card"><div class="eyebrow">ARCHIVE ATLAS · v0.13</div><h2>'+str(n)+' indexed performance record'+('s' if n!=1 else '')+'</h2><p class="tiny">Includes fully researched dossiers and separately labeled date-and-venue source pointers; not a complete concert chronology.</p>'+a('/era-atlas/?artist='+artist,'Explore the indexed history →')+'</section>'
   assert html.count('<footer>')==1
   html=html.replace('<footer>',panel+'<footer>',1)
 if file==SITE/'index.html':html=html.replace('PUBLIC BETA · v0.12','PUBLIC BETA · v0.13')
 file.write_text(html,encoding='utf-8')

# Sitemaps are generated from actual output files, so pages cannot be silently omitted.
ET.register_namespace('','http://www.sitemaps.org/schemas/sitemap/0.9');ns='{http://www.sitemaps.org/schemas/sitemap/0.9}'
sp=SITE/'sitemap.xml';tree=ET.parse(sp)
existing_urls={node.text for node in tree.getroot().iter(ns+'loc')}
for file in sorted((SITE/'era-atlas').rglob('index.html')):
 route='/'+str(file.parent.relative_to(SITE)).replace('\\','/')+'/'
 url=ORIGIN+route
 assert url not in existing_urls,url
 ET.SubElement(ET.SubElement(tree.getroot(),ns+'url'),ns+'loc').text=url
sp.write_text(ET.tostring(tree.getroot(),encoding='unicode',xml_declaration=True),encoding='utf-8')
report_path=SITE/'assets/build_report.json';report=json.loads(report_path.read_text(encoding='utf-8'))
report.update(version='0.13', era_atlas_records=unique_performance_count,era_atlas_new_source_pointers=source_index_count,era_atlas_original_dossiers=len(old),era_atlas_spotlights=enriched,era_atlas_chapters=len(chapters),site_files=sum(f.is_file() for f in SITE.rglob('*')))
report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('v0.13 Archive Atlas:',unique_performance_count,'unique records,',source_index_count,'new source pointers,',len(old),'original researched dossiers,',enriched,'spotlights,',len(chapters),'chapters')
