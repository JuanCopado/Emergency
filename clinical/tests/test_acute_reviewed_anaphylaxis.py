"""Synthetic acceptance cases: constants are independent manual calculations.

Device limits, product checks and the 60-min use limit are fixture declarations,
not certification of a real device, product or stability interval.
"""
from copy import deepcopy
from decimal import Decimal
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from acute_medication_contracts import contract, field
from acute_reviewed_anaphylaxis import (
    IM_ID, INFUSION_ID, _im_dose_micrograms,
    reviewed_contracts, validation_errors, calculate,
)


IM_INITIAL_INPUTS = {
    'population': 'pediatric', 'route': 'IM', 'indication_confirmed': True,
    'clinical_situation': 'anaphylaxis', 'adrenaline_risk_assessment_completed': True,
    'age_months': 2, 'weight_kg': 5, 'abc_compromise': True,
    'concentration': 1, 'undiluted_im': True, 'product_verified': True,
    'measurement_increment_ml': 0.01, 'minimum_measurable_volume_ml': 0.01,
    'syringe_capacity_ml': 1, 'device_delivery_accuracy_verified': True,
    'im_needle_and_site_verified': True, 'monitoring_and_help_plan': True,
    'dose_phase': 'initial',
}
IM_REPEAT_INPUTS = {
    **IM_INITIAL_INPUTS, 'dose_phase': 'repeat', 'prior_im_doses': 1,
    'last_im_dose_micrograms': 50, 'last_im_dose_regimen': 'erc_wao_weight_based',
    'elapsed_min': 5, 'early_repeat_context': 'none',
    'refractory_escalation_active': False, 'iv_infusion_running': False,
}
INFUSION_INITIAL_INPUTS = {
    'population': 'adult', 'route': 'IV', 'indication_confirmed': True,
    'clinical_situation': 'anaphylaxis', 'adrenaline_risk_assessment_completed': True,
    'age_years': 40, 'weight_kg': 70, 'persistent_compromise': 'circulatory',
    'prior_im_doses': 2,
    'previous_im_dose_micrograms': 500, 'previous_im_dose_regimen': 'rcuk_age_banded',
    'minutes_since_previous_im': 6,
    'last_im_dose_micrograms': 500, 'last_im_dose_regimen': 'rcuk_age_banded',
    'minutes_since_last_im': 1, 'early_repeat_context': 'none',
    'initial_severity': 'moderate', 'expert_present': True,
    'fluid_resuscitation_assessed': True,
    'stock_concentration_mg_ml': 1, 'drug_amount_mg': 1, 'final_volume_ml': 100,
    'volume_basis': 'verified_final_volume', 'concentration': 10,
    'diluent': 'NaCl_0.9_percent', 'product_compatibility_stability_verified': True,
    'preparation_age_min': 10, 'verified_use_limit_min': 60,
    'immediate_use_and_asepsis_verified': True,
    'pump_ready': True, 'dedicated_primed_line_ready': True,
    'no_bp_cuff_on_infusion_arm': True, 'continuous_ecg_spo2_ready': True,
    'bp_interval_min': 5, 'extravasation_surveillance_ready': True,
    'suspected_adrenaline_toxicity': False,
}

# Browser/API fixtures, intentionally literal: never generated with calculate().
BROWSER_ACCEPTANCE_CASES = [
    {'regimen_id': IM_ID, 'name': 'IM initial, 2 months, 5 kg', 'inputs': IM_INITIAL_INPUTS,
     'expected': {'dose': 50, 'dose_unit': 'micrograms', 'administration_volume_ml': 0.05,
                  'pump_ml_h': None, 'duration_min': None}},
    {'regimen_id': IM_ID, 'name': 'IM repeat at 5 min, 5 kg', 'inputs': IM_REPEAT_INPUTS,
     'expected': {'dose': 50, 'dose_unit': 'micrograms', 'administration_volume_ml': 0.05,
                  'pump_ml_h': None, 'duration_min': None}},
    {'regimen_id': INFUSION_ID, 'name': 'IV initial moderate, 70 kg', 'inputs': INFUSION_INITIAL_INPUTS,
     'expected': {'dose': 5.833333333333333, 'dose_unit': 'micrograms/min',
                  'pump_ml_h': 35, 'amount_per_hour': 350, 'amount_per_hour_unit': 'micrograms/h',
                  'administration_volume_ml': None, 'duration_min': None}},
]


class ReviewedAnaphylaxisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = {r['id']: r for r in reviewed_contracts(contract, field)}

    def errors(self, rid, inputs):
        return dict(validation_errors(self.rows[rid], inputs))

    def assert_rejected(self, rid, inputs, code):
        self.assertIn(code, self.errors(rid, inputs))
        with self.assertRaises(ValueError):
            calculate(self.rows[rid], inputs)

    def test_exact_ids_review_provenance_and_no_hospital_or_absolute_allergy_gate(self):
        self.assertEqual(set(self.rows), {IM_ID, INFUSION_ID})
        for row in self.rows.values():
            self.assertEqual(row['reviewed_workflow'], 'anaphylaxis')
            self.assertEqual(row['review_reference'], 'references/acute-anaphylaxis-reviewed-2026-11-16.md')
            self.assertNotIn('block_reason', row)
            keys = [f['key'] for f in row['fields']]
            self.assertEqual(len(keys), len(set(keys)))
            self.assertNotIn('local_protocol_verified', keys)
            self.assertNotIn('allergy_contraindication_present', keys)

    def test_manual_browser_acceptance_examples(self):
        for case in BROWSER_ACCEPTANCE_CASES:
            with self.subTest(case=case['name']):
                row = self.rows[case['regimen_id']]
                self.assertEqual(validation_errors(row, case['inputs']), [])
                actual = calculate(row, case['inputs'])
                for key, expected in case['expected'].items():
                    if isinstance(expected, float):
                        self.assertAlmostEqual(actual[key], expected, places=12)
                    else:
                        self.assertEqual(actual[key], expected)

    def test_missing_active_inputs_fail_closed(self):
        for case in BROWSER_ACCEPTANCE_CASES:
            for key in case['inputs']:
                with self.subTest(case=case['name'], missing=key):
                    inputs = deepcopy(case['inputs'])
                    del inputs[key]
                    self.assert_rejected(case['regimen_id'], inputs, key)

    def test_initial_dose_has_no_invented_prior_history_and_rejects_stale_history(self):
        self.assertEqual(self.errors(IM_ID, IM_INITIAL_INPUTS), {})
        self.assert_rejected(IM_ID, {**IM_INITIAL_INPUTS, 'prior_im_doses': 1}, 'prior_im_doses')
        self.assertEqual(self.errors(IM_ID, {**IM_INITIAL_INPUTS, 'prior_im_doses': None}), {})

    def test_zero_six_month_boundary_and_birth_resuscitation(self):
        for age in (0, 5.999999):
            inputs = {**IM_INITIAL_INPUTS, 'age_months': age, 'weight_kg': 3}
            self.assertEqual(calculate(self.rows[IM_ID], inputs)['dose'], 30)
        for age in (-0.01, 6, 7):
            self.assert_rejected(IM_ID, {**IM_INITIAL_INPUTS, 'age_months': age}, 'age_months')
        self.assert_rejected(IM_ID, {**IM_INITIAL_INPUTS, 'clinical_situation': 'resuscitation_at_birth'}, 'clinical_situation')

    def test_numeric_inputs_reject_boolean_string_nonfinite_and_nonpositive_weight(self):
        for value in (True, '5', float('nan'), float('inf'), -1, 0, 10**400):
            with self.subTest(value=str(value)):
                self.assert_rejected(IM_ID, {**IM_INITIAL_INPUTS, 'weight_kg': value}, 'weight_kg')

    def test_no_minimum_100_micrograms_and_no_automatic_rounding(self):
        inputs = {**IM_INITIAL_INPUTS, 'weight_kg': 9}
        result = calculate(self.rows[IM_ID], inputs)
        self.assertEqual(result['dose'], 90)
        self.assertEqual(result['administration_volume_ml'], 0.09)
        self.assertIs(result['components']['minimum_dose_applied'], False)
        self.assertIs(result['components']['automatic_rounding_applied'], False)
        self.assertEqual(_im_dose_micrograms(Decimal('60')), Decimal('500'))

    def test_fractional_microvolume_requires_an_actual_declared_measurement_method(self):
        self.assert_rejected(IM_ID, {**IM_INITIAL_INPUTS, 'weight_kg': 3.55}, 'measurement_increment')
        inputs = {**IM_INITIAL_INPUTS, 'weight_kg': 3.55,
                  'measurement_increment_ml': 0.0005, 'minimum_measurable_volume_ml': 0.0005}
        result = calculate(self.rows[IM_ID], inputs)
        self.assertEqual(result['dose'], 35.5)
        self.assertEqual(result['administration_volume_ml'], 0.0355)
        self.assert_rejected(IM_ID, {**inputs, 'device_delivery_accuracy_verified': False}, 'device_delivery_accuracy_verified')

    def test_device_minimum_capacity_and_inconsistent_limits(self):
        self.assert_rejected(IM_ID, {**IM_INITIAL_INPUTS, 'minimum_measurable_volume_ml': 0.1}, 'measurable_volume')
        self.assert_rejected(IM_ID, {**IM_INITIAL_INPUTS, 'syringe_capacity_ml': 0.03}, 'measurable_volume')
        self.assert_rejected(IM_ID, {**IM_INITIAL_INPUTS, 'measurement_increment_ml': 2}, 'device_parameters')

    def test_im_rejects_iv_dilutions_and_wrong_route(self):
        for strength in (0.1, 0.01, 1000):
            self.assert_rejected(IM_ID, {**IM_INITIAL_INPUTS, 'concentration': strength}, 'concentration')
        self.assert_rejected(IM_ID, {**IM_INITIAL_INPUTS, 'undiluted_im': False}, 'undiluted_im')
        self.assert_rejected(IM_ID, {**IM_INITIAL_INPUTS, 'route': 'IV'}, 'route')

    def test_repeat_dose_and_real_count_must_match_declared_source(self):
        self.assert_rejected(IM_ID, {**IM_REPEAT_INPUTS, 'last_im_dose_micrograms': 0.05}, 'prior_im_dose')
        self.assert_rejected(IM_ID, {**IM_REPEAT_INPUTS, 'prior_im_doses': 1.5}, 'prior_im_doses')
        self.assert_rejected(IM_ID, {**IM_REPEAT_INPUTS, 'prior_im_doses': 0}, 'prior_im_doses')
        inputs = {**IM_REPEAT_INPUTS, 'last_im_dose_regimen': 'rcuk_age_banded', 'last_im_dose_micrograms': 100}
        self.assertEqual(calculate(self.rows[IM_ID], inputs)['dose'], 50)

    def test_early_repeat_keeps_urgent_guidance_without_numeric_exception(self):
        for declaration in ('none', 'documented_expert_decision_for_life_threatening_recurrence'):
            inputs = {**IM_REPEAT_INPUTS, 'elapsed_min': 4.99, 'early_repeat_context': declaration}
            result = calculate(self.rows[IM_ID], inputs)
            self.assertEqual(result['result_kind'], 'decision_support')
            for key in ('dose', 'dose_unit', 'administration_volume_ml', 'withdrawal_ml', 'pump_ml_h',
                        'components', 'concentration', 'maximum', 'preparation'):
                self.assertIsNone(result[key])
            self.assertTrue(any('sin esperar al formulario' in x for x in result['next_actions']))
            self.assert_rejected(IM_ID, {**inputs, 'elapsed_min': 0}, 'elapsed_min')
        self.assertEqual(calculate(self.rows[IM_ID], IM_REPEAT_INPUTS)['dose'], 50)

    def test_after_two_doses_escalation_is_required_without_forbidding_im_bridge(self):
        inputs = {**IM_REPEAT_INPUTS, 'prior_im_doses': 2}
        self.assert_rejected(IM_ID, inputs, 'refractory_escalation')
        inputs['refractory_escalation_active'] = True
        self.assertEqual(calculate(self.rows[IM_ID], inputs)['dose'], 50)
        self.assert_rejected(IM_ID, {**inputs, 'iv_infusion_running': True}, 'iv_infusion_running')

    def test_infusion_severe_manual_units(self):
        result = calculate(self.rows[INFUSION_ID], {**INFUSION_INITIAL_INPUTS, 'initial_severity': 'severe_hypotensive_or_hypoxic'})
        self.assertEqual(result['pump_ml_h'], 70)
        self.assertEqual(result['amount_per_hour'], 700)
        self.assertAlmostEqual(result['dose'], 11.666666666666666, places=12)
        self.assertAlmostEqual(result['components']['dose_micrograms_kg_min'], 1 / 6, places=12)
        self.assertEqual(result['withdrawal_ml'], 1)
        self.assertIsNone(result['duration_min'])
        self.assertIsNone(self.rows[INFUSION_ID]['maximum'])

    def test_pediatric_infusion_same_source_formula_with_actual_prior_doses(self):
        inputs = {**INFUSION_INITIAL_INPUTS, 'population': 'pediatric', 'age_years': 0.25, 'weight_kg': 5,
                  'previous_im_dose_micrograms': 50, 'last_im_dose_micrograms': 50,
                  'previous_im_dose_regimen': 'erc_wao_weight_based', 'last_im_dose_regimen': 'erc_wao_weight_based'}
        result = calculate(self.rows[INFUSION_ID], inputs)
        self.assertEqual(result['pump_ml_h'], 2.5)
        self.assertEqual(result['amount_per_hour'], 25)
        self.assertAlmostEqual(result['dose'], 0.4166666666666667, places=12)
        self.assert_rejected(INFUSION_ID, {**inputs, 'previous_im_dose_micrograms': 500}, 'previous_im_dose')

    def test_population_and_rcuk_age_boundaries(self):
        inputs = {**INFUSION_INITIAL_INPUTS, 'population': 'pediatric', 'age_years': 12,
                  'previous_im_dose_micrograms': 300, 'last_im_dose_micrograms': 300}
        self.assertEqual(self.errors(INFUSION_ID, inputs), {})
        self.assert_rejected(INFUSION_ID, {**inputs, 'age_years': 12.01}, 'previous_im_dose')
        self.assert_rejected(INFUSION_ID, {**INFUSION_INITIAL_INPUTS, 'age_years': 17.99}, 'population_age')
        self.assertEqual(self.errors(INFUSION_ID, {**INFUSION_INITIAL_INPUTS, 'age_years': 18}), {})

    def test_refractory_requires_two_doses_persistent_compromise_and_real_chronology(self):
        self.assert_rejected(INFUSION_ID, {**INFUSION_INITIAL_INPUTS, 'prior_im_doses': 1}, 'prior_im_doses')
        self.assert_rejected(INFUSION_ID, {**INFUSION_INITIAL_INPUTS, 'persistent_compromise': 'skin_only'}, 'persistent_compromise')
        self.assert_rejected(INFUSION_ID, {**INFUSION_INITIAL_INPUTS, 'minutes_since_previous_im': 0}, 'im_chronology')
        self.assert_rejected(INFUSION_ID, {**INFUSION_INITIAL_INPUTS, 'minutes_since_previous_im': 1}, 'im_chronology')
        for declaration in ('none', 'documented_expert_decision_for_life_threatening_recurrence'):
            result = calculate(self.rows[INFUSION_ID], {**INFUSION_INITIAL_INPUTS,
                               'minutes_since_previous_im': 5.99, 'early_repeat_context': declaration})
            self.assertEqual(result['result_kind'], 'decision_support')
            self.assertIsNone(result['dose'])
            self.assertIsNone(result['pump_ml_h'])
            self.assertIsNone(result['preparation'])

    def test_infusion_final_volume_and_concentration_cannot_be_interchanged(self):
        for key, value in [('concentration', 100), ('concentration', 1000), ('stock_concentration_mg_ml', 0.1),
                           ('final_volume_ml', 101), ('final_volume_ml', 1000), ('drug_amount_mg', 10),
                           ('final_volume_ml', 50), ('drug_amount_mg', 0.5), ('diluent', 'glucose_5_percent')]:
            with self.subTest(key=key, value=value):
                self.assert_rejected(INFUSION_ID, {**INFUSION_INITIAL_INPUTS, key: value}, key)

    def test_infusion_requires_resources_and_stops_at_expiry_and_toxicity(self):
        for key in ('expert_present', 'pump_ready', 'dedicated_primed_line_ready', 'continuous_ecg_spo2_ready',
                    'no_bp_cuff_on_infusion_arm', 'extravasation_surveillance_ready', 'product_compatibility_stability_verified'):
            self.assert_rejected(INFUSION_ID, {**INFUSION_INITIAL_INPUTS, key: False}, key)
        self.assert_rejected(INFUSION_ID, {**INFUSION_INITIAL_INPUTS, 'bp_interval_min': 5.01}, 'bp_interval_min')
        self.assert_rejected(INFUSION_ID, {**INFUSION_INITIAL_INPUTS, 'preparation_age_min': 60}, 'preparation_expired')
        self.assert_rejected(INFUSION_ID, {**INFUSION_INITIAL_INPUTS, 'suspected_adrenaline_toxicity': True}, 'suspected_adrenaline_toxicity')
        result = calculate(self.rows[INFUSION_ID], INFUSION_INITIAL_INPUTS)
        self.assertEqual(result['components']['remaining_verified_use_min'], 50)

    def test_infusion_rejects_arrest_io_and_numeric_overflow(self):
        self.assert_rejected(INFUSION_ID, {**INFUSION_INITIAL_INPUTS, 'clinical_situation': 'cardiac_arrest'}, 'clinical_situation')
        self.assert_rejected(INFUSION_ID, {**INFUSION_INITIAL_INPUTS, 'route': 'IO'}, 'route')
        self.assert_rejected(INFUSION_ID, {**INFUSION_INITIAL_INPUTS, 'weight_kg': 1e308}, 'weight_kg')

    def test_unknown_contract_and_inputs(self):
        self.assertIn('unsupported_contract', dict(validation_errors({'id': 'other'}, IM_INITIAL_INPUTS)))
        self.assert_rejected(IM_ID, {**IM_INITIAL_INPUTS, 'hospital_name': 'synthetic'}, 'unsupported_inputs')


if __name__ == '__main__':
    unittest.main()
