"""Pediatric safety contracts: fixtures, finite arithmetic and API integration."""
import math
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import pediatric_emergency_calculator as emergency
import pediatric_fluid_calculator as fluids
import pediatric_dka_calculator as dka
import pediatric_burn_calculator as burns
import pediatric_blood_product_calculator as blood
import pediatric_hypertension_calculator as hypertension
import pediatric_respiratory_support as respiratory
import pediatric_bolus_calculator as bolus
import pediatric_antibiotic_calculator as antibiotics
import pediatric_pump_table as pumps
from pediatric_outpatient_calculator import calculate, load_registry, MedicationSafetyStop
from pediatric_outpatient_alert_engine import evaluate
from run_pediatric_outpatient_regressions import run
from pediatric_catalog import build_catalog, serialize_catalog, ROOT
from pediatric_outpatient_api import calculate_request

BAD = [float('inf'), float('-inf'), float('nan'), True, '20', None, {}, []]


class PediatricSafetyCases(unittest.TestCase):
    def test_device_frequency_preserves_source_band(self):
        for regimen_id, age, daily in (
            ('fluticasone-controller-preschool', 24, 2),
            ('ciclesonide-controller-6to11-step2', 84, 1),
            ('fluticasone-controller-6to11-step2', 84, 2),
            ('budesonide-formoterol-controller-6to11-step3-rch', 84, 2),
            ('mometasone-nasal-allergic-rhinitis', 48, 1),
            ('fluticasone-propionate-nasal-allergic-rhinitis', 60, 1),
            ('azelastine-fluticasone-nasal-ge12', 156, 2),
            ('budesonide-formoterol-air-mart-6to11-gina2026', 84, None),
        ):
            with self.subTest(regimen_id=regimen_id):
                result = calculate(regimen_id, {
                    'age_months': age, 'actual_weight_kg': 20,
                    'allergies': [], 'active_medications': [],
                    'known_renal_impairment': False,
                    'known_hepatic_impairment': False,
                })
                self.assertEqual(result['device'].get('doses_per_day'), daily)
                self.assertEqual(result['doses_per_day'], daily)

    def test_bank_all_eighteen_expectations(self):
        self.assertEqual(run(), {'cases': 18, 'passed': 18, 'errors': []})

    def test_three_required_clinical_gates_remain_fail_closed(self):
        cases = [('paracetamol-pain-fever-home', 'home_analgesia_antipyresis_appropriate'),
                 ('dexamethasone-croup-mild-moderate', 'croup_discharge_criteria_met'),
                 ('rizatriptan-migraine-rch', 'secondary_headache_red_flags_excluded')]
        for regimen, field in cases:
            for value in (None, False):
                with self.subTest(regimen=regimen, value=value), self.assertRaises(MedicationSafetyStop):
                    calculate(regimen, {'age_months': 120, 'actual_weight_kg': 35,
                                       'ideal_weight_kg': 35, field: value}, selected_duration_days=2)

    def test_rizatriptan_boundary_and_interactions_preserved(self):
        patient = {'age_months': 120, 'actual_weight_kg': 40, 'secondary_headache_red_flags_excluded': True}
        with self.assertRaisesRegex(ValueError, 'no matching'):
            calculate('rizatriptan-migraine-rch', patient)
        for weight, dose in ((35, 5), (41, 10)):
            self.assertEqual(calculate('rizatriptan-migraine-rch', {**patient, 'actual_weight_kg': weight})['dose_mg'], dose)
        self.assertTrue(evaluate('rizatriptan-migraine-rch', patient, ['sumatriptan'])['blocked'])
        self.assertEqual(evaluate('rizatriptan-migraine-rch', patient, ['propranolol'])['prescription_status'], 'REVIEW_REQUIRED')


