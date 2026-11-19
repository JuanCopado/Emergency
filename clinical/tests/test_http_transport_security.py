"""Bounded loopback sockets and ephemeral synthetic TLS; no clinical files/network."""
from contextlib import contextmanager
import http.client
import json
import os
from pathlib import Path
import queue
import shutil
import socket
import ssl
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import clinical_note_api as api
from http_transport import BoundedHTTPServer


@contextmanager
def running_server(*, tls_context=None, max_workers=2, request_timeout=.3, handler=api.ClinicalNoteHandler):
    server = BoundedHTTPServer(("127.0.0.1", 0), handler, tls_context=tls_context,
                               max_workers=max_workers, request_timeout=request_timeout)
    thread = threading.Thread(target=server.serve_forever,
                              kwargs={"poll_interval": .01}, daemon=True)
    thread.start()
    try:
        yield server
    finally:
        server.shutdown()
        thread.join(2)
        server.server_close()


def health(server, context=None):
    client = (http.client.HTTPSConnection("127.0.0.1", server.server_port, timeout=2, context=context)
              if context else http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=2))
    try:
        client.request("GET", "/api/clinical-note/health")
        response = client.getresponse()
        return response.status, json.loads(response.read())
    finally:
        client.close()


def raw_request(server, headers, body=b"{}", *, half_close=False):
    with socket.create_connection(server.server_address, timeout=2) as client:
        request = "POST /api/clinical-note/analyze HTTP/1.0\r\n" + "\r\n".join(headers) + "\r\n\r\n"
        client.sendall(request.encode("utf-8") + body)
        if half_close:
            client.shutdown(socket.SHUT_WR)
        response = http.client.HTTPResponse(client)
        response.begin()
        return response.status, json.loads(response.read())


class HttpFramingSecurityTests(unittest.TestCase):
    def test_valid_json_preserves_exact_synthetic_payload_and_response(self):
        payload = {"synthetic": "<tag> & Unicode —", "nested": [1, True, None]}
        body = json.dumps(payload, ensure_ascii=False).encode("utf8")
        with running_server() as server, patch.object(api, "dispatch", return_value=(200, payload)) as dispatch:
            result = raw_request(server, [f"Content-Length: {len(body)}", "Content-Type: Application/JSON; charset=utf-8"], body)
        self.assertEqual(result, (200, payload))
        dispatch.assert_called_once_with("/api/clinical-note/analyze", payload)

    def test_ambiguous_or_invalid_framing_is_rejected_before_dispatch(self):
        cases = [([], 411), (["Content-Length: 2", "Content-Length: 2"], 400),
                 (["Content-Length: 2, 2"], 400), (["Content-Length: -2"], 400),
                 (["Content-Length: +2"], 400), (["Content-Length: ٢"], 400),
                 (["Content-Length: 0"], 400), (["Content-Length: 99999999999"], 400),
                 (["Content-Length: 99999999"], 413),
                 (["Transfer-Encoding: chunked", "Content-Length: 2"], 400),
                 (["Transfer-Encoding: identity", "Content-Length: 2"], 400)]
        with running_server() as server, patch.object(api, "dispatch") as dispatch:
            for headers, expected in cases:
                with self.subTest(headers=headers):
                    status, response = raw_request(server, [*headers, "Content-Type: application/json"])
                    self.assertEqual(status, expected)
                    self.assertEqual(set(response), {"error"})
            dispatch.assert_not_called()

    def test_browser_simple_types_and_cross_site_requests_never_dispatch(self):
        cases = [([], 415), (["Content-Type: text/plain"], 415),
                 (["Content-Type: application/x-www-form-urlencoded"], 415),
                 (["Content-Type: multipart/form-data; boundary=synthetic"], 415),
                 (["Content-Type: application/json", "Content-Type: text/plain"], 415),
                 (["Content-Type: application/json", "Content-Encoding: gzip"], 415),
                 (["Content-Type: application/json", "Content-Encoding: identity", "Content-Encoding: gzip"], 415),
                 (["Content-Type: application/json", "Content-Encoding: identity", "Content-Encoding: identity"], 415),
                 (["Content-Type: application/json", "Sec-Fetch-Site: cross-site"], 403)]
        with running_server() as server, patch.object(api, "dispatch") as dispatch:
            for headers, expected in cases:
                with self.subTest(headers=headers):
                    status, _ = raw_request(server, ["Content-Length: 2", *headers])
                    self.assertEqual(status, expected)
            dispatch.assert_not_called()

    def test_same_origin_dev_proxy_metadata_remains_compatible(self):
        with running_server() as server, patch.object(api, "dispatch", return_value=(200, {"ok": True})):
            status, _ = raw_request(server, ["Content-Length: 2", "Content-Type: application/json",
                                            "Origin: http://localhost:5173", "Sec-Fetch-Site: same-origin"])
        self.assertEqual(status, 200)

    def test_truncated_body_is_rejected_even_if_its_prefix_is_valid_json(self):
        with running_server() as server, patch.object(api, "dispatch") as dispatch:
            result = raw_request(server, ["Content-Length: 100", "Content-Type: application/json"], half_close=True)
            self.assertEqual(result, (400, {"error": "incomplete request body"}))
            dispatch.assert_not_called()

    def test_dispatch_failures_recover_capacity_without_private_details(self):
        completed = queue.Queue()
        with running_server(max_workers=1) as server, patch.object(api, "dispatch", side_effect=RuntimeError("SYNTHETIC_PRIVATE")):
            process_request_thread = server.process_request_thread
            def notify_completed_request(request, address):
                process_request_thread(request, address)
                completed.put(True)
            with patch.object(server, "process_request_thread", notify_completed_request):
                for _ in range(4):
                    status, response = raw_request(server, ["Content-Length: 2", "Content-Type: application/json"])
                    self.assertEqual(status, 500)
                    self.assertNotIn("SYNTHETIC_PRIVATE", json.dumps(response))
                    # Reading Content-Length can finish before the worker releases its slot.
                    self.assertTrue(completed.get(timeout=2))
        self.assertEqual(response, {"error": "clinical-note backend failure"})


