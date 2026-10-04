# CLINICAL NOTE — EXECUTABLE DIAGNOSTIC SUPPORT ENGINE

Date: 2026-10-04
Branch: `v1.39-clinical-note-diagnostic-support`

## Components
- Rule registry: `qa/clinical-note-diagnostic-rules.json`
- Engine: `scripts/clinical_note_diagnostic_engine.py`
- Synthetic cases: `qa/clinical-note-diagnostic-synthetic-cases.json`
- Regression runner: `scripts/run_clinical_note_diagnostic_cases.py`

## Current executable syndrome coverage
1. Acute coronary syndrome.
2. Pulmonary embolism.
3. Tension pneumothorax.
4. Acute ischemic stroke.
5. Spontaneous intracerebral hemorrhage.
6. SAH / dangerous secondary headache.
7. Sepsis / septic shock.
8. Acute aortic syndrome.
9. Complicated/ruptured abdominal aortic aneurysm.
10. DKA / hyperglycemic crisis.
11. Acute heart failure / cardiogenic pulmonary edema.

## Operation
The engine consumes only the privacy-cleared structured clinical note.

It uses:
- history text;
- examination text;
- latest vital signs;
- official reports;
- labelled AI interpretations;
- laboratory/blood-gas report text.

Every rule is inspectable. Each triggered diagnosis contains:
- qualitative confidence;
- evidence detected;
- missing discriminating information;
- source module(s).

## Output
- problem representation;
- active problem list;
- likely diagnoses;
- differential diagnoses;
- must-not-miss diagnoses;
- complementary tests;
- treatment/module routing;
- disposition;
- reassessment;
- contradictions;
- limitations.

## Safety
- No calibrated numeric diagnostic probability is generated.
- “Not mentioned” is never converted to “negative”.
- Objective instability inserts ABCDE/stabilization before diagnostic completion.
- Treatment suggestions call existing disease modules instead of duplicating dose/protocol logic.
- Applying a generated assessment resets clinician validation to false.
- The note cannot be exported again until clinician review.

## Synthetic regression set
The synthetic regression bank now contains **24 cases**, including ACS, tension pneumothorax, stroke, sepsis, DKA, acute aortic syndrome, severe asthma, COPD exacerbation, anaphylaxis, CNS infection, status epilepticus, upper GI bleeding, pancreatitis, hyperkalaemia, adrenal crisis, hypertensive emergency, arrhythmia, toxicology, mesenteric ischaemia, AKI, rhabdomyolysis, thyroid storm, acute liver failure and cauda equina.

These validate deterministic behavior only and are not diagnostic-accuracy validation.

## Current validation
Clinical QA #553:
- SUCCESS
- 360/360 tests PASS
- 131/131 modules registered
- 29 green / 102 yellow / 0 red

## Status
Yellow. The engine is executable and tested, but syndrome coverage is intentionally incomplete and requires continued expansion plus final human clinical review.
