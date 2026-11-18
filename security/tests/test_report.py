"""Adversarial checks for public reports and failure propagation."""
import importlib.util
import json
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

    def test_all_required_targets_must_exist(self):
        result = subprocess.run([sys.executable, str(SCRIPT), "trivy", "--check", "--require-target", "missing"],
                                input=json.dumps({"SchemaVersion": 2, "Results": []}), capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["status"], "ERROR")

    def test_invalid_json_does_not_echo_input(self):
        result = subprocess.run([sys.executable, str(SCRIPT), "trivy", "--check"],
                                input="{PRIVATE_SENTINEL", capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertNotIn("PRIVATE_SENTINEL", result.stdout + result.stderr)

    def test_paths_and_baseline_override_are_not_cli_capabilities(self):
        with tempfile.TemporaryDirectory() as directory:
            outside = Path(directory) / "must-remain-untouched.json"
            outside.write_text("PRIVATE_SENTINEL")
            for args in [[str(outside), str(outside)], ["--baseline", str(outside)],
                         ["../escape.json", "../escape.json"], ["C:\\outside.json", "C:\\outside.json"]]:
                with self.subTest(args=args):
                    result = subprocess.run([sys.executable, str(SCRIPT), "trivy", *args],
                                            input="{}", capture_output=True, text=True)
                    self.assertEqual(result.returncode, 2)
                    self.assertEqual(result.stdout, "")
                    self.assertEqual(outside.read_text(), "PRIVATE_SENTINEL")

    def test_stdout_is_only_valid_allowlisted_json(self):
        result = self.run_report("trivy", {"SchemaVersion": 2, "Results": []})
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["findings"], [])
        self.assertIn("trivy: PASS", result.stderr)

    def test_trivy_severity_is_required_and_valid_for_every_finding_kind(self):
        for key, item in [("Vulnerabilities", {"VulnerabilityID": "CVE-TEST", "PkgName": "synthetic", "InstalledVersion": "0"}),
                          ("Secrets", {"RuleID": "synthetic"}),
                          ("Misconfigurations", {"ID": "synthetic"})]:
            for severity in [None, "", "high", "TYPO", 42, []]:
                with self.subTest(kind=key, severity=severity):
                    finding = dict(item)
                    if severity is not None:
                        finding["Severity"] = severity
                    data = {"SchemaVersion": 2, "Results": [{"Target": "synthetic", key: [finding]}]}
                    self.assertEqual(self.run_report("trivy", data).returncode, 2)
        explicit_unknown = {"SchemaVersion": 2, "Results": [{"Target": "synthetic", "Vulnerabilities": [{
            "VulnerabilityID": "CVE-TEST", "PkgName": "synthetic", "InstalledVersion": "0", "Severity": "UNKNOWN"}]}]}
        self.assertEqual(self.run_report("trivy", explicit_unknown).returncode, 0)

    @staticmethod
    def run_report(tool, data):
        return subprocess.run([sys.executable, str(SCRIPT), tool, "--check"],
                              input=json.dumps(data), capture_output=True, text=True, check=False)



if __name__ == "__main__":
    unittest.main()
