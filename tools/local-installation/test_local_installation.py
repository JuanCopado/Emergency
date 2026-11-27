"""Synthetic stdlib tests; no product release or patient data."""
import contextlib
import hashlib
import http.client
import importlib.util
import io
import json
import os
from pathlib import Path
import socket
import stat
import struct
import subprocess
import tempfile
import threading
import unittest
from unittest.mock import patch
import zipfile

spec = importlib.util.spec_from_file_location("local_installation", Path(__file__).with_name("local_installation.py"))
local = importlib.util.module_from_spec(spec)
spec.loader.exec_module(local)


class LocalReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="emergency-local-test-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / "installation"
        self.sequence = 0

    def archive(self, source="a" * 40, files=None, extra=None, entries=None, manifest_transform=None):
        self.sequence += 1
        files = {"index.html": b'<html><script>document.title="SYNTHETIC";</script><div id="root">synthetic fixture</div></html>', "assets/main.js": source.encode(), "assets/pdf.worker.mjs": b"// synthetic module worker", "sw.js": b"// synthetic worker"} if files is None else files
        manifest = {"schema": local.SCHEMA, "source_sha": source, "capabilities": ["static-reference-partial", "no-clinical-api", "no-remote-case-processing"], "files": [{"path": name, "size": len(value), "sha256": local.digest(value)} for name, value in files.items()]}
        if manifest_transform:
            manifest_transform(manifest)
        raw = local.canonical_json(manifest)
        archive = self.base / f"fixture-{self.sequence}.zip"
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as target:
            target.writestr("manifest.json", raw)
            for name, value in files.items():
                target.writestr(name, value)
            for name, value in (extra or {}).items():
                target.writestr(name, value)
            for info, value in entries or []:
                target.writestr(info, value)
        return archive, local.digest(raw), local.version_id(manifest, local.digest(raw))

    def receive(self, source="a" * 40):
        archive, expected, version = self.archive(source)
        local.install(archive, self.root, expected)
        return expected, version

    @contextlib.contextmanager
    def server(self):
        server = local.make_server(self.root)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield server
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)
            self.assertFalse(thread.is_alive())

    def request(self, server, path="/", method="GET", headers=None):
        connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=3)
        try:
            connection.request(method, path, headers=headers or {})
            response = connection.getresponse()
            return response.status, dict(response.getheaders()), response.read()
        finally:
            connection.close()

    def test_receive_requires_separately_trusted_hash(self):
        archive, expected, _ = self.archive()
        for invalid in (None, "", "0" * 64, expected.upper()):
            with self.subTest(invalid=invalid), self.assertRaises(local.ReleaseError):
                local.install(archive, self.root, invalid)
        self.assertFalse((self.root / "active.json").exists())

    def test_paths_reject_windows_aliases_traversal_controls_and_hidden(self):
        for name in ("../evil", "/tmp/evil", "C:/evil", "C:evil", "//server/evil", "x:y", "a\\b", "a/./b", "a//b", "a/../b", "a.", "a ", "NUL.txt", "a/COM1", ".env", "a/%2e", "a/\x00bad", "a/\nbad", "MAIN~1.JS", "é.js"):
            with self.subTest(name=name), self.assertRaises(local.ReleaseError):
                local.safe_name(name)
        self.assertEqual(local.safe_name("assets/index-A_12.js"), "assets/index-A_12.js")

    def test_zip_extra_missing_casefold_duplicate_and_file_parent_rejected(self):
        for extra in ({"extra.js": b"extra"}, {"INDEX.HTML": b"collision"}, {"index.html": b"duplicate"}, {"assets": b"parent"}):
            with self.subTest(extra=list(extra)), contextlib.redirect_stderr(io.StringIO()):
                archive, expected, _ = self.archive(extra=extra)
                with self.assertRaises(local.ReleaseError):
                    local.install(archive, self.root, expected)
        archive, expected, _ = self.archive(manifest_transform=lambda m: m["files"].append({"path": "missing.css", "size": 0, "sha256": local.digest(b"")}))
        with self.assertRaises(local.ReleaseError):
            local.install(archive, self.root, expected)

    def test_symlink_zip_rejected(self):
        info = zipfile.ZipInfo("link.js")
        info.external_attr = (stat.S_IFLNK | 0o777) << 16
        archive, expected, _ = self.archive(entries=[(info, b"../outside")])
        with self.assertRaises(local.ReleaseError):
            local.install(archive, self.root, expected)

    def test_native_symlink_install_root_rejected(self):
        archive, expected, _ = self.archive()
        target = self.base / "outside"
        target.mkdir()
        link = self.base / "link"
        try:
            link.symlink_to(target, target_is_directory=True)
        except OSError as exc:
            self.skipTest(f"Native Windows symlink creation unavailable: {exc.winerror}")
        with self.assertRaises(local.ReleaseError):
            local.install(archive, link, expected)
        self.assertEqual(list(target.iterdir()), [])

    @unittest.skipUnless(os.name == "nt", "Windows junction control")
    def test_native_windows_junction_install_root_rejected(self):
        import _winapi
        target = self.base / "junction-target"
        target.mkdir()
        link = self.base / "junction"
        _winapi.CreateJunction(str(target), str(link))
        archive, expected, _ = self.archive()
        with self.assertRaises(local.ReleaseError):
            local.install(archive, link, expected)
        self.assertEqual(list(target.iterdir()), [])

    def test_package_clean_source_and_deterministic_bytes(self):
        source, dist = self.base / "source", self.base / "dist"
        source.mkdir()
        dist.mkdir()
        def git(*args):
            try:
                return subprocess.check_output(["git", "-c", "user.name=Synthetic Fixture", "-c", "user.email=fixture@localhost", "-c", "commit.gpgsign=false", *args], cwd=source, text=True, stderr=subprocess.PIPE).strip()
            except subprocess.CalledProcessError as error:
                raise AssertionError(f"Synthetic Git {args[0]} failed: {error.stderr}") from error
        git("init", "--initial-branch=fixture")
        (source / "source.txt").write_text("synthetic input")
        git("add", "source.txt")
        git("commit", "--no-gpg-sign", "-m", "synthetic package fixture")
        head = git("rev-parse", "HEAD")
        (dist / "index.html").write_text("<html>fixture</html>")
        (dist / "main.js").write_text(f'const source="{head}";')
        (dist / "pdf.worker.mjs").write_text("// synthetic PDF module worker")
        (dist / "main.js.map").write_text("synthetic audit map excluded")
        environment = {k: v for k, v in os.environ.items() if not k.startswith("VITE_") and k not in {"EMERGENCY_LOCAL_REVIEW", "EMERGENCY_LOCAL_API_TOKEN"}}
        with patch.dict(os.environ, environment, clear=True):
            first, second = self.base / "one.zip", self.base / "two.zip"
            a = local.package(dist, source, first)
            b = local.package(dist, source, second)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertEqual(a["manifest_sha256"], b["manifest_sha256"])
            with zipfile.ZipFile(first) as archive:
                self.assertNotIn("main.js.map", archive.namelist())
                self.assertIn("pdf.worker.mjs", archive.namelist())
            local.install(first, self.root, a["manifest_sha256"])
            with patch.dict(os.environ, {"VITE_CLINICAL_NOTE_API_BASE": "https://example.invalid"}), self.assertRaises(local.ReleaseError):
                local.package(dist, source, self.base / "remote.zip")
            (dist / "unexpected.exe").write_bytes(b"synthetic unsupported content")
            with self.assertRaises(local.ReleaseError):
                local.package(dist, source, self.base / "executable.zip")
            (dist / "unexpected.exe").unlink()
            (source / "app").mkdir()
            (source / "app/.env.production").write_text("VITE_CLINICAL_NOTE_API_BASE=https://example.invalid")
            with self.assertRaises(local.ReleaseError):
                local.package(dist, source, self.base / "implicit-env.zip")
            (source / "app/.env.production").unlink()
            (source / "source.txt").write_text("changed")
            with self.assertRaises(local.ReleaseError):
                local.package(dist, source, self.base / "dirty.zip")

    @unittest.skipUnless(os.name == "nt", "Native Windows GetShortPathNameW control")
    def test_package_native_short_path_checkout_identity(self):
        import ctypes
        source = self.base / "source directory with spaces"
        source.mkdir()
        environment = {k: v for k, v in os.environ.items() if not k.startswith(("VITE_", "GIT_")) and k not in {"EMERGENCY_LOCAL_REVIEW", "EMERGENCY_LOCAL_API_TOKEN"}}
        def git(*args):
            return subprocess.check_output(["git", "-c", "user.name=Synthetic Fixture", "-c", "user.email=fixture@localhost", "-c", "commit.gpgsign=false", *args], cwd=source, env=environment, text=True, stderr=subprocess.DEVNULL).strip()
        git("init", "--initial-branch=fixture")
        (source / "source.txt").write_text("synthetic short-path source")
        git("add", "source.txt")
        git("commit", "--no-gpg-sign", "-m", "native short-path fixture")
        head = git("rev-parse", "HEAD")
        dist = self.base / "dist"
        dist.mkdir()
        (dist / "index.html").write_text("<html>short-path fixture</html>")
        (dist / "main.js").write_text(f'const source="{head}";')
        get_short = ctypes.WinDLL("kernel32", use_last_error=True).GetShortPathNameW
        get_short.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32]
        get_short.restype = ctypes.c_uint32
        buffer = ctypes.create_unicode_buffer(32768)
        count = get_short(str(source), buffer, len(buffer))
        if not count:
            raise ctypes.WinError(ctypes.get_last_error())
        self.assertLess(count, len(buffer))
        short = Path(buffer.value)
        self.assertTrue(os.path.samefile(source, short))
        with patch.dict(os.environ, environment, clear=True):
            result = local.package(dist, short, self.base / "native-short.zip")
        self.assertEqual(result["source_sha"], head)
        # Both spellings identify the same directory, without a link/reparse.
        self.assertEqual(local.no_links(short), short)

    def test_package_rejects_nested_checkout_and_different_git_root(self):
        source, dist, foreign = self.base / "source", self.base / "dist", self.base / "foreign"
        source.mkdir()
        dist.mkdir()
        foreign.mkdir()
        with self.assertRaisesRegex(local.ReleaseError, "own checkout"):
            local.package(dist, source, self.base / "no-checkout.zip")
        (source / ".git").mkdir()
        with patch.object(local.subprocess, "check_output", return_value=str(foreign) + "\n"), self.assertRaisesRegex(local.ReleaseError, "own checkout"):
            local.package(dist, source, self.base / "foreign-root.zip")
        nested = source / "nested"
        nested.mkdir()
        with self.assertRaisesRegex(local.ReleaseError, "own checkout"):
            local.package(dist, nested, self.base / "nested.zip")

    def test_zip_limits_and_descriptor_types(self):
        archive, expected, _ = self.archive()
        with patch.object(local, "MAX_FILES", 1), self.assertRaises(local.ReleaseError):
            local.install(archive, self.root, expected)
        for mutation in (lambda m: m["files"][0].update(size=True), lambda m: m.update(extra=True), lambda m: m["files"][0].update(sha256="0" * 64)):
            archive, expected, _ = self.archive(manifest_transform=mutation)
            with self.assertRaises(local.ReleaseError):
                local.install(archive, self.root, expected)
        # Actual DEFLATE bomb ratio exceeds the 1MiB allowance and 1000x ratio.
        archive, expected, _ = self.archive(files={"index.html": b"x" * (2 * 1024 * 1024)})
        with self.assertRaises(local.ReleaseError):
            local.install(archive, self.root, expected)

    def test_central_metadata_limits_before_zipfile_materialization(self):
        archive, expected, _ = self.archive()
        raw = bytearray(archive.read_bytes())
        # EOCD excessive declared record count is rejected before constructing ZipFile.
        excessive = bytearray(raw)
        struct.pack_into("<HH", excessive, len(excessive) - 14, local.MAX_FILES + 2, local.MAX_FILES + 2)
        # Excessive central bytes are also rejected before ZipInfo allocations.
        oversized = bytearray(raw)
        struct.pack_into("<I", oversized, len(oversized) - 10, local.MAX_CENTRAL_DIRECTORY + 1)
        # Lying about count does not bypass counting actual bounded central records.
        undercount = bytearray(raw)
        struct.pack_into("<HH", undercount, len(undercount) - 14, 1, 1)
        for index, value in enumerate((excessive, oversized, undercount)):
            path = self.base / f"central-invalid-{index}.zip"
            path.write_bytes(value)
            with patch.object(local.zipfile, "ZipFile") as constructor, self.assertRaises(local.ReleaseError):
                local.install(path, self.root, expected)
            constructor.assert_not_called()
        self.assertFalse(self.root.exists())

    def test_zip64_locator_cannot_override_preflight_metadata(self):
        archive, expected, _ = self.archive(files={"index.html": b"fixture", "assets/long-tail-name-for-locator-synthetic.js": b"fixture"})
        raw = bytearray(archive.read_bytes())
        raw[-42:-38] = b"PK\x06\x07"
        archive.write_bytes(raw)
        with patch.object(local.zipfile, "ZipFile") as constructor, self.assertRaisesRegex(local.ReleaseError, "ZIP64 locator"):
            local.install(archive, self.root, expected)
        constructor.assert_not_called()

    def test_inline_csp_hash_uses_browser_html_newline_normalization(self):
        lf = b'<script>\nconst x=1;\nconst y=2;\n</script>'
        crlf = lf.replace(b'\n', b'\r\n')
        cr = lf.replace(b'\n', b'\r')
        self.assertEqual(local.policy(lf), local.policy(crlf))
        self.assertEqual(local.policy(lf), local.policy(cr))

    def test_bad_update_keeps_existing_active_and_cleans_own_staging(self):
        expected, version = self.receive()
        local.select(self.root, version, expected)
        previous = (self.root / "active.json").read_bytes()
        archive, changed, _ = self.archive("b" * 40, manifest_transform=lambda m: m["files"][-1].update(sha256="0" * 64))
        with self.assertRaises(local.ReleaseError):
            local.install(archive, self.root, changed)
        self.assertEqual((self.root / "active.json").read_bytes(), previous)
        self.assertEqual(list(self.root.glob("staging-*")), [])
        self.assertTrue((self.root / "releases" / version).is_dir())

    def test_versions_immutable_and_single_writer_lock(self):
        archive, expected, version = self.archive()
        local.install(archive, self.root, expected)
        with self.assertRaises(local.ReleaseError):
            local.install(archive, self.root, expected)
        with local.writer(self.root), self.assertRaises(local.ReleaseError):
            local.select(self.root, version, expected)
        self.assertFalse((self.root / "writer.lock").exists())

    def test_activation_rehash_and_atomic_pointer_failure(self):
        expected, version = self.receive()
        local.select(self.root, version, expected)
        previous = (self.root / "active.json").read_bytes()
        second, next_version = self.receive("b" * 40)
        with patch.object(local.os, "replace", side_effect=OSError("synthetic atomic failure")), self.assertRaises(OSError):
            local.select(self.root, next_version, second)
        self.assertEqual((self.root / "active.json").read_bytes(), previous)
        self.assertEqual(list(self.root.glob("pending-*")), [])
        (self.root / "releases" / version / "assets/main.js").write_bytes(b"tampered")
        with self.assertRaises(local.ReleaseError):
            local.select(self.root, version, expected)

    def test_file_set_and_manifest_duplicate_json_keys(self):
        expected, version = self.receive()
        directory = self.root / "releases" / version
        (directory / "extra.txt").write_bytes(b"unlisted")
        with self.assertRaises(local.ReleaseError):
            local.verify_directory(directory, expected)
        with self.assertRaises(local.ReleaseError):
            local.object_json(b'{"x":1,"x":2}')

    def test_http_positive_headers_and_inline_hash_are_from_manifest(self):
        expected, version = self.receive()
        local.select(self.root, version, expected)
        with self.server() as server:
            status, headers, body = self.request(server)
            self.assertEqual(status, 200)
            self.assertIn(b"synthetic fixture", body)
            self.assertIn("'sha256-", headers["Content-Security-Policy"])
            self.assertNotIn("script-src 'self' 'unsafe-inline'", headers["Content-Security-Policy"])
            self.assertIn("connect-src 'self'", headers["Content-Security-Policy"])
            self.assertEqual(headers["Cache-Control"], "no-store")
            self.assertEqual(headers["X-Content-Type-Options"], "nosniff")
            self.assertNotIn("Access-Control-Allow-Origin", headers)
            self.assertEqual(self.request(server, "/assets/main.js")[2], b"a" * 40)
            self.assertEqual(self.request(server, "/assets/pdf.worker.mjs")[1]["Content-Type"], "text/javascript")
            self.assertEqual(self.request(server, "/", "HEAD")[2], b"")
            self.assertEqual(self.request(server, "/guides", headers={"Accept": "text/html"})[0], 200)

    def test_http_foreign_duplicate_host_and_origin_rejected(self):
        expected, version = self.receive()
        local.select(self.root, version, expected)
        with self.server() as server:
            for headers in ({"Host": "evil.example"}, {"Origin": "https://foreign.example"}, {"Origin": "null"}, {"Sec-Fetch-Site": "cross-site"}):
                self.assertEqual(self.request(server, headers=headers)[0], 403)
            for duplicated in ("Host", "Origin"):
                with socket.create_connection(("127.0.0.1", server.server_port), timeout=3) as connection:
                    host = f"127.0.0.1:{server.server_port}"
                    extra = f"Host: {host}" if duplicated == "Host" else f"Origin: http://{host}\r\nOrigin: http://{host}"
                    connection.sendall(f"GET / HTTP/1.0\r\nHost: {host}\r\n{extra}\r\n\r\n".encode())
                    self.assertIn(b"403", connection.recv(4096).split(b"\r\n")[0])

    def test_http_api_methods_never_get_shell_and_unsafe_paths_rejected(self):
        expected, version = self.receive()
        local.select(self.root, version, expected)
        with self.server() as server:
            for path in ("/api", "/api/clinical-note/analyze?SYNTHETIC_SECRET=1", "/%61pi/x"):
                for method in ("GET", "POST", "HEAD", "OPTIONS"):
                    status, headers, body = self.request(server, path, method)
                    self.assertEqual(status, 503)
                    self.assertEqual(headers["Content-Type"], "application/json")
                    self.assertNotIn(b"synthetic fixture", body)
            for path in ("/../outside", "/%2e%2e/outside", "/%252e%252e/outside", "/.env", "/assets/main.js:stream", "/assets%5cmain.js"):
                self.assertEqual(self.request(server, path, headers={"Accept": "text/html"})[0], 400)
            self.assertEqual(self.request(server, "/assets/missing.js")[0], 404)
            self.assertEqual(self.request(server, "/assets/")[0], 400)
            self.assertEqual(self.request(server, "/", "POST")[0], 405)

    def test_real_http_update_rollback_preserves_existing_server(self):
        first, version_a = self.receive()
        second, version_b = self.receive("b" * 40)
        local.select(self.root, version_a, first)
        with self.server() as server_a:
            local.select(self.root, version_b, second)
            with self.server() as server_b:
                self.assertNotEqual(server_a.server_port, server_b.server_port)
                self.assertEqual(self.request(server_a, "/assets/main.js")[2], b"a" * 40)
                self.assertEqual(self.request(server_b, "/assets/main.js")[2], b"b" * 40)
                local.select(self.root, version_a, first)
                with self.server() as rollback:
                    self.assertEqual(self.request(rollback, "/assets/main.js")[2], b"a" * 40)
                    ports = json.loads((self.root / "used-ports.json").read_text())
                    self.assertEqual(len(ports), 3)
                    self.assertEqual(len(set(ports)), 3)
                    self.assertEqual(json.loads(self.request(rollback, "/__local_release__")[2])["version"], version_a)
        self.assertEqual(len(list((self.root / "releases").iterdir())), 2)

    def test_served_file_tampering_fails_closed_and_bad_ledger_blocks(self):
        expected, version = self.receive()
        local.select(self.root, version, expected)
        with self.server() as server:
            (server.directory / "assets/main.js").write_bytes(b"tampered")
            self.assertEqual(self.request(server, "/assets/main.js")[0], 400)
        (self.root / "used-ports.json").write_text('[true]')
        with self.assertRaises(local.ReleaseError):
            local.make_server(self.root)

    def test_invalid_ledger_blocks_a_valid_release(self):
        expected, version = self.receive()
        local.select(self.root, version, expected)
        (self.root / "used-ports.json").write_text('[true]')
        with self.assertRaises(local.ReleaseError):
            local.make_server(self.root)


if __name__ == "__main__":
    unittest.main(verbosity=2)
