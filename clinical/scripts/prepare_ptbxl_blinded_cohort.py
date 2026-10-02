#!/usr/bin/env python3
"""Prepare a blinded PTB-XL cohort with references stored separately.

This script does not render ECG images and does not run diagnostic evaluation.
It creates a model-facing cohort file without labels and a sealed reference file
that must not be revealed until predictions are frozen.
"""

import argparse
import ast
import csv
import hashlib
import json
from pathlib import Path

def _hash(value, salt):
    return hashlib.sha256(f"{salt}:{value}".encode("utf-8")).hexdigest()

def _parse_codes(raw):
    value = ast.literal_eval(raw)
    if not isinstance(value, dict):
        raise ValueError("scp_codes must decode to a dict")
    return value

def prepare(database_csv, target_code, salt, fold=10):
    if not target_code.strip():
        raise ValueError("target_code is required")
    if not salt or len(salt) < 16:
        raise ValueError("salt must be at least 16 characters and kept outside the repository")

    blinded_cases = []
    references = []
    positives = negatives = 0

    with Path(database_csv).open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"ecg_id", "patient_id", "strat_fold", "scp_codes"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"missing PTB-XL columns: {sorted(missing)}")

        for row in reader:
            if int(row["strat_fold"]) != int(fold):
                continue
            codes = _parse_codes(row["scp_codes"])
            target_positive = target_code in codes and float(codes[target_code]) > 0
            patient_hash = _hash(row["patient_id"], salt)
            study_hash = _hash(row["ecg_id"], salt)
            case_id = f"ptbxl-{study_hash[:16]}"

            blinded_cases.append({
                "id": case_id,
                "patient_uid_hash": patient_hash,
                "study_uid_hash": study_hash,
                "source_record_hash": study_hash,
                "source_fold": int(fold),
            })
            references.append({
                "id": case_id,
                "study_uid_hash": study_hash,
                "target_positive": bool(target_positive),
                "reference_source": "PTB-XL scp_codes",
                "target_code": target_code,
            })
            if target_positive:
                positives += 1
            else:
                negatives += 1

    if not blinded_cases:
        raise ValueError("no cases selected")
    if positives == 0 or negatives == 0:
        raise ValueError("selected cohort must contain both positive and negative reference cases")

    cohort = {
        "schema_version": "1.0",
        "source_id": "ptb-xl",
        "source_version": "1.0.3-or-later-currently-reviewed",
        "dataset_class": "blinded_accuracy",
        "modality": "ecg",
        "target_condition": target_code,
        "target_question": f"Is PTB-XL target code {target_code} present on this ECG?",
        "selection_rule": f"PTB-XL strat_fold == {int(fold)}",
        "patient_grouping_prespecified": True,
        "labels_separated": True,
        "reference_file_sealed_until_prediction_freeze": True,
        "benchmark_contamination_risk": "unknown_model_pretraining_exposure",
        "cases": blinded_cases,
    }
    reference = {
        "schema_version": "1.0",
        "source_id": "ptb-xl",
        "target_code": target_code,
        "fold": int(fold),
        "case_count": len(references),
        "positive_reference_cases": positives,
        "negative_reference_cases": negatives,
        "references": references,
    }
    return cohort, reference

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("database_csv", type=Path)
    p.add_argument("target_code")
    p.add_argument("cohort_output", type=Path)
    p.add_argument("reference_output", type=Path)
    p.add_argument("--salt", required=True, help=">=16 chars; keep outside repository")
    p.add_argument("--fold", type=int, default=10)
    args = p.parse_args()
    cohort, reference = prepare(args.database_csv, args.target_code, args.salt, args.fold)
    args.cohort_output.write_text(json.dumps(cohort, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.reference_output.write_text(json.dumps(reference, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "cohort": str(args.cohort_output),
        "sealed_reference": str(args.reference_output),
        "case_count": len(cohort["cases"]),
        "warning": "Do not reveal sealed_reference until all predictions are frozen."
    }, ensure_ascii=False))
