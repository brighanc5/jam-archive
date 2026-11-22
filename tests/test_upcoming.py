"""Upcoming shows: data rules, pages, and the safeguards on ticket prices.

The price cases mirror the Ticket Price Index v0.1 comparator: exact event-ID
match, licensed feeds only, all-in fees, seats together, normal view, fresh
quotes, and at least two providers. Fixtures live only in this file; nothing
synthetic is ever written to data/.
"""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import copy
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
sys.path.insert(0, str(ROOT))
import upcoming_shows as us  # noqa: E402

NOW = datetime(2026, 11, 22, 17, 0, tzinfo=timezone.utc)
IDS = {'stubhub': 'sh-1', 'tickpick': 'tp-1', 'seatgeek': 'sg-1', 'ticketmaster': 'tm-1'}
BASE = {'id': 'test-show', 'artist': 'Phish', 'date': '2027-01-01', 'venue': 'V', 'city': 'C', 'region': 'R',
        'source': 'https://phish.com/tours/', 'checked_on': '2026-11-21', 'tickets': {'official_url': None},
        'marketplace_ids': dict(IDS), 'price_snapshots': []}


def ago(minutes):
    return (NOW - timedelta(minutes=minutes)).strftime('%Y-%m-%dT%H:%M:%SZ')


def quote(provider, price, when=None, **kw):
    q = {'provider': provider, 'event_id': IDS.get(provider, 'x'), 'feed': 'api', 'market': 'resale', 'all_in': True,
         'price_each': price, 'quantity': 2, 'seats_together': True, 'view': 'normal', 'currency': 'USD',
         'captured_at': when or ago(30), 'url': 'https://www.' + provider + '.com/event/1'}
    q.update(kw)
    return q


def show(*quotes):
    return dict(copy.deepcopy(BASE), price_snapshots=list(quotes))


def problems(*quotes):
    try:
        us.validate({'shows': [show(*quotes)]})
    except us.ShowDataError as err:
        return str(err)
    return ''


class DataRules(unittest.TestCase):
    def test_published_data_is_valid(self):
        shows = us.load()
        self.assertTrue(shows)
        self.assertEqual(len({s['id'] for s in shows}), len(shows))

    def test_a_well_formed_quote_passes(self):
        self.assertEqual(problems(quote('stubhub', 80), quote('tickpick', 90.5)), '')

    def test_rejects_prices_without_fees(self):
        self.assertIn('all-in', problems(quote('stubhub', 80, all_in=False)))

    def test_rejects_unapproved_provider_and_missing_source(self):
        s = show(quote('scalperbot', 50))
        s['source'] = 'http://example.org'
        with self.assertRaises(us.ShowDataError) as err:
            us.validate({'shows': [s]})
        self.assertIn('source', str(err.exception))
        self.assertIn('unknown provider', str(err.exception))

    def test_rejects_quote_for_a_different_or_unmapped_event(self):
        self.assertIn('event_id', problems(quote('stubhub', 80, event_id='some-other-show')))
        s = show(quote('stubhub', 80))
        s['marketplace_ids'] = {}
        with self.assertRaises(us.ShowDataError) as err:
            us.validate({'shows': [s]})
        self.assertIn('event_id', str(err.exception))

    def test_synthetic_prices_cannot_enter_the_data(self):
        self.assertIn('feed', problems(quote('stubhub', 80, feed='demo')))
        self.assertIn('feed', problems(quote('stubhub', 80, feed=None)))
        for url in ('https://example.com/fictional-ticket', 'https://tickets.example.org/x', 'https://seller.test/x'):
            self.assertIn('reserved test domain', problems(quote('stubhub', 80, url=url)), url)

    def test_rejects_ambiguous_fields(self):
        self.assertIn('timezone', problems(quote('stubhub', 80, captured_at='2026-11-22T12:00:00')))
        self.assertIn('seats_together', problems(quote('stubhub', 80, seats_together='yes')))
        self.assertIn('view', problems(quote('stubhub', 80, view='obstructed-ish')))
        self.assertIn('2 decimals', problems(quote('stubhub', 80.125)))
        self.assertIn('quantity', problems(quote('stubhub', 80, quantity=True)))


