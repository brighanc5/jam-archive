#!/usr/bin/env python3
"""Read-only production release verifier. Run manually after Cloudflare deployment.

Uses a handful of HTTP GETs; never changes a deployment or Cloudflare settings.
"""
from urllib.error import URLError, HTTPError
from urllib.request import Request,urlopen
import json,sys,os

ORIGIN=os.environ.get('JAM_ARCHIVE_ORIGIN','https://thejamarchive.org').rstrip('/')
HEADERS={'User-Agent':'JamArchive-ReleaseVerifier/0.13','Accept':'text/html,application/json'}

def fetch(path,allow404=False):
    request=Request(ORIGIN+path,headers=HEADERS)
    try:
        with urlopen(request,timeout=12) as r:
            return r.status,r.read().decode('utf-8'),dict(r.headers)
    except HTTPError as exc:
        if allow404 and exc.code==404:
            return 404,exc.read().decode('utf-8'),dict(exc.headers)
        raise

def main():
    try:
        status,raw,headers=fetch('/assets/build_report.json')
        report=json.loads(raw)
        print('Live release:',report.get('version','unknown'))
        if report.get('version')!='0.13':
            print('NOT CURRENT: v0.13 has not reached Cloudflare. Check GitHub push and production deploy.');return 1
        if (report.get('performance_sequences'),report.get('performance_track_positions'))!=(12,62):
            print('MISMATCH: performance evidence metadata not in published release');return 1
        _,raw,_=fetch('/assets/site_audit.json');audit=json.loads(raw)
        if audit.get('issues')!=0 or audit.get('html_pages_inspected')!=673:
            print('MISMATCH: offline site quality audit report not published');return 1
        checks={'/era-atlas/':['History is bigger','id="ea-search"'],
                '/era-atlas/shows/phish-1997-11-17/':['McNichols Arena','Live Phish 11'],
                '/era-atlas/chapters/goose-2024/':['Goose: selected 2024 dates'],
                '/performance-lab/':['Find the moments.','id="pl-search"'],
                '/performance-lab/gd-1977-05-08-scarlet/':['Scarlet Begonias','Fire on the Mountain'],
                '/performance-lab/lineages/':['Plangent Processes','Betty Cantor-Jackson'],
                '/deep-archive/':['The stories behind the shows.'],
                '/connections/':['SIX DEGREES OF JAM'],
                '/song-paths/':['Every song has'],
                '/recordings/':['Follow the tape.']}
        for path,needles in checks.items():
            _,html,headers=fetch(path)
            if not all(n in html for n in needles):
                print('MISMATCH:',path,'does not show expected content');return 1
        status,raw,headers=fetch('/not-an-indexed-show-v013/',allow404=True)
        if status!=404 or 'We haven\'t indexed this page.' not in raw:
            print('MISMATCH: missing page is not correctly returning the custom 404');return 1
        print('LIVE DEPLOYMENT PASS: v0.13 pages, source evidence, quality audit and 404 response are served.')
        print('Optional: use curl -I '+ORIGIN+'/performance-lab/ to inspect response security headers.')
        return 0
    except (OSError,URLError,HTTPError,json.JSONDecodeError,UnicodeDecodeError) as exc:
        print('COULD NOT VERIFY LIVE: '+str(exc))
        print('The local build may be fine. Check GitHub Actions and Cloudflare Deployments.');return 2
if __name__=='__main__':sys.exit(main())
