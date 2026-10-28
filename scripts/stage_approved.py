#!/usr/bin/env python3
"""Stage a previously reviewed real Internet Archive candidate in Git-tracked data.

Usage: python3 scripts/stage_approved.py --id <candidate-id>
Requires a local research.sqlite with an approved, manually matched candidate.
Does NOT conduct verification, auto-approve, commit, or publish anything.
"""
import argparse
import json
import sys
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from approved_recordings import APPROVED, load, valid_source_url  # noqa: E402
import research_agent as agent  # noqa: E402


def stage(candidate_id, db=None):
    own = db is None
    if own:
        if not agent.STATE.exists():
            raise ValueError('No local research database. Run the manual collector and review a candidate first.')
        db = agent.connect()
    try:
        row = db.execute('SELECT * FROM candidate WHERE id=?', (candidate_id,)).fetchone()
        if row is None or row['status'] != 'approved' or row['candidate_type'] != 'recording' or row['demo']:
            raise ValueError('Candidate must be a real, approved recording (never a demo or pending lead)')
        show_id = row['proposed_show_id']
        cat = agent.catalog()
        show = next((s for s in cat['historical_shows'] if s['id'] == show_id and s['artist_id'] == row['artist_id']), None)
        if show is None or not row['observed_date'] or row['observed_date'] != show['date']:
            raise ValueError('Candidate date, artist and curated show must match exactly')
        evidence = json.loads(row['evidence_json'])
        if evidence.get('creator_match') is not True:
            raise ValueError('Creator match is not explicit; manually verify source and update the research evidence first')
        if row['provider'] != 'internet-archive' or not valid_source_url(row['source_url']):
            raise ValueError('This stage tool currently supports only Internet Archive HTTPS source pages')
        p = urlsplit(row['source_url'])
        if p.netloc.lower() != 'archive.org' or p.path != '/details/' + row['external_id']:
            raise ValueError('Archive page must be the exact original candidate identifier')
        if not row['reviewed_at'] or not row['review_note'] or len(row['review_note'].strip()) < 24:
            raise ValueError('Review must include specific evidence (24+ characters) and review date')
        doc = json.loads(APPROVED.read_text(encoding='utf-8'))
        rid = 'agent-' + row['id']
        if any(x['id'] == rid for x in doc['recordings']):
            raise ValueError('Candidate is already staged')
        title = row['title'] or row['external_id']
        staged = {
            'id': rid, 'show_id': show_id, 'artist_id': row['artist_id'],
            'title': title, 'kind': 'Archive recording reference', 'source_url': row['source_url'],
            'provider': 'Internet Archive — Live Music Archive',
            'description': 'Source metadata identified by research agent; linked to one curated performance after manual source inspection.',
            'access': 'External source page; availability and permissions determined by custodian.',
            'reviewed_at': row['reviewed_at'][:10], 'review_note': row['review_note'].strip()
        }
        doc['recordings'].append(staged)
        # Full integrity check before a tracked file may be written.
        load_original = [s for s in cat['recording_sources'] if not s['id'].startswith('agent-')]
        from approved_recordings import validate_recordings
        validate_recordings(doc, cat['historical_shows'], {s['id']: s for s in load_original})
        APPROVED.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        return staged
    finally:
        if own:
            db.close()


def main():
    ap = argparse.ArgumentParser(description='Stage a manually approved archive link for reproducible publication')
    ap.add_argument('--id', required=True, help='Exact ID from research agent review list')
    args = ap.parse_args()
    try:
        r = stage(args.id)
        print('STAGED FOR GIT REVIEW:', r['id'], '|', r['show_id'])
        print('No public change is made until you commit and deploy this reviewed source data.')
    except (ValueError, FileNotFoundError) as e:
        ap.error(str(e))

if __name__ == '__main__':
    main()
