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
HISTORICAL_MANIFEST_SHA256 = "e39c0a81ea1f0af477c378053459b9563ad7e7b9496e7c00a9418e438df76929"
Q4_TEST = "app/src/t06/viewModel.test.ts"
ORIGINAL_TEST_SHA256 = "ba17ff4a6823253ff06615db9381f3e013410528151af31b6e854f4f5e79d6da"
ADAPTED_TEST_SHA256 = "f26b06b9cb2a57598ccdd91625b5c829c5465db499a02a24772290382fb71d7a"
AMENDMENT = {
    "id": "T06-Q4-SURROGATE-AST-20261126",
    "destination": Q4_TEST,
    "source_sha256": ORIGINAL_TEST_SHA256,
    "source_snapshot": "provenance/viewModel.test.ts.original.txt",
    "adapted_sha256": ADAPTED_TEST_SHA256,
    "transformation": "construct_surrogate_controls_at_runtime_v1",
}


def adapted_test_source(original):
    """One exact, reviewed source adaptation; no assertion or case removed."""
    if hashlib.sha256(original).hexdigest() != ORIGINAL_TEST_SHA256:
        raise ValueError("Original Q4 test identity changed")
    pair = b"'\\ud800', '\\udfff'"
    anchor = b"  it.each(['\\u0000'"
    if original.count(pair) != 1 or original.count(anchor) != 1:
        raise ValueError("Unexpected Q4 source layout")
    comment = (b"  // Keep lone-surrogate inputs at runtime without malformed string values in\n"
               b"  // the source AST consumed by the analyzer's UTF-8 Protobuf serializer.\n")
    return original.replace(pair, b"String.fromCharCode(0xd800), String.fromCharCode(0xdfff)").replace(anchor, comment + anchor)


def verify_test_amendment(original, current, amendment):
    if amendment != AMENDMENT:
        raise ValueError("Q4 amendment differs from the reviewed contract")
    if current != adapted_test_source(original) or hashlib.sha256(current).hexdigest() != ADAPTED_TEST_SHA256:
        raise ValueError("Current Q4 test differs from the exact reviewed adaptation")


class SourceAmendmentTests(unittest.TestCase):
    def setUp(self):
        self.original = (ROOT / AMENDMENT["source_snapshot"]).read_bytes()

    def test_reviewed_current_test_matches_exact_original_transformation(self):
        current = (ROOT.parents[1] / Q4_TEST).read_text(encoding="utf-8").encode("utf-8")
        verify_test_amendment(self.original, current, AMENDMENT)

    def test_deleted_assertion_is_rejected(self):
        current = adapted_test_source(self.original)
        assertion = b"expect(buildT06ViewModel(service, input)).toEqual(rejected);"
        self.assertIn(assertion, current)
        with self.assertRaises(ValueError):
            verify_test_amendment(self.original, current.replace(assertion, b"", 1), AMENDMENT)

    def test_changed_original_or_relabelled_hash_is_rejected(self):
        current = adapted_test_source(self.original)
        with self.assertRaises(ValueError):
            verify_test_amendment(self.original + b"\n", current, AMENDMENT)
        with self.assertRaises(ValueError):
            verify_test_amendment(self.original, current, {**AMENDMENT, "adapted_sha256": ORIGINAL_TEST_SHA256})


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

    def test_recovered_sources_and_explicit_adaptation_match_provenance(self):
        repository = ROOT.parents[1]
        historical = (ROOT / "SOURCE_PROVENANCE.json").read_bytes()
        self.assertEqual(hashlib.sha256(historical).hexdigest(), HISTORICAL_MANIFEST_SHA256)
        manifest = json.loads(historical)
        amendment = json.loads((ROOT / "CURRENT_ADAPTATIONS.json").read_text(encoding="utf-8"))
        self.assertEqual(amendment, {"historical_manifest_sha256": HISTORICAL_MANIFEST_SHA256, "adaptations": [AMENDMENT]})
        unchanged = [item for item in manifest["files"] if item["identity_preserved"]]
        self.assertEqual(len(unchanged), 19)
        self.assertEqual(sum(item["destination"] == Q4_TEST for item in unchanged), 1)
        exact_destinations = 0
        for item in unchanged:
            with self.subTest(path=item["destination"]):
                current = (repository / item["destination"]).read_bytes()
                if item["destination"] == Q4_TEST:
                    self.assertEqual(item["source_sha256"], ORIGINAL_TEST_SHA256)
                    verify_test_amendment((ROOT / AMENDMENT["source_snapshot"]).read_bytes(), current, AMENDMENT)
                else:
                    self.assertEqual(hashlib.sha256(current).hexdigest(), item["source_sha256"])
                    exact_destinations += 1
        self.assertEqual(exact_destinations, 18)

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
