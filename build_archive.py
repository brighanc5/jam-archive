#!/usr/bin/env python3
"""Rebuild The Jam Archive v0.2 from the original founding registry and sourced enrichment.
All data is locally stored, source-first, no audio files downloaded.
"""
import json, sqlite3, subprocess, sys, unicodedata, re
from pathlib import Path
from datetime import date
ROOT=Path(__file__).resolve().parent
subprocess.run([sys.executable, str(ROOT/'seed_v01.py')],cwd=ROOT,check=True,capture_output=True)
CAT=ROOT/'catalog.json'
data=json.loads(CAT.read_text())
entities={e['id']:e for e in data['entities']}
nameid={e['name']:e['id'] for e in data['entities']}
def slug(s):
 return re.sub(r'-+','-',re.sub('[^a-z0-9]+','-',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower())).strip('-')
def add_person(name,aliases=None):
 id=slug(name)
 if id not in entities:
  e={'id':id,'name':name,'type':'person','origins':['related'],'aliases':aliases or []}
  entities[id]=e; data['entities'].append(e);nameid[name]=id
 return id
for name in ['Peter Anspach','Trevor Weekz','Cotter Ellis','Bill Kreutzmann','Mickey Hart','John Mayer','John Bell','John “JoJo” Hermann','Dave Schools','Duane Trucks','Billy Martin','Chris Wood','Gregg Allman','Duane Allman','Butch Trucks','Duane Betts','Colonel Bruce Hampton','Steve Kimock','Jeff Chimenti']:
 add_person(name)
for name,typ in [('Dead & Company','band'),('Oteil & Friends','project'),('Old & In the Way','band')]:
 id=slug(name)
 if id not in entities:
  e={'id':id,'name':name,'type':typ,'origins':['related'],'aliases':[]}
  entities[id]=e;data['entities'].append(e);nameid[name]=id
# Strongly sourced relationships, distinct from one-off guest appearances at specific concerts.
rels=data['relationships'];rel_keys={(r['from'],r['to'],r['type']) for r in rels}
def add_rel(person,group,url,notes='',rel='member_of'):
 key=(nameid[person],nameid[group],rel)
 if key not in rel_keys:
  rels.append({'from':key[0],'to':key[1],'type':rel,'source_url':url,'note':notes,'verification':'verified'});rel_keys.add(key)
for person in ['Rick Mitarotonda','Peter Anspach','Trevor Weekz','Cotter Ellis']:
 add_rel(person,'Goose','https://www.goosetheband.com/about')
add_rel('Jimmy Herring','Widespread Panic','https://widespreadpanic.com/band/')
for person in ['John Bell','John “JoJo” Hermann','Dave Schools','Duane Trucks']:
 add_rel(person,'Widespread Panic','https://widespreadpanic.com/band/')
for person in ['Jerry Garcia','Bob Weir','Phil Lesh','Bill Kreutzmann','Mickey Hart']:
 add_rel(person,'Grateful Dead','https://www.dead.net/about', 'Historical membership; this is not an active touring lineup')
add_rel('Jerry Garcia','Jerry Garcia Band','https://media.jerrygarcia.com/band/jerry-garcia-band/','Historical; project ended in 1995')
add_rel('Jerry Garcia','New Riders of the Purple Sage','https://media.jerrygarcia.com/bands/','Early membership, 1969–1971')
add_rel('Dickey Betts','The Allman Brothers Band','https://allmanbrothersband.com/biography/dickey-betts/','Historical membership; Dickey Betts died in 2024')
add_rel('Dickey Betts','Dickey Betts & Great Southern','https://allmanbrothersband.com/biography/dickey-betts/','Historical membership; not an indication of present lineup')
add_rel('Oteil Burbridge','The Allman Brothers Band','https://www.oteilburbridge.com/bands','Historical membership beginning 1997')
add_rel('Oteil Burbridge','Tedeschi Trucks Band','https://www.oteilburbridge.com/bands','Founding member, historical')
add_rel('Oteil Burbridge','Aquarium Rescue Unit','https://www.oteilburbridge.com/about','Early member')
add_rel('Oteil Burbridge','Dead & Company','https://www.oteilburbridge.com/bands')
add_rel('Oteil Burbridge','Oteil & Friends','https://www.oteilburbridge.com/bands','Rotating group')
for person in ['Bob Weir','Bill Kreutzmann','Mickey Hart','John Mayer']:
 add_rel(person,'Dead & Company','https://www.oteilburbridge.com/bands')
