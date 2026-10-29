#!/usr/bin/env python3
"""Read-only check that Cloudflare actually serves the new release.

This script is deliberately NOT included in the offline build or GitHub CI.
Run it manually after a successful deployment. It makes only three GET requests.
"""
from pathlib import Path
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen
import json
import sys

ORIGIN = 'https://odd-king-7e31.brighamhancock.workers.dev'


def fetch(path, allow_404=False):
    request = Request(ORIGIN + path, headers={'User-Agent': 'TheJamArchive-ReleaseVerifier/0.11', 'Accept': 'text/html,application/json'})
    try:
        with urlopen(request, timeout=12) as response:
            return response.read().decode('utf-8')
    except HTTPError as exc:
        # A correct custom 404 intentionally has HTTP status 404.
        if allow_404 and exc.code == 404:
            return exc.read().decode('utf-8')
        raise


def main():
    print('Checking live website:', ORIGIN)
    try:
        report = json.loads(fetch('/assets/build_report.json'))
        print('Live release:', report.get('version', 'unknown'))
        if report.get('version') != '0.11':
            print('NOT DEPLOYED: GitHub and/or Cloudflare is serving an older version.')
            return 1
        if report.get('verified_relationships') != 52:
            print('MISMATCH: v0.10 relationship report is missing.')
            return 1
        if report.get('deep_archive_assertions') != 110 or report.get('deep_archive_dossiers') != 22:
            print('MISMATCH: Deep Archive counts are missing from production build.')
            return 1
        library = fetch('/deep-archive/')
        if 'The stories behind the shows.' not in library or 'id="da-query"' not in library:
            print('MISMATCH: Deep Archive index missing or incomplete.')
            return 1
        dossier = fetch('/deep-archive/shows/gd-1977-05-08/')
        if 'Betty Cantor-Jackson' not in dossier or 'Source bibliography' not in dossier:
            print('MISMATCH: Cornell research dossier missing or incomplete.')
            return 1
        family = fetch('/connections/')
        if 'id="cx-data"' not in family or 'SIX DEGREES OF JAM' not in family:
            print('MISMATCH: Family Tree page is missing or incomplete.')
            return 1
        missing = fetch('/connections/__not_an_indexed_show__/index.html', allow_404=True)
        if 'href="/assets/detail.css"' not in missing or 'href="/connections/"' not in missing:
            print('MISMATCH: old 404 page may still be deployed.')
            return 1
    except (OSError, URLError, HTTPError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        print('COULD NOT VERIFY LIVE: ' + str(exc))
        print('The local build can still be correct; check GitHub Actions and Cloudflare Deployments.')
        return 2
    print('LIVE DEPLOYMENT PASS: v0.11 Deep Archive, v0.10 Family Tree and 404 routing are publicly served.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
