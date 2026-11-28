"""New process-level installer regressions; synthetic files, no signing keys."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

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

    def test_process_crash_releases_guard_and_reclaims_only_complete_marker(self):
        process = self.holder()
        marker = (self.root / "writer.lock").read_bytes()
        process.kill()
        process.communicate(timeout=5)
        self.assertEqual((self.root / "writer.lock").read_bytes(), marker)
        self.assertTrue((self.root / "writer.guard").is_file())
        result = self.attempt()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "ACQUIRED")
        self.assertFalse((self.root / "writer.lock").exists())

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

    def test_clean_return_allows_legacy_writer_without_changing_root_or_selection(self):
        with local.writer(self.root):
            pass
        guard = (self.root / "writer.guard").read_bytes()
        active = b'{"synthetic":"unchanged"}\n'
        sequence = b'{"maximum":2}\n'
        (self.root / "active.json").write_bytes(active)
        (self.root / "release-sequence.json").write_bytes(sequence)
        result = subprocess.run([sys.executable, "-c", """
import os,sys
try:
    fd=os.open(sys.argv[1],os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
except FileExistsError:
    sys.exit(3)
else:
    os.write(fd,str(os.getpid()).encode())
    os.close(fd)
    os.unlink(sys.argv[1])
""", str(self.root / "writer.lock")], capture_output=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.root / "writer.guard").read_bytes(), guard)
        self.assertEqual((self.root / "active.json").read_bytes(), active)
        self.assertEqual((self.root / "release-sequence.json").read_bytes(), sequence)
        self.assertEqual(self.attempt().returncode, 0)

    def test_legacy_wins_reclaim_gap_new_writer_preserves_its_live_marker(self):
        self.root.mkdir()
        lock = self.root / "writer.lock"
        lock.write_bytes(b"emergency.writer.v2:" + b"a" * 32 + b"\n")
        ready = self.base / "legacy-ready"
        original_open = local.os.open
        processes = []

        def interleave(path, flags, mode=0o777, **kwargs):
            if Path(path) == lock and flags & local.os.O_EXCL:
                process = subprocess.Popen([sys.executable, "-c", """
import os,sys,time
from pathlib import Path
fd=os.open(sys.argv[1],os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
os.write(fd,b'LEGACY_LIVE_PID_FIXTURE');os.close(fd)
Path(sys.argv[2]).write_text('ready')
time.sleep(30)
""", str(lock), str(ready)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                processes.append(process)
                self.addCleanup(self.stop, process)
                deadline = time.monotonic() + 5
                while not ready.exists() and process.poll() is None and time.monotonic() < deadline:
                    time.sleep(.02)
                self.assertTrue(ready.exists(), "legacy process did not win O_EXCL")
            return original_open(path, flags, mode, **kwargs)

        with patch.object(local.os, "open", side_effect=interleave):
            with self.assertRaisesRegex(local.ReleaseError, "legacy writer"):
                with local.writer(self.root):
                    self.fail("new writer entered after legacy won")
        self.assertIsNone(processes[0].poll())
        self.assertEqual(lock.read_bytes(), b"LEGACY_LIVE_PID_FIXTURE")
        self.assertEqual(self.attempt().returncode, 3)
        self.assertEqual(lock.read_bytes(), b"LEGACY_LIVE_PID_FIXTURE")

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
