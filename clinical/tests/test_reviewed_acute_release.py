"""Cross-workflow release invariants, source freshness and faithful exports.

These tests complement the clinical example banks. Source mutations are mocked
in memory; no reviewed source or shared file is changed by this test suite.
"""
import base64
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import acute_medication_api as api
from test_acute_reviewed_anaphylaxis import IM_INITIAL_INPUTS, IM_REPEAT_INPUTS, INFUSION_INITIAL_INPUTS
from test_acute_reviewed_reversal import EXAMPLE_CASES
from test_acute_reviewed_status import PHENYTOIN_DOSE_ONLY_INPUTS


EXPECTED_REVIEWED_IDS = {
    'status-refractory', 'status-phenytoin-local',
    'anaphylaxis-under6months', 'anaphylaxis-refractory',
    'reversal-vka-pcc', 'reversal-superwarfarin', 'reversal-edoxaban',
    'reversal-betrixaban', 'reversal-fondaparinux', 'reversal-other-lmwh',
    'reversal-enoxaparin-over12', 'reversal-argatroban', 'reversal-bivalirudin',
    'reversal-other-dti', 'reversal-danaparoid', 'reversal-fibrinolytics',
    'reversal-antiplatelets', 'reversal-unknown', 'reversal-dabigatran-repeat',
}
NUMERIC_RESULT_FIELDS = (
    'dose', 'dose_unit', 'withdrawal_ml', 'administration_volume_ml', 'pump_ml_h',
    'components', 'concentration', 'duration_min', 'amount_per_hour',
    'amount_per_hour_unit', 'maximum',
)
EXAMPLES = {item['contract_id']: item for item in EXAMPLE_CASES}


def request(regimen_id, inputs, current=None):
    current = current or api.catalog()
    return {'regimen_id': regimen_id, 'source_revision': current['source_revision'], 'inputs': deepcopy(inputs)}


