#!/usr/bin/env python3
"""The Jam Archive: bounded, source-first research assistant (stdlib only).

No generative model is required to ingest metadata. Nothing collected automatically
becomes a verified concert, collaboration, or tape; a reviewer must approve it.
"""
import argparse, datetime as dt, hashlib, json, os, re, sqlite3, sys, time, unicodedata
from pathlib import Path
from urllib.parse import urlencode, quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parent
STATE = ROOT / 'research.sqlite'
QUEUED = ROOT / 'research_queue.json'
CONFIG = ROOT / 'source_config.json'
DATE = re.compile(r'^\d{4}-\d{2}-\d{2}$')
IA_ID = re.compile(r'^[A-Za-z0-9_-]{1,120}$')

def iso_now(): return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
def canon(x):
    v = unicodedata.normalize('NFKD', str(x or '')).encode('ascii','ignore').decode().casefold()
    return re.sub(r'\s+',' ',re.sub(r'[^a-z0-9]+',' ',v)).strip().removeprefix('the ')

def a_date(x):
    if isinstance(x,list): x=x[0] if x else ''
    if not isinstance(x,str): return None
    match=re.fullmatch(r'(\d{4})[-./](\d{2})[-./](\d{2})(?:T.*)?',x.strip())
    if not match: return None
    val='-'.join(match.groups())
    try: dt.date.fromisoformat(val)
    except ValueError: return None
    return val

def connect(path=STATE):
    db=sqlite3.connect(path)
    db.row_factory=sqlite3.Row
    db.executescript('''PRAGMA journal_mode=WAL;
    CREATE TABLE IF NOT EXISTS candidate(
      id TEXT PRIMARY KEY, candidate_type TEXT NOT NULL CHECK(candidate_type IN ('recording','event')),
      provider TEXT NOT NULL, external_id TEXT NOT NULL, artist_id TEXT NOT NULL,
      artist TEXT NOT NULL, title TEXT NOT NULL, observed_date TEXT, venue TEXT,
      source_url TEXT NOT NULL, proposed_show_id TEXT, status TEXT NOT NULL
         CHECK(status IN ('pending','approved','rejected')) DEFAULT 'pending',
      reason TEXT NOT NULL, evidence_json TEXT NOT NULL, demo INTEGER NOT NULL DEFAULT 0,
      first_seen TEXT NOT NULL, last_seen TEXT NOT NULL, reviewed_at TEXT, review_note TEXT,
      UNIQUE(provider,external_id,artist_id,candidate_type));
    CREATE TABLE IF NOT EXISTS sync_run(id INTEGER PRIMARY KEY AUTOINCREMENT,
      started_at TEXT NOT NULL, finished_at TEXT, mode TEXT NOT NULL,
      sources_ok INTEGER DEFAULT 0, sources_failed INTEGER DEFAULT 0,
      observations INTEGER DEFAULT 0, message TEXT);
    CREATE INDEX IF NOT EXISTS candidate_review_idx ON candidate(status,candidate_type);
    ''')
    return db

def catalog():
    return json.loads((ROOT/'catalog.json').read_text())

def evidence_url(url):
    return isinstance(url,str) and url.startswith('https://') and len(url)<1500

def resolve_from_creator(creators, ent):
    if isinstance(creators,str):creators=[creators]
    if not isinstance(creators,list):return False
    known={canon(x) for x in [ent['name'],*ent.get('aliases',[])]}
    return any(isinstance(c,str) and canon(c) in known for c in creators)

def suggested_show(cat,artist_id,date):
    if not date:return None,'No exact source performance date; date needs research'
    possibilities=[s for s in cat.get('historical_shows',[]) if s['artist_id']==artist_id and s['date']==date]
    if len(possibilities)>1:return None, f'{len(possibilities)} performances on date; early/late slot cannot be inferred'
    if len(possibilities)==1:return possibilities[0]['id'], 'Same artist and date as curated show; source lineage and slot still need confirmation'
    return None,'Date absent from curated show index; review before creating historical show'