class PediatricFiniteNumbers(unittest.TestCase):
    def test_emergency_rejects_bad_divisors_and_weights(self):
        for value in BAD + [0, -1]:
            for args in ((0.1, 20, value), (0.1, value, 10)):
                with self.subTest(args=args), self.assertRaises(ValueError):
                    emergency.infusion_per_kg_min_ml_h(*args)

    def test_adjacent_calculators_reject_same_numeric_defect(self):
        calls = [fluids.maintenance_ml_day, blood.trauma_rbc_ml, respiratory.hfno_flow_l_min,
                 lambda v: burns.burn_plan(v, 10), lambda v: dka.insulin_ml_h(20, 0.1, v),
                 lambda v: hypertension.labetalol_ml_h(20, 1, v),
                 lambda v: bolus.calculate(next(iter(bolus.load_registry())), v),
                 lambda v: antibiotics.calculate(next(iter(antibiotics.load_registry())), v),
                 lambda v: pumps.pump_table(next(iter(pumps.load_registry())), v)]
        for i, call in enumerate(calls):
            for value in BAD + [0, -1]:
                with self.subTest(calculator=i, value=value), self.assertRaises(ValueError):
                    call(value)

    def test_age_time_and_divisors_reject_invalid_values(self):
        for value in BAD + [-1]:
            for call in (lambda: respiratory.ventilation_rate_reference(value), lambda: burns.burn_plan(20, 10, value)):
                with self.subTest(value=value), self.assertRaises(ValueError):
                    call()
        for value in BAD + [0, -1]:
            for call in (lambda: fluids.shock_bolus(20, minutes=value), lambda: fluids.ors_rehydration(20, hours=value),
                         lambda: dka.corrected_sodium(value, 20)):
                with self.subTest(value=value), self.assertRaises(ValueError):
                    call()

    def test_finite_inputs_cannot_overflow_to_nonfinite_outputs_or_capped_fallback(self):
        calls = [lambda: emergency.weight_based_total(1e308, 20, 1000),
                 lambda: emergency.volume_for_dose(1e308, 1e-308),
                 lambda: emergency.infusion_per_kg_hour_ml_h(1e308, 20, 1),
                 lambda: fluids.shock_bolus(1e308), lambda: fluids.symptomatic_hyponatremia_bolus(1e308),
                 lambda: blood.ffp_range_ml(1e308),
                 lambda: burns.burn_plan(1e308, 10), lambda: dka.cerebral_injury_rescue(1e308),
                 lambda: hypertension.hydralazine_ml_h(1e308, 10)]
        for i, call in enumerate(calls):
            with self.subTest(calculator=i), self.assertRaisesRegex(ValueError, 'finite'):
                call()

    def test_valid_calculations_keep_expected_finite_results(self):
        self.assertAlmostEqual(emergency.infusion_per_kg_min_ml_h(0.1, 20, 10), 12)
        self.assertEqual(emergency.weight_based_total(15, 80, 1000), {'total_dose': 1000, 'capped': True})
        self.assertEqual(respiratory.ventilation_rate_reference(0), 25)
        self.assertEqual(burns.burn_plan(20, 10, 8)['first_phase_rate_ml_h'], 0)
        self.assertTrue(math.isfinite(fluids.maintenance_ml_h(20)))

    def test_outpatient_rejects_invalid_weights_selections_and_overflow(self):
        for value in BAD + [0, -1]:
            with self.subTest(weight=value), self.assertRaises(ValueError):
                calculate('amoxicillin-aom', {'age_months': 84, 'actual_weight_kg': value})
        patient = {'age_months': 120, 'actual_weight_kg': 55, 'ideal_weight_kg': 35,
                   'home_analgesia_antipyresis_appropriate': True}
        for value in BAD + [0, -1]:
            with self.subTest(duration=value), self.assertRaises(ValueError):
                calculate('paracetamol-pain-fever-home', patient, selected_duration_days=value)
        with self.assertRaisesRegex(ValueError, 'finite'):
            calculate('paracetamol-pain-fever-home', {**patient, 'ideal_weight_kg': 1e308}, selected_duration_days=1)
        with self.assertRaises(ValueError):
            calculate('paracetamol-pain-fever-home', patient,
                      {'concentration_mg_per_ml': 1e-308, 'external_concentration_verified': True}, selected_duration_days=1)

    def test_alert_preflight_blocks_nonfinite_and_mistyped_numbers(self):
        for value in BAD:
            for field in ('age_months', 'actual_weight_kg'):
                patient = {'age_months': 84, 'actual_weight_kg': 20, field: value}
                with self.subTest(field=field, value=value):
                    self.assertTrue(evaluate('amoxicillin-aom', patient)['blocked'])
        self.assertTrue(evaluate('amoxicillin-aom', {'age_months': 84, 'actual_weight_kg': 20},
                                product={'concentration_mg_per_ml': float('inf'), 'external_concentration_verified': True})['blocked'])


