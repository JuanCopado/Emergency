"""QA-only synthetic tests, NOT a syringe validation or production acceptance."""
import unittest
import sys
from decimal import Decimal
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from anaphylaxis_under6months_microvolume_preflight import preflight


class MicrovolumePreflightTests(unittest.TestCase):
    def setUp(self):
        self.base = dict(age_months=2, weight_kg=5, route='IM',
                         concentration_mg_ml=1, measurement_increment_ml=0.01)

    def run_case(self, **kwargs):
        return preflight(**{**self.base, **kwargs})

    def test_01_five_kg_exact(self):
        v = self.run_case()
        self.assertEqual(Decimal(v['theoretical_ml_for_qa_only']), Decimal('0.05'))
        self.assertEqual(Decimal(v['qa_rounding_relative_error_percent']), 0)

    def test_02_seven_point_six_kg_rounding_error(self):
        v = self.run_case(weight_kg=7.6, age_months=5)
        self.assertEqual(Decimal(v['theoretical_ml_for_qa_only']), Decimal('0.076'))
        self.assertEqual(Decimal(v['qa_rounding_candidate_ml_NOT_FOR_ADMINISTRATION']), Decimal('0.08'))
        self.assertEqual(Decimal(v['qa_rounding_relative_error_percent']), Decimal('5.263'))

    def test_03_three_point_two_kg_neonatal_requires_review(self):
        v = self.run_case(weight_kg=3.2, age_months=0.2)
        self.assertEqual(Decimal(v['theoretical_ml_for_qa_only']), Decimal('0.032'))
        self.assertIn('NEONATAL_SPECIALIST_REVIEW_REQUIRED', v['flags'])

    def test_04_exact_six_months_excluded(self):
        v = self.run_case(age_months=6)
        self.assertNotIn('theoretical_ml_for_qa_only', v)

    def test_05_unknown_weight_no_default(self):
        v = self.run_case(weight_kg=None)
        self.assertIn('WEIGHT_MISSING_OR_INVALID_NO_AGE_DEFAULT', v['flags'])
        self.assertNotIn('theoretical_ml_for_qa_only',v)

    def test_06_iv_concentration_rejected_for_im(self):
        v = self.run_case(concentration_mg_ml=0.1)
        self.assertIn('CONCENTRATION_MISMATCH_1MG_ML_IM_REQUIRED',v['flags'])
        self.assertNotIn('theoretical_ml_for_qa_only',v)

    def test_07_iv_route_rejected(self):
        v=self.run_case(route='IV')
        self.assertIn('WRONG_ROUTE_IM_ONLY',v['flags'])

    def test_08_invalid_weights(self):
        for invalid in (0,-1,'5',float('nan'),float('inf'),True):
            with self.subTest(invalid=repr(invalid)):
                self.assertNotIn('theoretical_ml_for_qa_only',self.run_case(weight_kg=invalid))

    def test_09_repeat_not_auto_ordered(self):
        self.assertFalse(self.run_case(prior_im_doses=1)['prescription_enabled'])

    def test_10_two_prior_doses_escalation_only(self):
        v=self.run_case(prior_im_doses=2)
        self.assertIn('SPECIALIST_ESCALATION_ALERT_ONLY_NO_IV_AUTOMATION',v['flags'])
        self.assertFalse(v['prescription_enabled'])

    def test_11_missing_device_means_no_rounding(self):
        v=self.run_case(measurement_increment_ml=None)
        self.assertIn('DEVICE_INCREMENT_UNKNOWN_NO_ROUNDING',v['flags'])
        self.assertNotIn('qa_rounding_candidate_ml_NOT_FOR_ADMINISTRATION',v)

    def test_12_bogus_device_increment(self):
        v=self.run_case(measurement_increment_ml='0.01')
        self.assertIn('DEVICE_INCREMENT_UNKNOWN_NO_ROUNDING',v['flags'])

    def test_13_units_and_theoretical_volume(self):
        v=self.run_case(weight_kg=5)
        self.assertEqual(Decimal(v['theoretical_mg_for_qa_only']),Decimal('0.05'))
        self.assertEqual(Decimal(v['theoretical_ml_for_qa_only']),Decimal('0.05'))

    def test_14_extreme_rounding_2point5kg(self):
        v=self.run_case(weight_kg=2.5)
        self.assertEqual(Decimal(v['qa_rounding_relative_error_percent']),Decimal('20.000'))
        self.assertFalse(v['prescription_enabled'])

    def test_15_four_kg_rounding_exact_but_measurement_not_validated(self):
        v=self.run_case(weight_kg=4)
        self.assertEqual(Decimal(v['qa_rounding_relative_error_percent']), 0)
        self.assertIn('MEASUREMENT_ACCURACY_AND_ROUNDING_POLICY_NOT_APPROVED',v['flags'])

    def test_16_iv_dilution_never_mapped_to_im(self):
        v=self.run_case(iv_dilution_selected=True)
        self.assertIn('IV_DILUTION_FORBIDDEN_IN_IM_CONTRACT',v['flags'])
        self.assertNotIn('theoretical_ml_for_qa_only',v)

    def test_17_missing_age_is_blocked(self):
        self.assertNotIn('theoretical_ml_for_qa_only',self.run_case(age_months=None))

    def test_18_negative_age_is_blocked(self):
        self.assertNotIn('theoretical_ml_for_qa_only',self.run_case(age_months=-0.1))

    def test_19_route_sc_rejected(self):
        self.assertNotIn('theoretical_ml_for_qa_only',self.run_case(route='SC'))

    def test_20_all_paths_prescription_disabled(self):
        for extra in ({},{'age_months':6},{'weight_kg':None},{'route':'IV'},
                      {'concentration_mg_ml':0.1},{'weight_kg':2.5}):
            with self.subTest(extra=extra):
                v=self.run_case(**extra)
                self.assertEqual(v['status'],'BLOCKED')
                self.assertFalse(v['prescription_enabled'])


if __name__ == '__main__':
    unittest.main()
