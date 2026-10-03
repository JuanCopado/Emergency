# RSNA ICH DICOM RENDER PROTOCOL v1.0 — FROZEN

Fecha de congelación: 03/10/2026.

## Target
`any_acute_ich` on a complete non-contrast head CT examination.

## Primary render
A single standardized **brain window** is used for every slice:
- Window width: **80 HU**
- Window level: **40 HU**
- Linear clip/min-max to 8-bit grayscale.

This setting is supported by RSNA work using the RSNA 2019 ICH dataset and external
head-CT test sets, where images were rendered with standard brain WW=80/WL=40.
No extra "subdural", bone or diagnosis-dependent window is added post hoc.

Sources:
- RSNA Radiology: Artificial Intelligence, Examination-Level Supervision for Deep Learning–based Intracranial Hemorrhage Detection on Head CT Scans: https://pubs.rsna.org/doi/10.1148/ryai.230159
- RSNA ATLAS data card for the same task/dataset: https://atlas.rsna.org/cards/c41a4d08-2a3c-4a5f-9019-626f2c7b5a2d

## HU conversion
For each DICOM:
`HU = stored_pixel * RescaleSlope + RescaleIntercept`.

MONOCHROME1 is inverted after windowing; MONOCHROME2 is retained.

## Slice order
Never sort by filename or label.
- Require `ImageOrientationPatient` (6 values).
- Require `ImagePositionPatient` (3 values).
- Compute slice normal as row-direction × column-direction.
- Sort by dot(IPP, slice-normal).
- Mixed orientation, duplicate positions or missing geometry -> **fail closed**.

## Study/series integrity
Each rendered case must contain:
- exactly one `StudyInstanceUID`;
- exactly one `SeriesInstanceUID`;
- CT modality;
- >=2 slices;
- supported MONOCHROME1/2 pixel data.

If an exam contains multiple CT series, series selection must occur upstream under a
separate pre-specified, diagnosis-independent rule. The renderer will not guess.

## Leakage
- Original DICOM and identifying tags remain outside the model-facing package.
- Output filenames use only hashed case ID + sequential slice number.
- `BurnedInAnnotation=YES` is rejected.
- No label, study UID, series UID, source filename or reference truth is written into
  rendered PNG filenames or model-facing metadata.

## Limits
This render protocol standardizes pixels; it does not prove diagnostic accuracy.
RSNA 2019 is a public retrospective benchmark with possible model-pretraining exposure.
