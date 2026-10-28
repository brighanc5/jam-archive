#!/usr/bin/env python3
"""Fail-closed preflight: free/static-only infrastructure, review-only research.

This is a repository safety tripwire, NOT an audit of your actual Cloudflare
billing/account configuration. Edit it only after deliberate review.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check(condition, message):
    if not condition:
        raise SystemExit('SAFETY CHECK FAILED: ' + message)


def text(path):
    return (ROOT / path).read_text(encoding='utf-8')


wrangler = json.loads('\n'.join(
    row for row in text('wrangler.jsonc').splitlines()
    if not row.lstrip().startswith('//')
))
check(wrangler.get('name') == 'odd-king-7e31', 'Worker name changed')
check(wrangler.get('workers_dev') is True, 'workers_dev unexpectedly disabled')
check(wrangler.get('assets', {}).get('directory') == './site', 'static asset directory changed')
# Fail closed: any new key must undergo review. This prevents quietly adding
# paid storage, AI, cron triggers, email bindings, or executable Worker logic.
allowed_worker_keys = {'name', 'compatibility_date', 'workers_dev', 'assets'}
check(set(wrangler) <= allowed_worker_keys,
      'Cloudflare config gained unreviewed settings: ' + str(sorted(set(wrangler) - allowed_worker_keys)))
check(not any(x in wrangler for x in ('main', 'triggers', 'd1_databases', 'kv_namespaces',
      'r2_buckets', 'ai', 'durable_objects', 'queues', 'send_email', 'browser', 'workflows')),
      'A Worker execution, schedule, or paid binding is configured')

research = text('.github/workflows/daily-research.yml')
check(re.search(r'(?m)^on:\s*\n\s+workflow_dispatch:\s*$', research) is not None,
      'Research workflow must be manual-only')
check(not re.search(r'(?m)^\s*(schedule|push|pull_request|repository_dispatch|workflow_run):', research),
      'Research was configured to run automatically')
check('contents: read' in research, 'Research needs read-only repository permission')
check('timeout-minutes: 15' in research, 'Research execution cap changed')
check('secrets.JAM_ARCHIVE_CONTACT' in research, 'Manual source identification check removed')
check('research_queue.json' in research, 'Review queue output is missing')

site = ROOT / 'site'
check(site.is_dir() and (site / 'index.html').exists(), 'Public static site has not been built')
check((site / '_headers').read_text(encoding='utf-8') == text('security_headers.txt'),
      'Published security headers differ from reviewed policy')
check('connect-src \'self\'' in text('security_headers.txt') and 'frame-ancestors \'none\'' in text('security_headers.txt'),
      'Critical CSP restrictions missing')

banned_media_extensions = {'.mp3', '.flac', '.wav', '.ogg', '.m4a', '.aac', '.aiff', '.mp4', '.mov', '.webm'}
for p in site.rglob('*'):
    if not p.is_file():
        continue
    check(p.suffix.lower() not in banned_media_extensions,
          f'Unreviewed copyrighted media in public build: {p.relative_to(site)}')
    check(p.suffix.lower() not in {'.py', '.pem', '.key', '.sqlite', '.db', '.env'},
          f'Private executable/key/database in public build: {p.relative_to(site)}')
    check(p.name not in {'research_queue.json', '.dev.vars', 'id_rsa'},
          f'Private state in public build: {p.relative_to(site)}')

# These files should never be committed to the repository or included in a public ZIP.
for pattern in ('.env', '.env.*', '.dev.vars*', '*.pem', 'id_rsa*', '*.p12', '*.pfx'):
    for p in ROOT.glob(pattern):
        check(not p.is_file(), f'Private credential-like file in repository root: {p.name}')

print('OVERNIGHT SAFETY PASS: static Worker only; no cron research, billable bindings,')
print('  outbound email integration, private build state, or hosted audio/video detected.')
print('NOTE: Cloudflare billing plan, account settings, identity security, and legal rights')
print('  require separate manual verification; this check cannot inspect them.')
