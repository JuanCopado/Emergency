#!/usr/bin/env python3
"""Create a fail-closed blinded-image dataset manifest.

The generated manifest is intentionally NOT validation-ready:
authorized/deidentified/independent_reference are false until a human completes them.
"""

import argparse
import json
from pathlib import Path

ALLOWED_MODALITIES = {
    "musculoskeletal_xray", "chest_xray", "pocus", "ecg", "blood_gas",
    "skin_wound", "ct_mri", "ophthalmology", "other"
}

def build(modality, target_condition, target_question, reference_type="independent_expert_reference"):
    if modality not in ALLOWED_MODALITIES:
        raise ValueError(f"unsupported modality: {modality}")
    if not target_condition.strip() or not target_question.strip():
        raise ValueError("target_condition and target_question are required")
    return {
        "schema_version": "1.1",
        "dataset_class": "blinded_accuracy",
        "authorized": False,
        "deidentified": False,
        "protocol_prespecified": True,
        "independent_reference": False,
        "modality": modality,
        "target_condition": target_condition,
        "target_question": target_question,
        "reference_standard": {
            "type": reference_type,
            "description": "Complete independent reference/adjudication method before validation"
        },
        "patient_grouping_prespecified": True,
        "metrics_requested": False,
        "cases": []
    }

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("modality", choices=sorted(ALLOWED_MODALITIES))
    p.add_argument("target_condition")
    p.add_argument("target_question")
    p.add_argument("output", type=Path)
    p.add_argument("--reference-type", default="independent_expert_reference")
    args = p.parse_args()
    data = build(args.modality, args.target_condition, args.target_question, args.reference_type)
    args.output.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(args.output)
