#!/usr/bin/env python3
"""Prepare a fail-closed RSNA ICH exam-level blinded cohort.

Expected images CSV:
study_id,image_id,dicom_path[,patient_id]

Expected references CSV:
study_id,target_positive,reference_type
"""

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ACCEPTED_REFERENCE_TYPES = {
    "majority_3_neuroradiologists",
    "senior_neuroradiologist_adjudication",
}

def _hash(value, salt):
    return hashlib.sha256(f"{salt}:{value}".encode("utf-8")).hexdigest()

def _bool(value):
    v = str(value).strip().lower()
    if v in {"1", "true", "yes", "positive"}:
        return True
    if v in {"0", "false", "no", "negative"}:
        return False
    raise ValueError(f"invalid target_positive value: {value}")

def prepare(images_csv, references_csv, salt):
    if len(salt) < 16:
        raise ValueError("salt must be at least 16 characters")

    studies = defaultdict(list)
    patients = {}
    with Path(images_csv).open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"study_id", "image_id", "dicom_path"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"images CSV missing columns: {sorted(missing)}")
        for row in reader:
            sid = row["study_id"].strip()
            iid = row["image_id"].strip()
            path = row["dicom_path"].strip()
            if not sid or not iid or not path:
                raise ValueError("study_id/image_id/dicom_path cannot be empty")
            studies[sid].append({"image_id": iid, "dicom_path": path})
            pid = (row.get("patient_id") or sid).strip()
            if sid in patients and patients[sid] != pid:
                raise ValueError(f"{sid}: inconsistent patient_id")
            patients[sid] = pid

    refs = {}
    with Path(references_csv).open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"study_id", "target_positive", "reference_type"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"reference CSV missing columns: {sorted(missing)}")
        for row in reader:
            sid = row["study_id"].strip()
            if sid in refs:
                raise ValueError(f"duplicate reference study_id: {sid}")
            rtype = row["reference_type"].strip()
            if rtype not in ACCEPTED_REFERENCE_TYPES:
                raise ValueError(f"{sid}: unsupported reference_type {rtype}")
            refs[sid] = {
                "target_positive": _bool(row["target_positive"]),
                "reference_type": rtype,
            }

    eligible = sorted(set(studies) & set(refs))
    if not eligible:
        raise ValueError("no studies have accepted reference provenance")

    positives = sum(1 for sid in eligible if refs[sid]["target_positive"])
    negatives = len(eligible) - positives
    if not positives or not negatives:
        raise ValueError("eligible cohort must contain positive and negative exams")

    blinded = []
    sealed = []
    for sid in eligible:
        study_hash = _hash(sid, salt)
        patient_hash = _hash(patients[sid], salt)
        case_id = f"rsnaich-{study_hash[:16]}"
        slices = sorted(studies[sid], key=lambda x: x["image_id"])
        blinded.append({
            "id": case_id,
            "patient_uid_hash": patient_hash,
            "study_uid_hash": study_hash,
            "slices": [
                {
                    "slice_id_hash": _hash(x["image_id"], salt),
                    "source_path_token": _hash(x["dicom_path"], salt),
                }
                for x in slices
            ],
            "evaluation": {
                "mode": "blinded",
                "annotated": False,
                "prediction_frozen": False,
                "reference_revealed_after_prediction": False,
            },
        })
        sealed.append({
            "id": case_id,
            "study_uid_hash": study_hash,
            "source_study_id": sid,
            "target_positive": refs[sid]["target_positive"],
            "reference_type": refs[sid]["reference_type"],
        })

    return {
        "schema_version": "1.1-preprediction",
        "dataset_class": "blinded_accuracy",
        "source_id": "rsna-ich-2019",
        "authorized": True,
        "deidentified": True,
        "protocol_prespecified": True,
        "independent_reference": True,
        "modality": "ct_mri",
        "target_condition": "any_acute_ich",
        "target_question": "Is acute intracranial hemorrhage present on this non-contrast head CT exam?",
        "reference_standard": {
            "type": "RSNA multi-reader majority/adjudicated expert reference"
        },
        "patient_grouping_prespecified": True,
        "metrics_requested": False,
        "render_protocol_status": "must_be_frozen_before_visual_prediction",
        "cases": blinded,
    }, {
        "schema_version": "1.0",
        "source_id": "rsna-ich-2019",
        "references": sealed,
        "case_count": len(sealed),
        "positive_reference_cases": positives,
        "negative_reference_cases": negatives,
    }

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("images_csv", type=Path)
    p.add_argument("references_csv", type=Path)
    p.add_argument("output_dir", type=Path)
    p.add_argument("--salt", required=True)
    args = p.parse_args()
    blinded, sealed = prepare(args.images_csv, args.references_csv, args.salt)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "blinded_manifest.json").write_text(
        json.dumps(blinded, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (args.output_dir / "SEALED_REFERENCE_DO_NOT_REVEAL.json").write_text(
        json.dumps(sealed, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "case_count": sealed["case_count"],
        "positive_reference_cases": sealed["positive_reference_cases"],
        "negative_reference_cases": sealed["negative_reference_cases"],
    }))
