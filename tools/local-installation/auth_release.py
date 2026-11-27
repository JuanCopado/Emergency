"""Ed25519 owner-pinned release authentication; no self-trusting archive keys."""
from __future__ import annotations

import base64
import ctypes
from ctypes import wintypes
import hashlib
import json
import os
from pathlib import Path
import stat
import tempfile
import zipfile

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

import local_installation as local

PUBLIC_SCHEMA = "emergency.publisher-public.v1"
SIGNATURE_SCHEMA = "emergency.release-signature.v1"
DOMAIN = b"EMERGENCY-INDIVIDUAL-RELEASE-v2\x00"


def _b64(raw):
    return base64.b64encode(raw).decode("ascii")


def _decode(value, length):
    local.require(type(value) is str and len(value) <= 1024, "Invalid encoded key/signature")
    try:
        raw = base64.b64decode(value, validate=True)
    except (ValueError, TypeError) as exc:
        raise local.ReleaseError("Invalid base64") from exc
    local.require(len(raw) == length and _b64(raw) == value, "Invalid encoded length")
    return raw


def public_document(key):
    raw = key.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    return {"schema": PUBLIC_SCHEMA, "algorithm": "Ed25519", "key_base64": _b64(raw),
            "fingerprint": hashlib.sha256(raw).hexdigest()}


def read_public(data, expected_fingerprint):
    value = local.object_json(data)
    local.require(type(value) is dict and set(value) == {"schema", "algorithm", "key_base64", "fingerprint"}, "Invalid publisher document")
    local.require(value["schema"] == PUBLIC_SCHEMA and value["algorithm"] == "Ed25519", "Unsupported publisher key")
    raw = _decode(value["key_base64"], 32)
    fingerprint = hashlib.sha256(raw).hexdigest()
    local.require(type(expected_fingerprint) is str and bool(local.HEX.fullmatch(expected_fingerprint))
                  and value["fingerprint"] == expected_fingerprint == fingerprint, "Publisher fingerprint mismatch")
    return Ed25519PublicKey.from_public_bytes(raw), value


def _dpapi(raw, *, decrypt=False):
    """Current Windows logon only. No machine-wide flag or interactive prompt."""
    local.require(os.name == "nt", "Publisher key storage requires Windows DPAPI")

    class Blob(ctypes.Structure):
        _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_ubyte))]

    data = (ctypes.c_ubyte * len(raw)).from_buffer_copy(raw)
    incoming = Blob(len(raw), data)
    outgoing = Blob()
    crypt = ctypes.WinDLL("crypt32", use_last_error=True)
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.LocalFree.argtypes = [ctypes.c_void_p]
    kernel.LocalFree.restype = ctypes.c_void_p
    if decrypt:
        function = crypt.CryptUnprotectData
        function.argtypes = [ctypes.POINTER(Blob), ctypes.c_void_p, ctypes.c_void_p,
                             ctypes.c_void_p, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(Blob)]
        arguments = (ctypes.byref(incoming), None, None, None, None, 1, ctypes.byref(outgoing))
    else:
        function = crypt.CryptProtectData
        function.argtypes = [ctypes.POINTER(Blob), wintypes.LPCWSTR, ctypes.c_void_p,
                             ctypes.c_void_p, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(Blob)]
        arguments = (ctypes.byref(incoming), "Emergency owner release signing", None, None, None, 1, ctypes.byref(outgoing))
    function.restype = wintypes.BOOL
    if not function(*arguments):
        raise local.ReleaseError("Windows could not protect/unprotect the publisher key")
    try:
        return ctypes.string_at(outgoing.pbData, outgoing.cbData)
    finally:
        kernel.LocalFree(ctypes.cast(outgoing.pbData, ctypes.c_void_p))


