#!/usr/bin/env python3
"""Compute blinded clinical-image metrics only after strict dataset validation."""

import argparse
import json
import math
from pathlib import Path

from validate_blinded_image_dataset import validate

def _wilson(successes, total, z=1.959963984540054):
    if total <= 0:
        return None
    p = successes / total
    denom = 1 + z*z/total
    centre = (p + z*z/(2*total)) / denom
    half = z * math.sqrt((p*(1-p)/total) + z*z/(4*total*total)) / denom
    return [max(0.0, centre-half), min(1.0, centre+half)]

def _safe(num, den):
    return None if den == 0 else num / den

def calculate(data):
    gate = validate(data)
    if gate["errors"]:
        return {"errors": gate["errors"], "metrics": None, "gate": gate}

    tp = fp = tn = fn = abstain = nondiagnostic = 0
    unresolved_positive = unresolved_negative = 0

    for case in data.get("cases", []):
        ref_pos = bool(case["reference"]["target_positive"])
        pred = case.get("prediction", {})
        pred_class = pred.get("class")
        if pred_class is None and "target_positive" in pred:
            pred_class = "positive" if bool(pred["target_positive"]) else "negative"

        if pred_class == "positive":
            if ref_pos:
                tp += 1
            else:
                fp += 1
        elif pred_class == "negative":
            if ref_pos:
                fn += 1
            else:
                tn += 1
        elif pred_class == "abstain":
            abstain += 1
            if ref_pos:
                unresolved_positive += 1
            else:
                unresolved_negative += 1
        elif pred_class == "nondiagnostic":
            nondiagnostic += 1
            if ref_pos:
                unresolved_positive += 1
            else:
                unresolved_negative += 1

    total = len(data.get("cases", []))
    classified = tp + fp + tn + fn
    unresolved = abstain + nondiagnostic
    full_binary_coverage = unresolved == 0 and total > 0

    metrics = {
        "n": total,
        "tp": tp, "fp": fp, "tn": tn, "fn": fn,
        "abstain": abstain,
        "nondiagnostic": nondiagnostic,
        "unresolved_reference_positive": unresolved_positive,
        "unresolved_reference_negative": unresolved_negative,
        "classified_cases": classified,
        "coverage": _safe(classified, total),
        "abstention_rate": _safe(abstain, total),
        "nondiagnostic_rate": _safe(nondiagnostic, total),
        "standard_binary_metrics_available": full_binary_coverage,
        "sensitivity": None,
        "specificity": None,
        "ppv": None,
        "npv": None,
        "accuracy": None,
        "sensitivity_95ci_wilson": None,
        "specificity_95ci_wilson": None,
    }

    if full_binary_coverage:
        metrics["sensitivity"] = _safe(tp, tp + fn)
        metrics["specificity"] = _safe(tn, tn + fp)
        metrics["ppv"] = _safe(tp, tp + fp)
        metrics["npv"] = _safe(tn, tn + fn)
        metrics["accuracy"] = _safe(tp + tn, total)
        metrics["sensitivity_95ci_wilson"] = _wilson(tp, tp + fn)
        metrics["specificity_95ci_wilson"] = _wilson(tn, tn + fp)
    else:
        metrics["metric_limit"] = (
            "Standard sensitivity/specificity suppressed because one or more cases "
            "were abstain/nondiagnostic; report coverage and unresolved counts instead."
        )

    return {"errors": [], "metrics": metrics, "gate": gate}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("dataset", type=Path)
    args = p.parse_args()
    result = calculate(json.loads(args.dataset.read_text(encoding="utf-8")))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(bool(result["errors"]))
