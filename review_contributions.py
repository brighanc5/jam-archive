#!/usr/bin/env python3
"""Offline research lead importer. Never edits or publishes the archive."""
import argparse,hashlib,json,re,sys
from pathlib import Path
from datetime import date
from urllib.parse import urlsplit
KINDS={'show_correction','recording_source','musician_relationship','tour_announcement','broken_link','other'}
FIELDS={'schema','kind','subject','date','source_url','details','credit','status','submitted_at','notice'}

def validate(row):
    if not isinstance(row,dict) or row.get('schema')!='jam-archive-contribution-v1':raise ValueError('Unknown submission schema')
    if row.get('kind') not in KINDS:raise ValueError('Invalid kind')
    if row.get('status')!='pending_review':raise ValueError('Only pending research leads are allowed')
    for name,lo,hi in [('subject',2,160),('details',20,5000),('credit',0,120)]:
        val=row.get(name,'')
        if not isinstance(val,str) or not lo<=len(val.strip())<=hi:raise ValueError('Invalid '+name)
    url=row.get('source_url','')
    if not isinstance(url,str) or len(url)>1000:raise ValueError('Invalid source URL')
    parsed=urlsplit(url)
    if parsed.scheme!='https' or not parsed.netloc or parsed.username or parsed.password:raise ValueError('Source must be a public HTTPS URL without embedded credentials')
    d=row.get('date','')
    if d:
        try:date.fromisoformat(d)
        except Exception as e:raise ValueError('Invalid date') from e
    return {k:row.get(k,'') for k in FIELDS if k!='notice'}

def import_directory(folder,out):
    out.mkdir(parents=True,exist_ok=True)
    added=0;existing=0;bad=[]
    for file in sorted(folder.glob('*.json')):
        try:
            if file.stat().st_size>16000:raise ValueError('File too large')
            row=validate(json.loads(file.read_text(encoding='utf-8')))
            # stable fingerprint ignores download time and optional credit to spot repeated leads
            key={k:row[k] for k in ['kind','subject','date','source_url','details']}
            digest=hashlib.sha256(json.dumps(key,sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:20]
            target=out/(digest+'.json')
            if target.exists():existing+=1;continue
            target.write_text(json.dumps({'review_id':digest,'review_status':'pending','contribution':row},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            added+=1
        except Exception as e:bad.append(f'{file.name}: {e}')
    return added,existing,bad

if __name__=='__main__':
    p=argparse.ArgumentParser(description='Import fan JSON leads to an offline moderation queue, without publishing')
    p.add_argument('folder',type=Path,help='Folder containing exported fan JSON files')
    p.add_argument('--out',type=Path,default=Path('review_inbox'),help='Private, offline moderation directory')
    a=p.parse_args()
    if not a.folder.is_dir():p.error('Folder not found')
    added,existing,bad=import_directory(a.folder,a.out)
    print(f'Queued: {added} · duplicates: {existing} · rejected: {len(bad)}')
    for err in bad:print('REJECTED '+err,file=sys.stderr)
    sys.exit(bool(bad))