def create_publisher(directory):
    """Store encrypted private material outside release/archive trees."""
    directory = local.no_links(directory)
    directory.mkdir(parents=True, exist_ok=True)
    public_path, private_path = directory / "publisher-public.json", directory / "publisher-private.dpapi"
    local.no_links(public_path)
    local.no_links(private_path)
    local.require(not public_path.exists() and not private_path.exists(), "Publisher already exists; never replace a trust root automatically")
    key = Ed25519PrivateKey.generate()
    raw = key.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw, serialization.NoEncryption())
    protected = _dpapi(raw)
    with private_path.open("xb") as handle:
        handle.write(protected)
    try:
        with public_path.open("xb") as handle:
            handle.write(local.canonical_json(public_document(key.public_key())))
    except BaseException:
        private_path.unlink(missing_ok=True)
        raise
    return {"public_key_path": str(public_path), "private_key_path": str(private_path),
            "fingerprint": public_document(key.public_key())["fingerprint"], "private_protection": "Windows DPAPI CurrentUser"}


def load_private(path):
    raw = _dpapi(local.regular_bytes(path, 16384), decrypt=True)
    local.require(len(raw) == 32, "Invalid protected publisher key")
    key = Ed25519PrivateKey.from_private_bytes(raw)
    registered = local.object_json(local.regular_bytes(Path(path).parent / "publisher-public.json", 4096))
    local.require(registered == public_document(key.public_key()), "Protected private key does not match registered publisher")
    return key


def sign_manifest(raw, key):
    expected = local.digest(raw)
    manifest, _ = local.read_manifest(raw, expected)
    local.require(manifest["schema"] == local.INDIVIDUAL_SCHEMA, "Only individual manifests are signed here")
    return {"schema": SIGNATURE_SCHEMA, "algorithm": "Ed25519",
            "publisher_fingerprint": public_document(key.public_key())["fingerprint"],
            "manifest_sha256": expected, "signature": _b64(key.sign(DOMAIN + raw))}


def authenticate(raw, envelope, public_data, expected_fingerprint):
    key, _ = read_public(public_data, expected_fingerprint)
    value = local.object_json(envelope)
    local.require(type(value) is dict and set(value) == {"schema", "algorithm", "publisher_fingerprint", "manifest_sha256", "signature"}, "Invalid signature envelope")
    local.require(value["schema"] == SIGNATURE_SCHEMA and value["algorithm"] == "Ed25519"
                  and value["publisher_fingerprint"] == expected_fingerprint and value["manifest_sha256"] == local.digest(raw), "Signature binding mismatch")
    signature = _decode(value["signature"], 64)
    try:
        key.verify(signature, DOMAIN + raw)
    except InvalidSignature as exc:
        raise local.ReleaseError("Publisher signature rejected") from exc
    manifest, files = local.read_manifest(raw, value["manifest_sha256"])
    local.require(manifest["schema"] == local.INDIVIDUAL_SCHEMA, "Unsigned/legacy individual activation is forbidden")
    return manifest, files, value["manifest_sha256"]


def _pin(root, publisher_file, fingerprint):
    public_data = local.regular_bytes(publisher_file, 4096)
    _, document = read_public(public_data, fingerprint)
    with local.writer(root) as directory:
        path = directory / "publisher-trust.json"
        if path.exists():
            old = local.object_json(local.regular_bytes(path, 4096))
            local.require(old == document, "Pinned publisher cannot be replaced by an update")
        else:
            local.atomic_json(path, document)
    return local.canonical_json(document)


def trusted_public(root):
    raw = local.regular_bytes(local.no_links(root) / "publisher-trust.json", 4096)
    document = local.object_json(raw)
    local.require(type(document) is dict and type(document.get("fingerprint")) is str, "Missing publisher trust root")
    read_public(raw, document["fingerprint"])
    return raw, document["fingerprint"]


def inspect_archive(archive):
    archive = local.no_links(archive)
    local.preflight_zip(archive)
    with zipfile.ZipFile(archive) as package:
        candidates = [i for i in package.infolist() if i.filename == "manifest.json"]
        local.require(len(candidates) == 1 and candidates[0].file_size <= local.MAX_MANIFEST, "Invalid manifest entry")
        return package.read(candidates[0])


def _maximum(root):
    path = Path(root) / "release-sequence.json"
    if not path.exists():
        return 0
    sequence = local.object_json(local.regular_bytes(path, 4096))
    local.require(type(sequence) is dict and set(sequence) == {"maximum"}
                  and type(sequence["maximum"]) is int and sequence["maximum"] > 0,
                  "Invalid release sequence")
    return sequence["maximum"]


