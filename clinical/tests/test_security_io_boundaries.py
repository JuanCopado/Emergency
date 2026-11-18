"""Offline regressions of launcher capabilities, transport and export adapters."""
import argparse
import io
import json
import os
import pathlib
import runpy
import socket
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import Mock, patch

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'clinical/scripts'))
import cli_paths as paths
import clinical_note_api as api
import evidence_surveillance as surveillance
from test_clinical_note_http_privacy import make_handler


class LauncherCapabilityTests(unittest.TestCase):
    def test_selected_workspace_accepts_regular_files_and_nested_outputs(self):
        with tempfile.TemporaryDirectory() as td, patch.dict(os.environ, {'EMERGENCY_CLI_ROOT': td}):
            base = pathlib.Path(td).resolve()
            (base/'synthetic.json').write_text('{}', encoding='utf-8')
            self.assertEqual(paths.input_file('synthetic.json'), base/'synthetic.json')
            self.assertEqual(paths.input_file(base/'synthetic.json'), base/'synthetic.json')
            self.assertEqual(paths.input_directory('.'), base)
            self.assertEqual(paths.output_file('nested/report.json'), base/'nested/report.json')
            self.assertEqual(paths.output_directory('nested'), base/'nested')
            with self.assertRaises(argparse.ArgumentTypeError): paths.input_file('.')
            with self.assertRaises(argparse.ArgumentTypeError): paths.input_directory('synthetic.json')
            with self.assertRaises(argparse.ArgumentTypeError): paths.output_file('.')
            with self.assertRaises(argparse.ArgumentTypeError): paths.output_directory('synthetic.json')

    def test_argv_cannot_choose_another_root_or_a_sibling_prefix(self):
        with tempfile.TemporaryDirectory() as td:
            base = pathlib.Path(td)/'allowed'
            other = pathlib.Path(td)/'allowed-sibling'
            base.mkdir(); other.mkdir()
            (other/'secret.json').write_text('SYNTHETIC_OUTSIDE', encoding='utf-8')
            with patch.dict(os.environ, {'EMERGENCY_CLI_ROOT': str(base)}):
                for raw in ('../allowed-sibling/secret.json', str(other/'secret.json'),
                            '', 'x\x00.json', 'x\n.json', 'report:stream', 'NUL.txt', 'sub/COM1', 'name. ', '\\\\?\\C:\\x'):
                    with self.subTest(raw=repr(raw)), self.assertRaises((argparse.ArgumentTypeError, ValueError)):
                        paths.output_file(raw)
                self.assertEqual((other/'secret.json').read_text(), 'SYNTHETIC_OUTSIDE')

    def test_symlink_to_external_workspace_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            base = pathlib.Path(td)/'allowed'; other = pathlib.Path(td)/'outside'
            base.mkdir(); other.mkdir()
            try: (base/'link').symlink_to(other, target_is_directory=True)
            except OSError as exc: self.skipTest(f'Host cannot create symlink: {type(exc).__name__}')
            with patch.dict(os.environ, {'EMERGENCY_CLI_ROOT': str(base)}):
                with self.assertRaises(argparse.ArgumentTypeError): paths.output_file('link/report.json')

    def test_separate_input_output_grants_preserve_external_dataset_use(self):
        with tempfile.TemporaryDirectory() as td:
            base = pathlib.Path(td); data = base/'data'; output = base/'output'
            data.mkdir(); output.mkdir(); (data/'synthetic.json').write_text('{}')
            grants = {'EMERGENCY_CLI_INPUT_ROOT': str(data), 'EMERGENCY_CLI_OUTPUT_ROOT': str(output)}
            with patch.dict(os.environ, grants):
                self.assertEqual(paths.input_file('synthetic.json'), (data/'synthetic.json').resolve())
                self.assertEqual(paths.output_file('report.json'), (output/'report.json').resolve())
                with self.assertRaises(argparse.ArgumentTypeError): paths.output_file(str(data/'overwrite.json'))

    def test_invalid_root_and_missing_input_are_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            base = pathlib.Path(td); file = base/'file'; file.write_text('x')
            with patch.dict(os.environ, {'EMERGENCY_CLI_ROOT': str(file)}):
                with self.assertRaises(argparse.ArgumentTypeError): paths.input_file('x')
            with patch.dict(os.environ, {'EMERGENCY_CLI_ROOT': td}):
                with self.assertRaises(argparse.ArgumentTypeError): paths.input_file('missing.json')


