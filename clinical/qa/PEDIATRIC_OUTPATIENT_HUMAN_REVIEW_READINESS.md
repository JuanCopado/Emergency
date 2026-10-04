# PEDIATRIC OUTPATIENT — HUMAN REVIEW READINESS

Date: 2026-10-04
Branch: `v1.38-pediatric-outpatient-medications`
Module: `pediatric-outpatient-medications`
Current status: **yellow**

## Purpose
Prepare the 89-regimen outpatient registry for independent pediatric and pharmacy review.
Automated QA cannot promote this module to green.

## Required reviewers
- Pediatric clinician.
- Pharmacist with pediatric medication experience.

## Review dimensions for every regimen
1. Diagnosis/indication is exact and not broader than the cited source.
2. Minimum/maximum age is correct.
3. Dosing-weight basis is correct: actual / ideal / adjusted / age-band / weight-band / device / topical.
4. Dose and dose units are correct.
5. Per-dose maximum is correct where applicable.
6. Daily/source adult maximum is correct where applicable.
7. Frequency is correct.
8. Duration is correct and source-specific.
9. Product concentration is correct before automatic mL arithmetic is allowed.
10. Administration instructions are correct.
11. Food/fasting/milk instructions are correct where relevant.
12. Contraindications are represented.
13. Important interactions/cautions are represented.
14. Renal adjustment/gate is correct where applicable.
15. Hepatic adjustment/gate is correct where applicable.
16. Outpatient suitability/red flags are not overridden by arithmetic.
17. Source/version is appropriate and current.
18. Portugal product-strength reconciliation is sufficient for automatic volume use.
19. Azores real-time stock is explicitly **not** a review gate.

## Mandatory high-risk review sample
The reviewer must explicitly inspect at minimum:
- beta-lactam immediate vs non-immediate allergy pathways;
- renal impairment with amoxicillin/co-amoxiclav/clarithromycin/oseltamivir/cetirizine;
- nitrofurantoin lower UTI vs pyelonephritis;
- ibuprofen with dehydration;
- obesity/adult-dose caps;
- ideal-body-weight paracetamol;
- variable-day azithromycin schedule;
- AIR/MART age/device boundaries;
- ORS vs shock/IV-fluid indication;
- unverified product concentration;
- rizatriptan 40-kg unresolved boundary.

## Automated evidence available
- Clinical QA run #493: SUCCESS.
- 89 diagnosis-specific regimens.
- 18 synthetic high-risk regression cases stored in:
  `qa/pediatric-outpatient-regression-cases.json`.
- Regression runner:
  `scripts/run_pediatric_outpatient_regressions.py`.
- Portugal product reconciliation:
  `qa/PEDIATRIC_OUTPATIENT_PORTUGAL_RECONCILIATION.md`.
- Gap/exclusion audit:
  `qa/PEDIATRIC_OUTPATIENT_GAP_AUDIT.md`.

## Promotion rule
Promotion from yellow to green requires:
- pediatric review complete;
- pharmacy review complete;
- all critical findings corrected;
- Clinical QA passing after corrections;
- no unresolved red/high-risk medication error;
- product concentration rules remain fail-closed.

## Review outcome fields
For each regimen use one of:
- PASS
- PASS_WITH_NONCRITICAL_NOTE
- CHANGE_REQUIRED
- BLOCKED_PENDING_SOURCE

Critical findings must block green promotion until corrected and re-tested.