def ingest(db,cat,record):
    # All values are source observations, NOT editorial fact.
    ent=next((x for x in cat['entities'] if x['id']==record.get('artist_id')),None)
    if ent is None:raise ValueError('Unknown artist ID')
    typ=record.get('candidate_type')
    if typ not in ('recording','event'):raise ValueError('Unsupported observation')
    provider=str(record.get('provider',''))
    ext=str(record.get('external_id',''))
    if not provider or len(provider)>70 or not ext or len(ext)>180:raise ValueError('Invalid provider ID')
    if not evidence_url(record.get('source_url')):raise ValueError('Missing HTTPS source URL')
    dtval=a_date(record.get('observed_date'))
    if typ=='recording':
        suggested,reason=suggested_show(cat,ent['id'],dtval)
    else:
        suggested=None;reason='Event from ticketing source; match artist, billing and date against official announcement before approving'
    if not record.get('creator_match',True):
        suggested=None;reason='Artist/creator identity not an exact catalog or alias match; manual verification required'
    if record.get('reason_override'): reason=record['reason_override']
    cid=hashlib.sha256(f'{provider}\x1f{ext}\x1f{ent["id"]}\x1f{typ}'.encode()).hexdigest()[:18]
    now=iso_now()
    payload={k:record.get(k) for k in ('raw_creator','raw_date','artist_evidence','source_kind','artist_match','source_excerpt') if k in record}
    db.execute('''INSERT INTO candidate(id,candidate_type,provider,external_id,artist_id,artist,
        title,observed_date,venue,source_url,proposed_show_id,status,reason,evidence_json,demo,
        first_seen,last_seen)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,'pending',?,?,?,?,?)
        ON CONFLICT(id) DO UPDATE SET
        last_seen=excluded.last_seen, title=excluded.title, reason=excluded.reason,
        evidence_json=excluded.evidence_json
        ''',(cid,typ,provider,ext,ent['id'],ent['name'],str(record.get('title') or '')[:240],
        dtval,str(record.get('venue') or '')[:160],record['source_url'],suggested,reason,
        json.dumps(payload,ensure_ascii=False),int(bool(record.get('demo',False))),now,now))
    return cid

def get_json(url,contact):
    req=Request(url,headers={'User-Agent':f'JamArchiveResearchAgent/0.4 ({contact})','Accept':'application/json'})
    for attempt in range(3):
        try:
            with urlopen(req,timeout=28) as res:
                if int(res.headers.get('Content-Length','0'))>3_000_000:raise ValueError('Oversized result')
                return json.loads(res.read(3_000_000))
        except HTTPError as e:
            if e.code not in (429,500,502,503,504) or attempt==2:raise
            time.sleep(2*(attempt+1))
    raise RuntimeError('API repeatedly unavailable')

def fetch_archive(ent,contact,limit):
    query=f'collection:etree AND creator:"{ent["name"].replace(chr(34), "")}"'
    params=[('q',query),('rows',str(limit)),('output','json')]
    params += [('fl[]',v) for v in ('identifier','title','date','creator')]
    doc=get_json('https://archive.org/advancedsearch.php?'+urlencode(params),contact)
    for item in doc.get('response',{}).get('docs',[]):
        identifier=item.get('identifier')
        if not isinstance(identifier,str) or not IA_ID.fullmatch(identifier):continue
        match=resolve_from_creator(item.get('creator',[]),ent)
        yield {'candidate_type':'recording','provider':'internet-archive','external_id':identifier,
            'artist_id':ent['id'],'title':item.get('title') if isinstance(item.get('title'),str) else identifier,
            'observed_date':item.get('date'), 'raw_date':item.get('date'),
            'raw_creator':item.get('creator'),'creator_match':match,
            'source_kind':'public Live Music Archive descriptive metadata',
            'source_url':'https://archive.org/details/'+quote(identifier)}

