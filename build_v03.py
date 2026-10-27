#!/usr/bin/env python3
"""Build Jam Archive v0.3: preserve v0.2 + source-linked historical performances and tapes."""
import json,sqlite3,sys,subprocess,re,unicodedata
from pathlib import Path
from history_seed import H,R
ROOT=Path(__file__).resolve().parent
subprocess.run([sys.executable,str(ROOT/'build_archive.py')],cwd=ROOT,check=True)
p=ROOT/'catalog.json'; db=json.loads(p.read_text()); ids={e['name']:e['id'] for e in db['entities']}
# Artist-expansion candidates. Not identified as an exhaustive roster and no tour/relationship claims are inferred.
expansion=[
 ('King Gizzard & the Lizard Wizard','band'),('Eggy','band'),('Dogs in a Pile','band'),
 ("Daniel Donato's Cosmic Country",'band'),('Circles Around the Sun','band'),
 ('Dark Star Orchestra','band'),('Greensky Bluegrass','band'),('Kitchen Dwellers','band'),
 ('Papadosio','band'),('TAUK','band'),('The Wood Brothers','band'),('Molly Tuttle','person'),
 ('Neighbor','band'),("Taper's Choice",'band'),('The Slip','band'),('The Nth Power','band'),
 ('The New Mastersounds','band'),('Sam Grisman Project','band'),('Billy & the Kids','band'),
 ('Snarky Puppy','band'),('Lettuce','band'),('Vulfpeck','band'),('The Meters','band'),
 ("Ivan Neville's Dumpstaphunk",'band')]
def slug(n):
 return re.sub(r'-+','-',re.sub(r'[^a-z0-9]+','-',unicodedata.normalize('NFKD',n).encode('ascii','ignore').decode().lower())).strip('-')
for name,typ in expansion:
 if name in ids: continue
 uid=slug(name)
 if any(x['id']==uid for x in db['entities']): raise ValueError('Slug collision: '+name)
 db['entities'].append({'id':uid,'name':name,'type':typ,'origins':['expansion_candidate'],'aliases':[]})
 ids[name]=uid

assert all(h['artist'] in ids for h in H)
assert len({h['id'] for h in H})==len(H)
assert len({r['id'] for r in R})==len(R)
assert all(r['show_id'] in {h['id'] for h in H} for r in R)
for h in H:h['artist_id']=ids[h['artist']]
db['historical_shows']=sorted(H,key=lambda x:(x['date'],x['slot']))
db['recording_sources']=R
db['about'].update(version='0.3 / show laboratory', disclaimer='This is a dated, limited research snapshot, not comprehensive show or audio coverage. Individual recordings are externally linked, not hosted. Present-day tour listings are not updated automatically.')
for entry in [
 ('abb-1971-official-release','ABB · 1971 Fillmore East box set','https://allmanbrothersband.com/discography/the-1971-fillmore-east-recordings/','official archive release','The Allman Brothers Band'),
 ('gdao','Grateful Dead Archive Online','https://www.gdao.org/','recording provenance','Grateful Dead'),
 ('phish-official-1995','LivePhish · NYE 1995','https://www.livephish.com/LP-387.html','official release','Phish'),
 ('kglw-api','KGLW.net fan documentation and API','https://kglw.net/api/docs.php','setlist and guest appearance research',None)
]:
 sid,name,url,kind,entity=entry
 if not any(s['id']==sid for s in db['sources']):db['sources'].append({'id':sid,'name':name,'url':url,'kind':kind,'entity':entity,'access':'External source link only; separate permission required for data replication'})
p.write_text(json.dumps(db,ensure_ascii=False,indent=2)+'\n')
con=sqlite3.connect(ROOT/'jam_archive.sqlite')
con.execute('PRAGMA foreign_keys=ON')
for name,typ in expansion:
 ent=next((e for e in db['entities'] if e['name']==name),None)
 con.execute('INSERT OR IGNORE INTO entity(id,name,type,origins_json,aliases_json) VALUES(?,?,?,?,?)',(ent['id'],ent['name'],ent['type'],json.dumps(ent['origins']),json.dumps(ent['aliases'])))
con.executescript('''
CREATE TABLE IF NOT EXISTS historical_show(
 id TEXT PRIMARY KEY,artist_id TEXT NOT NULL REFERENCES entity(id),show_date TEXT NOT NULL,
 slot TEXT,venue TEXT,city TEXT,region TEXT,highlight TEXT,source_url TEXT NOT NULL,
 verified_as_of TEXT NOT NULL,scope TEXT NOT NULL,notes TEXT);
CREATE TABLE IF NOT EXISTS historical_show_song(
 show_id TEXT NOT NULL REFERENCES historical_show(id),position INTEGER NOT NULL,song_title TEXT NOT NULL,
 PRIMARY KEY(show_id,position));
CREATE TABLE IF NOT EXISTS recording_source(
 id TEXT PRIMARY KEY,show_id TEXT NOT NULL REFERENCES historical_show(id),title TEXT NOT NULL,
 kind TEXT NOT NULL,source_url TEXT NOT NULL,provider TEXT NOT NULL,description TEXT,
 access_note TEXT,source_verified TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS idx_historical_show_date ON historical_show(show_date);
CREATE INDEX IF NOT EXISTS idx_historical_show_artist ON historical_show(artist_id);
CREATE INDEX IF NOT EXISTS idx_recording_source_show ON recording_source(show_id);
''')
for h in H:
 con.execute('INSERT OR REPLACE INTO historical_show VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',(h['id'],h['artist_id'],h['date'],h['slot'],h['venue'],h['city'],h['region'],h['highlight'],h['source_url'],h['data_checked'],h['setlist_scope'],h['notes']))
 for ix,s in enumerate(h['songs']):con.execute('INSERT OR REPLACE INTO historical_show_song VALUES(?,?,?)',(h['id'],ix,s))
for r in R:con.execute('INSERT OR REPLACE INTO recording_source VALUES(?,?,?,?,?,?,?,?,?)',(r['id'],r['show_id'],r['title'],r['kind'],r['source_url'],r['provider'],r['description'],r['access'],r['source_verified']))
for s in db['sources']:
 con.execute('INSERT OR IGNORE INTO external_source(id,name,url,source_type,access_notes,associated_entity_id) VALUES(?,?,?,?,?,?)',(s['id'],s['name'],s['url'],s['kind'],s['access'],ids.get(s['entity'])))
assert con.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
con.commit();con.close()
template=(ROOT/'template.html').read_text()
# Keep the canonical feature script editable outside the minified/embedded page template.
start='<script>\n/* Jam Archive v0.3'
if start in template:
 before,old=template.split(start,1)
 _,after=old.split('</script>',1)
 template=before+'<script>\n'+(ROOT/'history_ui.js').read_text()+'\n</script>'+after
else:raise AssertionError('Historical UI script marker missing from template')
encoded=json.dumps(db,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
assert template.count('/*__EMBEDDED_CATALOG__*/')==1
(ROOT/'index.html').write_text(template.replace('/*__EMBEDDED_CATALOG__*/',encoded))
print(json.dumps({'entities':len(db['entities']),'relationships':len(db['relationships']),'upcoming_snapshot_events':len(db['events']),'historical_shows':len(H),'expansion_candidates':len(expansion),'recording_source_links':len(R),'sources':len(db['sources'])},indent=2))
