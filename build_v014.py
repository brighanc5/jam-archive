#!/usr/bin/env python3
"""v0.14: source-based show studies and repertoire index over versioned editorial records.

No network access in build. No automated extraction of pages. Facts and sequence
markers are from 13 human-reviewed original URLs; data/source review is explicit.
"""
from collections import defaultdict
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import urlsplit
import json, os, re, subprocess, sys, unicodedata, xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent
subprocess.run([sys.executable,str(ROOT/'build_v013.py')],cwd=ROOT,check=True)
SITE=ROOT/'site'
ORIGIN=os.environ.get('JAM_ARCHIVE_ORIGIN','https://thejamarchive.org').rstrip('/')
assert ORIGIN.startswith('https://')
meta=json.loads((ROOT/'data/show_depth_v014.json').read_text(encoding='utf-8'))
assert meta['version']=='0.14' and meta['reviewed_on']=='2026-10-29'
assert len(meta['studies'])==17 and len(meta['sources'])==13
cat=json.loads((SITE/'assets/catalog.json').read_text(encoding='utf-8'))
atlas=json.loads((SITE/'assets/era-atlas.json').read_text(encoding='utf-8'))
assert len(atlas['events'])==361
artists={x['id']:x['name'] for x in cat['entities']}
canon={(x['artist_id'],x['date']):[] for x in cat['historical_shows']}
for x in cat['historical_shows']:canon[(x['artist_id'],x['date'])].append(x)
indexed={(x['artist_id'],x['date']):x for x in atlas['events']}

def E(s):return escape(str(s),quote=True)
def slug(t):
 t=unicodedata.normalize('NFKD',t).encode('ascii','ignore').decode().lower()
 return re.sub('-+','-',re.sub('[^a-z0-9]+','-',t)).strip('-')
def link(url,title):return '<a href="'+E(url)+'">'+E(title)+'</a>'
def ext(url,title):return '<a href="'+E(url)+'" rel="noopener noreferrer" target="_blank">'+E(title)+' ↗</a>'
def write(rel,content):
 p=SITE/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content,encoding='utf-8')
def page(title,desc,route,body):
 return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="'+E(desc[:250])+'"><meta property="og:title" content="'+E(title)+' · The Jam Archive"><meta property="og:description" content="'+E(desc[:250])+'"><title>'+E(title)+' · The Jam Archive</title><link rel="canonical" href="'+E(ORIGIN+route)+'"><link rel="stylesheet" href="/assets/detail.css"><link rel="stylesheet" href="/assets/site-quality.css"><link rel="stylesheet" href="/assets/show-depth.css"><script src="/assets/show-depth.js" defer></script></head><body><a class="ja-skip" href="#ja-main">Skip to main content</a><header><a href="/">THE <span>JAM</span> ARCHIVE</a><nav aria-label="Archive sections"><a href="/">Discover</a><a href="/era-atlas/">Archive Atlas</a><a href="/show-depth/">Show Studies</a><a href="/repertoire/">Repertoire</a><a href="/deep-archive/">Deep Archive</a><a href="/performance-lab/">Performance Lab</a><a href="/connections/">Family Tree</a><a href="/contribute/">Contribute</a></nav></header><main id="ja-main"><div class="sd-wrap">'+body+'</div><footer>The Jam Archive · independent, fan-built, source-first · reviewed '+E(meta['reviewed_on'])+' · Original recordings are not hosted here</footer></main></body></html>'

def study_route(s):return '/show-depth/'+s['id']+'/'
def title_route(t):return '/repertoire/songs/'+slug(t)+'/'
def source_links(s):return '<ul class="sd-list">'+''.join('<li class="sd-source">'+ext(meta['sources'][sid]['url'],meta['sources'][sid]['title'])+' · '+E(meta['sources'][sid]['type'].replace('_',' '))+'</li>' for sid in s['source_ids'])+'</ul>'

seen=set();occurrences=defaultdict(list); total_positions=0; transitions=0;guest_count=0
for key,src in meta['sources'].items():
 url=urlsplit(src['url']);assert url.scheme=='https' and url.netloc and '@' not in url.netloc,key
