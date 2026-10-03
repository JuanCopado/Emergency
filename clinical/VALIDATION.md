# Validation report — estado autoritativo actual v1.35

## v1.36 blinded image evaluation infrastructure
- Dataset contract v1.1 requires one modality/target, patient/study hashes, prediction-freeze and reference-reveal timestamps, independent reference and leakage controls.
- Allowed prediction classes: positive, negative, abstain, nondiagnostic.
- Standard sensitivity/specificity/PPV/NPV/accuracy are suppressed whenever any case is abstain/nondiagnostic; coverage and unresolved counts remain visible.
- Wilson 95% intervals are computed only when binary metrics are available.
- `scripts/create_blinded_image_dataset.py` creates new manifests fail-closed with authorization/deidentification/reference flags false.
- Current Clinical QA after this infrastructure: 151 tests PASS. This validates methodology/structure, not diagnostic accuracy.
- Candidate real-world sources are documented separately in `qa/IMAGE_DATASET_SOURCES.md`; none is counted as an evaluated case merely by being listed.


## v1.36 current branch snapshot — 127 modules
- `scripts/validate_modules.py`: 127 modules resolved.
- Evidence registry: 127/127; 29 green / 98 yellow / 0 red.
- `Clinical QA`: **151 automated tests PASS** on the current v1.36 branch snapshot.
- These are structural/arithmetic/regression checks, not clinical validation.


## v1.36 pediatric procedural sedation
- Adds `pediatric-procedural-sedation` (112 -> 113 modules).
- Sources: RCH procedural sedation, ketamine, nitrous oxide and intranasal fentanyl guidance.
- Separates procedural sedation from RSI and continuous PICU sedation.
- Expected registry state: 113/113 evidence records; 31 green / 82 yellow / 0 red.
- Automated tests preserve dose/monitoring/recovery boundaries; this is not clinical validation.


## v1.36 pediatric blood products and major haemorrhage
- Adds `pediatric-blood-transfusion-major-hemorrhage` (111 -> 112 modules).
- Sources: ERC/RCUK PLS 2025, RCH Blood Product Prescription and RCH Trauma Primary Survey.
- Provides deterministic component-volume calculations while deliberately avoiding a universal massive-transfusion pack ratio.
- Expected registry state: 112/112 evidence records; 31 green / 81 yellow / 0 red.
- Automated tests verify arithmetic and source boundaries; this is not clinical validation.


## v1.36 pediatric electrolyte emergencies
- Adds `pediatric-electrolyte-emergencies` (110 -> 111 modules).
- Sources: RCH pediatric hyperkalaemia/hypokalaemia/hypomagnesaemia, NICE NG29 sodium emergencies, calcium gluconate SmPC and RCH hypoglycaemia.
- Expected registry state: 111/111 evidence records; 31 green / 80 yellow / 0 red.
- Automated checks verify sourced dose/monitoring invariants; this is not clinical validation.


## v1.36 pediatric asthma and RSI
- Adds `pediatric-acute-asthma` and `pediatric-airway-rsi` (108 -> 110 modules).
- Sources: GINA 2026 pediatric acute asthma and RCH current emergency airway management.
- Expected registry after registration: 110/110 evidence records; 31 green / 79 yellow / 0 red.
- Automated checks verify key pediatric doses and route separation; they are not clinical validation.


## v1.36 pediatric IV fluid therapy
- Adds one high-risk module ID: `pediatric-iv-fluid-therapy` (107 -> 108).
- Current evidence set: NICE NG29/CG84, SSC pediatric sepsis 2026, ISPAD DKA 2022, RCH dehydration/hypernatraemia 2026.
- Adds deterministic calculations for shock bolus, ORS 4-hour rehydration, Holliday-Segar maintenance, percentage deficit, staged 24+24 h generic deficit replacement, gastroenteritis IV deficit, hypernatraemia 48-hour deficit rate and symptomatic hyponatraemia bolus.
- Expected branch evidence state after registration: 108/108; 31 green / 77 yellow / 0 red.
- These are structural/arithmetic checks, not clinical validation.


