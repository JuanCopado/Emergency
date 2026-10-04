# Documentation and governance

## clinical-note-diagnostic-support

### Purpose
Structured clinician-facing note workspace for emergency/acute care. It is designed around the patterns present in the supplied clinical-history examples: concise demographics/context, past history, chronic medication, allergy status, history of present illness, examination, complementary tests, problem list, diagnostic synthesis and plan. Uploaded ECG, radiography, CT/MRI, laboratory reports, blood gases and other clinical files are routed to the relevant image/calculator module and their report is inserted into the appropriate section with provenance.

### Core workflow
1. Create a pseudonymous encounter.
2. Enter history using structured fields plus optional free text.
3. Add serial observations/timeline events.
4. Add MCDT results manually or from uploaded files.
5. For uploaded ECG/Rx/CT/PDF/laboratory material:
   - run privacy preflight;
   - route to the appropriate interpretation module;
   - store the original official report separately from any AI interpretation;
   - record provenance, timestamp and limitations;
   - never overwrite the official report.
6. Build problem representation and active problem list.
7. Call the relevant disease modules, central scores/formulas and medication-safety modules.
8. Produce clinician decision support:
   - likely diagnosis/diagnoses ranked qualitatively;
   - differential diagnosis;
   - must-not-miss alternatives;
   - supporting and opposing evidence;
   - suggested complementary tests;
   - treatment options;
   - disposition/reassessment suggestions;
   - explicit uncertainty and data gaps.
9. Require clinician review before export.
10. Export as DOCX and/or PDF in a privacy-appropriate mode.

### Clinical note sections
- Encounter/context
- Baseline functional/cognitive/social status
- Past medical history
- Chronic medication and medication-reconciliation discrepancies
- Allergy status
- History of present illness
- Timeline/evolution
- Examination
- Vital signs
- Complementary tests
  - Laboratory
  - Blood gas
  - ECG
  - Imaging (Rx/CT/MRI/US)
  - Microbiology
  - Other
- Active problems
- Clinical synthesis/problem representation
- Likely diagnoses
- Differential diagnosis
- Must-not-miss diagnoses
- Suggested additional tests
- Treatment suggestions
- Disposition/reassessment/follow-up
- Contradictions/data to clarify
- Limitations
- Clinician validation
- Privacy/export status

### Diagnostic-support rules
- Do not invent missing findings.
- Do not present an unsupported numerical probability as calibrated risk.
- Use qualitative confidence: high / moderate / low.
- Separate confirmed diagnoses from suspected diagnoses.
- Every diagnostic candidate should expose evidence-for, evidence-against and missing discriminating data when relevant.
- Route syndrome-specific recommendations through the existing module registry rather than duplicating management logic.
- Surface red flags and alternative diagnoses before treatment suggestions.
- If instability/sepsis/airway/breathing/circulation/neuro red flags exist, prioritize emergency stabilization over note completion.
- Treatment output must preserve allergy, renal/hepatic, pregnancy, interaction and medication-safety gates.

### Attachment routing
- ECG -> `ecg-image` (+ arrhythmia/ACS modules as indicated)
- Chest radiograph -> `chest-xray`
- CT/MRI screenshot/report -> `ct-mri-screenshot`
- POCUS/ultrasound -> `pocus-image`
- Blood-gas image -> `blood-gas-image`
- Skin/wound -> `skin-wound-image`
- Ophthalmology -> `ophthalmology-image`
- Musculoskeletal X-ray -> `musculoskeletal-xray`
- Other image -> `other-clinical-image`
- Structured laboratory report -> central calculators + syndrome modules as indicated

### Provenance
Each imported datum/report must be labelled as one of:
- clinician_entry
- official_report
- laboratory_system
- device_measurement
- ai_image_interpretation
- ai_document_extraction
- patient_or_family_report
- external_record

AI output must never silently replace a clinician or official-source value.

### Privacy by design
The note workspace is designed for data minimization and pseudonymization. Pseudonymized health data remain personal data under GDPR; do not describe reversible pseudonyms as anonymous. External teaching/research/export mode must remove direct identifiers and block export when direct identifiers or unsafe source attachments remain.

The structured note does not require:
- patient name;
- full address;
- phone/email;
- national health/tax/document numbers;
- exact date of birth.

Use an encounter UUID plus clinically necessary age/sex/context. Exact dates should be retained only when clinically necessary; otherwise prefer relative timing.

### Uploaded-file privacy
- Do not embed original DICOM/PDF/image files into exported notes by default.
- Store/report extracted clinical findings and provenance.
- Before using an image for AI interpretation, remove accessible metadata where possible and require confirmation that burned-in identifiers are absent or masked.
- DICOM private tags and burned-in patient text require dedicated de-identification review; metadata removal alone is insufficient.
- Generated DOCX/PDF metadata must not contain patient identifiers.

### Export
The deterministic exporter supports:
- DOCX
- PDF
- JSON structured note

Exports require privacy validation. The exported report contains the clinical synthesis and reports, not the original attachments by default.

### Status
Yellow. Technical/documentation module; requires final human clinical, legal/privacy and information-governance review before green.

## final-human-review-gate

### Purpose
Project-wide end-stage review gate for all modules that remain yellow. This module formalizes the user's decision to defer yellow-to-green promotion until the end of the project rather than repeatedly blocking feature development.

### Final review workflow
For every yellow module:
1. Identify required specialty reviewer(s).
2. Clinical review.
3. Pharmacy review where medication/dose/concentration is involved.
4. Nursing/operational review where bedside workflow is involved.
5. Legal/privacy/information-governance review where personal health data are handled.
6. Portugal/local implementation review only where the module depends on local product/protocol/system details.
7. Resolve all critical findings.
8. Re-run Clinical QA.
9. Record reviewer, date, scope and outcome.
10. Promote only the individually reviewed module to green.

### Promotion outcomes
- PASS -> eligible for green after QA.
- PASS_WITH_NONCRITICAL_NOTE -> eligible only if note is documented and does not alter safety.
- CHANGE_REQUIRED -> remain yellow until corrected/retested.
- BLOCKED_PENDING_SOURCE -> remain yellow.
- NOT_REVIEWED -> remain yellow.

### Important
Automated QA, synthetic cases, AI-assisted clinical/pharmacy audit and source review are preparation for human review, not substitutes for it.