class HttpTransportTests(unittest.TestCase):
    def test_json_roundtrip_retains_unicode_and_markup_as_data(self):
        body = {'synthetic': '<script>&value</script>', 'label': 'μg • ñ'}
        handler = make_handler()
        handler._send(200, body)
        raw = handler.wfile.getvalue()
        self.assertNotIn(b'<script>', raw)
        self.assertEqual(json.loads(raw), body)
        self.assertEqual(int(handler.sent_headers['Content-Length']), len(raw))
        self.assertTrue(handler.sent_headers['Content-Type'].startswith('application/json'))

    def test_network_bind_requires_explicit_tls_before_constructing_server(self):
        for argv in (['api', '--host', '0.0.0.0'],
                     ['api', '--host', '0.0.0.0', '--allow-network'],
                     ['api', '--tls-cert', 'cert.pem']):
            with self.subTest(argv=argv), patch.object(sys, 'argv', argv), \
                 patch.object(api, 'ThreadingHTTPServer') as server:
                with self.assertRaises(SystemExit): api.main()
                server.assert_not_called()

    def test_tls_server_loads_explicit_certificate_and_wraps_socket(self):
        with patch.object(sys, 'argv', ['api', '--host', '0.0.0.0', '--allow-network',
                                      '--tls-cert', 'synthetic-cert', '--tls-key', 'synthetic-key']), \
             patch.object(api.ssl, 'SSLContext') as context, \
             patch.object(api, 'ThreadingHTTPServer') as factory, redirect_stdout(io.StringIO()):
            api.main()
            context.return_value.load_cert_chain.assert_called_once_with('synthetic-cert', 'synthetic-key')
            context.return_value.wrap_socket.assert_called_once()
            factory.return_value.serve_forever.assert_called_once()

    def test_local_development_binding_remains_loopback(self):
        with patch.object(sys, 'argv', ['api']), patch.object(api, 'ThreadingHTTPServer') as factory, \
             patch.object(api.ssl, 'SSLContext') as context, redirect_stdout(io.StringIO()):
            api.main()
            self.assertEqual(factory.call_args.args[0], ('127.0.0.1', 8765))
            context.assert_not_called()

    def test_pinned_tls_uses_numeric_destination_and_original_hostname(self):
        conn = surveillance._PublicHTTPSConnection('www.who.int', timeout=2)
        conn._context = Mock()
        raw = Mock()
        with patch.object(surveillance, '_require_public_dns', return_value=('93.184.216.34',)), \
             patch.object(surveillance.socket, 'create_connection', return_value=raw) as connect:
            conn.connect()
            self.assertEqual(connect.call_args.args[0], ('93.184.216.34', 443))
            conn._context.wrap_socket.assert_called_once_with(raw, server_hostname='www.who.int')

    def test_pin_failure_closes_raw_socket_and_never_disables_certificate_checks(self):
        conn = surveillance._PublicHTTPSConnection('www.who.int', timeout=2)
        conn._context = Mock(); conn._context.wrap_socket.side_effect = OSError('synthetic TLS failure')
        raw = Mock()
        with patch.object(surveillance, '_require_public_dns', return_value=('93.184.216.34',)), \
             patch.object(surveillance.socket, 'create_connection', return_value=raw):
            with self.assertRaises(OSError): conn.connect()
        raw.close.assert_called_once()
        conn._tunnel_host = 'forbidden.example'
        with self.assertRaises(ValueError): conn.connect()

    def test_dns_fail_closed_without_http(self):
        with patch.object(surveillance.socket, 'getaddrinfo', side_effect=OSError('synthetic')):
            with self.assertRaises(ValueError): surveillance._require_public_dns('www.who.int')

    def test_nonpublic_multicast_mapped_ipv6_and_scoped_addresses_are_rejected(self):
        for value in ('127.0.0.1', '169.254.169.254', '10.1.2.3', '224.0.0.1',
                      '240.0.0.1', '0.0.0.0', '::1', '::', 'ff02::1', 'fe80::1',
                      '::ffff:127.0.0.1', '2606:4700:4700::1111%eth0'):
            with self.subTest(value=value): self.assertFalse(surveillance._is_public_address(value))
        self.assertTrue(surveillance._is_public_address('93.184.216.34'))
        self.assertTrue(surveillance._is_public_address('2606:4700:4700::1111'))

    def test_all_exports_reject_path_components_before_any_calculation(self):
        import acute_medication_api as acute
        import pediatric_result_exporter as pediatric
        for fmt in ('../outside', '/tmp/report', 'pdf/../../outside', 'PDF', '', None, ['pdf']):
            with self.subTest(fmt=fmt), patch.object(acute, 'calculate_request') as calculate:
                with self.assertRaises(ValueError): acute.export_request({'format': fmt, 'confirmed': True})
                calculate.assert_not_called()
            with self.subTest(fmt=fmt), self.assertRaises(ValueError): pediatric.export_request({'format': fmt})


