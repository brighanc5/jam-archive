#!/usr/bin/env python3
"""v0.3 structural, source and generated browser bundle checks."""
import json,re,sqlite3,subprocess,tempfile
from pathlib import Path
root=Path(__file__).resolve().parent
j=json.loads((root/'catalog.json').read_text())
ids={e['id'] for e in j['entities']}
assert len(j['entities'])==196 and len(ids)==196
assert sum(x['list']=='founding' for x in j['source_entries'])==110
assert sum(x['list']=='precursor' for x in j['source_entries'])==11
assert sum('expansion_candidate' in e['origins'] for e in j['entities'])==24
assert len(j['relationships'])==77
assert len(j['events'])==45
assert len(j['historical_shows'])==9
assert len(j['recording_sources'])==9
assert len(j['sources'])==26
assert 'research' in j
assert j['research']['summary']['demo'] == sum(x['demo'] for x in j['research']['items'])
assert len({s['id'] for s in j['historical_shows']})==9
assert len({s['id'] for s in j['recording_sources']})==9
assert len([s for s in j['historical_shows'] if s['artist']=='The Allman Brothers Band'])==6
assert len([s for s in j['historical_shows'] if s['date']=='1971-03-12'])==2
assert len([s for s in j['historical_shows'] if s['date']=='1971-03-13'])==2
assert len([s for s in j['recording_sources'] if s['show_id']=='gd-1977-05-08'])==3
historical_ids={h['id'] for h in j['historical_shows']}
for h in j['historical_shows']:
 assert h['artist_id'] in ids and re.fullmatch(r'\d{4}-\d{2}-\d{2}',h['date'])
 assert h['source_url'].startswith('https://') and h['songs'] and h['setlist_scope'].startswith('Selected songs')
for r in j['recording_sources']:
 assert r['show_id'] in historical_ids and r['source_url'].startswith('https://')
con=sqlite3.connect(root/'jam_archive.sqlite')
assert con.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
assert con.execute('PRAGMA foreign_key_check').fetchall()==[]
for table,expected in [('entity',196),('source_seed',121),('artist_relationship',77),('event',45),('historical_show',9),('recording_source',9)]:
 actual=con.execute('SELECT count(*) FROM '+table).fetchone()[0]
 assert actual==expected,(table,actual,expected)
assert con.execute('select count(*) from historical_show_song').fetchone()[0]>=40
con.close()
html=(root/'site/index.html').read_text()
assert len(html)>80000
assert '/*__EMBEDDED_CATALOG__*/' not in html
for name in ['discover','universe','shows','network','history','recordings','following','sources','research']:
 assert f'id="view-{name}"' in html
assert 'id="history-dialog"' in html
scripts=re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>',html,flags=re.DOTALL|re.IGNORECASE)
assert len(scripts)==5
for i,script in enumerate(scripts):
 with tempfile.NamedTemporaryFile(mode='w',suffix='.js') as tmp:
  tmp.write(script);tmp.flush()
  proc=subprocess.run(['node','--check',tmp.name],capture_output=True,text=True)
  assert proc.returncode==0,(i,proc.stderr)
assert (root/'site/assets/discovery.js').exists()
assert not json.loads((root/'site/assets/catalog.json').read_text())['research']['items']
assert len(list((root/'site/artists').glob('*/index.html')))==196
assert len(list((root/'site/shows').glob('*/index.html')))==9
assert len(list((root/'site/songs').glob('*/index.html')))==32
print(f'PASS: {len(ids)} artists, 110+11 original rows, 77 relationships, 45 static events, 9 historic shows, 196 artist pages, 32 song pages, 4 inline scripts, valid SQLite')
