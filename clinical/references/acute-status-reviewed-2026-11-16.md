# Status: reviewed conditional contracts — 2026-11-16

## Decision and scope

The project owner has accepted the clinical work and authorized resolving the P2 medication blockers. This review preserves that acceptance and the previous phenytoin adoption; it does not ask for the same authorization again. The exact contract IDs remain `status-phenytoin-local` and `status-refractory`. The former is a compatibility identifier, not a requirement to work in a particular hospital or jurisdiction.

These two contracts now have implementable, bounded outputs. Phenytoin offers a dose/time calculation and, separately, an optional product-specific preparation calculation. Refractory status offers specialist decision support, including escalation when resources are unavailable. Neither change asserts prospective clinical validation or an independently authenticated Pharmacy signature. The project's `CLINICALLY_PENDING` status and unrelated safety gates are preserved.

The recorded acceptance is carried by `acute-contract-owner-acceptance-2026-11-16.json`. Earlier provenance remains in the status owner acceptance of 2026-11-13 and the phenytoin preflight branch `review/status-phenytoin-preflight-20261115`, commit `4dcd6903c50910327e95c4b29d9d5909434f212e`. Its three historical files are:

- `clinical/qa/STATUS_PHENYTOIN_LOCAL_PRECLINICAL_GATE_2026-11-15.md`
- `clinical/scripts/status_phenytoin_local_preflight.py`
- `clinical/tests/test_status_phenytoin_local_preflight.py`

That preflight was deliberately disconnected from the API. Its historical NO-GO wording and always-blocked return do not override the later owner-authorized conditional release described here. The new helper does not import or silently change those historical files.

## Primary sources checked on 2026-11-16

