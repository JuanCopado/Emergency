"""Focal real HTTP/TLS checks for the composed synthetic loopback adapter."""
from __future__ import annotations

import hashlib
import http.client
import json
from pathlib import Path
import select
import socket
import subprocess
import sys
import tempfile
import time
import unittest


ROOT = Path(__file__).resolve().parent
APP_HEADER = {"X-Emergency-T06-Lab": "synthetic-loopback"}


class ComposedT06Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory(prefix="t06-composed-")
        cls.logs = Path(cls.directory.name)
        cls.stderr = (cls.logs / "server.stderr").open("w+")
        cls.process = subprocess.Popen([
            sys.executable, "-B", str(ROOT / "lab/backend/server.py"),
            "--port", "0", "--ui-port", "5173", "--evidence-dir", str(cls.logs),
        ], stdout=subprocess.PIPE, stderr=cls.stderr, text=True)
        if not select.select([cls.process.stdout], [], [], 10)[0]:
            cls.process.terminate()
            cls.process.wait(timeout=5)
            raise RuntimeError("T06 server did not become ready")
        line = cls.process.stdout.readline()
        if not line:
            cls.stderr.seek(0)
            raise RuntimeError("T06 startup failed: " + cls.stderr.read())
        cls.ready = json.loads(line)
        cls.port = cls.ready["bind"][1]

    @classmethod
    def tearDownClass(cls):
        cls.process.terminate()
        cls.process.wait(timeout=10)
        cls.process.stdout.close()
        cls.stderr.close()
        cls.directory.cleanup()

    def request(self, path, *, headers=None, method="GET"):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=8)
        try:
            connection.request(method, path, headers=APP_HEADER if headers is None else headers)
            response = connection.getresponse()
            return response.status, json.loads(response.read()), dict(response.getheaders())
        finally:
            connection.close()

    def test_recovered_components_remain_byte_identical(self):
        repository = ROOT.parents[1]
        manifest = json.loads((ROOT / "SOURCE_PROVENANCE.json").read_text())
        unchanged = [item for item in manifest["files"] if item["identity_preserved"]]
        self.assertEqual(len(unchanged), 19)
        for item in unchanged:
            with self.subTest(path=item["destination"]):
                self.assertEqual(hashlib.sha256((repository / item["destination"]).read_bytes()).hexdigest(), item["source_sha256"])

    def test_real_r6_b1_tls_success_and_aggregate_unicode_limit(self):
        self.assertEqual(self.ready["bind"][0], "127.0.0.1")
        for scenario, service, count in (("pubmed", "pubmed", 2), ("combined_limits", "nvd", 50)):
            with self.subTest(scenario=scenario):
                status, body, headers = self.request("/api/search?scenario=" + scenario)
                self.assertEqual(status, 200)
                self.assertEqual(body["service"], service)
                self.assertEqual(len(body["records"]), count)
                request_id = headers["X-Par02-Request-Id"]
                # Delivery precedes atomic receipt persistence. Wait for completion of
                # this identified request without sending the provider request again.
                receipt_file = self.logs / (request_id + ".json")
                deadline = time.monotonic() + 2
                while not receipt_file.exists() and time.monotonic() < deadline:
                    time.sleep(0.01)
                self.assertTrue(receipt_file.exists())
                receipt = json.loads(receipt_file.read_text())
                self.assertGreater(receipt["provider_requests"], 0)
                self.assertTrue(receipt["raw_hash_matches_transport"])
                self.assertEqual(receipt["provider_bind"][0], "127.0.0.1")
                self.assertEqual(receipt["worker_stats"]["live"], 0)

    def test_untrusted_browser_request_is_rejected_before_transport(self):
        cases = [
            {},
            {**APP_HEADER, "Host": "evil.invalid"},
            {**APP_HEADER, "Origin": "https://evil.invalid"},
            {**APP_HEADER, "Origin": "null"},
            {**APP_HEADER, "Sec-Fetch-Site": "cross-site"},
        ]
        for headers in cases:
            with self.subTest(headers=headers):
                status, body, _ = self.request("/api/search?scenario=pubmed", headers=headers)
                self.assertEqual(status, 403)
                self.assertEqual(body["error"]["code"], "invalid_request")

    def test_proxy_origin_and_fixed_application_header_are_accepted(self):
        status, body, _ = self.request("/api/lab-status", headers={
            **APP_HEADER, "Origin": "http://127.0.0.1:5173", "Sec-Fetch-Site": "same-origin",
        })
        self.assertEqual(status, 200)
        self.assertEqual(body["scope"], "synthetic_loopback_only")

    def test_closed_input_contract_and_provider_failures(self):
        for path, expected in (
            ("/api/search?scenario=pubmed&query=patient", 400),
            ("/api/search?scenario=pubmed&scenario=nvd", 400),
            ("/api/search?scenario=unknown", 400),
            ("/api/search?scenario=invalid_json", 502),
            ("/api/search?scenario=redirect", 502),
            ("/api/search?scenario=timeout", 504),
        ):
            with self.subTest(path=path):
                status, body, _ = self.request(path)
                self.assertEqual(status, expected)
                self.assertNotIn("records", body)
        status, _, _ = self.request("/api/search?scenario=pubmed", headers={**APP_HEADER, "Content-Length": "1"})
        self.assertEqual(status, 400)
        status, _, _ = self.request("/api/search?scenario=pubmed", method="POST")
        self.assertEqual(status, 405)

    def test_parser_errors_are_fixed_json_and_head_has_no_body(self):
        for line in (b"GET /SYNTHETIC_PRIVATE HTTP/not-a-version", b"UNKNOWN_PRIVATE / HTTP/1.1", b"HEAD /SYNTHETIC_PRIVATE HTTP/1.1"):
            with self.subTest(line=line):
                with socket.create_connection(("127.0.0.1", self.port), timeout=3) as connection:
                    connection.sendall(line + b"\r\nHost: 127.0.0.1:" + str(self.port).encode() + b"\r\n\r\n")
                    chunks = []
                    while True:
                        part = connection.recv(4096)
                        if not part:
                            break
                        chunks.append(part)
                raw = b"".join(chunks)
                headers, body = raw.split(b"\r\n\r\n", 1)
                self.assertTrue(headers.startswith(b"HTTP/"))
                self.assertIn(b"application/json", headers)
                self.assertIn(b"Cache-Control: no-store", headers)
                self.assertNotIn(b"PRIVATE", raw)
                self.assertNotIn(b"<html", raw)
                if line.startswith(b"HEAD"):
                    self.assertEqual(body, b"")
                else:
                    self.assertEqual(json.loads(body)["error"]["code"], "invalid_request")


if __name__ == "__main__":
    unittest.main(verbosity=2)
