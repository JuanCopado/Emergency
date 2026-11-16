# EMERGENCY — Contract 3/19: anaphylaxis-under6months evidence reconciliation
**Date:** 2026-11-16. **Scope:** IM adrenaline in anaphylaxis, infants younger than 6 months, including careful neonatal boundary review. **Status:** \`CLINICAL_REVIEW_REQUIRED\` / \`BLOCKED\` (software only). No executable dosing or clinical release.

## Actual evidence provenance
This entry is based on primary public clinical sources. The project owner's message refers to anaphylaxis documentation, but **no new anaphylaxis attachment was available in the current conversation at this review**; no user file was silently inferred or claimed to have been reviewed. Incorporate the supplied document when it becomes available and cross-reference its exact version and source.

1. [ERC Guidelines 2025 — Paediatric Life Support](https://www.erc.edu/media/03xnpjmj/gl2025-09-pls-e.pdf): IM adrenaline **0.01 mg/kg = 10 micrograms/kg**, solution **1 mg/mL**, anterolateral mid-thigh, general maximum 0.5 mg; repeat IM after **5 min** if symptoms persist. Published pragmatic age-band doses begin at **1 year**, not a specific validated fixed dose for infants under 6 months.
2. [Direção-Geral da Saúde — Norma 014/2012, updated 18/12/2014, Anafilaxia: Abordagem Clínica](https://www.dgs.pt/directrizes-da-dgs/normas-e-circulares-normativas/norma-n-0142012-de-16122012.aspx): IM adrenaline **0.01 mg/kg**, maximum 0.5 mg, in the anterolateral thigh; may be repeated after **5 min** in the described national protocol. This is the DGS **general clinical anaphylaxis** norm, not the vaccination-focused Norma 002/2023.
3. [RCUK paediatric emergency algorithm, publication July 2025, based on 2021 guidance](https://www.resus.org.uk/sites/default/files/2025-07/RCUK%20Paediatric%20emergency%20algorithms%20and%20resources%20Jul%2025%20V3.1.pdf): pragmatic **100–150 micrograms IM for children <6 months**; repeat after 5 min if no response. **This is materially different from 10 micrograms/kg in a small infant. It must not be merged automatically with the weight-based approach or treated as directly interchangeable.**
4. [AEMPS Adrenalina Basi label (Spain)](https://cima.aemps.es/cima/dochtml/ft/89175/FT_89175.html): may inform 1 mg/mL formulation safety but **does not prove the exact Portuguese stocked formulation or precise small-volume administration device**.

## Candidate reconciliation (not implemented as executable care)
- Proposed reference for review: **ERC 2025 / DGS 014/2012 weight-based IM recommendation**, not an automatic approval of the age-band RCUK option.
- Restrict to **confirmed acute anaphylaxis and IM route**. This contract does **not** implement an IV bolus/infusion or use any IV refractory pathway.
- Capture exact chronological age in **days/months** and weight in kg; no guessed age-based default for newborn/young infants. Obtain expert paediatric assessment, but **never delay life-saving clinical adrenaline while obtaining software sign-off**.
- Require documentation of exact product concentration and trained ability to measure small volumes reliably. Do not generate a syringe volume until the locally approved formulation, measurement method and dosing rules are reconciled.
- For very young neonates, confirm any specific population exceptions and product restrictions before permitting an automated calculator.
- Record the difference between ERC/DGS weight-based and RCUK fixed-age approaches as an unresolved choice; do not add doses, repeat counts or automatic conversions to the canonical API.
- If professional reviewers select a route, record named reviewer, competence, version/date, exact source, allowable neonatal/infant population, dose limit, repeat/escalation conditions and relevant pharmacy/product reference.

## Required QA and clinical release gates
- Weighted/adversarial tests: age 0 days; 1 day; 1, 3 and 5 months; exact 6-month boundary; valid/invalid/missing weights; concentration mismatch; route mismatch; units micrograms/mg/mL; precision/rounding/measurement; repeat timing and clinical escalation.
- Check clinical risk: support ABCDE; IM immediately according to treating clinician; emergency escalation if refractory or persistent compromise; RCUK/European and DGS disagreement explicit in UI; no delay of therapy because of computer workflow.
- Verify product stocked in Portugal, IM authorization, exact 1 mg/mL label, reliable syringe capability and operational training.
- Clinical/pharmacy review and independent functional QA linked to the final code SHA required before any executable dosing or change to \`BLOCKED\`.

## Registry integrity
Current \`clinical/qa/V1.44_MEDICATION_PRODUCT_PROTOCOL_RECONCILIATION.json\` lists \`anaphylaxis-under6months\` as \`BLOCKED\` due to the unresolved 100–150 microgram fixed-band vs individual selection. No production change, no altered canonical dose, no YELLOW→GREEN promotion. All 19 medication blocks, four historical P1 issues and \`CLINICALLY_PENDING\` remain in force.

**Documentary evidence captured; clinical choice and approval remain pending.**
