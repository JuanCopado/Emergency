# PTB-XL AFIB IMAGE BASELINE v1 — PRE-REVEAL FROZEN

Frozen before any NATURAL_500 v2 sealed-reference access.

## Purpose
Provide a reproducible **engineering baseline** using only the standardized rendered
lead-II rhythm strip. It is not a clinical AF detector and must not be represented as
ChatGPT clinical accuracy.

## Input
- PTB-XL NATURAL_500 v2 blinded artifact only.
- No PTB-XL source IDs, SCP labels, aggregate prevalence or sealed reference.

## QRS extraction
- Crop the standardized 10 s lead-II rhythm strip.
- Reconstruct the blue waveform from pixels.
- Detrend, 5--18 Hz bandpass, derivative-square integration.
- Detect QRS energy peaks with minimum 280 ms separation.

## Frozen classification rule
- **positive**: RR CV >= 0.18 AND normalized RMSSD >= 0.22 AND RR MAD ratio >= 0.08.
- **negative**: RR CV <= 0.08 AND normalized RMSSD <= 0.12 AND RR MAD ratio <= 0.05.
- **nondiagnostic**: QRS/trace extraction failure or <5 QRS.
- **abstain**: all intermediate patterns.

No threshold may be changed after the sealed reference is revealed.

## Interpretation boundary
This baseline measures whether a simple blinded image-derived rhythm-irregularity
heuristic can recover AFIB labels from this specific rendering pipeline. Ectopy,
flutter with variable conduction, noise and regularized AF may cause errors. It is
not an external clinical validation and does not justify green promotion.