## v1.36 pediatric emergency medication layer
- Working branch adds one high-risk module ID: `pediatric-emergency-medications` (106 -> 107).
- Adds deterministic arithmetic in `scripts/pediatric_emergency_calculator.py` for capped weight-based doses, volume-from-concentration, weight-based infusion mL/h, fluid boluses, Holliday-Segar maintenance and NICE gastroenteritis deficit references.
- Clinical source layer: ERC/RCUK PLS 2025 + AHA/AAP PALS 2025 + SSC pediatric sepsis 2026 + NICE NG29/CG84 + HSE pediatric status 2025 + PANDEM 2022 + official product information.
- The calculator does **not** select a diagnosis or indication. The pump generator only uses dose/concentration entries explicitly source-verified in the pediatric infusion registry; Horta-local verification is not required for pediatrics.
- Current branch state: 127/127 records; 29 green / 98 yellow / 0 red; **151 automated tests PASS**.
- Source-verified continuous infusion entries: epinephrine, norepinephrine, dopamine (with source weight restriction), dobutamine, milrinone, fentanyl and midazolam. Dexmedetomidine/propofol remain fail-closed because of guideline/product-label conflict; ketamine continuous dosing remains pending.


## v1.35 ICU/ED continuous infusion modules
- Added two module IDs (104 -> 106) in existing bundles; no new bundle and no duplicated ID.
- Worked 70 kg pump-rate examples for every continuous infusion are reproduced by unit tests using `scripts/infusion_calculator.py`.
- Evidence records added as yellow/high priority; SSC 2026 full text, ESC 2021 dose table and Portuguese RCM were not accessible/checked (see update note).
- These are structural/arithmetic checks only; no clinical validation, human review or local protocol reconciliation has been performed.

## v1.35 execution results (2026-09-29)
- `scripts/validate_modules.py`: PASS, 106 modules resolved.
- `scripts/audit_evidence_coverage.py`: PASS, 106/106 evidence records; 31 green / 75 yellow / 0 red; no errors or warnings.

## Nota sobre snapshots históricos
Los resultados numéricos que aparecen en secciones posteriores (por ejemplo **93/93**, **98 IDs** o **104/104**) corresponden exclusivamente a la versión indicada en cada bloque. **No representan el estado vigente.** El estado autoritativo actual es v1.35: **106 IDs**, **106/106 evidencia**, **31 green / 75 yellow / 0 red** y **63/63 tests**.
- `python3 -m unittest discover -s tests -q`: PASS, 63/63 tests (manifest cardinality assertion updated to 106; five new infusion tests).
- `scripts/check_evidence_registry.py`: completed; 75 records review-due (all yellow), including both new modules; no release approval implied.

## Histórico — snapshot v1.34

## v1.34 shock, rhythm and cardiac arrest pathway audit
- Added six focused modules after confirming the previous bundle had only one brief combined adult-leaning rhythm/arrest pathway and lacked a general shock entry route.
- Reused existing etiologic pathways for septic, cardiogenic, hemorrhagic, anaphylactic, obstructive, adrenal and obstetric causes; no duplicate cause module added.
- Current checks are recorded after running structural, evidence-coverage and unit-test validation below. Clinical review and Portuguese local protocol reconciliation remain pending.

## Histórico — seguimiento v1.34

## Historical v1.33 pediatric pathways review
- Added five pediatric module IDs in the existing special-populations bundle; no new bundle.
- Router, evidence registry and pending queue updated; local Portugal/Azores protocols and clinician review pending.
- Validation results follow after execution.

# Validation report v1.32 working draft

## v1.32 small-bowel bleeding review
- Reused existing `lower-gi-bleeding` module; no new ID, dose or test case.
- Source/scope limitations are documented; ACG acute imaging guidance is from 2015.
- Structural, evidence and unit-test results are updated below.
- Local GI/IR workflow and formulary review, human clinical review and prospective validation remain pending.

# Validation report v1.31 working draft

## v1.31 GI antithrombotic review
- Reused existing upper-GI, lower-GI and anticoagulation-reversal module IDs; no cases or doses added.
- ESGE 2026/2021 and ACG-CAG 2022 source reconciliation recorded, including certainty and scope limitations.
- Structural/evidence/unit-test validation results are recorded below after execution.
- Portugal/Azores formulary/protocol review, human specialist review and prospective clinical validation remain pending.

# Validation report v1.30 working draft

## v1.30 enteral evidence review
- **Histórico de esa versión:** 93-module manifest and existing modules unchanged; no regression cases added.
- Evidence note and queue updated. No new medication regimen was promoted.
- scripts/validate_modules.py: PASS, 93 modules resolved.
- scripts/audit_evidence_coverage.py: PASS, 93/93 records, 34 green / 59 yellow / 0 red; no errors or warnings.
- python -m unittest discover -s tests -q: PASS, 58/58 tests.
- No local formulary or prospective clinical validation was performed.

