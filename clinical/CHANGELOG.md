## High-risk evidence source splitting — batch 6 (02/10/2026)
- Split and verified sources for orthopedic emergencies and acid-base emergencies.
- Added regulatory-source splits for vasopressin, dexmedetomidine, remifentanil and clevidipine; residual drug-label sets remain explicit compounds.
- Catalog increased from 140 to 147 normalized sources; compound identities reduced from 14 to 12.
- Added verified NICE NG37/NG38, ACP/AAFP acute musculoskeletal pain 2020, NEJM acid-base reviews, DailyMed Vasostrict 2026, Dexdor SmPC, remifentanil SmPC and Cleviprex DailyMed.
- Added regression coverage for this batch. No clinical recommendation, dose or module text changed.

## High-risk evidence source splitting — batch 5 (02/10/2026)
- Split and verified sources for CNS infection, acute respiratory failure/ARDS, pericardial/tamponade guidance, syncope/falls/frailty, croup, febrile infant, bronchiolitis and non-coronary chest-pain framing.
- Catalog increased from 132 to 140 normalized sources; compound identities reduced from 19 to 14.
- Added verified WHO meningitis 2025 + practical manual 2026, ATS/ESICM/SCCM ARDS ventilation 2017, ESC myocarditis/pericarditis 2025, ESC syncope 2018, ACEP geriatric ED guidance, CPS croup 2026, RCH upper-airway guidance, CPS febrile-infant 2026, AAP febrile-infant 2021, NICE NG9, CPS bronchiolitis 2021 and AHA/ACC chest-pain 2021.
- Residual syndrome-specific respiratory, pericardiocentesis and non-coronary chest-pain sets remain explicitly compound pending individual verification.
- Added regression coverage for this batch. No clinical recommendation, dose or module text changed.

## High-risk evidence source splitting — batch 4 (02/10/2026)
- Split and verified sources for ECG image interpretation, ECG/POCUS integration, thyroid storm, myxoedema coma, acute spinal cord compression, altered consciousness imaging, CT/MRI screenshot context and ophthalmology image review.
- Catalog increased from 128 to 132 normalized sources; compound identities reduced from 26 to 19.
- Added verified AHA/ACCF/HRS ECG standards, 2026 thyroid-storm and myxoedema joint consensus statements, ATA 2016 hyperthyroidism, ATA 2014 hypothyroidism, NICE NG234, 2024 acute SCI hemodynamic guideline, ACR altered-mental-status criteria, ACR criteria collection and AAO PPP sources.
- Altered-consciousness syndrome-specific stabilization guidance remains explicitly compound pending individual split.
- Added regression coverage for this batch. No clinical recommendation, dose or module text changed.

## High-risk evidence source splitting — batch 3 (02/10/2026)
- Split and verified sources for noninvasive ventilation, high-flow nasal oxygen, emergency oxygen, POCUS image review, ECG/POCUS integration, spontaneous intracerebral hemorrhage and status epilepticus.
- Catalog increased from 123 to 128 normalized sources; compound identities reduced from 31 to 26.
- Added verified ERS/ATS NIV 2017, BTS/ICS NIV 2016, ERS HFNC 2022, ROX multicenter validation 2019, BTS emergency oxygen 2017, ACEP POCUS 2023, ESO/EANS ICH 2025, AHA/ASA ICH 2022, AES convulsive status epilepticus 2016 and ILAE status definition/classification 2015.
- Oxygen implementation details and syndrome-specific ECG guidance remain explicitly compound pending individual verification.
- Added regression coverage for this batch. No clinical recommendation, dose or module text changed.

## High-risk evidence source splitting — batch 2 (02/10/2026)
- Split and verified sources for ICU sedation/PADIS, hypertensive emergencies, IV antihypertensive selection, pediatric dehydration/shock, lower-GI/small-bowel bleeding and traumatic intracranial mass effect.
- Catalog increased from 112 to 123 normalized sources; compound identities reduced from 34 to 31.
- Added verified SCCM PADIS 2018/2025, ESC hypertension 2024, ACC/AHA aortic 2022, AHA/ASA ICH 2022, DailyMed nicardipine 2026, NICE NG29, RCH dehydration 2026, ESGE small-bowel 2022, ACG small-bowel 2015, ACG LGIB 2023, BTF severe TBI 4th edition, NCS cerebral-edema 2020 and ENLS 6.0 ICP/herniation.
- Remaining mixed ICU-drug-label, hypertensive syndrome-specific and obstetric/product-label sets stay explicitly compound pending individual verification.
- Added regression coverage for this batch. No clinical recommendation, dose or module text changed.

