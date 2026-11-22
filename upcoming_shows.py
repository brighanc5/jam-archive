"""Upcoming shows: load, validate, and (one day) compare ticket prices.

data/upcoming_shows.json is the only place show data lives. build_archive.py
loads it into the catalog; scripts/build_upcoming.py turns it into pages.

Ticket prices are designed in but switched off by data: a show only gets a price
table when at least MIN_PROVIDERS different approved providers have an all-in
quote for the same number of tickets. See docs/ticket-price-index.md.
"""
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlsplit
import json
import re

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data' / 'upcoming_shows.json'

# Providers we may ever show prices from. Adding one means an approved, licensed feed.
PROVIDERS = {'ticketmaster': 'Ticketmaster', 'tickpick': 'TickPick', 'stubhub': 'StubHub',
             'seatgeek': 'SeatGeek', 'vividseats': 'Vivid Seats'}
MARKETS = {'primary', 'resale'}
MIN_PROVIDERS = 2


class ShowDataError(ValueError):
    pass


def _https(url):
    return isinstance(url, str) and urlsplit(url).scheme == 'https' and bool(urlsplit(url).netloc)


def _iso_day(v):
    try:
        return date.fromisoformat(v)
    except (TypeError, ValueError):
        return None


def validate(doc, known_names=None):
    """Return the list of shows, or raise ShowDataError listing every problem."""
    problems, seen = [], set()
    for i, s in enumerate(doc.get('shows', [])):
        where = f"show {i + 1} ({s.get('id', '?')})"
        sid = s.get('id')
        if not isinstance(sid, str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]*', sid):
            problems.append(f'{where}: id must be lowercase letters, digits and dashes')
        elif sid in seen:
            problems.append(f'{where}: duplicate id')
        seen.add(sid)
        for key in ('artist', 'venue', 'city', 'region'):
            if not s.get(key):
                problems.append(f'{where}: missing {key}')
        if not _iso_day(s.get('date')):
            problems.append(f'{where}: date must be YYYY-MM-DD')
        if s.get('date_end') and (not _iso_day(s['date_end']) or s['date_end'] < s.get('date', '')):
            problems.append(f'{where}: date_end must be a YYYY-MM-DD on or after date')
        if not _iso_day(s.get('checked_on')):
            problems.append(f'{where}: checked_on must be YYYY-MM-DD')
        if not _https(s.get('source')):
            problems.append(f'{where}: source must be an https link that announces the show')
        if s.get('corroboration') and not _https(s['corroboration']):
            problems.append(f'{where}: corroboration must be https')
        names = s.get('performers') or [s.get('artist')]
        if known_names is not None:
            for n in [s.get('artist')] + list(names):
                if n not in known_names:
                    problems.append(f'{where}: unknown artist name "{n}" (add it to the Family Tree first)')
        official = (s.get('tickets') or {}).get('official_url')
        if official is not None and not _https(official):
            problems.append(f'{where}: tickets.official_url must be https or null')
        for prov, ext in (s.get('marketplace_ids') or {}).items():
            if prov not in PROVIDERS or not isinstance(ext, str) or not ext:
                problems.append(f'{where}: marketplace_ids.{prov} is not an approved provider with an id')
        for j, q in enumerate(s.get('price_snapshots') or []):
            w = f'{where} price_snapshots[{j}]'
            if q.get('provider') not in PROVIDERS:
                problems.append(f'{w}: unknown provider')
            if q.get('market') not in MARKETS:
                problems.append(f'{w}: market must be primary or resale')
            if q.get('all_in') is not True:
                problems.append(f'{w}: only all-in prices (fees included) are allowed')
            if not isinstance(q.get('price_each'), (int, float)) or q['price_each'] <= 0:
                problems.append(f'{w}: price_each must be a positive number')
            if not isinstance(q.get('quantity'), int) or q['quantity'] < 1:
                problems.append(f'{w}: quantity must be a whole number of tickets')
            if q.get('currency') not in ('USD', 'CAD', 'MXN', 'JPY', 'EUR', 'GBP'):
                problems.append(f'{w}: currency missing or unsupported')
            try:
                datetime.fromisoformat(str(q.get('captured_at')).replace('Z', '+00:00'))
            except ValueError:
                problems.append(f'{w}: captured_at must be an ISO timestamp')
            if 'affiliate' in q and not isinstance(q['affiliate'], bool):
                problems.append(f'{w}: affiliate must be true or false')
            if not _https(q.get('url')):
                problems.append(f'{w}: url must be https')
    if problems:
        raise ShowDataError('data/upcoming_shows.json has problems:\n  - ' + '\n  - '.join(problems))
    return doc['shows']


def load(known_names=None):
    return validate(json.loads(DATA.read_text(encoding='utf-8')), known_names)


def comparable_prices(show, quantity=2):
    """Latest all-in quote per provider for `quantity` tickets, cheapest first.

    Returns None unless MIN_PROVIDERS different providers have such a quote:
    one marketplace on its own is a link, not a comparison.
    """
    latest = {}
    for q in show.get('price_snapshots') or []:
        if q.get('quantity') != quantity or q.get('all_in') is not True:
            continue
        p = q['provider']
        if p not in latest or q['captured_at'] > latest[p]['captured_at']:
            latest[p] = q
    if len(latest) < MIN_PROVIDERS or len({q['currency'] for q in latest.values()}) != 1:
        return None
    return sorted(latest.values(), key=lambda q: q['price_each'])
