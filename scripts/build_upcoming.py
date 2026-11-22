#!/usr/bin/env python3
"""Upcoming shows: data/upcoming_shows.json -> /upcoming/ and /upcoming/<id>/.

Runs after build_trails.py and BEFORE site_nav.py (which normalizes the header
this script writes). Idempotent, offline.

Every page is static. Past dates are hidden in the browser by jam_experience.js
(data-show-date / data-show-end), so the build stays deterministic.

Ticket prices: a show page gets a price table only when
upcoming_shows.comparable_prices() returns fresh, matched quotes from at least
two approved providers. Otherwise the page links to the official announcement
and says plainly that there's no comparison yet. A table carries
data-fresh-until; once that passes, jam_experience.js hides it and shows the
empty state instead. See docs/ticket-price-index.md.
"""
from collections import defaultdict
from datetime import date, datetime
from html import escape
from pathlib import Path
from urllib.parse import urlsplit
import json
import os
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import upcoming_shows  # noqa: E402

SITE = ROOT / 'site'
ORIGIN = os.environ.get('JAM_ARCHIVE_ORIGIN', 'https://thejamarchive.org').rstrip('/')
E = lambda s: escape(str(s), quote=True)

catalog = json.loads((ROOT / 'catalog.json').read_text(encoding='utf-8'))
ent = {e['id']: e for e in catalog['entities']}
graph = json.loads((SITE / 'assets/connections.json').read_text(encoding='utf-8'))
gname = {n['id']: n['name'] for n in graph['nodes']}
members = defaultdict(list)
for edge in graph['edges']:
    if edge['type'] == 'member_of':
        members[edge['to']].append(edge['from'])

shows_by_id = {s['id']: s for s in upcoming_shows.load()}
events = sorted(catalog['events'], key=lambda e: (e['date'], e['artist']))
assert {e['id'] for e in events} == set(shows_by_id), 'build_upcoming: catalog events differ from data/upcoming_shows.json'


def day(d, fmt='%A, %B %-d, %Y'):
    return date.fromisoformat(d).strftime(fmt)


def when(e):
    text = day(e['date'])
    if e.get('date_end'):
        text += ' through ' + day(e['date_end'], '%A, %B %-d')
    return text


def host(url):
    h = urlsplit(url).netloc
    return h[4:] if h.startswith('www.') else h


def ext(url, label, rel='noopener noreferrer'):
    return '<a href="' + E(url) + '" target="_blank" rel="' + rel + '">' + E(label) + ' ↗</a>'


def page(title, desc, route, body):
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta name="description" content="' + E(desc) + '"><meta property="og:title" content="' + E(title) + ' · The Jam Archive">'
            '<meta property="og:description" content="' + E(desc) + '"><meta property="og:type" content="website">'
            '<title>' + E(title) + ' · The Jam Archive</title><link rel="canonical" href="' + E(ORIGIN + route) + '">'
            '<link rel="stylesheet" href="/assets/detail.css"><link rel="stylesheet" href="/assets/site-quality.css"><link rel="stylesheet" href="/assets/jam-look.css"></head><body>'
            '<a class="ja-skip" href="#ja-main">Skip to main content</a><header><a href="/">The Jam Archive</a><nav aria-label="Archive sections"><a href="/connections/">Family Tree</a></nav></header>'
            '<main id="ja-main">' + body +
            '<footer>The Jam Archive doesn\'t sell tickets. Dates come from the artists\' and venues\' own announcements; confirm with them before you buy.</footer>'
            '</main><script src="/assets/jam-experience.js" defer></script></body></html>')