for s in meta['studies']:
 assert s['id'] not in seen and re.fullmatch(r'[a-z0-9-]+',s['id']);seen.add(s['id'])
 assert s['artist_id'] in artists and date.fromisoformat(s['date'])<=date(2026,10,29)
 assert s['source_ids'] and all(sid in meta['sources'] for sid in s['source_ids'])
 assert s['evidence_scope'] in {'official_release_track_order','official_show_setlist','community_curated_setlist','artist_official_setlist_and_release'}
 assert s['sections'] and all(sec['tracks'] for sec in s['sections'])
 for section in s['sections']:
  assert [x['position'] for x in section['tracks']]==list(range(1,len(section['tracks'])+1))
  assert section['tracks'][-1]['transition_after'] is None
  for t in section['tracks']:
   assert t['title'] and t['transition_after'] in (None,'>','->')
   occurrences[t['title']].append({'study':s['id'],'artist':artists[s['artist_id']],'date':s['date'],'set':section['name'],'position':t['position']})
   total_positions+=1;transitions+=bool(t['transition_after'])
 for guest in s['documented_guests']:
  assert guest['on_title'] in {t['title'] for sec in s['sections'] for t in sec['tracks']}
  assert all(sid in meta['sources'] for sid in guest['source_ids']);guest_count+=1
 if s['official_recording']:
  assert s['official_recording']['source_id'] in s['source_ids']
 if s['id'] not in {x['id'] for x in cat['historical_shows']}:
  # Study must at least refer to an already indexed date/venue, except one
  # new Greek Theatre official release sourced directly from Goose.
  assert (s['artist_id'],s['date']) in indexed or s['id']=='goose-2024-09-27',s['id']

assert total_positions==238 and len(occurrences)==158 and guest_count==3
assert len({slug(k) for k in occurrences})==len(occurrences),'Ambiguous slug: add title-disambiguation keys'

write('assets/show-depth.css',(ROOT/'show_depth.css').read_text(encoding='utf-8'))
write('assets/show-depth.js',(ROOT/'show_depth.js').read_text(encoding='utf-8'))
write('assets/show-depth.json',json.dumps(meta,ensure_ascii=False,separators=(',',':'))+'\n')