## v1.29 mesenteric anticoagulation update
- **Histórico de esa versión:** no new module ID or regression case; existing 93-module manifest retained.
- scripts/validate_modules.py: PASS, 93 modules resolved.
- scripts/audit_evidence_coverage.py: PASS, 93/93 records, 34 green / 59 yellow / 0 red; no errors or warnings.
- python -m unittest discover -s tests -q: PASS, 58/58 tests.
- Exact hospital anticoagulation nomogram, local monitoring and clinician review remain pending.

## v1.28 GI hemorrhage update
- **Histórico de esa versión:** 93 module IDs remained in the manifest; no new IDs or regression cases were added.
- Existing upper/lower GI and anticoagulation module routes were reused.
- `scripts/validate_modules.py`: PASS, 93 modules resolved.
- `scripts/audit_evidence_coverage.py`: PASS, 93/93 records, 34 green / 59 yellow / 0 red, no errors or warnings.
- `python -m unittest discover -s tests -v`: PASS, 58/58 tests.
- Evidence freshness check leaves yellow records due for external review by design; no DGS/INFARMED/local stock verification was performed.
- Clinical release review, local Portugal/Azores protocol/formulary checks, and prospective validation remain pending.

# Validation report v1.27 working draft

## v1.27 targeted update

- **Histórico de esa versión:** 93/93 manifest IDs resolved and had evidence records.
- All 58 existing unit tests pass; module and evidence-coverage audits pass.
- The targeted endocrine consensus comparison is documented in
  `updates/endocrine-consensus-review-2026-09-27.md`.
- No regression cases were added and no clinical-response/diagnostic-accuracy
  evaluation was performed for this content change. Clinician review and Portuguese
  product/formulary checks remain pending; this is not an installed release.

## v1.24 scope

Targeted source reconciliation completed for ESVS 2025 recommendations 37/40/41/45
and ESGE 2026 peptic-ulcer timing/PPI/escalation. Source access limitations reported
in v1.23 are resolved. The queue retains narrower regimen/detail follow-up.
No new patient cases or independent clinical-response evaluation were performed.

## v1.23 scope

Two GI/vascular modules and two synthetic cases added. Automated checks validate
structure and case metadata; they do not run clinical responses or establish
diagnostic accuracy. ESVS 2025 and the identified ESGE 2026 update remain pending
full-text reconciliation, explicitly recorded in the update queue.

## v1.22 scope

Two burn/smoke modules and two synthetic source-attributed cases were added.
Case validation checks provenance and module references, not actual clinical
answers. No clinical accuracy or patient-outcome claim follows from passing.

## Scope of validation

Automated tests cover module loading, shared preamble preservation, numerical
examples and contextual missing/invalid input handling. They do not evaluate
image recognition, sensitivity, specificity, diagnostic calibration or outcomes.
Manual image cases in `tests/image-review-cases.json` remain not_run until actual
authorized image-based evaluation with independent references is performed. One
ankle radiograph workflow was exercised after v1.3, but no independent report was
supplied, so it is not counted as an accuracy case. Prior successful demonstrations
are not clinical validation. Run current tests with:

`python3 -B -m unittest discover -s tests -p 'test_*.py' -v`

`python3 scripts/validate_modules.py`

`python3 scripts/validate_clinical_cases.py`

`python3 scripts/audit_evidence_coverage.py`

`python3 -B scripts/evaluate_image_cases.py tests/image-evaluation-example.json`

## v1.21 IV antihypertensive alternative audit

- 86/86 manifest modules resolve deterministically and have evidence records
- 23 source-attributed synthetic regressions include an unavailable-nicardipine case
- nimodipine cannot be selected as a general nicardipine replacement
- labetalol and clevidipine preserve verified concentrations, mL/h arithmetic,
  titration and cardiopulmonary/formulation contraindications
- drug selection branches by ICH, aortic syndrome, pulmonary edema/ACS, pregnancy
  and toxicologic physiology rather than treating the BP number alone
- these are structure and regression checks, not prospective clinical validation

## v1.20 neurovascular and spinal emergency audit

- 85/85 manifest modules resolve deterministically and have evidence records
- 22 source-attributed synthetic regressions include three new neurologic/spinal cases
- spontaneous ICH preserves immediate reversal, smooth BP control without SBP below
  130 mm Hg, neurosurgical escalation and non-routine platelet/seizure/ICP treatment