def price_table(show):
    rows = upcoming_shows.comparable_prices(show)
    if not rows:
        return ''
    qty = rows[0]['quantity']
    cur = rows[0]['currency']
    body = ''.join(
        '<tr><td>' + E(upcoming_shows.PROVIDERS[q['provider']]) + '</td><td>' + ('Resale' if q['market'] == 'resale' else 'Face value') + '</td>'
        '<td><b>' + E(f"{q['price_each']:,.2f} {cur}") + '</b> each</td><td>' + E(q.get('section') or 'Any seat') + '</td>'
        '<td>' + E(datetime.fromisoformat(q['captured_at'].replace('Z', '+00:00')).strftime('%b %-d, %-I:%M %p UTC')) + '</td>'
        '<td>' + ext(q['url'], 'View', 'sponsored noopener noreferrer' if q.get('affiliate') else 'noopener noreferrer') + '</td></tr>'
        for q in rows)
    note = ('All-in prices, fees included, for ' + str(qty) + ' tickets together, as of the time shown. '
            'Prices move fast; the seller\'s page is the final word.')
    if any(q.get('affiliate') for q in rows):
        note += ' Some of these links pay The Jam Archive a commission. It never changes the order, which is cheapest first.'
    return ('<section class="card ja-prices" data-fresh-until="' + E(upcoming_shows.fresh_until(rows)) + '"><h2>Ticket prices</h2><div class="ja-table-wrap"><table><thead><tr><th>Seller</th><th>Type</th><th>Lowest all-in</th><th>Seats</th><th>Checked</th><th></th></tr></thead>'
            '<tbody>' + body + '</tbody></table></div><p class="tiny">' + E(note) + '</p></section>')


routes = []
by_artist = defaultdict(list)
for e in events:
    by_artist[e['artist_id']].append(e)

for e in events:
    s = shows_by_id[e['id']]
    aid = e['artist_id']
    artist = ent[aid]['name'] if aid in ent else e['artist']
    place = e['venue'] + ', ' + e['city'] + ', ' + e['region']
    route = '/upcoming/' + e['id'] + '/'
    ticket_url = e.get('ticket_url') or e['source_url']
    who = ("the artist's or venue's own announcement" if e['source_type'].startswith('official')
           else "the band's own schedule, cross-checked with " + host(e['corroboration']) if e.get('corroboration') else "the band's own schedule")
    prices = price_table(s)
    # Empty state: shown whenever there's no comparison, and revealed by jam_experience.js if a table goes stale.
    price_note = ('<p class="tiny ja-price-note"' + (' hidden' if prices else '') + '>No price comparison for this show yet. '
                  'We only compare prices from approved seller feeds, with every mandatory fee included and the time each was checked.</p>')
    tickets = ('<div class="ja-ticket-box"><a class="button" href="' + E(ticket_url) + '" target="_blank" rel="noopener noreferrer">' +
               ('Get tickets' if e.get('ticket_url') else 'Tickets and info') + ' ↗</a>'
               '<p class="tiny">From ' + E(who) + ' on ' + E(host(e['source_url'])) + ', checked ' + E(day(e['verified_as_of'], '%B %-d, %Y')) +
               '. Plans change, so confirm there before you buy.</p>' + price_note + '</div>')
    past = ('<div class="ja-past-note" hidden><p>This one\'s in the books. Setlists and tapes usually turn up within a few days; '
            'start with <a href="/artists/' + E(aid) + '/">' + E(artist) + '\'s page</a>.</p></div>')
    collab = ('<p class="ja-show-note">' + E(e['note']) + '</p>') if e.get('collaboration_confirmed') and e.get('note') else ''
    billed = [p for p in e['performers'] if p != aid and p in ent]
    with_line = ('<p>With ' + ', '.join('<a href="/artists/' + E(p) + '/">' + E(ent[p]['name']) + '</a>' for p in billed) + '</p>') if billed else ''
    band = sorted(members.get(aid, []), key=lambda m: gname[m])
    tree = ''
    if band:
        tree = ('<section class="card"><h2>Who\'s in the band</h2><p class="tiny">Every musician we\'ve sourced as a member, past or present. '
                'It isn\'t a lineup for this show.</p><div class="ja-chips">' +
                ''.join('<a class="ja-chip" href="/artists/' + E(m) + '/">' + E(gname[m]) + '</a>' for m in band) + '</div>'
                '<p class="tiny"><a href="/connections/?artist=' + E(aid) + '">Open ' + E(artist) + ' in the Family Tree</a></p></section>')
    others = [x for x in by_artist[aid] if x['id'] != e['id']]
    more = ''
    if others:
        more = ('<section class="card" data-show-list><h2>More ' + E(artist) + ' dates</h2><ol class="ja-dates">' +
                ''.join('<li data-show-date="' + E(x['date']) + '" data-show-end="' + E(x.get('date_end') or x['date']) + '"><a href="/upcoming/' + E(x['id']) + '/">'
                        '<span class="ja-date">' + E(day(x['date'], '%a %b %-d')) + '</span><span>' + E(x['venue'] + ', ' + x['city']) + '</span></a></li>' for x in others) +
                '</ol><p class="empty ja-none-left" hidden>No other upcoming dates on our list.</p></section>')
    body = ('<article class="ja-show" data-show-date="' + E(e['date']) + '" data-show-end="' + E(e.get('date_end') or e['date']) + '">'
            '<p class="ja-show-when">' + E(when(e)) + '</p><h1>' + E(artist) + '</h1><p class="lead">' + E(place) + '</p>' + with_line + collab +
            tickets + past + prices + '</article>' + tree + more +
            '<p><a href="/upcoming/">All upcoming shows</a> · <a href="/artists/' + E(aid) + '/">About ' + E(artist) + '</a></p>')
    desc = artist + ' at ' + place + ' on ' + when(e) + '. Where to find tickets, and who\'s in the band.'
    out = SITE / 'upcoming' / e['id'] / 'index.html'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page(artist + ', ' + day(e['date'], '%b %-d, %Y') + ', ' + e['city'], desc, route, body), encoding='utf-8')
    routes.append(route)