def fetch_ticketmaster(ent,api_key,limit):
    # Key is NEVER included in the saved source URL or output files.
    params=urlencode({'apikey':api_key,'keyword':ent['name'],'size':min(limit,25),'sort':'date,asc'})
    doc=get_json('https://app.ticketmaster.com/discovery/v2/events.json?'+params,
                 'https://github.com/jamarchive/community-archive')
    for item in doc.get('_embedded',{}).get('events',[]):
        source=item.get('url')
        ext=item.get('id')
        if not ext or not evidence_url(source):continue
        acts=item.get('_embedded',{}).get('attractions',[])
        exact=any(canon(x.get('name'))==canon(ent['name']) for x in acts)
        if not exact:continue   # No fuzzy promotion of unrelated keyword hits.
        venues=item.get('_embedded',{}).get('venues',[])
        venue=venues[0].get('name') if venues else None
        yield {'candidate_type':'event','provider':'ticketmaster','external_id':str(ext),
               'artist_id':ent['id'],'title':item.get('name') or ent['name'],
               'observed_date':item.get('dates',{}).get('start',{}).get('localDate'),
               'venue':venue,'source_url':source,
               'artist_evidence':[x.get('name') for x in acts],
               'artist_match':'exact_ticketmaster_attraction',
               'source_kind':'ticketing API listing, not independently corroborated'}

def do_sync(args):
    cat=catalog(); chosen=set(args.artists)
    allowed={e['id']:e for e in cat['entities']}
    unknown=chosen-set(allowed)
    if unknown:raise ValueError('Unknown artist IDs: '+', '.join(sorted(unknown)))
    if not chosen:raise ValueError('Provide explicit --artists to avoid bulk catalog sweeps')
    if len(chosen)>12:raise ValueError('At most 12 selected artists per run')
    if not 1<=args.limit<=25:raise ValueError('Limit must be 1–25')
    if not args.contact or not ('@' in args.contact or args.contact.startswith('https://')):
        raise ValueError('Provide --contact with identifying email or project URL')
    db=connect();count=0;ok=0;failed=0
    started=iso_now();mode='live'
    with db:
        run=db.execute('INSERT INTO sync_run(started_at,mode) VALUES(?,?)',(started,mode)).lastrowid
    for i,uid in enumerate(sorted(chosen)):
        ent=allowed[uid]
        if i:time.sleep(1.2)
        adapters=[('archive',lambda:fetch_archive(ent,args.contact,args.limit))]
        if args.ticketmaster:
            key=os.environ.get('TICKETMASTER_API_KEY','')
            if not key:raise ValueError('Set TICKETMASTER_API_KEY in environment to enable ticketing adapter')
            adapters.append(('ticketmaster',lambda:fetch_ticketmaster(ent,key,args.limit)))
        for label,adapter in adapters:
            try:
                vals=list(adapter())
                with db:
                    for rec in vals:ingest(db,cat,rec);count+=1
                ok+=1;print(f'{ent["name"]}: {label}: {len(vals)} observations',file=sys.stderr)
            except (URLError,HTTPError,TimeoutError,ValueError,KeyError) as exc:
                failed+=1;print(f'{ent["name"]}: {label} FAILED: {type(exc).__name__}: {exc}',file=sys.stderr)
    with db:
        db.execute('UPDATE sync_run SET finished_at=?,sources_ok=?,sources_failed=?,observations=?,message=? WHERE id=?',
                   (iso_now(),ok,failed,count,'Source observations only; all new entries await review',run))
    export(db,cat)
    print(f'Updated research queue: {count} observations; {ok} source requests succeeded; {failed} failed.')
    if failed:sys.exit(2)

def export(db=None,cat=None):
    owned=db is None
    if owned:db=connect()
    if cat is None:cat=catalog()
    rows=[dict(r) for r in db.execute('SELECT * FROM candidate ORDER BY first_seen DESC,id')]
    for r in rows:
        r['evidence']=json.loads(r.pop('evidence_json'))
        r['demo']=bool(r['demo'])
        # No source payload is silently elevated to verified status.
    output={'version':1,'generated_at':iso_now(),'policy':'UNREVIEWED SOURCE OBSERVATIONS; demo rows are synthetic; no automatic publishing',
            'summary':{'pending':sum(r['status']=='pending' for r in rows),
                       'approved':sum(r['status']=='approved' for r in rows),
                       'rejected':sum(r['status']=='rejected' for r in rows),
                       'demo':sum(r['demo'] for r in rows)},
            'items':rows}
    QUEUED.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    if owned:db.close()
    return output

