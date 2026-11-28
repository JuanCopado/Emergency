"""New stable-origin transport tests with inert authenticated-verifier doubles."""
import contextlib
import http.client
import json
from pathlib import Path
import socket
import tempfile
import threading
import unittest
from unittest.mock import patch

import local_installation as local
import stable_launcher as stable


class FakeBackend:
    def __init__(self, directory, port, revision):
        self.revision = revision
        self.calls = []
        self.closed = False

    def request(self, path, payload):
        self.calls.append((path, payload))
        return 200, {"synthetic": True, "revision": self.revision}

    def close(self):
        self.closed = True


class StableTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="emergency-stable-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.selected = self.release("a" * 40)

    def release(self, revision):
        directory = self.root / revision
        directory.mkdir()
        contents = {"index.html": b'<html><script>document.title="synthetic";</script>fixture</html>',
                    "assets/main.js": revision.encode(), "assets/pdf.mjs": b"// inert worker", "backend/private.py": b"never public"}
        files = {}
        for name, data in contents.items():
            target = directory / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            files[name] = {"path": name, "size": len(data), "sha256": local.digest(data)}
        manifest = {"source_sha": revision, "capabilities": ["synthetic-test"]}
        return directory, manifest, files, {"version": revision, "manifest_sha256": "f" * 64}

    def verifier(self, root):
        self.assertEqual(root, self.root)
        return self.selected

    @contextlib.contextmanager
    def running(self, factory=FakeBackend):
        server = stable.make_stable_server(self.root, verify_release=self.verifier, backend_factory=factory)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield server
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)
            self.assertFalse(thread.is_alive())

    def request(self, server, path="/", method="GET", body=None, headers=None):
        connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=3)
        try:
            connection.request(method, path, body=body, headers=headers or {})
            r = connection.getresponse()
            return r.status, dict(r.getheaders()), r.read()
        finally:
            connection.close()

    def post(self, server, revision="a" * 40, body=b"{}", **headers):
        return self.request(server, "/api/clinical-note/new", "POST", body,
                            {"Content-Type": "application/json", stable.REVISION_HEADER: revision, **headers})

    def test_origin_retained_across_restart_update_and_rollback(self):
        a = self.selected
        with self.running() as first:
            port = first.server_port
            self.assertEqual(self.request(first, "/assets/main.js")[2], b"a" * 40)
            self.selected = self.release("b" * 40)
            self.assertEqual(self.request(first, "/assets/main.js")[2], b"a" * 40)
            with self.assertRaises(local.ReleaseError):
                stable.make_stable_server(self.root, verify_release=self.verifier, backend_factory=FakeBackend)
        with self.running() as second:
            self.assertEqual(second.server_port, port)
            self.assertEqual(self.request(second, "/assets/main.js")[2], b"b" * 40)
            self.selected = a
        with self.running() as rollback:
            self.assertEqual(rollback.server_port, port)
            self.assertEqual(self.request(rollback, "/assets/main.js")[2], b"a" * 40)

    def test_stale_revision_is_rejected_before_backend_and_private_files_never_served(self):
        with self.running() as server:
            self.assertEqual(self.post(server, revision="b" * 40)[0], 409)
            self.assertEqual(server.backend.calls, [])
            self.assertEqual(self.post(server)[0], 200)
            self.assertEqual(len(server.backend.calls), 1)
            self.assertEqual(self.request(server, "/backend/private.py")[0], 404)
            self.assertNotIn("backend/private.py", server.files)
            self.assertEqual(self.request(server, "/assets/pdf.mjs")[1]["Content-Type"], "text/javascript")

    def test_frame_input_and_method_rejections_do_not_reach_backend(self):
        with self.running() as server:
            for method in ["GET", "PUT", "OPTIONS", "HEAD"]:
                self.assertEqual(self.request(server, "/api/clinical-note/new", method)[0], 405)
            for body in [b"[]", b'{"a":1,"a":2}', b'{"a":NaN}', b"invalid"]:
                self.assertEqual(self.post(server, body=body)[0], 400)
            self.assertEqual(self.post(server, **{"Transfer-Encoding": "chunked"})[0], 400)
            self.assertEqual(self.post(server, **{"Content-Length": str(stable.MAX_REQUEST + 1)})[0], 413)
            self.assertEqual(self.post(server, **{"Origin": "https://outside.invalid"})[0], 403)
            self.assertEqual(server.backend.calls, [])

    def test_duplicate_revision_header_and_foreign_host_rejected(self):
        with self.running() as server:
            for header, value in [(stable.REVISION_HEADER, "a" * 40), ("Host", "outside.invalid")]:
                c = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=3)
                c.putrequest("POST", "/api/clinical-note/new")
                c.putheader("Content-Type", "application/json")
                c.putheader("Content-Length", "2")
                c.putheader(stable.REVISION_HEADER, "a" * 40)
                c.putheader(header, value)
                c.endheaders(b"{}")
                r = c.getresponse()
                self.assertEqual(r.status, 409 if header == stable.REVISION_HEADER else 403)
                r.read();c.close()
            self.assertEqual(server.backend.calls, [])

    def test_unsigned_verifier_not_optional_and_backend_failure_releases_lock(self):
        with self.assertRaises(TypeError):
            stable.make_stable_server(self.root)
        def reject(_root):
            raise local.ReleaseError("Untrusted signature")
        with self.assertRaises(local.ReleaseError):
            stable.make_stable_server(self.root, verify_release=reject)
        with self.running() as server:
            self.assertEqual(self.request(server)[0], 200)

    def test_occupied_origin_fails_closed_without_reassigning_port(self):
        with self.running() as first:
            port = first.server_port
        blocker = socket.socket()
        blocker.bind(("127.0.0.1", port));blocker.listen()
        try:
            with self.assertRaises(local.ReleaseError):
                stable.make_stable_server(self.root, verify_release=self.verifier, backend_factory=FakeBackend)
            self.assertEqual(json.loads((self.root / "stable-origin.json").read_text())["port"], port)
        finally:
            blocker.close()
        with self.running() as next_server:
            self.assertEqual(next_server.server_port, port)

    def test_oversized_backend_result_fails_without_leaking_payload(self):
        with self.running() as server:
            with patch.object(server.backend, "request", return_value=(200, {"private": "never echoed"})):
                with patch.object(stable, "MAX_RESPONSE", 4):
                    status, _, body = self.post(server)
            self.assertEqual(status, 503)
            self.assertNotIn(b"private", body)

    def test_unbundled_ocr_has_explicit_nonclinical_unavailability(self):
        with self.running() as server:
            status, _, body = self.request(server, "/api/blood-gas/session")
            self.assertEqual(status, 503)
            self.assertEqual(json.loads(body)["error_code"], "OCR_RUNTIME_NOT_PACKAGED")
            self.assertEqual(server.backend.calls, [])

    def test_backend_close_failure_still_releases_runtime_lease(self):
        class BrokenClose(FakeBackend):
            def close(self):
                raise OSError("synthetic close failure")
        server = stable.make_stable_server(self.root, verify_release=self.verifier, backend_factory=BrokenClose)
        port = server.server_port
        with self.assertRaises(OSError):
            server.server_close()
        with self.running() as recovered:
            self.assertEqual(recovered.server_port, port)


if __name__ == "__main__":
    unittest.main(verbosity=2)
