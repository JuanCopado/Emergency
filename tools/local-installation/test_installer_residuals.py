"""New process-level installer regressions; synthetic files, no signing keys."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

import local_installation as local


class InstallerResidualTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="emergency-residual-")
        self.base = Path(self.temporary.name)
        self.root = self.base / "installation"
        self.module_dir = Path(local.__file__).resolve().parent

    def tearDown(self):
        self.doCleanups()  # Release child handles before TemporaryDirectory cleanup.
        self.temporary.cleanup()

    def attempt(self):
        return subprocess.run([sys.executable, "-c", """
import sys
import local_installation as local
try:
    with local.writer(sys.argv[1]):
        print('ACQUIRED')
except local.ReleaseError:
    print('REJECTED')
    sys.exit(3)
""", str(self.root)], cwd=self.module_dir, capture_output=True, text=True, timeout=5)

    def holder(self):
        ready = self.base / "holder-ready"
        process = subprocess.Popen([sys.executable, "-c", """
import sys,time
from pathlib import Path
import local_installation as local
with local.writer(sys.argv[1]):
    Path(sys.argv[2]).write_text('synthetic-ready')
    time.sleep(30)
""", str(self.root), str(ready)], cwd=self.module_dir,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.addCleanup(self.stop, process)
        deadline = time.monotonic() + 5
        while not ready.exists() and process.poll() is None and time.monotonic() < deadline:
            time.sleep(.02)
        self.assertTrue(ready.exists(), "child did not acquire its lease")
        return process

    @staticmethod
    def stop(process):
        if process.poll() is None:
            process.kill()
        process.communicate(timeout=5)

    def test_process_crash_releases_os_lease_without_deleting_marker(self):
        process = self.holder()
        marker = (self.root / "writer.lock").read_bytes()
        process.kill()
        process.communicate(timeout=5)
        self.assertEqual((self.root / "writer.lock").read_bytes(), marker)
        result = self.attempt()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "ACQUIRED")
        self.assertEqual((self.root / "writer.lock").read_bytes(), marker)

    def test_real_competing_process_cannot_enter_or_remove_live_lease(self):
        self.holder()
        marker = (self.root / "writer.lock").read_bytes()
        result = self.attempt()
        self.assertEqual(result.returncode, 3, result.stderr)
        self.assertEqual(result.stdout.strip(), "REJECTED")
        self.assertEqual((self.root / "writer.lock").read_bytes(), marker)

    def test_legacy_and_partial_markers_fail_closed_without_pid_or_age_recovery(self):
        self.root.mkdir()
        for marker in (b"", b"1234", b"emergency.os-writer."):
            with self.subTest(marker=marker):
                (self.root / "writer.lock").write_bytes(marker)
                result = self.attempt()
                self.assertEqual(result.returncode, 3, result.stderr)
                self.assertEqual((self.root / "writer.lock").read_bytes(), marker)

    def test_marker_prevents_old_exclusive_create_writer_after_release(self):
        with local.writer(self.root):
            pass
        result = subprocess.run([sys.executable, "-c", """
import os,sys
try:
    fd=os.open(sys.argv[1],os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
except FileExistsError:
    sys.exit(3)
else:
    os.close(fd)
""", str(self.root / "writer.lock")], capture_output=True, timeout=5)
        self.assertEqual(result.returncode, 3)
        self.assertEqual(self.attempt().returncode, 0)

    def release(self, counter, *, individual=True):
        content = b"<html>INVENTED NONCLINICAL FIXTURE</html>"
        manifest = {"schema": local.INDIVIDUAL_SCHEMA if individual else local.SCHEMA,
            "source_sha": str(counter) * 40,
            "capabilities": local.INDIVIDUAL_CAPABILITIES if individual else
                ["static-reference-partial", "no-clinical-api", "no-remote-case-processing"],
            "files": [{"path": "index.html", "size": len(content), "sha256": local.digest(content)}]}
        if individual:
            manifest["release_counter"] = counter
        raw = local.canonical_json(manifest)
        expected = local.digest(raw)
        version = local.version_id(manifest, expected)
        directory = self.root / "releases" / version
        directory.mkdir(parents=True)
        (directory / "index.html").write_bytes(content)
        (directory / "manifest.json").write_bytes(raw)
        return version, expected

    def legacy_cli(self, command, version, expected):
        return subprocess.run([sys.executable, str(self.module_dir / "local_installation.py"),
            command, version, "--root", str(self.root), "--expected-manifest-sha256", expected],
            capture_output=True, text=True, timeout=5)

    def test_legacy_activate_and_rollback_reject_individual_before_selection_changes(self):
        older, old_hash = self.release(1)
        current, current_hash = self.release(2)
        # Shared library still supports the authenticated route's manifest type.
        # This schema-boundary fixture performs no signing/authentication claim.
        local.select(self.root, current, current_hash)
        sequence = self.root / "release-sequence.json"
        sequence.write_bytes(local.canonical_json({"maximum": 2}))
        active_before = (self.root / "active.json").read_bytes()
        sequence_before = sequence.read_bytes()
        for command in ("activate", "rollback"):
            with self.subTest(command=command):
                result = self.legacy_cli(command, older, old_hash)
                self.assertEqual(result.returncode, 1)
                self.assertIn("authenticated individual", result.stderr)
                self.assertEqual((self.root / "active.json").read_bytes(), active_before)
                self.assertEqual(sequence.read_bytes(), sequence_before)

    def test_legacy_static_activation_remains_available(self):
        version, expected = self.release(1, individual=False)
        result = self.legacy_cli("activate", version, expected)
        self.assertEqual(result.returncode, 0, result.stderr)
        selected = json.loads((self.root / "active.json").read_bytes())
        self.assertEqual(selected, {"version": version, "manifest_sha256": expected})


if __name__ == "__main__":
    unittest.main()
