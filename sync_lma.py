#!/usr/bin/env python3
"""OPTIONAL Internet Archive / Live Music Archive metadata-only indexer.

Does not fetch audio, setlists, or scrape artist sites. Does not assert that
source metadata is a fully verified show date, or that a recording is CC0.
Requires explicit artist selection and user-provided contact identifier.
"""
import argparse,json,re,time,sys,unicodedata
from pathlib import Path
from urllib.parse import urlencode,quote
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
ROOT=Path(__file__).resolve().parent

def norm(s):
 if not isinstance(s,str): return ''
 s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()
 s=re.sub(r'[^a-z0-9]+',' ',s).strip()
 return re.sub(r'^the ', '',s)

def get_json(url,contact):
 # Contact is specified by the user at runtime, never saved to the project.
 req=Request(url,headers={'User-Agent':f'JamArchiveFanResearch/0.2 (contact: {contact})','Accept':'application/json'})
 for attempt in range(3):
  try:
   with urlopen(req,timeout=25) as f:
    if int(f.headers.get('content-length','0'))>2_000_000:raise ValueError('Oversized API response')
    return json.loads(f.read(2_000_000))
  except HTTPError as e:
   if e.code not in (429,502,503,504) or attempt==2:raise
   time.sleep(3*(attempt+1))
 raise RuntimeError('Retry exhausted')

def main():
 p=argparse.ArgumentParser(description='Index only limited, attributed Internet Archive etree item metadata.')
 p.add_argument('--artists',nargs='+',required=True,help='Canonical artist names: e.g. "Goose" "Grateful Dead"')
 p.add_argument('--contact',required=True,help='Your email or project URL for ethical API identification (NOT stored)')
 p.add_argument('--limit',type=int,default=15,help='Max metadata rows requested per artist (1–50); default 15')
 args=p.parse_args()
 if not 1<=args.limit<=50:p.error('--limit must be between 1 and 50')
 if not any(ch in args.contact for ch in ('@','://')):p.error('--contact must be an email or URL')
 catalog=json.loads((ROOT/'catalog.json').read_text());ent={e['name']:e for e in catalog['entities']}
 aliases={e['name']:[e['name']]+e['aliases'] for e in ent.values()}
 unknown=[a for a in args.artists if a not in ent]
 if unknown:p.error('Artist names not in catalog: '+', '.join(unknown))
 existing=json.loads((ROOT/'recordings.json').read_text()) if (ROOT/'recordings.json').exists() else []
 accepted={r['id']:r for r in existing};review=[]
 for i,artist in enumerate(args.artists):
  if i:time.sleep(1.2)
  query='collection:etree AND creator:"'+artist.replace('"','')+'"'
  args_query=[('q',query),('rows',str(args.limit)),('output','json')]
  args_query += [('fl[]',f) for f in ('identifier','title','date','creator')]
  url='https://archive.org/advancedsearch.php?'+urlencode(args_query)
  print(f'Looking up public item metadata: {artist}',file=sys.stderr)
  try: doc=get_json(url,args.contact)
  except (HTTPError,URLError,ValueError,TimeoutError) as e:
   print(f'Archive API failed for {artist}: {e}',file=sys.stderr);continue
  rows=doc.get('response',{}).get('docs',[])
  for row in rows:
   identifier=row.get('identifier')
   if not isinstance(identifier,str) or not re.fullmatch(r'[a-zA-Z0-9_-]{1,120}',identifier):
    review.append({'artist':artist,'reason':'invalid identifier','metadata':row});continue
   creators=row.get('creator') or []
   if isinstance(creators,str):creators=[creators]
   matched=any(norm(c) in [norm(n) for n in aliases[artist]] for c in creators if isinstance(c,str))
   if not matched:
    review.append({'artist':artist,'reason':'creator does not exactly match canonical artist/aliases','metadata':row});continue
   title=row.get('title') if isinstance(row.get('title'),str) else identifier
   rawdate=row.get('date')
   if isinstance(rawdate,list):rawdate=rawdate[0] if rawdate else None
   record={
    'id':'ia-'+identifier,'artist_id':ent[artist]['id'],'artist':artist,
    'title':title[:300], 'date':str(rawdate)[:30] if rawdate else None,
    'date_status':'source_metadata_unverified_as_performance_date',
    'source_url':'https://archive.org/details/'+quote(identifier),
    'source_platform':'Internet Archive',
    'item_identifier':identifier,'permission_status':'link_only_review_artist_policy',
    'verification':'creator_exactly_matches_registered_artist',
    'metadata_source':'Internet Archive Advanced Search API'
   }
   accepted[record['id']]=record
  print(f'  Examined {len(rows)} items; {sum(x["artist"]==artist for x in accepted.values())} matched in local index',file=sys.stderr)
 (ROOT/'recordings.json').write_text(json.dumps(sorted(accepted.values(),key=lambda r:(r['artist'],r['title'])),ensure_ascii=False,indent=2)+'\n')
 (ROOT/'candidate_review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
 print(f'{len(accepted)} metadata links stored; {len(review)} ambiguous rows flagged. Now run: python3 build_archive.py')

if __name__=='__main__': main()
