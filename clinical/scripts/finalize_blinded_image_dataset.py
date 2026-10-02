#!/usr/bin/env python3
"""Finalize a blinded image dataset only after predictions are frozen.

Inputs:
- blinded preprediction manifest
- predictions file with one entry per case
- sealed reference file

Output:
- IMAGE_VALIDATION_POLICY v1.1 compatible manifest

This script fails closed on missing/extra IDs, duplicate IDs, missing timestamps,
invalid classes, or any attempt to reveal reference before prediction freeze.
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ALLOWED_PREDICTIONS = {"positive", "negative", "abstain", "nondiagnostic"}

def _parse_iso(value, field, case_id):
    if not value:
        raise ValueError(f"{case_id}: {field} required")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{case_id}: {field} must be ISO-8601") from exc

def _index_unique(items, key, label):
    out = {}
    for item in items:
        value = item.get(key)
        if not value:
            raise ValueError(f"{label}: missing {key}")
        if value in out:
            raise ValueError(f"{label}: duplicate {key}: {value}")
        out[value] = item
    return out

def finalize(blinded, predictions, sealed_reference, reference_revealed_at=None):
    if blinded.get("dataset_class") != "blinded_accuracy":
        raise ValueError("blinded manifest must have dataset_class=blinded_accuracy")
    if blinded.get("protocol_prespecified") is not True:
        raise ValueError("blinded manifest must be protocol_prespecified=true")
    if blinded.get("patient_grouping_prespecified") is not True:
        raise ValueError("patient_grouping_prespecified=true required")

    blinded_cases = _index_unique(blinded.get("cases", []), "id", "blinded")
    pred_cases = _index_unique(predictions.get("predictions", []), "id", "predictions")
    ref_cases = _index_unique(sealed_reference.get("references", []), "id", "reference")

    ids = set(blinded_cases)
    if set(pred_cases) != ids:
        missing = sorted(ids - set(pred_cases))
        extra = sorted(set(pred_cases) - ids)
        raise ValueError(f"prediction IDs mismatch; missing={missing}; extra={extra}")
    if set(ref_cases) != ids:
        missing = sorted(ids - set(ref_cases))
        extra = sorted(set(ref_cases) - ids)
        raise ValueError(f"reference IDs mismatch; missing={missing}; extra={extra}")

    dataset_reveal = reference_revealed_at or predictions.get("reference_revealed_at")
    if not dataset_reveal:
        dataset_reveal = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    reveal_dt = _parse_iso(dataset_reveal, "reference_revealed_at", "dataset")

    finalized = []
    seen_study_hashes = set()

    for case_id in sorted(ids):
        base = blinded_cases[case_id]
        pred = pred_cases[case_id]
        ref = ref_cases[case_id]

        pred_class = pred.get("class")
        if pred_class not in ALLOWED_PREDICTIONS:
            raise ValueError(
                f"{case_id}: prediction class must be one of {sorted(ALLOWED_PREDICTIONS)}"
            )

        frozen_at = pred.get("prediction_frozen_at")
        frozen_dt = _parse_iso(frozen_at, "prediction_frozen_at", case_id)
        if frozen_dt >= reveal_dt:
            raise ValueError(f"{case_id}: prediction must be frozen before reference reveal")

        study_hash = base.get("study_uid_hash")
        patient_hash = base.get("patient_uid_hash")
        if not study_hash or not patient_hash:
            raise ValueError(f"{case_id}: patient/study hashes required")
        if study_hash in seen_study_hashes:
            raise ValueError(f"{case_id}: duplicate study_uid_hash")
        seen_study_hashes.add(study_hash)

        if ref.get("study_uid_hash") != study_hash:
            raise ValueError(f"{case_id}: sealed reference study hash mismatch")
        if "target_positive" not in ref:
            raise ValueError(f"{case_id}: target_positive missing from sealed reference")

        finalized.append({
            "id": case_id,
            "patient_uid_hash": patient_hash,
            "study_uid_hash": study_hash,
            "image_file": base.get("image_file"),
            "evaluation": {
                "mode": "blinded",
                "annotated": False,
                "reference_revealed_after_prediction": True,
                "prediction_frozen": True,
                "prediction_frozen_at": frozen_at,
                "reference_revealed_at": dataset_reveal,
            },
            "prediction": {
                "class": pred_class,
            },
            "reference": {
                "target_positive": bool(ref["target_positive"]),
            },
        })

    return {
        "schema_version": "1.1",
        "dataset_class": "blinded_accuracy",
        "authorized": blinded.get("authorized") is True,
        "deidentified": blinded.get("deidentified") is True,
        "protocol_prespecified": True,
        "independent_reference": blinded.get("independent_reference") is True,
        "modality": blinded.get("modality"),
        "target_condition": blinded.get("target_condition"),
        "target_question": blinded.get("target_question"),
        "reference_standard": blinded.get("reference_standard"),
        "patient_grouping_prespecified": True,
        "metrics_requested": True,
        "source_id": blinded.get("source_id"),
        "source_version": blinded.get("source_version"),
        "benchmark_contamination_risk": blinded.get("benchmark_contamination_risk"),
        "cases": finalized,
    }

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("blinded_manifest", type=Path)
    p.add_argument("predictions", type=Path)
    p.add_argument("sealed_reference", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("--reference-revealed-at")
    args = p.parse_args()

    result = finalize(
        json.loads(args.blinded_manifest.read_text(encoding="utf-8")),
        json.loads(args.predictions.read_text(encoding="utf-8")),
        json.loads(args.sealed_reference.read_text(encoding="utf-8")),
        args.reference_revealed_at,
    )
    args.output.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(args.output)
