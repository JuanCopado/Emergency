"""Technical regression cases for total-dose labels and independent dose/infusion inputs."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'clinical/scripts'))
from pediatric_bolus_calculator import calculate as bolus, load_registry as bolus_registry
from pediatric_antibiotic_calculator import calculate as antibiotic, load_registry as antibiotic_registry
from infusion_calculator import infusion_ml_h, fixed_dose_ml_h, weight_per_hour_ml_h
from clinical_calculator import calculate as central

BAD = [float('nan'), float('inf'), float('-inf'), True, False, '2', None, {}, [], -1, 10**400]


class PediatricTotalDoseUnits(unittest.TestCase):
    def test_bolus_total_units_keep_daily_and_component_dimensions(self):
        expected = {'mg/kg': 'mg', 'micrograms/kg': 'micrograms', 'mL/kg': 'mL',
                    'g/kg': 'g', 'units/kg': 'units', 'mmol/kg': 'mmol', 'mg/kg/day': 'mg/day'}
        for rid, row in bolus_registry().items():
            if 'dose_per_kg' not in row and 'dose_per_kg_min' not in row:
                continue
            with self.subTest(regimen=rid):
                result = bolus(rid, 20)
                self.assertEqual(result['dose_unit'], expected[row['dose_unit']])
                self.assertEqual(result['dose_per_kg_unit'], row['dose_unit'])

    def test_antibiotic_total_units_preserve_component_specificity(self):
        for rid, row in antibiotic_registry().items():
            if rid == 'sepsis-community-ceftriaxone' or row.get('dose_automation') is False:
                continue
            if 'dose_per_kg' not in row and 'dose_per_kg_min' not in row:
                continue
            with self.subTest(regimen=rid):
                result = antibiotic(rid, 20)
                expected = 'mg piperacillin component' if row['dose_unit'] == 'mg/kg piperacillin component' else 'mg'
                self.assertEqual(result['dose_unit'], expected)
                self.assertEqual(result['dose_per_kg_unit'], row['dose_unit'])

    def test_bolus_amount_range_cap_fixed_dose_and_volume_are_preserved(self):
        capped = bolus('anaphylaxis-epinephrine-im', 80)
        self.assertEqual((capped['dose'], capped['dose_unit'], capped['volume_ml']), (.5, 'mg', .5))
        fluid = bolus('hypoglycemia-dextrose10', 20)
        self.assertEqual((fluid['dose'], fluid['dose_unit'], fluid['volume_ml']), (4, 'g', 40))
        self.assertEqual(bolus('rsi-ketamine', 20)['dose_range'], [20, 40])
        self.assertEqual(bolus('acute-asthma-ipratropium', 18)['dose_unit'], 'micrograms nebulized')

    def test_cli_json_exposes_total_and_reference_units_separately(self):
        result = subprocess.run([sys.executable, str(ROOT/'clinical/scripts/pediatric_bolus_calculator.py'),
                                 'anaphylaxis-epinephrine-im', '20'], capture_output=True, text=True, check=True)
        row = json.loads(result.stdout)
        self.assertEqual(row['dose_unit'], 'mg')
        self.assertEqual(row['dose_per_kg_unit'], 'mg/kg')


class IndependentInfusionGuards(unittest.TestCase):
    def test_infusion_rejects_invalid_numbers_before_arithmetic(self):
        for position in range(4):
            for bad in BAD + ([0] if position != 2 else []):
                args = [8, 100, .1, 80]
                args[position] = bad
                with self.subTest(position=position, bad=str(bad)), self.assertRaises(ValueError):
                    infusion_ml_h(*args)

    def test_fixed_and_weighted_hourly_reject_each_invalid_input(self):
        for function, good, positive_positions in [(fixed_dose_ml_h, [1, 2], {1}),
                                                   (weight_per_hour_ml_h, [1, 20, 2], {1, 2})]:
            for position in range(len(good)):
                for bad in BAD + ([0] if position in positive_positions else []):
                    args = good.copy(); args[position] = bad
                    with self.subTest(function=function.__name__, position=position, bad=str(bad)), self.assertRaises(ValueError):
                        function(*args)

    def test_central_dose_and_infusion_paths_reject_each_invalid_numeric_field(self):
        cases = [('mgkg-dose', {'mg_per_kg': 10, 'weight_kg': 20}, {'weight_kg'}),
                 ('final-concentration', {'drug_amount': 10, 'final_volume_mL': 20}, {'final_volume_mL'}),
                 ('mcgkgmin-to-mlh', {'dose_mcg_kg_min': .1, 'weight_kg': 20, 'concentration_mcg_mL': 10}, {'weight_kg','concentration_mcg_mL'}),
                 ('mgkgh-to-mlh', {'dose_mg_kg_h': 1, 'weight_kg': 20, 'concentration_mg_mL': 10}, {'weight_kg','concentration_mg_mL'}),
                 ('unitskgh-to-mlh', {'dose_units_kg_h': 1, 'weight_kg': 20, 'concentration_units_mL': 10}, {'weight_kg','concentration_units_mL'})]
        for fid, good, positive_fields in cases:
            for key in good:
                for bad in BAD + ([0] if key in positive_fields else []):
                    with self.subTest(formula=fid, key=key, bad=str(bad)), self.assertRaises(ValueError):
                        central(fid, {**good, key: bad})

    def test_finite_inputs_cannot_overflow_or_cancel_two_negatives(self):
        cases = [lambda: infusion_ml_h(1e308, 100, .1, 80),
                 lambda: fixed_dose_ml_h(1e308, 1e-308),
                 lambda: weight_per_hour_ml_h(1e308, 80, 1),
                 lambda: weight_per_hour_ml_h(-1, -20, 1),
                 lambda: central('mgkg-dose', {'mg_per_kg':1e308, 'weight_kg':20}),
                 lambda: central('final-concentration', {'drug_amount':1e308, 'final_volume_mL':1e-308}),
                 lambda: central('mcgkgmin-to-mlh', {'dose_mcg_kg_min':1e308,'weight_kg':20,'concentration_mcg_mL':1})]
        for index, call in enumerate(cases):
            with self.subTest(index=index), self.assertRaises(ValueError): call()

    def test_existing_valid_arithmetic_and_zero_selected_dose_are_preserved(self):
        self.assertAlmostEqual(infusion_ml_h(8,100,.1,80)['ml_h'], 6)
        self.assertEqual(fixed_dose_ml_h(0,1), 0)
        self.assertEqual(weight_per_hour_ml_h(0,20,1), 0)
        self.assertEqual(infusion_ml_h(8,100,0,80)['ml_h'], 0)
        self.assertEqual(central('mgkg-dose', {'mg_per_kg':10,'weight_kg':20}), (200,'mg'))
        self.assertEqual(central('mgkgh-to-mlh', {'dose_mg_kg_h':1,'weight_kg':20,'concentration_mg_mL':10}), (2,'mL/h'))
