## v1.44 cobertura pediátrica ampliada — 14/10/2026

89/89 regímenes, 1061/1061 escenarios de navegador y 89 exports JSON PASS; los 73 regímenes sin prueba específica ya están cubiertos. Corregidos selector E2E, frecuencia numérica de dispositivos según banda canónica y selección de volumen en fixtures límite. Build PASS; Clinical QA 7/7 y 568 Python PASS. Evidencia en qa/V1.44_PEDIATRIC_BROWSER_COMPLETION.md. Seis grupos sin flujo completo: qa/V1.44_PHARMACOLOGY_GAPS.md. v1.44 ABIERTA / CLINICALLY_PENDING; sin promoción de evidencia.

## v1.44 verificación final del bloque — 13/10/2026

Verificación final del código 1c343a91fbc7223a89cf24a9fcc21a6d193fd54e: 567 Python, 370 frontend, Clinical QA 7/7, lint/typecheck/build y diff-check PASS. D E2E: 40 adultos y 22 pediátricos PASS. P0/P1 nuevos no confirmados; P2 cobertura pendiente y flujos ausentes; P3 localización/avisos heredados. Main/RC1/v1.43 intactos, sin merge/push/promociones. Graphify local sin seguimiento. v1.44 ABIERTA/CLINICALLY_PENDING.

## v1.44 bloque D verificado — 13/10/2026

D completado: 40 cálculos adultos E2E (17 fármacos, 26 preparaciones) y 22 escenarios pediátricos (16 regímenes, siete exports JSON y 15 rechazos esperados) PASS. Correcciones solo del conductor E2E: unidad del ejemplo y selector hepático. 73 regímenes sin caso específico de navegador; seis grupos piloto sin flujo farmacológico completo. Sin cambios clínicos ni promociones. v1.44 ABIERTA/CLINICALLY_PENDING; informe qa/V1.44_FUNCTIONAL_VALIDATION.md.

## v1.44 cierre parcial — 13/10/2026

A/B/C completados en 1b53039/1704cec/400999c. 13 scores, export pediatrico en cuatro formatos y 196 fichas + 4 alias PASS. QA local final: 567 Python, 370 frontend, 7/7 Clinical QA, lint/typecheck/build PASS. D: 17 farmacos, 26 preparaciones, 40 casos Python PASS; nuevo E2E NO EJECUTADO por fallo de revision automatica (cuota). D/documentacion sin commit. v1.44 ABIERTA, CLINICALLY_PENDING. Ver qa/V1.44_FUNCTIONAL_VALIDATION.md.

## v1.44 bloque C — 13/10/2026

Bloque C: 196/196 fichas completas (186 incorporadas), 4 alias sin duplicacion, 16 familias. Componentes genericos y proyeccion literal del JSON canonico; STOP, confirmacion y fuentes visibles. Rescate/escalada solo donde existen. 209 pruebas frontend de procedimientos, 9 pruebas Node de fidelidad, 196 rutas + 4 alias en Edge PASS; lint/typecheck/build PASS. Sin imagenes nuevas, sin cambios de evidencia. CLINICALLY_PENDING.

## v1.44 bloque B — 13/10/2026

Bloque B: exportacion pediatrica JSON/PDF/DOCX e impresion desde snapshot canonico, invalidada al editar. Tres casos (paracetamol, dexametasona, rizatriptan), fidelidad de todos los campos, Unicode y 4-5 paginas PASS; 40 kg sigue bloqueado. 566 tests Python PASS; build/typecheck y lint PASS. Sin nuevas pautas ni promocion. CLINICALLY_PENDING.

## v1.44 — interactive score forms

13 formularios prioritarios conectados al motor canónico; 135 escalas / 45 fórmulas inventariadas, 122 escalas sin formulario en backlog. 54 tests API, 182 frontend (5 nuevos), 13 escenarios reales de navegador normal/boundary/reset PASS; lint/typecheck/build PASS. GRACE conserva wrapper oficial. Bloques B/C/D pendientes; CLINICALLY_PENDING.

## v1.44 — expand functional evidence without production changes
- After five pilots, execute 20 canonical synthetic expectations through engine/API and 16 through real UI/JSON export. Verify representative PDF/DOCX downloads and four browser-print guides.
- Add regressions for duplicate ECG, empty note, invalid export format and combined procedure filters. Fresh results: 509 Python, 177 frontend, Clinical QA 7/7, lint/typecheck/build, 12 fidelity checks PASS.
- Keep scores UI, pediatric export and remaining coverage gaps explicit; phase OPEN/CLINICALLY_PENDING.

