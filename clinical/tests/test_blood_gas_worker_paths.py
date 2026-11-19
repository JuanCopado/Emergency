"""Real worker argv boundaries and private parent staging; synthetic data only."""
from contextlib import nullcontext
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "clinical/scripts"))
import blood_gas_worker as worker


class WorkerPathCapabilities(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.allowed = self.base / "allowed"
        self.outside = self.base / "outside"
        self.allowed.mkdir()
        self.outside.mkdir()
        self.source = self.allowed / "source.bin"
        self.options = self.allowed / "regions.json"
        self.source.write_bytes(b"SYNTHETIC")
        self.options.write_text("null", encoding="utf8")

    def invoke(self, source, options):
        environment = dict(os.environ, EMERGENCY_CLI_INPUT_ROOT=str(self.allowed),
                           EMERGENCY_CLI_ROOT=str(self.outside),
                           PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1")
        return subprocess.run(
            [sys.executable, str(Path(worker.__file__)), "--worker", str(source), str(options)],
            cwd=ROOT, env=environment, capture_output=True, text=True, timeout=30)

    def test_each_argv_rejects_external_and_parent_escape(self):
        sentinel = self.outside / "sentinel.json"
        sentinel.write_text("SYNTHETIC_UNCHANGED", encoding="utf8")
        for argument in (0, 1):
            for path in (sentinel, Path("../outside/sentinel.json")):
                with self.subTest(argument=argument, path=str(path)):
                    paths = [self.source, self.options]
                    paths[argument] = path
                    result = self.invoke(*paths)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("CLI path escapes the launcher workspace", result.stderr)
                    self.assertEqual(result.stdout, "")
                    self.assertEqual(sentinel.read_text(), "SYNTHETIC_UNCHANGED")

    def test_valid_absolute_and_relative_argv_preserve_platform_gate(self):
        if os.name == "nt":
            from reportlab.pdfgen.canvas import Canvas
            output = io.BytesIO()
            document = Canvas(output, pagesize=(580, 220), invariant=1)
            document.drawString(20, 190, "pH 7.42")
            document.save()
            self.source.write_bytes(output.getvalue())
        for paths in ((self.source, self.options), ("source.bin", "regions.json")):
            with self.subTest(paths=tuple(map(str, paths))):
                result = self.invoke(*paths)
                if os.name == "nt":
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(json.loads(result.stdout)[0]["fields"][0]["number"], "7.42")
                else:
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("Resource containment requires Windows Job Objects", result.stderr)
                    self.assertEqual(result.stdout, "")

    def test_parent_grants_its_generated_directory_and_keeps_cwd(self):
        def launch(command, **kwargs):
            source, options = map(Path, command[-2:])
            self.assertEqual(source.name, "source.bin")
            self.assertEqual(options.name, "regions.json")
            self.assertEqual(source.parent, options.parent)
            self.assertEqual(Path(kwargs["env"]["EMERGENCY_CLI_INPUT_ROOT"]), source.parent)
            self.assertNotEqual(source.parent, self.outside)
            self.assertEqual(kwargs["env"]["BG_OCR_MODEL"], "synthetic-preserved-model")
            self.assertNotIn("cwd", kwargs)
            self.assertEqual(kwargs["stderr"], subprocess.DEVNULL)
            self.assertEqual(source.read_bytes(), b"SYNTHETIC")
            self.assertEqual(json.loads(options.read_text()), None)
            kwargs["stdout"].write(b"[]")
            return Mock(wait=Mock(return_value=0))

        with patch.dict(os.environ, {"EMERGENCY_CLI_INPUT_ROOT": str(self.outside),
                                    "BG_OCR_MODEL": "synthetic-preserved-model"}):
            with patch.object(worker.subprocess, "Popen", side_effect=launch):
                self.assertEqual(worker.safe_extract(b"SYNTHETIC"), [])
            self.assertEqual(os.environ["EMERGENCY_CLI_INPUT_ROOT"], str(self.outside))

    def test_private_staging_does_not_overwrite_existing_files(self):
        for filename in ("source.bin", "regions.json"):
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as directory:
                sentinel = Path(directory, filename)
                sentinel.write_bytes(b"SYNTHETIC_UNCHANGED")
                with patch.object(worker.tempfile, "TemporaryDirectory", return_value=nullcontext(directory)):
                    with patch.object(worker.subprocess, "Popen") as launch:
                        with self.assertRaises(FileExistsError):
                            worker.safe_extract(b"SYNTHETIC")
                        launch.assert_not_called()
                self.assertEqual(sentinel.read_bytes(), b"SYNTHETIC_UNCHANGED")


if __name__ == "__main__":
    unittest.main()