for person in ['John Medeski','Billy Martin','Chris Wood']:
 add_rel(person,'Medeski Martin & Wood','https://www.medeskimartinandwood.com/about')
add_rel('John Medeski','The Word','https://www.johnmedeski.com/about','Collaborative project')
add_rel('John Popper','Blues Traveler','https://www.roundhillrecords.com/artists/blues-traveler')
add_rel('Joe Russo',"Joe Russo's Almost Dead",'https://joerussosalmostdead.com/','Founding musician; project name and personnel should be double-checked against official biography')
# historical personnel below: supported by official legacy material
for p in ['Gregg Allman','Duane Allman','Butch Trucks']:
 add_rel(p,'The Allman Brothers Band','https://allmanbrothersband.com/','Historical')
add_rel('Colonel Bruce Hampton','Aquarium Rescue Unit','https://www.oteilburbridge.com/about','Historical collective')
# Official data sources and informational linkouts, not blanket copying rights.
new_sources=[
 ('goose-official','Goose / official','https://www.goosetheband.com/about','artist lineup','Goose'),
 ('goose-shows','Goose / live releases & shows','https://goosetheband.bandcamp.com/','artist show listing','Goose'),
 ('panic-tour','Widespread Panic / official shows','https://widespreadpanic.com/shows/','tour schedule','Widespread Panic'),
 ('trey-tour','Trey Anastasio / official tour','https://trey.com/tour/','tour schedule','Trey Anastasio'),
 ('trey-benefit','Trey + Billy official collaboration announcement','https://trey.com/dsfbenefit/','confirmed collaboration','Trey Anastasio'),
 ('ttb-tour','Tedeschi Trucks Band / tour','https://www.tedeschitrucksband.com/tour','tour schedule','Tedeschi Trucks Band'),
 ('jrad-tour',"Joe Russo's Almost Dead / official",'https://joerussosalmostdead.com/','tour schedule',"Joe Russo's Almost Dead"),
 ('panic-band','Widespread Panic / band','https://widespreadpanic.com/band/','personnel relationships','Widespread Panic'),
 ('garcia-bands','Jerry Garcia official band history','https://media.jerrygarcia.com/bands/','historical membership','Jerry Garcia'),
 ('oteil-bands','Oteil Burbridge official projects','https://www.oteilburbridge.com/bands','musician projects','Oteil Burbridge'),
 ('abb-dickey','Allman Brothers / Dickey Betts biography','https://allmanbrothersband.com/biography/dickey-betts/','historical membership','Dickey Betts'),
 ('mmw-official','Medeski Martin & Wood / official','https://www.medeskimartinandwood.com/about','musician projects','Medeski Martin & Wood')]
ids={s['id'] for s in data['sources']}
for id,name,url,kind,entity in new_sources:
 if id not in ids: data['sources'].append({'id':id,'name':name,'url':url,'kind':kind,'entity':entity,'access':'Source link and citation; no bulk-reuse permission inferred'})
# Announced upcoming shows live in data/upcoming_shows.json (validated by upcoming_shows.py).
# Not ticket inventory: each entry is checked against the artist's or venue's own announcement.
import upcoming_shows, family_tree_data
# Shows may name anyone in the catalog or in data/family_tree.json (merged later, in build_v03).
show_ids=dict(nameid)
for _ft in family_tree_data.load().get('entries',[]):
 show_ids.setdefault(_ft['name'],_ft.get('id') or family_tree_data.slug(_ft['name']))
events=[]
for s in upcoming_shows.load(known_names=set(show_ids)):
 e=dict(id=s['id'],date=s['date'],artist_id=show_ids[s['artist']],artist=s['artist'],
  performers=[show_ids[n] for n in (s.get('performers') or [s['artist']])],
  venue=s['venue'],city=s['city'],region=s['region'],source_url=s['source'],
  source_type='official artist / venue announcement' if s.get('official',True) else 'artist-maintained listing + secondary corroboration',
  verified_as_of=s['checked_on'],status='announced',
  ticket_url=(s.get('tickets') or {}).get('official_url'))
 for k in ('date_end','corroboration','note','collaboration_confirmed'):
  if s.get(k): e[k]=s[k]
 events.append(e)
