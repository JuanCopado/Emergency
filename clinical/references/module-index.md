<!-- Sodium clinical referenceGREEN2026-11-14;owner preparation/fluids reconfirmed;113GREEN/18YELLOW; ../qa/SODIUM_CLINICAL_REFERENCE_CLOSURE_2026-11-14.json;mapping unchanged. -->
<!-- Nine selected review2026-11-14:2GREEN/7YELLOW retained;112GREEN/19YELLOW; ../qa/NINE_SELECTED_MODULES_REVIEW_2026-11-14.json; mappings unchanged. -->
<!-- Next10 owner-selected modules reviewed2026-11-14:110GREEN/21YELLOW; ../qa/NEXT_TEN_PEDIATRIC_ADULT_REVIEW_2026-11-14.json;131 mappings retained. -->
<!-- TBI biomarker/CBI-M and eight pediatric modules reviewed2026-11-14;100GREEN/31YELLOW; ../qa/TBI_AND_EIGHT_PEDIATRIC_REVIEW_2026-11-14.json;131 mappings retained. -->
<!--Owner local Empressin1IU/mL and handling clarification2026-11-14; ../qa/LOCAL_INFUSION_DECISIONS_2026-11-14.json; no mappings/status promotions.-->
<!--17 product/preparation sheets reconciled2026-11-14; ../qa/INFUSION_PRODUCT_RECONCILIATION_2026-11-14.json; both infusion modules remainYELLOW,mappings unchanged. -->
<!-- Ten shock/infusion/pediatric-support references reviewed2026-11-14:8GREEN/2YELLOW; ../qa/TEN_SHOCK_INFUSION_PEDIATRIC_SUPPORT_REVIEW_2026-11-14.json; no mappings or blocked contracts changed. -->
<!-- Ten syncope/pediatric/resuscitation references reviewed2026-11-14; ../qa/TEN_SYNCOPE_PEDIATRIC_RESUSCITATION_REVIEW_2026-11-14.json; local operational gates and19 blocked contracts retained; mappings unchanged. -->
<!-- Five adult frameworks GREEN2026-11-14; ../qa/PSYCHIATRY_IMAGING_CHEST_DISPOSITION_EYE_REVIEW_2026-11-14.json; musculoskeletal image accuracy remains unvalidated and broader image gate unchanged; mappings preserved. -->
<!-- Eight adult umbrella/safety modules GREEN2026-11-14 by owner-requested validation; ../qa/EIGHT_UMBRELLA_REVIEW_2026-11-14.json; child/individual procedure states and mappings unchanged. -->
<!-- Abdomen and musculoskeletal pain GREEN2026-11-14 by explicit owner request; ../qa/ABDOMEN_MUSCULOSKELETAL_REVIEW_2026-11-14.json; mappings unchanged. -->
<!-- Delirium, alcohol-withdrawal and altered-consciousness GREEN2026-11-14; ../qa/DELIRIUM_WITHDRAWAL_CONSCIOUSNESS_REVIEW_2026-11-14.json; mappings unchanged. -->
<!-- DVT GREEN2026-11-14 by explicit owner request; ../qa/DVT_REVIEW_AND_GREEN_2026-11-14.json; mapping unchanged. -->
<!-- Sodium mixture arithmetic verified2026-11-14; ../qa/SODIUM_20PCT_MIXTURE_VERIFICATION_2026-11-14.json; no status/mapping change. -->
<!-- Sodium preparation owner follow-up2026-11-14: nursing staff, recipe pending; ../qa/SODIUM_PREPARATION_FOLLOWUP_2026-11-14.json; mapping unchanged. -->
<!-- Acid-base/sodium reviewed2026-11-13, remain YELLOW; ../qa/ACID_BASE_SODIUM_REVIEW_2026-11-13.json; mappings unchanged. -->
<!-- TBI, NIV and calcium/magnesium GREEN2026-11-13; ../qa/TBI_NIV_CALCIUM_MAGNESIUM_RECONCILIATION_2026-11-13.json; mappings unchanged. -->
<!-- Three accepted circuits GREEN2026-11-13; ../qa/HEMOPTYSIS_RESPIRATORY_LIVER_OWNER_ACCEPTANCE_2026-11-13.json; mappings unchanged. -->
<!-- Reversal generic PCC and circuit GREEN2026-11-13; ../qa/REVERSAL_GENERIC_PCC_OWNER_ACCEPTANCE_2026-11-13.json; mapping unchanged. -->
<!-- Status local acceptance and adult AES IM contract reconciled2026-11-13; ../qa/STATUS_OWNER_ACCEPTANCE_AND_MIDAZOLAM_FIX_2026-11-13.json; ID mapping unchanged. -->
<!-- Obstetric circuit owner-accepted GREEN2026-11-13; ../qa/OBSTETRIC_OWNER_CIRCUIT_GREEN_2026-11-13.json; mapping unchanged. -->
<!-- Toxicology rare products and trauma GREEN2026-11-13; see ../qa/TOXICOLOGY_RARE_PRODUCTS_REVIEW_2026-11-13.md; mappings unchanged. -->
<!-- Anafilaxia GREEN aceptada; marco antibiótico GREEN 2026-11-13: ../qa/ANAPHYLAXIS_ANTIBIOTICS_ACCEPTANCE_2026-11-13.json; mappings unchanged. -->
<!-- Second10 overdue source review2026-11-13: ../qa/NEXT_TEN_OVERDUE_REVIEW_2026-11-13.md; ID mappings unchanged. -->
<!-- First ten overdue review 2026-11-13: ../qa/FIRST_TEN_OVERDUE_REVIEW_2026-11-13.md; mappings unchanged. -->
<!-- Six-source reconciliation 2026-11-13: see ../qa/SIX_EVIDENCE_RECONCILIATIONS_2026-11-13.md; IDs and bundle mapping unchanged. -->
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

