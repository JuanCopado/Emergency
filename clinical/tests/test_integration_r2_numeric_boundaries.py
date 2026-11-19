"""R2: positive arithmetic may not silently become a zero dose or pump rate."""
import ast
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from infusion_calculator import infusion_ml_h, fixed_dose_ml_h, weight_per_hour_ml_h
from clinical_calculator import calculate
from pediatric_bolus_calculator import calculate_with_selected_concentration


class NumericBoundaries(unittest.TestCase):
    def infusion_cli(self, raw_dose):
        return subprocess.run([
            sys.executable, '-B', str(Path(__file__).resolve().parents[1] / 'scripts/infusion_calculator.py'),
            '--drug-mg=8', '--volume-ml=100', f'--dose-mcg-kg-min={raw_dose}', '--weight-kg=80',
        ], text=True, capture_output=True)

    def test_real_cli_rejects_nonzero_mantissas_lost_to_underflow(self):
        for raw in ['1e-4000', '+1e-4000', '-1e-4000', '0.' + '0' * 400 + '1']:
            with self.subTest(raw=raw):
                result = self.infusion_cli(raw)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, '')
                self.assertIn('underflow', result.stderr.lower())

    def test_real_cli_preserves_explicit_zero_and_representable_doses(self):
        for raw, rate in [('0', 0), ('0e-4000', 0), ('+0e-4000', 0), ('-0e-4000', 0),
                          ('0.000e-4000', 0), ('0.1', 6), ('1e-1', 6), ('+0.1', 6), (' 0.1 ', 6)]:
            with self.subTest(raw=raw):
                result = self.infusion_cli(raw)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(ast.literal_eval(result.stdout)['ml_h'], rate)

    def test_real_cli_rejects_other_invalid_dose_inputs(self):
        for raw in ['-0.1', 'NaN', 'Infinity', '1e309', '0,1', 'true', '1 000', '1_000']:
            with self.subTest(raw=raw):
                result = self.infusion_cli(raw)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, '')

    def test_underflow_and_nonfinite_intermediate_are_rejected(self):
        calls = [
            lambda: infusion_ml_h(8, 100, 5e-324, .01),
            lambda: infusion_ml_h(1e308, 100, 0, 80),
            lambda: fixed_dose_ml_h(5e-324, 2),
            lambda: weight_per_hour_ml_h(5e-324, .01, 1),
            lambda: calculate('mgkg-dose', {'mg_per_kg': 5e-324, 'weight_kg': .01}),
            lambda: calculate('final-concentration', {'drug_amount': 5e-324, 'final_volume_mL': 2}),
            lambda: calculate('mcgkgmin-to-mlh', {'dose_mcg_kg_min': 5e-324, 'weight_kg': .01, 'concentration_mcg_mL': 1}),
            lambda: calculate('mgkgh-to-mlh', {'dose_mg_kg_h': 5e-324, 'weight_kg': .01, 'concentration_mg_mL': 1}),
            lambda: calculate('unitskgh-to-mlh', {'dose_units_kg_h': 5e-324, 'weight_kg': .01, 'concentration_units_mL': 1}),
        ]
        for index, call in enumerate(calls):
            with self.subTest(index=index), self.assertRaises(ValueError):
                call()

    def test_explicit_zero_remains_valid(self):
        self.assertEqual(fixed_dose_ml_h(0, 2), 0)
        self.assertEqual(weight_per_hour_ml_h(0, 20, 2), 0)
        self.assertEqual(infusion_ml_h(8, 100, 0, 80)['ml_h'], 0)
        self.assertEqual(calculate('mgkg-dose', {'mg_per_kg': 0, 'weight_kg': 20}), (0, 'mg'))

    def test_selected_product_volume_cannot_underflow_to_zero(self):
        with self.assertRaises(ValueError):
            calculate_with_selected_concentration('anaphylaxis-epinephrine-im', 1e-300, 1e308)
