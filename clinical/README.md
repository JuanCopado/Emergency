# Emergency Medicine Skill v1.35 — ICU/ED Continuous Infusions (draft)

106 module IDs. This ZIP is a v1.35 working copy based on the uploaded v1.26 package;
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


The v1.34 draft adds six shock, arrhythmia and cardiac-arrest routes, separating adult and pediatric rhythm/arrest care and preserving etiology-specific shock modules. It retains the shared prior route as a selector. Human review and Portugal/Azores local protocols remain pending. The v1.33 pediatric pathway additions are documented in CURRENT_STATE.md.

The v1.35 draft adds adult continuous-infusion references: `vasoactive-inotrope-infusions` and `icu-sedation-analgesia-infusions`, each with dilution, concentration, unit-tested 70 kg mL/h arithmetic and safety gates. Sources and unresolved discrepancies are in `updates/icu-infusions-review-2026-09-29.md`. Human review, Portuguese RCM/local protocol checks and pediatric infusions remain pending.
