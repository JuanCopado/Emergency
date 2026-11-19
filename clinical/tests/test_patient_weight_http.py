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