## High-risk evidence source splitting — batch 1 (02/10/2026)
- Added verified source overrides for airway RSI, anticoagulation reversal, paediatric status epilepticus, paediatric shock/emergencies/arrhythmias/arrest, adult resuscitation/arrhythmias, sepsis and vasoactive infusions.
- Normalized source catalog increased from 103 to 112 identities; compound identities reduced from 36 to 34.
- Verified sources include official DAS 2025, SCCM RSI 2023, ACC 2020, ACG-CAG 2022, ESGE 2021/2026, HSE 2025, NICE NG217/NG254, ERC/RCUK 2025, SSC 2021/2026, norepinephrine SmPC and dopamine DailyMed.
- Remaining vasoactive product-label set stays explicitly compound until each label is individually verified.
- Source overrides are deterministic and included in the normalizer; no clinical recommendation, dose or module text changed.

## Evidence provenance normalization (02/10/2026)
- Added `references/evidence-sources.json`: 103 normalized source identities mapped to all 106 modules.
- Added deterministic regeneration/check script; unknown organization/date/language/jurisdiction/license metadata remains null/unknown instead of being invented.
- 36 legacy compound source identities are explicitly flagged and are not automatically split without documentary verification.
- Knowledge Graph now consumes normalized source nodes and module→source relationships with role/claim scope.
- Evidence audit now fails on missing/unknown source IDs or broken reverse mappings.
- Clinical CI verifies that the normalized catalog is reproducible and current.
- No clinical recommendation, dose or module content changed.

## Audit hardening — validation, evidence freshness and CI (02/10/2026)
- Manifest validation now rejects duplicate IDs/sections and uses exact module-ID boundaries in router checks.
- Living Evidence now enforces configured 30/90/180-day review windows; expired green records fail the audit instead of remaining silently current.
- Added regression tests for evidence expiry, duplicate manifest IDs and exact router matching.
- Added dedicated PWA CI: install, unit tests, lint, typecheck and production build.
- Clinical CI now covers architecture/model policy paths and uses current Node-24-based GitHub Actions.
- Generated Graphify/Knowledge Graph/RAG artifacts and common local secret files are excluded from Git.
- No clinical recommendation, dose or module content changed.

## Project consolidation — Graph/RAG/Graphify infrastructure (02/10/2026)
- Added project architecture, Graphify guidance/exclusions, RAG contract and external-model registry.
- Added deterministic module→bundle→evidence-source graph builder and tests; it performs no clinical inference and fails on manifest/evidence mismatch.
- Added GitHub Actions clinical CI for manifest, evidence, unit/regression tests and graph generation.
- No clinical recommendation, dose or module content changed in this infrastructure update.

## v1.35 working update — ICU/ED Continuous Infusions (draft)
- Added `vasoactive-inotrope-infusions` (cardiovascular bundle): norepinephrine, vasopressin, epinephrine, dopamine (not first-line in septic shock), dobutamine, milrinone, levosimendan, phenylephrine and availability-caveated angiotensin II, with phenotype position (cross-referenced, not duplicated), label/guideline doses, titration, ceilings, dilution/concentration, 70 kg mL/h arithmetic, peripheral/central caveats, extravasation and weaning.
- Added `icu-sedation-analgesia-infusions` (procedures-pharmacology bundle): analgesia-first ICU continuous fentanyl, remifentanil, morphine, hydromorphone, propofol, dexmedetomidine, midazolam and ketamine adjunct; RASS/CPOT/BPS targets, light sedation, daily interruption, PRIS/triglycerides, dexmedetomidine bradycardia, benzodiazepine accumulation/delirium. `sedoanalgesia` kept as procedural sedation with a one-line cross-reference.
- Sources: SSC 2026/2021, PADIS 2018/2025, product labels/SmPC (see `updates/icu-infusions-review-2026-09-29.md`). Infusion calculator gains fixed-dose and per-hour helpers; every worked mL/h example is unit-tested. Manifest 104 -> 106. Human review, Portuguese RCM/local protocol checks and pediatric infusions pending.

## v1.34 working update — Shock, Arrhythmia and Arrest Pathways (draft)
- Audited actual module index: etiologic shock pathways already existed, but no undifferentiated shock route; one short combined rhythm/arrest module did not provide age-specific algorithms.
- Added six focused routes: undifferentiated shock, pediatric shock, adult arrhythmias, adult cardiac arrest, pediatric arrhythmias and pediatric cardiac arrest. Preserved the old combined ID as a shared router and reused existing cause-specific modules.
- Updated age/cause routing and evidence records; ERC/RCUK 2025 sources checked. Human clinical and Portugal/Azores protocol review remain pending.

