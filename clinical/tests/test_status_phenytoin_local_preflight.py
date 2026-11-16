"""Synthetic boundary tests for non-prescriptive phenytoin preflight."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from status_phenytoin_local_preflight import (
    preflight, galway_minimum_nacl09_volume_ml, ALWAYS_BLOCKED
)


def case(weight=70, rate=50, bag=250, **extra):
    inputs = dict(
        weight_kg=weight, max_rate_mg_min=rate, bag_ml=bag,
        risk_review_confirmed=True, monitoring_ready=True,
        iv_access_ready=True, pharmacy_formulary_approved=True,
        pharmacy_signed_approval_ref="SYNTHETIC_TEST_ONLY",
    )
    inputs.update(extra)
    return preflight(**inputs)


class PhenytoinGalwayPreflightTests(unittest.TestCase):
    def test_weight_dose_20mgkg_and_initial_cap_2000mg(self):
        for kg, expected in [(40,800),(50,1000),(60,1200),(70,1400),(90,1800),(100,2000),(110,2000)]:
            with self.subTest(kg=kg):
                x = case(weight=kg, bag=100 if kg <= 50 else 250)
                self.assertEqual(x["dose_mg_for_review_only"], expected)

    def test_protocol_bag_brackets_exact_boundaries(self):
        for mg, expected in [(499.99,50),(500,100),(1000,100),(1000.01,250),(2000,250)]:
            with self.subTest(mg=mg):
                self.assertEqual(galway_minimum_nacl09_volume_ml(mg),expected)

    def test_reject_bag_below_recommended_even_when_nominal_concentration_is_ok(self):
        x = case(weight=25, bag=50)
        self.assertIn("NACL09_VOLUME_BELOW_GALWAY_MINIMUM", x["reasons"])
        self.assertNotIn("NOMINAL_CONCENTRATION_EXCEEDS_10_MG_ML",x["reasons"])

    def test_reject_too_little_bag_and_excess_concentration(self):
        x = case(weight=70,bag=100)
        self.assertIn("NACL09_VOLUME_BELOW_GALWAY_MINIMUM",x["reasons"])
        self.assertIn("NOMINAL_CONCENTRATION_EXCEEDS_10_MG_ML",x["reasons"])

    def test_reject_bags_above_table_pending_separate_pharmacy_approval(self):
        self.assertIn("NACL09_VOLUME_ABOVE_GALWAY_TABLE_REQUIRES_SEPARATE_VALIDATION",
                      case(bag=500)["reasons"])

    def test_galway_exact_bag_is_only_review_candidate(self):
        x=case()
        self.assertEqual(x["status"],"CANDIDATE_FOR_NOMINAL_REVIEW_ONLY")
        self.assertEqual(x["galway_minimum_nacl09_bag_ml"],250)
        self.assertFalse(x["prescription_enabled"])

    def test_slow_rate_is_recorded_and_excess_time_is_blocked(self):
        x=case(weight=90,rate=25)
        self.assertEqual(x["minimum_duration_min_for_review_only"],72)
        self.assertIn("PREPARATION_60_MIN_WINDOW_NOT_SATISFIED",x["reasons"])

    def test_at_60_minutes_also_fails_conservatively(self):
        x=case(weight=75,rate=25)
        self.assertEqual(x["minimum_duration_min_for_review_only"],60)
        self.assertIn("PREPARATION_60_MIN_WINDOW_NOT_SATISFIED",x["reasons"])

    def test_elapsed_since_mixing_affects_stability_window(self):
        self.assertIn("PREPARATION_60_MIN_WINDOW_NOT_SATISFIED",
                      case(time_since_preparation_min=21)["reasons"])

    def test_diluent_not_nacl09_is_blocked(self):
        self.assertIn("DILUENT_MUST_BE_NACL_0_9",case(diluent="glucose 5%")["reasons"])

    def test_unsupported_product_is_blocked(self):
        self.assertIn("PRODUCT_OUTSIDE_DOCUMENTED_GALWAY_SCOPE",
                      case(product_strength="100mg/2mL")["reasons"])

    def test_children_blocked(self):
        self.assertEqual(case(age_class="pediatric")["status"],"BLOCKED")

    def test_bad_numbers_are_blocked_and_no_dose_returned(self):
        for bad in [0,-2,True,float("inf"),float("nan"),"70"]:
            with self.subTest(bad=str(bad)):
                x=case(weight=bad)
                self.assertEqual(x["status"],"BLOCKED")
                self.assertNotIn("dose_mg_for_review_only",x)

    def test_invalid_bag_is_blocked_and_no_dose_returned(self):
        for bad in [None,0,-5,True,float("nan"),"250"]:
            with self.subTest(bad=str(bad)):
                x=case(bag=bad)
                self.assertIn("INVALID_BAG_VOLUME",x["reasons"])
                self.assertNotIn("dose_mg_for_review_only",x)

    def test_missing_pharmacy_approval_blocks_even_if_nominal_parameters_match(self):
        self.assertIn("PHARMACY_PRODUCT_AND_PREPARATION_ATTESTATION_REQUIRED",
                      case(pharmacy_signed_approval_ref="")["reasons"])

    def test_clinical_contraindication_blocks(self):
        self.assertIn("CLINICAL_CONTRAINDICATION",
                      case(contraindication_present=True)["reasons"])

    def test_monitoring_and_risk_review_required(self):
        self.assertEqual(case(risk_review_confirmed=False,monitoring_ready=False)["status"],"BLOCKED")

    def test_precipitate_blocks(self):
        self.assertIn("PRECIPITATE_OR_UNCONFIRMED_CLARITY",
                      case(visible_precipitate=True)["reasons"])

    def test_no_prescription_or_pump_fields_any_path(self):
        self.assertTrue(ALWAYS_BLOCKED)
        for x in [case(),case(bag=100),case(rate=25),case(weight="bad")]:
            self.assertFalse(x["prescription_enabled"])
            self.assertNotIn("pump_ml_h",x)
            self.assertNotIn("withdrawal_ml",x)


if __name__ == "__main__":
    unittest.main()
