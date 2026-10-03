#!/usr/bin/env python3
"""Prepare EchoNet-Dynamic official-test blind cohort for EF <40%."""
import argparse,csv,hashlib,json
from pathlib import Path

def _hash(v,s): return hashlib.sha256(f"{s}:{v}".encode()).hexdigest()

def prepare(filelist_csv, salt):
    if len(salt)<16: raise ValueError("salt must be at least 16 characters")
    rows=[]
    with Path(filelist_csv).open(newline="",encoding="utf-8") as f:
        reader=csv.DictReader(f)
        required={"FileName","EF","Split"}
        missing=required-set(reader.fieldnames or [])
        if missing: raise ValueError(f"missing columns: {sorted(missing)}")
        for row in reader:
            if row["Split"].strip().upper()!="TEST": continue
            name=row["FileName"].strip()
            if not name: raise ValueError("empty FileName")
            ef=float(row["EF"])
            if not (0 <= ef <= 100): raise ValueError(f"{name}: EF outside 0-100")
            rows.append((name,ef))
    if not rows: raise ValueError("no TEST videos")
    pos=sum(1 for _,ef in rows if ef<40.0)
    neg=len(rows)-pos
    if not pos or not neg: raise ValueError("TEST cohort must contain both EF groups")
    cases=[]; refs=[]
    for name,ef in sorted(rows):
        h=_hash(name,salt); cid=f"echonet-{h[:16]}"
        cases.append({
            "id":cid,
            "patient_uid_hash":h,
            "study_uid_hash":h,
            "video_uid_hash":h,
            "evaluation":{"mode":"blinded","annotated":False,"prediction_frozen":False,
                          "reference_revealed_after_prediction":False}
        })
        refs.append({"id":cid,"study_uid_hash":h,"source_filename":name,
                     "ejection_fraction":ef,"target_positive":ef<40.0})
    return {
        "schema_version":"1.1-preprediction","dataset_class":"blinded_accuracy",
        "source_id":"echonet-dynamic","authorized":False,"deidentified":True,
        "protocol_prespecified":True,"independent_reference":True,"modality":"pocus",
        "target_condition":"lvef_below_40_percent",
        "target_question":"Is reference LVEF below 40.0% on this apical-4-chamber echocardiography video?",
        "reference_standard":{"type":"clinical EF measured by sonographer and verified by level-3 echocardiographer"},
        "patient_grouping_prespecified":True,"metrics_requested":False,
        "visual_input_protocol":"qa/ECHONET_VISUAL_INPUT_PROTOCOL.md","cases":cases
    },{
        "schema_version":"1.0","source_id":"echonet-dynamic","references":refs,
        "case_count":len(refs),"positive_reference_cases":pos,"negative_reference_cases":neg
    }

if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("filelist_csv",type=Path)
    p.add_argument("output_dir",type=Path); p.add_argument("--salt",required=True)
    a=p.parse_args(); b,r=prepare(a.filelist_csv,a.salt); a.output_dir.mkdir(parents=True,exist_ok=True)
    (a.output_dir/"blinded_manifest.json").write_text(json.dumps(b,indent=2)+"\n")
    (a.output_dir/"SEALED_REFERENCE_DO_NOT_REVEAL.json").write_text(json.dumps(r,indent=2)+"\n")
