"""Reconcile existing R88 records without reading pixels or admitting stimuli.

This is a coordination verifier, not a clinical/diagnostic validator. Originals,
the canonical bank and historical records are read-only.
"""
from __future__ import annotations

import collections
import argparse
import hashlib
import json
from pathlib import Path


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest(path: Path):
    raw = path.read_bytes()
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def main():
    output = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path,
                        default=output.parents[1] / "WORK_CIERRE_FINAL_20261127" / "IMAGEN_R88")
    source = parser.parse_args().source_root.resolve()
    admission_path = source / "COORDINACION" / "ADMISION_OPERATIVA_30.json"
    admission = read_json(admission_path)
    reference = read_json(source / "COORDINACION" / "REFERENCIAS_16_NA14_Y_CUSTODIA.json")
    nominations = read_json(source / "COORDINACION" / "DESIGNACION_Y_TRANSFERENCIA_PREPARADA.json")
    manifest = read_json(source / "MANIFEST_SHA256.json")
    findings = []
    documentary_integrity = []
    for entry in manifest["files"]:
        path = source / entry["name"]
        actual = digest(path) if path.is_file() else None
        ok = actual == {"bytes": entry["bytes"], "sha256": entry["sha256"]}
        documentary_integrity.append({"file": entry["name"].replace("\\", "/"), "matches": ok,
                                      "expected_sha256": entry["sha256"], "actual": actual})
        if not ok:
            findings.append("Documentary integrity mismatch: " + entry["name"])
    rows = admission["rows"]
    ids = [r["stimulus_id"] for r in rows]
    expected = {f"S{s}-{n:02d}" for n in range(1, 16) for s in (1, 2)}
    if len(ids) != 30 or set(ids) != expected:
        findings.append("Stimulus IDs are not the exact 30 unique historical IDs")
    counts = dict(collections.Counter(r["status"] for r in rows))
    if counts != admission["counts"]:
        findings.append("Status counts differ from historical preparation")
    if {r["stimulus_id"] for r in reference["rows"]} != expected:
        findings.append("Reference/custody IDs differ from admission IDs")
    canonical = [r for r in rows if r["canonical_file"]]
    pending = [r for r in rows if not r["canonical_file"]]
    if len(canonical) != 10 or len(pending) != 20:
        findings.append("Historical canonical count 10/30 not preserved")
    if any(r["formal_admission"] or r["reviewer_1"] or r["reviewer_2"] or
           r["owner_adjudication"] for r in rows):
        findings.append("Unexpected human/admission claim in preparation record")
    if nominations["human_assignments"] != 0 or nominations["people"]:
        findings.append("Unexpected human nomination in prepared form")
    inventory = []
    for r in rows:
        available = r.get("available_file")
        inventory.append({
            "stimulus_id": r["stimulus_id"], "canonical_file_present_in_record": bool(r["canonical_file"]),
            "status": r["status"], "available_file_sha256": available["sha256"] if available else None,
            "available_bytes": available["bytes"] if available else None,
            "formal_admission": False, "independent_reference_and_review": "PENDING",
            "existing_dossier_pointer": r["original_requirement"]["existing_dossier_pointer"],
            "action": r["next_action"],
        })
    report = {
        "task_id": "E-R88-RECONCILIATION-20261127", "executor": "Codex fallback coordination",
        "not_antigravity_audit": True, "source_observed_UTC": admission["observed_UTC"],
        "canonical_commit": admission["canonical_commit"],
        "receiver_declared_by_coordinator": "2058e97179ae793914dcd016e4fd033395dbc3e2",
        "source_admission": {"relative_path": "WORK_CIERRE_FINAL_20261127/IMAGEN_R88/COORDINACION/ADMISION_OPERATIVA_30.json", **digest(admission_path)},
        "new_verification": "Documentary bytes and structural reconciliation only; no image bytes decoded or rehashed",
        "documentary_integrity": documentary_integrity,
        "status": "PASS_DOCUMENTARY_RECONCILIATION_ONLY" if not findings else "CHANGES_REQUIRED",
        "findings": findings, "counts": counts, "canonical_present": len(canonical),
        "canonical_absent": len(pending), "new_canonical_promotions": 0,
        "diagnostic_reference_required": reference["diagnostic_required"],
        "diagnostic_reference_NA": reference["diagnostic_NA"],
        "physical_asset_integrity_reused": {"source": "WORK_CIERRE_FINAL_20261127/IMAGEN_R88/VERIFICACION_RECEPCION.json",
            "canonical": 10, "mobile_candidates": 5, "dermatology": 24,
            "scope": "Earlier Work receipt; not new pixel/privacy/diagnostic review"},
        "external_review_reused": {"reviewer": "Gemini web", "not_antigravity": True,
            "verdict": "FAVORABLE_ALCANCE_DOCUMENTAL", "source": "WORK_CIERRE_FINAL_20261127/GEMINI/DICTAMEN_IMAGEN_V2_RECIBIDO.md",
            "scope": "Documentary preparation and A1-A8 only; no human independence or admission"},
        "inventory": inventory, "pending_stimulus_ids": [r["stimulus_id"] for r in pending],
        "clinical": "CLINICALLY_PENDING", "bank": "NOT_FROZEN_NOT_VALIDATED",
        "release": "NO_GO_CLINICAL_RELEASE", "participants_started": False,
        "clinical_adjudications_created": 0, "new_external_transmissions": 0,
    }
    target = output / "EXPERIMENTAL_PREPARATION_RECONCILIATION.json"
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "documents_checked": len(documentary_integrity),
                      "canonical": len(canonical), "pending": len(pending), "findings": findings,
                      "report": str(target), **digest(target)}, ensure_ascii=True))
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