## v1.44 — synthetic functional validation opening
- Freeze v1.43 at 737bb1b8dce5ffbdb296bb0c99d134ea318c8298; open separate branch. Define 20 traceable fixtures and execute five pilots before expansion.
- Add engine/API/export and real-browser expectation checks; production code and clinical evidence unchanged.

## v1.43 — formal UI/UX closure, 2026-10-12
- Add qa/V1.43_UI_UX_FINAL.md with scope, priorities, remaining limits and fresh validation (176 frontend, 505 Python, 7 QA checks, 12 fidelity tests, typecheck/build).
- Documentation only; canonical clinical content and evidence statuses unchanged. CLINICALLY_PENDING.

## v1.43 — clinical UI/UX audit and limited procedure pilot
- Preserve technical RC1 at 0fa17bf and begin v1.43-clinical-ui-validation from that exact clean baseline; record screenshots before changes.
- Put drug precautions and expanded source rules before calculation; add clinical navigation, accessible labels, touch target sizes and mobile guide-grid wrapping.
- Add searchable 196-procedure catalog with alias/family/level support and ten source-preserving pilot layouts. Keep shared preambles, STOP/confirmation, pending rescue/escalation and YELLOW. No approved visual assets exist; do not invent or promote them.
- Provide pediatric section navigation, focus/announcement and primary arithmetic display without changing API values, gates or clinical logic.
- Add fifteen exclusively synthetic UI cases and loopback browser checks; retain explicit limits for textual scores, 186 non-pilot references and prospective clinical validation.
- See qa/V1.43_UI_UX_AUDIT.md for current verification and gallery. Main/RC1 unchanged; no merge/push.

## v1.42 RC1 — resolve SP-002 from history and freeze technical baseline
- Establish canonical identity as Medición de presión compartimental from explicit normalization 9e50ffc, evidence alignment b679f19 and review coverage 08bbe958; preserve the procedure body and all YELLOW states.
- Reproduce two Python failures and one frontend failure (5427050), then align both indexes and regenerate the structured JSON and frontend catalog (82e6ca9). No new IDs, clinical technique, dose or visual asset.
- New execution: 505 Python, Clinical QA 7/7, 163 frontend, lint/typecheck/build, 12 Node fidelity checks, four browser PDFs and four pediatric API scenarios PASS. Prior 503/162 results remain historical.
- Technical P0/P1 open = 0 in audited scope; prospective validation, local evidence and P2/P3 remain pending. Local RC only, no merge/push. See qa/V1.42_RC1_FREEZE.md and qa/V1.42_SP002_IDENTITY_REVIEW.md.

## Historical audit before SP-002 repair

## v1.42 consolidation — global technical audit (clinical release blocked)
- Complete all 196 source-preserving procedure JSON files across 16 families; preserve four aliases, 43 explicit rescue/153 pending and 55 explicit escalation/141 pending. All remain YELLOW.
- Reproduce and correct two erroneous GREEN guide statuses to the existing YELLOW evidence state; add fidelity regression and evidence-registry CI trigger. Separate test/fix commits preserve traceability.
- Derive global inventory and reconcile continuity documents, keeping historical snapshots. Record unresolved P1 title/content mismatch in PROC-SP-002 and P2 nomenclature review in PROC-SP-003; do not change clinical text.
- Reproduce and separately fix 11 lint errors without changing clinical behavior. Local QA: 503 Python, 162 frontend, lint/typecheck/build, 12 Node checks, four browser PDFs and four pediatric API/browser scenarios PASS. Remote Actions pending; no prospective validation.
- See `qa/V1.42_FINAL_AUDIT.md`, `qa/V1.42_INVENTORY.json` and the migration report. No main change, merge, push, dependency upgrade or automatic evidence promotion.

## Historical block entries

The entries below preserve the status and test counts observed when each block was performed.

## v1.42 consolidation — source-preserving procedure migration foundation (historical; now complete)
- Inventory 196 canonical procedures, four aliases and 16 families from local HEAD; 26 legacy JSON files validate v1.41 but diverge from textual source projections.
- Add versioned source-preserving schema, deterministic extractor, literal safety excerpt register and real JSON Schema/fidelity invariants. Preserve unresolved rescue/escalation as null plus pending review; do not infer clinical subcategories or evidence metadata.
- See `qa/V1.42_PROCEDURE_STRUCTURED_MIGRATION.md` for family progress and limits. Canonical text, statuses and visual layer unchanged.