assert len({e['id'] for e in events})==len(events)
assert len([s for s in data['source_entries'] if s['list']=='founding'])==110
assert len([s for s in data['source_entries'] if s['list']=='precursor'])==11
data['about'].update(version='0.2 / source-connected preview',as_of='2026-10-26',
 disclaimer='Concert listings are a SOURCE-CHECKED SNAPSHOT as of October 26, 2026, not live updates, ticket availability, or notifications. The recording index is empty until optional authorized metadata ingestion.')
data['events']=sorted(events,key=lambda x:(x['date'],x['artist']))
rec_file=ROOT/'recordings.json'
if rec_file.exists(): data['recordings']=json.loads(rec_file.read_text())
else: data['recordings']=[];rec_file.write_text('[]\n')
CAT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
# Reconcile SQLite to enriched catalog, with source traces for each event.
conn=sqlite3.connect(ROOT/'jam_archive.sqlite');conn.execute('PRAGMA foreign_keys=ON')
for e in data['entities']:
 conn.execute('INSERT OR IGNORE INTO entity(id,name,type,origins_json,aliases_json) VALUES (?,?,?,?,?)',(e['id'],e['name'],e['type'],json.dumps(e['origins']),json.dumps(e['aliases'])))
for r in rels:
 conn.execute('INSERT OR REPLACE INTO artist_relationship(source_entity_id,target_entity_id,relation,evidence_url,notes,verification) VALUES(?,?,?,?,?,?)',(r['from'],r['to'],r['type'],r['source_url'],r['note'],r['verification']))
for s in data['sources']:
 target=nameid.get(s['entity']) if s.get('entity') else None
 conn.execute('INSERT OR IGNORE INTO external_source(id,name,url,source_type,access_notes,associated_entity_id) VALUES(?,?,?,?,?,?)',(s['id'],s['name'],s['url'],s['kind'],s['access'],target))
conn.execute('CREATE TABLE IF NOT EXISTS event_snapshot (event_id TEXT PRIMARY KEY REFERENCES event(id), verified_as_of TEXT, note TEXT, corroboration_url TEXT, collaboration_confirmed INTEGER DEFAULT 0, date_end TEXT)')
for e in events:
 conn.execute('INSERT OR REPLACE INTO event (id,event_date,venue,city,region,country,timezone,event_status,source_url,confirmed_at) VALUES (?,?,?,?,?,?,?,?,?,?)',(e['id'],e['date'],e['venue'],e['city'],e['region'],None,None,'announced',e['source_url'],e['verified_as_of']))
 for p in e['performers']:
  conn.execute('INSERT OR IGNORE INTO event_entity(event_id,entity_id,billing_role) VALUES(?,?,?)',(e['id'],p,'performer'))
 conn.execute('INSERT OR REPLACE INTO event_snapshot(event_id,verified_as_of,note,corroboration_url,collaboration_confirmed,date_end) VALUES(?,?,?,?,?,?)',(e['id'],e['verified_as_of'],e.get('note',''),e.get('corroboration'),int(e.get('collaboration_confirmed',False)),e.get('date_end')))
for r in data['recordings']:
 if r.get('source_platform')=='Internet Archive':
  conn.execute('INSERT OR REPLACE INTO recording(id,event_id,source_url,source_platform,recording_type,recording_lineage,permission_status,metadata_verified) VALUES(?,?,?,?,?,?,?,?)',(r['id'],None,r['source_url'],'Internet Archive',None,None,'link_only','source_metadata_only'))
conn.commit();conn.close()
# embed JSON for a standalone offline HTML. External source links still require internet.
template=(ROOT/'template.html').read_text()
encoded=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
(ROOT/'index.html').write_text(template.replace('/*__EMBEDDED_CATALOG__*/',encoded),encoding='utf-8')
print(json.dumps({'founding':110,'roots':11,'artists':len(entities),'relationships':len(rels),'source_linked':sum(bool(r['source_url']) for r in rels),'events':len(events),'recordings':len(data['recordings']),'sources':len(data['sources'])},indent=2))
