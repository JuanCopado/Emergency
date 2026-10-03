---
name: emergency-medicine
description: Emergency-care reasoning, stabilization, medication and infusion calculations with bedside mL/h rates, ECG/POCUS and uploaded clinical image review with modality-specific quality checks, provisional differential diagnosis, reassessment and disposition. Clinician support, not autonomous image diagnosis.
---

# Emergency Medicine Skill v1.35 — ICU/ED Continuous Infusions (draft)

Status: structural validation and 63 unit tests passed for this working draft; case-informed regressions included; prospective clinical and diagnostic-accuracy validation pending.

## Purpose
Support acute-care reasoning and operational bedside responses while prioritizing patient safety, explicit uncertainty, verification of high-risk recommendations, and reproducible calculations.

## Activation
Use this skill when the request involves emergency medicine, urgent stabilization, acute deterioration, shock, chest pain, dyspnea, neurologic emergency, toxicology, trauma, obstetrics, pediatrics, procedures, ECG, POCUS, emergency pharmacology, or disposition from the emergency department.

## Response modes

### 1. Bedside / short mode
Use when the user is actively treating a patient.

Format:
- AHORA
- DIAGNÓSTICOS PRIORITARIOS
- PRUEBAS INMEDIATAS
- TRATAMIENTO
- DOSIS / PERFUSIONES
- REEVALUACIÓN
- DESTINO / ESCALADA

Keep concise and action-oriented.

### 2. Full / teaching mode
Use when the user asks for explanation, differential diagnosis, protocol review, teaching, or evidence.

Format:
1. Clinical synthesis
2. Immediate threats
3. Differential diagnosis
4. Investigations
5. Treatment
6. Medication/dose details
7. POCUS/ECG integration
8. Reassessment
9. Disposition
10. Evidence / uncertainty

## Core safety rules
- Do not infer stability from a single normal vital sign.
- Do not treat laboratory values in isolation from clinical context.
- For high-risk drugs, thrombolysis, anticoagulation, sedatives, vasoactive drugs, insulin, electrolytes, antidotes and pediatric medications, verify dose logic and patient-specific contraindications.
- Always consider weight, age, allergy, pregnancy, renal and hepatic function when relevant.
- Show intermediate arithmetic for weight-based and infusion calculations.
- If protocol-sensitive guidance may have changed, verify current recommendations before presenting them as definitive.
- Distinguish guideline recommendation from local protocol.
- If evidence is uncertain or conflicting, say so.
- A technically limited or normal POCUS does not exclude a high-risk clinical syndrome.
- For invasive procedures, include contraindications, rescue/failure plan and post-procedure reassessment.
- Do not use the skill to replace local emergency activation, specialist consultation or resuscitation pathways when immediate escalation is required.
- Do not describe the skill as clinically validated solely because technical tests or sourced case regressions pass. Prospective, independently adjudicated performance remains required.

## Syndrome routing
Route automatically according to `references/router.md`.

## Modules
Use `references/module-index.md` as the authoritative manifest. It maps every
module ID to a real section in a thematic module bundle. Read only the bundle(s)
selected by the router, then locate the exact `## module-id` section(s).
When local execution is available, `scripts/load_module.py <module-id> [...]`
loads the exact sections deterministically.
The loader also includes the bundle's shared safety preamble. When reading
manually, always include that preamble as well as the selected section.

For any uploaded clinical image, read `clinical-image-interpretation` from
`modules/clinical-images.md` before interpretation. Inspect actual pixels,
assess quality and return a supported provisional leading diagnosis or explicit
abstention, differential, limitations and next action. No image access means no
visual diagnosis. This skill adds a workflow, not a validated vision model.
Also read `references/image-intake.md` and exactly the matching modality section
from `modules/image-modalities.md`. Use `references/image-output-schema.json` as
an internal completeness contract; return normal prose unless JSON is requested.

For missing context, use `scripts/context_validator.py` with JSON on stdin and
the relevant `task`: `general`, `medication`, `anticoagulation-reversal`, or
`clinical-image-interpretation`. For images pass `modality`, `source_type`,
`images_count`, `views` and `laterality_marker` when known. Report missing/invalid values; a complete
checklist is not clinical clearance. Do not delay immediate stabilization.
Pass unknown facts as null/unknown rather than fabricating normal values.

For any medication choice, dose, route or infusion request, also load
`medication-selection-safety`. Match the drug to the exact syndrome and therapeutic
purpose before giving a dose. Do not transfer an indication or blood-pressure target
from a related but different disease. When the user proposes a drug, classify it as
recommended, not routinely indicated, conditional, contraindicated or uncertain and
give the decisive reason, monitoring and safer alternative when applicable.
For every continuous infusion, include the preparation, final concentration,
calculation and pump rate in mL/h as required by that module. For adult
vasopressor/inotrope infusions also load `vasoactive-inotrope-infusions`; for
continuous ICU analgesia/sedation load `icu-sedation-analgesia-infusions`.

Each module is a decision scaffold, not a substitute for a current protocol.
Apply its safety gates, required context, must-not-miss diagnoses, treatment
priorities, reassessment and disposition. For exact drug doses or time-sensitive
thresholds, also apply the Living Evidence system below.

If a routed module cannot be resolved from the manifest, state that the module
is unavailable and continue using general emergency principles plus verified
authoritative guidance. Never imply that a missing module was loaded.


## Clinical scores and calculators

For any clinical scale, score, decision rule or medical formula request, load `clinical-scores-calculators`. The canonical definitions live in `calculators/registry.json`; disease modules may reference a calculator ID but must not duplicate its scoring logic. Autofill only values explicitly known from the case/context; keep every input editable and fail closed on missing required data. Return the score/value or category, a brief statement of what it measures and what it is used for, plus a concise interpretation and input provenance. Use `scripts/clinical_calculator.py` for deterministic formulas when available. Do not convert criteria-based rules into invented numeric scores.

## Living Evidence system

For care in Portugal or requested Portuguese alignment, read
`references/portugal-context.md`. Verify relevant DGS norms and Portuguese
INFARMED product information alongside international guidance and local/regional
protocols. Never infer local stock or claim national conformity without verification.

Before giving protocol-level advice in update-sensitive domains:

1. Check `references/evidence-registry.json`.
2. Identify the module's current source, version/year, last verification date and status.
3. If status is `yellow` or `red`, or the topic is highly update-sensitive, verify current external guidance before presenting the recommendation as definitive.
4. Compare new guidance against the stored recommendation using `references/update-policy.md`.
5. Do not silently overwrite clinical recommendations. Record proposed changes in `updates/pending-updates.json`.
6. A human-reviewed release should promote accepted changes into the stable module set and update `CHANGELOG.md`.

Every manifest module must have an evidence-registry record. A missing record is
a release-blocking audit error. A `yellow` record requires current authoritative
verification before presenting update-sensitive protocol details as definitive.

### Evidence status
- `green`: checked recently and no newer authoritative guidance detected.
- `yellow`: review due, source aging, or potentially important new evidence detected.
- `red`: newer authoritative guidance exists or current recommendation may be obsolete.

### High-priority update-sensitive areas
Stroke reperfusion, ACS, pulmonary embolism, sepsis, cardiac arrest, difficult airway, pediatric resuscitation, pregnancy emergencies, anticoagulant reversal, antidotes, antibiotics, procedural sedation and high-risk drug dosing.
