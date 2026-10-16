import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from acute_medication_api import catalog, calculate_request, export_request


def request(regimen, **inputs):
    return {'regimen_id': regimen, 'source_revision': catalog()['source_revision'], 'inputs': {
        'population': 'adult', 'route': 'IV', 'indication_confirmed': True,
        'allergy_contraindication_present': False, 'interaction_reviewed': True,
        'monitoring_ready': True, 'local_protocol_verified': True,
        'concentration': 50, 'product_verified': True, **inputs,
    }}


class AmiodaroneFlow(unittest.TestCase):
    def test_oversized_json_integer_is_a_gate_not_an_unhandled_exception(self):
        data = calculate_request(request('amiodarone-arrest-third', shock_count=3, concentration=10**400))
        self.assertTrue(data['blocked'])
        self.assertNotIn('result', data)

    def test_oversized_export_value_is_rejected_without_overflow(self):
        payload = request('amiodarone-arrest-third', shock_count=3)
        result = calculate_request(payload)['result']
        result['dose'] = 10**400
        with self.assertRaises(ValueError):
            export_request({'format':'json', 'calculation':payload, 'expected_result':result, 'confirmed':True})

    def test_distinct_indications_and_source_preparation_limits(self):
        for rid, extra, dose, volume in [
            ('amiodarone-arrest-third', {'shock_count': 3}, 300, 6),
            ('amiodarone-arrest-fifth', {'shock_count': 5, 'prior_300mg_given': True}, 150, 3),
            ('amiodarone-failed-cardioversion', {'failed_cardioversion_unstable': True, 'duration_min': 20}, 300, 6),
            ('amiodarone-maintenance', {'loading_pathway_confirmed': True}, 900, 18),
        ]:
            with self.subTest(rid=rid):
                data = calculate_request(request(rid, **extra))
                self.assertFalse(data['blocked'])
                self.assertEqual(data['result']['dose'], dose)
                self.assertEqual(data['result']['dose_unit'], 'mg')
                self.assertEqual(data['result']['withdrawal_ml'], volume)
                self.assertIsNone(data['result']['administration_volume_ml'])
                self.assertIsNone(data['result']['pump_ml_h'])
                self.assertTrue(data['result']['limitations'])
                self.assertEqual(data['result']['clinical_status'], 'CLINICALLY_PENDING')

    def test_gates_and_no_safe_fallback(self):
        for update in [{'shock_count': 2}, {'concentration': 0}, {'concentration': 0.1},
                       {'route': 'IM'}, {'population': 'pediatric'},
                       {'allergy_contraindication_present': True}, {'product_verified': False},
                       {'interaction_reviewed': False}, {'monitoring_ready': False},
                       {'shock_count': float('nan')}, {'concentration': float('inf')}]:
            with self.subTest(update=update):
                data = calculate_request(request('amiodarone-arrest-third', shock_count=3, **update) if 'shock_count' not in update else request('amiodarone-arrest-third', **update))
                self.assertTrue(data['blocked'])
                self.assertNotIn('result', data)
        data = calculate_request(request('amiodarone-failed-cardioversion', failed_cardioversion_unstable=True, duration_min=21))
        self.assertTrue(data['blocked'])

    def test_stale_revision_unknown_indication_and_fields(self):
        payload = request('amiodarone-arrest-third', shock_count=3)
        for altered in [{**payload, 'source_revision': 'stale'}, {**payload, 'regimen_id': 'amiodarone-af-unmodeled'}, {**payload, 'inputs': {**payload['inputs'], 'dose': 600}}]:
            with self.assertRaises(ValueError): calculate_request(altered)

    def test_export_requires_confirmation_and_complete_result_fidelity(self):
        payload = request('amiodarone-arrest-third', shock_count=3)
        calculated = calculate_request(payload)
        body = {'calculation': payload, 'expected_result': calculated['result'], 'format': 'json', 'confirmed': True}
        import base64, json
        report = json.loads(base64.b64decode(export_request(body)['content_base64']))
        self.assertEqual(report['snapshot']['result'], calculated['result'])
        for bad in [{**body, 'confirmed': False}, {**body, 'expected_result': {**body['expected_result'], 'dose': 150}}]:
            with self.assertRaises(ValueError): export_request(bad)
        blocked = copy.deepcopy(payload); blocked['inputs']['route'] = 'IM'
        with self.assertRaises(ValueError): export_request({**body, 'calculation': blocked})

    def test_browser_json_number_roundtrip_keeps_export_faithful(self):
        payload = request('amiodarone-arrest-third', shock_count=3)
        result = calculate_request(payload)['result']
        result['withdrawal_ml'] = 6  # JSON.stringify sends 6, not Python's 6.0.
        body = {'calculation': payload, 'expected_result': result, 'format': 'json', 'confirmed': True}
        self.assertEqual(export_request(body)['mime_type'], 'application/json')
        result['withdrawal_ml'] = 6.01
        with self.assertRaises(ValueError): export_request(body)

    def test_docx_preserves_every_report_section_including_release_warning(self):
        import base64, io, zipfile
        from xml.etree import ElementTree
        payload = request('amiodarone-arrest-third', shock_count=3)
        data = calculate_request(payload)
        exported = export_request({'calculation': payload, 'expected_result': data['result'], 'format': 'docx', 'confirmed': True})
        with zipfile.ZipFile(io.BytesIO(base64.b64decode(exported['content_base64']))) as document:
            xml = ElementTree.fromstring(document.read('word/document.xml'))
        text = '\n'.join(n.text or '' for n in xml.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'))
        for title, paragraphs in data['report']['sections']:
            for value in [title, *paragraphs]: self.assertIn(value, text)


class SourceBoundFlowCases(unittest.TestCase):
    def test_every_contract_has_an_independent_browser_fixture(self):
        import json
        bank = json.loads((Path(__file__).resolve().parents[1] / 'qa/V1.44_ACUTE_MEDICATION_CASES.json').read_text(encoding='utf-8'))
        rows = catalog()['regimens']
        self.assertEqual({r['id'] for r in rows}, {c['id'] for c in bank['cases']})
        self.assertEqual(len(rows), len({r['id'] for r in rows}))
        self.assertEqual({r['group'] for r in rows}, {'amiodarone', 'insulin', 'sodium', 'status', 'anaphylaxis', 'reversal'})

    def test_independent_nominal_and_blocked_cases(self):
        import json
        bank = json.loads((Path(__file__).resolve().parents[1] / 'qa/V1.44_ACUTE_MEDICATION_CASES.json').read_text(encoding='utf-8'))
        current = catalog()
        for case in bank['cases']:
            import os
            if os.environ.get('ACUTE_FLOW') and case['group'] != os.environ['ACUTE_FLOW']:
                continue
            with self.subTest(case=case.get('case_id', case['id'])):
                inputs = {**bank['common'], **case['inputs']}
                row = next((r for r in current['regimens'] if r['id'] == case['id']), None)
                self.assertIsNotNone(row, case['id'])
                inputs = {k: v for k, v in inputs.items() if k in {f['key'] for f in row['fields']}}
                payload = {'regimen_id': case['id'], 'source_revision': current['source_revision'], 'inputs': inputs}
                actual = calculate_request(payload)
                self.assertEqual(actual['blocked'], case.get('blocked', False))
                if actual['blocked']:
                    self.assertNotIn('result', actual)
                    self.assertTrue(actual['alerts'])
                    with self.assertRaises(ValueError):
                        export_request({'format': 'json', 'calculation': payload, 'confirmed': True})
                    continue
                for key, expected in case['expect'].items():
                    self.assertEqual(actual['result'][key], expected, key)
                for updates in case.get('reject', []):
                    rejected = calculate_request({**payload, 'inputs': {**inputs, **updates}})
                    self.assertTrue(rejected['blocked'], updates)
                    self.assertNotIn('result', rejected)
                for f in row['fields']:
                    for value in [None, {}, [], float('nan'), float('inf')]:
                        rejected = calculate_request({**payload, 'inputs': {**inputs, f['key']: value}})
                        self.assertTrue(rejected['blocked'], (case['id'], f['key'], value))
                        self.assertNotIn('result', rejected)


if __name__ == '__main__':
    unittest.main()