class SyntheticFixtureIntegrityTests(unittest.TestCase):
    def test_browser_bank_rebuild_is_lossless_without_writing_existing_artifacts(self):
        destination = ROOT/'clinical/qa/V1.44_PEDIATRIC_BROWSER_CASES.json'
        original = destination.read_bytes()
        writes = []
        def capture(path, content, *args, **kwargs):
            self.assertEqual(path, destination)
            writes.append(content)
            return len(content)
        with patch.object(pathlib.Path, 'write_text', capture), redirect_stdout(io.StringIO()):
            result = runpy.run_path(str(ROOT/'clinical/qa/build_pediatric_browser_cases_v144.py'))
        self.assertEqual(len(writes), 1)
        self.assertEqual(json.loads(writes[0]), json.loads(original))
        self.assertEqual(destination.read_bytes(), original)
        self.assertEqual(result['output']['status'], 'CLINICALLY_PENDING')
        self.assertEqual(len(result['output']['cases']), 1061)


class UnifiedQaSubprocessTests(unittest.TestCase):
    def test_real_child_uses_repository_root_and_preserves_failure_status(self):
        runner = runpy.run_path(str(ROOT/'clinical/qa/qa_runner.py'))
        result = runner['run_check']('synthetic-cwd', [sys.executable, '-c',
            'from pathlib import Path; import sys; print(Path.cwd()); sys.exit(3)'])
        self.assertEqual(pathlib.Path(result['stdout']).resolve(), ROOT)
        self.assertFalse(result['passed'])
        self.assertEqual(result['returncode'], 3)
        self.assertEqual(result['name'], 'synthetic-cwd')


class DerivedManifestPathTests(unittest.TestCase):
    def test_manifest_escape_is_rejected_before_image_decode(self):
        import predict_ptbxl_afib_image_baseline as predictor
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)/'images'; root.mkdir()
            outside = pathlib.Path(td)/'outside.png'; outside.write_bytes(b'SYNTHETIC_NOT_AN_IMAGE')
            for name in ('../outside.png', str(outside), 'missing.png', 'nested/../../outside.png'):
                manifest = {'cases': [{'id': 'synthetic', 'image_file': name}]}
                with self.subTest(name=name), patch.object(predictor, 'extract_features') as decode:
                    with self.assertRaises(ValueError): predictor.predict(manifest, root)
                    decode.assert_not_called()
            self.assertEqual(outside.read_bytes(), b'SYNTHETIC_NOT_AN_IMAGE')

    def test_blinded_id_and_frozen_metadata_are_preserved_for_safe_image(self):
        import predict_ptbxl_afib_image_baseline as predictor
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td); (root/'safe.png').write_bytes(b'SYNTHETIC')
            manifest = {'target_condition': 'synthetic', 'cases': [{'id': 'blinded-001', 'image_file': 'safe.png'}]}
            features = {'npeaks': 0, 'cv': None, 'rmssd': None, 'mad': None}
            with patch.object(predictor, 'extract_features', return_value=features) as decode:
                result = predictor.predict(manifest, root, '2026-01-01T00:00:00Z')
            decode.assert_called_once_with((root/'safe.png').resolve())
            self.assertEqual(result['predictions'], [{'id': 'blinded-001', 'class': 'nondiagnostic',
                             'prediction_frozen_at': '2026-01-01T00:00:00Z'}])
            self.assertEqual(result['target_condition'], 'synthetic')


