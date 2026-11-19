"""Test QA orchestration failure handling with synthetic child receipts only.

These tests do not assert that mocked clinical/browser commands were executed;
they assert that the controller preserves evidence and propagates failures.
"""
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import runpy
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]


class ReconciliationControllerIntegrityTests(unittest.TestCase):
    def exercise(self, fault=None):
        module = runpy.run_path(str(ROOT/'clinical/qa/run_product_reconciliation_v144.py'))
        main = module['main']
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); qa = root/'clinical/qa'; scripts = root/'app/scripts'
            qa.mkdir(parents=True); scripts.mkdir(parents=True)
            historical = qa/'SYNTHETIC_BROWSER_RESULTS.json'
            historical.write_text('{"synthetic":true}\n', encoding='utf-8')
            original = historical.read_bytes()
            drivers = {'check-synthetic.mjs': 'SYNTHETIC_BROWSER_RESULTS.json'}
            source = scripts/'check-synthetic.mjs'
            old = '../../clinical/qa/SYNTHETIC_BROWSER_RESULTS.json'
            new = '../../clinical/qa/product-reconciliation-v144/SYNTHETIC_BROWSER_RESULTS.json'
            content = 'const destination = "' + old + '";\n// synthetic assertions remain\n'
            if fault == 'duplicate': content += '// ' + old + '\n'
            if fault == 'ambiguous': content += '// ' + new + '\n'
            source.write_text(content, encoding='utf-8')
            original_source = source.read_bytes()
            copied = scripts/'check-reconciliation-synthetic.mjs'
            if fault == 'existing': copied.write_text('FOREIGN_SYNTHETIC_SENTINEL', encoding='utf-8')
            seen = []
            def child(command, **kwargs):
                seen.append(command)
                if command[0] == 'node':
                    text = copied.read_text(encoding='utf-8')
                    self.assertEqual(text, content.replace(old, new))
                    self.assertEqual(source.read_bytes(), original_source)
                if fault == 'history-changed': historical.write_text('SYNTHETIC_TAMPER', encoding='utf-8')
                code = 7 if fault == 'child-failed' else 0
                return subprocess.CompletedProcess(command, code, 'synthetic-child-receipt', '')
            main.__globals__.update(ROOT=root, OUT=qa/'product-reconciliation-v144', DRIVERS=drivers)
            with patch.dict(os.environ, dict(os.environ)), \
                 patch.object(subprocess, 'check_output', return_value='synthetic-head\n'), \
                 patch.object(subprocess, 'run', side_effect=child), \
                 contextlib.redirect_stdout(io.StringIO()):
                status = main()
            report = json.loads((qa/'product-reconciliation-v144/QA_RESULTS.json').read_text())
            self.assertEqual(source.read_bytes(), original_source)
            self.assertEqual(report['clinical_status'], 'CLINICALLY_PENDING')
            self.assertEqual(report['historical_evidence_hashes'][str(historical.relative_to(root))], hashlib.sha256(original).hexdigest())
            self.assertFalse((qa/'product-reconciliation-v144/QA_RESULTS.json.tmp').exists())
            if fault == 'existing': self.assertEqual(copied.read_text(), 'FOREIGN_SYNTHETIC_SENTINEL')
            else: self.assertFalse(copied.exists())
            if fault != 'history-changed': self.assertEqual(historical.read_bytes(), original)
            return status, report, seen

    def test_controller_copies_only_destination_and_removes_its_private_driver(self):
        status, report, commands = self.exercise()
        self.assertEqual(status, 0)
        self.assertEqual(report['status'], 'PASS')
        self.assertTrue(report['historical_evidence_unchanged'])
        self.assertEqual(len(report['browser_driver_copies']), 1)
        self.assertTrue(any(command[0] == 'node' for command in commands))

    def test_child_failure_is_propagated_and_preservation_still_checked(self):
        status, report, _ = self.exercise('child-failed')
        self.assertEqual(status, 1)
        self.assertEqual(report['status'], 'FAIL')
        self.assertTrue(report['historical_evidence_unchanged'])
        self.assertIn('QA command failed', report['error'])

    def test_tampered_history_prevents_success_even_when_child_exits_zero(self):
        status, report, _ = self.exercise('history-changed')
        self.assertEqual(status, 1)
        self.assertEqual(report['status'], 'FAIL')
        self.assertFalse(report['historical_evidence_unchanged'])

    def test_duplicate_destination_ambiguous_reversal_and_foreign_copy_fail_closed(self):
        for fault in ('duplicate', 'ambiguous', 'existing'):
            with self.subTest(fault=fault):
                status, report, commands = self.exercise(fault)
                self.assertEqual(status, 1)
                self.assertEqual(report['status'], 'FAIL')
                self.assertTrue(report['historical_evidence_unchanged'])
                self.assertFalse(any(command[0] == 'node' for command in commands))


if __name__ == '__main__':
    unittest.main()
