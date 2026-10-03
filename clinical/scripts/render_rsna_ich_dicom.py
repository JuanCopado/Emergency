#!/usr/bin/env python3
"""Fail-closed RSNA ICH DICOM -> PNG renderer.

Frozen primary visual representation:
- non-contrast head CT
- standard brain window WW=80 HU, WL=40 HU
- slice order from ImageOrientationPatient + ImagePositionPatient geometry
- one SeriesInstanceUID per rendered exam
- no diagnostic labels or source IDs in output filenames

Heavy dependencies (pydicom/numpy/Pillow) are imported only at render time so the
pure geometry/window helpers remain unit-testable in Clinical QA.
"""

import argparse
import json
import math
from pathlib import Path

WINDOW_WIDTH = 80.0
WINDOW_LEVEL = 40.0

def window_hu_scalar(hu, center=WINDOW_LEVEL, width=WINDOW_WIDTH):
    if width <= 0:
        raise ValueError("window width must be >0")
    low = center - width / 2.0
    high = center + width / 2.0
    if hu <= low:
        return 0
    if hu >= high:
        return 255
    return int(round((hu - low) / (high - low) * 255.0))

def _cross(a, b):
    return (
        a[1]*b[2]-a[2]*b[1],
        a[2]*b[0]-a[0]*b[2],
        a[0]*b[1]-a[1]*b[0],
    )

def _dot(a, b):
    return sum(float(x)*float(y) for x, y in zip(a, b))

def slice_position(image_orientation_patient, image_position_patient):
    if len(image_orientation_patient) != 6 or len(image_position_patient) != 3:
        raise ValueError("IOP(6) and IPP(3) are required")
    row = tuple(float(x) for x in image_orientation_patient[:3])
    col = tuple(float(x) for x in image_orientation_patient[3:])
    normal = _cross(row, col)
    norm = math.sqrt(_dot(normal, normal))
    if norm < 0.9 or norm > 1.1:
        raise ValueError("invalid/non-orthonormal DICOM orientation")
    return _dot(image_position_patient, normal)

def _window_array(hu):
    import numpy as np
    low = WINDOW_LEVEL - WINDOW_WIDTH / 2.0
    high = WINDOW_LEVEL + WINDOW_WIDTH / 2.0
    return np.clip((hu - low) / (high - low) * 255.0, 0, 255).astype(np.uint8)

def render_exam(dicom_files, output_dir, case_id):
    import numpy as np
    import pydicom
    from PIL import Image

    records = []
    study_uids = set()
    series_uids = set()
    orientations = []

    for path in dicom_files:
        ds = pydicom.dcmread(str(path), force=False)
        if str(getattr(ds, "Modality", "")) != "CT":
            raise ValueError(f"{path}: Modality must be CT")
        if not hasattr(ds, "PixelData"):
            raise ValueError(f"{path}: PixelData missing")
        if str(getattr(ds, "BurnedInAnnotation", "NO")).upper() == "YES":
            raise ValueError(f"{path}: BurnedInAnnotation=YES")
        photo = str(getattr(ds, "PhotometricInterpretation", ""))
        if photo not in {"MONOCHROME1", "MONOCHROME2"}:
            raise ValueError(f"{path}: unsupported PhotometricInterpretation {photo}")

        study_uid = str(getattr(ds, "StudyInstanceUID", ""))
        series_uid = str(getattr(ds, "SeriesInstanceUID", ""))
        if not study_uid or not series_uid:
            raise ValueError(f"{path}: StudyInstanceUID/SeriesInstanceUID required")
        study_uids.add(study_uid)
        series_uids.add(series_uid)

        iop = [float(x) for x in getattr(ds, "ImageOrientationPatient", [])]
        ipp = [float(x) for x in getattr(ds, "ImagePositionPatient", [])]
        pos = slice_position(iop, ipp)
        orientations.append(tuple(round(x, 5) for x in iop))

        slope = float(getattr(ds, "RescaleSlope", 1.0))
        intercept = float(getattr(ds, "RescaleIntercept", 0.0))
        pixels = ds.pixel_array.astype(float)
        hu = pixels * slope + intercept
        image = _window_array(hu)
        if photo == "MONOCHROME1":
            image = 255 - image

        records.append((pos, path, image))

    if len(study_uids) != 1:
        raise ValueError("one rendered exam must contain exactly one StudyInstanceUID")
    if len(series_uids) != 1:
        raise ValueError("one rendered exam must contain exactly one SeriesInstanceUID")
    if len(set(orientations)) != 1:
        raise ValueError("mixed ImageOrientationPatient within series")

    records.sort(key=lambda x: x[0])
    if len(records) < 2:
        raise ValueError("exam requires >=2 slices")
    positions = [x[0] for x in records]
    if any(b <= a for a, b in zip(positions, positions[1:])):
        raise ValueError("slice positions must be unique and strictly ordered")

    out = Path(output_dir) / case_id
    out.mkdir(parents=True, exist_ok=True)
    slices = []
    for index, (pos, _, arr) in enumerate(records):
        name = f"slice-{index:04d}.png"
        Image.fromarray(arr, mode="L").save(out / name)
        slices.append({"index": index, "position": pos, "image_file": f"{case_id}/{name}"})

    metadata = {
        "schema_version": "1.0",
        "case_id": case_id,
        "render_protocol": "rsna-ich-brain-window-v1",
        "window_width_hu": WINDOW_WIDTH,
        "window_level_hu": WINDOW_LEVEL,
        "slice_order": "IOP_IPP_geometry",
        "slice_count": len(slices),
        "slices": slices,
    }
    (out / "render_manifest.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return metadata

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("dicom_dir", type=Path)
    p.add_argument("output_dir", type=Path)
    p.add_argument("case_id")
    args = p.parse_args()
    files = sorted(x for x in args.dicom_dir.rglob("*") if x.is_file())
    result = render_exam(files, args.output_dir, args.case_id)
    print(json.dumps({"case_id": result["case_id"], "slice_count": result["slice_count"]}))
