#!/usr/bin/env python3
"""Strict validation gate for blinded clinical-image evaluation datasets."""

import argparse
import json
from datetime import datetime
from pathlib import Path

ALLOWED_CLASSES = {"workflow_only", "teaching_source_known", "blinded_accuracy", "prospective_validation"}
ALLOWED_MODALITIES = {
    "musculoskeletal_xray", "chest_xray", "pocus", "ecg", "blood_gas",
    "skin_wound", "ct_mri", "ophthalmology", "other"
}
ALLOWED_PREDICTIONS = {"positive", "negative", "abstain", "nondiagnostic"}

def _parse_iso(value, field, errors, cid):
    if not value:
        errors.append(f"{cid}: {field} required")
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        errors.append(f"{cid}: {field} must be ISO-8601")
        return None

def validate(data):
    errors = []
    warnings = []
    klass = data.get("dataset_class")
    if klass not in ALLOWED_CLASSES:
        errors.append("invalid dataset_class")
        return {"errors": errors, "warnings": warnings, "metrics_eligible": False}

    cases = data.get("cases", [])
    if not isinstance(cases, list):
        errors.append("cases must be a list")
        cases = []

    metrics_requested = bool(data.get("metrics_requested"))
    strict = klass in {"blinded_accuracy", "prospective_validation"}

    if strict:
        for field in ("authorized", "deidentified", "protocol_prespecified", "independent_reference"):
            if data.get(field) is not True:
                errors.append(f"{field} must be true for {klass}")
        if not data.get("target_question"):
            errors.append("target_question required for blinded/prospective dataset")
        if not data.get("target_condition"):
            errors.append("target_condition required for blinded/prospective dataset")
        if data.get("modality") not in ALLOWED_MODALITIES:
            errors.append("valid modality required for blinded/prospective dataset")
        ref_std = data.get("reference_standard")
        if not isinstance(ref_std, dict) or not ref_std.get("type"):
            errors.append("reference_standard.type required for blinded/prospective dataset")

    seen_ids = set()
    seen_studies = set()
    positives = 0
    negatives = 0
    binary_predictions = 0
    unresolved_predictions = 0
    patient_counts = {}

    for case in cases:
        cid = case.get("id")
        if not cid:
            errors.append("case missing id")
            continue
        if cid in seen_ids:
            errors.append(f"duplicate case id: {cid}")
        seen_ids.add(cid)

        ev = case.get("evaluation", {})
        ref = case.get("reference")
        pred = case.get("prediction")

        if strict:
            if ev.get("mode") != "blinded":
                errors.append(f"{cid}: evaluation.mode must be blinded")
            if ev.get("annotated") is not False:
                errors.append(f"{cid}: annotated must be false")
            if ev.get("reference_revealed_after_prediction") is not True:
                errors.append(f"{cid}: reference must be revealed only after prediction freeze")
            if ev.get("prediction_frozen") is not True:
                errors.append(f"{cid}: prediction_frozen must be true")

            study_hash = case.get("study_uid_hash")
            patient_hash = case.get("patient_uid_hash")
            if not study_hash:
                errors.append(f"{cid}: study_uid_hash required for leakage control")
            elif study_hash in seen_studies:
                errors.append(f"{cid}: duplicate study_uid_hash")
            else:
                seen_studies.add(study_hash)
            if not patient_hash:
                errors.append(f"{cid}: patient_uid_hash required for leakage control")
            else:
                patient_counts[patient_hash] = patient_counts.get(patient_hash, 0) + 1

            if not ref:
                errors.append(f"{cid}: independent reference required")
            if not pred:
                errors.append(f"{cid}: recorded prediction required")

            frozen_at = _parse_iso(ev.get("prediction_frozen_at"), "prediction_frozen_at", errors, cid)
            revealed_at = _parse_iso(ev.get("reference_revealed_at"), "reference_revealed_at", errors, cid)
            if frozen_at and revealed_at and frozen_at >= revealed_at:
                errors.append(f"{cid}: prediction must be frozen before reference reveal")

        if ref and "target_positive" in ref:
            if bool(ref["target_positive"]):
                positives += 1
            else:
                negatives += 1

        if pred:
            klass_pred = pred.get("class")
            if klass_pred is None and "target_positive" in pred:
                klass_pred = "positive" if bool(pred["target_positive"]) else "negative"
            if strict and klass_pred not in ALLOWED_PREDICTIONS:
                errors.append(f"{cid}: prediction.class must be one of {sorted(ALLOWED_PREDICTIONS)}")
            if klass_pred in {"positive", "negative"}:
                binary_predictions += 1
            elif klass_pred in {"abstain", "nondiagnostic"}:
                unresolved_predictions += 1

    repeated_patients = sorted(k for k, v in patient_counts.items() if v > 1)
    if repeated_patients and strict and data.get("patient_grouping_prespecified") is not True:
        errors.append("repeated patient_uid_hash requires patient_grouping_prespecified=true")

    metrics_eligible = strict and not errors
    if metrics_requested and not strict:
        errors.append("metrics requested for non-blinded dataset")
        metrics_eligible = False
    if metrics_requested and strict:
        if positives == 0 or negatives == 0:
            errors.append("sensitivity/specificity require both positive and negative reference cases")
            metrics_eligible = False

    if klass == "teaching_source_known" and metrics_requested:
        errors.append("source-known teaching cases cannot be used for performance metrics")

    return {
        "errors": errors,
        "warnings": warnings,
        "metrics_eligible": metrics_eligible,
        "case_count": len(cases),
        "positive_reference_cases": positives,
        "negative_reference_cases": negatives,
        "binary_predictions": binary_predictions,
        "unresolved_predictions": unresolved_predictions,
        "repeated_patient_groups": len(repeated_patients),
    }

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("dataset", type=Path)
    args = p.parse_args()
    result = validate(json.loads(args.dataset.read_text(encoding="utf-8")))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(bool(result["errors"]))
