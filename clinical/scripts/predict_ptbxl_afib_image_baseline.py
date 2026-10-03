#!/usr/bin/env python3
"""Blinded AFIB engineering baseline for standardized PTB-XL ECG renders.

This baseline deliberately uses only the model-facing PNGs. It never reads PTB-XL
metadata, source IDs or sealed references. It is an engineering comparator, not
a clinically validated AF detector.

Pre-reveal frozen rule:
- positive: RR CV >=0.18 AND normalized RMSSD >=0.22 AND RR MAD ratio >=0.08
- negative: RR CV <=0.08 AND normalized RMSSD <=0.12 AND RR MAD ratio <=0.05
- nondiagnostic: trace/QRS extraction fails or <5 detected QRS complexes
- abstain: everything else
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

POS_CV = 0.18
POS_RMSSD = 0.22
POS_MAD = 0.08
NEG_CV = 0.08
NEG_RMSSD = 0.12
NEG_MAD = 0.05
MIN_QRS = 5

def classify_features(npeaks, cv, rmssd, mad):
    if npeaks is None or npeaks < MIN_QRS:
        return "nondiagnostic"
    if cv is None or rmssd is None or mad is None:
        return "nondiagnostic"
    if cv >= POS_CV and rmssd >= POS_RMSSD and mad >= POS_MAD:
        return "positive"
    if cv <= NEG_CV and rmssd <= NEG_RMSSD and mad <= NEG_MAD:
        return "negative"
    return "abstain"

def extract_features(image_path):
    import numpy as np
    from PIL import Image
    from scipy.ndimage import uniform_filter1d
    from scipy.signal import butter, filtfilt, find_peaks

    image = np.asarray(Image.open(image_path).convert("RGB"))
    h, w, _ = image.shape

    # Frozen against the standardized v1.36 renderer; use relative crop so modest
    # PNG dimension changes do not move the lead-II rhythm strip out of scope.
    y0, y1 = int(h * 0.711), int(h * 0.938)
    x0, x1 = int(w * 0.042), int(w * 0.956)
    crop = image[y0:y1, x0:x1]
    r, g, b = crop[:, :, 0], crop[:, :, 1], crop[:, :, 2]
    mask = (b > 120) & (b > r * 1.15) & ((b.astype(float) - r.astype(float)) > 25)

    counts = mask.sum(axis=0)
    good = counts > 0
    if int(good.sum()) < 500:
        return {"npeaks": 0, "cv": None, "rmssd": None, "mad": None}

    rows = np.arange(mask.shape[0], dtype=float)[:, None]
    sums = (mask * rows).sum(axis=0)
    trace = np.full(mask.shape[1], np.nan, dtype=float)
    trace[good] = sums[good] / counts[good]
    x = np.arange(len(trace))
    trace = np.interp(x, x[good], trace[good])
    signal = -trace

    # The rendered rhythm strip spans 10 s.
    fs = len(signal) / 10.0
    baseline = uniform_filter1d(signal, max(3, int(fs * 0.8)), mode="nearest")
    signal = signal - baseline

    low, high = 5.0 / (fs / 2.0), 18.0 / (fs / 2.0)
    if not (0 < low < high < 1):
        return {"npeaks": 0, "cv": None, "rmssd": None, "mad": None}

    bb, aa = butter(2, [low, high], btype="band")
    filtered = filtfilt(bb, aa, signal)
    derivative = np.diff(filtered, prepend=filtered[0])
    energy = derivative * derivative
    integrated = uniform_filter1d(energy, max(3, int(fs * 0.12)), mode="nearest")

    prominence = max(float(np.percentile(integrated, 75)) * 0.25,
                     float(np.std(integrated)) * 0.20)
    height = float(np.percentile(integrated, 65))
    peaks, _ = find_peaks(
        integrated,
        distance=max(1, int(fs * 0.28)),
        prominence=prominence,
        height=height,
    )
    peaks = peaks[(peaks > fs * 0.1) & (peaks < len(signal) - fs * 0.1)]
    rr = np.diff(peaks)
    if len(rr) < 4:
        return {"npeaks": int(len(peaks)), "cv": None, "rmssd": None, "mad": None}

    mean_rr = float(np.mean(rr))
    median_rr = float(np.median(rr))
    cv = float(np.std(rr) / mean_rr)
    rmssd = float(np.sqrt(np.mean(np.diff(rr) ** 2)) / mean_rr)
    mad = float(np.median(np.abs(rr - median_rr)) / median_rr)

    return {"npeaks": int(len(peaks)), "cv": cv, "rmssd": rmssd, "mad": mad}

def predict(blinded_manifest, root_dir, frozen_at=None):
    frozen_at = frozen_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    predictions = []
    feature_rows = []
    for case in blinded_manifest.get("cases", []):
        image_file = case.get("image_file")
        if not image_file:
            raise ValueError(f"{case.get('id')}: image_file required")
        features = extract_features(Path(root_dir) / image_file)
        pred_class = classify_features(
            features.get("npeaks"), features.get("cv"),
            features.get("rmssd"), features.get("mad")
        )
        predictions.append({
            "id": case["id"],
            "class": pred_class,
            "prediction_frozen_at": frozen_at,
        })
        feature_rows.append({"id": case["id"], **features, "class": pred_class})
    return {
        "schema_version": "1.0",
        "interpreter": "ptbxl-afib-render-irregularity-baseline-v1",
        "target_condition": blinded_manifest.get("target_condition"),
        "prediction_frozen_at": frozen_at,
        "rule": {
            "positive": {"cv_gte": POS_CV, "rmssd_gte": POS_RMSSD, "mad_gte": POS_MAD},
            "negative": {"cv_lte": NEG_CV, "rmssd_lte": NEG_RMSSD, "mad_lte": NEG_MAD},
            "min_qrs": MIN_QRS,
        },
        "predictions": predictions,
        "features": feature_rows,
    }

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("blinded_manifest", type=Path)
    p.add_argument("artifact_root", type=Path)
    p.add_argument("output", type=Path)
    args = p.parse_args()
    manifest = json.loads(args.blinded_manifest.read_text(encoding="utf-8"))
    result = predict(manifest, args.artifact_root)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    counts = {}
    for item in result["predictions"]:
        counts[item["class"]] = counts.get(item["class"], 0) + 1
    print(json.dumps({"prediction_count": len(result["predictions"]), "class_counts": counts,
                      "prediction_frozen_at": result["prediction_frozen_at"]}, ensure_ascii=False))
