## v1.44 conciliación de producto y protocolo — 17/10/2026

Revisión documental de seis grupos: 19 contratos permanentemente bloqueados,
18 perfiles de producto y 11 referencias de preparación separados en un dossier
no ejecutable. Ningún producto/protocolo local aprobado ni firma humana aportada:
0 PROFESSIONALLY_RECONCILED; gates y recomendaciones canónicas intactos.
Ver `qa/V1.44_MEDICATION_PRODUCT_PROTOCOL_RECONCILIATION.md` y el JSON asociado.
QA nueva y límites en `qa/product-reconciliation-v144/QA_RESULTS.json`;
los tests de futuros perfiles locales no implementados no se declaran PASS.
v1.44 ABIERTA / CLINICALLY_PENDING; no funcionalmente cerrable.

## v1.44 farmacología integrada — 16/10/2026

Seis grupos implementados con alcance explícito y revisión clínica pendiente.
58 escenarios / 46 contratos PASS: 39 calculables con cuatro formatos y 19
bloqueos verificados. 578 Python, Clinical QA 7/7, 376 frontend,
lint/typecheck/build y generadores deterministas PASS. Pediatría: 1061/1061,
89 regímenes y 89 JSON; exportación focal de cuatro formatos PASS.
Ver `qa/V1.44_ACUTE_FINAL_REVIEW.md` y matriz individual. v1.44 ABIERTA /
CLINICALLY_PENDING, ningún YELLOW promovido. Los límites de producto, protocolo
local y validación clínica impiden cierre funcional/clínico global.

# MODULES — índice verificado

Reconciliación 15/10/2026: trabajo pediátrico recuperado en commits separados; 1061/1061 escenarios de navegador, 89/89 regímenes y 89 exports JSON PASS; exportación focal JSON/PDF/DOCX/impresión PASS. Clinical QA 7/7, 568 Python, 370 frontend, lint/typecheck/build PASS. Inventario completo, ejecuciones interrumpidas conservadas, exclusiones locales sin borrados y procedencia en `qa/V1.44_WORKTREE_RECONCILIATION.md`. Seis flujos farmacológicos sin iniciar. v1.44 ABIERTA / CLINICALLY_PENDING; sin promoción de evidencia.

Actualización técnica 14/10/2026: pediatría ambulatoria 89/89 regímenes, 1061 escenarios de navegador y 89 exports JSON PASS. Registro: `qa/V1.44_PEDIATRIC_BROWSER_COMPLETION.md`. Evidencia YELLOW; v1.44 ABIERTA / CLINICALLY_PENDING, con seis flujos farmacológicos pendientes.

Estado v1.42 auditado el 10/10/2026: 131 IDs únicos, 29 GREEN / 102 YELLOW / 0 RED; todos tienen sección y registro. Inventario derivado en `qa/V1.42_INVENTORY.json`; límites y cierre técnico en `qa/V1.42_FINAL_AUDIT.md`.
El estado green/yellow corresponde al registro de evidencia, no a una declaración de validación clínica.

