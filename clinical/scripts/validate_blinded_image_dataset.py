#!/usr/bin/env python3
"""Strict validation gate for blinded clinical-image evaluation datasets."""

import argparse
import json
from pathlib import Path

ALLOWED_CLASSES={"workflow_only","teaching_source_known","blinded_accuracy","prospective_validation"}

def validate(data):
    errors=[]
    warnings=[]
    klass=data.get("dataset_class")
    if klass not in ALLOWED_CLASSES:
        errors.append("invalid dataset_class")
        return {"errors":errors,"warnings":warnings,"metrics_eligible":False}
    cases=data.get("cases",[])
    if not isinstance(cases,list):
        errors.append("cases must be a list")
        cases=[]
    metrics_requested=bool(data.get("metrics_requested"))
    strict=klass in {"blinded_accuracy","prospective_validation"}
    if strict:
        for field in ("authorized","deidentified","protocol_prespecified","independent_reference"):
            if data.get(field) is not True:
                errors.append(f"{field} must be true for {klass}")
        if not data.get("target_question"):
            errors.append("target_question required for blinded/prospective dataset")
    seen=set()
    positives=0
    negatives=0
    for case in cases:
        cid=case.get("id")
        if not cid:
            errors.append("case missing id")
            continue
        if cid in seen:
            errors.append(f"duplicate case id: {cid}")
        seen.add(cid)
        ev=case.get("evaluation",{})
        ref=case.get("reference")
        pred=case.get("prediction")
        if strict:
            if ev.get("mode")!="blinded":
                errors.append(f"{cid}: evaluation.mode must be blinded")
            if ev.get("annotated") is not False:
                errors.append(f"{cid}: annotated must be false")
            if ev.get("reference_revealed_after_prediction") is not True:
                errors.append(f"{cid}: reference must be revealed only after prediction freeze")
            if ev.get("prediction_frozen") is not True:
                errors.append(f"{cid}: prediction_frozen must be true")
            if not case.get("study_uid_hash"):
                errors.append(f"{cid}: study_uid_hash required for leakage control")
            if not ref:
                errors.append(f"{cid}: independent reference required")
            if not pred:
                errors.append(f"{cid}: recorded prediction required")
        if ref and "target_positive" in ref:
            if bool(ref["target_positive"]):
                positives+=1
            else:
                negatives+=1
    metrics_eligible = strict and not errors
    if metrics_requested and not strict:
        errors.append("metrics requested for non-blinded dataset")
        metrics_eligible=False
    if metrics_requested and strict:
        if positives==0 or negatives==0:
            errors.append("sensitivity/specificity require both positive and negative reference cases")
            metrics_eligible=False
    if klass=="teaching_source_known" and metrics_requested:
        errors.append("source-known teaching cases cannot be used for performance metrics")
    return {"errors":errors,"warnings":warnings,"metrics_eligible":metrics_eligible,"case_count":len(cases),"positive_reference_cases":positives,"negative_reference_cases":negatives}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("dataset",type=Path)
    args=p.parse_args()
    result=validate(json.loads(args.dataset.read_text(encoding="utf-8")))
    print(json.dumps(result,indent=2,ensure_ascii=False))
    raise SystemExit(bool(result["errors"]))
