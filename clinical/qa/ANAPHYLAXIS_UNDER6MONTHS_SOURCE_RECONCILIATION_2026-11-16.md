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


## Addendum — 2026-11-16: owner-supplied clinical compendium reviewed

**Supersedes the earlier statement in this file that no user attachment was available.** The owner subsequently provided `compendio_cl_nico_diagn_stico_manejo_de_emergencia_y_prevenci_n_de_la_anafilaxia.md`, SHA-256 **81de9bbc77e585d007e89424dd287a1edd6c10e29cf7d775a2cbd7d8d55e5895** (20,618 bytes). It describes a consolidation of an **ANAFILAXIA.pdf** covering 255 pages and multiple UpToDate topics; the infant chapter is listed as topic 5750 v26.0, last updated **2026-09-22**, and the emergency treatment chapter as topic 392 v74.0. Versions/dates are as supplied in the compendium, not independently authenticated against UpToDate. The compendium explicitly reports OCR/automatic-translation corrections, so do **not** import its wording without primary-source cross-checking. Its full proprietary medical text is **not copied into this repository**.

### Evidence contributed, limited to contract 3

- The compendium describes **IM epinephrine 0.01 mg/kg from a 1 mg/mL solution**, anterolateral thigh, with exact weight-based measurement where feasible. This agrees with [ERC 2025 paediatric life support](https://www.sciencedirect.com/science/article/abs/pii/S0300957225002795) and the treatment rationale of [Portugal DGS Norma 014/2012, amended 2014](https://www.dgs.pt/directrizes-da-dgs/normas-e-circulares-normativas/norma-n-0142012-de-16122012.aspx). DGS's source text explicitly states 0.01 mg/kg IM, max 0.5 mg, and may repeat after 5 minutes.
- Its **infant chapter** describes repetition in **5–15 minutes** if necessary, while the emergency treatment overview and ERC recommend reassessment/repetition at **5 minutes if symptoms persist**. Preserve this chapter-level difference rather than merging it into an automatic schedule. There is no software-triggered repeat.
- For an infant **below 10 kg**, the source emphasizes precise weight-based dosing in a clinical setting where it can be prepared rapidly and measured safely. Its alternative **0.1 or 0.15 mg autoinjector** discussion applies to availability and urgency in community/self-rescue settings; it is **not equivalent** to a default hospital dose for a small infant, nor proof such a device is authorized/stocked in Portugal.
- The RCUK age-band alternative **100–150 micrograms for <6 months**, as recorded in the previous source dossier, remains **non-interchangeable** with 10 micrograms/kg in small infants. The prior RCUK July 2025 algorithm PDF link could not be re-fetched in this review; check the exact current primary algorithm before any decision on that pathway. No automated selection of fixed doses is allowed.
- The compendium's general paediatric maximum of **0.3 mg in children <=30 kg** and the ERC/DGS general maximum of **0.5 mg** are **different scopes/caps**: neither should be silently propagated to neonatal code. The infant 0.01 mg/kg rule and population-specific ceiling must be reviewed explicitly.
- The compendium documents clinically subtle infant presentations (sudden lethargy/hypotonia, altered activity, hoarse cry, drooling) and the danger of delaying IM epinephrine. This should inform **clinical alerts and diagnostic support**, not become a diagnostic gate requiring skin findings or measured hypotension.
- IV boluses, IV infusions for refractory anaphylaxis, prehospital auto-injector selection, and discharge prescribing belong to **separate contracts**; this review does not authorize or implement them.

### Operational acceptance conditions before any executable infant dose

1. Explicit local paediatric/Pharmacy choice between a **weight-based 0.01 mg/kg IM** pathway and any fixed-band alternative, with documented neonatal/infant scope and repeat policy; do not use age-only interpolation.
2. Identify the **exact locally stocked IM product** (1 mg/mL), its Portuguese label and a reliable **small-volume syringe/measurement technique**, including independent double-check and rounding limits. Do not infer reliable measurement from nominal concentration.
3. Verify boundaries and negatives: 0 days, 1 day, 1/3/5 months, just before and at 6 months; extreme/missing weights; mg vs micrograms; mL rounding; wrong concentration; IV/IM route mix-up; duplicate administration and monitoring/escalation; no delays in real clinical care while software waits.
4. Resolve source differences on observation policy (the historical DGS norm prescribes **8–24 hours**, while the supplied compendium discusses shorter observation in low-risk cases) in the **separate disposition module**, not by changing this IM medication gate.
5. Obtain professional review of the final protocol + QA evidence tied to the exact code/tree version before removing `block_reason` from `anaphylaxis-under6months`.

**Decision:** documentary evidence augmented; `anaphylaxis-under6months` stays **BLOCKED / CLINICAL_REVIEW_REQUIRED**; 19 medication blocks retained; no clinical dosage engine, source registry, `main`, protected branches or I02 modified.


## Addendum — 2026-11-16: owner-reported diluted adrenaline for small doses (NOT APPROVED FOR IM)

**New local report:** the project owner describes "Adrenalina 1 mg, dilución en 10 mL de cloreto de sodio 0,9 % para dosis pequeñas." This is recorded verbatim as **OWNER_REPORTED_PREPARATION_NOT_YET_RECONCILED**, not an authenticated Pharmacy order or authorization to change the IM route.

**Crucial volume ambiguity:**
- 1 mg made up to a **FINAL total volume of 10 mL**: 0.1 mg/mL = 100 micrograms/mL.
- 1 mg in 1 mL **added to** 10 mL NaCl 0.9%: approximate nominal total volume 11 mL and concentration 0.0909 mg/mL (about 90.9 micrograms/mL); actual preparation still requires validated manufacturing/measurement.
- These formulations are **NOT interchangeable**. No automatic conversion is permitted without an explicitly written FINAL total volume, independent double-check and verified product.

**Route conflict requiring specific clinical/Pharmacy sign-off:** The [ERC 2025 paediatric life support guidance](https://www.sciencedirect.com/science/article/abs/pii/S0300957225002795) and [Portugal DGS 014/2012](https://www.dgs.pt/directrizes-da-dgs/normas-e-circulares-normativas/norma-n-0142012-de-16122012.aspx) reference **1 mg/mL IM adrenaline** for anaphylaxis (dose 0.01 mg/kg). The [licensed SmPC for a prefilled adrenaline 1 mg/10 mL (0.1 mg/mL) product](https://www.medicines.org.uk/emc/product/2024/smpc) explicitly says it is *not recommended for IM use* in acute anaphylaxis and indicates 1 mg/mL for IM. This warning refers to that product, not automatically every hospital-prepared dilution, but it underscores a serious route/formulation confusion risk. A diluted hospital IM procedure would require its own signed, product-specific approval and demonstrated safe preparation/administration; do not infer it from IV resuscitation syringes.

**Temporary software gate:** Keep \`anaphylaxis-under6months\` \`BLOCKED\`, return \`CLINICAL_REVIEW_REQUIRED\`, and do not compute/administer IM/IV volume from the proposed dilution. Do not auto-populate an age-fixed dose, generate a prefilled-syringe instruction or infer permission to use 0.1 mg/mL IM. The clinical emergency treatment must never be delayed by a software approval gate.

**Single clarification needed from owner/Pharmacy:** Does "10 mL" mean **final prepared volume** or **10 mL of diluent added to a 1 mL ampoule**, and is that dilution explicitly approved for **IM use in infants <6 months**, as distinct from IV emergency use? Confirm the actual ampoule label, whether dilution is performed aseptically, final concentration, device/rounding, preparation age/expiry, reviewer's name/date, and nursing double-check. If no validated IM-specific approval exists, retain the guideline's 1 mg/mL IM pathway for professional review instead.

**No executable medication-code changes, no dose calculation, no automatic unblock, no global status change.**


## Addendum — 2026-11-16: explicit owner's clarification of dose and FINAL volume

**Correction to previous ambiguity, confirmed by owner:** the preferred dosing rule for professional review is **0.01 mg/kg = 10 micrograms/kg IM**. The hospital-described dilution means **1 mg of adrenaline brought up to a TOTAL FINAL VOLUME of 10 mL of NaCl 0.9%**, not 1 mL drug plus 10 mL diluent. Its **nominal** final concentration is **0.1 mg/mL = 100 micrograms/mL**. The earlier 11 mL possibility is ruled out by this correction; it must not be treated as the local preparation. This is recorded as an **owner-reported** preparation; exact formulation, aseptic method, stability, and IM authorization are **not independently validated**.

**Mandatory route safety gate remains open:** [ERC 2025 PLS](https://www.sciencedirect.com/science/article/abs/pii/S0300957225002795) and [DGS Anafilaxia Norma 014/2012 (2014 update)](https://www.dgs.pt/directrizes-da-dgs/normas-e-circulares-normativas/norma-n-0142012-de-16122012.aspx) specify **1 mg/mL IM** with 0.01 mg/kg for anaphylaxis. [RCUK 2025 paediatric emergency algorithm](https://www.resus.org.uk/sites/default/files/2025-07/RCUK%20Paediatric%20emergency%20algorithms%20and%20resources%20Jul%2025%20V3.1.pdf) also specifies **1 mg/mL IM**, but provides a pragmatic fixed 100–150 microgram band for <6 months; the owner selects **weight-based** as the project-preferred reference, not the RCUK fixed band. [SmPC for a commercial adrenaline 1 mg/10 mL prefilled syringe](https://www.medicines.org.uk/emc/product/2024/smpc) explicitly warns it is **not recommended for IM administration in acute anaphylaxis** and recommends 1 mg/mL IM instead. This is a PRODUCT-specific SmPC, not proof that all locally prepared diluted products are contraindicated, but no transfer of approval from IV/IO to IM is permitted.

**Do not create an executable dilution-based IM dose or volume in the clinical API at this stage.** A 0.1 mg/mL diluted preparation is **10-fold less concentrated** than the 1 mg/mL IM solution described in primary guidance and is a high-risk route/concentration mismatch. The treating clinician may administer guideline-based urgent therapy independently of the software; software review must never delay emergency care.

**Next required confirmation:** Does the owner's 1mg/10mL final preparation refer to **hospital IM injection in infants under 6 months** or only **IV emergency administration**? If IM: obtain Pharmacy-approved exact product and dilution/IM route SOP, syringe/measurement/recheck method, dating and monitoring; then conduct pediatric QA against the final authorized specification. If IV: it belongs to a separate IV-resuscitation protocol, not an IM anaphylaxis loading calculator, and this contract must retain a 1 mg/mL IM reference.

**STATUS:** owner decision on weight-based dose and final volume **recorded**; clinical use of diluted preparation **not authorized by this dossier**; `anaphylaxis-under6months` remains **BLOCKED / CLINICAL_REVIEW_REQUIRED**. All other blocks and `CLINICALLY_PENDING` remain unchanged.


## DEFINITIVE ROUTE RECONCILIATION — Owner confirmation 2026-11-16

**This paragraph supersedes the earlier open IM-vs-IV questions in this document. Route and dilution ambiguity is RESOLVED by the owner's explicit clarification:**

| Use | Route | Product/preparation | Clinical rule | Boundary |
|---|---|---|---|---|
| Infant acute anaphylaxis | **IM** | **UNDILUTED adrenaline 1 mg/mL** | **0.01 mg/kg = 10 micrograms/kg**, weight-based | This is the only preparation proposed for the **contract 3** IM pathway; exact product, dose-measurement process, clinical sign-off and tests remain pending |
| Separately described hospital IV preparation | **IV ONLY** | **1 mg adrenaline made up to a FINAL total volume of 10 mL with NaCl 0.9%** = **0.1 mg/mL (100 micrograms/mL)** | **NO IV dose or infusion authorization derived from this statement** | Explicitly PROHIBITED for the contract 3 IM route; IV use requires its own approved indication, protocol and team, including separation from resuscitation/infusion rules |

There is **NO local IM dilution**. Never transform the IM order into 0.1 mg/mL, or convert the hospital's IV dilution into IM syringes. Preserve distinct route/concentration identifiers. Any input claiming IM with 0.1 mg/mL or IV with the 1 mg/mL IM reference **must fail closed** in future software. Do not confuse this with an established or validated IV anaphylaxis protocol.

The owner-selected weight-based dose takes precedence over the RCUK pragmatic fixed 100–150 microgram under-6-month band in the *proposed* contract, but the discrepancy remains recorded for professional review. **The emergency clinician should never delay immediate evidence-based treatment awaiting software approval.**

**Open prerequisites for removing the BLOCKED software guard:** independently reconcile exact locally stocked IM 1 mg/mL medicine and its Portuguese product information, trained small-volume syringe/measurement and double-check procedure, age/weight/units/rounding and repeat-interval rules (including neonates), signed local paediatric and Pharmacy acceptance, source-hash-bound adverse/negative tests, and independent QA of the final integrated release. `anaphylaxis-under6months` stays **BLOCKED / CLINICAL_REVIEW_REQUIRED**. The separate IV/refractory pathway also stays blocked. `main`, all 19 blocked contracts, four P1, `CLINICALLY_PENDING`, and I02 NO-GO are untouched.
