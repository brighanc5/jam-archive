"""Strict, reproducible publication boundary for human-reviewed recording pointers.

The only contents of this file are validators; this module never fetches sources or
approves a claim. A reviewer must confirm source contents separately.
"""
import datetime as dt
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
APPROVED = ROOT / 'data' / 'approved_recordings.json'
ID = re.compile(r'^[a-z0-9][a-z0-9_-]{3,99}$')
SHA = re.compile(r'^agent-[0-9a-f]{18}$')


def valid_source_url(url):
    if not isinstance(url, str) or len(url) > 1500 or any(ord(c) < 32 for c in url):
        return False
    try:
        p = urlsplit(url)
        return p.scheme == 'https' and bool(p.hostname) and p.username is None and p.password is None and p.port in (None, 443) and not p.fragment
    except ValueError:
        return False


def validate_recordings(doc, shows, seeds):
    if not isinstance(doc, dict) or set(doc) != {'schema', 'recordings'} or doc['schema'] != 'jam-archive-approved-recordings-v1':
        raise ValueError('Approved recordings document has an unexpected schema')
    rows = doc['recordings']
    if not isinstance(rows, list) or len(rows) > 500:
        raise ValueError('Approved recording list invalid or above its 500-entry review limit')
    by_show = {s['id']: s for s in shows}
    seen_ids = set(seeds)
    seen_urls = {(s['show_id'], s['source_url']) for s in seeds.values()}
    out = []
    for pos, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            raise ValueError(f'Approved row {pos} must be an object')
        required = {'id', 'show_id', 'artist_id', 'title', 'kind', 'source_url', 'provider', 'description', 'access', 'reviewed_at', 'review_note'}
        if set(row) != required:
            raise ValueError(f'Approved row {pos} must have precisely {sorted(required)}')
        sid = row['show_id']
        if sid not in by_show or row['artist_id'] != by_show[sid]['artist_id']:
            raise ValueError(f'Approved row {pos} does not match a curated show and artist')
        rid = row['id']
        if not isinstance(rid, str) or not (ID.fullmatch(rid) or SHA.fullmatch(rid)) or rid in seen_ids:
            raise ValueError(f'Approved row {pos} has invalid or duplicate ID')
        if not valid_source_url(row['source_url']):
            raise ValueError(f'Approved row {pos} has invalid source URL')
        if (sid, row['source_url']) in seen_urls:
            raise ValueError(f'Approved row {pos} duplicates a source for the same show')
        for key, length in [('title', 240), ('kind', 80), ('provider', 80), ('description', 500), ('access', 200), ('review_note', 500)]:
            v = row[key]
            if not isinstance(v, str) or not v.strip() or len(v) > length:
                raise ValueError(f'Approved row {pos} invalid {key}')
        if len(row['review_note'].strip()) < 24:
            raise ValueError(f'Approved row {pos} review note must describe specific evidence')
        try:
            approved_date = dt.date.fromisoformat(row['reviewed_at'])
        except (ValueError, TypeError):
            raise ValueError(f'Approved row {pos} has invalid review date') from None
        if approved_date > dt.datetime.now(dt.timezone.utc).date():
            raise ValueError(f'Approved row {pos} review date is in the future')
        if any('<' in row[k] or '>' in row[k] for k in ('title', 'provider', 'description', 'review_note')):
            raise ValueError(f'Approved row {pos} cannot contain HTML markup')
        seen_ids.add(rid)
        seen_urls.add((sid, row['source_url']))
        out.append({k: row[k] for k in required if k not in ('artist_id', 'reviewed_at', 'review_note')} | {
            'source_verified': 'editorially_reviewed_' + row['reviewed_at'],
            'description': row['description'] + ' Editorial evidence: ' + row['review_note']
        })
    return out


def load(shows, original_recordings):
    doc = json.loads(APPROVED.read_text(encoding='utf-8'))
    return validate_recordings(doc, shows, {s['id']: s for s in original_recordings})
