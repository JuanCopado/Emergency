# CLINICAL NOTE — DIAGNOSTIC REASONING CONTRACT

## Input
Only privacy-cleared structured note content and source-labelled reports.

## Reasoning sequence
1. Identify immediate instability/red flags.
2. Build a one-sentence problem representation.
3. Generate active problem list.
4. Route each problem to existing syndrome modules and central scores/formulas.
5. Generate likely diagnoses with qualitative confidence.
6. Generate differential diagnoses.
7. Generate must-not-miss diagnoses even when less likely.
8. Identify contradictions and missing discriminating data.
9. Suggest tests only when they can discriminate diagnoses, detect dangerous complications or change management.
10. Suggest treatment in order:
   - stabilization;
   - syndrome-specific treatment;
   - medication-safety preflight;
   - supportive care;
   - disposition/follow-up.
11. State uncertainty and limitations.
12. Require clinician acceptance/edit before the assessment becomes part of the export.

## Required diagnostic candidate structure
- diagnosis
- confidence: high / moderate / low
- evidence_for[]
- evidence_against[]
- missing_discriminating_data[]
- source_modules[]

## Rules
- Never fabricate findings from an uploaded file.
- Never convert “not mentioned” into “negative”.
- Do not silently merge official radiology/ECG reports with AI interpretation.
- Do not use a numerical probability unless a validated score/model in the central registry supports it.
- Reassess the differential whenever a new test is added.
- Highlight when a new result materially changes the leading diagnosis or disposition.
