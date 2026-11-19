"""Entered patient-weight domain; existing regimen rules remain authoritative."""
import base64
from copy import deepcopy
import json
import math
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from pediatric_catalog import build_catalog
from pediatric_numbers import outpatient_inputs, patient_weight, positive
from pediatric_outpatient_api import calculate_request
from pediatric_outpatient_calculator import _weight
from pediatric_result_exporter import export_request

CASES = json.loads((ROOT / 'qa/V1.44_PEDIATRIC_EXPORT_CASES.json').read_text())['cases']
BAD_WEIGHTS = (None, 0, -1, 5e-324, .5, math.nextafter(1, 0),
               math.nextafter(180, math.inf), 181, 1e308,
               math.inf, -math.inf, math.nan, True, False, '20', {}, [])


def body_for(case_id):
    case = next(item for item in CASES if item['id'] == case_id)
    return {**deepcopy(case['calculation']), 'source_revision': build_catalog()['source_revision']}


class PediatricPatientWeightRangeTests(unittest.TestCase):
    def test_entered_weights_have_inclusive_bounds_without_clipping_or_defaults(self):
        for field in ('actual_weight_kg', 'ideal_weight_kg', 'adjusted_weight_kg'):
            for value in (1, 18.25, 180):
                with self.subTest(field=field, value=value):
                    self.assertEqual(patient_weight(field, value), value)
                    outpatient_inputs({field: value})
            for value in BAD_WEIGHTS:
                with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                    outpatient_inputs({field: value})
        self.assertEqual(positive('dose_mg_per_kg', .5), .5)
        outpatient_inputs({})  # Optional weights are not fabricated or required.

    def test_each_supported_dosing_weight_basis_requires_its_own_input(self):
        for basis in ('actual', 'ideal', 'adjusted'):
            field = basis + '_weight_kg'
            for value in (1, 27.75, 180):
                with self.subTest(basis=basis, value=value):
                    self.assertEqual(_weight({'weight_basis': basis}, {field: value}), value)
            with self.subTest(basis=basis, missing=True), self.assertRaises(ValueError):
                _weight({'weight_basis': basis}, {})

    def test_actual_and_ideal_regimens_reject_invalid_values_before_calculating(self):
        for case_id, field in (('dexamethasone', 'actual_weight_kg'), ('paracetamol', 'ideal_weight_kg')):
            for value in BAD_WEIGHTS:
                body = body_for(case_id)
                body['patient'][field] = value
                with self.subTest(regimen=body['regimen_id'], weight=value), self.assertRaises(ValueError):
                    calculate_request(body)

    def test_missing_dosing_weights_remain_blocked_without_substituting_other_weights(self):
        for case_id, field in (('dexamethasone', 'actual_weight_kg'), ('paracetamol', 'ideal_weight_kg')):
            body = body_for(case_id)
            body['patient'].pop(field)
            with self.subTest(regimen=body['regimen_id']):
                response = calculate_request(body)
                self.assertTrue(response['blocked'])
                self.assertNotIn('result', response)
                self.assertIn('DOSING_WEIGHT_REQUIRED', [a['code'] for a in response['safety']['alerts']])

    def test_inclusive_boundaries_and_fractional_weights_survive_json_export(self):
        for case_id, field in (('dexamethasone', 'actual_weight_kg'), ('paracetamol', 'ideal_weight_kg')):
            for value in (1, 18.25, 180):
                body = body_for(case_id)
                body['patient'][field] = value
                with self.subTest(regimen=body['regimen_id'], weight=value):
                    computed = calculate_request(body)
                    self.assertFalse(computed['blocked'])
                    self.assertEqual(computed['result']['dosing_weight_kg'], value)
                    response = export_request({'format': 'json', 'calculation': body,
                                               'expected_result': computed['result']})
                    snapshot = json.loads(base64.b64decode(response['content_base64']))['snapshot']
                    self.assertEqual(snapshot['inputs']['patient'][field], value)
                    self.assertEqual(snapshot['result']['dosing_weight_kg'], value)
                    self.assertEqual(snapshot['clinical_status'], 'CLINICALLY_PENDING')

    def test_exports_recalculate_and_reject_invalid_weights_despite_previous_valid_result(self):
        body = body_for('paracetamol')
        previous = calculate_request(body)['result']
        for value in (.5, 181):
            body['patient']['ideal_weight_kg'] = value
            for fmt in ('json', 'pdf', 'docx'):
                with self.subTest(weight=value, fmt=fmt), self.assertRaisesRegex(ValueError, 'between 1 and 180'):
                    export_request({'format': fmt, 'calculation': body, 'expected_result': previous})

    def test_non_weight_regimens_do_not_require_or_invent_a_weight(self):
        for regimen_id in ('albendazole-ascariasis-ge2y', 'cetirizine-urticaria-ge1y'):
            body = {'regimen_id': regimen_id, 'source_revision': build_catalog()['source_revision'],
                    'patient': {'age_months': 84}}
            with self.subTest(regimen=regimen_id):
                computed = calculate_request(body)
                self.assertFalse(computed['blocked'])
                self.assertNotIn('dosing_weight_kg', computed['result'])
                self.assertFalse(any('weight' in key for key in computed['export_report']['snapshot']['inputs']['patient']))

    def test_source_specific_weight_band_exclusion_is_preserved(self):
        body = body_for('rizatriptan')
        body['patient']['actual_weight_kg'] = 40
        with self.assertRaisesRegex(ValueError, 'no matching age/weight band'):
            calculate_request(body)
        for weight, dose in ((35, 5), (41, 10)):
            body['patient']['actual_weight_kg'] = weight
            with self.subTest(weight=weight):
                self.assertEqual(calculate_request(body)['result']['dose_mg'], dose)


if __name__ == '__main__':
    unittest.main()
