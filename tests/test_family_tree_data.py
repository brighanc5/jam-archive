"""data/family_tree.json: the editable Family Tree store and its merge rules."""
from pathlib import Path
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import family_tree_data as ft  # noqa: E402


def catalog():
    return {
        'entities': [
            {'id': 'phish', 'name': 'Phish', 'type': 'band', 'origins': [], 'aliases': []},
            {'id': 'trey-anastasio', 'name': 'Trey Anastasio', 'type': 'person', 'origins': [], 'aliases': ['Trey']},
        ],
        'relationships': [
            {'from': 'trey-anastasio', 'to': 'phish', 'type': 'member_of', 'source_url': '', 'note': '', 'verification': 'needs_review'},
        ],
    }


class MergeTests(unittest.TestCase):
    def test_sourced_link_upgrades_placeholder(self):
        cat = catalog()
        added, new, upgraded = ft.merge(cat, {'links': [{'from': 'Trey', 'to': 'Phish', 'source': 'https://example.org/x'}]})
        self.assertEqual((added, new, upgraded), (0, 0, 1))
        self.assertEqual(cat['relationships'][0]['verification'], 'verified')
        self.assertEqual(len(cat['relationships']), 1)

    def test_new_entry_and_link(self):
        cat = catalog()
        result = ft.merge(cat, {'entries': [{'name': 'Page McConnell', 'type': 'person'}],
                                'links': [{'from': 'Page McConnell', 'to': 'phish', 'source': 'https://example.org/p'}]})
        self.assertEqual(result, (1, 1, 0))
        self.assertIn('page-mcconnell', {e['id'] for e in cat['entities']})

    def test_rejects_unknown_names_missing_sources_and_duplicates(self):
        bad = {'links': [
            {'from': 'Nobody', 'to': 'Phish', 'source': 'https://example.org'},
            {'from': 'Trey', 'to': 'Phish', 'source': 'http://insecure.example'},
            {'from': 'Trey', 'to': 'Phish', 'source': 'https://example.org/a'},
            {'from': 'trey-anastasio', 'to': 'phish', 'source': 'https://example.org/b'},
        ]}
        with self.assertRaises(ft.FamilyTreeError) as err:
            ft.merge(catalog(), bad)
        message = str(err.exception)
        self.assertIn("unknown entry 'Nobody'", message)
        self.assertIn('https source', message)
        self.assertIn('listed twice', message)

    def test_repository_file_is_valid(self):
        data = json.loads(ft.DATA_FILE.read_text(encoding='utf-8'))
        self.assertIn('entries', data)
        self.assertIn('links', data)
        built = json.loads((ROOT / 'site/assets/catalog.json').read_text(encoding='utf-8'))
        public = {(r['from'], r['to'], r['type']) for r in built['relationships'] if r['verification'] == 'verified'}
        ids = {e['id'] for e in built['entities']}
        names = {e['name'].casefold(): e['id'] for e in built['entities']}
        for e in built['entities']:
            for a in e.get('aliases', []):
                names[a.casefold()] = e['id']
        for link in data['links']:
            a = link['from'] if link['from'] in ids else names[link['from'].casefold()]
            b = link['to'] if link['to'] in ids else names[link['to'].casefold()]
            self.assertIn((a, b, link.get('type', 'member_of')), public, link)


if __name__ == '__main__':
    unittest.main()