## v1.42 consolidation — pediatric contracts and canonical frontend (YELLOW)
- Reconcile three synthetic outpatient fixtures with existing clinical gates; 18/18 expectations pass, including continued blocking at exactly 40 kg for the RCH rizatriptan regimen.
- Share strict finite-number validation across affected pediatric calculators; reject malformed types, nonfinite input/output, zero divisors and overflow hidden by dose caps.
- Generate 89 outpatient regimens in 52 drug/combination groups from the canonical registry/rules. Add a diagnosis-specific form and thin API using the existing calculator; preserve source limits, alerts and stale-response/catalog checks. The former 17-drug frontend catalog is adult-only and unchanged.
- Add 15 Python and nine frontend tests plus four actual browser/backend scenarios. Clinical QA 7/7, 493 unique Python tests, frontend 162, typecheck/build and browser checks PASS locally. Remote Actions pending.
- See `qa/V1.42_PEDIATRIC_CONSOLIDATION.md` for inventory definitions, source discrepancies and limits. No clinical regimen, evidence-status, procedure migration or visual changes; no merge/push.

## v1.42 consolidation — CI coverage and complete procedure catalog (YELLOW)
- Cover v1.x pushes, PRs and clinical input paths in Clinical/UI QA; install declared Python runtime/test requirements and run canonical-artifact and browser-PDF checks.
- Discover all Python suites once, including scores and evidence, preserving structural validators and clinical release gates. Keep surveillance mutation guards; avoid duplicate push/PR regression jobs.
- Generate 196 canonical procedures and four direct aliases from the textual index and 16 family files. Preserve canonical source paths/headings; general related-procedure suggestions no longer use the filtered 158-item visual catalog.
- Add six CI regressions, eight Node generator tests and eight frontend catalog/resolution tests. Clinical QA 7/7 with 478 unique tests, frontend 153, typecheck/build and four browser PDFs PASS locally. Six workflows parse and pass actionlint; remote Actions execution pending.
- See `qa/V1.42_CI_PROCEDURE_CATALOG.md`. No clinical source edits, evidence promotion, visual work, merge or push.

## v1.42 consolidation — Unicode export and canonical safety preambles (YELLOW)
- Replace lossy CP1252 PDF output with ReportLab and bundled libre DejaVu fonts; preserve clinical symbols, escape paragraph markup and fail explicitly on missing glyphs before writing output.
- Derive shared preamble and exact module section from canonical bundles; assemble once for library/print. Include full canonical content for all three quick algorithms. Handle CRLF and exact heading boundaries.
- Add Unicode, 131-module fidelity, DOM and real browser PDF regressions. Local Clinical QA 12/12 PASS (419 main tests); frontend 145 PASS, typecheck/build PASS, including previous asynchronous-response tests.
- See `qa/V1.42_UNICODE_SAFETY_PREAMBLE.md` and Python requirements. CI dependency installation remains pending/out of scope. No clinical recommendation or evidence-status changes.

## v1.42 consolidation — diagnostic context and request sequencing (YELLOW)
- Filter locally negated and historical/resolved textual mentions, preserving current positive mentions and explicit negative rule criteria. History fields require per-trigger `allow_historical: true`; existing weights, thresholds and rules are unchanged.
- Bind diagnostic responses/errors to note revision and monotonic request ID; allow a new analysis after editing and discard obsolete responses.
- Add 10 Python regressions (PASS) and five frontend cases (NOT RUN: local Vitest dependencies missing). Existing 60 diagnostic scenarios and 12 Clinical QA checks PASS; main suite 416 tests.
- Record limits in `qa/V1.42_DIAGNOSTIC_CONTEXT_SEQUENCING.md`. No evidence promotion or clinical recommendation change.

## v1.42 consolidation — clinical-note input/privacy/acceptance (YELLOW)
- Inspect scalar text in nested lists and privacy notes without duplicate visits.
- Enforce the existing note schema at runtime, strict booleans, finite numbers, valid ages and structured fields; reject malformed upload acknowledgements, edits and provider responses before use.
- Preserve signed findings, impression and limitations on omission; retain original/accepted values and actual edits in optional server-generated `acceptance_provenance` v1.0. Existing prepared-upload HMAC and source hashes are unchanged.
- Add 30 targeted regressions; existing v1.39 tests and local Clinical QA pass. See `qa/V1.42_P1_INPUT_PRIVACY_ACCEPTANCE.md` for limits and deferred findings. No evidence promotion or clinical recommendation change.

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
