"""Authenticated local releases at a retained origin; no automatic episode reload."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import socket
import time
import uuid

import local_installation as local

# Same canonical transfer envelope as clinical_note_api: 12 MiB upload, base64/metadata allowance.
MAX_REQUEST = 26_165_824
MAX_RESPONSE = 33_554_432
REVISION_HEADER = "X-Emergency-Revision"
ORIGIN_SCHEMA = "emergency.individual-origin.v1"


class RuntimeLease:
    """OS lock survives the lock-file but is released by the OS after a crash."""

    def __init__(self, root):
        target = local.no_links(Path(root) / "runtime.lock")
        self.handle = target.open("a+b")
        self.closed = False
        if target.stat().st_size == 0:
            self.handle.write(b"\0")
            self.handle.flush()
        self.handle.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(self.handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            self.handle.close()
            self.closed = True
            raise local.ReleaseError("This installation already has an active runtime") from exc

    def close(self):
        if self.closed:
            return
        self.closed = True
        try:
            self.handle.seek(0)
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(self.handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.handle.fileno(), fcntl.LOCK_UN)
        finally:
            self.handle.close()


class StableHandler(local.StaticHandler):
    """The browser never receives the backend process token."""

    def trusted_origin(self):
        host = f"127.0.0.1:{self.server.server_port}"
        hosts = self.headers.get_all("Host", [])
        origins = self.headers.get_all("Origin", [])
        sites = self.headers.get_all("Sec-Fetch-Site", [])
        return (self.client_address[0] == "127.0.0.1" and hosts == [host]
                and (not origins or origins == [f"http://{host}"])
                and len(sites) <= 1 and (not sites or sites[0] in {"same-origin", "same-site", "none"}))

    def handle_request(self):
        # Apply origin checks before metadata and before reading any request body.
        if not self.trusted_origin():
            return self.respond(403, b'{"error":"origin_rejected"}', "application/json")
        if self.path.startswith("/api"):
            if len(self.path) > 256 or not re.fullmatch(r"/api(?:/[a-z0-9-]+)*", self.path):
                return self.respond(400, b'{"error":"request_rejected"}', "application/json")
            return self.handle_api()
        if self.path.split("?", 1)[0].startswith(("/backend", "/runtime")):
            return self.respond(404, b'{"error":"not_found"}', "application/json")
        return super().handle_request()

    def handle_api(self):
        if self.path == "/api/blood-gas" or self.path.startswith("/api/blood-gas/"):
            return self.respond(503, b'{"error":"ocr_runtime_not_packaged","error_code":"OCR_RUNTIME_NOT_PACKAGED"}', "application/json")
        if self.command != "POST":
            return self.respond(405, b'{"error":"method_not_allowed"}', "application/json")
        if self.headers.get_all(REVISION_HEADER, []) != [self.server.identity["source_sha"]]:
            return self.respond(409, b'{"error":"local_application_version_changed","error_code":"local_revision_mismatch"}', "application/json")
        if self.server.backend is None:
            return self.respond(503, b'{"error":"clinical_api_unavailable"}', "application/json")
        lengths = self.headers.get_all("Content-Length", [])
        content_types = self.headers.get_all("Content-Type", [])
        if (self.headers.get_all("Transfer-Encoding", []) or len(lengths) != 1
                or not re.fullmatch(r"[0-9]{1,8}", lengths[0])
                or content_types != ["application/json"]):
            return self.respond(400, b'{"error":"request_rejected"}', "application/json")
        size = int(lengths[0])
        if not 0 < size <= MAX_REQUEST:
            return self.respond(413, b'{"error":"request_too_large"}', "application/json")
        try:
            deadline = time.monotonic() + 10
            chunks = bytearray()
            while len(chunks) < size:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError
                self.connection.settimeout(min(5, remaining))
                chunk = self.rfile.read1(min(65536, size - len(chunks)))
                if not chunk:
                    raise ValueError("Incomplete request")
                chunks.extend(chunk)
            payload = local.object_json(bytes(chunks))
            local.require(type(payload) is dict, "Expected JSON object")
        except (ValueError, OSError, RecursionError):
            return self.respond(400, b'{"error":"request_rejected"}', "application/json")
        try:
            status, value = self.server.backend.request(self.path, payload)
            local.require(type(status) is int and 100 <= status <= 599 and type(value) is dict, "Invalid backend response")
            raw = json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode("utf-8")
            local.require(len(raw) <= MAX_RESPONSE, "Backend response exceeds limit")
        except Exception:
            return self.respond(503, b'{"error":"local_backend_unavailable"}', "application/json")
        return self.respond(status, raw, "application/json; charset=utf-8")

    do_GET = handle_request
    do_HEAD = handle_request
    do_POST = handle_request
    do_OPTIONS = handle_request
    do_PUT = handle_request
    do_DELETE = handle_request


class StableServer(local.LocalServer):
    allow_reuse_address = os.name != "nt"
    backend = None
    lease = None

    def server_bind(self):
        if os.name == "nt":
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()

    def server_close(self):
        try:
            super().server_close()
        finally:
            try:
                backend, self.backend = self.backend, None
                if backend is not None:
                    backend.close()
            finally:
                lease, self.lease = self.lease, None
                if lease is not None:
                    lease.close()


def make_stable_server(root, *, verify_release, backend_factory=None):
    """A read-only authenticated verifier is mandatory; no unsigned default path.

    verify_release(root) returns (directory, manifest, descriptors, selection).
    backend_factory(directory, ui_port, revision) starts a private backend session.
    Installation/selection changes only affect a subsequent explicit runtime start.
    """
    root = local.no_links(root)
    local.require(root.is_dir(), "Installation root missing")
    lease = RuntimeLease(root)
    server = None
    try:
        with local.writer(root):
            directory, manifest, files, selected = verify_release(root)
            local.require(bool(local.SHA.fullmatch(manifest["source_sha"])), "Invalid release revision")
            # Private backend source, wheels and runtime material never enter HTTP.
            public = {n: row for n, row in files.items()
                      if not n.startswith(("backend/", "runtime/"))
                      and Path(n).suffix.lower() in {".html", ".js", ".mjs", ".css", ".json", ".svg", ".png", ".ico", ".woff2", ".webmanifest"}}
            local.require("index.html" in public, "Frontend index missing")
            origin_path = root / "stable-origin.json"
            if origin_path.exists():
                origin = local.object_json(local.regular_bytes(origin_path, 4096))
                local.require(type(origin) is dict and set(origin) == {"schema", "port", "installation_id"}
                              and origin["schema"] == ORIGIN_SCHEMA and type(origin["port"]) is int
                              and 1024 <= origin["port"] <= 65535
                              and type(origin["installation_id"]) is str
                              and re.fullmatch(r"[a-f0-9]{32}", origin["installation_id"]), "Invalid stable origin")
                port = origin["port"]
            else:
                origin = {"schema": ORIGIN_SCHEMA, "installation_id": uuid.uuid4().hex}
                port = 0
            try:
                server = StableServer(("127.0.0.1", port), StableHandler)
            except OSError as exc:
                raise local.ReleaseError("Stable local origin is occupied; no replacement origin was chosen") from exc
            server.lease = lease
            if port == 0:
                origin["port"] = server.server_port
                local.atomic_json(origin_path, origin)
            server.directory, server.files = directory, public
            server.policy = local.policy(local.regular_bytes(directory / "index.html"))
            server.identity = {"version": selected["version"], "manifest_sha256": selected["manifest_sha256"],
                               "source_sha": manifest["source_sha"], "installation_id": origin["installation_id"],
                               "capabilities": manifest["capabilities"], "backend_available": False,
                               "update_policy": "EXPLICIT_RUNTIME_RESTART_AND_PER_TAB_RELOAD_CONSENT",
                               "clinical": "CLINICALLY_PENDING", "release": "NO_GO_CLINICAL_RELEASE"}
            if backend_factory is not None:
                server.backend = backend_factory(directory, server.server_port, manifest["source_sha"])
                server.identity["backend_available"] = True
            elif (directory / "backend").exists():
                raise local.ReleaseError("Authenticated release requires a configured local backend")
        return server
    except BaseException:
        if server is not None:
            server.server_close()
        else:
            lease.close()
        raise
