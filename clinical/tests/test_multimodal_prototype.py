"""Synthetic bytes test engineering gates, never diagnostic performance."""
import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import struct
import sys
import tempfile
import unittest
import zlib

from PIL import Image, PngImagePlugin

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from multimodal.intake import inspect_media, extract_navigation_frames
from multimodal.bank import validate_bank, blinded_inputs
from multimodal.bank import admitted_inputs
from multimodal.adapters import build_input
from multimodal.evaluation import evaluate
import multimodal_prototype as cli


class MultimodalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        Image.new('RGB', (32, 24), (10, 40, 90)).save(self.root / 'asset-001.png')
        payload = (self.root / 'asset-001.png').read_bytes()
        self.asset = dict(id='asset-001', path='asset-001.png',
                          sha256=hashlib.sha256(payload).hexdigest(), size_bytes=len(payload), derivative=False)
        self.case = dict(id='case-001', patient_group_id='patient-001',
                         study_group_id='study-001', source_group_id='source-001',
                         split='development', data_kind='synthetic', source_known=True,
                         modality='ecg', task_id='ecg_still', annotated=False,
                         assets=[self.asset], context=dict(speed_mm_s=25, gain_mm_mv=10),
                         rights=dict(authorized=True, authorization_ref='fixture-rights',
                                     allowed_uses=['development', 'teaching']),
                         privacy=dict(metadata_reviewed=True, pixels_reviewed=True,
                                      full_video_reviewed=False, reviewer_id='fixture-reviewer',
                                      reviewed_sha256=[self.asset['sha256']]))
        self.bank = dict(schema_version='1.0', cases=[self.case])

    def real_blind(self):
        self.case.update(split='blind_test', data_kind='authorized_deidentified', source_known=False)
        self.case['rights']['allowed_uses'].append('blind_test')

    def test_blind_video_asset_cannot_open_codecs_under_image_task(self):
        from unittest import mock
        import multimodal.bank as bank_module
        self.real_blind()
        for suffix in ('.mp4', '.webm', '.MP4', '.WEBM'):
            with self.subTest(suffix=suffix):
                self.asset['path'] = 'asset-001' + suffix
                # The catalog is valid: this must fail at the blind asset gate,
                # independently of image task_id, media files or installed codecs.
                self.assertFalse(validate_bank(self.bank)['errors'])
                with mock.patch.object(bank_module, 'inspect_media') as inspect:
                    with self.assertRaisesRegex(ValueError, '^blind_video_not_supported$'):
                        blinded_inputs(self.bank, self.root)
                    inspect.assert_not_called()

    def test_blind_noncanonical_suffix_cannot_reach_inspection(self):
        from unittest import mock
        import multimodal.bank as bank_module
        self.real_blind()
        for path in ('asset-001.mp4.', 'asset-001.webm ', 'asset-001.png.', 'asset-001.jpg '):
            with self.subTest(path=path):
                self.asset['path'] = path
                self.assertFalse(validate_bank(self.bank)['errors'])
                with mock.patch.object(bank_module, 'inspect_media') as inspect:
                    with self.assertRaisesRegex(ValueError, '^blind_image_format_required$'):
                        blinded_inputs(self.bank, self.root)
                    inspect.assert_not_called()

    def test_valid_image_decodes_and_reports_only_technical_metadata(self):
        result = inspect_media(self.root, self.asset)
        self.assertEqual(result['errors'], [])
        self.assertEqual((result['width'], result['height']), (32, 24))
        self.assertEqual(result['sha256'], self.asset['sha256'])
        self.assertFalse(result['temporal_interpretation_validated'])
        self.assertNotIn('tags', result)

    def test_corrupt_png_with_matching_digest_is_rejected(self):
        payload = b'\x89PNG\r\n\x1a\ncorrupt'
        (self.root / self.asset['path']).write_bytes(payload)
        self.asset.update(size_bytes=len(payload), sha256=hashlib.sha256(payload).hexdigest())
        self.assertTrue(inspect_media(self.root, self.asset)['errors'])

    def test_integrity_and_extension_mismatch_are_rejected(self):
        original_digest = self.asset['sha256']
        self.asset['sha256'] = '0' * 64
        self.assertTrue(inspect_media(self.root, self.asset)['errors'])
        self.asset['sha256'] = original_digest
        self.asset['path'] = 'asset-001.jpg'
        shutil.copyfile(self.root / 'asset-001.png', self.root / self.asset['path'])
        self.assertEqual(inspect_media(self.root, self.asset)['errors'], ['extension_signature_mismatch'])

    def test_parent_absolute_url_and_alternate_stream_paths_are_rejected(self):
        for value in ('../outside.png', str(self.root / 'asset-001.png'),
                      'https://example.org/a.png', 'asset-001.png:secret', r'..\outside.png'):
            with self.subTest(value=value):
                self.asset['path'] = value
                self.assertTrue(inspect_media(self.root, self.asset)['errors'])

    def test_size_and_pixel_limits_are_enforced(self):
        self.assertTrue(inspect_media(self.root, self.asset, max_bytes=1)['errors'])
        self.assertTrue(inspect_media(self.root, self.asset, max_pixels=100)['errors'])

    def test_metadata_text_does_not_appear_in_report(self):
        meta = PngImagePlugin.PngInfo()
        meta.add_text('patient', 'DO-NOT-EXPOSE-IDENTITY')
        Image.new('RGB', (32, 24)).save(self.root / 'asset-001.png', pnginfo=meta)
        payload = (self.root / 'asset-001.png').read_bytes()
        self.asset.update(size_bytes=len(payload), sha256=hashlib.sha256(payload).hexdigest())
        report = inspect_media(self.root, self.asset)
        self.assertNotIn('DO-NOT-EXPOSE', json.dumps(report))
        self.assertTrue(report['metadata_present'])

    def test_blind_input_rejects_late_png_text_even_with_review_bound_to_its_hash(self):
        path = self.root / self.asset['path']
        raw = path.read_bytes()
        kind, payload = b'tEXt', b'note\x00SYNTHETIC-LATE-TEXT'
        chunk = struct.pack('>I', len(payload)) + kind + payload + struct.pack('>I', zlib.crc32(kind + payload) & 0xffffffff)
        end = raw.rindex(b'\x00\x00\x00\x00IEND')
        raw = raw[:end] + chunk + raw[end:]
        path.write_bytes(raw)
        self.asset.update(sha256=hashlib.sha256(raw).hexdigest(), size_bytes=len(raw))
        self.case['privacy']['reviewed_sha256'] = [self.asset['sha256']]
        self.real_blind()
        self.assertEqual(validate_bank(self.bank)['errors'], [])
        report = inspect_media(self.root, self.asset)
        self.assertEqual(report['errors'], [])
        self.assertTrue(report['metadata_present'])
        with self.assertRaisesRegex(ValueError, '^blind_media_metadata_requires_clean_derivative$'):
            blinded_inputs(self.bank, self.root)

    def test_demo_cli_reports_safe_fixed_failure_reasons(self):
        target = self.root / 'SYNTHETIC-DESTINATION'
        target.mkdir()
        commands = [(target, None, 'demo_destination_must_be_new'),
                    (self.root / 'new-demo', {'PATH': ''}, 'demo_requires_ffmpeg_and_ffprobe')]
        import os
        for destination, overrides, expected in commands:
            env = {**os.environ, **(overrides or {})}
            proc = subprocess.run([sys.executable, str(Path(cli.__file__)), 'demo', str(destination)],
                                  env=env, capture_output=True, text=True, timeout=10)
            self.assertEqual(proc.returncode, 1)
            self.assertEqual(json.loads(proc.stdout)['errors'], [expected])
            self.assertNotIn(str(destination), proc.stdout + proc.stderr)
        self.assertFalse((self.root / 'new-demo').exists())

    def test_patient_study_source_hash_and_lineage_cannot_cross_splits(self):
        Image.new('RGB', (32, 24), (100, 50, 20)).save(self.root / 'asset-002.png')
        second_digest = hashlib.sha256((self.root / 'asset-002.png').read_bytes()).hexdigest()
        for key in ('patient_group_id', 'study_group_id', 'source_group_id', 'sha256', 'lineage_group_id'):
            bank = copy.deepcopy(self.bank)
            row = copy.deepcopy(bank['cases'][0])
            row.update(id='case-002', patient_group_id='patient-002', study_group_id='study-002',
                       source_group_id='source-002', split='teaching')
            row['assets'][0].update(id='asset-002', path='asset-002.png', sha256=second_digest,
                                   size_bytes=(self.root / 'asset-002.png').stat().st_size)
            row['privacy']['reviewed_sha256'] = [second_digest]
            bank['cases'].append(row)
            self.assertEqual(validate_bank(bank)['errors'], [], 'Independent valid cases must pass before the collision')
            if key == 'sha256':
                row['assets'][0]['sha256'] = self.asset['sha256']
                row['privacy']['reviewed_sha256'] = [self.asset['sha256']]
            elif key == 'lineage_group_id':
                row[key] = 'lineage-001'
                bank['cases'][0][key] = 'lineage-001'
            else:
                row[key] = self.case[key]
            with self.subTest(key=key):
                expected = ('case_index_1:duplicate_binary_reuse_forbidden' if key == 'sha256'
                            else 'case_index_1:cross_split_' + key)
                self.assertIn(expected, validate_bank(bank)['errors'])

    def test_synthetic_known_or_annotated_data_cannot_be_blind(self):
        self.real_blind()
        for key, value in [('data_kind', 'synthetic'), ('source_known', True), ('annotated', True)]:
            bank = copy.deepcopy(self.bank)
            bank['cases'][0][key] = value
            self.assertTrue(validate_bank(bank)['errors'])

    def test_authorization_privacy_and_reviewed_hash_fail_closed(self):
        for key in ('authorized', 'metadata_reviewed', 'pixels_reviewed', 'reviewed_sha256'):
            bank = copy.deepcopy(self.bank)
            block = bank['cases'][0]['rights' if key == 'authorized' else 'privacy']
            block[key] = [] if key == 'reviewed_sha256' else False
            with self.subTest(key=key):
                self.assertTrue(validate_bank(bank)['errors'])

    def test_blind_export_has_no_reference_source_or_original_filename(self):
        self.real_blind()
        self.case.update(reference={'target_positive': True}, source_url='SECRET-DIAGNOSIS',
                         original_filename='SECRET-DIAGNOSIS.png')
        rows = blinded_inputs(self.bank, self.root)
        self.assertEqual(len(rows), 1)
        output = json.dumps(rows)
        for forbidden in ('SECRET', 'reference', 'source_url', 'original_filename', 'reviewer'):
            self.assertNotIn(forbidden, output)
        self.assertEqual(rows[0]['assets'][0]['asset_id'], 'asset-001')
        self.assertNotIn('path', rows[0]['assets'][0])
        limits = ' '.join(rows[0]['limitations'])
        self.assertIn('PNG IDAT', limits)
        self.assertIn('JPEG scans', limits)
        self.assertIn('not a deidentification certificate', limits)

    def test_all_adapters_expose_limits_without_diagnostic_or_temporal_claim(self):
        report = inspect_media(self.root, self.asset)
        for modality, task in [('ecg', 'ecg_still'), ('pocus', 'pocus_still'),
                               ('chest_xray', 'radiograph_still'), ('ct_mri', 'ct_mri_screenshot')]:
            case = copy.deepcopy(self.case)
            case.update(modality=modality, task_id=task, context={})
            result = build_input(case, [report])
            self.assertFalse(result['diagnostic_validation'])
            self.assertFalse(result['temporal_interpretation_validated'])
            self.assertTrue(result['limitations'])

    def test_bad_shapes_booleans_and_unknown_context_are_blocked(self):
        for bank in (None, [], {'cases': [None]}, {'cases': 'x'}, {'cases': []}):
            self.assertTrue(validate_bank(bank)['errors'])
        self.case['rights']['authorized'] = 'true'
        self.assertTrue(validate_bank(self.bank)['errors'])
        self.case['rights']['authorized'] = True
        self.case['context']['notes'] = 'revealed diagnosis'
        self.assertTrue(validate_bank(self.bank)['errors'])

    def test_synthetic_bank_cannot_produce_diagnostic_metrics(self):
        report = evaluate(self.bank, {'dataset_class': 'blinded_accuracy', 'cases': []}, self.root)
        self.assertIsNone(report['metrics'])
        self.assertTrue(report['errors'])

    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'local media tools required')
    def test_video_duration_decode_sampling_and_full_privacy_gate(self):
        subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i',
                        'testsrc=size=64x48:rate=5', '-t', '1', '-c:v', 'mpeg4',
                        '-an', str(self.root / 'asset-002.mp4')], check=True, timeout=20,
                       capture_output=True)
        payload = (self.root / 'asset-002.mp4').read_bytes()
        asset = dict(id='asset-002', path='asset-002.mp4', size_bytes=len(payload),
                     sha256=hashlib.sha256(payload).hexdigest(), derivative=False)
        result = inspect_media(self.root, asset)
        self.assertEqual(result['errors'], [])
        self.assertAlmostEqual(result['duration_seconds'], 1, places=1)
        self.assertEqual(result['decoded_frames'], 5)
        self.assertTrue(inspect_media(self.root, asset, max_duration=0.5)['errors'])
        frames = extract_navigation_frames(self.root, asset, self.root / 'frames', count=3)
        self.assertEqual(len(frames['frames']), 3)
        self.assertEqual([x['sequence_index'] for x in frames['frames']], [0, 1, 2])
        self.assertEqual([x['source_frame_index'] for x in frames['frames']], [0, 2, 4])
        self.assertFalse(frames['temporal_interpretation_validated'])
        self.case.update(assets=[asset], modality='pocus', task_id='pocus_video_navigation')
        self.case['privacy']['reviewed_sha256'] = [asset['sha256']]
        self.assertTrue(blinded_inputs(self.bank, self.root) == [])
        with self.assertRaisesRegex(ValueError, '^full_video_privacy_review_required$'):
            admitted_inputs(self.bank, self.root, 'development')
        self.case['privacy']['full_video_reviewed'] = True
        self.assertEqual(len(admitted_inputs(self.bank, self.root, 'development')), 1)
        self.real_blind()
        with self.assertRaisesRegex(ValueError, '^blind_video_not_supported$'):
            blinded_inputs(self.bank, self.root)

    def test_json_boundary_rejects_duplicate_keys_and_nonfinite_numbers(self):
        path = self.root / 'synthetic.json'
        for text in ('{"split":"blind_test","split":"development"}',
                     '{"nested":{"reviewed":false,"reviewed":true}}',
                     '{"extra":NaN}', '{"extra":Infinity}', '{"extra":-Infinity}',
                     '{"extra":1e999}', '{"extra":1e-999}'):
            path.write_text(text, encoding='utf-8')
            with self.subTest(text=text), self.assertRaises(ValueError):
                cli._read(path)
        path.write_text('{"number":0.1,"zero":0,"integer":42}', encoding='utf-8')
        self.assertEqual(cli._read(path), {'number': 0.1, 'zero': 0, 'integer': 42})

    def test_json_boundary_requires_a_bounded_object_and_cli_does_not_echo_input(self):
        path = self.root / 'synthetic-boundary.json'
        for raw in (b'[]', b'null', b'"SYNTHETIC-NO-ECHO"', b' ' * (8 * 1024 * 1024 + 1)):
            path.write_bytes(raw)
            with self.subTest(length=len(raw)), self.assertRaises(ValueError):
                cli._read(path)
        path.write_text('{"SYNTHETIC-NO-ECHO":NaN}', encoding='utf-8')
        proc = subprocess.run([sys.executable, str(Path(cli.__file__)), 'validate-bank', str(path)],
                              capture_output=True, text=True, timeout=10)
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(json.loads(proc.stdout)['errors'], ['operation_blocked'])
        self.assertNotIn('SYNTHETIC-NO-ECHO', proc.stdout + proc.stderr)

    def test_freeze_receipt_rejects_duplicate_keys_even_with_matching_anchor(self):
        dataset = self.evaluation_fixture()
        path = self.root / 'freeze.json'
        raw = path.read_bytes()
        # Duplicate an identical field: digest matches, semantic ambiguity must still fail.
        raw = raw.replace(b'"schema_version": "1.0"', b'"schema_version": "1.0", "schema_version": "1.0"')
        self.assertNotEqual(raw, path.read_bytes())
        path.write_bytes(raw)
        self.freeze_digest = hashlib.sha256(raw).hexdigest()
        self.assertIn('freeze_receipt_or_external_anchor_not_verified', self.evaluate_fixture(dataset)['errors'])

    def evaluation_fixture(self):
        """Declared-real contracts with artificial pixels exercise gates only."""
        self.real_blind()
        second = copy.deepcopy(self.case)
        Image.new('RGB', (32, 24), (200, 50, 10)).save(self.root / 'asset-002.png')
        payload = (self.root / 'asset-002.png').read_bytes()
        second.update(id='case-002', patient_group_id='patient-002', study_group_id='study-002',
                      source_group_id='source-002')
        second['assets'] = [dict(id='asset-002', path='asset-002.png', size_bytes=len(payload),
                                 sha256=hashlib.sha256(payload).hexdigest(), derivative=False)]
        second['privacy']['reviewed_sha256'] = [second['assets'][0]['sha256']]
        self.bank['cases'].append(second)
        dataset = dict(schema_version='1.1', dataset_class='blinded_accuracy', authorized=True,
                       deidentified=True, protocol_prespecified=True, independent_reference=True,
                       modality='ecg', target_condition='fixture-target', target_question='Fixture?',
                       reference_standard=dict(type='independent_expert_reference'),
                       run=dict(model_version='fixture-v0', prompt_version='fixture-v0',
                                preprocessing_version='fixture-v0', protocol_sha256='1' * 64,
                                rubric_id='fixture-rubric'), cases=[])
        for i, row in enumerate(self.bank['cases']):
            dataset['cases'].append(dict(id=row['id'], patient_uid_hash=row['patient_group_id'],
                study_uid_hash=row['study_group_id'],
                evaluation=dict(mode='blinded', annotated=False, prediction_frozen=True,
                    reference_revealed_after_prediction=True,
                    prediction_frozen_at='2026-11-16T00:01:00Z', reference_revealed_at='2026-11-16T00:02:00Z'),
                prediction=dict(class_='unused', **{'class': 'positive' if i == 0 else 'negative'},
                                timestamp='2026-11-16T00:00:00Z'),
                reference=dict(target_positive=i == 0, source_id='fixture-reference', reviewer_id='reader-001'),
                safety=dict(reviewed=True, reviewer_id='reader-002', critical_error=False, rubric_id='fixture-rubric')))
        protocol = self.root / 'protocol.json'
        protocol.write_text('{"purpose":"software fixture only"}', encoding='utf-8')
        dataset['run']['protocol_sha256'] = hashlib.sha256(protocol.read_bytes()).hexdigest()
        receipt = dict(schema_version='1.0', run=dataset['run'],
            frozen_at='2026-11-16T00:01:00Z', protocol_file='protocol.json',
            inputs_sha256=hashlib.sha256(json.dumps(blinded_inputs(self.bank, self.root),
                sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
            predictions=[{k: c[k] for k in ('id', 'prediction')} for c in dataset['cases']])
        raw = json.dumps(receipt, sort_keys=True).encode()
        (self.root / 'freeze.json').write_bytes(raw)
        self.freeze_digest = hashlib.sha256(raw).hexdigest()
        dataset['freeze_receipt_file'] = 'freeze.json'
        return dataset

    def evaluate_fixture(self, dataset):
        return evaluate(self.bank, dataset, self.root, freeze_sha256=self.freeze_digest)

    def test_metric_bridge_reuses_canonical_counts_and_human_critical_review(self):
        dataset = self.evaluation_fixture()
        dataset['cases'][0]['safety']['critical_error'] = True
        result = self.evaluate_fixture(dataset)
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['metrics']['n'], 2)
        self.assertEqual(result['metrics']['tp'], 1)
        self.assertEqual(result['critical_errors']['count'], 1)
        self.assertFalse(result['diagnostic_validation'])

    def test_abstention_suppresses_binary_metrics_but_preserves_coverage(self):
        dataset = self.evaluation_fixture()
        dataset['cases'][0]['prediction']['class'] = 'abstain'
        # This is a distinct frozen run, not editing a result after reveal.
        receipt = json.loads((self.root / 'freeze.json').read_text())
        receipt['predictions'][0]['prediction']['class'] = 'abstain'
        raw = json.dumps(receipt, sort_keys=True).encode()
        (self.root / 'freeze.json').write_bytes(raw)
        self.freeze_digest = hashlib.sha256(raw).hexdigest()
        result = self.evaluate_fixture(dataset)
        self.assertEqual(result['errors'], [])
        self.assertIsNone(result['metrics']['sensitivity'])
        self.assertEqual(result['metrics']['coverage'], 0.5)
        self.assertEqual(result['metrics']['abstention_rate'], 0.5)

    def test_metrics_reject_wrong_cases_invalid_reference_and_unreviewed_safety(self):
        dataset = self.evaluation_fixture()
        for key, value in [('patient_uid_hash', 'other-patient'), ('reference', {'target_positive': 'false'}),
                           ('safety', {'reviewed': False}), ('prediction', {'class': 'negative'})]:
            test = copy.deepcopy(dataset)
            test['cases'][0][key] = value
            result = self.evaluate_fixture(test)
            self.assertTrue(result['errors'])
            self.assertIsNone(result['metrics'])

    def test_metrics_require_versions_timezone_order_both_classes_and_complete_cohort(self):
        dataset = self.evaluation_fixture()
        tests = []
        missing_version = copy.deepcopy(dataset)
        missing_version['run'].pop('model_version')
        tests.append(missing_version)
        naive_time = copy.deepcopy(dataset)
        naive_time['cases'][0]['prediction']['timestamp'] = '2026-11-16T00:00:00'
        tests.append(naive_time)
        after_reveal = copy.deepcopy(dataset)
        after_reveal['cases'][0]['prediction']['timestamp'] = '2026-11-16T00:03:00Z'
        tests.append(after_reveal)
        one_class = copy.deepcopy(dataset)
        one_class['cases'][0]['reference']['target_positive'] = False
        tests.append(one_class)
        incomplete = copy.deepcopy(dataset)
        incomplete['cases'].pop()
        tests.append(incomplete)
        for test in tests:
            self.assertTrue(self.evaluate_fixture(test)['errors'])

    def test_duplicate_binary_cannot_inflate_cases_in_one_partition(self):
        second = copy.deepcopy(self.case)
        second.update(id='case-002', patient_group_id='patient-002', study_group_id='study-002',
                      source_group_id='source-002')
        second['assets'][0]['id'] = 'asset-002'
        self.bank['cases'].append(second)
        self.assertTrue(validate_bank(self.bank)['errors'])

    def test_parent_derivative_link_cannot_cross_partition_or_disappear(self):
        self.evaluation_fixture()
        child = self.bank['cases'][1]
        self.case['split'] = 'teaching'
        child['assets'][0].update(derivative=True, parent_sha256=self.asset['sha256'])
        child['lineage_group_id'] = 'lineage-001'
        self.assertTrue(validate_bank(self.bank)['errors'])
        self.bank['cases'].pop(0)
        self.assertTrue(validate_bank(self.bank)['errors'])

    def test_modified_prediction_protocol_or_input_rejects_metrics(self):
        dataset = self.evaluation_fixture()
        changed = copy.deepcopy(dataset)
        changed['cases'][0]['prediction']['class'] = 'negative'
        self.assertTrue(self.evaluate_fixture(changed)['errors'])
        changed = copy.deepcopy(dataset)
        changed['run']['protocol_sha256'] = '0' * 64
        self.assertTrue(self.evaluate_fixture(changed)['errors'])
        self.case['context']['gain_mm_mv'] = 20
        self.assertTrue(self.evaluate_fixture(dataset)['errors'])

    @unittest.skipUnless(shutil.which('ffmpeg'), 'local ffmpeg required')
    def test_matroska_renamed_as_webm_is_rejected(self):
        path = self.root / 'asset-003.webm'
        subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i',
            'testsrc=size=64x48:rate=5', '-t', '1', '-c:v', 'ffv1', '-f', 'matroska', str(path)],
            capture_output=True, check=True, timeout=20)
        raw = path.read_bytes()
        asset = dict(id='asset-003', path=path.name, sha256=hashlib.sha256(raw).hexdigest(),
                     size_bytes=len(raw), derivative=False)
        self.assertTrue(inspect_media(self.root, asset)['errors'])


if __name__ == '__main__':
    unittest.main()