- acute spinal compression separates malignant, traumatic, infectious and hemorrhagic
  causes and limits dexamethasone to supported indications
- cauda equina/conus preserves emergency MRI/referral, PVR limitations and rejects a
  nominal 48-hour interval as permission to delay
- these are structure and regression checks, not prospective clinical validation

## v1.19 critical respiratory audit

- 82/82 manifest modules resolve deterministically and have evidence records
- 19 source-attributed synthetic regressions include three new respiratory cases
- acute severe asthma preserves controlled oxygen, adequate inhaled bronchodilator
  dosing, early steroid, selective magnesium and dynamic-hyperinflation safeguards
- COPD exacerbation preserves 88--92% oxygen pending gas, a five-day systemic
  steroid course, conditional antibiotics and early NIV for hypercapnic acidosis
- life-threatening hemoptysis is physiology-defined and prioritizes airway/lung
  protection plus embolization/surgical control rather than a volume threshold
- these are structure and regression checks, not prospective clinical validation

## v1.18 shock and advanced chest-pain audit

- 79/79 manifest modules resolve deterministically and have evidence records
- 16 source-attributed synthetic regressions include three new shock/chest-pain cases
- cardiogenic shock requires SCAI staging, serial perfusion endpoints, cause control,
  phenotype-guided vasoactive therapy and shock-team escalation
- acute aortic syndrome preserves beta-blocker-before-vasodilator sequencing,
  perfusion-aware BP targets, definitive imaging and type-specific intervention
- tamponade is defined by physiology rather than effusion size, avoids preload loss
  and hazardous positive pressure, and requires cause-appropriate urgent drainage
- norepinephrine, dobutamine, esmolol, labetalol and nicardipine reference preparations
  have independently testable concentrations and bedside mL/h arithmetic
- these are structure and regression checks, not prospective clinical validation

## v1.16 sourced safety audit

- 76/76 manifest modules in that release resolved deterministically
- 13 synthetic, de-identified regressions in that release had an authoritative source identity,
  expected module set, required actions and prohibited unsafe actions
- source provenance and module references are machine-validated
- all declared high-risk modules have an evidence-registry record
- unregistered modules remain yellow by default rather than inheriting false assurance
- sepsis timing distinguishes shock/probable sepsis from possible sepsis without shock
- cardiovascular checks preserve rhythm instability, syndrome-specific BP reduction,
  heart-failure phenotype and critical-valve boundaries
- status epilepticus, eclampsia, traumatic hemorrhage, upper GI bleeding and oral
  anticoagulant reversal received explicit safety gates
- these are structure and regression checks, not prospective clinical validation

## v1.10 targeted hypernatremia checks

- serum osmolality and effective tonicity use explicit unit-aware formulae
- measured versus calculated osmolality produces an osmolal gap
- urine osmolality and urine sodium are never fabricated from serum sodium alone
- urine sodium, urine potassium and urine volume produce electrolyte-free water clearance
- diagnostic interpretation distinguishes concentrated, intermediate and dilute urine

## v1.9 targeted emergency checks

- named electrolyte disorders route to ion-specific modules rather than generic replacement
- hyperkalemia distinguishes myocardial stabilization from potassium removal and monitors glucose
- sodium correction has symptom-based boluses, ceilings and an overcorrection rescue pathway
- IV potassium cannot be pushed or prescribed without mmol and final concentration
- suspected ruptured AAA cannot be excluded by POCUS or delayed for nonessential testing
- sedation requires a dedicated clinician, capnography and airway rescue capability
- RSI includes physiologic optimization, Plan A-D, first-pass strategy and post-intubation sedation

## v1.8 targeted intracranial mass-effect checks

- traumatic extra-axial hemorrhage with mass effect routes to an immediate neurosurgical pathway
- hyperosmolar treatment is a bridge and cannot replace or delay definitive evacuation
- spontaneous-ICH upper BP targets cannot be copied automatically into traumatic mass effect
- age-stratified SBP floors and cerebral perfusion are preserved
- adult 3% hypertonic saline remains a 5 mL/kg bolus over 5--20 minutes, not a continuous infusion
- nicardipine reference arithmetic is tied to a verified 20 mg/200 mL concentration
- the de-identified regression stores no patient image and does not establish diagnostic accuracy

## v1.7 targeted infusion checks

