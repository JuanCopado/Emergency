# QA POLICY — Emergency Medicine v1.36

## Purpose
This QA layer is a release-control system. It does not itself establish clinical validity.

## Principles
1. **Fail closed for structural defects.** Missing modules, duplicate IDs, broken routing, missing evidence records, invalid dates or malformed clinical regression cases block release.
2. **High-risk changes require human review.** A high-risk module cannot become `green` merely because automated tests pass.
3. **Clinical regression tests preserve reviewed invariants.** They are not prospective outcome validation.
4. **Medication QA is unit-sensitive.** Dose, maximum dose, route, concentration, final volume, units and mL/h arithmetic must remain internally consistent.
5. **Localization is explicit.** Portugal/Azores stock, product strength, salt/base expression, diluent, compatibility, stability and local protocol must never be inferred.
6. **Image QA is separate from diagnostic validation.** Teaching or annotated cases cannot be counted as blinded accuracy evidence.

## QA gates
- QA-1 Structural integrity
- QA-2 Evidence integrity
- QA-3 Clinical regression integrity
- QA-4 Pharmacology/calculation integrity
- QA-5 Localization and human-release gate

## Release classes
- **BLOCKED**: any mandatory automated gate fails.
- **TECHNICALLY_PASSING / CLINICALLY_PENDING**: automated gates pass but high-risk human/local review is incomplete.
- **RELEASE_CANDIDATE**: automated gates pass and required human/local review records are complete.
