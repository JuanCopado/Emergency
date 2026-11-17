"""Adversarial checks for public reports and failure propagation."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/security/report.py"
SPEC = importlib.util.spec_from_file_location("security_report", SCRIPT)
REPORT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REPORT)


class PublicReportTests(unittest.TestCase):
    def test_secret_values_and_context_never_exported(self):
        data = {"SchemaVersion": 2, "Results": [{"Target": "example.txt", "Secrets": [{
            "RuleID": "test", "Severity": "LOW", "StartLine": 1,
            "Match": "PRIVATE_SENTINEL", "Code": {"Lines": ["PRIVATE_SENTINEL"]},
            "Title": "PRIVATE_SENTINEL"}]}]}
        findings = REPORT.collect("trivy", data)
        self.assertNotIn("PRIVATE_SENTINEL", json.dumps(findings))
        result = self.run_report("trivy", data)
        self.assertEqual(result.returncode, 1, "Every secret must block, including LOW")

    def test_semgrep_code_and_message_never_exported(self):
        data = {"results": [{"check_id": "rule", "path": "app/example.ts", "start": {"line": 2},
                "extra": {"severity": "ERROR", "lines": "PRIVATE_SENTINEL",
                          "message": "PRIVATE_SENTINEL", "metadata": {"secret": "PRIVATE_SENTINEL"}}}], "errors": []}
        self.assertNotIn("PRIVATE_SENTINEL", json.dumps(REPORT.collect("semgrep", data)))
        self.assertEqual(self.run_report("semgrep", data).returncode, 1)

    def test_errors_and_malformed_reports_fail(self):
        self.assertEqual(self.run_report("semgrep", {"results": [], "errors": [{"message": "error"}]}).returncode, 2)
        self.assertEqual(self.run_report("trivy", {}).returncode, 2)

    def test_lower_vulnerabilities_are_visible_without_blocking(self):
        data = {"SchemaVersion": 2, "Results": [{"Target": "app/package-lock.json", "Vulnerabilities": [{
            "VulnerabilityID": "CVE-TEST", "PkgName": "example", "InstalledVersion": "1", "Severity": "MEDIUM"}]}]}
        self.assertEqual(self.run_report("trivy", data).returncode, 0)
        data["Results"][0]["Vulnerabilities"][0]["Severity"] = "HIGH"
        self.assertEqual(self.run_report("trivy", data).returncode, 1)

    @staticmethod
    def run_report(tool, data):
        with tempfile.TemporaryDirectory() as directory:
            security = Path(directory) / "security"
            security.mkdir()
            raw = security / f"{tool}.raw.json"
            raw.write_text(json.dumps(data))
            environment = {**os.environ, "RUNNER_TEMP": directory}
            return subprocess.run([sys.executable, str(SCRIPT), tool, "--check"],
                                  capture_output=True, text=True, check=False, env=environment)


if __name__ == "__main__":
    unittest.main()
