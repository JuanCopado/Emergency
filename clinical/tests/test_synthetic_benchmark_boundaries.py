"""Offline PTB-XL plumbing and label-separation tests using fabricated signals.

CI installs hash-locked extras and requires execution. Optional local hosts can
skip the class when those scientific wheels are not installed. No patient files,
PhysioNet downloads, or network calls are used by these tests.
"""
import csv
import importlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
try:
    benchmark = importlib.import_module('build_ptbxl_blinded_benchmark')
except ModuleNotFoundError as exc:
    if exc.name not in {'numpy', 'matplotlib', 'wfdb'} or os.getenv('EMERGENCY_REQUIRE_BENCHMARK_TESTS') == '1':
        raise
    benchmark = None


@unittest.skipIf(benchmark is None, 'Scientific wheels required; mandatory in Linux security coverage CI')
class SyntheticBenchmarkBoundaryTests(unittest.TestCase):
    SALT = 'synthetic-fixture-salt-only'

    def write_csv(self, directory, rows=None):
        rows = rows if rows is not None else [
            {'ecg_id': str(i), 'patient_id': f'SYNTHETIC-{i}', 'strat_fold': '10',
             'scp_codes': "{'SYNTHETIC': 100}" if i % 2 else "{'OTHER': 100}",
             'filename_lr': f'records100/synthetic-{i}'} for i in range(1, 5)]
        file = directory/'input.csv'
        with file.open('w', newline='', encoding='utf-8') as stream:
            writer = csv.DictWriter(stream, fieldnames=['ecg_id', 'patient_id', 'strat_fold', 'scp_codes', 'filename_lr'])
            writer.writeheader(); writer.writerows(rows)
        return file

    def synthetic_download(self, row, case_id, directory):
        record = directory/case_id/'fabricated'
        record.parent.mkdir(parents=True)
        return case_id, record

    def synthetic_render(self, record, output):
        from PIL import Image
        Image.new('RGB', (16, 16), 'white').save(output)
        return str(output)

    def test_manifest_and_sealed_reference_remain_separate_for_every_selection_mode(self):
        # Real selection, hashing, scheduling, manifest writing and image files;
        # only network input and costly rendering are replaced by synthetic I/O.
        modes = ({}, {'natural_limit': 3}, {'natural_limit': 10},
                 {'pilot_per_class': 1}, {'max_cases': 3})
        for options in modes:
            with self.subTest(options=options), tempfile.TemporaryDirectory() as td:
                directory = Path(td); database = self.write_csv(directory); output = directory/'output'
                with patch.object(benchmark, '_download_case_files', side_effect=self.synthetic_download), \
                     patch.object(benchmark, '_render_case', side_effect=self.synthetic_render), \
                     patch.object(benchmark, 'ProcessPoolExecutor', ThreadPoolExecutor), \
                     patch.object(benchmark.urllib.request, 'urlopen', side_effect=AssertionError('Network forbidden')):
                    benchmark.build(database, 'SYNTHETIC', self.SALT, output, **options)
                public = json.loads((output/'blinded_manifest.json').read_text())
                sealed = json.loads((output/'SEALED_REFERENCE_DO_NOT_REVEAL.json').read_text())
                self.assertEqual(len(public['cases']), sealed['case_count'])
                self.assertTrue(sealed['positive_reference_cases'])
                self.assertTrue(sealed['negative_reference_cases'])
                self.assertEqual({c['id'] for c in public['cases']}, {r['id'] for r in sealed['references']})
                self.assertNotIn('SYNTHETIC-1', json.dumps(public))
                for case in public['cases']:
                    self.assertNotIn('target_positive', case)
                    self.assertNotIn('source_patient_id', case)
                    self.assertFalse(case['evaluation']['annotated'])
                    self.assertFalse(case['evaluation']['prediction_frozen'])
                    self.assertTrue((output/case['image_file']).is_file())
                pilot = bool(options.get('max_cases') or options.get('pilot_per_class'))
                self.assertEqual(public['performance_metrics_allowed'], not pilot)
                self.assertFalse(public['metrics_requested'])

    def test_invalid_selection_contracts_fail_without_network_or_render(self):
        with tempfile.TemporaryDirectory() as td:
            directory = Path(td); database = self.write_csv(directory)
            for target, salt, options in (('', self.SALT, {}), ('SYNTHETIC', 'short', {}),
                    ('SYNTHETIC', self.SALT, {'fold': 9}),
                    ('SYNTHETIC', self.SALT, {'pilot_per_class': 3}),
                    ('SYNTHETIC', self.SALT, {'max_cases': 2}),
                    ('ABSENT', self.SALT, {})):
                with self.subTest(target=target, options=options), \
                     patch.object(benchmark, '_download_case_files') as download, \
                     patch.object(benchmark, '_render_case') as render:
                    with self.assertRaises(ValueError):
                        benchmark.build(database, target, salt, directory/'out', **options)
                    download.assert_not_called(); render.assert_not_called()
            database.write_text('unexpected\nvalue\n', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'missing PTB-XL columns'):
                benchmark.build(database, 'SYNTHETIC', self.SALT, directory/'out')

    def test_download_fallback_is_bounded_and_reports_failure(self):
        with tempfile.TemporaryDirectory() as td:
            output = Path(td)/'nested/synthetic.dat'
            with patch.object(benchmark.urllib.request, 'urlopen', side_effect=[OSError('synthetic'), io.BytesIO(b'fabricated')]) as request:
                benchmark._download(['https://first.invalid/x', 'https://second.invalid/x'], output)
                self.assertEqual(request.call_count, 2)
                self.assertEqual(output.read_bytes(), b'fabricated')
                self.assertEqual(request.call_args.kwargs['timeout'], 30)
            with patch.object(benchmark.urllib.request, 'urlopen', side_effect=OSError('synthetic')):
                with self.assertRaisesRegex(RuntimeError, 'all PTB-XL download mirrors failed'):
                    benchmark._download(['https://offline.invalid/x'], output)

    def test_record_paths_use_only_basename_inside_private_case_directory(self):
        with tempfile.TemporaryDirectory() as td, patch.object(benchmark, '_download') as download:
            case_id, record = benchmark._download_case_files({'filename_lr': 'records100/synthetic'}, 'blinded-1', Path(td))
            self.assertEqual(case_id, 'blinded-1')
            self.assertEqual(record, Path(td)/'blinded-1/synthetic')
            self.assertEqual(download.call_count, 2)
            for call in download.call_args_list:
                self.assertTrue(str(call.args[1]).startswith(str(Path(td))))
                self.assertTrue(all(url.startswith(benchmark.BASE_URLS) for url in call.args[0]))

    def test_metadata_parser_never_evaluates_python_code(self):
        self.assertEqual(benchmark._parse_codes("{'SYNTHETIC': 100}"), {'SYNTHETIC': 100})
        for raw in ('[]', "__import__('os').getcwd()", 'broken{'):
            with self.subTest(raw=raw), self.assertRaises((ValueError, SyntaxError)):
                benchmark._parse_codes(raw)
        self.assertNotEqual(benchmark._hash('synthetic-id', 'one'), benchmark._hash('synthetic-id', 'two'))

    def test_renderer_creates_png_from_fabricated_zero_signal_and_rejects_wrong_layout(self):
        import numpy as np
        from PIL import Image
        record = SimpleNamespace(fs=100, sig_name=benchmark.LEADS,
                                 p_signal=np.zeros((1000, 12), dtype=float))
        with tempfile.TemporaryDirectory() as td, patch.object(benchmark.wfdb, 'rdrecord', return_value=record):
            output = Path(td)/'synthetic.png'
            self.assertEqual(benchmark._render_case(Path(td)/'synthetic-record', output), str(output))
            with Image.open(output) as rendered:
                self.assertEqual(rendered.format, 'PNG')
                self.assertGreater(rendered.width, 1000)
                self.assertGreater(rendered.height, 1000)
            record.fs = 250
            with self.assertRaisesRegex(ValueError, 'expected 100 Hz'):
                benchmark._render_standard('synthetic', output)
            record.fs = 100; record.sig_name = ['I']
            with self.assertRaisesRegex(ValueError, 'missing leads'):
                benchmark._render_standard('synthetic', output)


if __name__ == '__main__':
    unittest.main()
