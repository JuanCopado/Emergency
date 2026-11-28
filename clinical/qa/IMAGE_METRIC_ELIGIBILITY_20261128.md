# Image-evaluation tooling: enforce the eligibility decision

Base: `ab96bc09b650d332f1bbf5c400a92a32d6610a44`. Isolated technical correction, not a clinical validation or release. `clinical-image-interpretation` and `clinical-note-diagnostic-support` remain YELLOW. CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE.

## Confirmed defect and correction

`calculate_blinded_image_metrics.calculate()` previously checked only validation errors. The validator can correctly return `metrics_eligible=false` without errors for a workflow or source-known teaching dataset when `metrics_requested` is absent/false. The calculator then returned performance metrics anyway. A two-case synthetic source-known fixture produced exit0 and accuracy1.0 despite an ineligible gate. No images, patients, actual diagnoses or real adjudication were used.

The calculator now rejects an explicitly ineligible gate before calculating: `metrics=null`, a nonempty error and CLI exit1. The validator, eligibility rules, metric formulas, references, clinical engines, thresholds, doses and product activation remain unchanged. This does not authenticate a study's asserted governance or turn synthetic assertions into independent clinical references.

## Observed validation

- New regression: one test/four subcases (workflow/source-known × absent/false request flag). Four failures before; four subcases pass after.
- Four existing affected tests pass: valid blinded structure; source-known/annotated rejection; frozen-prediction/leakage/grouping; abstention/nondiagnostic suppression.
- Real CLI on the preserved source-known fixture: before exit0/metrics present; after exit1/metrics null.
- Separate two-case synthetic abstention fixture: exit0, coverage0.5, sensitivity/specificity null. This checks denominator behavior only, not diagnostic performance.
- No broad suite, shadow-study replay, image model/provider, prospective evaluation or clinical-state promotion. Existing note47+8+5 synthetic harnesses were already executed in the AB96 coverage workflow and are reused, not counted as new tests.

Detailed original inputs, outputs and before/after logs are outside Git in `DESBLOQUEO_EFECTIVO_20261128/YELLOW/EVIDENCIAS`. The independent cohort, reference adjudication and predeclared clinical acceptance criteria remain absent. R5-1 human factors and R5-2 reassuring-language controls do not substitute them; no new medical decision is mature from this tooling fix.
