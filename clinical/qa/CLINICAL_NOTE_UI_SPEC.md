# CLINICAL NOTE DIAGNOSTIC SUPPORT — UI / WORKFLOW SPEC

## Goal
Make acute-care documentation fast enough for bedside use while preserving structured data for diagnostic support and export.

## Recommended screen

### Persistent top bar
- Pseudonymous encounter ID (auto-generated)
- Age
- Sex
- Origin / transferred from
- Functional baseline
- Privacy status badge
- Unsaved / clinician-review status

### Main navigation
1. **História**
2. **Exame**
3. **MCDT**
4. **Problemas**
5. **Apoio diagnóstico**
6. **Plano**
7. **Exportar**

## 1. História
Accordion blocks:
- Chief complaint
- HDA / present illness
- Past medical history
- Surgical history
- Baseline functional/cognitive status
- Chronic medication
- Medication discrepancies
- Allergies
- Social/living context
- Source reliability

Each block supports:
- structured quick fields;
- optional free text;
- provenance tag;
- “not known / not available” rather than forcing a guessed value.

## 2. Exame
- Vital-sign cards with timestamp and oxygen/device context
- General
- Neurologic
- Respiratory
- Cardiovascular
- Abdomen
- Skin/wounds
- Extremities
- Other

Allow repeated examinations over time; do not overwrite the first observation.

## 3. MCDT
Large buttons:
- **+ Analítica**
- **+ Gasometria**
- **+ ECG**
- **+ Rx**
- **+ TC/RM**
- **+ Ecografia/POCUS**
- **+ Microbiologia**
- **+ Outro**

For every upload:
1. privacy preflight;
2. classify modality;
3. route to the relevant project module;
4. show extracted/interpreted result in a review card;
5. clinician accepts/edits/rejects;
6. accepted content enters the note with provenance.

Display official report and AI interpretation as separate fields.

## 4. Problems
Editable numbered problem list.
Allow problem status:
- active
- improving
- resolved
- pending clarification

Automatic suggestions may be proposed from the history/MCDT but require clinician acceptance.

## 5. Diagnostic support
Four columns/cards:
- **Most likely**
- **Differential**
- **Must not miss**
- **Missing data / contradictions**

For each diagnosis:
- qualitative confidence: high / moderate / low;
- evidence for;
- evidence against;
- missing discriminating data;
- source modules used.

No uncalibrated numerical probability.

## 6. Plan
Separate:
- immediate stabilization;
- additional tests;
- disease-specific treatment;
- medication safety alerts;
- consultation/referral;
- disposition;
- reassessment;
- follow-up.

Medication suggestions must call the central medication safety/alert logic before display as actionable.

## 7. Export
Buttons:
- **Word (.docx)**
- **PDF**
- **JSON structured note**

Before export show a checklist:
- direct identifiers removed;
- free text screened;
- source metadata checked if required;
- burned-in identifiers checked for image-derived content;
- clinician reviewed;
- unresolved contradictions acknowledged.

STOP findings disable export.

## Timeline
A vertical timeline should remain available in all tabs:
- arrival
- serial vitals
- medication administration
- new lab values
- imaging
- consultations
- diagnostic changes
- disposition decision

## Privacy UX
Do not ask for name, full DOB, address, phone, email, SNS/NIF/ID as ordinary fields.
Use pseudonymous encounter ID.
If free text contains patterns such as “Nome:”, SNS, NIF, phone/address labels, display a red STOP banner and require removal before export.

## Valuable safety additions
- contradiction detector;
- medication reconciliation discrepancy banner;
- provenance badges;
- “official report” vs “AI interpretation” visual distinction;
- missing critical-data checklist;
- red-flag banner;
- explicit clinician sign-off;
- append-only audit history for changes;
- do not embed source images/PDF/DICOM into exported note by default.
