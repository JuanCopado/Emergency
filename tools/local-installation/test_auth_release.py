import base64
import json
import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest import mock
import zipfile

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import auth_release as auth
import local_installation as local


class AuthenticatedReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="emergency-auth-fixture-")
        self.base = Path(self.temporary.name)
        self.root = self.base / "installed"
        self.key = Ed25519PrivateKey.generate()  # Ephemeral synthetic publisher only.
        self.public = auth.public_document(self.key.public_key())
        self.public_path = self.base / "publisher.json"
        self.public_path.write_bytes(local.canonical_json(self.public))
        self.serial = 0

    def tearDown(self):
        self.temporary.cleanup()

    def release(self, counter=1, content=b"<html>synthetic</html>", key=None):
        self.serial += 1
        contents = {"index.html": content, "backend/runtime.json": b'{"fixture":true}'}
        manifest = {"schema": local.INDIVIDUAL_SCHEMA, "source_sha": "a" * 40,
                    "capabilities": local.INDIVIDUAL_CAPABILITIES, "release_counter": counter,
                    "files": [{"path": n, "size": len(b), "sha256": local.digest(b)} for n, b in contents.items()]}
        raw = local.canonical_json(manifest)
        signature = auth.sign_manifest(raw, key or self.key)
        archive = self.base / f"release-{self.serial}.zip"
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as package:
            for name, data in {"manifest.json": raw, **contents}.items():
                info = zipfile.ZipInfo(name)
                info.external_attr = (stat.S_IFREG | 0o644) << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                package.writestr(info, data)
        sig = archive.with_suffix(".sig.json")
        sig.write_bytes(local.canonical_json(signature))
        return archive, sig, manifest, raw

    def install(self, counter=1, **kwargs):
        archive, sig, _, _ = self.release(counter, **kwargs)
        return auth.install_signed(archive, sig, self.root, publisher_file=self.public_path,
                                   fingerprint=self.public["fingerprint"])

    def test_real_ed25519_signature_and_domain_binding(self):
        _, sig, manifest, raw = self.release()
        observed, _, digest = auth.authenticate(raw, sig.read_bytes(), self.public_path.read_bytes(), self.public["fingerprint"])
        self.assertEqual(observed, manifest)
        self.assertEqual(digest, local.digest(raw))
        value = json.loads(sig.read_bytes())
        value["signature"] = base64.b64encode(self.key.sign(raw)).decode()
        with self.assertRaises(local.ReleaseError):
            auth.authenticate(raw, local.canonical_json(value), self.public_path.read_bytes(), self.public["fingerprint"])

    def test_foreign_publisher_cannot_supply_its_own_trust_root(self):
        archive, sig, _, _ = self.release(key=Ed25519PrivateKey.generate())
        with self.assertRaises(local.ReleaseError):
            auth.install_signed(archive, sig, self.root, publisher_file=self.public_path, fingerprint=self.public["fingerprint"])
        self.assertFalse(self.root.exists())

    def test_tampered_signature_fails_before_extraction(self):
        archive, sig, _, _ = self.release()
        value = json.loads(sig.read_bytes())
        value["signature"] = base64.b64encode(b"\x00" * 64).decode()
        sig.write_bytes(local.canonical_json(value))
        with self.assertRaises(local.ReleaseError):
            auth.install_signed(archive, sig, self.root, publisher_file=self.public_path, fingerprint=self.public["fingerprint"])
        self.assertFalse(self.root.exists())

    def test_manifest_tampering_and_duplicate_envelope_fields_rejected(self):
        _, sig, _, raw = self.release()
        for body in [raw.replace(b'"release_counter":1', b'"release_counter":2'), raw+b" "]:
            with self.assertRaises(local.ReleaseError):
                auth.authenticate(body, sig.read_bytes(), self.public_path.read_bytes(), self.public["fingerprint"])
        duplicated = sig.read_bytes().rstrip()[:-1]+b',"algorithm":"Ed25519"}'
        with self.assertRaises(local.ReleaseError):
            auth.authenticate(raw, duplicated, self.public_path.read_bytes(), self.public["fingerprint"])

    def test_publisher_pin_cannot_be_replaced_by_valid_foreign_update(self):
        self.install()
        first_pin = (self.root / "publisher-trust.json").read_bytes()
        foreign = Ed25519PrivateKey.generate()
        other_public = self.base / "other-public.json"
        document = auth.public_document(foreign.public_key())
        other_public.write_bytes(local.canonical_json(document))
        archive, signature, _, _ = self.release(2, key=foreign)
        with self.assertRaises(local.ReleaseError):
            auth.install_signed(archive, signature, self.root, publisher_file=other_public, fingerprint=document["fingerprint"])
        self.assertEqual((self.root / "publisher-trust.json").read_bytes(), first_pin)
        self.assertEqual(len(list((self.root / "releases").iterdir())), 1)

    def test_atomic_activation_update_and_explicit_signed_rollback(self):
        a = self.install(1)
        auth.activate_signed(self.root, a["version"])
        b = self.install(2, content=b"<html>synthetic updated</html>")
        auth.activate_signed(self.root, b["version"])
        with self.assertRaises(local.ReleaseError):
            auth.activate_signed(self.root, a["version"])
        self.assertEqual(auth.active_signed_snapshot(self.root)[3]["version"], b["version"])
        auth.activate_signed(self.root, a["version"], rollback=True)
        self.assertEqual(auth.active_signed_snapshot(self.root)[3]["version"], a["version"])
        self.assertEqual(json.loads((self.root / "release-sequence.json").read_bytes())["maximum"], 2)

    def test_old_signed_update_intake_requires_explicit_rollback_intent(self):
        self.install(2)
        archive, signature, _, _ = self.release(1)
        with self.assertRaises(local.ReleaseError):
            auth.install_signed(archive, signature, self.root)
        result = auth.install_signed(archive, signature, self.root, for_rollback=True)
        self.assertEqual(result["release_counter"], 1)

    def test_runtime_retry_verifies_same_release_without_changing_installation(self):
        archive, signature, _, _ = self.release()
        first = auth.install_signed(archive, signature, self.root, publisher_file=self.public_path,
                                    fingerprint=self.public["fingerprint"])
        # Runtime bootstrap may have failed after the signed intake succeeded.
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        for kwargs in [{}, {"publisher_file": self.public_path, "fingerprint": self.public["fingerprint"]}]:
            resumed = auth.install_signed(archive, signature, self.root, **kwargs)
            self.assertTrue(resumed["resumed"])
            self.assertEqual(resumed["version"], first["version"])
        after = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_crash_between_extraction_signature_and_sequence_writes_is_resumable(self):
        for phase in ("signature", "sequence"):
            with self.subTest(phase=phase):
                self.root = self.base / ("crash-" + phase)
                self.install(1)
                archive, signature, _, _ = self.release(2)
                original_atomic = local.atomic_json

                def interrupt(path, value):
                    if ((phase == "signature" and Path(path).parent.name == "signatures")
                            or (phase == "sequence" and Path(path).name == "release-sequence.json")):
                        raise RuntimeError("synthetic process interruption")
                    return original_atomic(path, value)

                with mock.patch.object(local, "atomic_json", side_effect=interrupt):
                    with self.assertRaises(RuntimeError):
                        auth.install_signed(archive, signature, self.root)
                self.assertEqual(auth._maximum(self.root), 1)
                resumed = auth.install_signed(archive, signature, self.root)
                self.assertTrue(resumed["resumed"])
                self.assertEqual(auth._maximum(self.root), 2)
                self.assertEqual(auth.verify_version(self.root, resumed["version"])[3]["version"], resumed["version"])

    def test_missing_signature_repair_rejects_corrupt_payload_before_writing_metadata(self):
        archive, signature, _, _ = self.release()
        result = auth.install_signed(archive, signature, self.root, publisher_file=self.public_path,
                                     fingerprint=self.public["fingerprint"])
        stored = self.root / "signatures" / (result["version"] + ".json")
        stored.unlink()
        (self.root / "releases" / result["version"] / "index.html").write_bytes(b"corrupt")
        with self.assertRaises(local.ReleaseError):
            auth.install_signed(archive, signature, self.root)
        self.assertFalse(stored.exists())
        self.assertEqual(auth._maximum(self.root), 1)

    def test_competing_signed_intake_is_refused_without_removing_existing_lease(self):
        self.install(1)
        archive, signature, _, _ = self.release(2)
        with local.writer(self.root / "signed-intake"):
            lease = self.root / "signed-intake/writer.lock"
            before = lease.read_bytes()
            with self.assertRaises(local.ReleaseError):
                auth.install_signed(archive, signature, self.root)
            self.assertEqual(lease.read_bytes(), before)
            self.assertEqual(auth._maximum(self.root), 1)
            self.assertEqual(len(list((self.root / "releases").iterdir())), 1)

    def test_resume_rejects_changed_incoming_zip_payload_and_installed_payload(self):
        archive, signature, _, _ = self.release()
        result = auth.install_signed(archive, signature, self.root, publisher_file=self.public_path,
                                     fingerprint=self.public["fingerprint"])
        original = archive.read_bytes()
        with zipfile.ZipFile(archive) as package:
            entries = [(i, package.read(i)) for i in package.infolist()]
        with zipfile.ZipFile(archive, "w") as package:
            for info, body in entries:
                package.writestr(info, b"tampered" if info.filename == "index.html" else body)
        with self.assertRaises(local.ReleaseError):
            auth.install_signed(archive, signature, self.root)
        archive.write_bytes(original)
        (self.root / "releases" / result["version"] / "index.html").write_bytes(b"tampered")
        with self.assertRaises(local.ReleaseError):
            auth.install_signed(archive, signature, self.root)

    def test_resume_requires_stored_signature_and_pin(self):
        archive, signature, _, _ = self.release()
        result = auth.install_signed(archive, signature, self.root, publisher_file=self.public_path,
                                     fingerprint=self.public["fingerprint"])
        stored = self.root / "signatures" / (result["version"] + ".json")
        stored.write_bytes(b"{}")
        with self.assertRaises(local.ReleaseError):
            auth.install_signed(archive, signature, self.root)
        stored.write_bytes(signature.read_bytes())
        other = auth.public_document(Ed25519PrivateKey.generate().public_key())
        (self.root / "publisher-trust.json").write_bytes(local.canonical_json(other))
        with self.assertRaises(local.ReleaseError):
            auth.install_signed(archive, signature, self.root, publisher_file=self.public_path,
                                fingerprint=self.public["fingerprint"])

    def test_equal_counter_other_bytes_and_old_installed_release_cannot_resume_automatically(self):
        archive, signature, _, _ = self.release()
        auth.install_signed(archive, signature, self.root, publisher_file=self.public_path,
                            fingerprint=self.public["fingerprint"])
        other, other_signature, _, _ = self.release(content=b"different but signed")
        with self.assertRaises(local.ReleaseError):
            auth.install_signed(other, other_signature, self.root)
        self.install(2)
        with self.assertRaises(local.ReleaseError):
            auth.install_signed(archive, signature, self.root)
        self.assertTrue(auth.install_signed(archive, signature, self.root, for_rollback=True)["resumed"])
        self.assertEqual(auth._maximum(self.root), 2)

    def test_same_active_version_is_verified_noop_including_explicit_rollback_selection(self):
        a = self.install(1)
        auth.activate_signed(self.root, a["version"])
        with mock.patch.object(local, "atomic_json", wraps=local.atomic_json) as write:
            self.assertTrue(auth.activate_signed(self.root, a["version"])["unchanged"])
            write.assert_not_called()
        b = self.install(2)
        auth.activate_signed(self.root, b["version"])
        auth.activate_signed(self.root, a["version"], rollback=True)
        self.assertTrue(auth.activate_signed(self.root, a["version"])["unchanged"])
        self.assertEqual(auth._maximum(self.root), 2)
        (self.root / "releases" / a["version"] / "index.html").write_bytes(b"corrupted")
        with self.assertRaises(local.ReleaseError):
            auth.activate_signed(self.root, a["version"])

    def test_first_activation_of_old_intake_requires_explicit_rollback(self):
        self.install(2)
        archive, signature, _, _ = self.release(1)
        older = auth.install_signed(archive, signature, self.root, for_rollback=True)
        with self.assertRaises(local.ReleaseError):
            auth.activate_signed(self.root, older["version"])
        auth.activate_signed(self.root, older["version"], rollback=True)
        self.assertEqual(auth._maximum(self.root), 2)

    def test_explicit_rollback_recovers_from_corrupted_active_payload(self):
        a = self.install(1)
        auth.activate_signed(self.root, a["version"])
        b = self.install(2)
        auth.activate_signed(self.root, b["version"])
        (self.root / "releases" / b["version"] / "index.html").write_bytes(b"corrupted update")
        auth.activate_signed(self.root, a["version"], rollback=True)
        self.assertEqual(auth.active_signed_snapshot(self.root)[3]["version"], a["version"])
        self.assertEqual(auth._maximum(self.root), 2)

    def test_build_keeps_exact_collected_git_bytes_and_rejects_inventory_mismatch(self):
        names = ("auth_release.py", "individual_cli.py", "local_installation.py", "stable_launcher.py",
                 "backend_runtime.py", "backend_bundle.py")
        backend = {"backend/launcher/" + name: b"# exact Git LF blob\n" for name in names}
        inventory = {"source_sha": "a" * 40,
                     "files": [{"path": n, "bytes": len(body), "sha256": local.digest(body)}
                               for n, body in backend.items()]}
        backend["backend/BACKEND_MANIFEST.json"] = local.canonical_json(inventory)
        source = self.base / "checkout"
        (source / "tools/local-installation").mkdir(parents=True)
        for name in names:
            (source / "tools/local-installation" / name).write_bytes(b"# checkout CRLF bytes\r\n")

        def package_web(dist, root, output):
            with zipfile.ZipFile(output, "w") as package:
                package.writestr("index.html", b'<meta name="emergency-individual-installation" content="enabled">')
            return {"source_sha": "a" * 40}

        # collect_backend owns Git extraction; this fixture tests that the outer
        # builder preserves those canonical blobs rather than replacing them.
        with mock.patch.object(local, "package", side_effect=package_web), \
                mock.patch("backend_bundle.collect_backend", return_value=backend), \
                mock.patch.object(auth, "load_private", return_value=self.key):
            output = self.base / "signed.zip"
            result = auth.build_signed(self.base, source, self.base, output, 1, self.base / "unused-key")
            with zipfile.ZipFile(output) as package:
                for name in names:
                    self.assertEqual(package.read("backend/launcher/" + name), b"# exact Git LF blob\n")
                auth.authenticate(package.read("manifest.json"), Path(result["signature"]).read_bytes(),
                                  self.public_path.read_bytes(), self.public["fingerprint"])
            backend["backend/launcher/auth_release.py"] = b"inconsistent payload"
            with self.assertRaises(local.ReleaseError):
                auth.build_signed(self.base, source, self.base, self.base / "invalid.zip", 2, self.base / "unused-key")

    def test_every_launch_rejects_corrupted_payload_or_signature(self):
        a = self.install()
        auth.activate_signed(self.root, a["version"])
        path = self.root / "releases" / a["version"] / "index.html"
        path.write_bytes(b"tampered")
        with self.assertRaises(local.ReleaseError):
            auth.active_signed_snapshot(self.root)

    def test_unsigned_individual_version_cannot_use_legacy_static_launcher(self):
        a = self.install()
        auth.activate_signed(self.root, a["version"])
        with self.assertRaises(local.ReleaseError):
            local.make_server(self.root)
        (self.root / "signatures" / (a["version"]+".json")).unlink()
        with self.assertRaises(local.ReleaseError):
            auth.active_signed_snapshot(self.root)

    @unittest.skipUnless(os.name == "nt", "Windows DPAPI CurrentUser only")
    def test_native_windows_dpapi_roundtrip_not_plaintext_publisher_key(self):
        output = auth.create_publisher(self.base / "fixture-keys")
        loaded = auth.load_private(output["private_key_path"])
        self.assertEqual(auth.public_document(loaded.public_key())["fingerprint"], output["fingerprint"])
        protected = Path(output["private_key_path"]).read_bytes()
        self.assertGreater(len(protected), 32)
        self.assertFalse(protected.startswith(b"-----BEGIN"))
        with self.assertRaises(local.ReleaseError):
            auth.create_publisher(self.base / "fixture-keys")


if __name__ == "__main__":
    unittest.main()
