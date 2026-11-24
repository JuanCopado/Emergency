"""Exercise the local intake contract with synthetic file bytes."""
import hashlib
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lab"))
from human_factors import intake_r68 as intake

MANIFEST = {"stimuli": [
    {"stimulus_id": "S1-10", "file": None},
    {"stimulus_id": "S2-09", "file": "stimuli/S2-09.jpg"},
]}


class Intake(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        self.delivery = root / "incoming"
        self.delivery.mkdir()
        data = b"synthetic test content"
        (root / "outside.jpg").write_bytes(data)
        self.file = self.delivery / "original.jpg"
        self.file.write_bytes(data)
        self.asset = {
            "stimulus_id": "S1-10", "role": "original", "kind": "synthetic",
            "source": "example author and version", "license": "example declaration",
            "permission_ref": "example permissions document", "privacy_ref": "synthetic fixture",
            "transformation": "original", "file": self.file.name,
            "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
        }

    def test_reports_verified_bytes_without_promoting_stimulus(self):
        result = intake.check_receipt({"assets": [self.asset]}, self.delivery, MANIFEST)
        self.assertEqual(result["status"], "BYTES_VERIFIED_REVIEW_PENDING")
        self.assertEqual(result["assets"][0]["sha256"], self.asset["sha256"])
        self.assertIsNone(MANIFEST["stimuli"][0]["file"])

    def test_cli_reads_receipt_and_fails_closed_on_changed_file(self):
        bank = self.delivery.parent / "bank"
        bank.mkdir()
        (bank / "stimuli_manifest.json").write_text(json.dumps(MANIFEST), encoding="utf-8")
        receipt = self.delivery / "recepcion.json"
        receipt.write_text(json.dumps({"assets": [self.asset]}), encoding="utf-8")
        output = io.StringIO()
        with patch.object(intake, "BANK", bank), patch.object(sys, "argv", ["intake", str(receipt)]):
            with redirect_stdout(output):
                intake.main()
            self.assertEqual(json.loads(output.getvalue())["status"], "BYTES_VERIFIED_REVIEW_PENDING")
            self.file.write_bytes(b"changed")
            with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as result:
                intake.main()
            self.assertEqual(result.exception.code, 1)

    def test_rejects_unusable_entries(self):
        for change in (
            {"bytes": 0}, {"sha256": "0" * 64}, {"permission_ref": ""},
            {"file": "../outside.jpg"}, {"file": "missing.jpg"},
            {"stimulus_id": "S2-09"}, {"kind": "unknown"}, {"role": "unknown"},
        ):
            with self.subTest(change=change), self.assertRaises(ValueError):
                intake.check_receipt({"assets": [{**self.asset, **change}]}, self.delivery, MANIFEST)
        for assets in ([], [self.asset, self.asset]):
            with self.assertRaises(ValueError):
                intake.check_receipt({"assets": assets}, self.delivery, MANIFEST)
