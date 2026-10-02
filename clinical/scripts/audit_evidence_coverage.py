#!/usr/bin/env python3
"""Audit evidence-registry coverage without equating coverage with validation."""

import json
import sys
from datetime import date
from pathlib import Path

from validate_modules import validate as validate_modules


HIGH_RISK = {
    "acute-ischemic-stroke", "acute-coronary-syndrome", "pulmonary-embolism",
    "sepsis-shock", "arrhythmias-cardiac-arrest", "airway-rsi",
    "pediatric-emergencies", "pediatric-emergency-medications", "pediatric-iv-fluid-therapy", "pediatric-acute-asthma", "pediatric-airway-rsi", "pediatric-electrolyte-emergencies", "pediatric-blood-transfusion-major-hemorrhage", "pediatric-procedural-sedation", "pediatric-acute-respiratory-support", "pediatric-cns-infection", "pediatric-toxicology", "pediatric-dka", "pediatric-burns", "pediatric-sepsis", "pediatric-adrenal-crisis", "pediatric-major-trauma", "pediatric-head-injury", "pediatric-abdominal-surgical-emergencies", "obstetric-emergencies", "anticoagulation-reversal",
    "toxicology", "empiric-antibiotics", "sedoanalgesia",
    "medication-selection-safety", "clinical-image-interpretation",
    "tension-pneumothorax", "traumatic-intracranial-mass-effect",
    "trauma-major-hemorrhage", "status-epilepticus", "anaphylaxis",
    "diabetic-ketoacidosis-hhs", "sodium-emergencies", "potassium-emergencies",
    "calcium-magnesium-emergencies", "acute-respiratory-failure",
    "oxygen-therapy-emergency", "high-flow-nasal-oxygen", "noninvasive-ventilation",
    "vasoactive-inotrope-infusions", "icu-sedation-analgesia-infusions",
    "adult-arrhythmias", "adult-cardiac-arrest", "undifferentiated-shock",
    "pediatric-arrhythmias", "pediatric-cardiac-arrest", "pediatric-shock",
    "pediatric-status-epilepticus",
}


def audit(root: Path):
    manifest, module_errors = validate_modules(root)
    registry = json.loads(
        (root / "references/evidence-registry.json").read_text(encoding="utf-8")
    ).get("modules", {})
    errors = list(module_errors)
    warnings = []

    unknown = sorted(set(registry) - set(manifest))
    if unknown:
        errors.append(f"registry has unknown modules: {unknown}")
    missing_high_risk = sorted(HIGH_RISK - set(registry))
    if missing_high_risk:
        errors.append(f"high-risk modules missing evidence records: {missing_high_risk}")

    for module_id, record in registry.items():
        if record.get("status") not in {"green", "yellow", "red"}:
            errors.append(f"{module_id}: invalid evidence status")
        if not record.get("primary_source") or not record.get("stored_version"):
            errors.append(f"{module_id}: incomplete evidence identity")
        try:
            date.fromisoformat(record.get("last_checked", ""))
        except ValueError:
            errors.append(f"{module_id}: invalid last_checked date")

    absent = sorted(set(manifest) - set(registry))
    if absent:
        errors.append(
            f"modules missing evidence records: {', '.join(absent)}"
        )
    counts = {status: sum(1 for item in registry.values() if item.get("status") == status)
              for status in ("green", "yellow", "red")}
    return {"total_modules": len(manifest), "registered": len(registry),
            "unregistered": len(absent), "status_counts": counts,
            "errors": errors, "warnings": warnings}


if __name__ == "__main__":
    skill_root = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parents[1])
    result = audit(skill_root)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(bool(result["errors"]))
