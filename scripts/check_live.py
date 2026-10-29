#!/usr/bin/env python3
"""Read-only v0.14 production verifier. Never deploys or changes account settings."""
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen
import json, sys, os
ORIGIN=os.environ.get('JAM_ARCHIVE_ORIGIN','https://thejamarchive.org').rstrip('/')
HEADERS={'User-Agent':'JamArchive-ReleaseVerifier/0.14','Accept':'text/html,application/json,text/css,application/javascript'}

def fetch(path,allow404=False):
 req=Request(ORIGIN+path,headers=HEADERS)
 try:
  with urlopen(req,timeout=15) as res:return res.status,res.read().decode('utf-8'),dict(res.headers)
 except HTTPError as exc:
  if allow404 and exc.code==404:return 404,exc.read().decode('utf-8'),dict(exc.headers)
  raise

def main():
 try:
  _,raw,_=fetch('/assets/build_report.json');r=json.loads(raw)
  print('Public domain:',ORIGIN,'· live release:',r.get('version'))
  if r.get('version')!='0.14':
   print('NOT CURRENT: v0.14 has not reached this domain. Check GitHub push and Cloudflare Deployments.');return 1
  wanted={'show_depth_studies':17,'show_depth_track_positions':238,'show_depth_repertoire_titles':158,'era_atlas_records':361}
  for key,num in wanted.items():
   if r.get(key)!=num:print('MISMATCH:',key,r.get(key),'expected',num);return 1
  _,raw,_=fetch('/assets/site_audit.json');audit=json.loads(raw)
  if audit.get('issues')!=0 or audit.get('html_pages_inspected')!=850:
   print('MISMATCH: public site audit version or issues');return 1
  checks={'/':['Follow the music.','/assets/jam-look.css','/assets/jam-experience.js'],
   '/era-atlas/':['id="ea-search"','data-artist='],
   '/show-depth/':['id="sd-search"','What actually went down'],
   '/show-depth/gd-1977-05-08/':['Scarlet Begonias','Fire on the Mountain'],
   '/repertoire/':['id="sd-search"','Know the tune?'],
   '/repertoire/songs/mountain-jam/':['Mountain Jam','/show-depth/'],
   '/connections/':['SIX DEGREES OF JAM'],
   '/deep-archive/':['The stories behind the shows.'],
   '/recordings/':['Follow the tape.'],
   '/song-paths/':['Every tune has a story.']}
  for path,needles in checks.items():
   _,html,_=fetch(path)
   for text in needles:
    if text not in html:print('MISMATCH:',path,'missing',repr(text));return 1
  for asset,marker in [('/assets/jam-look.css','repeating-conic-gradient'),('/assets/jam-experience.js','ja-mobile-bar'),('/assets/era-atlas.js','ja-load-more'),('/assets/show-depth.js','ja-load-more')]:
   _,body,_=fetch(asset)
   if marker not in body:print('MISMATCH: style or pager asset',asset);return 1
  status,html,_=fetch('/not-a-real-show-v014/',allow404=True)
  if status!=404:print('MISMATCH: custom 404 should return HTTP 404');return 1
  print('LIVE DEPLOYMENT PASS: v0.14 content, 850-page audit, new mobile identity, pager assets and routing are published.')
  print('Note: human phone and desktop checks are still necessary for visual usability.')
  return 0
 except (OSError,URLError,HTTPError,json.JSONDecodeError,UnicodeDecodeError) as exc:
  print('COULD NOT VERIFY LIVE:',exc);print('Inspect GitHub Actions and Cloudflare production deployment.');return 2
if __name__=='__main__':sys.exit(main())
