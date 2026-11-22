"""Upcoming shows: data rules, pages, and the two-provider gate on ticket prices."""
from pathlib import Path
import copy
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
sys.path.insert(0, str(ROOT))
import upcoming_shows as us  # noqa: E402

BASE = {'id': 'test-show', 'artist': 'Phish', 'date': '2027-01-01', 'venue': 'V', 'city': 'C', 'region': 'R',
        'source': 'https://example.org/tour', 'checked_on': '2026-11-21', 'tickets': {'official_url': None},
        'marketplace_ids': {}, 'price_snapshots': []}


def quote(provider, price, when='2026-11-21T12:00:00Z', **kw):
    q = {'provider': provider, 'market': 'resale', 'all_in': True, 'price_each': price, 'quantity': 2,
         'currency': 'USD', 'captured_at': when, 'url': 'https://example.org/' + provider}
    q.update(kw)
    return q


class DataRules(unittest.TestCase):
    def test_published_data_is_valid(self):
        shows = us.load()
        self.assertTrue(shows)
        self.assertEqual(len({s['id'] for s in shows}), len(shows))

    def test_rejects_prices_without_fees(self):
        s = copy.deepcopy(BASE)
        s['price_snapshots'] = [quote('stubhub', 80, all_in=False)]
        with self.assertRaises(us.ShowDataError):
            us.validate({'shows': [s]})

    def test_rejects_unapproved_provider_and_missing_source(self):
        s = copy.deepcopy(BASE)
        s['source'] = 'http://example.org'
        s['price_snapshots'] = [quote('scalperbot', 50)]
        with self.assertRaises(us.ShowDataError) as err:
            us.validate({'shows': [s]})
        self.assertIn('source', str(err.exception))
        self.assertIn('unknown provider', str(err.exception))


class PriceGate(unittest.TestCase):
    def test_one_provider_is_not_a_comparison(self):
        s = dict(BASE, price_snapshots=[quote('stubhub', 80), quote('stubhub', 70, '2026-11-21T13:00:00Z')])
        self.assertIsNone(us.comparable_prices(s))

    def test_two_providers_cheapest_first_latest_quote_wins(self):
        s = dict(BASE, price_snapshots=[
            quote('stubhub', 80), quote('stubhub', 95, '2026-11-21T13:00:00Z'),
            quote('tickpick', 90), quote('seatgeek', 60, quantity=1)])
        rows = us.comparable_prices(s)
        self.assertEqual([(q['provider'], q['price_each']) for q in rows], [('tickpick', 90), ('stubhub', 95)])


class Pages(unittest.TestCase):
    def test_every_show_has_a_page_in_the_sitemap(self):
        sitemap = (SITE / 'sitemap.xml').read_text(encoding='utf-8')
        for s in us.load():
            page = SITE / 'upcoming' / s['id'] / 'index.html'
            self.assertTrue(page.exists(), s['id'])
            self.assertIn('/upcoming/' + s['id'] + '/', sitemap)
            html = page.read_text(encoding='utf-8')
            self.assertIn(s['source'].replace('&', '&amp;'), html)
            if us.comparable_prices(s) is None:
                self.assertNotIn('ja-prices', html)

    def test_index_lists_every_show(self):
        html = (SITE / 'upcoming' / 'index.html').read_text(encoding='utf-8')
        for s in us.load():
            self.assertIn('/upcoming/' + s['id'] + '/', html)


if __name__ == '__main__':
    unittest.main()
