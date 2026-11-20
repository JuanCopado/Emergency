"""Boundaries identified during the independent clinical calculator review."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from clinical_calculator import calculate, calculate_scale


class CalculatorReviewTests(unittest.TestCase):
    def test_all_registered_formulas_against_reference_examples(self):
        root = Path(__file__).resolve().parents[1]
        cases = json.loads((root / "qa/CALCULATOR_REFERENCE_CASES_20261120.json").read_text(encoding="utf8"))
        registry = json.loads((root / "calculators/registry.json").read_text(encoding="utf8"))
        self.assertCountEqual([r["id"] for r in cases], [r["id"] for r in registry["formulas"]])
        for case in cases:
            with self.subTest(formula=case["id"]):
                value, unit = calculate(case["id"], case["inputs"])
                self.assertAlmostEqual(value, case["expected"], places=5)
                self.assertEqual(unit, case["unit"])

    def test_legacy_meld_sodium_threshold_and_alias(self):
        case = dict(bilirubin_mg_dL=1, creatinine_mg_dL=1, sodium_mmol_L=125,
                    legacy_meld_na_acknowledged=True)
        for inr, expected in [(1, 6), (1.5, 11), (1.65, 23)]:
            with self.subTest(inr=inr):
                self.assertEqual(calculate_scale("meld-na", dict(case, INR=inr))["value"], expected)

    def test_invalid_inputs_rejected(self):
        for fid, data in [
            ("bedside-schwartz", dict(height_cm=-120, Scr_mg_dL=1)),
            ("minute-ventilation", dict(VT_L=-0.5, RR=16)),
            ("rox", dict(SpO2_percent=970, FiO2_fraction=.5, RR=20)),
            ("cao2", dict(Hb=12, SaO2_fraction=98, PaO2=90)),
            ("parkland", dict(weight_kg=60, TBSA_percent=101)),
            ("ckd-epi-2021", dict(age=float("nan"), Scr_mg_dL=1, sex="male")),
            ("bedside-schwartz", dict(height_cm=True, Scr_mg_dL=1)),
            ("minute-ventilation", dict(VT_L=1e300, RR=1e300)),
        ]:
            with self.subTest(fid=fid), self.assertRaises(ValueError):
                calculate(fid, data)

    def test_valid_boundaries(self):
        self.assertAlmostEqual(calculate("bedside-schwartz", dict(height_cm=120, Scr_mg_dL=1))[0], 49.56)
        self.assertEqual(calculate_scale("rox-index", dict(SpO2_percent=100, FiO2_fraction=.5, RR=20))["value"], 10)

    def test_apache2_bands(self):
        from specialist_scores_block3 import _apache_na, _apache_wbc
        for concentration, points in [(149,0),(150,1),(154,1),(155,2),(159,2),(160,3)]:
            self.assertEqual(_apache_na(concentration), points)
        for count, points in [(14.9,0),(15,1),(19.9,1),(20,2),(39.9,2),(40,4)]:
            self.assertEqual(_apache_wbc(count), points)

    def test_pediatric_motor_response_is_age_specific(self):
        case = dict(age_years=3, eye=4, verbal=5, motor="withdraws_to_touch")
        self.assertEqual(calculate_scale("pediatric-gcs",case)["components"]["M"],5)
        with self.assertRaises(ValueError):
            calculate_scale("pediatric-gcs",dict(case,age_years=4))

    def test_delayed_absorption_does_not_hide_an_above_line_result(self):
        case = dict(single_acute_ingestion_known_time=True, hours_since_ingestion=4,
                    acetaminophen_mcg_mL=151, extended_release_or_delayed_absorption=True)
        self.assertEqual(calculate_scale("rumack-matthew",case)["interpretation"],"at_or_above_150_treatment_line")
        self.assertEqual(calculate_scale("rumack-matthew",dict(case,acetaminophen_mcg_mL=50))["status"],"delayed_absorption_protocol_review")

    def test_edacs_risk_factor_age_boundary(self):
        case = dict(sex="female",known_cad_or_age18_50_ge3_risk_factors=True,
                    diaphoresis=False,radiation=False,pleuritic=False,palpation_reproduces=False)
        for age, points in [(50,4),(51,0)]:
            with self.subTest(age=age):
                self.assertEqual(calculate_scale("edacs",dict(case,age=age))["components"]["cad_or_risk_factors"],points)

    def test_every_scale_through_registry_dispatch(self):
        root = Path(__file__).resolve().parents[1]
        cases = json.loads((root / "qa/SCALE_DISPATCH_CASES_20261120.json").read_text(encoding="utf8"))
        registry = json.loads((root / "calculators/registry.json").read_text(encoding="utf8"))
        self.assertCountEqual([r["id"] for r in cases], [r["id"] for r in registry["scales"]])
        for case in cases:
            with self.subTest(scale=case["id"]):
                result = calculate_scale(case["id"], case["input"], registry)
                self.assertEqual(result["registry_id"], case["id"])
                self.assertEqual(result["status"], case["status"])
