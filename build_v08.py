#!/usr/bin/env python3
"""Static v0.8 Time Machine. Curated claims only. Zero network activity at build/runtime."""
from pathlib import Path
from html import escape
from collections import Counter, defaultdict
from datetime import date
import json, os, subprocess, sys, xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent
subprocess.run([sys.executable,str(ROOT/'build_v07.py')],cwd=ROOT,check=True)
site=ROOT/'site'
cat=json.loads((site/'assets/catalog.json').read_text(encoding='utf-8'))
origin=os.environ.get('JAM_ARCHIVE_ORIGIN','').rstrip('/')
assert origin.startswith('https://')
shows=cat['historical_shows']
recordings=defaultdict(list)
for r in cat['recording_sources']:
    recordings[r['show_id']].append(r)
# Two deliberately bounded collections; no suggestion of exhaustive coverage.
chosen=sorted((h for h in shows if
    (h['artist_id']=='the-allman-brothers-band' and '1969'<=h['date'][:4]<='1971') or
    (h['artist_id']=='grateful-dead' and h['date'].startswith('1977-05-'))),
    key=lambda x:(x['date'],x['artist'],x['slot']))
assert len(chosen)==22, f'Expected 15 original-era ABB and 7 May 77 Dead shows, got {len(chosen)}'
assert len(shows)==25 and len(cat['recording_sources'])>=17
assert sum(not h['songs'] for h in chosen)==5, 'Source-unknown setlists should stay visible as unknown'

def e(s):return escape(str(s),quote=True)

def card(h):
    rr=recordings[h['id']]
    songline=''.join('<span class="tm-chip">'+e(x)+'</span>' for x in h['songs'][:5]) if h['songs'] else '<span class="tm-chip missing">Setlist not established</span>'
    source_note='\u00b7 '+str(len(rr))+' linked recording / release '+('sources' if len(rr)!=1 else 'source') if rr else '\u00b7 no reviewed tape or release link indexed'
    internal='../shows/'+h['id']+'/index.html'
    return '''<article class="tm-show" data-artist="%s" data-year="%s" data-sources="%d">
    <div class="tm-date">%s &nbsp;·&nbsp; %s</div>
    <h3>%s</h3><div class="tm-location">%s, %s %s</div>
    <p class="tm-note">%s</p><div class="tm-chips">%s</div>
    <div class="tm-actions"><a href="%s">Explore dossier →</a><a href="%s" target="_blank" rel="noopener noreferrer">Original show record ↗</a></div>
    <div class="tm-fineprint">%s</div></article>''' % (e(h['artist']),e(h['date'][:4]),len(rr),e(h['date']),e(h['artist']),e(h['venue']),e(h['city']),e(h['region']),e(h['slot']),e(h['highlight']),songline,e(internal),e(h['source_url']),e(source_note))

def chapter(year,rows):
    return '<section class="tm-year-group" aria-label="'+e(year)+'"><h2 class="tm-year">'+e(year)+'</h2><div class="tm-list">'+''.join(card(h) for h in rows)+'</div></section>'
