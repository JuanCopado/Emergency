# BLINDED PREDICTION FREEZE AND REVEAL — v1.36

## Required order
1. Work only from the blinded artifact.
2. Produce exactly one prediction for every case.
3. Allowed classes: `positive`, `negative`, `abstain`, `nondiagnostic`.
4. Record `prediction_frozen_at` for every case.
5. Do not open the sealed reference before every prediction is frozen.
6. Record one dataset-level reference reveal timestamp.
7. Run `scripts/finalize_blinded_image_dataset.py`.
8. Run `scripts/validate_blinded_image_dataset.py`.
9. Only if the strict gate passes, run `scripts/calculate_blinded_image_metrics.py`.

## Fail-closed rules
The finalizer rejects:
- missing, duplicated or extra prediction IDs;
- missing, duplicated or extra reference IDs;
- invalid prediction classes;
- missing patient/study hashes;
- mismatched study hashes between blinded and sealed files;
- prediction timestamps at or after reference reveal;
- incomplete reference labels.

The final manifest contains only target truth, not original PTB-XL patient/ECG identifiers.

## Interpretation
A technically valid finalized manifest proves only that the blind/reveal sequence is internally coherent. It does not establish clinical validity, external generalizability or independence from model pretraining exposure.