# v1.44 scores interactivos

13 formularios prioritarios conectados al motor canónico; 135 escalas / 45 fórmulas inventariadas, 122 escalas sin formulario en backlog. 54 tests API, 182 frontend (5 nuevos), 13 escenarios reales de navegador normal/boundary/reset PASS; lint/typecheck/build PASS. GRACE conserva wrapper oficial. Bloques B/C/D pendientes; CLINICALLY_PENDING.

# v1.44 expanded functional evidence

20 engine/API and 16 real-browser note cases PASS; see `qa/V1.44_FUNCTIONAL_VALIDATION_MATRIX.md`. No module IDs, routes, clinical bodies or evidence status changes. Functional coverage remains partial; phase open.

# v1.44 functional validation

See `qa/V1.44_FUNCTIONAL_VALIDATION.md` and its matrix. No new modules, clinical IDs, routing or source changes.

# Formal v1.43 closure

See `qa/V1.43_UI_UX_FINAL.md`. No IDs, routing, clinical bodies or evidence statuses changed in the closure.

# UI/UX continuity v1.43

See `qa/V1.43_UI_UX_AUDIT.md`: 131 module IDs, routes and evidence statuses unchanged. New frontend procedure navigation and ten layouts read existing canonical artifacts directly; synthetic DEMO cases are UI fixtures, not evidence cases or new clinical modules.

# Module manifest v1.42 consolidation

v1.42 continuity: module IDs and routing are unchanged. Clinical-note runtime input/privacy/acceptance hardening is documented in `qa/V1.42_P1_INPUT_PRIVACY_ACCEPTANCE.md`; its evidence status remains YELLOW.

v1.42 diagnostic context and response sequencing: see `qa/V1.42_DIAGNOSTIC_CONTEXT_SEQUENCING.md`. No module/routing or evidence-status changes. Its pending frontend tests passed locally on 2026-10-09.

v1.42 Unicode and shared safety preambles: see `qa/V1.42_UNICODE_SAFETY_PREAMBLE.md`. All 131 generated guides preserve canonical preamble and section; no module or evidence promotion.

v1.42 CI and procedure catalog: see `qa/V1.42_CI_PROCEDURE_CATALOG.md`. The frontend catalog derives 196 canonical procedures plus four aliases from the textual index and 16 families; no module IDs, routing, clinical text or evidence statuses changed.

v1.42 pediatric consolidation: see `qa/V1.42_PEDIATRIC_CONSOLIDATION.md`. Finite arithmetic, existing safety gates and 89-regimen canonical frontend validated locally; no module IDs, routing or evidence statuses changed.

v1.42 procedure structural migration: see `qa/V1.42_PROCEDURE_STRUCTURED_MIGRATION.md` for source-preserving JSON coverage and pending clinical classification. No module/routing changes or evidence promotion.

v1.42 final audit: `qa/V1.42_FINAL_AUDIT.md`; generated inventory `qa/V1.42_INVENTORY.json`. 196 structured procedures complete; SP-002 identity P1 resolved (82e6ca9); technical RC gate evaluated in qa/V1.42_RC1_FREEZE.md. Clinical source/status dates unchanged.

