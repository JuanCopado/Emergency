"""M10 reports describe a single run and include unsuccessful subtests."""
import io
import json
from contextlib import redirect_stdout, redirect_stderr
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import run_m10_image_audit as audit


class TestAuditReport(unittest.TestCase):
    def test_reports_two_distinct_runs_and_counts_subtests(self):
        class Sample(unittest.TestCase):
            def test_pass(self):
                self.assertTrue(True)

            def test_failure(self):
                self.fail("synthetic failure")

            def test_error(self):
                raise ValueError("synthetic error")

            def test_skip(self):
                self.skipTest("synthetic skip")

            def test_subcases(self):
                with self.subTest(mode="unexpected result"):
                    self.fail("synthetic subtest failure")
                with self.subTest(mode="unavailable result"):
                    raise ValueError("synthetic subtest error")

        cases = unittest.defaultTestLoader.loadTestsFromTestCase(Sample)
        fresh = unittest.TestSuite([Sample("test_pass")])
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / "m10.json"
            with (patch.object(unittest.defaultTestLoader, "loadTestsFromName", side_effect=[cases, fresh]),
                  patch.object(audit, "CURRENT_REPORT", out)):
                self.assertEqual(audit.main(["--write-current"]), 1)
                failed = json.loads(out.read_text(encoding="utf8"))
                with redirect_stdout(io.StringIO()) as stream:
                    self.assertEqual(audit.main([]), 0)
                passed = json.loads(stream.getvalue())
                self.assertEqual(json.loads(out.read_text(encoding="utf8")), failed)

        self.assertEqual(failed["totals"], {"run": 5, "failures": 2, "errors": 2, "skipped": 1})
        self.assertCountEqual([row["status"] for row in failed["tests"]],
                              ["PASS", "FAIL", "ERROR", "SKIP", "FAIL", "ERROR"])
        self.assertEqual(passed["totals"], {"run": 1, "failures": 0, "errors": 0, "skipped": 0})
        self.assertEqual([row["status"] for row in passed["tests"]], ["PASS"])
        self.assertTrue(all(len(digest) == 64 for digest in passed["files_sha256"].values()))
        self.assertIn("CLINICALLY_PENDING", passed["validation_status"])


    def test_unrecognized_output_is_rejected_before_running_or_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "other.json"
            with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                audit.main([str(destination)])
            self.assertEqual(error.exception.code, 2)
            self.assertFalse(destination.exists())
