# EMERGENCY — I01 status-phenytoin-local: preflight candidate
**Date:** 2026-11-15. **Scope:** Adult IV phenytoin loading in convulsive status epilepticus.
**Change type:** Experimental, isolated preflight and synthetic tests, not connected to the clinical calculation API or UI.
**Clinical release:** NO-GO. **Contract:** `status-phenytoin-local` remains `BLOCKED`; all other 18 medication guards unchanged. `CLINICALLY_PENDING`, I02 NO-GO, P1 and other gates remain.

## Provenance / conflicting product sources
The owner reports that local Pharmacy accepts the [Medinfo Galway adult IV phenytoin protocol](https://www.medinfogalway.ie/ivguides/phenytoin-intravenous-adults), but no identifiable, dated local approval or exact product-specific Portuguese regulatory sheet has been independently supplied. This candidate **does not claim** that Galway is the authorized SmPC for the hospital's product.

Galway specifically covers phenytoin **250 mg/5 mL** (50 mg/mL) and states adult convulsive status loading **20 mg/kg, cap 2,000 mg**, NaCl 0.9% only, in-line **0.2 micron filter**, flush with NaCl 0.9% before/after, ECG and BP continuously, respiratory/site observation, maximum **50 mg/min**, and consider **25 mg/min or lower** for elderly or cardiac disease. Start immediately after preparation; complete within **60 minutes**. Dilution table: <500 mg → 50mL; 500–1000mg → 100mL; >1000mg → 250mL. **500mL is not in Galway's dilution table.**

[Hospira UK SmPC (July 2026)](https://www.medicines.org.uk/emc/product/3794/smpc) covers its *own* 250mg/5mL product, recommends a different 10–15mg/kg status loading regimen and distinct infusion-preparation requirements, with 50mg/min maximum and slower administration in selected patients. **Do not assume interchangeability.** Other manufacturers may advise against dilution. The pharmacy-identified specific product and a matching authorized regimen still need documented reconciliation.

## Candidate algorithm (QA ONLY)
A pure, standalone `clinical/scripts/status_phenytoin_local_preflight.py` assesses synthetic examples using `dose_mg = min(20*weight_kg, 2000)` and `minimum_duration = max(40, ceil(dose_mg / individual_max_rate_mg_min))`; requires the selected Galway bag size; hard-fails pediatric or 100mg/2mL substitutions, nonfinite/invalid values, contraindication, incomplete monitoring/IV/risk or pharmacy attestations, and duration plus delay **at or beyond** the 60-minute point. This strict inequality is a conservative QA buffer, **not a claimed new stability limit**. No extra dosing, maintenance, PE-unit conversion, product withdrawal volume, true final concentration or pump mL/h is generated; `prescription_enabled` is ALWAYS false.

## Requirements before any actual unblocking
1. Dated, attributable Pharmacy approval for the actually stocked product and the scope of the Galway dilution/filter/compatibility/stability procedure, or a manufacturer-specific approved alternative.
2. Adult clinical/Neurology review of 20mg/kg, the 2g initial cap, contraindications, prior drugs, risk-adjusted speed, stop/reassessment and handling of cases that cannot finish within 60 minutes after mixing.
3. Define bag overfill/withdrawal policy and **actual final volume**, product source, concentration, pump/flush behavior and documented expiry; do not infer mL/h from nominal bag volume.
4. Bounded integration into the clinical API with fail-closed acceptance/negative and export tests linked to the resulting SHA; regression of all 19 blocked contracts and the four P1 gates.
5. Independent clinical/Pharmacy review and a separate authorized release decision. No automatic change to evidence GREEN/YELLOW or CLINICALLY_PENDING.

## Tests
12 synthetic tests passed in an isolated authoring sandbox using `python -m unittest discover -s clinical/tests -p 'test_status_phenytoin_local_preflight.py'`. This is **not** full-project CI, on-repo execution, clinical validation or a release pass. The new module must remain disconnected from `acute_medication_api` and existing `block_reason` until all conditions are met.


## Follow-up decision recorded 2026-11-16 (owner-reported Pharmacy approval)
The project owner states that the local Pharmacy **authorizes/adopts the Galway adult phenytoin preparation**. Record as \`OWNER_REPORTED_PHARMACY_APPROVAL\` and retain its exact source and scope. This statement does not independently authenticate a signed, dated hospital formulary entry or product-specific Portuguese SmPC.

The owner confirms **20 mg/kg adult initial loading, cap 2,000 mg**, reference **40 min** (prolong as needed to respect the individual rate limit), and requires a hard **minimum NaCl 0.9% volume** check rather than using the 10 mg/mL nominal ceiling alone. The source-specific Galway brackets are:
- <500 mg: **50 mL** NaCl 0.9%.
- 500–1,000 mg inclusive: **100 mL** NaCl 0.9%.
- >1,000 mg: **250 mL** NaCl 0.9%.

The updated standalone preflight rejects volumes below those brackets (including 500 mg in 50 mL despite nominal 10 mg/mL), and additionally rejects larger bags such as 500 mL **unless separately validated by Pharmacy**, because Galway's table is not evidence for that substitution. It rejects non-NaCl 0.9%, absent filter/line checks by required clinician confirmation, visible precipitate, unsafe individual rates, insufficient monitoring, and schedules that cannot complete within the 60-minute preparation window. The minimum duration is only a review calculation. If it conflicts with stability, the proposal is blocked; never accelerate to comply with expiry.

The 250 mg/5 mL scope is the only Galway formulation automatically considered in this preflight. Owner-reported 100 mg/2 mL ampoules are documented but not covered by the Galway-specific source check. **No production prescription, dose administration or infusion pump calculation is released.**

## Evidence / implementation limitations
- Original module \`acute_medication_contracts.py\` still specifies \`block_reason\` for \`status-phenytoin-local\`; \`acute_medication_api.py\` still rejects it.
- Tests added to \`clinical/tests/test_status_phenytoin_local_preflight.py\` cover 19 separate synthetic test methods, including exact dose/volume boundaries, slow-rate expiry collision, unsupported products and inadmissible inputs.
- All 19 medication contracts remain BLOCKED; four historical P1 findings, project \`CLINICALLY_PENDING\`, I01 PARTIAL and I02 NO-GO remain.
- Future unblocking requires source/product matching and independent technical/clinical sign-off tied to the exact release tree. The reported local authorization cannot be silently represented as an authenticated signature.