class ReviewedAcuteReleaseTests(unittest.TestCase):
    def test_positive_dosing_outputs_must_survive_float_conversion_and_export_recalculation(self):
        cases = (
            ('anaphylaxis-refractory', INFUSION_INITIAL_INPUTS, 'weight_kg', 'dose'),
            ('reversal-other-lmwh', EXAMPLES['reversal-other-lmwh']['inputs'],
             'dalteparin_dose_to_neutralize_anti_xa_iu', 'dose'),
            ('status-phenytoin-local', PHENYTOIN_DOSE_ONLY_INPUTS, 'weight_kg', 'infusion_rate_mg_min'),
        )
        for regimen, inputs, field, output in cases:
            with self.subTest(regimen=regimen):
                payload = request(regimen, {**inputs, field: 1e-320})
                prior = api.calculate_request(payload)['result']
                self.assertGreater(prior[output], 0)
                payload['inputs'][field] = 5e-324
                with self.assertRaises(ValueError):
                    api.calculate_request(payload)
                for fmt in ('json', 'pdf', 'docx'):
                    with self.subTest(format=fmt), self.assertRaises(ValueError):
                        api.export_request({'format': fmt, 'confirmed': True,
                                            'calculation': payload, 'expected_result': prior})

    def test_exact_nineteen_acceptances_and_source_provenance(self):
        current = api.catalog()
        rows = current['regimens']
        reviewed = [row for row in rows if row.get('reviewed_workflow')]
        self.assertEqual(46, len(rows))
        self.assertEqual(46, len({row['id'] for row in rows}))
        self.assertEqual(EXPECTED_REVIEWED_IDS, {row['id'] for row in reviewed})
        self.assertFalse(any(row.get('block_reason') for row in rows))
        self.assertEqual(current['clinical_status'], 'CLINICALLY_PENDING')
        for row in reviewed:
            record = row['source']['contract_review']
            acceptance = record['owner_acceptance']
            self.assertEqual(EXPECTED_REVIEWED_IDS, set(acceptance['contract_ids']))
            self.assertEqual(19, len(acceptance['contract_ids']))
            self.assertEqual(acceptance['date'], '2026-11-16')
            self.assertEqual(acceptance['acceptance_type'], 'explicit_owner_clinical_validation_and_implementation_authorization')
            self.assertIs(acceptance['patient_specific_safety_gates_retained'], True)
            self.assertIs(acceptance['independent_pharmacy_signature_claimed'], False)
            self.assertIs(acceptance['prospective_validation_claimed'], False)
            source = api.ROOT / row['review_reference']
            self.assertEqual(record['sha256'], hashlib.sha256(source.read_bytes()).hexdigest())
            self.assertEqual(record['body'], source.read_text(encoding='utf-8'))
            self.assertEqual(record['path'], 'clinical/' + row['review_reference'])

    def test_owner_acceptance_rejects_missing_and_extra_scope(self):
        acceptance_path = (api.ROOT / 'references/acute-contract-owner-acceptance-2026-11-16.json').resolve()
        original = Path.read_text
        data = json.loads(original(acceptance_path, encoding='utf-8'))
        for ids in (data['contract_ids'][:-1], data['contract_ids'] + ['unexpected-new-contract']):
            changed = {**data, 'contract_ids': ids}

            def read_text(path, *args, **kwargs):
                return json.dumps(changed) if path.resolve() == acceptance_path else original(path, *args, **kwargs)

            with self.subTest(ids=len(ids)), patch.object(Path, 'read_text', read_text):
                with self.assertRaisesRegex(ValueError, 'owner acceptance scope'):
                    api.catalog()

    def test_imported_implementations_change_revision_and_reject_stale_export(self):
        current = api.catalog()
        payload = request('anaphylaxis-under6months', IM_INITIAL_INPUTS, current)
        confirmed = api.calculate_request(payload)['result']
        source_paths = [Path(module.__file__).resolve() for module in api.REVIEWED_WORKFLOWS.values()]
        source_paths += [Path(api.__file__).with_name(name).resolve() for name in
                         ('acute_medication_contracts.py', 'acid_base_hyperglycemia.py', 'pediatric_numbers.py')]
        original = Path.read_bytes
        for target in source_paths:

            def read_bytes(path):
                content = original(path)
                return content + b'\n# synthetic source revision\n' if path.resolve() == target else content

            with self.subTest(source=target.name), patch.object(Path, 'read_bytes', read_bytes):
                self.assertNotEqual(current['source_revision'], api.catalog()['source_revision'])
                with self.assertRaisesRegex(ValueError, 'Source revision changed'):
                    api.calculate_request(payload)
                with self.assertRaisesRegex(ValueError, 'Source revision changed'):
                    api.export_request({'format': 'json', 'confirmed': True,
                                        'calculation': payload, 'expected_result': confirmed})

    def test_decision_outputs_and_exports_do_not_inherit_numeric_regimen_values(self):
        cases = [
            ('reversal-unknown', EXAMPLES['reversal-unknown']['inputs']),
            ('anaphylaxis-under6months', {**IM_REPEAT_INPUTS, 'elapsed_min': 4.999}),
            ('anaphylaxis-refractory', {**INFUSION_INITIAL_INPUTS, 'minutes_since_previous_im': 5.999}),
        ]
        for rid, inputs in cases:
            with self.subTest(contract=rid):
                payload = request(rid, inputs)
                calculated = api.calculate_request(payload)
                self.assertFalse(calculated['blocked'])
                result = calculated['result']
                self.assertEqual(result['result_kind'], 'decision_support')
                for key in NUMERIC_RESULT_FIELDS:
                    self.assertIsNone(result[key], key)
                self.assertIsNone(result['preparation'])
                self.assertEqual(result['review_status'], 'OWNER_VALIDATED_2026_11_16')
                exported = api.export_request({'format': 'json', 'confirmed': True,
                                              'calculation': payload, 'expected_result': result})
                report = json.loads(base64.b64decode(exported['content_base64']))
                self.assertEqual(report['snapshot']['result'], result)
                self.assertIn('apoyo de decisión', report['sections'][0][0])
                self.assertEqual(report['snapshot']['clinical_status'], 'CLINICALLY_PENDING')

    def test_api_rejects_numeric_leak_from_decision_helper(self):
        inputs = EXAMPLES['reversal-unknown']['inputs']
        payload = request('reversal-unknown', inputs)
        row = next(row for row in api.catalog()['regimens'] if row['id'] == 'reversal-unknown')
        module = api.REVIEWED_WORKFLOWS['reversal']
        clean = module.calculate(row, inputs)
        leaks = {
            'dose': 1, 'dose_unit': 'mg', 'withdrawal_ml': 1,
            'administration_volume_ml': 1, 'pump_ml_h': 1,
            'components': {'bolus_mg': 1}, 'concentration': {'value': 1, 'unit': 'mg/mL'},
            'duration_min': 1, 'amount_per_hour': 1, 'amount_per_hour_unit': 'mg/h',
            'maximum': {'value': 1, 'unit': 'mg'},
        }
        for key, value in leaks.items():
            with self.subTest(leak=key), patch.object(module, 'calculate', return_value={**clean, key: value}):
                with self.assertRaisesRegex(ValueError, 'decision-support-only'):
                    api.calculate_request(payload)

    def test_mode_change_cannot_export_a_previous_numeric_confirmation(self):
        rid = 'reversal-vka-pcc'
        current = api.catalog()
        numeric = request(rid, EXAMPLES[rid]['inputs'], current)
        confirmed_numeric = api.calculate_request(numeric)['result']
        stale_inputs = {**numeric['inputs'], 'pcc_profile': 'other_or_unverified'}
        stale = request(rid, stale_inputs, current)
        self.assertTrue(api.calculate_request(stale)['blocked'])
        with self.assertRaisesRegex(ValueError, 'clinical safety gates'):
            api.export_request({'format': 'json', 'confirmed': True,
                                'calculation': stale, 'expected_result': confirmed_numeric})
        row = next(row for row in current['regimens'] if row['id'] == rid)
        clean_inputs = {key: value for key, value in stale_inputs.items()
                        if key not in {f['key'] for f in row['fields'] if f.get('required_if')}}
        decision = request(rid, clean_inputs, current)
        result = api.calculate_request(decision)['result']
        self.assertEqual(result['result_kind'], 'decision_support')
        self.assertIsNone(result['dose'])
        with self.assertRaisesRegex(ValueError, 'Result changed'):
            api.export_request({'format': 'json', 'confirmed': True,
                                'calculation': decision, 'expected_result': confirmed_numeric})

    def test_im_risk_review_replaces_absolute_allergy_gate_without_changing_doses(self):
        rows = api.catalog()['regimens']
        expected = {'anaphylaxis-adult': 500, 'anaphylaxis-over12': 500,
                    'anaphylaxis-6to12': 300, 'anaphylaxis-6monthsto6': 150}
        for rid, dose in expected.items():
            row = next(row for row in rows if row['id'] == rid)
            self.assertEqual(row['dose'], dose)
            fields = {f['key']: f for f in row['fields']}
            self.assertNotIn('allergy_contraindication_present', fields)
            self.assertIs(fields['adrenaline_risk_assessment_completed']['expected'], True)
        adult_inputs = {
            'population': 'adult', 'route': 'IM', 'indication_confirmed': True,
            'interaction_reviewed': True, 'monitoring_ready': True, 'local_protocol_verified': True,
            'concentration': 1, 'product_verified': True, 'abc_compromise': True,
            'prior_im_doses': 0, 'elapsed_min': 0, 'small_volume_checked': True,
            'adrenaline_risk_assessment_completed': True,
        }
        result = api.calculate_request(request('anaphylaxis-adult', adult_inputs))
        self.assertFalse(result['blocked'])
        self.assertEqual(result['result']['dose'], 500)
        self.assertEqual(result['result']['administration_volume_ml'], 0.5)


if __name__ == '__main__':
    unittest.main()