class HttpAvailabilityTests(unittest.TestCase):
    def test_parser_errors_do_not_reflect_private_request_lines(self):
        with running_server() as server:
            for request in (b"SYNTHETIC_PRIVATE /api HTTP/1.0\r\n\r\n",
                            b"GET /?note=SYNTHETIC_PRIVATE INVALID\r\n\r\n"):
                with self.subTest(request=request), socket.create_connection(server.server_address, timeout=2) as client:
                    client.sendall(request)
                    response = http.client.HTTPResponse(client)
                    response.begin()
                    raw = response.read()
                    self.assertIn(response.status, (400, 501))
                    self.assertEqual(json.loads(raw), {"error": "invalid HTTP request"})
                    self.assertNotIn(b"SYNTHETIC_PRIVATE", raw)
                    self.assertEqual(response.getheader("X-Content-Type-Options"), "nosniff")

    def test_head_parser_error_has_headers_without_response_body(self):
        with running_server() as server, socket.create_connection(server.server_address, timeout=2) as client:
            client.sendall(b"HEAD /api/clinical-note/health HTTP/1.0\r\n\r\n")
            wire = bytearray()
            while chunk := client.recv(4096):
                wire.extend(chunk)
            headers, body = bytes(wire).split(b"\r\n\r\n", 1)
            self.assertIn(b"501", headers)
            self.assertIn(b"application/json", headers)
            self.assertEqual(body, b"")

    def test_thread_creation_failure_closes_peer_and_recovers_capacity(self):
        from http.server import ThreadingHTTPServer
        original = ThreadingHTTPServer.process_request
        calls = 0
        def fail_once(server, request, address):
            nonlocal calls
            calls += 1
            if calls == 1:
                raise RuntimeError("SYNTHETIC_PRIVATE cannot start thread")
            return original(server, request, address)
        with running_server(max_workers=1) as server, \
             patch.object(ThreadingHTTPServer, "process_request", fail_once), \
             self.assertLogs("http_transport", level="WARNING") as logs:
            with socket.create_connection(server.server_address, timeout=2) as client:
                self.assertEqual(client.recv(1024), b"")
            self.assertEqual(health(server)[0], 200)
        self.assertIn("RuntimeError", "".join(logs.output))
        self.assertNotIn("SYNTHETIC_PRIVATE", "".join(logs.output))

    def test_trickled_response_reader_cannot_retain_the_only_worker(self):
        started = threading.Event()
        class SmallSendBuffer(api.ClinicalNoteHandler):
            def setup(self):
                super().setup()
                self.connection.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 4096)
            def _send(self, status, body, **kwargs):
                if "synthetic" in body:
                    started.set()
                super()._send(status, body, **kwargs)
        with running_server(handler=SmallSendBuffer, max_workers=1) as server, \
             socket.create_connection(server.server_address, timeout=2) as client, \
             patch.object(api, "dispatch", return_value=(200, {"synthetic": "x" * (2 * 1024 * 1024)})):
            client.sendall(b"POST /api/clinical-note/analyze HTTP/1.0\r\nContent-Length: 2\r\nContent-Type: application/json\r\n\r\n{}")
            self.assertTrue(started.wait(2))
            stop = threading.Event()
            def consume_slowly():
                while not stop.wait(.04):
                    try:
                        if not client.recv(1):
                            return
                    except OSError:
                        return
            reader = threading.Thread(target=consume_slowly, daemon=True)
            reader.start()
            deadline = time.monotonic() + 2
            try:
                while True:
                    try:
                        self.assertEqual(health(server)[0], 200)
                        break
                    except (ConnectionError, http.client.RemoteDisconnected):
                        if time.monotonic() >= deadline:
                            raise
                        time.sleep(.02)
            finally:
                stop.set()
                reader.join(2)

    def test_partial_body_times_out_without_dispatch(self):
        with running_server() as server, patch.object(api, "dispatch") as dispatch:
            with socket.create_connection(server.server_address, timeout=2) as client:
                client.sendall(b"POST /api/clinical-note/analyze HTTP/1.0\r\nContent-Length: 100\r\nContent-Type: application/json\r\n\r\n{")
                self.assertEqual(client.recv(1024), b"")
            dispatch.assert_not_called()
            self.assertEqual(health(server)[0], 200)

    def assert_trickle_expires(self, prefix):
        with running_server() as server, socket.create_connection(server.server_address, timeout=2) as client:
            stop = threading.Event()
            client.sendall(prefix)
            def trickle():
                while not stop.wait(.04):
                    try:
                        client.sendall(b" ")
                    except OSError:
                        return
            sender = threading.Thread(target=trickle, daemon=True)
            sender.start()
            try:
                self.assertEqual(client.recv(1024), b"")
            finally:
                stop.set()
                sender.join(1)
            self.assertEqual(health(server)[0], 200)

    def test_trickled_headers_cannot_reset_the_absolute_read_deadline(self):
        self.assert_trickle_expires(b"GET /api/clinical-note/health HTTP/1.0\r\nX-Synthetic: ")

    def test_trickled_body_cannot_reset_the_absolute_read_deadline(self):
        with patch.object(api, "dispatch") as dispatch:
            self.assert_trickle_expires(b"POST /api/clinical-note/analyze HTTP/1.0\r\nContent-Length: 1000\r\nContent-Type: application/json\r\n\r\n{")
            dispatch.assert_not_called()

    def test_worker_limit_closes_excess_connections_and_recovers(self):
        entered = queue.Queue()
        class ObservedHandler(api.ClinicalNoteHandler):
            def setup(self):
                super().setup()
                entered.put(True)
        with running_server(handler=ObservedHandler, max_workers=2, request_timeout=1) as server:
            clients = []
            try:
                for _ in range(2):
                    clients.append(socket.create_connection(server.server_address, timeout=2))
                    entered.get(timeout=2)
                with socket.create_connection(server.server_address, timeout=2) as excess:
                    self.assertEqual(excess.recv(1024), b"")
                self.assertTrue(entered.empty())
            finally:
                for client in clients:
                    client.close()
            deadline = time.monotonic() + 2
            while True:
                try:
                    self.assertEqual(health(server)[0], 200)
                    break
                except (ConnectionError, http.client.RemoteDisconnected):
                    if time.monotonic() >= deadline:
                        raise
                    time.sleep(.01)


class TlsAvailabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        openssl = os.getenv("EMERGENCY_TEST_OPENSSL") or shutil.which("openssl")
        if not openssl:
            if os.getenv("EMERGENCY_REQUIRE_TLS_TESTS") == "1":
                raise RuntimeError("CI must provide OpenSSL for real TLS regressions")
            raise unittest.SkipTest("OpenSSL required to generate an ephemeral synthetic certificate")
        cls.temporary = tempfile.TemporaryDirectory(prefix="emergency-synthetic-tls-")
        cls.addClassCleanup(cls.temporary.cleanup)
        directory = Path(cls.temporary.name)
        cert, key = directory / "cert.pem", directory / "key.pem"
        subprocess.run([openssl, "req", "-x509", "-newkey", "rsa:2048", "-sha256", "-nodes",
                        "-keyout", str(key), "-out", str(cert), "-days", "1", "-subj", "/CN=localhost",
                        "-addext", "subjectAltName=DNS:localhost,IP:127.0.0.1"],
                       check=True, capture_output=True, timeout=20)
        cls.server_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        cls.server_context.minimum_version = ssl.TLSVersion.TLSv1_2
        cls.server_context.load_cert_chain(str(cert), str(key))
        cls.client_context = ssl.create_default_context(cafile=str(cert))

    def test_real_tls_health_uses_verified_synthetic_certificate(self):
        with running_server(tls_context=self.server_context) as server:
            self.assertEqual(health(server, self.client_context)[0], 200)

    def test_idle_tls_peer_cannot_block_other_verified_clients(self):
        with running_server(tls_context=self.server_context, request_timeout=1) as server:
            with socket.create_connection(server.server_address, timeout=2):
                self.assertEqual(health(server, self.client_context)[0], 200)

    def test_failed_tls_handshake_releases_the_worker_slot(self):
        with running_server(tls_context=self.server_context, max_workers=1) as server:
            with socket.create_connection(server.server_address, timeout=2) as bad:
                bad.sendall(b"NOT-A-TLS-CLIENT")
                try:
                    self.assertEqual(bad.recv(1024), b"")
                except ConnectionResetError:
                    pass  # OpenSSL/OS may abort instead of sending EOF.
            self.assertEqual(health(server, self.client_context)[0], 200)

    def test_valid_client_hello_trickle_cannot_reset_handshake_timeout(self):
        incoming, outgoing = ssl.MemoryBIO(), ssl.MemoryBIO()
        client_tls = self.client_context.wrap_bio(incoming, outgoing, server_hostname="127.0.0.1")
        with self.assertRaises(ssl.SSLWantReadError):
            client_tls.do_handshake()
        hello = outgoing.read()
        self.assertGreater(len(hello), 100)
        with running_server(tls_context=self.server_context, max_workers=1) as server, \
             socket.create_connection(server.server_address, timeout=2) as client:
            stop = threading.Event()
            client.sendall(hello[:1])
            def trickle_hello():
                for value in hello[1:]:
                    if stop.wait(.04):
                        return
                    try:
                        client.sendall(bytes([value]))
                    except OSError:
                        return
            sender = threading.Thread(target=trickle_hello, daemon=True)
            sender.start()
            try:
                try:
                    self.assertEqual(client.recv(1024), b"")
                except ConnectionResetError:
                    pass
            finally:
                stop.set()
                sender.join(2)
            self.assertEqual(health(server, self.client_context)[0], 200)


if __name__ == "__main__":
    unittest.main()
