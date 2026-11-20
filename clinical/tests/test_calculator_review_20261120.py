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