## v1.33 working update — Pediatric Emergency Pathways (draft)
- Added five routes to the existing special-populations bundle: febrile infant ≤90 days, bronchiolitis, croup, pediatric dehydration/shock and pediatric convulsive status epilepticus.
- Updated router, manifest, evidence registry and pending queue; the generic pediatric module remains the shared base.
- No duplicated module IDs; local Portugal/Azores pediatric protocols/formulary and human clinical release review remain pending.

## v1.32 working update — Small-Bowel Bleeding (draft)
- Added the suspected small-bowel bleeding pathway after adequate nondiagnostic upper/lower endoscopy to the existing `lower-gi-bleeding` module.
- Separated unstable active hemorrhage (resuscitation, CTA/angiography pathway) from stable capsule evaluation, ideally within 48 h after overt bleeding where safe; added retention-risk screening and capsule-directed enteroscopy.
- No module IDs, medication doses or test cases added. ACG acute imaging guidance is older (2015); human and local GI/IR pathway review remains pending.

# Emergency Medicine Skill v1.32 — Small-Bowel Bleeding Review (draft)

93 module IDs. This ZIP is a v1.32 working copy based on the uploaded v1.26 package;
it is not an installed or published skill. Clinical images are reviewed through the host model's available
vision using a common intake/quality gate plus a modality-specific module for
musculoskeletal radiographs, chest radiographs, POCUS, ECG, skin/wounds,
CT/MRI screenshots, ophthalmology or other clinical images.
No new diagnostic model is trained or connected. Diagnostic accuracy is unvalidated.
Example: upload a de-identified image and ask in Spanish for the most probable
diagnosis, supporting visible signs, alternatives and next step; include region,
age, symptoms and onset if known. The skill must abstain when evidence is inadequate.

The internal image-output schema makes observations, inference, unavailable data,
confidence, urgency and next actions explicit. `scripts/evaluate_image_cases.py`
scores completed authorized cases against independent references and reports
leading/top-3 performance, critical sensitivity, false reassurance, appropriate
abstention, urgency accuracy and undertriage with denominators. Synthetic examples
test the evaluator only and are not clinical performance evidence.

Version 1.21 adds a dedicated IV-antihypertensive selection pathway when
nicardipine is unavailable. It explicitly rejects nimodipine substitution,
provides labelled labetalol and ready-to-use clevidipine concentrations with
mL/h arithmetic, and selects beta-blocker, nitrate or pregnancy-specific therapy
according to organ injury rather than BP alone. One sourced regression preserves
these availability and contraindication gates.

The v1.28 working draft expands the existing upper-GI-bleeding module across resuscitation, selective pre-endoscopy prokinetics, peptic-ulcer endoscopic stigmata/rescue, and a separate variceal pathway. It reuses the existing lower-GI and anticoagulation modules; no module ID was added. Small-bowel workup and detailed antithrombotic restart/reversal remain pending. This is not locally approved. See `updates/gi-bleeding-review-2026-09-28.md`.

The v1.29 draft adds focused acute mesenteric anticoagulation reconciliation to the existing module, including MVT heparin choice, duration and the fact that current guidelines do not give a universal UFH pump nomogram. Local protocol review remains pending. See updates/mesenteric-anticoagulation-review-2026-09-28.md.

The v1.28 draft expands the existing upper GI hemorrhage route across stabilization, risk/airway, selected prokinetics, peptic-ulcer endoscopic management and a separate variceal pathway. It reuses existing lower-GI and anticoagulation routes. Small-bowel diagnostic workup and agent-specific antithrombotic restart/reversal remain pending. See `updates/gi-bleeding-review-2026-09-28.md`.

The v1.27 working draft reconciles thyroid storm and myxoedema coma with 2026 joint
endocrine consensus statements. It labels the distinct thyroid-storm hydrocortisone
regimens, updates hepatic/PTU and potassium safety, and leaves the enteral
levothyroxine fallback pending source and local pharmacy review. It is not a
clinician-approved or locally adopted protocol.

Version 1.20 adds dedicated pathways for spontaneous intracerebral hemorrhage,
acute spinal cord compression and cauda equina/conus emergency. It separates
spontaneous from traumatic intracranial BP strategy, adds reversible 100/200 mL
nicardipine pump arithmetic, anticoagulant/platelet/ICP safety gates, etiology-
specific spinal steroid and source-control decisions, and emergency MRI/referral
timing. Three new source-attributed regressions cover high-risk non-delay errors.

