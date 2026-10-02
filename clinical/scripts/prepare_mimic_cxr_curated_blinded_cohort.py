#!/usr/bin/env python3
"""Prepare MIMIC-CXR-JPG 2.1.0 manually-curated test cohort.

Expected images CSV columns:
subject_id,study_id,dicom_id,image_path[,ViewPosition]

Expected curated labels CSV is mimic-cxr-2.1.0-test-set-labeled-like:
study_id,<target columns>

Only explicit 1.0 and 0.0 references are admitted.
Blank and -1.0 are excluded by prespecified rule before blinding.
"""

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ALLOWED_TARGETS = {
    "Atelectasis","Cardiomegaly","Consolidation","Edema",
    "Enlarged Cardiomediastinum","Fracture","Lung Lesion","Lung Opacity",
    "Pleural Effusion","Pneumonia","Pneumothorax","Pleural Other",
    "Support Devices","No Finding",
}

def _hash(v,s): return hashlib.sha256(f"{s}:{v}".encode("utf-8")).hexdigest()

def _label(v):
    x=str(v).strip()
    if x in {"1","1.0"}: return True
    if x in {"0","0.0"}: return False
    if x in {"","-1","-1.0"}: return None
    raise ValueError(f"unsupported curated label: {v!r}")

def prepare(images_csv, labels_csv, target, salt):
    if target not in ALLOWED_TARGETS: raise ValueError(f"unsupported target: {target}")
    if len(salt)<16: raise ValueError("salt must be at least 16 characters")

    studies=defaultdict(list); subjects={}
    with Path(images_csv).open(newline="",encoding="utf-8") as f:
        r=csv.DictReader(f); req={"subject_id","study_id","dicom_id","image_path"}
        missing=req-set(r.fieldnames or [])
        if missing: raise ValueError(f"images CSV missing: {sorted(missing)}")
        for row in r:
            sid=row["study_id"].strip(); subj=row["subject_id"].strip()
            did=row["dicom_id"].strip(); path=row["image_path"].strip()
            if not all([sid,subj,did,path]): raise ValueError("empty image identifiers")
            if sid in subjects and subjects[sid]!=subj: raise ValueError(f"{sid}: inconsistent subject")
            subjects[sid]=subj
            studies[sid].append({"dicom_id":did,"image_path":path,
                                 "view":(row.get("ViewPosition") or "").strip()})

    labels={}
    with Path(labels_csv).open(newline="",encoding="utf-8") as f:
        r=csv.DictReader(f)
        if "study_id" not in (r.fieldnames or []) or target not in (r.fieldnames or []):
            raise ValueError("labels CSV missing study_id or target")
        for row in r:
            sid=row["study_id"].strip()
            if sid in labels: raise ValueError(f"duplicate label study: {sid}")
            labels[sid]=_label(row[target])

    eligible=sorted(sid for sid in set(studies)&set(labels) if labels[sid] is not None)
    if not eligible: raise ValueError("no explicit binary curated references")
    pos=sum(1 for sid in eligible if labels[sid]); neg=len(eligible)-pos
    if not pos or not neg: raise ValueError("eligible cohort needs positive and negative references")

    cases=[]; refs=[]
    for sid in eligible:
        sh=_hash(sid,salt); ph=_hash(subjects[sid],salt); cid=f"mimiccxr-{sh[:16]}"
        imgs=sorted(studies[sid],key=lambda x:x["dicom_id"])
        cases.append({
            "id":cid,"patient_uid_hash":ph,"study_uid_hash":sh,
            "images":[{"image_uid_hash":_hash(x["dicom_id"],salt),
                       "source_path_token":_hash(x["image_path"],salt),
                       "view":x["view"] or None} for x in imgs],
            "evaluation":{"mode":"blinded","annotated":False,"prediction_frozen":False,
                          "reference_revealed_after_prediction":False}
        })
        refs.append({"id":cid,"study_uid_hash":sh,"source_study_id":sid,
                     "target_positive":labels[sid],
                     "reference_type":"mimic_cxr_2_1_0_manually_curated_test_label"})
    return {
        "schema_version":"1.1-preprediction","dataset_class":"blinded_accuracy",
        "source_id":"mimic-cxr-2.1.0","authorized":False,"deidentified":True,
        "protocol_prespecified":True,"independent_reference":True,
        "modality":"chest_xray","target_condition":target,
        "target_question":f"Is {target} explicitly present on this MIMIC-CXR test study?",
        "reference_standard":{"type":"MIMIC-CXR-JPG 2.1.0 manually curated test-set label; uncertain/blank excluded"},
        "patient_grouping_prespecified":True,"metrics_requested":False,"cases":cases
    },{
        "schema_version":"1.0","source_id":"mimic-cxr-2.1.0","target_condition":target,
        "references":refs,"case_count":len(refs),
        "positive_reference_cases":pos,"negative_reference_cases":neg
    }

if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("images_csv",type=Path)
    p.add_argument("labels_csv",type=Path); p.add_argument("target")
    p.add_argument("output_dir",type=Path); p.add_argument("--salt",required=True)
    a=p.parse_args(); b,r=prepare(a.images_csv,a.labels_csv,a.target,a.salt)
    a.output_dir.mkdir(parents=True,exist_ok=True)
    (a.output_dir/"blinded_manifest.json").write_text(json.dumps(b,indent=2)+"\n")
    (a.output_dir/"SEALED_REFERENCE_DO_NOT_REVEAL.json").write_text(json.dumps(r,indent=2)+"\n")
