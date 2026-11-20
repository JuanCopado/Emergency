#!/usr/bin/env python3
"""Run the M10 synthetic technical battery and write a reproducible JSON report.

Usage (from clinical/):  python scripts/run_m10_image_audit.py [output.json]
Technical QA only: synthetic data, no diagnostic validation (see M10 protocol).
"""
import hashlib
import json
import subprocess
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

FILES = ["clinical/scripts/image_upload_guard.py", "clinical/scripts/clinical_note_api.py",
         "clinical/scripts/clinical_note_vision_adapter.py", "clinical/tests/synthetic_images.py",
         "clinical/tests/test_m10_skin_wound_image_audit.py", "app/src/pages/ClinicalNote.tsx"]


def git(*args):
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True).stdout.strip()


class Collect(unittest.TextTestResult):
    rows = []

    def _add(self, test, status, detail=None):
        self.rows.append({"id": test.id().split("test_m10_skin_wound_image_audit.")[-1],
                          "status": status, "detail": (detail or "")[-400:] or None})

    def addSuccess(self, test):
        super().addSuccess(test)
        self._add(test, "PASS")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._add(test, "FAIL", self._exc_info_to_string(err, test))

    def addError(self, test, err):
        super().addError(test, err)
        self._add(test, "ERROR", self._exc_info_to_string(err, test))


def main(out):
    suite = unittest.defaultTestLoader.loadTestsFromName("test_m10_skin_wound_image_audit")
    runner = unittest.TextTestRunner(resultclass=Collect, verbosity=0, stream=open("nul" if sys.platform == "win32" else "/dev/null", "w"))
    result = runner.run(suite)
    groups = {}
    for r in Collect.rows:
        g = r["id"].split(".")[0]
        groups.setdefault(g, {"pass": 0, "fail": 0})["pass" if r["status"] == "PASS" else "fail"] += 1
    report = {
        "task": "M10-IMAGE-VALIDATION-20261120", "module": "skin-wound-image",
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "base_sha": git("rev-parse", "HEAD"), "base_tree": git("rev-parse", "HEAD^{tree}"),
        "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
        "python": sys.version.split()[0],
        "command": "cd clinical && python scripts/run_m10_image_audit.py",
        "data": "synthetic only; PNG decodable, JPEG/WebP structural containers",
        "totals": {"run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors)},
        "groups": groups, "tests": Collect.rows,
        "files_sha256": {f: hashlib.sha256((REPO / f).read_bytes()).hexdigest() for f in FILES},
        "not_measured": ["sensitivity", "specificity", "diagnostic accuracy", "skin-tone performance",
                         "real provider behaviour", "pixel-level blankness for JPEG/WebP",
                         "visual prompt-injection resistance of any real vision model"],
        "validation_status": "TECHNICAL_QA_ONLY; M10 remains YELLOW; project CLINICALLY_PENDING",
    }
    Path(out).write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else ROOT / "qa" / "M10_RESULTADOS_PRUEBAS.json"))
