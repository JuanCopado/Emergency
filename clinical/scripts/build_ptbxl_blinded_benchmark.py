#!/usr/bin/env python3
"""Build a blinded PTB-XL ECG image benchmark from PhysioNet v1.0.3.

Downloads only the selected low-resolution (100 Hz) WFDB records, renders each
ECG to a deterministic 12-lead image, writes a model-facing blinded manifest,
and stores labels/identifiers in a separate sealed reference JSON.

This is benchmark infrastructure, not clinical validation.
"""

import argparse
import ast
import csv
import hashlib
import json
import shutil
import tempfile
import urllib.request
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import wfdb

BASE_URLS = (
    "https://physionet-open.s3.amazonaws.com/ptb-xl/1.0.3/",
    "https://physionet.org/files/ptb-xl/1.0.3/",
)
LEADS = ["I","II","III","aVR","aVL","aVF","V1","V2","V3","V4","V5","V6"]

def _hash(value, salt):
    return hashlib.sha256(f"{salt}:{value}".encode("utf-8")).hexdigest()

def _parse_codes(raw):
    value = ast.literal_eval(raw)
    if not isinstance(value, dict):
        raise ValueError("scp_codes must decode to a dict")
    return value

def _download(urls, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    last_error = None
    for url in urls:
        try:
            with urllib.request.urlopen(url, timeout=30) as src, dest.open("wb") as dst:
                shutil.copyfileobj(src, dst)
            return
        except Exception as exc:
            last_error = exc
    raise RuntimeError(f"all PTB-XL download mirrors failed for {dest.name}: {last_error}")

def _record_urls(filename_lr):
    return (
        [base + filename_lr + ".hea" for base in BASE_URLS],
        [base + filename_lr + ".dat" for base in BASE_URLS],
    )

def _render_standard(record_path, output_png):
    rec = wfdb.rdrecord(str(record_path))
    if rec.fs != 100:
        raise ValueError(f"expected 100 Hz PTB-XL record, got {rec.fs}")
    signal = np.asarray(rec.p_signal, dtype=float)
    names = list(rec.sig_name)
    missing = [lead for lead in LEADS if lead not in names]
    if missing:
        raise ValueError(f"missing leads: {missing}")

    lead_idx = {name: i for i, name in enumerate(names)}
    fig = plt.figure(figsize=(16, 12), dpi=150)
    gs = fig.add_gridspec(4, 4, height_ratios=[1,1,1,1.15])

    segments = [
        ("I",0), ("aVR",1), ("V1",2), ("V4",3),
        ("II",0), ("aVL",1), ("V2",2), ("V5",3),
        ("III",0), ("aVF",1), ("V3",2), ("V6",3),
    ]
    for idx, (lead, col) in enumerate(segments):
        row = idx // 4
        ax = fig.add_subplot(gs[row, col])
        start = int(col * 2.5 * rec.fs)
        stop = start + int(2.5 * rec.fs)
        y = signal[start:stop, lead_idx[lead]]
        t = np.arange(len(y)) / rec.fs
        ax.plot(t, y, linewidth=0.8)
        ax.set_xlim(0, 2.5)
        ax.set_ylim(-2.5, 2.5)
        ax.set_xticks(np.arange(0, 2.51, 0.2), minor=False)
        ax.set_xticks(np.arange(0, 2.51, 0.04), minor=True)
        ax.set_yticks(np.arange(-2.5, 2.51, 0.5), minor=False)
        ax.set_yticks(np.arange(-2.5, 2.51, 0.1), minor=True)
        ax.grid(which="major", linewidth=0.5, alpha=0.45)
        ax.grid(which="minor", linewidth=0.25, alpha=0.20)
        ax.tick_params(labelbottom=False, labelleft=False, length=0)
        ax.text(0.02, 0.93, lead, transform=ax.transAxes, fontsize=10,
                verticalalignment="top")
        for spine in ax.spines.values():
            spine.set_visible(False)

    ax = fig.add_subplot(gs[3, :])
    y = signal[:, lead_idx["II"]]
    t = np.arange(len(y)) / rec.fs
    ax.plot(t, y, linewidth=0.8)
    ax.set_xlim(0, 10)
    ax.set_ylim(-2.5, 2.5)
    ax.set_xticks(np.arange(0, 10.01, 0.2), minor=False)
    ax.set_xticks(np.arange(0, 10.01, 0.04), minor=True)
    ax.set_yticks(np.arange(-2.5, 2.51, 0.5), minor=False)
    ax.set_yticks(np.arange(-2.5, 2.51, 0.1), minor=True)
    ax.grid(which="major", linewidth=0.5, alpha=0.45)
    ax.grid(which="minor", linewidth=0.25, alpha=0.20)
    ax.tick_params(labelbottom=False, labelleft=False, length=0)
    ax.text(0.01, 0.93, "II rhythm strip — 10 s", transform=ax.transAxes,
            fontsize=10, verticalalignment="top")
    for spine in ax.spines.values():
        spine.set_visible(False)

    fig.suptitle("12-lead ECG — standardized grid: 0.04 s / 0.1 mV minor divisions", fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.98])
    output_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_png, bbox_inches="tight")
    plt.close(fig)