for s in meta['studies']:
 report=''.join('<section class="sd-panel"><h2>'+E(sec['name'])+' · '+str(len(sec['tracks']))+' positions</h2><ol class="sd-tracklist">'+''.join('<li id="track-'+str(i)+'-'+str(t['position'])+'"><span class="sd-num">'+str(t['position'])+'</span><a href="'+E(title_route(t['title']))+'">'+E(t['title'])+'</a>'+('<span class="sd-arrow" aria-label="Source marker '+E(t['transition_after'])+'">'+E(t['transition_after'])+'</span>' if t['transition_after'] else '')+'</li>' for t in sec['tracks'])+'</ol></section>' for i,sec in enumerate(s['sections'],1))
 guests=''
 if s['documented_guests']:
  guests='<section class="sd-panel"><h2>Documented guests · song specific</h2><ul class="sd-list">'+''.join('<li>'+E(g['name'])+' — '+E(g['role'])+' on <strong>'+E(g['on_title'])+'</strong>. '+ext(meta['sources'][g['source_ids'][0]]['url'],'Evidence')+'</li>' for g in s['documented_guests'])+'</ul></section>'
 recording=''
 if s['official_recording']:
  r=s['official_recording']
  recording='<section class="sd-panel"><h2>Official recording / release</h2><p><strong>'+E(r['label'])+'</strong></p><p>'+E(r['recording_scope'])+'</p><p>'+ext(meta['sources'][r['source_id']]['url'],'Original publisher')+'</p></section>'
 canon_show=next((h for h in cat['historical_shows'] if h['id']==s['id']),None)
 reference=('/shows/'+s['id']+'/') if canon_show else (indexed.get((s['artist_id'],s['date'])) or {}).get('route','/era-atlas/')
 body='<div class="sd-hero"><div class="sd-tag">THE JAM ARCHIVE / SOURCE-REVIEWED SHOW</div><h1>'+E(artists[s['artist_id']]+' · '+s['date'])+'</h1><p>'+E(s['venue']+' · '+s['place'])+'</p><div class="sd-metrics"><span><b>'+str(sum(len(z['tracks']) for z in s['sections']))+'</b>Source-documented positions</span><span><b>'+str(len(s['sections']))+'</b>Source sections</span><span><b>'+str(len(s['documented_guests']))+'</b>Guest credits</span></div></div><div class="sd-actions">'+link('/show-depth/','← Show Studies')+link(reference,'Original archive entry →')+link('/artists/'+s['artist_id']+'/','Artist profile →')+link('/repertoire/','Repertoire index →')+'</div><div class="sd-notice"><b>Evidence level:</b> '+E(s['evidence_scope'].replace('_',' '))+'. Source-published order is not necessarily the complete performance. Transition markers are reproduced from the cited record, not from independent listening. An unlisted guest, recording, or segue has not been ruled out.</div><div class="sd-columns"><div>'+report+guests+recording+'</div><aside><section class="sd-panel sd-sticky"><h2>What the evidence says</h2><p>'+E(s['context'])+'</p><p class="sd-muted">'+E(meta['editorial_standard'])+'</p>'+('<ul class="sd-list">'+''.join('<li>'+E(n)+'</li>' for n in s['research_notes'])+'</ul>' if s['research_notes'] else '')+'<h2>Original source</h2>'+source_links(s)+'<h2>Research limitations</h2><p class="sd-muted">Precise tape provenance, every musician onstage, timing, authorship, and the exact audio boundaries of transitions require separate evidence. An artist-issued digital release is not evidence that a particular microphone or master tape was used.</p></section></aside></div>'
 write('show-depth/'+s['id']+'/index.html',page(artists[s['artist_id']]+' '+s['date']+' — show study',s['venue']+' · sourced setlist and recording references with per-song provenance.',study_route(s),body))

# Source-grounded repertoire routes. Exact title matching is not composition identification.
for name,entries in occurrences.items():
 repeated=len(entries);artists_hit=len({e['artist'] for e in entries})
 items=''.join('<div class="sd-appearance">'+link(study_route(next(s for s in meta['studies'] if s['id']==e['study'])),e['artist']+' · '+e['date'])+'<div class="sd-small">'+E(e['set']+' · printed position '+str(e['position']))+'</div></div>' for e in sorted(entries,key=lambda x:(x['date'],x['study'],x['set'],x['position'])))
 body='<div class="sd-hero"><div class="sd-tag">REPERTOIRE / EXACT TITLE INDEX</div><h1>'+E(name)+'</h1><p>Follow the specific source-documented appearances of this title across our researched shows.</p><div class="sd-metrics"><span><b>'+str(repeated)+'</b>Indexed positions</span><span><b>'+str(artists_hit)+'</b>Distinct artists</span></div></div><div class="sd-actions">'+link('/repertoire/','← All indexed titles')+link('/show-depth/','Show Studies →')+'</div><div class="sd-notice"><b>Exact title only.</b> A shared title does not establish identical composition, authorship, arrangement, or a musical quotation. This index covers 17 selected shows, not all '+str(len(atlas['events']))+' performances in Archive Atlas.</div><section class="sd-panel"><h2>Source-linked appearances</h2>'+items+'</section>'
 write('repertoire/songs/'+slug(name)+'/index.html',page(name+' — documented appearances','Show-by-show references for '+name+' across selected sourced performances.',title_route(name),body))

cards=[]
for s in meta['studies']:
 nt=sum(len(z['tracks']) for z in s['sections'])
 search=(artists[s['artist_id']]+' '+s['date']+' '+s['venue']+' '+s['place']+' '+' '.join(t['title'] for sec in s['sections'] for t in sec['tracks'])).casefold()
 cards.append('<a class="sd-card" data-depth-record data-artist="'+E(s['artist_id'])+'" data-search="'+E(search)+'" href="'+E(study_route(s))+'"><span class="sd-tag">'+E(artists[s['artist_id']])+' · '+s['date']+'</span><h2>'+E(s['venue'])+'</h2><p class="sd-muted">'+E(s['place'])+' · '+str(nt)+' documented track positions</p><p class="sd-small">'+E(s['evidence_scope'].replace('_',' '))+'</p></a>')
