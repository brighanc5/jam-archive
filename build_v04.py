#!/usr/bin/env python3
"""Assemble v0.4 keeping the complete v0.3 founding catalog intact.

Approved external *recording links* can join known historical shows; pending
metadata, event claims, and demo fixtures remain in a distinct research desk.
"""
from pathlib import Path
import subprocess,sys,json,sqlite3
ROOT=Path(__file__).resolve().parent
subprocess.run([sys.executable,str(ROOT/'build_v03.py')],cwd=ROOT,check=True)
# build_v03 resets catalog from explicit seed, not from external source claims.
cat=json.loads((ROOT/'catalog.json').read_text())
q=ROOT/'research_queue.json'
research=json.loads(q.read_text()) if q.exists() else {'version':1,'generated_at':None,'items':[],
  'summary':{'pending':0,'approved':0,'rejected':0,'demo':0}}
cat['research']=research
approved=[]
show_ids={s['id'] for s in cat['historical_shows']}
for x in research['items']:
 if x['status']!='approved' or x['demo'] or x['candidate_type']!='recording':continue
 if x['proposed_show_id'] not in show_ids:continue
 rid='agent-'+x['id']
 if any(r['id']==rid for r in cat['recording_sources']):continue
 approved.append({'id':rid,'show_id':x['proposed_show_id'],
   'title':x['title'],'kind':'Externally indexed recording · reviewed link',
   'source_url':x['source_url'],'provider':x['provider'],
   'description':'Manually matched by archive reviewer. Review note: '+(x.get('review_note') or '')[:300],
   'access':'External link only; artist rules apply','source_verified':'editorially_approved_'+str(x.get('reviewed_at') or '')[:10]})
cat['recording_sources'].extend(approved)
cat['about'].update(version='0.4 / source-first research agent',
 disclaimer='Original v0.3 shows and tours are dated snapshots. New source observations remain unverified until manually reviewed. Demo queue entries are synthetic, never show/tour claims. No agent is running continuously in this local file.')
(ROOT/'catalog.json').write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n')
if approved:
 db=sqlite3.connect(ROOT/'jam_archive.sqlite');db.execute('PRAGMA foreign_keys=ON')
 for r in approved:
  db.execute('INSERT OR IGNORE INTO recording_source VALUES(?,?,?,?,?,?,?,?,?)',
      (r['id'],r['show_id'],r['title'],r['kind'],r['source_url'],r['provider'],r['description'],r['access'],r['source_verified']))
 db.commit();db.close()
# Base builder embeds only before the v0.4 research enrichment. Regenerate from template.
template=(ROOT/'template.html').read_text()
start='<script>\n/* Jam Archive v0.3'
if start not in template:raise RuntimeError('History module was not found')
before,tail=template.split(start,1)
_,after=tail.split('</script>',1)
template=before+'<script>\n'+(ROOT/'history_ui.js').read_text()+'\n</script>'+after
assert template.count('/*__EMBEDDED_CATALOG__*/')==1
encoded=json.dumps(cat,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
(ROOT/'index.html').write_text(template.replace('/*__EMBEDDED_CATALOG__*/',encoded))
print(json.dumps({'artists':len(cat['entities']), 'relationships':len(cat['relationships']),
 'historical_shows':len(cat['historical_shows']),'recording_links':len(cat['recording_sources']),
 'research_observations':len(research['items']),'demo_records':research['summary'].get('demo',0),
 'approved_new_links':len(approved)},indent=2))