| ID | Archivo de módulos | Evidencia |
|---|---|---|
| `clinical-image-interpretation` | `modules/clinical-images.md` | yellow |
| `musculoskeletal-xray` | `modules/image-modalities.md` | yellow |
| `chest-xray` | `modules/image-modalities.md` | yellow |
| `pocus-image` | `modules/image-modalities.md` | yellow |
| `ecg-image` | `modules/image-modalities.md` | yellow |
| `blood-gas-image` | `modules/image-modalities.md` | yellow |
| `skin-wound-image` | `modules/image-modalities.md` | yellow |
| `ct-mri-screenshot` | `modules/image-modalities.md` | yellow |
| `ophthalmology-image` | `modules/image-modalities.md` | yellow |
| `other-clinical-image` | `modules/image-modalities.md` | yellow |
| `acute-ischemic-stroke` | `modules/neurologic.md` | green |
| `spontaneous-intracerebral-hemorrhage` | `modules/neurologic.md` | green |
| `acute-coronary-syndrome` | `modules/cardiovascular.md` | green |
| `pulmonary-embolism` | `modules/cardiovascular.md` | yellow |
| `sepsis-shock` | `modules/infection-respiratory.md` | green |
| `airway-rsi` | `modules/procedures-pharmacology.md` | green |
| `pediatric-airway-rsi` | `modules/procedures-pharmacology.md` | yellow |
| `arrhythmias-cardiac-arrest` | `modules/cardiovascular.md` | yellow |
| `adult-arrhythmias` | `modules/cardiovascular.md` | yellow |
| `adult-cardiac-arrest` | `modules/cardiovascular.md` | yellow |
| `undifferentiated-shock` | `modules/cardiovascular.md` | yellow |
| `electrolytes` | `modules/renal-metabolic.md` | yellow |
| `sodium-emergencies` | `modules/renal-metabolic.md` | yellow |
| `potassium-emergencies` | `modules/renal-metabolic.md` | green |
| `calcium-magnesium-emergencies` | `modules/renal-metabolic.md` | yellow |
| `sedoanalgesia` | `modules/procedures-pharmacology.md` | green |
| `icu-sedation-analgesia-infusions` | `modules/procedures-pharmacology.md` | yellow |
| `empiric-antibiotics` | `modules/procedures-pharmacology.md` | yellow |
| `anaphylaxis` | `modules/infection-respiratory.md` | yellow |
| `toxicology` | `modules/renal-metabolic.md` | yellow |
| `pediatric-emergencies` | `modules/special-populations.md` | yellow |
| `pediatric-procedural-sedation` | `modules/special-populations.md` | yellow |
| `pediatric-acute-respiratory-support` | `modules/special-populations.md` | yellow |
| `pediatric-cns-infection` | `modules/special-populations.md` | yellow |
| `pediatric-dka` | `modules/special-populations.md` | yellow |
| `pediatric-sepsis` | `modules/special-populations.md` | yellow |
| `pediatric-hematology-oncology-emergencies` | `modules/special-populations.md` | yellow |
| `pediatric-drowning-hypothermia` | `modules/special-populations.md` | yellow |
| `pediatric-foreign-body-emergencies` | `modules/special-populations.md` | yellow |
| `pediatric-hypertensive-emergency` | `modules/special-populations.md` | yellow |
| `pediatric-major-trauma` | `modules/special-populations.md` | yellow |
| `pediatric-head-injury` | `modules/special-populations.md` | yellow |
| `pediatric-abdominal-surgical-emergencies` | `modules/special-populations.md` | yellow |
| `pediatric-adrenal-crisis` | `modules/special-populations.md` | yellow |
| `pediatric-burns` | `modules/special-populations.md` | yellow |
| `pediatric-toxicology` | `modules/special-populations.md` | yellow |
| `pediatric-acute-asthma` | `modules/special-populations.md` | yellow |
| `pediatric-emergency-medications` | `modules/special-populations.md` | yellow |
| `pediatric-outpatient-medications` | `modules/special-populations.md` | yellow |
| `pediatric-iv-fluid-therapy` | `modules/special-populations.md` | yellow |
| `pediatric-electrolyte-emergencies` | `modules/special-populations.md` | yellow |
| `pediatric-blood-transfusion-major-hemorrhage` | `modules/special-populations.md` | yellow |
| `febrile-infant-0-90-days` | `modules/special-populations.md` | yellow |
| `bronchiolitis` | `modules/special-populations.md` | yellow |
| `croup` | `modules/special-populations.md` | yellow |
| `pediatric-dehydration-shock` | `modules/special-populations.md` | yellow |
| `pediatric-shock` | `modules/special-populations.md` | yellow |
| `pediatric-arrhythmias` | `modules/special-populations.md` | yellow |
| `pediatric-cardiac-arrest` | `modules/special-populations.md` | yellow |
| `pediatric-status-epilepticus` | `modules/special-populations.md` | yellow |
| `trauma-major-hemorrhage` | `modules/trauma-surgical.md` | yellow |
| `major-burns` | `modules/trauma-surgical.md` | green |
| `smoke-inhalation-toxic-injury` | `modules/trauma-surgical.md` | yellow |
| `obstetric-emergencies` | `modules/special-populations.md` | yellow |
| `hypertensive-emergencies` | `modules/cardiovascular.md` | yellow |
| `iv-antihypertensive-selection` | `modules/cardiovascular.md` | green |
| `acute-respiratory-failure` | `modules/infection-respiratory.md` | yellow |
| `acute-severe-asthma` | `modules/infection-respiratory.md` | green |
| `copd-exacerbation` | `modules/infection-respiratory.md` | green |
| `life-threatening-hemoptysis` | `modules/infection-respiratory.md` | yellow |
| `oxygen-therapy-emergency` | `modules/infection-respiratory.md` | green |
| `high-flow-nasal-oxygen` | `modules/infection-respiratory.md` | green |
| `noninvasive-ventilation` | `modules/infection-respiratory.md` | yellow |
| `tension-pneumothorax` | `modules/infection-respiratory.md` | green |
| `observation-discharge` | `modules/disposition-crosscutting.md` | yellow |
| `status-epilepticus` | `modules/neurologic.md` | yellow |
| `altered-consciousness` | `modules/neurologic.md` | yellow |
| `headache-sah` | `modules/neurologic.md` | green |
| `cns-infection` | `modules/neurologic.md` | green |
| `traumatic-intracranial-mass-effect` | `modules/neurologic.md` | yellow |
| `acute-spinal-cord-compression` | `modules/neurologic.md` | green |
| `cauda-equina-conus-emergency` | `modules/neurologic.md` | green |
| `upper-gi-bleeding` | `modules/trauma-surgical.md` | yellow |
| `lower-gi-bleeding` | `modules/trauma-surgical.md` | yellow |
| `acute-mesenteric-ischemia` | `modules/trauma-surgical.md` | yellow |
| `acute-abdomen` | `modules/trauma-surgical.md` | yellow |
| `abdominal-aortic-aneurysm` | `modules/trauma-surgical.md` | green |
| `urologic-emergencies` | `modules/renal-metabolic.md` | green |
| `endocrine-metabolic` | `modules/renal-metabolic.md` | yellow |
| `adrenal-crisis` | `modules/renal-metabolic.md` | green |
| `thyroid-storm` | `modules/renal-metabolic.md` | yellow |
| `myxedema-coma` | `modules/renal-metabolic.md` | yellow |
| `diabetic-ketoacidosis-hhs` | `modules/renal-metabolic.md` | green |
| `acid-base-emergencies` | `modules/renal-metabolic.md` | yellow |
| `aki-nephrology` | `modules/renal-metabolic.md` | yellow |
| `rhabdomyolysis` | `modules/renal-metabolic.md` | green |
| `acute-liver-failure` | `modules/renal-metabolic.md` | yellow |
| `pancreatitis` | `modules/trauma-surgical.md` | green |
| `hematology-oncology` | `modules/disposition-crosscutting.md` | yellow |
| `anticoagulation-reversal` | `modules/procedures-pharmacology.md` | yellow |
| `medication-selection-safety` | `modules/procedures-pharmacology.md` | yellow |
| `ophthalmology-emergencies` | `modules/disposition-crosscutting.md` | yellow |
| `ent-emergencies` | `modules/disposition-crosscutting.md` | yellow |
| `dermatology-severe` | `modules/infection-respiratory.md` | yellow |
| `soft-tissue-infections` | `modules/infection-respiratory.md` | yellow |
| `orthopedic-emergencies` | `modules/trauma-surgical.md` | yellow |
| `acute-musculoskeletal-pain` | `modules/trauma-surgical.md` | yellow |
| `emergency-procedures` | `modules/emergency-procedures-visual.md` + `modules/procedures/` | yellow |
| `geriatric-emergencies` | `modules/special-populations.md` | yellow |
| `delirium` | `modules/special-populations.md` | yellow |
| `syncope-falls-frailty` | `modules/special-populations.md` | yellow |
| `psychiatric-emergencies` | `modules/special-populations.md` | yellow |
| `suicide-risk` | `modules/special-populations.md` | green |
| `alcohol-withdrawal` | `modules/renal-metabolic.md` | yellow |
| `environmental-emergencies` | `modules/disposition-crosscutting.md` | yellow |
| `emergency-infectious-diseases` | `modules/infection-respiratory.md` | yellow |
| `non-coronary-chest-pain` | `modules/cardiovascular.md` | yellow |
| `acute-heart-failure` | `modules/cardiovascular.md` | yellow |
| `cardiogenic-shock` | `modules/cardiovascular.md` | green |
| `vasoactive-inotrope-infusions` | `modules/cardiovascular.md` | yellow |
| `acute-aortic-syndrome` | `modules/cardiovascular.md` | green |
| `cardiac-tamponade-pericardial-emergency` | `modules/cardiovascular.md` | green |
| `critical-valvular-disease` | `modules/cardiovascular.md` | yellow |
| `infective-endocarditis` | `modules/cardiovascular.md` | green |
| `dvt` | `modules/cardiovascular.md` | yellow |
| `device-complications` | `modules/cardiovascular.md` | yellow |
| `ecg-pocus-integration` | `modules/disposition-crosscutting.md` | yellow |
| `pocus` | `modules/disposition-crosscutting.md` | yellow |
| `clinical-scores-calculators` | `modules/clinical-scores-calculators.md` | yellow |

| `clinical-note-diagnostic-support` | `modules/documentation-governance.md` | yellow |
| `final-human-review-gate` | `modules/documentation-governance.md` | yellow |