def install_signed(archive, signature_file, root, *, publisher_file=None, fingerprint=None, for_rollback=False):
    """Verify publisher before extraction or executing any packaged code."""
    if publisher_file is not None:
        public_data = local.regular_bytes(publisher_file, 4096)
        read_public(public_data, fingerprint)
    else:
        public_data, fingerprint = trusted_public(root)
    raw = inspect_archive(archive)
    envelope = local.regular_bytes(signature_file, 4096)
    manifest, _, expected = authenticate(raw, envelope, public_data, fingerprint)
    root = local.no_links(root)
    sequence_file = root / "release-sequence.json"
    maximum = _maximum(root)
    version = local.version_id(manifest, expected)
    destination = local.no_links(root / "releases" / version)
    if destination.exists():
        # Runtime preparation happens after intake. Retry only an authenticated,
        # unchanged existing release; never treat a matching manifest alone as
        # proof that either the installed payload or the incoming ZIP is intact.
        with local.writer(root):
            pinned, pinned_fingerprint = trusted_public(root)
            local.require(pinned_fingerprint == fingerprint
                          and local.object_json(pinned) == local.object_json(public_data),
                          "Pinned publisher cannot be replaced by an update")
            local.require(for_rollback or manifest["release_counter"] == _maximum(root),
                          "Older update requires explicit signed rollback intake")
            _, _, _, installed = verify_version(root, version)
            local.require(installed["manifest_sha256"] == expected, "Existing signed release differs")
            with tempfile.TemporaryDirectory(prefix="emergency-resume-verification-") as temporary:
                local.install(archive, Path(temporary) / "verification", expected)
        return {**installed, "activated": False, "resumed": True,
                "authenticated_publisher": fingerprint, "release_counter": manifest["release_counter"]}
    local.require(for_rollback or manifest["release_counter"] > maximum,
                  "Older/equal update requires explicit signed rollback intake")
    if publisher_file is not None:
        _pin(root, publisher_file, fingerprint)
    # Authentication has completed. Legacy extraction retains its independent
    # file-set, ZIP/path/resource and byte-integrity checks for this v2 manifest.
    result = local.install(archive, root, expected)
    with local.writer(root) as directory:
        signatures = local.no_links(directory / "signatures")
        signatures.mkdir(exist_ok=True)
        local.atomic_json(signatures / (result["version"] + ".json"), local.object_json(envelope))
        previous = _maximum(directory)
        local.atomic_json(sequence_file, {"maximum": max(previous, manifest["release_counter"])})
    return {**result, "authenticated_publisher": fingerprint, "release_counter": manifest["release_counter"]}


def verify_version(root, version):
    local.require(type(version) is str and bool(local.VERSION.fullmatch(version)), "Invalid signed release version")
    directory = local.no_links(Path(root) / "releases" / version)
    public_data, fingerprint = trusted_public(root)
    raw = local.regular_bytes(directory / "manifest.json", local.MAX_MANIFEST)
    envelope = local.regular_bytes(Path(root) / "signatures" / (version + ".json"), 4096)
    manifest, files, expected = authenticate(raw, envelope, public_data, fingerprint)
    local.require(version == local.version_id(manifest, expected), "Signed version identity mismatch")
    local.verify_directory(directory, expected)
    return directory, manifest, files, {"version": version, "manifest_sha256": expected}


def active_signed_snapshot(root):
    selected = local.object_json(local.regular_bytes(Path(root) / "active.json", 4096))
    local.require(type(selected) is dict and set(selected) == {"version", "manifest_sha256"}, "Invalid active selection")
    result = verify_version(root, selected["version"])
    local.require(result[3] == selected, "Active selection does not match authenticated release")
    return result


