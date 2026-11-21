"""Regression of the offline study's source identity and non-mutating observer."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "clinical/scripts/run_r5_note_shadow_study.py"


class OfflineShadowStudy(unittest.TestCase):
    def run_study(self, output, tree=None):
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        if tree is None:
            tree = subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT, text=True).strip()
        return subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "--repo", str(ROOT), "--commit", commit,
             "--tree", tree, "--output", str(output)],
            # Measured CI instrumentation exceeded 90s for the full 153-case bank.
            cwd=ROOT, capture_output=True, text=True, timeout=240, check=False)

    def test_full_study_preserves_accepted_outputs_and_is_offline(self):
        with tempfile.TemporaryDirectory(prefix="r5-study-test-") as folder:
            output = Path(folder) / "study"
            process = self.run_study(output)
            self.assertEqual(process.returncode, 0, process.stderr[-2000:])
            report = json.loads((output / "study.json").read_text(encoding="utf8"))
            self.assertEqual(report["synthetic_cases"], 153)
            self.assertEqual(report["frozen_cases"], 60)
            self.assertEqual(report["outputs_unchanged"], 153)
            self.assertEqual(report["full_outputs_digest"],
                             "b3e9aede69db36ca2ebda3018c76719ca3e8a2be7f0bddbe3c9f4ff5802fbfa1")
            self.assertEqual(report["status"], "CLINICALLY_PENDING")
            self.assertEqual(sum(r["shadow_observer"]["review_priority_candidate_offline_only"]
                                 for r in report["records"]), 7)
            for record in report["records"]:
                self.assertEqual(record["before"], record["after"], record["case"])
            rejected = self.run_study(output)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("Output already exists", rejected.stderr)

    def test_wrong_tree_and_repository_output_are_rejected(self):
        with tempfile.TemporaryDirectory(prefix="r5-study-test-") as folder:
            output = Path(folder) / "study"
            rejected = self.run_study(output, tree="0" * 40)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("Tree identity mismatch", rejected.stderr)
            self.assertFalse(output.exists())
        rejected = self.run_study(ROOT / "not-created-by-r5-study")
        self.assertNotEqual(rejected.returncode, 0)
        self.assertIn("Output must be outside", rejected.stderr)
        self.assertFalse((ROOT / "not-created-by-r5-study").exists())


if __name__ == "__main__":
    unittest.main()