# Index: grouped by month, past dates hidden in the browser.
months = defaultdict(list)
for e in events:
    months[e['date'][:7]].append(e)
sections = ''.join(
    '<section data-show-list><h2>' + E(date.fromisoformat(m + '-01').strftime('%B %Y')) + '</h2><ol class="ja-dates">' +
    ''.join('<li data-show-date="' + E(e['date']) + '" data-show-end="' + E(e.get('date_end') or e['date']) + '"><a href="/upcoming/' + E(e['id']) + '/">'
            '<span class="ja-date">' + E(day(e['date'], '%a %b %-d')) + '</span><b>' + E(ent[e['artist_id']]['name'] if e['artist_id'] in ent else e['artist']) + '</b>'
            '<span>' + E(e['venue'] + ', ' + e['city'] + ', ' + e['region']) + '</span></a></li>' for e in evs) +
    '</ol></section>' for m, evs in sorted(months.items()))
index = ('<h1>Upcoming shows</h1><p class="lead">Announced dates we\'ve checked against the band\'s or venue\'s own announcement. '
         'Pick a show for tickets and the band\'s Family Tree.</p>' + sections +
         '<p class="empty ja-none-left" hidden>Nothing on our list right now. We add dates as bands announce them.</p>'
         '<p class="tiny">This list is hand-checked, not a live feed, so it won\'t have every date. Know one we\'re missing? '
         '<a href="/contribute/">Send us the announcement</a>.</p>')
(SITE / 'upcoming').mkdir(exist_ok=True)
(SITE / 'upcoming' / 'index.html').write_text(page('Upcoming shows', 'Announced jam band shows, checked against official announcements, with links to tickets.', '/upcoming/', index), encoding='utf-8')
routes.append('/upcoming/')

# Sitemap must list every public route exactly once.
ns = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
ET.register_namespace('', ns[1:-1])
tree = ET.parse(SITE / 'sitemap.xml')
locs = {x.text for x in tree.getroot().iter(ns + 'loc')}
for route in routes:
    if ORIGIN + route not in locs:
        ET.SubElement(ET.SubElement(tree.getroot(), ns + 'url'), ns + 'loc').text = ORIGIN + route
tree.write(SITE / 'sitemap.xml', encoding='unicode', xml_declaration=True)
print(f'UPCOMING PASS: {len(events)} show pages + index; prices shown only with {upcoming_shows.MIN_PROVIDERS}+ approved providers')
