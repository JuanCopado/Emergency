#!/usr/bin/env python3
"""Evaluate completed, authorized image-review cases from JSON.

This script scores recorded outputs; it does not inspect images or establish
ground truth. Reference diagnoses must come from an independent clinical source.
Cases lacking a reference or prediction are reported but excluded from metrics.
When ``require_blinded_for_metrics`` is true, annotated or non-blinded cases are
also excluded from performance metrics and remain teaching/workflow cases only.
"""

import argparse
import json
from pathlib import Path


URGENCY = {"routine": 0, "urgent": 1, "emergent": 2}


def norm(value):
    return " ".join(str(value or "").strip().casefold().split())


def ratio(numerator, denominator):
    return None if denominator == 0 else round(numerator / denominator, 4)


def diagnosis_matches(predicted, accepted):
    predicted = norm(predicted)
    accepted = {norm(item) for item in accepted if norm(item)}
    return bool(predicted and predicted in accepted)


def evaluate(data):
    cases = data.get("cases", [])
    usable = []
    excluded = []
    teaching_only = []
    require_blinded = bool(data.get("require_blinded_for_metrics"))
    for case in cases:
        if not case.get("reference") or not case.get("prediction"):
            excluded.append({"id": case.get("id", "unknown"),
                             "reason": "missing_reference_or_prediction"})
        elif require_blinded and (
                case.get("evaluation", {}).get("mode") != "blinded" or
                bool(case.get("evaluation", {}).get("annotated"))):
            teaching_only.append({
                "id": case.get("id", "unknown"),
                "reason": "not_blinded" if case.get("evaluation", {}).get("mode") != "blinded"
                else "annotated_image",
            })
        else:
            usable.append(case)

    counts = {
        "usable_cases": len(usable),
        "excluded_cases": len(excluded),
        "teaching_only_cases": len(teaching_only),
        "diagnostic_reference_cases": 0,
        "leading_correct": 0,
        "top3_correct": 0,
        "critical_reference_cases": 0,
        "critical_detected": 0,
        "abnormal_reference_cases": 0,
        "false_normal_claims": 0,
        "nondiagnostic_reference_cases": 0,
        "appropriate_abstentions": 0,
        "urgency_reference_cases": 0,
        "urgency_correct": 0,
        "undertriage_cases": 0,
    }

    case_results = []
    for case in usable:
        ref = case["reference"]
        pred = case["prediction"]
        accepted = ref.get("accepted_diagnoses", [])
        quality = ref.get("diagnostic_quality")
        abnormal = bool(ref.get("abnormal"))
        critical = bool(ref.get("critical"))
        abstained = bool(pred.get("abstained"))

        result = {"id": case.get("id", "unknown")}
        if quality == "adequate" and accepted:
            counts["diagnostic_reference_cases"] += 1
            result["leading_correct"] = diagnosis_matches(pred.get("leading_diagnosis"), accepted)
            differential = pred.get("differential", [])[:3]
            result["top3_correct"] = result["leading_correct"] or any(
                diagnosis_matches(item, accepted) for item in differential)
            counts["leading_correct"] += int(result["leading_correct"])
            counts["top3_correct"] += int(result["top3_correct"])

        if critical:
            counts["critical_reference_cases"] += 1
            detected = bool(pred.get("critical_flag"))
            result["critical_detected"] = detected
            counts["critical_detected"] += int(detected)

        if abnormal:
            counts["abnormal_reference_cases"] += 1
            false_normal = bool(pred.get("normal_claim"))
            result["false_normal_claim"] = false_normal
            counts["false_normal_claims"] += int(false_normal)

        if quality == "non_diagnostic":
            counts["nondiagnostic_reference_cases"] += 1
            result["appropriate_abstention"] = abstained
            counts["appropriate_abstentions"] += int(abstained)

        ref_urgency = ref.get("urgency")
        pred_urgency = pred.get("urgency")
        if ref_urgency in URGENCY and pred_urgency in URGENCY:
            counts["urgency_reference_cases"] += 1
            result["urgency_correct"] = ref_urgency == pred_urgency
            result["undertriage"] = URGENCY[pred_urgency] < URGENCY[ref_urgency]
            counts["urgency_correct"] += int(result["urgency_correct"])
            counts["undertriage_cases"] += int(result["undertriage"])

        case_results.append(result)

    metrics = {
        "leading_diagnosis_accuracy": {
            "value": ratio(counts["leading_correct"], counts["diagnostic_reference_cases"]),
            "numerator": counts["leading_correct"], "denominator": counts["diagnostic_reference_cases"]},
        "top3_recall": {"value": ratio(counts["top3_correct"], counts["diagnostic_reference_cases"]),
            "numerator": counts["top3_correct"], "denominator": counts["diagnostic_reference_cases"]},
        "critical_finding_sensitivity": {"value": ratio(counts["critical_detected"], counts["critical_reference_cases"]),
            "numerator": counts["critical_detected"], "denominator": counts["critical_reference_cases"]},
        "false_reassurance_rate": {"value": ratio(counts["false_normal_claims"], counts["abnormal_reference_cases"]),
            "numerator": counts["false_normal_claims"], "denominator": counts["abnormal_reference_cases"]},
        "appropriate_abstention_rate": {"value": ratio(counts["appropriate_abstentions"], counts["nondiagnostic_reference_cases"]),
            "numerator": counts["appropriate_abstentions"], "denominator": counts["nondiagnostic_reference_cases"]},
        "urgency_accuracy": {"value": ratio(counts["urgency_correct"], counts["urgency_reference_cases"]),
            "numerator": counts["urgency_correct"], "denominator": counts["urgency_reference_cases"]},
        "undertriage_rate": {"value": ratio(counts["undertriage_cases"], counts["urgency_reference_cases"]),
            "numerator": counts["undertriage_cases"], "denominator": counts["urgency_reference_cases"]},
    }
    return {"counts": counts, "metrics": metrics,
            "excluded_case_ids": [item["id"] for item in excluded],
            "exclusions": excluded, "teaching_only": teaching_only,
            "case_results": case_results,
            "limitations": ["Metrics describe only supplied cases with independent references.",
                            "Annotated, source-known or otherwise non-blinded cases are not diagnostic-accuracy evidence.",
                            "No confidence interval or clinical performance claim is valid for small or selected samples."]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = evaluate(json.loads(args.dataset.read_text(encoding="utf-8")))
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