- every continuous infusion requires a final concentration and pump rate in mL/h
- 100 mL and 200 mL preparations are supported when compatible and locally appropriate
- weight-based arithmetic cannot invent a missing patient weight or formulation
- titration includes dose units, mL/h, interval, ceiling and hold/stop thresholds
- bolus and intermittent drugs are not misleadingly converted into continuous rates
- norepinephrine 8 mg/100 mL at 0.1 mcg/kg/min for 80 kg = 6 mL/h
- norepinephrine 8 mg/200 mL at 0.1 mcg/kg/min for 80 kg = 12 mL/h

## v1.6 targeted respiratory regression checks

- shock cannot be dismissed because heart rate is within a usual reference range
- high clinical suspicion of tension pneumothorax does not wait for radiography
- POCUS is used only when immediately available without delaying decompression
- decompression includes technique/site verification, rescue planning, reassessment
  and definitive drainage rather than being treated as a completed pathway
- absent improvement triggers equipment review and renewed obstructive-shock differential
- the scenario is synthetic/de-identified and tests instructions, not patient outcomes

## v1.5 targeted regression checks

- brain CT/MRI instructions require explicit extra-axial, ventricular, cisternal,
  midline, mass-effect and herniation review before reassurance
- screen-recorded stacks require original-quality representative and contiguous frames
- absent orientation cannot silently become patient laterality
- medication selection must state indication, target, route, titration, monitoring
  and stop criteria
- nimodipine and nitrate examples test disease-indication boundaries rather than
  serving as a fixed formulary
- the triggering clinical case is recorded only as an abstract regression scenario;
  no patient media is retained in the skill
- these checks validate instructions and structure, not diagnostic sensitivity or
  medication safety outcomes

## v1.4 image checks

- all eight image modality routes resolve through the manifest
- attachment recovery has a single safe retry and forbids unrelated-file substitution
- image reports have a machine-readable completeness schema
- radiographs request views and laterality marker; POCUS states still/cine/compression scope
- evaluation exposes critical sensitivity, false reassurance, abstention and undertriage
- every metric reports numerator and denominator and excludes unreferenced cases explicitly
- synthetic evaluation data are labelled as non-clinical
- clinical/vision accuracy remains pending independent representative evaluation

## Structural checks
- SKILL.md present
- router present
- module index present
- response templates present
- evidence policy present
- calculators present
- test cases present

## Arithmetic checks
- 8 mg norepinephrine in 100 mL, 80 kg, 0.1 mcg/kg/min -> 6 mL/h
- weight-based dosing supports optional maximum dose cap

## Stability goals
v1.0 is the first consolidated stable release.
Further versions should prioritize validation and targeted refinement over uncontrolled module growth.

## v1.2 modular completeness checks
- all 54 manifest IDs resolve to existing bundle files
- each ID has exactly one matching `## module-id` section
- orphan and duplicate sections fail validation
- route lines must resolve to at least one known module
- unknown module loading fails explicitly rather than silently
- official Skill Creator quick validation passes

## v1.1 Living Evidence checks
- evidence registry present
- update policy present
- pending update queue present
- status model green/yellow/red defined
- high-risk 30-day review cadence defined
- stable modules cannot be silently overwritten
- registry checker script present
- update record generator present
- regression tests added for stale evidence handling
## v1.31 execution results
- `scripts/validate_modules.py`: PASS, 93 modules resolved.
- `scripts/audit_evidence_coverage.py`: PASS, 93/93 evidence records; 33 green / 60 yellow / 0 red; no errors or warnings.
- `python -m unittest discover -s tests -q`: PASS, 58/58 tests.
- Archive integrity (`unzip -t`) and SHA-256 are recorded after packaging.
## v1.32 execution results
- `scripts/validate_modules.py`: PASS, 93 modules resolved.
- `scripts/audit_evidence_coverage.py`: PASS, 93/93 evidence records; 33 green / 60 yellow / 0 red; no errors or warnings.
- `python -m unittest discover -s tests -q`: PASS, 58/58 tests.
- Local GI/IR pathway, human review and prospective clinical validation were not performed.
## v1.34 execution results
- `scripts/validate_modules.py`: PASS, 104 modules resolved.
- `scripts/audit_evidence_coverage.py`: PASS, 104/104 evidence records; 31 green / 73 yellow / 0 red; no errors or warnings.
- `python -m unittest discover -s tests -q`: PASS, 58/58 tests (manifest cardinality assertion updated to 104).
- Source checksum audit, ZIP integrity and archive SHA-256 are recorded after packaging.
- No local Portugal/Azores pediatric protocol or formulary check and no prospective clinical validation were performed.