def build(database_csv, target_code, salt, output_dir, fold=10, max_cases=0, pilot_per_class=0):
    if not target_code.strip():
        raise ValueError("target_code is required")
    if len(salt) < 16:
        raise ValueError("salt must be at least 16 characters")
    output_dir = Path(output_dir)
    images_dir = output_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    with Path(database_csv).open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"ecg_id","patient_id","strat_fold","scp_codes","filename_lr"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"missing PTB-XL columns: {sorted(missing)}")
        for row in reader:
            if int(row["strat_fold"]) == int(fold):
                codes = _parse_codes(row["scp_codes"])
                row["_target_positive"] = bool(
                    target_code in codes and float(codes[target_code]) > 0
                )
                rows.append(row)

    if not rows:
        raise ValueError("no fold cases selected")

    positives = [r for r in rows if r["_target_positive"]]
    negatives = [r for r in rows if not r["_target_positive"]]
    if not positives or not negatives:
        raise ValueError("target must have both positive and negative cases in selected fold")

    selection_mode = "full_fold"
    if pilot_per_class and pilot_per_class > 0:
        if len(positives) < pilot_per_class or len(negatives) < pilot_per_class:
            raise ValueError("pilot_per_class exceeds available positive/negative cases")
        rows = (
            sorted(positives, key=lambda r: int(r["ecg_id"]))[:pilot_per_class]
            + sorted(negatives, key=lambda r: int(r["ecg_id"]))[:pilot_per_class]
        )
        rows = sorted(rows, key=lambda r: int(r["ecg_id"]))
        selection_mode = f"balanced_pipeline_pilot_{pilot_per_class}_per_class"
    elif max_cases and max_cases > 0:
        if max_cases < len(positives) + 1:
            raise ValueError("max_cases too small: pilot must retain all positives plus >=1 negative")
        keep_neg = max_cases - len(positives)
        rows = sorted(positives, key=lambda r: int(r["ecg_id"])) + sorted(
            negatives, key=lambda r: int(r["ecg_id"])
        )[:keep_neg]
        selection_mode = "positive_preserving_pilot"
    else:
        rows = sorted(rows, key=lambda r: int(r["ecg_id"]))

    blinded_cases = []
    references = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for row in rows:
            patient_hash = _hash(row["patient_id"], salt)
            study_hash = _hash(row["ecg_id"], salt)
            case_id = f"ptbxl-{study_hash[:16]}"
            local_dir = tmp / case_id
            local_dir.mkdir(parents=True, exist_ok=True)
            original_base = Path(row["filename_lr"]).name
            recbase = local_dir / original_base
            hea_url, dat_url = _record_urls(row["filename_lr"])
            _download(hea_url, recbase.with_suffix(".hea"))
            _download(dat_url, recbase.with_suffix(".dat"))

            image_name = f"{case_id}.png"
            _render_standard(recbase, images_dir / image_name)
            blinded_cases.append({
                "id": case_id,
                "patient_uid_hash": patient_hash,
                "study_uid_hash": study_hash,
                "image_file": f"images/{image_name}",
                "evaluation": {
                    "mode": "blinded",
                    "annotated": False,
                    "prediction_frozen": False,
                    "reference_revealed_after_prediction": False
                }
            })
            references.append({
                "id": case_id,
                "study_uid_hash": study_hash,
                "source_ecg_id": row["ecg_id"],
                "source_patient_id": row["patient_id"],
                "source_filename_lr": row["filename_lr"],
                "target_positive": row["_target_positive"],
                "reference_source": "PTB-XL scp_codes",
                "target_code": target_code,
            })

    cohort = {
        "schema_version": "1.1-preprediction",
        "dataset_class": "blinded_accuracy",
        "source_id": "ptb-xl",
        "source_version": "1.0.3",
        "authorized": True,
        "deidentified": True,
        "protocol_prespecified": True,
        "independent_reference": True,
        "modality": "ecg",
        "target_condition": target_code,
        "target_question": f"Is PTB-XL target code {target_code} present on this ECG?",
        "reference_standard": {
            "type": "PTB-XL SCP-ECG cardiologist-derived annotation",
            "description": "Reference remains sealed until predictions are frozen."
        },
        "selection_rule": f"strat_fold == {int(fold)}",
        "selection_mode": selection_mode,
        "performance_metrics_allowed": selection_mode == "full_fold",
        "patient_grouping_prespecified": True,
        "metrics_requested": False,
        "render_protocol": "qa/PTBXL_BLINDED_PROTOCOL.md",
        "benchmark_contamination_risk": "unknown_model_pretraining_exposure",
        "cases": blinded_cases,
    }
    sealed = {
        "schema_version": "1.0",
        "source_id": "ptb-xl",
        "source_version": "1.0.3",
        "target_code": target_code,
        "fold": int(fold),
        "case_count": len(references),
        "positive_reference_cases": sum(1 for r in references if r["target_positive"]),
        "negative_reference_cases": sum(1 for r in references if not r["target_positive"]),
        "references": references,
    }
    (output_dir / "blinded_manifest.json").write_text(
        json.dumps(cohort, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (output_dir / "SEALED_REFERENCE_DO_NOT_REVEAL.json").write_text(
        json.dumps(sealed, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return cohort, sealed

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("database_csv", type=Path)
    p.add_argument("target_code")
    p.add_argument("output_dir", type=Path)
    p.add_argument("--salt", required=True)
    p.add_argument("--fold", type=int, default=10)
    p.add_argument("--max-cases", type=int, default=0)
    p.add_argument("--pilot-per-class", type=int, default=0)
    args = p.parse_args()
    cohort, sealed = build(
        args.database_csv, args.target_code, args.salt, args.output_dir,
        fold=args.fold, max_cases=args.max_cases, pilot_per_class=args.pilot_per_class
    )
    print(json.dumps({
        "case_count": len(cohort["cases"]),
        "positive_reference_cases": sealed["positive_reference_cases"],
        "negative_reference_cases": sealed["negative_reference_cases"],
        "blinded_manifest": str(args.output_dir / "blinded_manifest.json"),
        "sealed_reference": str(args.output_dir / "SEALED_REFERENCE_DO_NOT_REVEAL.json")
    }, ensure_ascii=False))
