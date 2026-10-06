#!/usr/bin/env python3
"""Unified QA release gate for the Emergency Medicine skill.

Automated PASS means structural/evidence/regression integrity only.
It never establishes clinical validity or auto-promotes high-risk modules.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
SCRIPTS = ROOT / "scripts"

CHECKS = [
    ("module-integrity", [sys.executable, str(SCRIPTS / "validate_modules.py"), str(ROOT)]),
    ("evidence-coverage", [sys.executable, str(SCRIPTS / "audit_evidence_coverage.py"), str(ROOT)]),
    ("clinical-case-provenance", [sys.executable, str(SCRIPTS / "validate_clinical_cases.py"), str(ROOT)]),
    ("real-image-provenance", [sys.executable, str(SCRIPTS / "validate_real_image_cases.py"), str(ROOT)]),
    ("image-source-registry", [sys.executable, str(SCRIPTS / "validate_image_dataset_source.py"), str(ROOT / "qa/image-dataset-source-registry.json")]),
    ("blinded-image-template", [sys.executable, str(SCRIPTS / "validate_blinded_image_dataset.py"), str(ROOT / "tests/blinded-image-dataset-template.json")]),
    ("unit-regression-tests", [sys.executable, "-m", "unittest", "discover", "-s", str(ROOT / "tests"), "-p", "test_skill.py"]),
    ("procedures-v1.41-tests", [sys.executable, "-m", "unittest", "discover", "-s", str(ROOT / "tests"), "-p", "test_*v141.py"]),
]

def run_check(name, cmd):
    proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    return {
        "name": name,
        "passed": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }

def human_gate_summary():
    registry = json.loads((ROOT / "references/evidence-registry.json").read_text(encoding="utf-8"))
    modules = registry.get("modules", {})
    high_risk_pending = sorted(
        module_id for module_id, item in modules.items()
        if item.get("priority") == "high" and item.get("status") != "green"
    )
    local = json.loads((ROOT / "qa/localization-portugal-azores.json").read_text(encoding="utf-8"))
    local_pending = sorted(item["drug"] for item in local["items"] if item.get("status") != "verified")
    return {
        "high_risk_not_green": high_risk_pending,
        "localization_pending": local_pending,
        "clinical_release_status": "CLINICALLY_PENDING" if high_risk_pending or local_pending else "ELIGIBLE_FOR_HUMAN_RELEASE_REVIEW",
    }

def main():
    results = [run_check(name, cmd) for name, cmd in CHECKS]
    automated_pass = all(item["passed"] for item in results)
    report = {
        "schema_version": "1.0",
        "automated_pass": automated_pass,
        "automated_status": "PASS" if automated_pass else "BLOCKED",
        "checks": results,
        "human_gates": human_gate_summary(),
        "disclaimer": "Automated QA PASS is not clinical validation and does not auto-promote evidence status.",
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if automated_pass else 1

if __name__ == "__main__":
    raise SystemExit(main())