Version 1.19 adds dedicated adult bedside pathways for acute severe asthma, COPD
exacerbation and life-threatening hemoptysis. It includes inhaled and systemic
drug doses, controlled-oxygen targets, magnesium timing, NIV/intubation failure
gates, airway/lung-isolation strategy, CTA/bronchoscopy sequencing, embolization
and surgical escalation, plus three new sourced regressions.

Version 1.18 adds dedicated bedside pathways for cardiogenic shock, acute aortic
syndrome and cardiac tamponade/pericardial emergency. These include explicit
cause control, hemodynamic targets, 100/200 mL pump preparations with mL/h
examples, contraindications, rescue/failure logic, POCUS integration and critical
care/definitive-procedure escalation. It adds three source-attributed regressions.

Version 1.17 gives all 76 modules an explicit evidence record, adds four
published real-image workflow cases with provenance and licensing metadata, and
prevents annotated or diagnosis-known cases from entering diagnostic-accuracy
metrics. It also strengthens SAH/headache, CNS infection, endocarditis, syncope,
delirium, suicide risk, pancreatitis, acute liver failure, alcohol withdrawal,
rhabdomyolysis and POCUS safety boundaries. These published cases are unblinded
teaching/workflow checks, not evidence of sensitivity or accuracy.

Version 1.5 adds a brain cross-sectional imaging safety pass for extra-axial
collections, mass effect and midline displacement, plus a medication-selection
module that verifies indication, target, titration, contraindications and monitoring.
It prevents transferring drugs or blood-pressure targets between related but distinct
neurologic syndromes.

Version 1.6 adds a dedicated tension-pneumothorax pathway. It treats shock with
compatible unilateral respiratory findings as time-critical, prevents a normal-range
heart rate or pending imaging from providing false reassurance, limits POCUS to use
that does not delay decompression, and requires a rescue plan, immediate reassessment
and definitive pleural drainage.

Version 1.7 requires every continuous infusion to show its 100 or 200 mL
preparation when appropriate, final concentration, arithmetic, titration and pump
rate in mL/h. Bolus and intermittent medication remain expressed as dose, volume
and administration time rather than being falsely converted to continuous rates.

Version 1.8 adds a traumatic intracranial mass-effect pathway. It separates
perfusion-preserving lower BP bounds from disease-specific upper targets, treats
hypertonic saline as a weight-based rescue bolus, gives a pump-ready nicardipine
reference only when compatible, and keeps neurosurgical evacuation definitive.

Version 1.9 separates sodium, potassium and calcium/magnesium emergencies; adds a
ruptured abdominal-aortic-aneurysm pathway; and expands procedural sedation and
rapid-sequence intubation with drug doses, monitoring, rescue plans and reassessment.

Version 1.10 prevents incomplete hypernatremia answers by requiring plasma osmolar
indices, urine osmolality/electrolytes and electrolyte-free water clearance whenever
the required measurements are supplied.

Version 1.16 adds source-attributed clinical regression cases, a provenance
validator and an evidence-coverage auditor. It corrects safety-critical details in
sepsis, arrhythmia, acute heart failure, hypertensive emergencies, critical valve
disease, status epilepticus, obstetric emergencies, traumatic hemorrhage, upper GI
bleeding and anticoagulant reversal. Passing these checks does not establish
prospective clinical effectiveness or diagnostic accuracy.

This release adds a controlled evidence-maintenance layer.

The module manifest now resolves every module ID to a real clinical decision
scaffold in `modules/`. Run `python3 scripts/validate_modules.py` to verify that
the manifest, bundles and router remain structurally consistent.

Important design choice:
The skill may detect and propose updates automatically, but should not silently rewrite high-risk clinical recommendations. New guidance enters a pending review queue and is promoted only after validation.

Recommended automation:
- weekly scan for new authoritative emergency-care guidelines
- monthly review of high-risk modules
- quarterly global audit
- immediate web verification for high-risk protocol-level questions


The v1.31 draft reconciles antithrombotic holding, selective reversal and restart across the existing upper-GI, lower-GI and anticoagulation modules. It records low-certainty disagreement on DOAC reversal and leaves restart timing individualized by source and thrombotic risk. No module IDs were added. Human clinical and local protocol review remain pending; see `updates/gi-antithrombotic-review-2026-09-28.md`.


The v1.32 draft adds a small-bowel bleeding diagnostic extension to the existing `lower-gi-bleeding` module after nondiagnostic upper/lower endoscopy. It distinguishes unstable active bleeding from stable early capsule evaluation, accounts for capsule-retention risk, and routes positive studies to device-assisted enteroscopy. No module IDs were added. See `updates/small-bowel-bleeding-review-2026-09-28.md`.
