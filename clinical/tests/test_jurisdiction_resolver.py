"""Regression checks for non-prescriptive multi-country coverage."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from jurisdiction_resolver import compare_topic, load_matrix, PENDING, REFERENCE, CONFLICT


class MultiCountrySafety(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.matrix = load_matrix()

    def test_14_countries_and_unique_topics(self):
        self.assertEqual(len(self.matrix['countries']), 14)
        self.assertGreaterEqual(len(self.matrix['topics']), 60)
        self.assertEqual(len({t['id'] for t in self.matrix['topics']}), len(self.matrix['topics']))
        self.assertEqual(self.matrix['clinical_release_status'], 'CLINICALLY_PENDING')
        self.assertEqual(self.matrix['country_topic_reviews'], [])

    def test_all_country_topic_combinations_fail_closed(self):
        codes = [c['code'] for c in self.matrix['countries']]
        for topic in self.matrix['topics']:
            result = compare_topic(topic['id'], codes, self.matrix)
            self.assertEqual(len(result['country_comparison']), 14)
            for row in result['country_comparison']:
                self.assertEqual(row['source_review_status'], PENDING)
                self.assertFalse(row['clinical_use_permitted'])
                self.assertIsNone(row['dose'])
                self.assertIsNone(row['recommendation'])

    def test_country_mandatory_no_geo_language_fallback(self):
        for country in (None, [], 'ES', [''], ['ZZ'], ['es'], ['ES', 'ES']):
            with self.subTest(country=country), self.assertRaises(ValueError):
                compare_topic('medication.octaplex-pcc', country, self.matrix, language='pt')

    def test_language_does_not_switch_country(self):
        english = compare_topic('medication.amiodarona', ['BR'], self.matrix, language='en')
        portuguese = compare_topic('medication.amiodarona', ['BR'], self.matrix, language='pt')
        self.assertEqual(english, portuguese)
        self.assertEqual(english['country_comparison'][0]['country_code'], 'BR')

    def test_review_does_not_transfer_to_other_country(self):
        matrix = copy.deepcopy(self.matrix)
        matrix['country_topic_reviews'] = [{
            'country_code': 'ES', 'topic_id': 'medication.octaplex-pcc',
            'review_status': 'DOCUMENTARY_REVIEWED', 'indication': 'synthetic',
            'population': 'synthetic', 'setting': 'synthetic',
            'source_url': 'https://example.invalid/synthetic-fixture',
            'source_title': 'Synthetic fixture, not clinical evidence',
            'source_version': 'test', 'source_date': '2026-01-01',
            'verified_at': '2026-11-16', 'reviewer_clinical': 'synthetic'
        }]
        rows = compare_topic('medication.octaplex-pcc', ['ES', 'PT'], matrix)['country_comparison']
        self.assertEqual(rows[0]['source_review_status'], REFERENCE)
        self.assertEqual(rows[1]['source_review_status'], PENDING)
        self.assertTrue(all(not x['clinical_use_permitted'] for x in rows))

    def test_incomplete_review_never_passes(self):
        matrix = copy.deepcopy(self.matrix)
        matrix['country_topic_reviews'] = [{
            'country_code': 'ES', 'topic_id': 'medication.amiodarona',
            'review_status': 'DOCUMENTARY_REVIEWED'}]
        result = compare_topic('medication.amiodarona', ['ES'], matrix)
        self.assertEqual(result['country_comparison'][0]['source_review_status'], PENDING)

    def test_multiple_reviews_require_conflict_resolution(self):
        matrix = copy.deepcopy(self.matrix)
        x = {'country_code': 'ES', 'topic_id': 'medication.amiodarona'}
        matrix['country_topic_reviews'] = [x, x]
        result = compare_topic('medication.amiodarona', ['ES'], matrix)
        self.assertEqual(result['country_comparison'][0]['source_review_status'], CONFLICT)

    def test_unknown_topic_rejected(self):
        with self.assertRaises(ValueError):
            compare_topic('medication.invalid', ['ES'], self.matrix)


if __name__ == '__main__':
    unittest.main()