class PediatricCatalogContract(unittest.TestCase):
    def test_exact_inventory_and_stable_regimen_ids(self):
        catalog = build_catalog()
        expected = {'regimens': 89, 'source_drug_labels': 54, 'drug_groups': 52,
                    'named_active_ingredients': 52, 'diagnoses': 88, 'drug_diagnosis_pairs': 89,
                    'documented_presentation_descriptions': 58, 'verified_liquid_products': 28,
                    'hidden_regimens': 0,
                    'unspecified_component_groups': ['electrolytes', 'low-osmolarity oral rehydration solution']}
        self.assertEqual(catalog['inventory'], expected)
        source = {e['id']: e for e in load_registry()['entries']}
        self.assertEqual(set(source), {e['id'] for e in catalog['regimens']})
        self.assertEqual(len(catalog['regimens']), len(source))
        drugs = {d['id'] for d in catalog['drugs']}
        for entry in catalog['regimens']:
            self.assertIn(entry['drug_id'], drugs)
            self.assertTrue(entry['diagnosis'])
            self.assertEqual({k: v for k, v in entry.items() if k != 'drug_id'}, source[entry['id']])
        self.assertEqual(drugs, {e['drug_id'] for e in catalog['regimens']})

    def test_formulations_do_not_duplicate_drug_identity(self):
        entries = {e['id']: e for e in build_catalog()['regimens']}
        self.assertEqual(entries['fluticasone-controller-preschool']['drug_id'],
                         entries['fluticasone-propionate-nasal-allergic-rhinitis']['drug_id'])
        self.assertNotEqual(entries['dexamethasone-croup-mild-moderate']['drug_id'],
                            entries['ciprofloxacin-dexamethasone-aoe-ge1y']['drug_id'])

    def test_deterministic_frontend_projection_and_central_conditions(self):
        first = serialize_catalog()
        self.assertEqual(first, serialize_catalog())
        self.assertEqual(first, (ROOT.parent / 'app/src/data/generatedPediatricOutpatient.json').read_text(encoding='utf-8'))
        rules = json.loads((ROOT / 'qa/pediatric-outpatient-alert-rules.json').read_text(encoding='utf-8'))
        self.assertEqual(build_catalog()['condition_rules'], rules['condition_rules'])

    def test_api_uses_canonical_calculation_and_keeps_gates(self):
        from clinical_note_api import dispatch
        payload = {'source_revision': build_catalog()['source_revision'], 'regimen_id': 'paracetamol-pain-fever-home',
                   'patient': {'age_months': 120, 'actual_weight_kg': 55, 'ideal_weight_kg': 35},
                   'product': {'concentration_mg_per_ml': 24}, 'selected_duration_days': 2}
        status, blocked = dispatch('/api/pediatric-outpatient/calculate', payload)
        self.assertEqual(status, 200)
        self.assertTrue(blocked['blocked'])
        self.assertNotIn('result', blocked)
        payload['patient']['home_analgesia_antipyresis_appropriate'] = True
        result = calculate_request(payload)['result']
        self.assertEqual(result['dose_mg'], 525)
        self.assertEqual(result['volume_per_dose']['rounded_0_1_ml'], 21.9)
        self.assertEqual(result['total_doses'], 8)
        self.assertEqual(result['estimated_total_course_ml'], 175)
        payload['source_revision'] = 'stale'
        with self.assertRaisesRegex(ValueError, 'catalog changed'):
            calculate_request(payload)

    def test_api_rejects_malformed_inputs_and_exposes_original_diagnosis(self):
        payload = {'source_revision': build_catalog()['source_revision'], 'regimen_id': 'dexamethasone-croup-mild-moderate',
                   'patient': {'age_months': 48, 'actual_weight_kg': 18, 'croup_discharge_criteria_met': True},
                   'product': {'concentration_mg_per_ml': 0.4}}
        result = calculate_request(payload)['result']
        self.assertAlmostEqual(result['dose_mg'], 2.7)
        self.assertAlmostEqual(result['volume_per_dose']['exact_ml'], 6.75)
        self.assertEqual(result['total_doses'], 1)
        self.assertIn('croup', result['diagnosis'])
        for field, value in [('patient', []), ('product', []), ('regimen_id', 1)]:
            with self.subTest(field=field), self.assertRaises(ValueError):
                calculate_request({**payload, field: value})
