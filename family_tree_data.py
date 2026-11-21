"""Load data/family_tree.json and merge it into the catalog.

This is the one place to add musicians, bands and sourced relationships.
Edit data/family_tree.json, then run `bash scripts/build_public.sh`.

Rules enforced here (the build fails with a readable message otherwise):
  * every link names two known entries (by display name or id)
  * every link has an https source
  * a link in this file replaces any older placeholder for the same
    (from, to, type), so a sourced entry upgrades a `needs_review` one
"""
from pathlib import Path
from urllib.parse import urlsplit
import json, re, unicodedata

ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / 'data' / 'family_tree.json'
TYPES = {'person', 'band', 'project'}
LINK_TYPES = {'member_of', 'collaboration_with'}


def slug(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', text.lower())).strip('-')


class FamilyTreeError(ValueError):
    pass


def load(path=DATA_FILE):
    if not path.exists():
        return {'entries': [], 'links': []}
    return json.loads(path.read_text(encoding='utf-8'))


def merge(catalog, data=None):
    """Mutate catalog['entities'] and catalog['relationships'] in place.

    Returns (entries_added, links_added, links_upgraded).
    """
    data = load() if data is None else data
    entities = catalog['entities']
    by_id = {e['id']: e for e in entities}
    by_name = {}
    for e in entities:
        for label in [e['name'], *e.get('aliases', [])]:
            by_name[label.casefold()] = e['id']
    problems = []

    added = 0
    for n, entry in enumerate(data.get('entries', []), 1):
        name, typ = entry.get('name', '').strip(), entry.get('type')
        if not name or typ not in TYPES:
            problems.append(f'entries #{n}: needs a name and a type of {sorted(TYPES)}')
            continue
        eid = entry.get('id') or slug(name)
        if eid in by_id:
            if by_id[eid]['name'] != name:
                problems.append(f'entries #{n}: id {eid!r} already belongs to {by_id[eid]["name"]!r}')
            continue
        record = {'id': eid, 'name': name, 'type': typ, 'origins': ['family_tree'],
                  'aliases': list(entry.get('aliases', []))}
        entities.append(record)
        by_id[eid] = record
        for label in [name, *record['aliases']]:
            by_name[label.casefold()] = eid
        added += 1

    def resolve(ref, where):
        ref = (ref or '').strip()
        if ref in by_id:
            return ref
        if ref.casefold() in by_name:
            return by_name[ref.casefold()]
        problems.append(f'{where}: unknown entry {ref!r} (add it under "entries" first)')
        return None

    rels = catalog['relationships']
    index = {(r['from'], r['to'], r['type']): i for i, r in enumerate(rels)}
    new_links = upgraded = 0
    seen = set()
    for n, link in enumerate(data.get('links', []), 1):
        where = f'links #{n} ({link.get("from")} -> {link.get("to")})'
        a, b = resolve(link.get('from'), where), resolve(link.get('to'), where)
        kind = link.get('type', 'member_of')
        source = link.get('source', '')
        parts = urlsplit(source)
        if kind not in LINK_TYPES:
            problems.append(f'{where}: type must be one of {sorted(LINK_TYPES)}')
        if parts.scheme != 'https' or not parts.netloc:
            problems.append(f'{where}: needs an https source URL')
        if not a or not b or a == b:
            continue
        key = (a, b, kind)
        if key in seen:
            problems.append(f'{where}: listed twice')
            continue
        seen.add(key)
        record = {'from': a, 'to': b, 'type': kind, 'source_url': source,
                  'note': link.get('note', ''), 'verification': 'verified'}
        if key in index:
            if rels[index[key]] != record:
                rels[index[key]] = record
                upgraded += 1
        else:
            index[key] = len(rels)
            rels.append(record)
            new_links += 1

    if problems:
        raise FamilyTreeError('data/family_tree.json has problems:\n  - ' + '\n  - '.join(problems))
    return added, new_links, upgraded
