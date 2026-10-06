# CLINICAL NOTE DIAGNOSTIC ENGINE — FINAL COVERAGE AUDIT

Date: 2026-10-06
Branch: `v1.39-clinical-note-diagnostic-support`

## Result
**PASS**

- Registered project modules: **131**
- Executable diagnostic syndrome rules: **92**
- Registered modules directly covered or routed from diagnostic rules: **115**
- Explicitly classified non-diagnostic/support modules: **16**
- Unexpected uncovered clinical modules: **0**
- Stale/invalid non-diagnostic classifications: **0**

## Diagnostic regression coverage
The executable reasoning engine is exercised by **60 synthetic diagnostic scenarios** across:
- cardiovascular;
- respiratory;
- resuscitation/shock;
- neurologic;
- infectious;
- GI/surgical;
- renal/metabolic;
- endocrine;
- hepatology;
- toxicology;
- trauma;
- obstetric/gynaecologic;
- paediatric;
- haematology/oncology;
- urologic;
- ophthalmology/ENT;
- orthopaedic;
- dermatologic;
- psychiatric;
- environmental;
- geriatric.

## Non-diagnostic/support modules intentionally outside direct diagnostic rules

### Image interpretation
- clinical-image-interpretation
- musculoskeletal-xray
- pocus-image
- other-clinical-image

### Procedures/treatment delivery
- pediatric-airway-rsi
- sedoanalgesia
- icu-sedation-analgesia-infusions
- high-flow-nasal-oxygen
- vasoactive-inotrope-infusions

### Broad routers/support
- pediatric-emergencies
- endocrine-metabolic
- pediatric-outpatient-medications
- medication-selection-safety
- ecg-pocus-integration

### Governance/note infrastructure
- clinical-note-diagnostic-support
- final-human-review-gate

These modules are called by diagnosis-specific rules or provide cross-cutting capabilities and therefore do not require their own syndrome hypothesis.

## Coverage gate
Files:
- `qa/clinical-note-diagnostic-coverage-policy.json`
- `scripts/audit_clinical_note_diagnostic_coverage.py`

Clinical QA now fails if:
1. a new registered module is not covered/routed by the diagnostic engine; and
2. it has not been explicitly classified as non-diagnostic support/infrastructure.

This prevents silent diagnostic coverage gaps as the repository grows.

## Important safety architecture
- Short diagnostic acronyms use token/word-boundary matching to avoid false positives inside ordinary words.
- Adult-only/pediatric-only rules can enforce age applicability.
- Paediatric cardiac arrest, arrhythmia, CNS infection, trauma, burns, toxicology, adrenal crisis, hypertensive emergency and haematology-oncology have explicit paediatric routing.
- Generated assessments reset clinician sign-off and cannot be exported as clinician-validated until reviewed.
- Confidence remains qualitative (high/moderate/low); no unsupported calibrated probability is produced.

## Validation
Clinical QA #586:
- **SUCCESS**
- **363/363 tests PASS**
- `automated_status: PASS`
- **131/131 modules registered**
- **29 green / 102 yellow / 0 red**

This is deterministic technical/clinical-rule regression validation. It is not prospective diagnostic accuracy validation or final human clinical sign-off.
