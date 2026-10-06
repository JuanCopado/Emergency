# CLINICAL NOTE — EXECUTABLE DIAGNOSTIC SUPPORT ENGINE

Date: 2026-10-04
Branch: `v1.39-clinical-note-diagnostic-support`

## Components
- Rule registry: `qa/clinical-note-diagnostic-rules.json`
- Engine: `scripts/clinical_note_diagnostic_engine.py`
- Synthetic cases: `qa/clinical-note-diagnostic-synthetic-cases.json`
- Regression runner: `scripts/run_clinical_note_diagnostic_cases.py`

## Current executable syndrome coverage
The registry now contains **92 transparent syndrome rules** spanning:
- cardiovascular/resuscitation/shock;
- respiratory;
- neurology/neuroinfection;
- infectious disease/sepsis;
- trauma/burns/environmental;
- gastrointestinal/hepatology/surgical abdomen;
- renal/electrolyte/metabolic/endocrine;
- toxicology;
- obstetrics/gynaecology;
- haematology/oncology;
- ophthalmology/ENT/urology/orthopaedics;
- psychiatry;
- geriatrics;
- pediatric emergency families with age-specific routing.

Age applicability gates prevent adult-only rules from becoming the primary route in pediatric cases.

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
The complete regression bank now contains **60 synthetic diagnostic scenarios** across:
- core emergency syndromes;
- respiratory/infectious/GI/metabolic expansion;
- trauma/obstetric/pediatric/specialty expansion;
- final coverage-closure cases;
- dedicated pediatric age-routing cases.

All **60/60 PASS** in the final validated state.

## Current validation
Clinical QA #587:
- SUCCESS
- **364/364 tests PASS**
- **131/131 modules registered**
- **29 green / 102 yellow / 0 red**
- Coverage audit: **115 directly covered/routed + 16 explicitly non-diagnostic support/infrastructure; 0 unexpected clinical gaps**

## Status
Yellow. The engine is executable and broadly covers the registered acute-care clinical families. Remaining yellow status is deliberate pending final human clinical/privacy/information-governance review; automated completeness is not clinical release.