class PriceGate(unittest.TestCase):
    def rows(self, *quotes, **kw):
        return us.comparable_prices(show(*quotes), now=NOW, **kw)

    def test_one_provider_is_not_a_comparison(self):
        self.assertIsNone(self.rows(quote('stubhub', 80), quote('stubhub', 70, ago(10))))

    def test_two_providers_cheapest_first_latest_quote_wins(self):
        rows = self.rows(quote('stubhub', 80, ago(60)), quote('stubhub', 95, ago(10)),
                         quote('tickpick', 90), quote('seatgeek', 60, quantity=1))
        self.assertEqual([(q['provider'], q['price_each']) for q in rows], [('tickpick', 90), ('stubhub', 95)])

    def test_stale_and_future_quotes_are_excluded(self):
        s = show()
        old = quote('tickpick', 50, ago(us.MAX_QUOTE_AGE.total_seconds() / 60 + 1))
        future = quote('tickpick', 50, (NOW + timedelta(minutes=5)).strftime('%Y-%m-%dT%H:%M:%SZ'))
        self.assertEqual(us.exclusion_reasons(s, old, now=NOW), ['stale_quote'])
        self.assertEqual(us.exclusion_reasons(s, future, now=NOW), ['observation_in_future'])
        self.assertIsNone(self.rows(quote('stubhub', 80), old))
        self.assertIsNone(self.rows(quote('stubhub', 80), future))

    def test_seats_must_be_together_for_the_requested_quantity(self):
        q = quote('tickpick', 50, seats_together=False)
        self.assertIn('seats_not_together', us.exclusion_reasons(show(), q, now=NOW))
        self.assertIsNone(self.rows(quote('stubhub', 80), q))
        self.assertIn('different_quantity', us.exclusion_reasons(show(), quote('tickpick', 50), quantity=4, now=NOW))

    def test_restricted_or_unknown_views_are_never_compared(self):
        for view in ('restricted', 'unknown'):
            q = quote('tickpick', 50, view=view)
            self.assertEqual(us.exclusion_reasons(show(), q, now=NOW), ['view_not_normal'])
            self.assertIsNone(self.rows(quote('stubhub', 80), q))

    def test_wrong_event_id_and_unknown_fees_are_excluded_even_if_unvalidated(self):
        # Belt and braces: the gate re-checks what validate() enforces.
        s = show()
        self.assertIn('event_not_verified', us.exclusion_reasons(s, quote('stubhub', 80, event_id='other'), now=NOW))
        self.assertIn('mandatory_fees_unknown', us.exclusion_reasons(s, quote('stubhub', 80, all_in=False), now=NOW))
        self.assertIn('not_a_licensed_feed', us.exclusion_reasons(s, quote('stubhub', 80, feed='demo'), now=NOW))

    def test_newest_excluded_quote_falls_back_to_an_older_fresh_one(self):
        rows = self.rows(quote('stubhub', 80, ago(60)), quote('stubhub', 70, ago(5), view='restricted'), quote('tickpick', 90))
        self.assertEqual([(q['provider'], q['price_each']) for q in rows], [('stubhub', 80), ('tickpick', 90)])

    def test_mixed_currencies_are_not_compared(self):
        self.assertIsNone(self.rows(quote('stubhub', 80), quote('tickpick', 90, currency='CAD')))

    def test_fresh_until_is_oldest_quote_plus_max_age(self):
        rows = self.rows(quote('stubhub', 80, ago(30)), quote('tickpick', 90, ago(90)))
        expected = (NOW - timedelta(minutes=90) + us.MAX_QUOTE_AGE).strftime('%Y-%m-%dT%H:%M:%SZ')
        self.assertEqual(us.fresh_until(rows), expected)


class Pages(unittest.TestCase):
    def test_every_show_has_a_page_in_the_sitemap(self):
        sitemap = (SITE / 'sitemap.xml').read_text(encoding='utf-8')
        for s in us.load():
            page = SITE / 'upcoming' / s['id'] / 'index.html'
            self.assertTrue(page.exists(), s['id'])
            self.assertIn('/upcoming/' + s['id'] + '/', sitemap)
            html = page.read_text(encoding='utf-8')
            self.assertIn(s['source'].replace('&', '&amp;'), html)
            self.assertIn('ja-price-note', html, s['id'])
            if us.comparable_prices(s) is None:
                self.assertNotIn('ja-prices', html)
                self.assertIn('No price comparison for this show yet', html)
                self.assertNotIn('class="tiny ja-price-note" hidden', html)

    def test_no_synthetic_or_unmatched_prices_on_any_page(self):
        for s in us.load():
            html = (SITE / 'upcoming' / s['id'] / 'index.html').read_text(encoding='utf-8')
            for bad in ('example.com', 'example.org', 'Fictional', 'demo-'):
                self.assertNotIn(bad, html, s['id'])
            for q in s.get('price_snapshots') or []:
                self.assertEqual(q['event_id'], s['marketplace_ids'][q['provider']])

    def test_index_lists_every_show(self):
        html = (SITE / 'upcoming' / 'index.html').read_text(encoding='utf-8')
        for s in us.load():
            self.assertIn('/upcoming/' + s['id'] + '/', html)


if __name__ == '__main__':
    unittest.main()