Read only the bundles required by `router.md`. Within a bundle, locate the exact
heading `## <module-id>`. Every routed ID must resolve here and in its target
bundle; `scripts/validate_modules.py` enforces that invariant.

| Module ID | Bundle |
|---|---|
| clinical-image-interpretation | `modules/clinical-images.md` |
| musculoskeletal-xray | `modules/image-modalities.md` |
| chest-xray | `modules/image-modalities.md` |
| pocus-image | `modules/image-modalities.md` |
| ecg-image | `modules/image-modalities.md` |
| blood-gas-image | `modules/image-modalities.md` |
| skin-wound-image | `modules/image-modalities.md` |
| ct-mri-screenshot | `modules/image-modalities.md` |
| ophthalmology-image | `modules/image-modalities.md` |
| other-clinical-image | `modules/image-modalities.md` |
| acute-ischemic-stroke | `modules/neurologic.md` |
| spontaneous-intracerebral-hemorrhage | `modules/neurologic.md` |
| acute-coronary-syndrome | `modules/cardiovascular.md` |
| pulmonary-embolism | `modules/cardiovascular.md` |
| sepsis-shock | `modules/infection-respiratory.md` |
| airway-rsi | `modules/procedures-pharmacology.md` |
| pediatric-airway-rsi | `modules/procedures-pharmacology.md` |
| arrhythmias-cardiac-arrest | `modules/cardiovascular.md` |
| adult-arrhythmias | `modules/cardiovascular.md` |
| adult-cardiac-arrest | `modules/cardiovascular.md` |
| undifferentiated-shock | `modules/cardiovascular.md` |
| electrolytes | `modules/renal-metabolic.md` |
| sodium-emergencies | `modules/renal-metabolic.md` |
| potassium-emergencies | `modules/renal-metabolic.md` |
| calcium-magnesium-emergencies | `modules/renal-metabolic.md` |
| sedoanalgesia | `modules/procedures-pharmacology.md` |
| icu-sedation-analgesia-infusions | `modules/procedures-pharmacology.md` |
| empiric-antibiotics | `modules/procedures-pharmacology.md` |
| anaphylaxis | `modules/infection-respiratory.md` |
| toxicology | `modules/renal-metabolic.md` |
| pediatric-emergencies | `modules/special-populations.md` |
| pediatric-procedural-sedation | `modules/special-populations.md` |
| pediatric-acute-respiratory-support | `modules/special-populations.md` |
| pediatric-cns-infection | `modules/special-populations.md` |
| pediatric-dka | `modules/special-populations.md` |
| pediatric-sepsis | `modules/special-populations.md` |
| pediatric-hematology-oncology-emergencies | `modules/special-populations.md` |
| pediatric-drowning-hypothermia | `modules/special-populations.md` |
| pediatric-foreign-body-emergencies | `modules/special-populations.md` |
| pediatric-hypertensive-emergency | `modules/special-populations.md` |
| pediatric-major-trauma | `modules/special-populations.md` |
| pediatric-head-injury | `modules/special-populations.md` |
| pediatric-abdominal-surgical-emergencies | `modules/special-populations.md` |
| pediatric-adrenal-crisis | `modules/special-populations.md` |
| pediatric-burns | `modules/special-populations.md` |
| pediatric-toxicology | `modules/special-populations.md` |
| pediatric-acute-asthma | `modules/special-populations.md` |
| pediatric-emergency-medications | `modules/special-populations.md` |
| pediatric-outpatient-medications | `modules/special-populations.md` |
| pediatric-iv-fluid-therapy | `modules/special-populations.md` |
| pediatric-electrolyte-emergencies | `modules/special-populations.md` |
| pediatric-blood-transfusion-major-hemorrhage | `modules/special-populations.md` |
| febrile-infant-0-90-days | `modules/special-populations.md` |
| bronchiolitis | `modules/special-populations.md` |
| croup | `modules/special-populations.md` |
| pediatric-dehydration-shock | `modules/special-populations.md` |
| pediatric-shock | `modules/special-populations.md` |
| pediatric-arrhythmias | `modules/special-populations.md` |
| pediatric-cardiac-arrest | `modules/special-populations.md` |
| pediatric-status-epilepticus | `modules/special-populations.md` |
| trauma-major-hemorrhage | `modules/trauma-surgical.md` |
| major-burns | `modules/trauma-surgical.md` |
| smoke-inhalation-toxic-injury | `modules/trauma-surgical.md` |
| obstetric-emergencies | `modules/special-populations.md` |
| hypertensive-emergencies | `modules/cardiovascular.md` |
| iv-antihypertensive-selection | `modules/cardiovascular.md` |
| acute-respiratory-failure | `modules/infection-respiratory.md` |
| acute-severe-asthma | `modules/infection-respiratory.md` |
| copd-exacerbation | `modules/infection-respiratory.md` |
| life-threatening-hemoptysis | `modules/infection-respiratory.md` |
| oxygen-therapy-emergency | `modules/infection-respiratory.md` |
| high-flow-nasal-oxygen | `modules/infection-respiratory.md` |
| noninvasive-ventilation | `modules/infection-respiratory.md` |
| tension-pneumothorax | `modules/infection-respiratory.md` |
| observation-discharge | `modules/disposition-crosscutting.md` |
| status-epilepticus | `modules/neurologic.md` |
| altered-consciousness | `modules/neurologic.md` |
| headache-sah | `modules/neurologic.md` |
| cns-infection | `modules/neurologic.md` |
| traumatic-intracranial-mass-effect | `modules/neurologic.md` |
| acute-spinal-cord-compression | `modules/neurologic.md` |
| cauda-equina-conus-emergency | `modules/neurologic.md` |
| upper-gi-bleeding | `modules/trauma-surgical.md` |
| lower-gi-bleeding | `modules/trauma-surgical.md` |
| acute-mesenteric-ischemia | `modules/trauma-surgical.md` |
| acute-abdomen | `modules/trauma-surgical.md` |
| abdominal-aortic-aneurysm | `modules/trauma-surgical.md` |
| urologic-emergencies | `modules/renal-metabolic.md` |
| endocrine-metabolic | `modules/renal-metabolic.md` |
| adrenal-crisis | `modules/renal-metabolic.md` |
| thyroid-storm | `modules/renal-metabolic.md` |
| myxedema-coma | `modules/renal-metabolic.md` |
| diabetic-ketoacidosis-hhs | `modules/renal-metabolic.md` |
| acid-base-emergencies | `modules/renal-metabolic.md` |
| aki-nephrology | `modules/renal-metabolic.md` |
| rhabdomyolysis | `modules/renal-metabolic.md` |
| acute-liver-failure | `modules/renal-metabolic.md` |
| pancreatitis | `modules/trauma-surgical.md` |
| hematology-oncology | `modules/disposition-crosscutting.md` |
| anticoagulation-reversal | `modules/procedures-pharmacology.md` |
| medication-selection-safety | `modules/procedures-pharmacology.md` |
| ophthalmology-emergencies | `modules/disposition-crosscutting.md` |
| ent-emergencies | `modules/disposition-crosscutting.md` |
| dermatology-severe | `modules/infection-respiratory.md` |
| soft-tissue-infections | `modules/infection-respiratory.md` |
| orthopedic-emergencies | `modules/trauma-surgical.md` |
| acute-musculoskeletal-pain | `modules/trauma-surgical.md` |
| emergency-procedures | `modules/procedures-pharmacology.md` |
| geriatric-emergencies | `modules/special-populations.md` |
| delirium | `modules/special-populations.md` |
| syncope-falls-frailty | `modules/special-populations.md` |
| psychiatric-emergencies | `modules/special-populations.md` |
| suicide-risk | `modules/special-populations.md` |
| alcohol-withdrawal | `modules/renal-metabolic.md` |
| environmental-emergencies | `modules/disposition-crosscutting.md` |
| emergency-infectious-diseases | `modules/infection-respiratory.md` |
| non-coronary-chest-pain | `modules/cardiovascular.md` |
| acute-heart-failure | `modules/cardiovascular.md` |
| cardiogenic-shock | `modules/cardiovascular.md` |
| vasoactive-inotrope-infusions | `modules/cardiovascular.md` |
| acute-aortic-syndrome | `modules/cardiovascular.md` |
| cardiac-tamponade-pericardial-emergency | `modules/cardiovascular.md` |
| critical-valvular-disease | `modules/cardiovascular.md` |
| infective-endocarditis | `modules/cardiovascular.md` |
| dvt | `modules/cardiovascular.md` |
| device-complications | `modules/cardiovascular.md` |
| ecg-pocus-integration | `modules/disposition-crosscutting.md` |
| pocus | `modules/disposition-crosscutting.md` |
| clinical-scores-calculators | `modules/clinical-scores-calculators.md` |

| clinical-note-diagnostic-support | `modules/documentation-governance.md` |
| final-human-review-gate | `modules/documentation-governance.md` |
