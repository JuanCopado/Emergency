"""Exact JSON input boundaries without imposing bounds on derived results."""
import http.client
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from patient_weight_request import parse_medication_request
from test_http_transport_security import running_server
import clinical_note_api as api


def post_literal(path, payload):
    with running_server(max_workers=1, request_timeout=2) as server:
        client = http.client.HTTPConnection(*server.server_address, timeout=2)
        try:
            client.request('POST', path, payload, {'Content-Type': 'application/json'})
            response = client.getresponse()
            return response.status, json.loads(response.read())
        finally:
            client.close()


class MedicationJsonIntegrityHttp(unittest.TestCase):
    def test_duplicate_members_rejected_before_dispatch_on_all_medication_routes(self):
        for api_name, container, field in (
                ('acute-medications', 'inputs', 'weight_kg'),
                ('pediatric-outpatient', 'patient', 'actual_weight_kg')):
            for first, second in ((70, 80), (181, 70), (70, 181), (70, 70)):
                members = f'"{field}":{first},"{field}":{second}'
                for calculation in ('{"' + container + '":{' + members + '}}',
                                    '{"' + container + '":{},"' + container + '":{}}'):
                    for action, raw in [('calculate', calculation),
                                        ('export', '{"calculation":' + calculation + '}')]:
                        with self.subTest(api=api_name, action=action, raw=raw), patch.object(api, 'dispatch') as dispatch:
                            self.assertEqual(post_literal(f'/api/{api_name}/{action}', raw),
                                             (422, {'error': 'invalid clinical request'}))
                            dispatch.assert_not_called()

    def test_real_calculation_and_confirmed_exports_require_unambiguous_exact_inputs(self):
        from test_acute_weight_range import calculation

        for regimen, field, valid, invalid in (
                ('insulin-dka', 'weight_kg', '70', ['181,"weight_kg":70', '80,"weight_kg":70']),
                ('status-lorazepam', 'prior_bzd_doses', '0e-400',
                 ['1e-400', '-1e-400', '1.000000000000000001', '0.999999999999999999'])):
            payload = calculation(regimen)
            payload['inputs'][field] = 'LITERAL'
            encoded = json.dumps(payload)
            calc_path = '/api/acute-medications/calculate'
            export_path = '/api/acute-medications/export'
            status, nominal = post_literal(calc_path, encoded.replace('"LITERAL"', valid))
            self.assertEqual(status, 200)
            self.assertFalse(nominal['blocked'])
            for fmt in ('json', 'pdf', 'docx'):
                envelope = json.dumps({'format': fmt, 'calculation': payload, 'confirmed': True,
                                       'expected_result': nominal['result']})
                status, artifact = post_literal(export_path, envelope.replace('"LITERAL"', valid))
                self.assertEqual(status, 200)
                self.assertTrue(artifact['content_base64'])
                for literal in invalid:
                    with self.subTest(regimen=regimen, fmt=fmt, literal=literal):
                        self.assertEqual(post_literal(export_path, envelope.replace('"LITERAL"', literal)),
                                         (422, {'error': 'invalid clinical request'}))
            for literal in invalid:
                with self.subTest(regimen=regimen, literal=literal):
                    self.assertEqual(post_literal(calc_path, encoded.replace('"LITERAL"', literal)),
                                     (422, {'error': 'invalid clinical request'}))

    def test_decimal_count_rounding_and_preservation(self):
        path = '/api/acute-medications/calculate'
        def parse_count(literal):
            return parse_medication_request(
                '{"regimen_id":"status-lorazepam","inputs":{"prior_bzd_doses":' + literal + '}}', path
            )['inputs']['prior_bzd_doses']

        for literal in ('0', '-0.0', '0e-400', '10e-1', '1.0', '100e-2'):
            self.assertEqual(parse_count(literal), float(literal))
        for literal in ('1e-400', '-1e-400', '0.99999999999999999999', '1.00000000000000000001'):
            with self.subTest(literal=literal), self.assertRaises(ValueError):
                parse_count(literal)
        # Ordinary fractional counts still reach the existing clinical STOP.
        self.assertEqual(parse_count('0.25'), 0.25)
        with self.assertRaises(ValueError):
            parse_medication_request(
                '{"regimen_id":"amiodarone-arrest-third","inputs":{"shock_count":3.0000000000000001}}', path)
        with self.assertRaises(ValueError):
            parse_medication_request('{"patient":{"age_months":1e-400}}', '/api/pediatric-outpatient/calculate')
        raw = '{"inputs":{"weight_kg":70},"other":{"weight_kg":80}}'
        self.assertEqual(parse_medication_request(raw, path), json.loads(raw))


class PatientWeightHttp(unittest.TestCase):
    def paths(self, literal):
        return (
            ('/api/acute-medications/calculate', '{"inputs":{"weight_kg":' + literal + '}}'),
            ('/api/acute-medications/export', '{"calculation":{"inputs":{"weight_kg":' + literal + '}}}'),
            ('/api/pediatric-outpatient/calculate', '{"patient":{"actual_weight_kg":' + literal + '}}'),
            ('/api/pediatric-outpatient/export', '{"calculation":{"patient":{"ideal_weight_kg":' + literal + '}}}'),
            ('/api/pediatric-outpatient/calculate', '{"patient":{"adjusted_weight_kg":' + literal + '}}'),
        )

    def test_outside_decimal_literals_are_rejected_before_float_rounding_and_dispatch(self):
        for literal in ('0.99999999999999999999', '180.000000000000000001'):
            for path, payload in self.paths(literal):
                with self.subTest(path=path, literal=literal), patch.object(api, 'dispatch') as dispatch:
                    status, body = post_literal(path, payload)
                    self.assertEqual(status, 422)
                    self.assertEqual(body, {'error': 'invalid clinical request'})
                    dispatch.assert_not_called()

    def test_endpoints_preserve_json_number_contract_without_coercing_strings(self):
        for literal in ('1', '1.0', '180', '180.000000000000000000'):
            for path, payload in self.paths(literal):
                with self.subTest(path=path, literal=literal), patch.object(api, 'dispatch', return_value=(200, {'ok': True})) as dispatch:
                    self.assertEqual(post_literal(path, payload), (200, {'ok': True}))
                    dispatch.assert_called_once()
                    self.assertEqual(dispatch.call_args.args[1], json.loads(payload))
        payload = parse_medication_request('{"inputs":{"weight_kg":"1"}}', '/api/acute-medications/calculate')
        self.assertIsInstance(payload['inputs']['weight_kg'], str)

    def test_derived_weights_nonweight_fields_and_other_paths_are_not_restricted(self):
        bodies = (
            ('/api/acute-medications/export', '{"calculation":{"inputs":{"weight_kg":70}},"expected_result":{"dosing_weight_kg":0.5,"weight_kg":181.5}}'),
            ('/api/pediatric-outpatient/export', '{"calculation":{"patient":{}},"expected_result":{"actual_weight_kg":0.5,"dosing_weight_kg":180.000000000000000001}}'),
            ('/api/acute-medications/calculate', '{"inputs":{"recent_ufh_units":0.5,"enoxaparin_mg":181.5,"duration_min":0.25}}'),
            ('/api/clinical-note/analyze', '{"weight_kg":180.000000000000000001}'),
        )
        for path, payload in bodies:
            with self.subTest(path=path, payload=payload), patch.object(api, 'dispatch', return_value=(200, {'ok': True})) as dispatch:
                self.assertEqual(post_literal(path, payload), (200, {'ok': True}))
                self.assertEqual(dispatch.call_args.args[1], json.loads(payload))
