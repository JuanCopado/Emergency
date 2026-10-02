# PTB-XL GITHUB ACTIONS INTAKE — v1.36

## Purpose
Build the first real blinded ECG benchmark without committing PTB-XL data or labels to the repository.

## Workflow
`.github/workflows/ptbxl-blinded-intake.yml`

Inputs:
- `target_code` — default `AFIB`.
- `max_cases` — `0` for all fold-10 cases; positive-preserving deterministic pilot when >0.

Required repository secret:
- `PTBXL_BLINDING_SALT` — random value >=16 characters. Never commit it.

## Output separation
The workflow produces two independent artifacts:
1. `ptbxl-blinded-<target>-fold10` — rendered ECG PNGs + model-facing manifest, **no labels/source IDs**.
2. `ptbxl-sealed-reference-<target>-fold10` — reference labels/source identifiers. Do not open before predictions are frozen.

## Blinded evaluation sequence
1. Download/use only the blinded artifact.
2. Record one of `positive / negative / abstain / nondiagnostic` for every case.
3. Freeze predictions with timestamps.
4. Only then reveal the sealed reference.
5. Merge predictions/reference into the v1.1 manifest.
6. Run strict validation and metrics scripts.
7. Preserve coverage/abstention; never discard difficult cases post hoc.

## Clinical interpretation
This benchmark is exploratory. PTB-XL is a known public dataset and model pretraining exposure cannot be excluded. It therefore cannot establish independent external clinical validation or justify automatic green promotion.
