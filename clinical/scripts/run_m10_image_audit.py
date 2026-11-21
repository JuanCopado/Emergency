#!/usr/bin/env python3
"""Run the M10 synthetic technical battery and emit its reproducible JSON report.

Usage (from clinical/):  python scripts/run_m10_image_audit.py [--write-current]
Default output is stdout. --write-current writes only the designated follow-up file.
Technical QA only: synthetic data, no diagnostic validation (see M10 protocol).
"""
import argparse
import hashlib
import io
import json
import subprocess
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
CURRENT_REPORT = ROOT / "qa" / "M10_RESULTADOS_ACTUALES.json"
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

FILES = ["clinical/scripts/image_upload_guard.py", "clinical/scripts/clinical_note_api.py",
         "clinical/scripts/clinical_note_vision_adapter.py", "clinical/tests/synthetic_images.py",
         "clinical/tests/test_m10_skin_wound_image_audit.py", "app/src/pages/ClinicalNote.tsx"]


def git(*args):
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True).stdout.strip()


class Collect(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rows = []

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

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        if err is not None:
            status = "FAIL" if issubclass(err[0], test.failureException) else "ERROR"
            self._add(subtest, status, self._exc_info_to_string(err, subtest))

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self._add(test, "SKIP", reason)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-current", action="store_true",
                        help="write the current report under clinical/qa, preserving historical evidence")
    options = parser.parse_args(argv)
    suite = unittest.defaultTestLoader.loadTestsFromName("test_m10_skin_wound_image_audit")
    runner = unittest.TextTestRunner(resultclass=Collect, verbosity=0, stream=io.StringIO())
    result = runner.run(suite)
    groups = {}
    for r in result.rows:
        g = r["id"].split(".")[0]
        counts = groups.setdefault(g, {"pass": 0, "fail": 0, "skip": 0})
        bucket = {"PASS": "pass", "SKIP": "skip"}.get(r["status"], "fail")
        counts[bucket] += 1
    report = {
        "task": "M10-IMAGE-VALIDATION-20261120", "module": "skin-wound-image",
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "base_sha": git("rev-parse", "HEAD"), "base_tree": git("rev-parse", "HEAD^{tree}"),
        "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
        "python": sys.version.split()[0],
        "command": "cd clinical && python scripts/run_m10_image_audit.py",
        "data": "Synthetic PNG, JPEG and WebP rasters, plus malformed or excluded fixtures.",
        "totals": {"run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
                   "skipped": len(result.skipped)},
        "groups": groups, "tests": result.rows,
        "files_sha256": {f: hashlib.sha256((REPO / f).read_bytes()).hexdigest() for f in FILES},
        "not_measured": ["sensitivity", "specificity", "diagnostic accuracy", "skin-tone performance",
                         "real provider behaviour", "diagnostic image quality",
                         "visual prompt-injection resistance of any real vision model"],
        "validation_status": "TECHNICAL_QA_ONLY; skin-wound reference accepted; image performance pending; CLINICALLY_PENDING",
    }
    output = json.dumps(report, indent=2, ensure_ascii=False)
    if options.write_current:
        CURRENT_REPORT.write_text(output + "\n", encoding="utf-8")
    else:
        print(output)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
