"""Synthetic scoring and guide safety regressions for the adult cognitive review."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from core_scores_block14_adult_remaining import calculate_four_at
from load_module import load


class CognitiveReviewTests(unittest.TestCase):
    def test_four_at_failure_refusal_and_untestable_have_distinct_scores(self):
        base = {'alertness': 'normal', 'amt4_mistakes': 0,
                'attention_months_backward': 12, 'acute_change_or_fluctuation': False}
        for value, points in [(0, 1), (1, 1), (6, 1), (7, 0), (12, 0),
                              ('refuses', 1), ('untestable', 2)]:
            with self.subTest(value=value):
                result = calculate_four_at({**base, 'attention_months_backward': value})
                self.assertEqual(result['components']['attention'], points)
                self.assertEqual(result['total'], points)
        both = calculate_four_at({**base, 'amt4_mistakes': 'untestable',
                                  'attention_months_backward': 'untestable'})
        self.assertEqual(both['total'], 4)
        self.assertEqual(both['interpretation'], 'possible_delirium_ge4')
        maximum = calculate_four_at({**base, 'alertness': 'clearly_abnormal',
                                    'amt4_mistakes': 4,
                                    'attention_months_backward': 'untestable',
                                    'acute_change_or_fluctuation': True})
        self.assertEqual(maximum['total'], 12)
        self.assertIn('does not definitively exclude delirium',
                      calculate_four_at(base)['warning'])

    def test_four_at_rejects_invalid_counts_instead_of_truncating(self):
        base = {'alertness': 'normal', 'amt4_mistakes': 0,
                'attention_months_backward': 12, 'acute_change_or_fluctuation': False}
        for key, values in [('amt4_mistakes', [-1, 5, 1.2, True, '1']),
                            ('attention_months_backward', [-1, 13, 6.9, False,
                                                           float('nan'), 10**400])]:
            for value in values:
                with self.subTest(key=key, value=str(value)[:16]), self.assertRaises(ValueError):
                    calculate_four_at({**base, key: value})
        del base['acute_change_or_fluctuation']
        with self.assertRaises(ValueError):
            calculate_four_at(base)

    def test_delirium_separates_screening_safety_and_icu_evidence(self):
        text = ' '.join(load(ROOT, 'delirium').split())
        for phrase in ('4AT', 'CAM-ICU or ICDSC',
                       'not a negative delirium result',
                       '0 does not definitively exclude delirium',
                       'Parkinson disease or dementia with Lewy bodies',
                       'baseline ECG', '1 week or less',
                       'could not recommend for or against antipsychotics',
                       'not routine non-withdrawal delirium'):
            self.assertIn(phrase, text)

    def test_withdrawal_keeps_loading_and_thiamine_phases_separate(self):
        text = ' '.join(load(ROOT, 'alcohol-withdrawal').split())
        for phrase in ('not a stand-alone diagnosis',
                       '20 mg orally every 2 h for 3 doses',
                       'not a compulsory 60 mg course',
                       '50 mg orally four times daily',
                       '200--300 mg IV or IM once daily',
                       '300--500 mg IV three times daily',
                       'after the first 5 days',
                       'do not delay glucose for hypoglycemia',
                       'cumulative-dose/airway plan',
                       'respiratory depression', 'senior/ICU assessment'):
            self.assertIn(phrase, text)

    def test_consciousness_supports_cause_search_and_specific_rescue(self):
        text = ' '.join(load(ROOT, 'altered-consciousness').split())
        for phrase in ('check bedside glucose immediately',
                       'do not delay glucose for thiamine',
                       'not an isolated score alone',
                       'Persistent altered mental status despite treatment',
                       'Consider EEG',
                       'Do not give flumazenil empirically for unexplained coma',
                       'without delaying resuscitation',
                       'Full recovery alone is insufficient for discharge'):
            self.assertIn(phrase, text)


if __name__ == '__main__':
    unittest.main()