def do_demo(args):
    # Explicitly synthetic input verifies both the single-show and ambiguous-slot safeguards.
    db=connect();cat=catalog()
    fixture=json.loads((ROOT/'agent'/'fixtures'/'research_demo.json').read_text())
    with db:
        for row in fixture:
            row={**row,'demo':True}
            ingest(db,cat,row)
    export(db,cat)
    print(f'Loaded {len(fixture)} explicitly SYNTHETIC records for local testing. They cannot be approved.')

def do_review(args):
    db=connect();cat=catalog()
    if args.action=='list':
        print(json.dumps(export(db,cat)['summary'],indent=2))
        for r in db.execute('SELECT * FROM candidate WHERE status=? ORDER BY first_seen DESC LIMIT 50',('pending',)):
            print(f'{r["id"]} {r["candidate_type"]} {r["artist"]} {r["observed_date"] or "date unknown"} {r["reason"][:90]}')
        return
    if args.action=='decision':
        row=db.execute('SELECT * FROM candidate WHERE id=?',(args.id,)).fetchone()
        if row is None:raise ValueError('Candidate ID not found')
        if row['demo']:raise ValueError('Synthetic fixture rows cannot be approved or rejected as real research')
        if args.verdict=='approve':
            if not args.note or len(args.note)<12:raise ValueError('Approval requires specific reviewer evidence in --note')
            if row['candidate_type']=='recording':
                show=args.show_id
                found=next((s for s in cat.get('historical_shows',[]) if s['id']==show),None)
                if not found:raise ValueError('Approve a recording only with an existing curated --show-id')
                if found['artist_id']!=row['artist_id']:raise ValueError('Show artist mismatch')
                if row['observed_date'] and found['date']!=row['observed_date']:
                    raise ValueError('Date mismatch: verify original performance date before approving')
            else:show=None
        else:show=None
        with db:
            db.execute('UPDATE candidate SET status=?,proposed_show_id=COALESCE(?,proposed_show_id),review_note=?,reviewed_at=? WHERE id=?',
                       ('approved' if args.verdict=='approve' else 'rejected',show,args.note,iso_now(),args.id))
        export(db,cat)
        print('Review decision saved. Run python build_v04.py to update the offline dashboard.')

def main():
    p=argparse.ArgumentParser(description='Jam Archive source-first research agent')
    sub=p.add_subparsers(dest='command',required=True)
    s=sub.add_parser('sync',help='Fetch a bounded, explicitly selected live-source sample')
    s.add_argument('--artists',nargs='+',required=True,help='Exact catalog slugs')
    s.add_argument('--contact',required=True,help='User-Agent contact email or project URL')
    s.add_argument('--limit',type=int,default=10)
    s.add_argument('--ticketmaster',action='store_true',help='Requires TICKETMASTER_API_KEY')
    sub.add_parser('demo',help='Load clearly marked synthetic test observations')
    r=sub.add_parser('review',help='List or manually decide on candidates')
    r.add_argument('action',choices=['list','decision']);r.add_argument('--id');r.add_argument('--verdict',choices=['approve','reject']);r.add_argument('--show-id');r.add_argument('--note',default='')
    sub.add_parser('export',help='Regenerate static research_queue.json')
    args=p.parse_args()
    try:
        if args.command=='sync':do_sync(args)
        elif args.command=='demo':do_demo(args)
        elif args.command=='review':do_review(args)
        else:out=export();print(json.dumps(out['summary'],indent=2))
    except (ValueError,FileNotFoundError) as e:p.error(str(e))
if __name__=='__main__':main()
