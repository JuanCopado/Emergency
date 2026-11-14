"""Local concentration/clock decisions stay distinct from manufacturer evidence."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from infusion_calculator import fixed_dose_ml_h


class OwnerEmpressinHandlingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads((ROOT / 'qa/LOCAL_INFUSION_DECISIONS_2026-11-14.json').read_text())

    def test_selected_syringe_is_40ml_final_not_topped_up_to_50(self):
        prep = self.record['selected_empressin_preparation']
        self.assertEqual(prep['stock_volume_ml'] * 20, prep['drug_amount_IU'])
        self.assertEqual(prep['stock_volume_ml'] + prep['diluent_volume_ml'], 40)
        self.assertEqual(prep['final_volume_ml'], 40)
        self.assertEqual(prep['drug_amount_IU'] / prep['final_volume_ml'], 1)

    def test_table_converts_units_minute_to_hour_without_weight(self):
        prep = self.record['selected_empressin_preparation']
        expected = [(0.01, 0.6), (0.02, 1.2), (0.03, 1.8)]
        self.assertEqual(len(prep['pump_table']), len(expected))
        for row, (dose, rate) in zip(prep['pump_table'], expected):
            self.assertEqual(row['dose_IU_min'], dose)
            self.assertAlmostEqual(row['rate_ml_h'], rate)
            self.assertAlmostEqual(fixed_dose_ml_h(dose * 60, 1), rate)
        self.assertEqual(prep['routine_label_dose_upper_IU_min'], 0.03)
        self.assertFalse(prep['automated_patient_prescription'])

    def test_08_reference_and_one_unit_table_cannot_be_swapped(self):
        self.assertAlmostEqual(fixed_dose_ml_h(0.03 * 60, 0.8), 2.25)
        self.assertAlmostEqual(fixed_dose_ml_h(0.03 * 60, 1), 1.8)
        #Using2.25mL/h with1IU/mL delivers0.0375IU/min, not0.03.
        self.assertAlmostEqual(2.25 / 60, 0.0375)

    def test_local_24h_ceiling_does_not_certify_stability_or_delayed_storage(self):
        policy = self.record['local_replacement_policy']
        self.assertTrue(policy['start_immediately_after_opening_reconstitution_dilution'])
        self.assertEqual(policy['max_container_and_tubing_hours'], 24)
        self.assertFalse(policy['delayed_storage_authorized'])
        self.assertFalse(policy['manufacturer_chemical_stability_certified_by_this_policy'])
        self.assertIn('not reset on transfer or connection', policy['clock_start'])
        self.assertIn('shorter limit', policy['replace_earlier_if'])

    def test_lipuro_clocks_depend_on_dilution_not_syringe_transfer(self):
        policy = self.record['propofol_lipuro_policy']
        self.assertEqual(policy['undiluted']['max_container_and_tubing_hours'], 12)
        self.assertIn('First opening/puncture', policy['undiluted']['clock_start'])
        self.assertTrue(policy['undiluted']['aseptic_immediate_extraction_and_administration_required'])
        self.assertEqual(policy['diluted_1percent']['max_hours_from_dilution'], 6)
        self.assertEqual(policy['diluted_1percent']['max_diluent_parts'], 4)
        self.assertEqual(policy['diluted_1percent']['minimum_concentration_mg_ml'], 2)
        self.assertFalse(policy['prepared_syringe_for_deferred_storage']['authorized'])
        self.assertFalse(policy['two_percent_dilution_allowed'])


if __name__ == '__main__':
    unittest.main()
