"""Bounded, static-only local release custody. No clinical API or cloud transport."""
from __future__ import annotations

import argparse
import base64
from contextlib import contextmanager
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from html.parser import HTMLParser
import json
import mimetypes
import os
from pathlib import Path
import re
import shutil
import stat
import struct
import subprocess
import tempfile
import threading
from urllib.parse import unquote, urlsplit
import uuid
import zipfile

SCHEMA = "emergency.local-release.v1"
INDIVIDUAL_SCHEMA = "emergency.individual-release.v2"
INDIVIDUAL_CAPABILITIES = ["individual-local", "offline-deterministic-api", "no-remote-case-processing"]
MAX_FILES = 2048
MAX_FILE = 32 * 1024 * 1024
MAX_TOTAL = 256 * 1024 * 1024
MAX_ARCHIVE = MAX_TOTAL + 4 * 1024 * 1024
MAX_MANIFEST = 1024 * 1024
MAX_CENTRAL_DIRECTORY = 1024 * 1024
HEX = re.compile(r"[a-f0-9]{64}\Z")
SHA = re.compile(r"[a-f0-9]{40}\Z")
VERSION = re.compile(r"[a-f0-9]{40}-[a-f0-9]{16}\Z")
RESERVED = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}
CSP = ("default-src 'none'; script-src 'self'{inline}; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; "
       "font-src 'self'; connect-src 'self'; worker-src 'self'; manifest-src 'self'; "
       "object-src 'none'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'")


class ReleaseError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ReleaseError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical_json(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode()


def object_json(data):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "Duplicate JSON key")
            result[key] = value
        return result
    try:
        return json.loads(data, object_pairs_hook=unique, parse_constant=lambda _: (_ for _ in ()).throw(ReleaseError("Invalid JSON number")))
    except (ValueError, UnicodeError) as exc:
        raise ReleaseError("Invalid JSON object") from exc


def safe_name(name):
    require(isinstance(name, str) and 0 < len(name) <= 240, "Invalid archive path")
    require(not any(ord(c) < 32 or ord(c) == 127 for c in name), "Control character in path")
    require("\\" not in name and ":" not in name and "%" not in name, "Nonportable path")
    require(bool(re.fullmatch(r"[A-Za-z0-9_./@+\-]+", name)), "Path must use the portable ASCII subset")
    parts = name.split("/")
    require(all(p not in {"", ".", ".."} and p == p.rstrip(" .") for p in parts), "Unsafe path component")
    require(all(p.split(".")[0].upper() not in RESERVED for p in parts), "Reserved Windows path")
    require(all(not p.startswith(".") for p in parts), "Hidden path is not permitted")
    return name


def no_links(path):
    """Reject links/reparse points in all existing ancestors before resolving."""
    absolute = Path(os.path.abspath(path))
    for item in (absolute, *absolute.parents):
        if item.exists() or item.is_symlink():
            info = item.lstat()
            require(not stat.S_ISLNK(info.st_mode) and not (getattr(info, "st_file_attributes", 0) & 1024), "Link/reparse path is not permitted")
    return absolute


def regular_bytes(path, limit=MAX_FILE):
    path = no_links(path)
    require(path.is_file() and path.stat().st_size <= limit, "Missing or oversized regular file")
    data = path.read_bytes()
    require(len(data) <= limit, "File grew beyond limit")
    return data