class CanonicalParserPreservationTests(unittest.TestCase):
    def test_procedure_header_captures_remain_identical_for_all_canonical_cards(self):
        import re
        import audit_procedure_schema_coverage_v141 as audit
        import validate_procedure_cards_v141 as cards
        import validate_procedure_template_v141 as template
        import build_procedure_visual_briefs as briefs
        old_header = re.compile(r"^##\s+(PROC-[A-Z]+-\d{3})\s+—\s+(.+?)(?:\s+—\s+([A-Z/]+))?$", re.M)
        old_template = re.compile(r"^##\s+(PROC-[A-Z]+-\d{3})\s+—\s+(.+)$", re.M)
        seen = 0
        for file in (ROOT/'clinical/modules/procedures').glob('*.md'):
            text = file.read_text(encoding='utf-8')
            def captures(pattern):
                return [(m.start(), m.end(), m.groups()) for m in pattern.finditer(text)]
            baseline = captures(old_header)
            for parser in (audit.HEADER, cards.HEADER, briefs.HEADER):
                self.assertEqual(captures(parser), baseline, file.name)
            self.assertEqual(captures(template.HEAD), captures(old_template), file.name)
            seen += len(baseline)
        self.assertEqual(seen, 200)

    def test_catalog_ingredient_projection_preserves_every_registry_label(self):
        import re
        from pediatric_catalog import ingredients
        registry = json.loads((ROOT/'clinical/qa/pediatric-outpatient-medications.json').read_text())
        for entry in registry['entries']:
            label = entry['drug']
            normalized = label.replace('epinephrine/adrenaline auto-injector', 'epinephrine')
            expected = []
            for part in normalized.split(' + '):
                part = re.sub(r'\s+\d+(?:\.\d+)?\s*(?:%|mg|g\b|micrograms?\b).*$', '', part)
                expected.extend(part.replace(' paediatric sachet', '').strip().split('/'))
            self.assertEqual(ingredients(label), expected, entry['id'])


class SyntheticPediatricBankTests(unittest.TestCase):
    def test_existing_independent_browser_expectations_also_hold_at_api_boundary(self):
        from pediatric_outpatient_api import calculate_request
        from pediatric_catalog import build_catalog
        bank = json.loads((ROOT/'clinical/qa/V1.44_PEDIATRIC_BROWSER_CASES.json').read_text(encoding='utf-8'))
        revision = build_catalog()['source_revision']
        exercised = 0
        for case in bank['cases']:
            if case.get('local_error'):
                continue  # Browser-only form checks are exercised by browser QA.
            payload = {k: case[k] for k in ('regimen_id', 'patient', 'product',
                       'selected_dose_per_kg', 'selected_duration_days', 'selected_volume_ml') if k in case}
            payload['patient'] = dict(payload['patient'])
            # Match the existing browser's comma-separated form serialization.
            for field in ('allergies', 'active_medications'):
                raw = payload['patient'].get(field)
                if raw is None:
                    payload['patient'].pop(field, None)
                elif isinstance(raw, str):
                    payload['patient'][field] = [v.strip() for v in raw.split(',') if v.strip()]
            payload['source_revision'] = revision
            with self.subTest(case=case['id']):
                try:
                    response = calculate_request(payload)
                except ValueError:
                    self.assertTrue(case['expect_rejection'])
                    continue
                exercised += 1
                for code in case.get('expect_alerts', []):
                    self.assertIn(code, {a['code'] for a in response['safety']['alerts']})
                self.assertEqual(response['blocked'], case['expect_rejection'])
                if response['blocked']:
                    self.assertNotIn('result', response)
                    continue
                for key, expected in case['expect'].items():
                    actual = response['result']
                    for part in key.split('.'):
                        actual = actual[int(part)] if isinstance(actual, list) else actual[part]
                    if isinstance(expected, (float, int)) and not isinstance(expected, bool):
                        self.assertAlmostEqual(actual, expected, delta=1e-8*max(1, abs(expected)), msg=key)
                    else:
                        self.assertEqual(actual, expected, key)
        self.assertGreater(exercised, 500)


if __name__ == '__main__':
    unittest.main()
