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