## v1.34 final verification (2026-09-28)
- `scripts/validate_modules.py`: PASS, 104 modules resolved.
- `scripts/audit_evidence_coverage.py`: PASS, 104/104 records; 31 green, 73 yellow, 0 red.
- `python -m unittest discover -s tests -q`: PASS, 58 tests.
- `scripts/check_evidence_registry.py`: completed; outputs review-due status for yellow/high-priority records, no release approval implied.
- `unzip -t`: PASS.
- Clinical performance and local protocol validation are not established by these technical checks.


## v1.36 — image source intake gate / PTB-XL blinded protocol — 02/10/2026
- Added fail-closed candidate-source registry and validator.
- Added PTB-XL prespecified fold-10 intake protocol with patient/study hashing and a physically separate sealed reference file.
- Synthetic targeted check: 2 fold-10 rows (1 positive, 1 negative) -> patient hashing stable across repeated patient; no `target_positive` field in the model-facing cohort.
- Registry logic check: 5 candidates, no structural errors; PTB-XL intake-ready only after license + protocol + label-separation gates; no source is described as clinically validated.
- `test_skill.py` currently contains 156 test functions. **Do not record 156 PASS until a complete CI/local run is observed.** Last complete verified run remains 151 PASS.

- Added manual GitHub Actions real-intake workflow for PTB-XL v1.0.3. It keeps blinded images/manifest separate from the sealed reference and can use an ephemeral masked salt when no repository secret exists.
- Added structural regression ensuring the sealed reference is not copied into the blinded artifact and that render wording does not claim unverified physical calibration.
- Test file now contains **157 test functions**. Full-suite PASS count remains **151 confirmed** until the new PR-triggered Clinical QA run is observable.
- Draft validation PR: #12. It is explicitly non-release/non-merge and does not change the v1.35 clinical line.

- Added freeze/reveal finalizer regression coverage: incomplete prediction sets and late freezes are blocked; valid finalized manifests strip source ECG identifiers and preserve abstentions.
- Current test file: **159 test functions**. GitHub Actions `Clinical QA` run #285 completed successfully: **Ran 159 tests ... OK** and `automated_status: PASS`.

## PTB-XL real blinded pipeline pilot — 02/10/2026
- GitHub Actions `PTB-XL Blinded ECG Intake` run #6 (37042742831): **SUCCESS**.
- Builder, blind/reference separation, blinded upload and sealed-reference upload all passed.
- Blind artifact: 10 PNG + 1 manifest; target AFIB; `selection_mode=balanced_pipeline_pilot_5_per_class`; `performance_metrics_allowed=false`.
- Static inspection confirmed no target labels or original PTB-XL ECG/patient IDs in the blinded manifest.
- One rendered ECG was visually inspected for layout integrity; no source label was revealed.
- The sealed-reference artifact was not downloaded/opened for diagnostic interpretation.
- This is pipeline validation only. Balanced class selection discloses prevalence and therefore must not be used for blinded diagnostic-performance claims.

## Blinded sharding / prediction merge — 02/10/2026
- Clinical QA run #295: **SUCCESS**.
- Unified QA: `automated_status: PASS`.
- Unit regression suite: **Ran 161 tests ... OK**.
- Sharding preserves patient groups; prediction merge fails closed on missing shards, incomplete classes or missing freeze timestamps.

## PTB-XL full-fold engineering hardening — 02/10/2026
- Clinical QA #297: SUCCESS after artifact sharding/leakage-gate integration.
- Clinical QA #298: SUCCESS after parallel deterministic ECG rendering.
- Current regression suite: **162 tests PASS**.
- Optimization changes execution only: concurrent record downloads and 4-process rendering. Selection, hashes, fold, target, layout, blinded manifest and sealed reference semantics are unchanged.
- Full-fold accelerated intake run #11 (37050506581) launched with `FULL_FOLD` / AFIB; reference remains sealed.

## PTB-XL AFIB NATURAL_500 blinded bank — 02/10/2026
- Intake run #13 (37051568918): **SUCCESS**.
- Selection: systematic label-agnostic sample across fold 10, n=500.
- Blinded package audit: 500 PNG, 11 shards, 11 prediction templates, 500 unique study hashes, 488 patient hashes.
- 11 repeated-patient groups, max 3 studies/patient; zero patient groups cross shards.
- No sealed reference file and no source/reference leakage terms were found in the blinded package.
- Blinded artifact digest: `sha256:c932d356b5fddf19f4e41417ac9320656a0d6d8af7f3219730cff916291ee6be`.
- Reference artifact remains sealed; only its GitHub artifact digest was recorded.
- Nine evenly distributed rendered ECGs were visually inspected for layout integrity; no diagnostic/source annotation leakage observed.
- No sensitivity/specificity/accuracy claim is made because predictions have not been generated/frozen by an actual blinded interpreter.


