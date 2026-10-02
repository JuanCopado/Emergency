# CONSOLIDATION v1.36 — plan de trabajo

Fecha de inicio: 02/10/2026.
Rama: `v1.36-consolidation`.

## Objetivo
Reducir deuda clínica y documental de v1.35 antes de añadir módulos de bajo valor incremental. La línea clínica vigente sigue siendo v1.35 hasta que una revisión humana promueva cambios.

## Línea base documentada
- 106 IDs clínicos.
- 106/106 registros de evidencia.
- 31 green / 75 yellow / 0 red.
- 63 tests definidos en `tests/test_skill.py`; el repositorio documenta 63/63 PASS en v1.35.
- Los tests estructurales/regresiones no equivalen a validación clínica prospectiva.

## Fase 1 — coherencia documental
- [x] Eliminar referencias obsoletas a v1.30 como estado actual.
- [x] Eliminar el pendiente pediátrico ya resuelto en v1.33.
- [x] Actualizar 59 yellow -> 75 yellow.
- [x] Eliminar duplicación de v1.28 en README.
- [x] Declarar v1.36 como rama de consolidación, no como liberación clínica.

## QA transversal
- [x] Política QA formal.
- [x] Matriz de controles.
- [x] Release gates fail-closed para defectos automatizables.
- [x] Runner único `qa/qa_runner.py`.
- [x] Gate de revisión humana para high-risk.
- [x] Gate Portugal/Azores para presentaciones/protocolos locales.
- [x] CI GitHub para ejecutar QA en push/PR de consolidación.
- [x] Regla: QA automático nunca convierte un high-risk yellow a green.

## Fase 2 — yellow de máximo riesgo
Orden de revisión:
1. [IN REVIEW] `adult-cardiac-arrest`, `adult-arrhythmias`, `arrhythmias-cardiac-arrest` — ERC/RCUK 2025 reconciled 02/10/2026; explicit energies/doses/pacing added; remains yellow pending human + Portugal/Azores operational review
2. [IN REVIEW] `pediatric-cardiac-arrest`, `pediatric-arrhythmias`, `pediatric-shock` — ERC/RCUK PLS 2025 reconciled 02/10/2026; explicit shock fluids/vasoactive timing, arrhythmia doses/energies and arrest drugs/defibrillation added; remains yellow pending human + Portugal/Azores operational review
3. [IN REVIEW] `vasoactive-inotrope-infusions` — SSC 2026 + current labels rechecked 02/10/2026; base/salt safety rule hardened; remains yellow pending ICU/pharmacy + Portugal/Azores product/formulary review
4. [IN REVIEW] `icu-sedation-analgesia-infusions` — PADIS 2018/2025 + current dexmedetomidine product information rechecked 02/10/2026; remains yellow pending ICU/pharmacy + Portugal/Azores product/formulary review
5. [IN REVIEW] `pulmonary-embolism` — ESC formal guideline 2019 + ACVC 2025 operational update reconciled 02/10/2026; 2026 PRAGUE-26 retained as emerging evidence; remains yellow pending human + Portugal/Azores reperfusion/anticoagulation review
6. [IN REVIEW] `anticoagulation-reversal` — ISTH SSC 2024 + current andexanet/idarucizumab product information reconciled 02/10/2026; remains yellow pending hematology/pharmacy + Portugal/Azores formulary/release workflow review
7. [IN REVIEW] `empiric-antibiotics` — SSC 2026 + IDSA cUTI 2025 reconciled 02/10/2026; timing/stewardship/local-antibiogram gates added; remains yellow pending ID/pharmacy + Horta/Azores antibiogram/formulary review
8. [IN REVIEW] `status-epilepticus` — NICE 2025 + ACEP 2024/AES-ESETT doses reconciled 02/10/2026; explicit benzodiazepine/second-line loads added; remains yellow pending neurology/ICU + Portugal/Azores operational review
9. [IN REVIEW] `sodium-emergencies` — European hyponatraemia/SfE guidance reconfirmed 02/10/2026; overcorrection/relowering gates strengthened; remains yellow pending renal/endocrine + local hypertonic-saline protocol review
10. [IN REVIEW] `obstetric-emergencies` — ACOG reaffirmed 2026 + WHO maternal guidance 2025 reconciled 02/10/2026; magnesium/eclampsia toxicity rescue added; remains yellow pending obstetric/anesthesia + Portugal/Azores protocol review
11. [IN REVIEW] `toxicology` — ERC/RCUK 2025 + ACMT/AACT current guidance reconciled 02/10/2026; decontamination/naloxone/poison-centre gates strengthened; remains yellow pending toxicology + local antidote-stock review
12. [IN REVIEW] `anaphylaxis` — RCUK/ERC 2025 reconciled 02/10/2026; explicit IM adrenaline/fluid/refractory pathway added; remains yellow pending local product/infusion/observation review

