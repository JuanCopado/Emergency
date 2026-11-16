"""Synthetic QA for C05 source reconciliation; no clinical integration/approval."""
import sys
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from octaplex_pt_c05_preflight import (
    source_band_differences, review_input, PRESENTATIONS, PT_BANDS_ML_KG,
    FIX_IU_PER_ML, MAX_PT_SINGLE_DOSE_IU, CONTRACT_STATUS,
)


def case(**extra):
    p = dict(inr=3.1, presentation_iu=500, proposed_total_iu=2000,
             infusion_stage="initial", proposed_rate_ml_min=1,
             source_revision="2020-08", exact_product_verified=True,
             clinical_review_signed=True)
    p.update(extra)
    return review_input(**p)


class OctaplexC05NonPrescriptiveTests(unittest.TestCase):
    def test_01_source_concentration_two_presentations(self):
        self.assertEqual(Decimal("500")/PRESENTATIONS[500], FIX_IU_PER_ML)
        self.assertEqual(Decimal("1000")/PRESENTATIONS[1000], FIX_IU_PER_ML)

    def test_02_first_band_lower_rcm_is_22point5_not_25(self):
        self.assertEqual(PT_BANDS_ML_KG[0][2] * FIX_IU_PER_ML, Decimal("22.5"))
        self.assertIn({"band":1,"type":"LOWER_BOUND_DIFFERENCE",
                       "rcm_iu_kg":"22.5","owner_iu_kg":"25"},
                      source_band_differences())

    def test_03_fourth_band_has_no_rcm_per_kg_upper(self):
        self.assertIsNone(PT_BANDS_ML_KG[3][3])
        self.assertIn({"band":4,"type":"UPPER_BOUND_DIFFERENCE",
                       "rcm_iu_kg":None,"owner_iu_kg":"50"},
                      source_band_differences())

    def test_04_only_two_documented_source_conflicts(self):
        self.assertEqual(len(source_band_differences()),2)

    def test_05_exact_inr_boundaries_flagged(self):
        for value in [2.5,3,3.5]:
            with self.subTest(inr=value):
                self.assertIn("INR_BOUNDARY_RULE_REQUIRES_SIGNOFF",
                              case(inr=value)["flags"])

    def test_06_inr_under_two_not_general_table(self):
        self.assertIn("GENERAL_PT_2020_INR_TABLE_NOT_APPLICABLE",case(inr=1.8)["flags"])

    def test_07_missing_and_invalid_inr(self):
        for v in [None,0,-1,True,"3.2",float("nan"),float("inf")]:
            with self.subTest(inr=str(v)):
                self.assertIn("INR_MISSING_OR_INVALID",case(inr=v)["flags"])

    def test_08_both_presentations_accepted_as_candidates(self):
        for x in [500,1000]:
            self.assertNotIn("PRESENTATION_UNKNOWN_OR_INVALID",
                             case(presentation_iu=x)["flags"])

    def test_09_unlisted_or_boolean_presentation_rejected(self):
        for x in [250,2000,True,None]:
            self.assertIn("PRESENTATION_UNKNOWN_OR_INVALID",
                          case(presentation_iu=x)["flags"])

    def test_10_pt_single_dose_cap_strict(self):
        self.assertEqual(MAX_PT_SINGLE_DOSE_IU,Decimal("3000"))
        self.assertNotIn("EXCEEDS_PT_2020_SINGLE_DOSE_3000_IU",
                         case(proposed_total_iu=3000)["flags"])
        self.assertIn("EXCEEDS_PT_2020_SINGLE_DOSE_3000_IU",
                      case(proposed_total_iu=3000.1)["flags"])

    def test_11_initial_rate_one_milliliter_per_min(self):
        self.assertNotIn("INITIAL_RATE_MUST_BE_1_ML_MIN_PER_PT_2020",case()["flags"])
        self.assertIn("INITIAL_RATE_MUST_BE_1_ML_MIN_PER_PT_2020",
                      case(proposed_rate_ml_min=8)["flags"])

    def test_12_subsequent_rate_two_to_three(self):
        for speed in [2,2.5,3]:
            self.assertNotIn("POST_INITIAL_RATE_OUTSIDE_2_TO_3_ML_MIN",
                             case(infusion_stage="after_initial",proposed_rate_ml_min=speed)["flags"])
        for speed in [1,3.1,8]:
            self.assertIn("POST_INITIAL_RATE_OUTSIDE_2_TO_3_ML_MIN",
                          case(infusion_stage="after_initial",proposed_rate_ml_min=speed)["flags"])

    def test_13_complication_blocks_all_recommendations(self):
        x=case(infusion_stage="after_initial",proposed_rate_ml_min=2.5,complication=True)
        self.assertIn("COMPLICATION_REQUIRES_STOP_AND_HUMAN_REVIEW",x["flags"])
        self.assertFalse(x["prescription_enabled"])

    def test_14_source_version_divergence(self):
        x=case(source_revision="UK-2024")
        self.assertIn("SOURCE_REVISION_CHANGED_OR_UNKNOWN",x["flags"])

    def test_15_missing_signoffs_never_releases(self):
        x=case(exact_product_verified=False,clinical_review_signed=False)
        self.assertIn("PORTUGUESE_PRODUCT_AND_STOCK_VERIFICATION_REQUIRED",x["flags"])
        self.assertIn("CLINICAL_SOURCE_SELECTION_AND_LOCAL_RANGES_NOT_SIGNED",x["flags"])

    def test_16_critical_concentration_difference_always_flagged(self):
        self.assertIn("OWNER_BANDS_DIFFER_FROM_PT_2020_RCM",case()["flags"])

    def test_17_all_paths_remain_blocked_without_orders(self):
        for kw in [{},{"inr":2.5},{"proposed_total_iu":4000},
                   {"presentation_iu":1000},{"proposed_rate_ml_min":8},
                   {"source_revision":"UK-2024"}]:
            with self.subTest(kw=kw):
                x=case(**kw)
                self.assertEqual(x["status"],CONTRACT_STATUS)
                self.assertFalse(x["prescription_enabled"])
                self.assertNotIn("dose_iu",x)
                self.assertNotIn("pump_ml_h",x)


if __name__ == "__main__":
    unittest.main()
