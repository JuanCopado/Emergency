"""Synthetic loopback regressions for the existing API's private process boundary."""
import http.client
import json
from pathlib import Path
import subprocess
import sys
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import clinical_note_api as api  # noqa: E402


class ClinicalHttpBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = api.make_server(ui_port=5173)
        cls.thread = threading.Thread(target=cls.server.serve_forever,
                                      kwargs={"poll_interval": .01}, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.thread.join(2)
        cls.server.server_close()

    def headers(self):
        return [("Host", f"127.0.0.1:{self.server.server_port}"),
                ("Origin", "http://127.0.0.1:5173"),
                ("X-Emergency-Local-Token", self.server.clinical_session_token)]

    def request(self, headers, *, method="POST", path="/api/clinical-note/new"):
        client = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=2)
        try:
            client.putrequest(method, path, skip_host=True)
            for name, value in headers:
                client.putheader(name, value)
            if method == "POST":
                client.putheader("Content-Type", "application/json")
                client.putheader("Content-Length", "2")
            client.endheaders(b"{}" if method == "POST" else None)
            response = client.getresponse()
            return response.status, dict(response.getheaders()), json.loads(response.read())
        finally:
            client.close()

    def test_legitimate_request_reaches_existing_contract(self):
        for origin in ("http://127.0.0.1:5173", "http://localhost:5173"):
            with self.subTest(origin=origin):
                request_headers = self.headers()
                request_headers[1] = ("Origin", origin)
                status, headers, body = self.request(request_headers)
                self.assertEqual(status, 200)
                self.assertEqual(body["schema_version"], "1.0")
                self.assertEqual(headers["Cache-Control"], "no-store")
                self.assertNotIn(self.server.clinical_session_token, json.dumps(body))

    def test_missing_wrong_or_duplicate_credential_never_dispatch(self):
        original = self.headers()
        cases = [original[:2], [*original[:2], (original[2][0], "0" * 64)],
                 [*original, original[2]]]
        with patch.object(api, "dispatch") as dispatch:
            for headers in cases:
                with self.subTest(headers=[name for name, _ in headers]):
                    self.assertEqual(self.request(headers)[0], 401)
            dispatch.assert_not_called()

    def test_foreign_missing_and_duplicate_origins_or_hosts_are_rejected(self):
        headers = self.headers()
        cases = [
            [("Host", "attacker.invalid"), *headers[1:]],
            [headers[0], ("Origin", "https://attacker.invalid"), headers[2]],
            [headers[0], ("Origin", "null"), headers[2]],
            [headers[0], ("Origin", "http://localhost.attacker.invalid:5173"), headers[2]],
            [headers[0], ("Origin", "http://127.0.0.1:5173.attacker.invalid"), headers[2]],
            [headers[0], headers[2]], [*headers, headers[0]], [*headers, headers[1]],
            [*headers, ("Sec-Fetch-Site", "cross-site")],
            [*headers, ("Sec-Fetch-Site", "same-origin"), ("Sec-Fetch-Site", "same-origin")],
            [headers[0], ("Origin", "https://attacker.invalid"), headers[2],
             ("X-Forwarded-Host", "127.0.0.1:5173"), ("X-Forwarded-For", "127.0.0.1")],
        ]
        with patch.object(api, "dispatch") as dispatch:
            for index, candidate in enumerate(cases):
                with self.subTest(case=index):
                    self.assertEqual(self.request(candidate)[0], 403)
            dispatch.assert_not_called()

    def test_all_existing_post_families_require_credential_before_dispatch(self):
        paths = ["/api/clinical-note/upload/prepare", "/api/clinical-note/export",
                 "/api/acute-medications/calculate", "/api/acute-medications/export",
                 "/api/pediatric-outpatient/calculate", "/api/pediatric-outpatient/export",
                 "/api/clinical-scores/calculate", "/api/clinical-scores/catalog"]
        with patch.object(api, "dispatch") as dispatch:
            for path in paths:
                with self.subTest(path=path):
                    self.assertEqual(self.request(self.headers()[:2], path=path)[0], 401)
            dispatch.assert_not_called()

    def test_health_is_minimal_origin_checked_and_does_not_issue_credentials(self):
        status, headers, body = self.request(self.headers()[:1], method="GET", path="/api/clinical-note/health")
        self.assertEqual(status, 200)
        self.assertEqual(body, {"status": "ok", "api_version": "1.0"})
        self.assertEqual(headers["Cache-Control"], "no-store")
        for candidate in [[("Host", "attacker.invalid")],
                          [self.headers()[0], ("Origin", "https://attacker.invalid")]]:
            self.assertEqual(self.request(candidate, method="GET", path="/api/clinical-note/health")[0], 403)

    def test_direct_network_mode_is_rejected_before_binding_or_reading_tls_files(self):
        with self.assertRaisesRegex(ValueError, "Direct network exposure"):
            api.make_server(host="0.0.0.0")
        result = subprocess.run([sys.executable, str(SCRIPTS / "clinical_note_api.py"),
                                 "--allow-network", "--tls-cert", "unused", "--tls-key", "unused"],
                                capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 2)
        self.assertIn("Direct network exposure is disabled", result.stderr)

    def test_boundary_configuration_rejects_nonloopback_server_addresses(self):
        for host in ("0.0.0.0", "192.0.2.1", "::", "::ffff:192.0.2.1"):
            with self.subTest(host=host), self.assertRaisesRegex(ValueError, "loopback bind"):
                api.configure_local_server(SimpleNamespace(server_address=(host, 8765)))

    def test_boundary_configuration_rejects_invalid_ui_ports(self):
        for port in (True, 0, -1, 65536, 5173.0, "5173", "5173@attacker.invalid"):
            with self.subTest(port=port), self.assertRaisesRegex(ValueError, "UI port"):
                api.make_server(ui_port=port)

    def test_boundary_configuration_rejects_malformed_session_credentials(self):
        for token in (True, 123, b"a" * 64, "", "a" * 63, "g" * 64, "a" * 64 + "\n"):
            with self.subTest(type=type(token).__name__), self.assertRaisesRegex(ValueError, "256-bit"):
                api.make_server(session_token=token)


if __name__ == "__main__":
    unittest.main()
