import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import pediatric_outpatient_calculator as calc


class PediatricDropDoseTest(unittest.TestCase):
    def patient(self):
        return {
            "age_months": 60,
            "actual_weight_kg": 10,
            "ideal_weight_kg": 10,
            "home_analgesia_antipyresis_appropriate": True,
        }

    def test_exact_product_verified_drop_factor_outputs_drops(self):
        product = {
            "form": "oral_drops",
            "concentration_mg_per_ml": 24,
            "external_drop_factor_verified": True,
            "exact_product_name": "Test exact 24 mg/mL oral drops",
            "drop_factor_source_url": "https://example.test/smpc",
            "drops_per_ml": 20,
        }
        result = calc.calculate(
            "paracetamol-pain-fever-home",
            self.patient(),
            product=product,
            selected_duration_days=1,
        )
        self.assertIn("volume_per_dose", result)
        self.assertIn("drops_per_dose", result)
        self.assertEqual(125, result["drops_per_dose"]["rounded_whole_drops"])
        self.assertAlmostEqual(6.25, result["volume_per_dose"]["exact_ml"])
        self.assertAlmostEqual(1.2, result["drops_per_dose"]["mg_per_drop"])

    def test_drop_form_without_verified_factor_is_fail_closed(self):
        product = {
            "form": "oral_drops",
            "concentration_mg_per_ml": 24,
        }
        result = calc.calculate(
            "paracetamol-pain-fever-home",
            self.patient(),
            product=product,
            selected_duration_days=1,
        )
        self.assertNotIn("drops_per_dose", result)
        self.assertEqual(
            "verified_exact_product_drop_factor_required",
            result["drops_status"],
        )

    def test_external_drop_factor_requires_exact_identity_and_source(self):
        product = {
            "form": "oral_drops",
            "concentration_mg_per_ml": 24,
            "external_drop_factor_verified": True,
            "drops_per_ml": 20,
        }
        with self.assertRaises(ValueError):
            calc.calculate(
                "paracetamol-pain-fever-home",
                self.patient(),
                product=product,
                selected_duration_days=1,
            )


if __name__ == "__main__":
    unittest.main()
