"""Upcoming shows: load, validate, and (one day) compare ticket prices.

data/upcoming_shows.json is the only place show data lives. build_archive.py
loads it into the catalog; scripts/build_upcoming.py turns it into pages.

Ticket prices are designed in but switched off by data: a show only gets a price
table when at least MIN_PROVIDERS different approved providers have a fresh,
all-in quote for the same number of seats together, with a normal view, from a
licensed feed, for the provider event ID we matched by hand.
See docs/ticket-price-index.md.
"""
from datetime import date, datetime, timedelta, timezone
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
FEEDS = {'api', 'licensed_feed'}          # how a quote reached us; anything else (e.g. 'demo') is rejected
VIEWS = {'normal', 'restricted', 'unknown'}  # only 'normal' is ever compared
MIN_PROVIDERS = 2
MAX_QUOTE_AGE = timedelta(hours=24)       # older quotes are dropped at build time and hidden in the browser
CLOCK_SKEW = timedelta(minutes=1)
# Reserved test domains (RFC 2606/6761): a quote pointing at one is synthetic by definition.
_TEST_HOSTS = re.compile(r'(^|\.)(example\.(com|net|org)|[^.]+\.(example|test|invalid|localhost))$|^localhost$')


class ShowDataError(ValueError):
    pass


def _https(url):
    return isinstance(url, str) and urlsplit(url).scheme == 'https' and bool(urlsplit(url).netloc)


def _iso_day(v):
    try:
        return date.fromisoformat(v)
    except (TypeError, ValueError):
        return None


def _instant(v):
    """Timezone-aware datetime from an ISO timestamp, or None (naive times are ambiguous)."""
    try:
        t = datetime.fromisoformat(str(v).replace('Z', '+00:00'))
    except ValueError:
        return None
    return t if t.tzinfo else None


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
        mapped = s.get('marketplace_ids') or {}
        for prov, ext in mapped.items():
            if prov not in PROVIDERS or not isinstance(ext, str) or not ext:
                problems.append(f'{where}: marketplace_ids.{prov} is not an approved provider with an id')
        for j, q in enumerate(s.get('price_snapshots') or []):
            w = f'{where} price_snapshots[{j}]'
            prov = q.get('provider')
            if prov not in PROVIDERS:
                problems.append(f'{w}: unknown provider')
            elif not mapped.get(prov) or q.get('event_id') != mapped[prov]:
                # Never fuzzy-match: the quote must name the exact event ID we reviewed for this show.
                problems.append(f'{w}: event_id must equal marketplace_ids.{prov} for this show')
            if q.get('feed') not in FEEDS:
                problems.append(f'{w}: feed must be api or licensed_feed (no demo or hand-typed prices)')
            if q.get('market') not in MARKETS:
                problems.append(f'{w}: market must be primary or resale')
            if q.get('all_in') is not True:
                problems.append(f'{w}: only all-in prices (fees included) are allowed')
            p = q.get('price_each')
            if isinstance(p, bool) or not isinstance(p, (int, float)) or p <= 0 or abs(p * 100 - round(p * 100)) > 1e-6:
                problems.append(f'{w}: price_each must be a positive amount with at most 2 decimals')
            if isinstance(q.get('quantity'), bool) or not isinstance(q.get('quantity'), int) or q['quantity'] < 1:
                problems.append(f'{w}: quantity must be a whole number of tickets')
            if not isinstance(q.get('seats_together'), bool):
                problems.append(f'{w}: seats_together must be true or false')
            if q.get('view') not in VIEWS:
                problems.append(f'{w}: view must be normal, restricted or unknown')
            if q.get('currency') not in ('USD', 'CAD', 'MXN', 'JPY', 'EUR', 'GBP'):
                problems.append(f'{w}: currency missing or unsupported')
            if _instant(q.get('captured_at')) is None:
                problems.append(f'{w}: captured_at must be an ISO timestamp with a timezone (e.g. ...Z)')
            if 'affiliate' in q and not isinstance(q['affiliate'], bool):
                problems.append(f'{w}: affiliate must be true or false')
            if not _https(q.get('url')):
                problems.append(f'{w}: url must be https')
            elif _TEST_HOSTS.search(urlsplit(q['url']).hostname or ''):
                problems.append(f'{w}: url points at a reserved test domain; synthetic prices never publish')
    if problems:
        raise ShowDataError('data/upcoming_shows.json has problems:\n  - ' + '\n  - '.join(problems))
    return doc['shows']


def load(known_names=None):
    return validate(json.loads(DATA.read_text(encoding='utf-8')), known_names)


def exclusion_reasons(show, q, quantity=2, now=None):
    """Why a (validated) quote can't be compared right now; [] means it can.

    Mirrors the Ticket Price Index v0.1 comparator: exact event-ID match, licensed
    feed, all-in fees, the requested number of seats together, normal view, fresh.
    """
    now = now or datetime.now(timezone.utc)
    reasons = []
    if (show.get('marketplace_ids') or {}).get(q.get('provider')) != q.get('event_id') or not q.get('event_id'):
        reasons.append('event_not_verified')
    if q.get('feed') not in FEEDS:
        reasons.append('not_a_licensed_feed')
    if q.get('all_in') is not True:
        reasons.append('mandatory_fees_unknown')
    if q.get('quantity') != quantity:
        reasons.append('different_quantity')
    if q.get('seats_together') is not True:
        reasons.append('seats_not_together')
    if q.get('view') != 'normal':
        reasons.append('view_not_normal')
    t = _instant(q.get('captured_at'))
    if t is None:
        reasons.append('no_timestamp')
    elif t - now > CLOCK_SKEW:
        reasons.append('observation_in_future')
    elif now - t > MAX_QUOTE_AGE:
        reasons.append('stale_quote')
    return reasons


def comparable_prices(show, quantity=2, now=None):
    """Latest comparable quote per provider for `quantity` seats together, cheapest first.

    Returns None unless MIN_PROVIDERS different providers have such a quote in one
    currency: one marketplace on its own is a link, not a comparison.
    """
    now = now or datetime.now(timezone.utc)
    latest = {}
    for q in show.get('price_snapshots') or []:
        if exclusion_reasons(show, q, quantity, now):
            continue
        p, key = q['provider'], (_instant(q['captured_at']), -q['price_each'])
        if p not in latest or key > latest[p][0]:
            latest[p] = (key, q)
    rows = [q for _, q in latest.values()]
    if len(rows) < MIN_PROVIDERS or len({q['currency'] for q in rows}) != 1:
        return None
    return sorted(rows, key=lambda q: (q['price_each'], q['provider']))


def fresh_until(rows):
    """When the oldest quote in a comparison expires (ISO, UTC); the browser hides the table after this."""
    oldest = min(_instant(q['captured_at']) for q in rows)
    return (oldest + MAX_QUOTE_AGE).astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
