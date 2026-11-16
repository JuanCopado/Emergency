"""Independent clinical-contract cases; expected numbers are manually specified."""
import base64
import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from acute_medication_api import catalog, calculate_request, export_request


# Browser-bank examples: explicit inputs, not generated from the implementation.
PHENYTOIN_DOSE_ONLY_INPUTS = {
    'population': 'adult', 'route': 'IV', 'indication_confirmed': True,
    'allergy_contraindication_present': False, 'interaction_reviewed': True,
    'monitoring_ready': True, 'local_protocol_verified': True,
    'age_years': 40, 'weight_kg': 70, 'convulsive_status_confirmed': True,
    'adequate_benzodiazepine_given': True,
    'previous_phenytoin_or_fosphenytoin': False,
    'cause_specific_pathway_required': False,
    'cardiac_contraindication_present': False,
    'standard_loading_appropriate': True, 'elderly_or_cardiac_risk': False,
    'max_rate_mg_min': 50, 'duration_min': 40, 'calculation_scope': 'dose_only',
}
PHENYTOIN_DOSE_ONLY_EXPECTED = {
    'dose': 1400, 'dose_unit': 'mg', 'duration_min': 40,
    'infusion_rate_mg_min': 35, 'amount_per_hour': 2100,
    'withdrawal_ml': None, 'administration_volume_ml': None, 'pump_ml_h': None,
    'preparation': None, 'compatibility': None, 'stability': None,
}
PHENYTOIN_PREPARATION_INPUTS = {
    **PHENYTOIN_DOSE_ONLY_INPUTS, 'calculation_scope': 'verified_preparation',
    'preparation_product': 'Epanutin 250 mg/5 mL', 'concentration': 50,
    'product_preparation_matched': True, 'diluent': 'NaCl 0.9%',
    'diluent_volume_ml': 250, 'final_volume_ml': 278,
    'actual_volumes_verified': True, 'elapsed_since_preparation_min': 0,
    'immediate_start_confirmed': True, 'drawup_filter_5micron_verified': True,
    'inline_filter_0_2micron_verified': True, 'large_vein_access_verified': True,
    'pre_flush_confirmed': True, 'post_flush_volume_ml': 20,
    'post_flush_plan_verified': True, 'solution_clear': True,
}
PHENYTOIN_PREPARATION_EXPECTED = {
    'dose': 1400, 'dose_unit': 'mg', 'duration_min': 40,
    'infusion_rate_mg_min': 35, 'withdrawal_ml': 28,
    'administration_volume_ml': 278, 'pump_ml_h': 417,
}
REFRACTORY_INPUTS = {
    'population': 'adult', 'indication_confirmed': True,
    'monitoring_ready': True, 'local_protocol_verified': True,
    'age_years': 40, 'obstetric_context': False,
    'adequate_benzodiazepine_given': True, 'adequate_second_line_given': True,
    'second_line_agent': 'levetiracetam', 'current_state': 'ongoing_convulsions',
    'eeg_evidence_available': False, 'expert_team_contacted': True,
    'critical_care_available': True, 'continuous_eeg_available': True,
    'airway_support_available': True, 'cause_specific_pathway_required': False,
}
REFRACTORY_EXPECTED = {
    'result_kind': 'decision_support', 'treatment_calculated': False,
    'dose': None, 'dose_unit': None, 'duration_min': None,
    'withdrawal_ml': None, 'administration_volume_ml': None, 'pump_ml_h': None,
}


class ReviewedStatusContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = catalog()
        cls.rows = {row['id']: row for row in cls.catalog['regimens']}

    def payload(self, inputs, regimen='status-phenytoin-local'):
        return {'regimen_id': regimen, 'source_revision': self.catalog['source_revision'], 'inputs': copy.deepcopy(inputs)}

    def result(self, inputs, regimen='status-phenytoin-local'):
        data = calculate_request(self.payload(inputs, regimen))
        self.assertFalse(data['blocked'], data.get('alerts'))
        return data['result']

    def blocked(self, inputs, regimen='status-phenytoin-local', code=None):
        data = calculate_request(self.payload(inputs, regimen))
        self.assertTrue(data['blocked'])
        self.assertNotIn('result', data)
        if code is not None:
            self.assertIn(code, {alert['code'] for alert in data['alerts']})

    def test_public_ids_and_owner_acceptance_are_not_administrative_blockers(self):
        for rid in ('status-phenytoin-local', 'status-refractory'):
            row = self.rows[rid]
            self.assertFalse(row.get('block_reason'))
            self.assertEqual(row['reviewed_workflow'], 'status')
            self.assertEqual(row['review_reference'], 'references/acute-status-reviewed-2026-11-16.md')
            self.assertIn(rid, row['source']['contract_review']['owner_acceptance']['contract_ids'])
            self.assertIn('local_protocol_verified', {field['key'] for field in row['fields']})

    def test_dose_only_without_product_or_preparation(self):
        result = self.result(PHENYTOIN_DOSE_ONLY_INPUTS)
        for key, expected in PHENYTOIN_DOSE_ONLY_EXPECTED.items():
            self.assertEqual(result[key], expected, key)
        self.assertEqual(result['capabilities'], {'dose_and_time': True, 'product_withdrawal': False, 'pump_setting': False})
        self.assertEqual(result['clinical_status'], 'CLINICALLY_PENDING')
        self.assertEqual(result['review_status'], 'OWNER_VALIDATED_2026_11_16')

    def test_verified_preparation_uses_actual_final_volume_and_same_rate_flush(self):
        result = self.result(PHENYTOIN_PREPARATION_INPUTS)
        for key, expected in PHENYTOIN_PREPARATION_EXPECTED.items():
            self.assertEqual(result[key], expected, key)
        self.assertAlmostEqual(result['concentration']['value'], 5.035971223021583)
        self.assertEqual(result['preparation']['post_flush']['pump_ml_h'], 417)
        self.assertAlmostEqual(result['preparation']['post_flush']['duration_min'], 2.8776978417266186)
        self.assertAlmostEqual(result['stability']['completion_including_drug_delivery_flush_min'], 42.87769784172662)

    def test_dose_cap_and_exact_adult_boundary(self):
        for weight, expected in [(99.99, 1999.8), (100, 2000), (160, 2000), (1e308, 2000)]:
            with self.subTest(weight=weight):
                result = self.result({**PHENYTOIN_DOSE_ONLY_INPUTS, 'age_years': 18, 'weight_kg': weight})
                self.assertAlmostEqual(result['dose'], expected)
        self.blocked({**PHENYTOIN_DOSE_ONLY_INPUTS, 'age_years': 17.999}, code='age_years')
        self.blocked({**PHENYTOIN_DOSE_ONLY_INPUTS, 'population': 'pediatric'}, code='population')

    def test_source_dilution_brackets_do_not_follow_concentration_alone(self):
        cases = [
            (24.999, 499.98, 50, 59.9996),
            (25, 500, 100, 110),
            (50, 1000, 100, 120),
            (50.001, 1000.02, 250, 270.0004),
        ]
        for weight, dose, saline, final in cases:
            with self.subTest(weight=weight):
                result = self.result({**PHENYTOIN_PREPARATION_INPUTS, 'weight_kg': weight, 'diluent_volume_ml': saline, 'final_volume_ml': final})
                self.assertAlmostEqual(result['dose'], dose)
        # 500 mg in 50 mL saline is under 10 mg/mL after adding product,
        # but does not meet the selected source's 500 mg -> 100 mL bracket.
        self.blocked({**PHENYTOIN_PREPARATION_INPUTS, 'weight_kg': 25, 'diluent_volume_ml': 50, 'final_volume_ml': 60}, code='source_dilution')
        self.blocked({**PHENYTOIN_PREPARATION_INPUTS, 'diluent_volume_ml': 500, 'final_volume_ml': 528}, code='source_dilution')

    def test_final_volume_is_not_assumed_from_nominal_bag(self):
        self.blocked({**PHENYTOIN_PREPARATION_INPUTS, 'final_volume_ml': 250}, code='actual_final_volume')
        self.blocked({**PHENYTOIN_PREPARATION_INPUTS, 'final_volume_ml': 300}, code='actual_final_volume')
        self.blocked({**PHENYTOIN_PREPARATION_INPUTS, 'actual_volumes_verified': False}, code='actual_volumes_verified')

    def test_source_product_diluent_filter_and_clear_solution_gates(self):
        for patch, code in [
            ({'preparation_product': 'Hospira 250 mg/5 mL'}, 'preparation_product'),
            ({'preparation_product': 'Phenytoin 100 mg/2 mL'}, 'preparation_product'),
            ({'concentration': 25}, 'concentration'),
            ({'diluent': 'Dextrose 5%'}, 'diluent'),
            ({'product_preparation_matched': False}, 'product_preparation_matched'),
            ({'inline_filter_0_2micron_verified': False}, 'inline_filter_0_2micron_verified'),
            ({'drawup_filter_5micron_verified': False}, 'drawup_filter_5micron_verified'),
            ({'solution_clear': False}, 'solution_clear'),
            ({'post_flush_plan_verified': False}, 'post_flush_plan_verified'),
        ]:
            with self.subTest(patch=patch):
                self.blocked({**PHENYTOIN_PREPARATION_INPUTS, **patch}, code=code)
        result = self.result({**PHENYTOIN_PREPARATION_INPUTS, 'preparation_product': 'Phenytoin (Mercury) 250 mg/5 mL'})
        self.assertEqual(result['dose'], 1400)

    def test_all_active_inputs_are_required_without_numeric_fallback(self):
        for regimen, fixture in [
            ('status-phenytoin-local', PHENYTOIN_DOSE_ONLY_INPUTS),
            ('status-phenytoin-local', PHENYTOIN_PREPARATION_INPUTS),
            ('status-refractory', REFRACTORY_INPUTS),
        ]:
            for key in fixture:
                with self.subTest(regimen=regimen, missing=key, mode=fixture.get('calculation_scope')):
                    incomplete = dict(fixture)
                    incomplete.pop(key)
                    self.blocked(incomplete, regimen, code=key)

    def test_mode_switch_rejects_hidden_preparation_values(self):
        self.blocked({**PHENYTOIN_PREPARATION_INPUTS, 'calculation_scope': 'dose_only'}, code='preparation_product')
        self.blocked({**PHENYTOIN_DOSE_ONLY_INPUTS, 'calculation_scope': 'verified_preparation'}, code='preparation_product')
        self.result(PHENYTOIN_DOSE_ONLY_INPUTS)

    def test_rate_limits_and_selected_40_minute_reference(self):
        self.blocked({**PHENYTOIN_DOSE_ONLY_INPUTS, 'duration_min': 39.999}, code='duration_min')
        self.blocked({**PHENYTOIN_DOSE_ONLY_INPUTS, 'max_rate_mg_min': 50.001}, code='max_rate_mg_min')
        self.blocked({**PHENYTOIN_DOSE_ONLY_INPUTS, 'max_rate_mg_min': 25}, code='infusion_rate')
        self.blocked({**PHENYTOIN_DOSE_ONLY_INPUTS, 'elderly_or_cardiac_risk': True}, code='individual_rate')
        result = self.result({**PHENYTOIN_DOSE_ONLY_INPUTS, 'weight_kg': 100})
        self.assertEqual(result['infusion_rate_mg_min'], 50)

    def test_slow_dose_only_reference_does_not_invent_product_stability(self):
        slow = {**PHENYTOIN_DOSE_ONLY_INPUTS, 'weight_kg': 100, 'elderly_or_cardiac_risk': True, 'max_rate_mg_min': 25, 'duration_min': 80}
        result = self.result(slow)
        self.assertEqual(result['dose'], 2000)
        self.assertEqual(result['infusion_rate_mg_min'], 25)
        self.assertIsNone(result['stability'])
        self.assertIsNone(result['pump_ml_h'])
        full = {**PHENYTOIN_PREPARATION_INPUTS, **slow, 'calculation_scope': 'verified_preparation', 'final_volume_ml': 290}
        self.blocked(full, code='preparation_window')

    def test_exact_60_minute_completion_includes_flush_and_rejects_overrun(self):
        # 278 mL drug solution + 20 mL flush, at 298 mL/h, take exactly 60 min.
        # The drug-infusion duration is 278 / 298 * 60 = 8340 / 149 min.
        exact = {**PHENYTOIN_PREPARATION_INPUTS, 'duration_min': 8340 / 149}
        result = self.result(exact)
        self.assertAlmostEqual(result['pump_ml_h'], 298)
        self.assertAlmostEqual(result['stability']['completion_including_drug_delivery_flush_min'], 60)
        self.blocked({**exact, 'elapsed_since_preparation_min': 0.001}, code='preparation_window')
        # The infusion alone fits; residual-drug delivery takes it past expiry.
        self.blocked({**PHENYTOIN_PREPARATION_INPUTS, 'duration_min': 60}, code='preparation_window')

    def test_clinical_gates_prior_load_contraindication_and_missing_monitoring(self):
        for key, value in [
            ('previous_phenytoin_or_fosphenytoin', True),
            ('cardiac_contraindication_present', True),
            ('cause_specific_pathway_required', True),
            ('standard_loading_appropriate', False),
            ('allergy_contraindication_present', True),
            ('adequate_benzodiazepine_given', False),
            ('monitoring_ready', False),
        ]:
            with self.subTest(key=key):
                self.blocked({**PHENYTOIN_DOSE_ONLY_INPUTS, key: value}, code=key)

    def test_invalid_numeric_inputs_are_gates(self):
        for key, values in [
            ('weight_kg', [0, -1, True, '70', float('nan'), float('inf'), 10**400]),
            ('duration_min', [0, -40, True, float('inf')]),
            ('max_rate_mg_min', [0, -1, 51]),
        ]:
            for value in values:
                with self.subTest(key=key, value=str(value)):
                    self.blocked({**PHENYTOIN_DOSE_ONLY_INPUTS, key: value}, code=key)

    def test_refractory_returns_actions_and_no_anesthetic_arithmetic(self):
        result = self.result(REFRACTORY_INPUTS, 'status-refractory')
        for key, expected in REFRACTORY_EXPECTED.items():
            self.assertEqual(result[key], expected, key)
        self.assertEqual(result['decision_support']['stage'], 'refractory_status')
        self.assertFalse(result['decision_support']['anaesthetic_treatment_authorized'])
        self.assertTrue(result['next_actions'])

    def test_resource_gaps_allow_escalation_and_transfer_support(self):
        unavailable = {**REFRACTORY_INPUTS, 'monitoring_ready': False, 'expert_team_contacted': False, 'critical_care_available': False, 'continuous_eeg_available': False, 'airway_support_available': False}
        result = self.result(unavailable, 'status-refractory')
        self.assertEqual(len(result['decision_support']['resource_gaps']), 5)
        self.assertIn('traslado', ' '.join(result['next_actions']))
        self.assertIn('Activar ahora', result['next_actions'][0])
        self.assertIsNone(result['pump_ml_h'])

    def test_persistent_unconsciousness_is_not_automatically_nonconvulsive_status(self):
        result = self.result({**REFRACTORY_INPUTS, 'current_state': 'no_convulsions_impaired_consciousness'}, 'status-refractory')
        self.assertFalse(result['decision_support']['refractory_status_supported_by_entered_state'])
        self.assertEqual(result['decision_support']['stage'], 'persistent_impaired_consciousness_requires_eeg')
        self.assertIn('solicitar EEG urgente', ' '.join(result['next_actions']))

    def test_eeg_claim_requires_matching_evidence_and_state(self):
        self.blocked({**REFRACTORY_INPUTS, 'current_state': 'electrographic_seizures'}, 'status-refractory', code='eeg_evidence')
        self.blocked({**REFRACTORY_INPUTS, 'current_state': 'no_convulsions_impaired_consciousness', 'eeg_evidence_available': True}, 'status-refractory', code='eeg_state')
        result = self.result({**REFRACTORY_INPUTS, 'current_state': 'electrographic_seizures', 'eeg_evidence_available': True}, 'status-refractory')
        self.assertTrue(result['decision_support']['refractory_status_supported_by_entered_state'])

    def test_refractory_population_and_prior_treatment_gates(self):
        for patch, code in [
            ({'age_years': 17}, 'age_years'),
            ({'population': 'pediatric'}, 'population'),
            ({'obstetric_context': True}, 'obstetric_context'),
            ({'adequate_benzodiazepine_given': False}, 'adequate_benzodiazepine_given'),
            ({'adequate_second_line_given': False}, 'adequate_second_line_given'),
        ]:
            with self.subTest(patch=patch):
                self.blocked({**REFRACTORY_INPUTS, **patch}, 'status-refractory', code=code)

    def test_decision_support_export_preserves_meaning_and_no_calculated_treatment(self):
        payload = self.payload(REFRACTORY_INPUTS, 'status-refractory')
        response = calculate_request(payload)
        self.assertIn('apoyo de decisión', response['report']['sections'][0][0])
        exported = export_request({'format': 'json', 'calculation': payload, 'expected_result': response['result'], 'confirmed': True})
        report = json.loads(base64.b64decode(exported['content_base64']))
        self.assertEqual(report['snapshot']['result'], response['result'])
        self.assertFalse(report['snapshot']['result']['treatment_calculated'])


if __name__ == '__main__':
    unittest.main()