## PTB-XL NATURAL_500 v2 — AFIB image baseline v1 — post-reveal
- Pre-reveal protocol frozen in `qa/PTBXL_AFIB_IMAGE_BASELINE_V1.md`.
- Freeze record committed before reference access: `qa/results/PTBXL_NATURAL500_V2_AFIB_BASELINE_V1_FREEZE.json`, commit `aa6649785c6dad3d9daa3838c902d3136774d624`.
- Prediction freeze timestamp: `2026-10-03T00:07:32.888774Z`.
- Sealed reference revealed only afterwards: `2026-10-03T00:08:41.803705165Z`.
- Reference: 3 positive / 497 negative.
- Predictions: 46 positive / 359 negative / 93 abstain / 2 nondiagnostic.
- Classified counts: TP=3, FP=43, TN=359, FN=0.
- Coverage=0.81; abstention=0.186; nondiagnostic=0.004.
- Standard binary sensitivity/specificity/PPV/NPV/accuracy intentionally suppressed under v1.1 because unresolved cases exist.
- This result validates the blind/freeze/reveal mechanics and a simple image-derived engineering comparator only; it does not establish clinical performance.


## Phase 5 image infrastructure closure — 03/10/2026
- Clinical QA run #338: **SUCCESS**.
- Unified QA: `automated_status: PASS`.
- Unit regression suite: **Ran 175 tests ... OK**.
- RSNA ICH DICOM render frozen: WW=80 HU / WL=40 HU, HU slope/intercept, IOP/IPP ordering and fail-closed study/series integrity.
- CheXpert/MIMIC-CXR visual-input protocol frozen with no diagnosis-dependent enhancement.
- EchoNet visual protocol frozen with native video or deterministic 32-frame uniform sampling.
- Source-level versus actual-access status is explicitly separated.
- Full closure/status: `qa/PHASE5_IMAGE_CLOSURE.md`.


## Toxicology high-risk structured clinical QA — 03/10/2026
- Existing IDs audited: `toxicology` and `anticoagulation-reversal`; no duplicate module added.
- **24/24 structured high-risk regression cases PASS**: cocaine/sympathomimetic toxicity, sodium-channel blockade/TCA, digoxin, organophosphate, acute and repeated acetaminophen, methanol/ethylene glycol, beta-blocker/CCB shock, cyanide, dabigatran, apixaban, rivaroxaban, UFH, enoxaparin, fondaparinux, edoxaban, argatroban/bivalirudin, superwarfarin, warfarin, benzodiazepine/flumazenil safety and sulfonylurea/octreotide.
- Evidence anchors: AHA poisoning update 2023; 2023 US/Canada acetaminophen consensus; current EMA Praxbind and Ondexxya product information; toxin-specific EXTRIP where applicable.
- These are documented clinical regression cases, **not** Python-unit-test executions or prospective clinical validation. Toxicology/reversal remain yellow pending CIAV/INFARMED/local formulary/stock and human toxicology/hematology/pharmacy review.
- Detailed bank: `qa/TOXICOLOGY_HIGH_RISK_QA_2026-10-03.md`.


## Clinical Scores & Calculators registry — 03/10/2026
- Added one cross-cutting module ID: `clinical-scores-calculators` (127 -> 128); no score/formula duplicated as a module.
- Canonical registry: **134 active scales** (CORE/SPECIALIST) and **45 formulas**.
- Each registry entry contains name, domain, tier, what it measures, intended use, calculation type and editable flag.
- Central formula engine added at `scripts/clinical_calculator.py`; it performs arithmetic only and fails closed when required inputs are missing.
- Complex decision rules (e.g. PECARN, Duke-ISCVID) are represented as criteria/classification tools rather than artificial numeric scores.
- NEWS2 is marked as an official-table implementation and must not be modified from the RCP table.
- Phoenix pediatric sepsis is the contemporary pediatric sepsis definition anchor; SIRS is retained only as contextual/specialist physiology, not the active pediatric sepsis definition.
- This is structural/calculation infrastructure, not prospective validation. Registry remains yellow pending source-by-source verification, unit-regression coverage and clinician review.


