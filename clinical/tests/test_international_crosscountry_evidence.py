"""Check sourced multinational comparison examples never become prescribing rules."""
import json
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / 'references'


class InternationalEvidenceCandidates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.candidates = json.loads((BASE / 'international-crosscountry-evidence-candidates-2026-11-16.json').read_text(encoding='utf-8'))
        cls.matrix = json.loads((BASE / 'international-country-topic-matrix.json').read_text(encoding='utf-8'))

    def test_examples_are_source_candidates_not_medication_contracts(self):
        self.assertEqual(self.candidates['clinical_status'], 'CLINICALLY_PENDING')
        self.assertEqual(self.candidates['review_state'], 'SOURCE_CANDIDATES_ONLY')
        for row in self.candidates['comparisons']:
            self.assertFalse(row['clinical_use_permitted'])
            self.assertFalse(row['calculation_enabled'])
            self.assertNotIn('dose', row)
            self.assertNotIn('pump_ml_h', row)

    def test_all_observations_have_an_eligible_country_and_https_source(self):
        known = {c['code'] for c in self.matrix['countries']}
        # EU-wide observations are not incorrectly treated as a country; national evidence must be explicit.
        for row in self.candidates['comparisons']:
            for observation in row['jurisdiction_evidence']:
                self.assertIn(observation['code'], known | {'EU'})
                self.assertTrue(observation['source_url'].startswith('https://'))
                self.assertTrue(observation['source_type'])

    def test_evidence_topics_are_crosslinked_to_matrix(self):
        allowed = {t['id'] for t in self.matrix['topics']}
        self.assertEqual(len(self.candidates['comparisons']), 2)
        self.assertTrue(all(row['topic_id'] in allowed for row in self.candidates['comparisons']))
        self.assertEqual(len(self.matrix['country_topic_reviews']), 0)


if __name__ == '__main__':
    unittest.main()
