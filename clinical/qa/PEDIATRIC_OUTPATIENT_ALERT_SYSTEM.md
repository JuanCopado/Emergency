# PEDIATRIC OUTPATIENT — MEDICATION SAFETY ALERT SYSTEM

Date: 2026-10-04
Branch: `v1.38-pediatric-outpatient-medications`
Module: `pediatric-outpatient-medications`

## Components
- Rules: `qa/pediatric-outpatient-alert-rules.json`
- Engine: `scripts/pediatric_outpatient_alert_engine.py`
- Calculator integration: `scripts/pediatric_outpatient_calculator.py`

## Severity model
- **STOP** — contraindication/high-risk conflict. Standard prescription is blocked.
- **ALERT** — clinically significant issue requiring active prescriber review.
- **CAUTION** — use with caution; review monitoring, timing or dose.
- **INFO** — non-blocking administration/follow-up information.

## Alert families
1. Exact drug allergy.
2. Drug-class allergy.
3. Beta-lactam cross-allergy, including severe/immediate penicillin-cephalosporin risk and amoxicillin/ampicillin shared-side-chain caution with cefalexin.
4. Duplicate active ingredient.
5. Duplicate therapeutic class.
6. Curated clinically important drug interactions.
7. QT/electrolyte risk.
8. Renal/hepatic standard-regimen incompatibility.
9. Age outside regimen range.
10. Required dosing weight missing.
11. Required clinical criterion absent.
12. Explicit clinical exclusion present.
13. Required clinical value missing/outside range.
14. Product concentration invalid or inconsistent with verified strengths.
15. Allergy status not documented.
16. Medication reconciliation not documented.
17. Global red flags invalidating outpatient treatment:
   - clinical instability;
   - admission requirement;
   - inability to tolerate oral treatment;
   - suspected sepsis;
   - significant hypoxaemia;
   - active anaphylaxis;
   - surgical red flags.
18. Pregnancy-specific review where relevant.

## Curated interaction examples
- Clarithromycin: contraindicated CYP3A/QT combinations; anticoagulant alerts.
- Ondansetron: apomorphine STOP; QT and serotonergic alerts.
- Co-trimoxazole: methotrexate and hyperkalaemia-risk medicines.
- Ibuprofen: anticoagulants/antiplatelets, ACEi/ARB/diuretics, corticosteroids/SSRIs.
- Rizatriptan: MAOI/ergot/other triptan STOP; propranolol reduced-dose alert.
- Fexofenadine: aluminium/magnesium antacid timing caution.

## Input contract
Patient safety context can include:
- `allergies`: strings or structured objects with substance/class/phenotype/severity;
- `active_medications`: strings or structured objects with medication classes;
- renal/hepatic impairment flags;
- eGFR;
- QT/electrolyte flags;
- pregnancy;
- clinical red flags;
- exact product concentration.

Missing allergy status or medication reconciliation produces an **ALERT** rather than being silently treated as negative.

## Output
The preflight returns:
- all alerts;
- count by severity;
- highest severity;
- `blocked` boolean;
- `prescription_status`:
  - BLOCKED
  - REVIEW_REQUIRED
  - OK_WITH_CAUTIONS
  - OK

The dose calculator embeds the safety result. STOP alerts raise a structured `MedicationSafetyStop` and prevent routine dose calculation.

## Safety philosophy
The engine is deliberately fail-closed for contraindications and uncertain product concentration. It is not a complete commercial drug-interaction database and does not replace clinician/pharmacist judgment. New interaction rules require source verification and boundary tests.

## Sources
- RCH pediatric beta-lactam allergy guidance.
- Current SmPC sources for clarithromycin, ondansetron, co-trimoxazole, ibuprofen and rizatriptan.
- Existing v1.38 regimen-specific source registry.

## Status
Technically implemented and Clinical QA validated.
Module remains **yellow** pending human pediatric/pharmacy sign-off.