body='<div class="sd-hero"><div class="sd-tag">THE JAM ARCHIVE · v0.14</div><h1>Beyond the show date.<br>Inside the performance.</h1><p>Source-reviewed setlists, official release sequences, narrowly attributed guest appearances, and recording references. Investigate the Allmans at Fillmore East, the Dead in 1977, Phish in fall 1997, and Goose in 2024.</p><div class="sd-metrics"><span><b>17</b>Sourced show studies</span><span><b>'+str(total_positions)+'</b>Track positions</span><span><b>'+str(transitions)+'</b>Printed transitions</span><span><b>'+str(len(meta['sources']))+'</b>Original sources</span></div></div><div class="sd-actions">'+link('/era-atlas/','Archive Atlas →')+link('/repertoire/','Source-backed song index →')+link('/performance-lab/','Performance Lab →')+'</div><div class="sd-notice">Every show includes direct source attribution and a clear evidence level. The 17 studies are a curated selection, not a claim that the remaining shows lack tapes or setlists.</div><section class="sd-panel"><h2>Find a researched concert</h2><div class="sd-controls"><label for="sd-search">Search song, date, venue or artist<input id="sd-search" type="search" placeholder="Try Elvin Bishop, Ghost, Forest Hills…"></label><label for="sd-artist">Artist<select id="sd-artist"><option value="">All artists</option>'+''.join('<option value="'+E(k)+'">'+E(artists[k])+'</option>' for k in ('the-allman-brothers-band','grateful-dead','phish','goose'))+'</select></label></div><p id="sd-count" role="status" aria-live="polite" class="sd-small">17 documented results</p><div class="sd-grid">'+''.join(cards)+'</div></section>'
write('show-depth/index.html',page('Show Studies','Deep, source-linked concert setlists, release contexts, guest credits and recording references.','/show-depth/',body))

sort_titles=sorted(occurrences,key=str.casefold)
song_cards=''.join('<a class="sd-card" data-depth-record data-search="'+E((n+' '+' '.join(e['artist'] for e in occurrences[n])).casefold())+'" href="'+E(title_route(n))+'"><span class="sd-tag">'+str(len(occurrences[n]))+' studied appearances</span><h2>'+E(n)+'</h2><p class="sd-small">'+str(len({e['artist'] for e in occurrences[n]}))+' artist(s)</p></a>' for n in sort_titles)
body='<div class="sd-hero"><div class="sd-tag">THE JAM ARCHIVE / DOCUMENTED REPERTOIRE</div><h1>Find the song.<br>Find the night.</h1><p>158 exact song-title entries link directly to the researched show where each appears. This is a factual title index—not a musicological determination that same-named songs share a composition.</p><div class="sd-metrics"><span><b>'+str(len(occurrences))+'</b>Exact titles</span><span><b>'+str(total_positions)+'</b>Documented positions</span><span><b>17</b>Selected performances</span></div></div><div class="sd-actions">'+link('/show-depth/','Show Studies →')+link('/song-paths/','Original Song Paths →')+'</div><div class="sd-notice">Research boundary: the title index covers the new reviewed 17-show dataset. It is not a claim to include every performance, cover, alternate title, tease, or song in the wider archive.</div><section class="sd-panel"><h2>Browse 158 source-backed titles</h2><div class="sd-controls"><label for="sd-search">Find a title or performer<input id="sd-search" type="search" placeholder="Try Mountain Jam, Thatch, Fire…"></label></div><p id="sd-count" role="status" aria-live="polite">158 results</p><div class="sd-grid">'+song_cards+'</div></section>'
write('repertoire/index.html',page('Repertoire Index','Source-linked appearances for 158 indexed song titles across 17 researched shows.','/repertoire/',body))