byyear=defaultdict(list)
for h in chosen:byyear[h['date'][:4]].append(h)
chapters=''.join(chapter(yr,byyear[yr]) for yr in sorted(byyear))
count_recording_sources=sum(len(recordings[x['id']]) for x in chosen)
html='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Follow source-documented performances by the early Allman Brothers Band and the Grateful Dead's May 1977 tour. Verify shows, known setlist excerpts, and archival releases."><meta property="og:title" content="Time Machine · The Jam Archive"><title>Time Machine · The Jam Archive</title><link rel="canonical" href="'''+e(origin+'''/time-machine/''')+'''"><link rel="stylesheet" href="../assets/detail.css"><link rel="stylesheet" href="../assets/time-machine.css"><script src="../assets/time-machine.js" defer></script></head><body>
<header><a href="../index.html">THE <span>JAM</span> ARCHIVE</a><nav><a href="../index.html">Discover</a><a href="../recordings/index.html">Recording Explorer</a><a href="../trails/index.html">Listening trails</a><a href="../contribute/index.html">Contribute</a></nav></header><main>
<div class="tm-head"><div class="tm-kicker">THE JAM ARCHIVE / HISTORICAL FIELD GUIDE</div><h1>Go back.<br>Follow the music.</h1><p class="tm-sub">Explore two remarkable stretches of live-music history: the original Allman Brothers' climb toward <em>At Fillmore East</em>, and the Grateful Dead's May 1977 run. Each date is tied to an original show source. Where we don't know a setlist or recording, we say so.</p>
<div class="tm-meta"><div class="tm-metric"><b>'''+str(len(chosen))+'''</b><span>Indexed performances</span></div><div class="tm-metric"><b>'''+str(count_recording_sources)+'''</b><span>Linked release/tape entries</span></div><div class="tm-metric"><b>4</b><span>Historical years represented</span></div></div>
<div class="tm-hero-links"><a href="../recordings/index.html">Explore the recording sources →</a><a href="../contribute/index.html">Help verify a missing tape →</a></div></div>
<div class="tm-editorial"><div class="tm-feature"><div class="tm-chapter-count">CHAPTER 01 · 1969–1971</div><h2>Before the peach.</h2><p>The Allmans' early stages, festival sets, multiple Fillmore East performances, and the remarkable final Duane Allman recording. Dates, setlist details and tape provenance must be checked independently—not collapsed into one legendary night.</p></div>
<div class="tm-feature alt"><div class="tm-chapter-count">CHAPTER 02 · MAY 1977</div><h2>After Cornell.</h2><p>New Haven, Boston, Ithaca, Buffalo, St. Paul and Chicago. See what surrounded Cornell 5/8/77, then distinguish the tapes fans circulated from the later official box set.</p></div></div>
<div class="warning">This is a deliberately small source-linked selection, not the complete touring history or tape census. Early-show times and some recording dates are contested. A show listing is not evidence that a recording exists. External media belongs to its respective custodian.</div>
<section aria-label="Explore historical performances"><div class="tm-controls">
<label for="tm-search">Search performances<input id="tm-search" type="search" placeholder="Venue, song, place, 1977…" autocomplete="off"></label>
<label for="tm-artist">Artist<select id="tm-artist"><option value="">Both artists</option><option value="The Allman Brothers Band">Allman Brothers</option><option value="Grateful Dead">Grateful Dead</option></select></label>
<label for="tm-year">Year<select id="tm-year"><option value="">All years</option><option value="1969">1969</option><option value="1970">1970</option><option value="1971">1971</option><option value="1977">1977</option></select></label>
<label class="tm-toggle" for="tm-recorded"><span>Recording availability</span><span class="tm-checkline"><input id="tm-recorded" type="checkbox">Only with a tape or release</span></label>
</div><p class="tm-results" id="tm-results" role="status" aria-live="polite">'''+str(len(chosen))+''' source-linked performances</p><div id="tm-empty" class="tm-empty" hidden>No entries match these filters. You can change the year or artist, or uncheck the recording filter.</div>'''+chapters+'''</section>
<div class="card"><h2>What does “documented” mean?</h2><p>We independently index <strong>performances</strong>, <strong>setlist evidence</strong>, and <strong>recording or release references</strong>. The date of a concert does not establish the date written on a tape box. A commercial album may combine multiple nights. Use each dossier's source links and notes to evaluate the record.</p><p class="tm-fineprint">Editorial check: October 28, 2026. This site does not host concert audio, album art, or scraped source content. It is not affiliated with the bands or record labels.</p></div>
<footer>THE JAM ARCHIVE · Independent fan research · Sources remain with their publishers. <a href="../about/index.html">Editorial policy</a></footer></main></body></html>'''
p=site/'time-machine/index.html';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(html,encoding='utf-8')
(site/'assets/time-machine.css').write_text((ROOT/'time_machine.css').read_text(encoding='utf-8'),encoding='utf-8')
(site/'assets/time-machine.js').write_text((ROOT/'time_machine.js').read_text(encoding='utf-8'),encoding='utf-8')
# Homepage contextual link and current release label.
home=site/'index.html';s=home.read_text(encoding='utf-8');marker='<a class="outlink" href="recordings/index.html">Explore recording sources →</a>'
assert s.count(marker)==1
s=s.replace(marker,'<a class="outlink" href="time-machine/index.html">Step into the Time Machine →</a><div class="divider"></div>'+marker)
s=s.replace('PUBLIC BETA · v0.7','PUBLIC BETA · v0.8')
home.write_text(s,encoding='utf-8')
# Prominent link from the other source-first page.
rec=site/'recordings/index.html';s=rec.read_text(encoding='utf-8');needle='<a href="../trails/index.html">Listening trails</a>'
assert s.count(needle)==1
s=s.replace(needle,'<a href="../time-machine/index.html">Time Machine</a>'+needle)
rec.write_text(s,encoding='utf-8')
# Add to sitemap, using the same verified origin as the other builder steps.
ET.register_namespace('','http://www.sitemaps.org/schemas/sitemap/0.9')
ns='{http://www.sitemaps.org/schemas/sitemap/0.9}'
tree=ET.parse(site/'sitemap.xml');locs={x.text for x in tree.getroot().iter(ns+'loc')};url=origin+'/time-machine/'
assert url not in locs
el=ET.SubElement(tree.getroot(),ns+'url');ET.SubElement(el,ns+'loc').text=url
tree.write(site/'sitemap.xml',encoding='unicode',xml_declaration=True)
# Version/report includes real counts, not formerly hardcoded v0.7 deltas.
reportp=site/'assets/build_report.json'; report=json.loads(reportp.read_text(encoding='utf-8'))
report.update(version='0.8',historical_shows=len(shows),recording_references=len(cat['recording_sources']),
              time_machine=True,time_machine_performances=len(chosen),
              source_unknown_setlists=sum(not x['songs'] for x in chosen),
              site_files=sum(f.is_file() for f in site.rglob('*')))
reportp.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(f'v0.8 Time Machine: {len(shows)} total historic show dossiers; '
      f'{len(cat["recording_sources"])} reviewed source references; '
      f'{len(chosen)} curated timeline performances; {len(byyear)} years')