def activate_signed(root, version, *, rollback=False):
    with local.writer(root) as directory:
        _, manifest, _, selected = verify_version(directory, version)
        active = directory / "active.json"
        previous = None
        if active.exists():
            try:
                previous = active_signed_snapshot(directory)
            except local.ReleaseError:
                # Explicit rollback must still recover from a corrupt current
                # payload. The requested rollback target was verified above.
                if not rollback:
                    raise
        unchanged = previous is not None and previous[3] == selected
        if not unchanged:
            local.require(rollback or manifest["release_counter"] == _maximum(directory),
                          "Older activation requires explicit rollback")
            if previous is not None and not rollback:
                local.require(manifest["release_counter"] > previous[1]["release_counter"],
                              "Downgrade requires explicit rollback")
            local.atomic_json(active, selected)
    return {**selected, "release_counter": manifest["release_counter"], "rollback": rollback,
            "unchanged": unchanged, "active_for_next_launch": True, "open_episodes_changed": False}


def build_signed(dist, source_root, wheelhouse, output, counter, private_key_file):
    from backend_bundle import collect_backend
    output = local.no_links(output)
    signature_path = output.with_suffix(output.suffix + ".sig.json")
    local.require(not output.exists() and not signature_path.exists(), "Release output already exists")
    with tempfile.TemporaryDirectory(prefix="emergency-static-stage-") as temporary:
        web_archive = Path(temporary) / "web.zip"
        web = local.package(dist, source_root, web_archive)
        with zipfile.ZipFile(web_archive) as package:
            contents = {i.filename: package.read(i) for i in package.infolist() if i.filename != "manifest.json"}
    from html.parser import HTMLParser
    class BuildMarker(HTMLParser):
        enabled = False
        def handle_starttag(self, tag, attributes):
            attrs = dict(attributes)
            if tag == "meta" and attrs.get("name") == "emergency-individual-installation" and attrs.get("content") == "enabled":
                self.enabled = True
    marker = BuildMarker()
    marker.feed(contents["index.html"].decode("utf-8"))
    local.require(marker.enabled, "Build was not configured for authenticated individual installation")
    backend = collect_backend(source_root, wheelhouse, revision=web["source_sha"])
    inventory = local.object_json(backend["backend/BACKEND_MANIFEST.json"])
    local.require(inventory.get("source_sha") == web["source_sha"], "Backend revision differs from frontend")
    rows = {row["path"]: row for row in inventory["files"]}
    local.require(len(rows) == len(inventory["files"])
                  and set(rows) == set(backend) - {"backend/BACKEND_MANIFEST.json"},
                  "Backend inventory differs from packaged files")
    for name, row in rows.items():
        local.require(row["bytes"] == len(backend[name]) and row["sha256"] == local.digest(backend[name]),
                      "Backend inventory bytes differ")
    # collect_backend reads exact Git blobs at source_sha. Do not overwrite them
    # with checkout bytes (e.g. CRLF), which would invalidate its inner inventory.
    for name in ["auth_release.py", "individual_cli.py", "local_installation.py", "stable_launcher.py", "backend_runtime.py", "backend_bundle.py"]:
        local.require("backend/launcher/" + name in rows, "Missing canonical launcher")
    contents.update(backend)
    files = [{"path": local.safe_name(name), "size": len(data), "sha256": local.digest(data)} for name, data in sorted(contents.items())]
    manifest = {"schema": local.INDIVIDUAL_SCHEMA, "source_sha": web["source_sha"],
                "capabilities": local.INDIVIDUAL_CAPABILITIES, "release_counter": counter, "files": files}
    raw = local.canonical_json(manifest)
    local.read_manifest(raw, local.digest(raw))
    signature = sign_manifest(raw, load_private(private_key_file))
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as handle, zipfile.ZipFile(handle, "w", compression=zipfile.ZIP_DEFLATED) as package:
        for name, data in {"manifest.json": raw, **contents}.items():
            info = zipfile.ZipInfo(name, (2026, 11, 27, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            package.writestr(info, data)
    local.require(output.stat().st_size <= local.MAX_ARCHIVE, "Signed archive exceeds size bound")
    with signature_path.open("xb") as handle:
        handle.write(local.canonical_json(signature))
    return {"version": local.version_id(manifest, local.digest(raw)), "manifest_sha256": local.digest(raw),
            "publisher_fingerprint": signature["publisher_fingerprint"], "files": len(files), "release_counter": counter,
            "archive": str(output), "signature": str(signature_path), "sha256": local.digest(output.read_bytes())}