# Relevant new notes on existing Atlas and canonical concert records.
for s in meta['studies']:
 targets=[]
 canonical=SITE/'shows'/s['id']/'index.html'
 if canonical.is_file():targets.append(canonical)
 atlas_record=SITE/'era-atlas/shows'/s['id']/'index.html'
 if atlas_record.is_file():targets.append(atlas_record)
 for target in targets:
  html=target.read_text(encoding='utf-8')
  insert='<section class="card"><h2>New: v0.14 source-reviewed show study</h2><p>A full documented track sequence, source-recorded transitions, release context, and narrowly credited guests.</p><p>'+link(study_route(s),'Explore the sourced show study →')+'</p></section>'
  if 'id="ja-main"' in html:
   assert '<footer>' in html
   html=html.replace('<footer>',insert+'<footer>',1)
  else:
   assert '</main>' in html
   html=html.replace('</main>',insert+'</main>',1)
  target.write_text(html,encoding='utf-8')

for path in [SITE/'index.html', SITE/'era-atlas/index.html']:
 html=path.read_text(encoding='utf-8')
 introduction='<section class="card"><div class="eyebrow">NEW · v0.14 SOURCE RESEARCH</div><h2>17 detailed show studies · 238 recorded track positions</h2><p>See sourced setlists, song-specific guest evidence and official recording references for the Allmans, Grateful Dead, Phish and Goose.</p><p>'+link('/show-depth/','Explore Show Studies →')+' · '+link('/repertoire/','Explore the Repertoire →')+'</p></section>'
 assert '<footer' in html
 html=html.replace('<footer',introduction+'<footer',1)
 path.write_text(html,encoding='utf-8')
for aid in ('the-allman-brothers-band','grateful-dead','phish','goose'):
 p=SITE/'artists'/aid/'index.html'
 html=p.read_text(encoding='utf-8')
 n=sum(s['artist_id']==aid for s in meta['studies'])
 snippet='<section class="card"><h2>'+str(n)+' source-reviewed show studies</h2><p>Documented song positions, original source URLs and recording context.</p><p>'+link('/show-depth/?artist='+aid,'Explore the studies →')+'</p></section>'
 assert '<footer>' in html
 p.write_text(html.replace('<footer>',snippet+'<footer>',1),encoding='utf-8')

# Global navigation (do not insert twice into existing unrelated navs).
for f in SITE.rglob('*.html'):
 if f.is_relative_to(SITE/'show-depth') or f.is_relative_to(SITE/'repertoire'):continue
 html=f.read_text(encoding='utf-8')
 marker='<nav aria-label="Archive sections">'
 if marker in html:html=html.replace(marker,marker+'<a href="/show-depth/">Show Studies</a><a href="/repertoire/">Repertoire</a>',1)
 f.write_text(html,encoding='utf-8')

# Reconstruct sitemap from final generated HTML rather than assuming old route count.
ns='http://www.sitemaps.org/schemas/sitemap/0.9';ET.register_namespace('',ns)
root=ET.Element('{'+ns+'}urlset')
for p in sorted(SITE.rglob('index.html')):
 route='/' if p.parent==SITE else '/'+str(p.parent.relative_to(SITE)).replace('\\','/')+'/'
 ET.SubElement(ET.SubElement(root,'{'+ns+'}url'),'{'+ns+'}loc').text=ORIGIN+route
write('sitemap.xml',ET.tostring(root,encoding='unicode',xml_declaration=True))
report_path=SITE/'assets/build_report.json';report=json.loads(report_path.read_text())
report.update(version='0.14',show_depth_studies=len(meta['studies']),show_depth_sources=len(meta['sources']),show_depth_track_positions=total_positions,show_depth_source_transitions=transitions,show_depth_guest_credits=guest_count,show_depth_repertoire_titles=len(occurrences),show_depth_new_routes=len(meta['studies'])+len(occurrences)+2,site_files=sum(p.is_file() for p in SITE.rglob('*')))
write('assets/build_report.json',json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('v0.14:',len(meta['studies']),'full show studies,',total_positions,'documented track positions,',len(occurrences),'title routes,',transitions,'source-marked transitions,',guest_count,'guest credits')