| Source | Identified version and applicability | Use in these contracts |
|---|---|---|
| [Medinfo Galway: Phenytoin Intravenous for Adults](https://www.medinfogalway.ie/ivguides/phenytoin-intravenous-adults) | Live institutional IV guide; no page revision date is displayed. Its bibliography includes the Epanutin SPC of March 2023, Medusa accessed March 2024, and the adult GUH algorithm of March 2023. | The previously adopted adult initial loading regimen; a separately selected preparation profile for the exact products listed there. It is not a universal product label. |
| [NICE NG217, chapter 7](https://www.nice.org.uk/guidance/ng217/chapter/treating-status-epilepticus-repeated-or-cluster-seizures-and-prolonged-seizures) | NG217, updated 30 January 2025; recommendations 7.1.8–7.1.11. | After adequate initial treatment, IV second-line options and expert-led further treatment. Failure of one second-line option may lead to another under expert guidance; phenobarbital or general anaesthesia requires expert management. No numeric anaesthetic regimen is inferred. |
| [Intensive Care Society: acute management of adult status epilepticus](https://pmc.ncbi.nlm.nih.gov/articles/PMC12062632/) | Published 8 May 2025; *J Intensive Care Society* 26(2):249–262, DOI [10.1177/17511437251321338](https://doi.org/10.1177/17511437251321338). Scope: patients over 16 years, excluding obstetric presentations. | Refractory-stage identification, early critical-care involvement, EEG and referral/transfer. The implemented subset is adults aged 18 years or older and excludes obstetric management. |
| [Phenytoin Hospira 50 mg/mL SmPC](https://www.medicines.org.uk/emc/product/3794/smpc) | UK product information, eMC update 8 July 2026. | Product-specific contraindications and evidence that equal concentration does not establish preparation/regimen equivalence. Its adult loading recommendation of 10–15 mg/kg and its preparation instructions differ from the adopted Galway profile. It is not substituted into the Galway pump calculation. |

The international policy in `international-guideline-policy.md` applies: one canonical clinical module, with justified, complete source-specific choices. A dose source, a product label and an organization's operational capabilities are different kinds of evidence. Selecting this regimen does not declare it universally preferable, combine incompatible regimens or impose a hospital on the rest of Emergency.

## Phenytoin: two explicit capabilities

Both modes require adult age, verified weight, a clinician-confirmed convulsive indication after adequate benzodiazepine treatment, assessment of contraindications/interactions, available monitoring, and confirmation that the selected initial loading regimen is appropriate. Prior phenytoin/fosphenytoin exposure or maintenance therapy is outside this initial-load calculator: it requires a separate assessment rather than an automatic repeat. Cause-specific exceptions likewise do not receive this automatic loading result.

The selected calculation is:

```
dose_mg = 20 × min(weight_kg, 100)
rate_mg_min = dose_mg / selected_duration_min
```

The 2,000 mg cap is part of this selected regimen. The minimum duration of 40 minutes records the owner's preceding adoption decision; Galway itself does not impose a universal 40-minute minimum. The selected duration must respect the individual rate limit. This implementation adds a conservative maximum selected rate of 25 mg/min for an explicitly identified elderly/cardiac-risk patient; slower administration or a different dose/regimen may still be necessary. This is a bounded implementation rule, not a claim that every such patient has one universally correct rate.

### `dose_only`

The result contains mg, the selected duration and the corresponding mg/min. Product, withdrawal volume, final concentration, dilution, pump setting and stability are absent. The patient may therefore use a product not listed in the optional preparation profile, provided the clinician has verified that this selected dosing regimen applies; that product still needs its own preparation assessment before use.

For example, 100 kg at a selected maximum of 25 mg/min requires at least 80 minutes for this 2 g dose. Dose-only mode may represent that arithmetic without inventing a product's stability. It does not authorize preparing or infusing a mixture whose stability cannot accommodate it.

### `verified_preparation`

This optional profile requires the exact Epanutin or Mercury 250 mg/5 mL product listed by Galway, with documented correspondence between the actual product and the complete procedure. Equal concentration alone is insufficient; 100 mg/2 mL or another manufacturer's product is not automatically interchangeable.

The profile's source-bound values are: stock 50 mg/mL, NaCl 0.9% only, final concentration at most 10 mg/mL, maximum rate 50 mg/min, 5-micron drawing-up filter and 0.2-micron inline filter. Its saline table is:

| Dose | Verified NaCl volume before drug addition |
|---|---:|
| Below 500 mg | 50 mL |
| 500–1,000 mg inclusive | 100 mL |
| Above 1,000 mg | 250 mL |

The guide requires immediate initiation and completion within 60 minutes, a large-vein access, ECG/BP monitoring plus respiratory/site observation, clear solution, and saline flushing before/after. The final flush delivers residual drug at the same infusion rate. These are preparation-specific requirements, not global stability rules for all phenytoin products.

The implementation requires actual saline and final volumes to be independently verified, including the handling of bag overfill. It does not silently infer the final volume from the nominal bag label. Within this additive preparation the cross-check is `final_volume = verified_saline_volume + dose / 50`; a discrepancy stops the pump calculation instead of adapting the preparation.

```
pump_ml_h = verified_final_volume_ml × 60 / selected_duration_min
flush_duration_min = selected_duration_min × verified_post_flush_ml / verified_final_volume_ml
completion_min = elapsed_since_preparation_min + selected_duration_min + flush_duration_min
```

The post-flush volume is a required, verified case input, not a volume invented by this project. Counting the time needed to deliver residual drug through the line is an explicit conservative implementation of the completion limit. Exactly 60 minutes is allowed, subject only to floating-point representation tolerance; the older preflight's strict less-than-60 buffer is not misrepresented as a manufacturer stability limit. The elapsed-time check is not permission to delay the required immediate start or store the mixture. A timing conflict stops this preparation; the calculator never accelerates the infusion to satisfy expiry.

Manual acceptance example: 70 kg gives 1,400 mg; over 40 minutes this is 35 mg/min. Withdrawal from a verified 50 mg/mL product is 28 mL. Adding this to a measured 250 mL saline volume gives a verified final 278 mL and 417 mL/h. A verified 20 mL final flush at the same pump rate takes about 2.878 minutes; the total from an immediate start is about 42.878 minutes. This example is synthetic verification, not a default flush-volume recommendation.

## Refractory status: specialized decisions without an invented prescription

The decision workflow requires a non-obstetric adult after adequate benzodiazepine and second-line treatment. Ongoing convulsions or documented electrographic seizures support the entered refractory state. Continued impairment of consciousness without visible convulsions instead prompts urgent assessment and EEG; it is not automatically labelled non-convulsive status. An electrographic claim without EEG evidence is rejected.

The ICU consensus supports early critical-care review after adequate treatment fails, continuous EEG for refractory cases or persisting depressed consciousness, and specialist advice about management/transfer if EEG is unavailable. The contract translates that guidance into explicit actions determined by actual resources. Missing monitoring, airway expertise, critical care or EEG does not block access to the escalation instructions. It triggers the relevant support/transfer action and cannot enable an anaesthetic infusion.

The result is `result_kind=decision_support`, `treatment_calculated=false`. Medication dose, administration volume, duration and pump rate are all null. The expert team selects any additional antiseizure drug or anaesthetic regimen, with the necessary airway, haemodynamic and EEG support. The project does not turn a referral decision into a medication order.

## Interface and verification

`acute_reviewed_status.py` supplies exactly these two replacement rows through `reviewed_contracts(contract, field)`. Both identify this reference through `review_reference` and the dispatcher through `reviewed_workflow=status`. Common fields come from the canonical contract constructor. The compatibility key `local_protocol_verified` now means verifying the selected guidance and clinical context; it does not require a local hospital protocol.

The `calculation_scope` choice drives `required_if` for preparation fields. The API validates the active fields' types, expected values and boundaries. Missing active data cannot produce a result. Non-null data from an inactive preparation mode are rejected so an export cannot retain a hidden stale preparation. The helper adds cross-field checks, not a second type validator. Source revision hashes and faithful export checks remain the responsibility of the canonical API.

`test_acute_reviewed_status.py` provides explicit, independent browser fixtures and tests for both phenytoin modes and refractory decision support. It checks active missing inputs, populations, prior drugs, contraindications, numeric limits, product/diluent/filter mismatch, the 500/1,000 mg dilution boundaries, the 2 g cap, actual volume, rate/time conflicts, exact 60-minute completion including flushing, resource gaps, EEG-state consistency and export semantics. Test success establishes the stated functional behavior only.