## Criterios para pasar yellow -> green
Un módulo solo puede pasar a green cuando:
- fuente primaria/autoritativa vigente identificada;
- fecha y versión documentadas;
- discrepancias entre guías resueltas o explícitamente descritas;
- dosis, concentraciones, máximos y unidades verificadas;
- para perfusiones: concentración final y cálculo mL/h comprobados;
- contraindicaciones y monitorización revisadas;
- aplicabilidad Portugal/Azores comprobada cuando exista fuente nacional/local;
- ausencia de afirmaciones de stock o protocolo local no verificadas;
- revisión humana registrada.

## Fase 3 — farmacología Portugal/Azores
Crear una tabla separada de presentaciones y estándares locales, sin inferir stock:
- principio activo;
- presentación/ampolla;
- expresión como base o sal;
- diluyente compatible;
- concentración estándar local;
- estabilidad;
- acceso periférico/central;
- observaciones de seguridad;
- fuente INFARMED/RCM o protocolo local;
- estado: verificado / pendiente.

Prioridad: noradrenalina, adrenalina, vasopresina, dopamina, dobutamina, amiodarona, isoprenalina, propofol, dexmedetomidina, midazolam, fentanilo, remifentanilo.

## Fase 4 — pediatría
Después de consolidar los módulos críticos:
- medicación de emergencia por peso;
- dosis máximas;
- bolos y perfusiones;
- concentración y mL/h;
- fluidoterapia, mantenimiento, deshidratación y hemoderivados;
- PCR/arritmias/RSI/estatus/sepsis/anafilaxia/asma/electrolitos;
- controles anti-error decimal y límites máximos.

## Fase 5 — imagen
Mantener el motor como workflow no validado hasta disponer de banco ciego con referencia independiente. No convertir casos docentes/regresión en sensibilidad/especificidad.

## Regla de liberación
No fusionar a `main` cambios clínicos de alto riesgo únicamente porque pasen tests. Requieren revisión humana y actualización del registro de evidencia.


## Segunda ola de consolidación
- [AUDITED / NO CHANGE] `airway-rsi` — already green; DAS 2025/SCCM 2023 basis preserved.
- [AUDITED / NO CHANGE] `diabetic-ketoacidosis-hhs` — already green; 2024 ADA/EASD/JBDS/AACE/DTS consensus remains current.
- [AUDITED / NO CHANGE] `potassium-emergencies` — already green; RCUK 2025 operational hyperkalaemia details are concordant with the module.
- [IN REVIEW] `calcium-magnesium-emergencies` — SfE + RCUK/ERC 2025 reconciled 02/10/2026; remains yellow pending endocrine/pharmacy + Portugal/Azores infusion/formulary review.

- [IN REVIEW] `trauma-major-hemorrhage` — reconciled 02/10/2026 with DGS Norma 011/2013 (current DGS listing updated 18/07/2017) + European trauma guideline 2023. Historical fixed pack/TXA/rFVIIa wording corrected; status changed green -> yellow pending human transfusion/trauma review and current Horta/Azores operational verification.

- [IN REVIEW] `traumatic-intracranial-mass-effect` — Hospital da Horta local TCE card supplied 02/10/2026 integrated and compared with NICE NG232/BTF. Local CT/observation routing preserved; status green -> yellow until the SBP and mild-TBI CT/antiplatelet differences are confirmed as intentional and the card version/date is recorded.

- [IN REVIEW] `acute-respiratory-failure` + `noninvasive-ventilation` — ERS HFNO 2022 + ERS/ATS NIV 2017 reconciled 02/10/2026. HFNO remains preferred over NIV for de-novo hypoxemic failure; COPD-acidotic and cardiogenic indications preserved. Both remain yellow pending respiratory/ICU + local device/escalation review.
- [AUDITED / NO CHANGE] `high-flow-nasal-oxygen` — already green; ERS 2022 and ROX limitations remain concordant.
- [AUDITED / NO CHANGE] `oxygen-therapy-emergency` — already green; target-based oxygen and device limitations preserved.
