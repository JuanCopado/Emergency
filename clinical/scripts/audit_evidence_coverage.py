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
    "pediatric-emergencies", "obstetric-emergencies", "anticoagulation-reversal",
    "toxicology", "empiric-antibiotics", "sedoanalgesia",
    "medication-selection-safety", "clinical-image-interpretation",
    "tension-pneumothorax", "traumatic-intracranial-mass-effect",
    "trauma-major-hemorrhage", "status-epilepticus", "anaphylaxis",
    "diabetic-ketoacidosis-hhs", "sodium-emergencies", "potassium-emergencies",
    "calcium-magnesium-emergencies", "acute-respiratory-failure",
    "oxygen-therapy-emergency", "high-flow-nasal-oxygen", "noninvasive-ventilation",
    "vasoactive-inotrope-infusions", "icu-sedation-analgesia-infusions",
}


def _review_days(priority: str, policy: dict) -> int:
    if priority == "high":
        return int(policy.get("high_risk_days", 30))
    if priority == "standard":
        return int(policy.get("standard_days", 90))
    return int(policy.get("low_change_days", 180))


def audit(root: Path, today: date | None = None):
    today = today or date.today()
    manifest, module_errors = validate_modules(root)
    registry_doc = json.loads(
        (root / "references/evidence-registry.json").read_text(encoding="utf-8")
    )
    registry = registry_doc.get("modules", {})
    policy = registry_doc.get("review_policy", {})
    errors = list(module_errors)
    warnings = []

    unknown = sorted(set(registry) - set(manifest))
    if unknown:
        errors.append(f"registry has unknown modules: {unknown}")
    missing_high_risk = sorted(HIGH_RISK - set(registry))
    if missing_high_risk:
        errors.append(f"high-risk modules missing evidence records: {missing_high_risk}")

    for module_id, record in registry.items():
        status = record.get("status")
        if status not in {"green", "yellow", "red"}:
            errors.append(f"{module_id}: invalid evidence status")
        if not record.get("primary_source") or not record.get("stored_version"):
            errors.append(f"{module_id}: incomplete evidence identity")

        try:
            checked = date.fromisoformat(record.get("last_checked", ""))
        except ValueError:
            errors.append(f"{module_id}: invalid last_checked date")
            continue

        if checked > today:
            errors.append(f"{module_id}: last_checked is in the future ({checked.isoformat()})")
            continue

        max_age = _review_days(record.get("priority", ""), policy)
        age_days = (today - checked).days
        if age_days > max_age:
            message = (
                f"{module_id}: evidence review overdue "
                f"({age_days} days; limit {max_age}; status {status})"
            )
            if status == "green":
                errors.append(message + "; green cannot remain current past its review window")
            else:
                warnings.append(message)

    absent = sorted(set(manifest) - set(registry))
    if absent:
        errors.append(
            f"modules missing evidence records: {', '.join(absent)}"
        )
    counts = {
        status: sum(1 for item in registry.values() if item.get("status") == status)
        for status in ("green", "yellow", "red")
    }
    return {
        "audit_date": today.isoformat(),
        "total_modules": len(manifest),
        "registered": len(registry),
        "unregistered": len(absent),
        "status_counts": counts,
        "errors": errors,
        "warnings": warnings,
    }


if __name__ == "__main__":
    skill_root = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parents[1])
    result = audit(skill_root)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(bool(result["errors"]))
