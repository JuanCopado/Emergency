"""Synthetic boundary tests; explicitly NOT clinical validation."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from status_phenytoin_local_preflight import preflight, ALWAYS_BLOCKED


def case(weight=70, rate=50, bag=250, **kwargs):
    return preflight(weight_kg=weight, max_rate_mg_min=rate, bag_ml=bag,
                     risk_review_confirmed=True, monitoring_ready=True,
                     iv_access_ready=True, pharmacy_formulary_approved=True,
                     pharmacy_signed_approval_ref="SYNTHETIC_TEST_ONLY", **kwargs)


class PhenytoinPreflightBoundaryTests(unittest.TestCase):
    def test_rejects_unlock_for_any_input(self):
        self.assertTrue(ALWAYS_BLOCKED)
        for weight in [40, 50, 70, 75, 80, 100, 110]:
            self.assertFalse(case(weight=weight, bag=100 if weight <= 50 else 250)['prescription_enabled'])

    def test_supported_70kg_load_and_duration_are_only_advisory(self):
        x = case()
        self.assertEqual(x['dose_mg_for_review_only'], 1400)
        self.assertEqual(x['minimum_duration_min_for_review_only'], 40)
        self.assertEqual(x['status'], 'CANDIDATE_FOR_NOMINAL_REVIEW_ONLY')

    def test_dose_capped_at_2000mg(self):
        x = case(weight=110)
        self.assertEqual(x['dose_mg_for_review_only'], 2000)
        self.assertEqual(x['minimum_duration_min_for_review_only'], 40)

    def test_bag_table_boundaries(self):
        for weight, bag in [(20, 50), (25, 100), (50, 100), (50.01, 250)]:
            with self.subTest(weight=weight):
                x = case(weight=weight, bag=bag)
                self.assertNotIn('DILUENT_BAG_NOT_IN_SELECTED_PROTOCOL_TABLE', x['reasons'])
        self.assertIn('DILUENT_BAG_NOT_IN_SELECTED_PROTOCOL_TABLE', case(bag=500)['reasons'])

    def test_rate_reduction_cannot_overrun_mixture_window(self):
        x = case(weight=90, rate=25)
        self.assertEqual(x['minimum_duration_min_for_review_only'], 72)
        self.assertIn('PREPARATION_60_MIN_WINDOW_NOT_SATISFIED', x['reasons'])

    def test_boundary_at_60_minutes_is_fail_closed(self):
        x = case(weight=75, rate=25)
        self.assertEqual(x['minimum_duration_min_for_review_only'], 60)
        self.assertIn('PREPARATION_60_MIN_WINDOW_NOT_SATISFIED', x['reasons'])

    def test_mix_to_start_delay_matters(self):
        x = case(time_since_preparation_min=21)
        self.assertIn('PREPARATION_60_MIN_WINDOW_NOT_SATISFIED', x['reasons'])

    def test_unsupported_formulation_or_age(self):
        x = case(product_strength='100mg/2mL')
        self.assertIn('PRODUCT_OUTSIDE_DOCUMENTED_GALWAY_SCOPE', x['reasons'])
        x = case(age_class='pediatric')
        self.assertIn('ADULT_ONLY', x['reasons'])

    def test_strict_invalid_numbers(self):
        for x in [0, -5, True, float('nan'), float('inf'), '70']:
            with self.subTest(x=x):
                r = case(weight=x)
                self.assertEqual(r['status'], 'BLOCKED')
                self.assertNotIn('dose_mg_for_review_only', r)

    def test_unverified_pharmacy_or_clinical_controls_block(self):
        x=preflight(weight_kg=70,max_rate_mg_min=50,bag_ml=250)
        self.assertEqual(x['status'],'BLOCKED')
        self.assertIn('PHARMACY_PRODUCT_AND_PREPARATION_ATTESTATION_REQUIRED',x['reasons'])
        x=case(contraindication_present=True)
        self.assertEqual(x['status'],'BLOCKED')
        self.assertIn('CLINICAL_CONTRAINDICATION',x['reasons'])

    def test_boolean_guards_are_strict(self):
        x=preflight(weight_kg=70,max_rate_mg_min=50,bag_ml=250,
                    risk_review_confirmed="yes",monitoring_ready="yes",
                    iv_access_ready=1, pharmacy_formulary_approved="yes",
                    pharmacy_signed_approval_ref="SYNTHETIC",
                    contraindication_present=0)
        self.assertEqual(x["status"], "BLOCKED")
        self.assertGreaterEqual(len(x["reasons"]), 4)

    def test_no_rate_or_pump_calculation_in_output(self):
        s = case()
        self.assertNotIn('pump_ml_h',s)
        self.assertNotIn('withdrawal_ml',s)


if __name__ == '__main__':
    unittest.main()
