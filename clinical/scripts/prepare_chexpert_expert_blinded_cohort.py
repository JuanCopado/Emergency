#!/usr/bin/env python3
"""Prepare a fail-closed CheXpert expert-test blinded cohort.

Expected images CSV:
study_id,patient_id,image_path[,view]

Expected expert ground truth CSV:
study_id,<target columns...>

Only explicitly allowed expert-test targets are accepted.
"""

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ALLOWED_TARGETS = {
    "Atelectasis",
    "Cardiomegaly",
    "Consolidation",
    "Edema",
    "Pleural Effusion",
}

def _hash(value, salt):
    return hashlib.sha256(f"{salt}:{value}".encode("utf-8")).hexdigest()

def _truth(value):
    v = str(value).strip().lower()
    if v in {"1", "true", "positive"}:
        return True
    if v in {"0", "false", "negative"}:
        return False
    raise ValueError(f"expert test truth must be binary 0/1, got {value!r}")

def prepare(images_csv, groundtruth_csv, target, salt):
    if target not in ALLOWED_TARGETS:
        raise ValueError(f"unsupported target: {target}")
    if len(salt) < 16:
        raise ValueError("salt must be at least 16 characters")

    studies = defaultdict(list)
    patients = {}
    with Path(images_csv).open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"study_id", "patient_id", "image_path"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"images CSV missing columns: {sorted(missing)}")
        for row in reader:
            sid = row["study_id"].strip()
            pid = row["patient_id"].strip()
            path = row["image_path"].strip()
            if not sid or not pid or not path:
                raise ValueError("study_id/patient_id/image_path required")
            if sid in patients and patients[sid] != pid:
                raise ValueError(f"{sid}: inconsistent patient_id")
            patients[sid] = pid
            studies[sid].append({
                "image_path": path,
                "view": (row.get("view") or "").strip(),
            })

    gt = {}
    with Path(groundtruth_csv).open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if "study_id" not in (reader.fieldnames or []) or target not in (reader.fieldnames or []):
            raise ValueError("groundtruth CSV must contain study_id and requested target")
        for row in reader:
            sid = row["study_id"].strip()
            if sid in gt:
                raise ValueError(f"duplicate groundtruth study_id: {sid}")
            gt[sid] = _truth(row[target])

    eligible = sorted(set(studies) & set(gt))
    if not eligible:
        raise ValueError("no expert-test studies matched images to groundtruth")

    pos = sum(1 for sid in eligible if gt[sid])
    neg = len(eligible) - pos
    if not pos or not neg:
        raise ValueError("cohort must contain positive and negative expert references")

    blind_cases, refs = [], []
    for sid in eligible:
        study_hash = _hash(sid, salt)
        patient_hash = _hash(patients[sid], salt)
        cid = f"chexpert-{study_hash[:16]}"
        views = sorted(studies[sid], key=lambda x: (x["view"], x["image_path"]))
        blind_cases.append({
            "id": cid,
            "patient_uid_hash": patient_hash,
            "study_uid_hash": study_hash,
            "images": [
                {
                    "image_uid_hash": _hash(v["image_path"], salt),
                    "view": v["view"] or None,
                }
                for v in views
            ],
            "evaluation": {
                "mode": "blinded",
                "annotated": False,
                "prediction_frozen": False,
                "reference_revealed_after_prediction": False,
            },
        })
        refs.append({
            "id": cid,
            "study_uid_hash": study_hash,
            "source_study_id": sid,
            "target_positive": gt[sid],
            "reference_type": "majority_vote_5_of_8_board_certified_radiologists",
        })

    return {
        "schema_version": "1.1-preprediction",
        "dataset_class": "blinded_accuracy",
        "source_id": "chexpert",
        "authorized": False,
        "deidentified": True,
        "protocol_prespecified": True,
        "independent_reference": True,
        "modality": "chest_xray",
        "target_condition": target,
        "target_question": f"Is {target} present on this chest radiograph study?",
        "reference_standard": {
            "type": "CheXpert expert test set majority vote of 5/8 board-certified radiologists"
        },
        "patient_grouping_prespecified": True,
        "metrics_requested": False,
        "visual_input_protocol": "qa/CXR_VISUAL_INPUT_PROTOCOL.md",
        "cases": blind_cases,
    }, {
        "schema_version": "1.0",
        "source_id": "chexpert",
        "target_condition": target,
        "references": refs,
        "case_count": len(refs),
        "positive_reference_cases": pos,
        "negative_reference_cases": neg,
    }

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("images_csv", type=Path)
    p.add_argument("groundtruth_csv", type=Path)
    p.add_argument("target")
    p.add_argument("output_dir", type=Path)
    p.add_argument("--salt", required=True)
    args = p.parse_args()
    blind, ref = prepare(args.images_csv, args.groundtruth_csv, args.target, args.salt)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "blinded_manifest.json").write_text(
        json.dumps(blind, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (args.output_dir / "SEALED_REFERENCE_DO_NOT_REVEAL.json").write_text(
        json.dumps(ref, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