class InlineScripts(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.collect = False
        self.buffer = []
        self.hashes = []

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            self.collect = not any(key == "src" for key, _ in attrs)
            self.buffer = []

    def handle_data(self, data):
        if self.collect:
            self.buffer.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self.collect:
            # HTML input preprocessing normalizes CRLF and lone CR before the
            # browser computes an inline-script CSP hash; preserve that semantic.
            code = "".join(self.buffer).replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
            self.hashes.append("'sha256-" + base64.b64encode(hashlib.sha256(code).digest()).decode("ascii") + "'")
            self.collect = False


def policy(index):
    scripts = InlineScripts()
    scripts.feed(index.decode("utf-8"))
    require(not scripts.collect, "Unclosed inline script")
    return CSP.format(inline="".join(" " + value for value in sorted(set(scripts.hashes))))


def read_manifest(data, expected):
    require(isinstance(expected, str) and bool(HEX.fullmatch(expected)), "A separately trusted manifest SHA-256 is required")
    require(len(data) <= MAX_MANIFEST and digest(data) == expected, "Manifest digest mismatch")
    value = object_json(data)
    require(type(value) is dict, "Invalid manifest object")
    individual = value.get("schema") == INDIVIDUAL_SCHEMA
    fields = {"schema", "source_sha", "capabilities", "files"} | ({"release_counter"} if individual else set())
    require(set(value) == fields, "Unexpected manifest fields")
    require(value["schema"] in {SCHEMA, INDIVIDUAL_SCHEMA} and type(value["source_sha"]) is str and bool(SHA.fullmatch(value["source_sha"])), "Invalid source identity")
    expected_capabilities = INDIVIDUAL_CAPABILITIES if individual else ["static-reference-partial", "no-clinical-api", "no-remote-case-processing"]
    require(value["capabilities"] == expected_capabilities, "Unexpected release capabilities")
    if individual:
        require(type(value["release_counter"]) is int and 1 <= value["release_counter"] <= 2**53 - 1, "Invalid release counter")
    files = value["files"]
    require(type(files) is list and 1 <= len(files) <= MAX_FILES, "Invalid file inventory")
    names, total, result = set(), 0, {}
    for item in files:
        require(type(item) is dict and set(item) == {"path", "size", "sha256"}, "Invalid file descriptor")
        name = safe_name(item["path"])
        require(name.casefold() != "manifest.json", "Reserved manifest path")
        require(name.casefold() not in names, "Duplicate/colliding file path")
        require(type(item["size"]) is int and 0 <= item["size"] <= MAX_FILE and type(item["sha256"]) is str and bool(HEX.fullmatch(item["sha256"])), "Invalid file size or hash")
        names.add(name.casefold())
        total += item["size"]
        result[name] = item
    require(total <= MAX_TOTAL and "index.html" in result, "Release size/index is invalid")
    for name in result:
        parts = name.split("/")
        require(not any("/".join(parts[:i]).casefold() in names for i in range(1, len(parts))), "File/directory path collision")
    return value, result


def version_id(manifest, expected):
    return f"{manifest['source_sha']}-{expected[:16]}"


def package(dist, source_root, output):
    """Package an already built, clean-source artifact; not a build attestation."""
    dist, source_root, output = no_links(dist), no_links(source_root), no_links(output)
    require(dist.is_dir() and not output.exists(), "Dist missing or output already exists")
    def git(*args):
        environment = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        environment.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="NUL" if os.name == "nt" else "/dev/null", GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0")
        return subprocess.check_output(["git", "--no-pager", "-c", "core.fsmonitor=false", "-c", "core.autocrlf=false", *args], cwd=source_root, env=environment, text=True, timeout=30).strip()
    # Git for Windows expands native 8.3 aliases (e.g. RUNNER~1) in its root
    # output. Compare directory identities, never their spellings. Validate both
    # paths first so a symlink/junction is not accepted merely by samefile().
    require((source_root / ".git").exists() and os.path.samefile(no_links(git("rev-parse", "--show-toplevel")), source_root), "Source root must be its own checkout")
    source = git("rev-parse", "HEAD")
    require(bool(SHA.fullmatch(source)) and not git("status", "--porcelain", "--untracked-files=normal"), "Source checkout must be clean")
    require(not any(k.startswith("VITE_") or k in {"EMERGENCY_LOCAL_REVIEW", "EMERGENCY_LOCAL_API_TOKEN"} for k in os.environ), "Local package requires an explicit environment without API/LAB overrides")
    require(not any((source_root / "app" / name).exists() for name in (".env", ".env.local", ".env.production", ".env.production.local")), "Implicit Vite production environment files are not accepted")
    files, contents, total = [], {}, 0
    for path in sorted(dist.rglob("*")):
        no_links(path)
        if path.is_dir():
            continue
        name = safe_name(path.relative_to(dist).as_posix())
        # Audit-only maps are not runtime resources and are never shipped.
        if name.endswith(".map"):
            continue
        require(path.suffix in {".js", ".mjs", ".css", ".html", ".svg", ".png", ".json", ".woff2", ".webmanifest", ".ico"}, "Unexpected distribution file type")
        data = regular_bytes(path)
        total += len(data)
        require(len(files) < MAX_FILES and total <= MAX_TOTAL, "Distribution size limit")
        contents[name] = data
        files.append({"path": name, "size": len(data), "sha256": digest(data)})
    require(any(source.encode() in data for name, data in contents.items() if name.endswith((".js", ".mjs"))), "Build does not contain the claimed source revision")
    manifest = {"schema": SCHEMA, "source_sha": source, "capabilities": ["static-reference-partial", "no-clinical-api", "no-remote-case-processing"], "files": files}
    raw = canonical_json(manifest)
    expected = digest(raw)
    read_manifest(raw, expected)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as destination, zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in {"manifest.json": raw, **contents}.items():
            info = zipfile.ZipInfo(name, (2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            archive.writestr(info, data)
    require(output.stat().st_size <= MAX_ARCHIVE, "Archive exceeds limit")
    return {"version": version_id(manifest, expected), "manifest_sha256": expected, "zip_sha256": digest(regular_bytes(output, MAX_ARCHIVE)), "files": len(files), "source_sha": source, "build_attestation": "NOT_INDEPENDENTLY_ATTESTED; clean checkout and embedded revision verified; retain actual build log"}


@contextmanager
def writer(root):
    root = no_links(root)
    root.mkdir(parents=True, exist_ok=True)
    lock = root / "writer.lock"
    no_links(lock)
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise ReleaseError("Another writer or unreviewed stale lock exists") from exc
    try:
        os.write(descriptor, str(os.getpid()).encode())
        os.close(descriptor)
        yield root
    finally:
        lock.unlink()


def atomic_json(path, value):
    no_links(path)
    temporary = path.parent / f"pending-{uuid.uuid4().hex}.json"
    try:
        with temporary.open("xb") as handle:
            handle.write(canonical_json(value))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def verify_directory(directory, expected):
    directory = no_links(directory)
    raw = regular_bytes(directory / "manifest.json", MAX_MANIFEST)
    manifest, files = read_manifest(raw, expected)
    actual = set()
    for path in directory.rglob("*"):
        no_links(path)
        if path.is_dir():
            continue
        name = safe_name(path.relative_to(directory).as_posix())
        actual.add(name)
        if name == "manifest.json":
            continue
        require(name in files, "Unmanifested release file")
        data = regular_bytes(path)
        require(len(data) == files[name]["size"] and digest(data) == files[name]["sha256"], "Release bytes mismatch")
    require(actual == {"manifest.json", *files}, "Release file set mismatch")
    return manifest, files


def preflight_zip(path):
    """Bound central metadata before ZipFile allocates ZipInfo objects.

    Only the plain ZIP format emitted by package() is accepted: no ZIP64,
    multipart, archive comments, entry extras/comments or streaming descriptors.
    Count actual central records too; an attacker can lie in the EOCD count.
    """
    with Path(path).open("rb") as handle:
        size = os.fstat(handle.fileno()).st_size
        require(22 <= size <= MAX_ARCHIVE, "Archive size limit")
        handle.seek(size - 22)
        end = handle.read(22)
        signature, disk, central_disk, disk_count, count, central_size, offset, comment = struct.unpack("<4s4H2IH", end)
        require(signature == b"PK\x05\x06" and disk == central_disk == comment == 0, "Only single-disk plain ZIP archives are accepted")
        # ZipFile otherwise lets a ZIP64 locator override the 32-bit EOCD even
        # when the ordinary EOCD has no sentinel fields. Reject before parsing.
        if size >= 42:
            handle.seek(size - 42)
            require(handle.read(4) != b"PK\x06\x07", "ZIP64 locator is not accepted")
        require(disk_count == count and 1 <= count <= MAX_FILES + 1 and count != 65535, "ZIP entry count limit")
        require(0 < central_size <= MAX_CENTRAL_DIRECTORY and offset != 0xFFFFFFFF and offset + central_size == size - 22, "ZIP central directory limit or offset")
        handle.seek(offset)
        central = handle.read(central_size)
        position, observed = 0, 0
        while position < len(central):
            require(position + 46 <= len(central), "Truncated central ZIP record")
            row = struct.unpack_from("<4s6H3I5H2I", central, position)
            observed += 1
            require(observed <= MAX_FILES + 1 and row[0] == b"PK\x01\x02", "Invalid or excessive central ZIP records")
            require(row[3] & ~0x800 == 0 and row[4] in {zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED}, "Unsupported ZIP flags or compression")
            require(row[8] != 0xFFFFFFFF and row[9] <= MAX_FILE and row[13] == 0 and row[16] < offset, "ZIP64 or invalid file metadata")
            require(1 <= row[10] <= 240 and row[11] == row[12] == 0, "Noncanonical ZIP entry metadata")
            try:
                safe_name(central[position + 46:position + 46 + row[10]].decode("ascii"))
            except UnicodeError as exc:
                raise ReleaseError("Nonportable central filename") from exc
            position += 46 + row[10]
            require(position <= len(central), "Truncated central filename")
        require(position == len(central) and observed == count, "Central ZIP count mismatch")


def install(archive_path, root, expected):
    archive_path = no_links(archive_path)
    require(archive_path.is_file() and archive_path.stat().st_size <= MAX_ARCHIVE, "Archive is missing or oversized")
    preflight_zip(archive_path)
    with writer(root) as root, zipfile.ZipFile(archive_path) as archive:
        entries, names, total = {}, set(), 0
        for info in archive.infolist():
            name = safe_name(info.filename)
            require(info.orig_filename == info.filename, "Noncanonical ZIP filename")
            mode = info.external_attr >> 16
            require(not info.is_dir() and stat.S_IFMT(mode) in {0, stat.S_IFREG} and not (info.flag_bits & 1), "Only unencrypted regular ZIP files are accepted")
            require(name.casefold() not in names, "Duplicate/colliding ZIP entry")
            names.add(name.casefold())
            require(info.file_size <= MAX_FILE and info.file_size <= max(1024 * 1024, info.compress_size * 1000), "Oversized or suspicious ZIP entry")
            entries[name] = info
            total += info.file_size
            require(len(entries) <= MAX_FILES + 1 and total <= MAX_TOTAL + MAX_MANIFEST, "Archive expansion limit")
        require("manifest.json" in entries and entries["manifest.json"].file_size <= MAX_MANIFEST, "Missing manifest")
        manifest, files = read_manifest(archive.read(entries["manifest.json"]), expected)
        require(set(entries) == {"manifest.json", *files}, "Unexpected/missing ZIP entry")
        releases = no_links(root / "releases")
        releases.mkdir(exist_ok=True)
        version = version_id(manifest, expected)
        destination = no_links(releases / version)
        require(not destination.exists(), "Release already exists; versions are immutable")
        staging = Path(tempfile.mkdtemp(prefix="staging-", dir=root))
        try:
            for name, info in entries.items():
                target = staging / name
                target.parent.mkdir(parents=True, exist_ok=True)
                maximum = MAX_MANIFEST if name == "manifest.json" else files[name]["size"]
                require(info.file_size == maximum if name != "manifest.json" else info.file_size <= maximum, "Declared ZIP size mismatch")
                with archive.open(info) as source, target.open("xb") as output:
                    count = 0
                    while chunk := source.read(65536):
                        count += len(chunk)
                        require(count <= maximum, "Actual expansion limit")
                        output.write(chunk)
            verify_directory(staging, expected)
            os.replace(staging, destination)
        finally:
            if staging.exists():
                shutil.rmtree(staging)
        return {"version": version, "manifest_sha256": expected, "activated": False}


def select(root, version, expected):
    require(isinstance(version, str) and bool(VERSION.fullmatch(version)), "Invalid release version")
    with writer(root) as root:
        manifest, _ = verify_directory(root / "releases" / version, expected)
        require(version == version_id(manifest, expected), "Version/manifest identity mismatch")
        atomic_json(root / "active.json", {"version": version, "manifest_sha256": expected})
    return {"version": version, "active_for_next_launch": True, "open_episodes_changed": False}


def active_snapshot(root):
    root = no_links(root)
    value = object_json(regular_bytes(root / "active.json", 4096))
    require(type(value) is dict and set(value) == {"version", "manifest_sha256"} and type(value["version"]) is str and bool(VERSION.fullmatch(value["version"])), "Invalid active selection")
    directory = root / "releases" / value["version"]
    manifest, files = verify_directory(directory, value["manifest_sha256"])
    require(value["version"] == version_id(manifest, value["manifest_sha256"]), "Invalid selected identity")
    return directory, manifest, files, value


class StaticHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"
    server_version = "EmergencyLocalStatic/1"
    sys_version = ""

    def log_message(self, *_):
        pass  # Never log request path/query/headers or clinical input.

    def log_error(self, *_):
        pass

    def send_error(self, code, message=None, explain=None):
        self.respond(code, b'{"error":"request_rejected"}', "application/json")

    def respond(self, code, body, content_type):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Security-Policy", self.server.policy)
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Cross-Origin-Resource-Policy", "same-origin")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def handle_request(self):
        hosts = self.headers.get_all("Host", [])
        origins = self.headers.get_all("Origin", [])
        sites = self.headers.get_all("Sec-Fetch-Site", [])
        host = f"127.0.0.1:{self.server.server_port}"
        trusted = self.client_address[0] == "127.0.0.1" and hosts == [host] and (not origins or origins == [f"http://{host}"]) and len(sites) <= 1 and (not sites or sites[0] in {"same-origin", "same-site", "none"})
        if not trusted:
            return self.respond(403, b'{"error":"origin_rejected"}', "application/json")
        try:
            require(len(self.path) <= 4096 and self.path.startswith("/") and not self.path.startswith("//"), "Invalid request target")
            target = urlsplit(self.path)
            require(not target.scheme and not target.netloc and not target.fragment, "Invalid target")
            path = unquote(target.path, errors="strict")
            require("%" not in path and "\\" not in path and not any(ord(c) < 32 for c in path), "Invalid decoded path")
            if path == "/api" or path.startswith("/api/"):
                return self.respond(503, b'{"error":"clinical_api_unavailable","scope":"static_reference_only"}', "application/json")
            if self.command not in {"GET", "HEAD"}:
                return self.respond(405, b'{"error":"method_not_allowed"}', "application/json")
            if path == "/__local_release__":
                return self.respond(200, canonical_json(self.server.identity), "application/json")
            name = "index.html" if path == "/" else safe_name(path[1:])
            if name not in self.server.files:
                # Only extensionless document navigation may receive the SPA shell.
                accepts = self.headers.get("Accept", "")
                if "." in name or "text/html" not in accepts:
                    return self.respond(404, b'{"error":"not_found"}', "application/json")
                name = "index.html"
            data = regular_bytes(self.server.directory / name)
            item = self.server.files[name]
            require(len(data) == item["size"] and digest(data) == item["sha256"], "Static bytes changed")
            media = mimetypes.guess_type(name)[0] or "application/octet-stream"
            if name.endswith((".js", ".mjs")):
                media = "text/javascript"
            elif name.endswith(".webmanifest"):
                media = "application/manifest+json"
            return self.respond(200, data, media)
        except (ReleaseError, UnicodeError, ValueError, OSError):
            return self.respond(400, b'{"error":"request_or_release_rejected"}', "application/json")

    do_GET = handle_request
    do_HEAD = handle_request
    do_POST = handle_request
    do_OPTIONS = handle_request
    do_PUT = handle_request
    do_DELETE = handle_request


class LocalServer(ThreadingHTTPServer):
    daemon_threads = True
    block_on_close = False
    request_queue_size = 8

    def __init__(self, *args):
        self.slots = threading.BoundedSemaphore(16)
        super().__init__(*args)

    def process_request(self, request, client_address):
        if not self.slots.acquire(blocking=False):
            self.shutdown_request(request)
            return
        try:
            super().process_request(request, client_address)
        except BaseException:
            self.slots.release()
            raise

    def process_request_thread(self, request, client_address):
        try:
            super().process_request_thread(request, client_address)
        finally:
            self.slots.release()

    def get_request(self):
        request, peer = super().get_request()
        request.settimeout(5)
        return request, peer

    def handle_error(self, *_):
        pass


def make_server(root):
    """New origin on every launch: never replace bytes under a previous PWA origin."""
    with writer(root) as root:
        directory, manifest, files, selected = active_snapshot(root)
        require(manifest["schema"] == SCHEMA, "Individual releases require the authenticated stable launcher")
        content_policy = policy(regular_bytes(directory / "index.html"))
        ledger = root / "used-ports.json"
        used = object_json(regular_bytes(ledger, MAX_MANIFEST)) if ledger.exists() else []
        require(type(used) is list and len(used) <= 65535 and all(type(p) is int and 1 <= p <= 65535 for p in used) and len(used) == len(set(used)), "Invalid origin ledger")
        server = None
        for _ in range(128):
            candidate = LocalServer(("127.0.0.1", 0), StaticHandler)
            if candidate.server_port not in used:
                server = candidate
                break
            candidate.server_close()
        require(server is not None, "No fresh local origin available; browser-safe launch blocked")
        try:
            atomic_json(ledger, [*used, server.server_port])
        except BaseException:
            server.server_close()
            raise
        server.directory, server.files = directory, files
        server.policy = content_policy
        server.identity = {**selected, "source_sha": manifest["source_sha"], "capabilities": manifest["capabilities"], "browser_upgrade": "NEW_ORIGIN_ONLY_WITHIN_THIS_RETAINED_INSTALLATION_LEDGER; existing tabs/bookmarks/installations stay on their original release", "browser_activation": "PENDING_ACTUAL_PAGE_IDENTITY_VERIFICATION; no global browser cache guarantee", "clinical": "CLINICALLY_PENDING", "release": "NO_GO_CLINICAL_RELEASE"}
        return server


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("package")
    build.add_argument("--dist", required=True)
    build.add_argument("--source-root", required=True)
    build.add_argument("--output", required=True)
    intake = commands.add_parser("install")
    intake.add_argument("archive")
    for name in ("activate", "rollback"):
        sub = commands.add_parser(name)
        sub.add_argument("version")
    commands.add_parser("serve")
    for name, sub in commands.choices.items():
        if name != "package":
            sub.add_argument("--root", required=True)
        if name in {"install", "activate", "rollback"}:
            sub.add_argument("--expected-manifest-sha256", required=True)
    args = parser.parse_args()
    try:
        if args.command == "package":
            result = package(args.dist, args.source_root, args.output)
        elif args.command == "install":
            result = install(args.archive, args.root, args.expected_manifest_sha256)
        elif args.command in {"activate", "rollback"}:
            result = select(args.root, args.version, args.expected_manifest_sha256)
        else:
            with make_server(args.root) as server:
                print(json.dumps({"url": f"http://127.0.0.1:{server.server_port}", **server.identity}), flush=True)
                server.serve_forever()
            return
        print(json.dumps(result))
    except (ReleaseError, OSError, zipfile.BadZipFile, subprocess.SubprocessError) as error:
        detail = f": {error}" if isinstance(error, ReleaseError) else ""
        parser.exit(1, f"Local release operation failed ({type(error).__name__}){detail}; no clinical API was enabled.\n")


if __name__ == "__main__":
    main()