## Clinical Scores & Calculators structural audit — 03/10/2026
- Direct repository audit: 134/134 unique scale IDs; 45/45 unique formula IDs.
- Manifest: 128 module IDs; `clinical-scores-calculators` resolves to its bundle.
- Evidence registry: 128 records; new module has evidence entry.
- Core routing IDs present: NIHSS, ABCD2, HEART, Wells-PE, PERC, PESI, SOFA, NEWS2, GCS, Phoenix Sepsis and PECARN head injury.
- Added 7 regression tests in `tests/test_clinical_scores_registry.py` plus manifest-cardinality update to 128.
- No GitHub Actions run was observed for the final commit at the time of this audit; therefore these new tests are **not yet recorded as PASS**.


## Pre-branch calculator consolidation — 03/10/2026
- Router regression repaired: score routes resolve through `clinical-scores-calculators`.
- Central formula engine completed: **45/45 registered formulas implemented**.
- CKD-EPI 2021, alveolar gas/A-a, Devine IBW, final concentration, DO2 and guarded legacy MELD-Na added with regression coverage.
- Scale execution remains fail-closed: generic component sums require explicit pre-scored components; raw clinical findings are not converted to score points without dedicated source-validated logic.
- Clinical QA run #356: **178/178 tests PASS**, `automated_status: PASS`.
- Pre-branch audit: `qa/PREBRANCH_AUDIT_V1.36.md`.


## v1.37 CORE scores — milestone 1 — 03/10/2026
- 14/93 CORE source-encoded or validated official wrapper.
- Dedicated deterministic rules added for NIHSS, GCS, NEWS2, SOFA-1, HEART, CHA2DS2 variants, Wells PE, PERC, YEARS, GBS, CURB-65 and Phoenix.
- GRACE 2.0 intentionally remains a validated wrapper to the official calculator; no local approximation of revised non-linear probabilities.
- Boundary/safety regressions include NIHSS 0/42/UN, GCS NT, NEWS2 Scale 2 authorization, SOFA 0/24, HEART 0/10, PERC low-pretest gate, YEARS FEU thresholds, GBS 0/23, CURB-65 0/5 and Phoenix sepsis/shock.
- Clinical QA run #369: **195/195 tests PASS**, `automated_status: PASS`.


## SOFA-2 — 03/10/2026
- Added as separate CORE score `sofa-2`; SOFA-1 remains `sofa`.
- Implements the six 0-4 domains from JAMA 2025: brain, respiratory, cardiovascular, liver, kidney, hemostasis.
- Contemporary support variables are explicit and never inferred from free text.
- Boundary regressions cover 0/24 and intermediate organ-support thresholds.
- Clinical QA run #375: **198/198 tests PASS**, `automated_status: PASS`.


## v1.37 CORE scores complete — 03/10/2026
- Calculator registry: **135 scales / 45 formulas**.
- CORE: **94/94 implemented**, 0 pending.
- SPECIALIST: 41 pending.
- Clinical QA run #422: **262/262 tests PASS**, `automated_status: PASS`.
- Final CORE blocks added and boundary-tested:
  - Bishop; NNUH-MEOWS v7; adult Rule of Nines; age-adjusted Lund-Browder.
  - Bedside PEWS; Pediatric Trauma Score; SIPA.
  - FLACC; authorized Wong-Baker FACES wrapper.
  - PRAM; Westley Croup.
  - Clinical Dehydration Scale; Pediatric Appendicitis Score.
  - PECARN Head Injury; PECARN Febrile Infant 2019; Step-by-Step.
  - APGAR.
- Safety/version gates remain explicit: institutional MEOWS/PEWS variants are not silently mixed; copyrighted Wong-Baker artwork is not reproduced; PECARN/Step-by-Step age/applicability boundaries are enforced.
- Canonical detail: `qa/V1.37_SCORES_VALIDATION_STATE.md`.


## v1.37 SPECIALIST scores complete — 03/10/2026
- All **41/41 SPECIALIST** scales are now source-encoded, official-wrapper validated, or delegated to a canonical central formula.
- Registry total: **135 scales (94 CORE + 41 SPECIALIST) + 45 formulas**.
- Pending scale implementations: **0**.
- Last code QA: Clinical QA #442 — **289/289 tests PASS**, `automated_status: PASS`.
- High-risk or licensed/external tools preserve explicit boundaries rather than approximating unavailable algorithms.
- Human review remains required before any yellow module is promoted clinically.
