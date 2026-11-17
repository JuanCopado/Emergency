"""Security regressions for the isolated GitHub Actions report writer."""
import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/security/report.py"
SPEC = importlib.util.spec_from_file_location("security_report", SCRIPT)
REPORT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REPORT)


class BoundedReportPathsTests(unittest.TestCase):
    def run_with_temp(self, root, tool="trivy", *extra_args, env_override=None):
        env = os.environ.copy()
        env.pop("GITHUB_STEP_SUMMARY", None)
        env["RUNNER_TEMP"] = str(root)
        if env_override:
            env.update(env_override)
        return subprocess.run([sys.executable, str(SCRIPT), tool, "--check", *extra_args],
                              env=env, capture_output=True, text=True, check=False)

    @staticmethod
    def make_trivy(security_dir, severity="MEDIUM"):
        security_dir.mkdir(parents=True, exist_ok=True)
        data = {"SchemaVersion": 2, "Results": [{
            "Target": "app/package-lock.json", "Vulnerabilities": [{
                "VulnerabilityID": "CVE-SYNTHETIC", "PkgName": "synthetic",
                "InstalledVersion": "0.1", "Severity": severity,
                "Description": "PRIVATE_SENTINEL", "Title": "PRIVATE_SENTINEL"}]}]}
        (security_dir / "trivy.raw.json").write_text(json.dumps(data))
        return data

    def test_normal_scan_reports_only_metadata_and_is_mode_600(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_trivy(root / "security")
            result = self.run_with_temp(root)
            self.assertEqual(result.returncode, 0, result.stderr)
            output = root / "security/trivy.summary.json"
            self.assertTrue(output.exists())
            report = json.loads(output.read_text())
            self.assertEqual(report["status"], "PASS")
            self.assertEqual(report["findings"][0]["rule"], "CVE-SYNTHETIC")
            self.assertNotIn("PRIVATE_SENTINEL", output.read_text())
            if os.name == "posix":
                self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o600)
                self.assertEqual(stat.S_IMODE((root / "security").stat().st_mode), 0o700)

    def test_high_issue_still_blocks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_trivy(root / "security", "HIGH")
            result = self.run_with_temp(root)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(json.loads((root / "security/trivy.summary.json").read_text())["status"], "FINDINGS")

    def test_missing_required_target_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_trivy(root / "security")
            result = self.run_with_temp(root, "trivy", "--require-target", "clinical/requirements.txt")
            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads((root / "security/trivy.summary.json").read_text())["status"], "ERROR")

    def test_old_arbitrary_cli_paths_are_not_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_trivy(root / "security")
            outside = root / "do-not-write.txt"
            outside.write_text("PRIVATE_SENTINEL")
            result = self.run_with_temp(root, "trivy", str(outside), str(outside))
            self.assertEqual(result.returncode, 2)
            self.assertEqual(outside.read_text(), "PRIVATE_SENTINEL")
            self.assertFalse((root / "security/trivy.summary.json").exists())

    def test_missing_runner_temp_fails_closed(self):
        env = os.environ.copy()
        env.pop("RUNNER_TEMP", None)
        env.pop("GITHUB_STEP_SUMMARY", None)
        result = subprocess.run([sys.executable, str(SCRIPT), "trivy", "--check"],
                                capture_output=True, text=True, check=False, env=env)
        self.assertEqual(result.returncode, 2)
        self.assertIn("ERROR", result.stdout)

    def test_relative_runner_temp_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_with_temp(Path(directory), "trivy", env_override={"RUNNER_TEMP": "../untrusted"})
            self.assertEqual(result.returncode, 2)

    @unittest.skipUnless(hasattr(os, "symlink"), "requires symlink support")
    def test_symlinked_raw_cannot_read_unrelated_private_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            security = root / "security"
            security.mkdir()
            private = root / "private.txt"
            private.write_text("PRIVATE_SENTINEL")
            try:
                (security / "trivy.raw.json").symlink_to(private)
            except OSError:
                self.skipTest("symlink creation is unavailable")
            result = self.run_with_temp(root)
            self.assertEqual(result.returncode, 2)
            self.assertNotIn("PRIVATE_SENTINEL", result.stdout + result.stderr)
            self.assertFalse((security / "trivy.summary.json").exists())

    @unittest.skipUnless(hasattr(os, "symlink"), "requires symlink support")
    def test_symlinked_output_does_not_overwrite_external_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            security = root / "security"
            self.make_trivy(security)
            private = root / "private.txt"
            private.write_text("PRIVATE_SENTINEL")
            try:
                (security / "trivy.summary.json").symlink_to(private)
            except OSError:
                self.skipTest("symlink creation is unavailable")
            result = self.run_with_temp(root)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(private.read_text(), "PRIVATE_SENTINEL")

    @unittest.skipUnless(hasattr(os, "symlink"), "requires symlink support")
    def test_symlinked_reports_directory_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            elsewhere = root / "elsewhere"
            self.make_trivy(elsewhere)
            try:
                (root / "security").symlink_to(elsewhere, target_is_directory=True)
            except OSError:
                self.skipTest("symlink creation is unavailable")
            result = self.run_with_temp(root)
            self.assertEqual(result.returncode, 2)
            self.assertFalse((elsewhere / "trivy.summary.json").exists())

    def test_oversized_input_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "large.json"
            path.write_text('{"data": "untrusted"}')
            previous = REPORT.MAX_RAW_REPORT_BYTES
            try:
                REPORT.MAX_RAW_REPORT_BYTES = 10
                with self.assertRaises(ValueError):
                    REPORT._load_scan(path)
            finally:
                REPORT.MAX_RAW_REPORT_BYTES = previous

    def test_malformed_json_fails_closed_with_no_sensitive_payload(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            p = root / "security/trivy.raw.json"
            p.parent.mkdir()
            p.write_text('{"x":"PRIVATE_SENTINEL", bad:inf}')
            result = self.run_with_temp(root)
            self.assertEqual(result.returncode, 2)
            output = (root / "security/trivy.summary.json").read_text()
            self.assertNotIn("PRIVATE_SENTINEL", output)
            self.assertEqual(json.loads(output)["status"], "ERROR")


if __name__ == "__main__":
    unittest.main()
