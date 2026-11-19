"""Owner-approved input bounds; formulas and source-specific gates stay intact."""
import base64
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from acute_medication_api import catalog, calculate_request, export_request


WEIGHT_REGIMENS = ('insulin-dka', 'insulin-mixed', 'insulin-dextrose',
                  'insulin-hhs', 'status-lorazepam', 'status-diazepam')
EXPECTED_DOSES = {
    1: (.1, .1, .05, .05, .1, .2),
    70: (7, 7, 3.5, 3.5, 4, 10),
    180: (18, 18, 9, 9, 4, 10),
}
BANK = {case['id']: case for case in json.loads(
    (Path(__file__).resolve().parents[1] / 'qa/V1.44_ACUTE_MEDICATION_CASES.json')
    .read_text(encoding='utf-8'))['cases']}


def calculation(regimen):
    return {'regimen_id': regimen, 'source_revision': catalog()['source_revision'],
            'inputs': {'population': 'adult', 'route': 'IV',
                       'indication_confirmed': True, 'allergy_contraindication_present': False,
                       'interaction_reviewed': True, 'monitoring_ready': True,
                       'local_protocol_verified': True, **deepcopy(BANK[regimen]['inputs'])}}


class AcuteWeightRange(unittest.TestCase):
    def test_catalog_intersects_all_weight_fields_with_existing_constraints(self):
        for row in catalog()['regimens']:
            for field in row['fields']:
                if field['key'] == 'weight_kg':
                    with self.subTest(regimen=row['id']):
                        self.assertGreaterEqual(field['minimum'], 1)
                        self.assertLessEqual(field['maximum'], 180)
        midazolam = next(row for row in catalog()['regimens'] if row['id'] == 'status-midazolam')
        self.assertEqual(next(f for f in midazolam['fields'] if f['key'] == 'weight_kg')['exclusive_minimum'], 40)

    def test_six_regimens_require_finite_in_range_numeric_weight(self):
        for regimen in WEIGHT_REGIMENS:
            for weight in (None, False, True, 0, -1, 5e-324, .999, 180.00000000000003,
                           181, float('nan'), float('inf'), -float('inf'), '70'):
                with self.subTest(regimen=regimen, weight=weight):
                    payload = calculation(regimen)
                    payload['inputs']['weight_kg'] = weight
                    result = calculate_request(payload)
                    self.assertTrue(result['blocked'])
                    self.assertNotIn('result', result)
            payload = calculation(regimen)
            del payload['inputs']['weight_kg']
            self.assertTrue(calculate_request(payload)['blocked'])

    def test_inclusive_endpoints_and_nominal_doses_are_not_clamped(self):
        for weight, doses in EXPECTED_DOSES.items():
            for regimen, expected in zip(WEIGHT_REGIMENS, doses):
                with self.subTest(regimen=regimen, weight=weight):
                    payload = calculation(regimen)
                    payload['inputs']['weight_kg'] = weight
                    result = calculate_request(payload)
                    self.assertFalse(result['blocked'])
                    self.assertEqual(result['result']['dose'], expected)
                    self.assertEqual(result['report']['snapshot']['inputs']['weight_kg'], weight)
                    self.assertEqual(result['result']['clinical_status'], 'CLINICALLY_PENDING')

    def test_export_rechecks_all_six_regimens_and_preserves_valid_weight(self):
        for regimen in WEIGHT_REGIMENS:
            for weight in (1, 180):
                payload = calculation(regimen)
                payload['inputs']['weight_kg'] = weight
                expected = calculate_request(payload)['result']
                for fmt in ('json', 'pdf', 'docx'):
                    with self.subTest(regimen=regimen, weight=weight, fmt=fmt):
                        body = {'calculation': payload, 'expected_result': expected,
                                'format': fmt, 'confirmed': True}
                        exported = export_request(body)
                        data = base64.b64decode(exported['content_base64'])
                        if fmt == 'json':
                            report = json.loads(data)
                            self.assertEqual(report['snapshot']['inputs']['weight_kg'], weight)
                            self.assertEqual(report['snapshot']['result'], expected)
                        else:
                            self.assertTrue(data.startswith(b'%PDF' if fmt == 'pdf' else b'PK'))
                        changed = deepcopy(body)
                        changed['calculation']['inputs']['weight_kg'] = .999 if weight == 1 else 181
                        with self.assertRaises(ValueError):
                            export_request(changed)

    def test_midazolam_stricter_limit_and_fixed_dose_without_weight_are_preserved(self):
        payload = calculation('status-midazolam')
        for weight, blocked in ((1, True), (40, True), (41, False), (180, False), (181, True)):
            payload['inputs']['weight_kg'] = weight
            result = calculate_request(payload)
            self.assertEqual(result['blocked'], blocked)
            if not blocked:
                self.assertEqual(result['result']['dose'], 10)
        payload = calculation('amiodarone-arrest-third')
        self.assertNotIn('weight_kg', payload['inputs'])
        self.assertEqual(calculate_request(payload)['result']['dose'], 300)


class LegacyProtamineUnderflow(unittest.TestCase):
    CASES = (('reversal-ufh', 'recent_ufh_units', 1e-302),
             ('reversal-enoxaparin-late', 'enoxaparin_mg', 5e-301),
             ('reversal-enoxaparin-repeat', 'enoxaparin_mg', 5e-301))

    def test_positive_input_cannot_become_zero_dose_or_export(self):
        for regimen, field, _ in self.CASES:
            payload = calculation(regimen)
            expected = calculate_request(payload)['result']
            self.assertNotIn('weight_kg', payload['inputs'])
            payload['inputs'][field] = 5e-324
            with self.subTest(regimen=regimen), self.assertRaisesRegex(ValueError, 'dose must remain positive'):
                calculate_request(payload)
            for fmt in ('json', 'pdf', 'docx'):
                with self.subTest(regimen=regimen, fmt=fmt), self.assertRaisesRegex(ValueError, 'dose must remain positive'):
                    export_request({'format': fmt, 'calculation': payload,
                                    'expected_result': expected, 'confirmed': True})

    def test_representable_positive_doses_are_not_given_a_new_minimum(self):
        for regimen, field, expected in self.CASES:
            with self.subTest(regimen=regimen):
                payload = calculation(regimen)
                payload['inputs'][field] = 1e-300
                result = calculate_request(payload)
                self.assertFalse(result['blocked'])
                self.assertAlmostEqual(result['result']['dose'] / expected, 1)
                self.assertGreater(result['result']['dose'], 0)
                self.assertIsNone(result['result']['pump_ml_h'])
                exported = export_request({'format': 'json', 'calculation': payload,
                                           'expected_result': result['result'], 'confirmed': True})
                self.assertGreater(json.loads(base64.b64decode(exported['content_base64']))['snapshot']['result']['dose'], 0)
