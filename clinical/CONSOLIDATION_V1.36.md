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
2. [IN REVIEW] `pediatric-cardiac-arrest`, `pediatric-arrhythmias`, `pediatric-shock` — ERC/RCUK PLS 2025 + SSC pediatric 2026 reconciled 02/10/2026; explicit shock fluids/vasoactive timing, arrhythmia doses/energies and arrest drugs/defibrillation added; remains yellow pending human pediatric/critical-care review. Horta-local protocol is not required.
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

- [IN REVIEW] `medication-selection-safety` — WHO Medication Without Harm 2024 + ISMP high-alert list 2024 reconciled 02/10/2026; unit/concentration/high-alert/double-check/transition gates strengthened; remains yellow pending Horta pharmacy/smart-pump/local-policy review.
- [IN REVIEW] `pediatric-status-epilepticus` — HSE CDI/0277/1.0/2025 rechecked 02/10/2026; glucose, rectal diazepam, levetiracetam administration and consultant alternatives completed; remains yellow pending human pediatric neurology/pharmacy review.

## Fase 3 — farmacología Portugal/Azores (iniciada)
- [REFERENCE FOUND / LOCAL PENDING] noradrenalina, adrenalina, dopamina, dobutamina, amiodarona e isoprenalina: presentaciones de referencia encontradas en el Formulário Hospitalar Nacional de Medicamentos de INFARMED. **No equivalen a stock actual, RCM del producto concreto ni estándar local del Hospital da Horta.**
- [PENDING] vasopresina/argipresina para shock: la referencia pública revisada no permitió confirmar una presentación portuguesa de perfusión para shock.
- Próximo paso: propofol, dexmedetomidina, midazolam, fentanilo y remifentanilo; después compatibilidad/estabilidad y concentraciones locales.

- [REFERENCE FOUND / LOCAL PENDING] propofol, dexmedetomidina, midazolam y remifentanilo: referencias portuguesas encontradas en INFARMED. No equivalen a stock actual ni a concentración estándar local de Horta.
- [PENDING] fentanilo IV de perfusión: las referencias públicas revisadas no permiten todavía fijar una presentación IV local operativa.

- [x] Gate local creado: `qa/HORTA_FORMULARY_VERIFICATION.md`. Ningún fármaco puede pasar a `verified` sin producto/RCM real, concentración estándar, estabilidad, smart-pump y revisión farmacia + médica.


## Fase 4 — pediatría (en curso)
- [x] Nuevo módulo transversal `pediatric-emergency-medications` registrado como high-risk.
- [x] Motor determinista `scripts/pediatric_emergency_calculator.py`: dosis por kg con máximo, volumen por concentración, perfusión mL/h, bolos, mantenimiento Holliday-Segar y déficit IV de gastroenteritis.
- [x] Dosis de resucitación referenciadas a ERC/RCUK 2025; fluidos a NICE NG29/CG84.
- [x] Diferencia explícita de glucosa 10%: ERC PLS general 2 mL/kg vs HSE status 3 mL/kg; no fusionarlas.
- [x] Regla anti-error: ninguna concentración pediátrica se infiere si no está respaldada por guía, ficha técnica oficial o fuente farmacológica pediátrica reconocida.
- [x] Concentraciones/dose ladders fuente-verificadas cargadas para adrenalina, noradrenalina, dopamina (con restricción <30 kg de la fuente), dobutamina, milrinona, fentanilo y midazolam.
- [ ] Revisión humana pediatría/farmacia antes de promover a green.

- [x] Registro `qa/pediatric-infusion-localization.json` y generador de tablas de bomba pediátricas `scripts/pediatric_pump_table.py`: fail-closed hasta que concentración y escalera de dosis estén verificadas por fuente pediátrica/SmPC.
- [x] Propofol bloqueado como perfusión de sedación UCI pediátrica <=16 años según ficha técnica; no confundir con anestesia/sedación procedimental.

- [x] Jerarquía pediátrica actualizada: ERC/RCUK 2025 (ruta europea primaria), AHA/AAP PALS 2025 (contraste), SSC pediátrica 2026 (sepsis/shock), NICE NG29/CG84 (fluidos), HSE 2025 (status), PANDEM 2022 (PICU sedación/delirium), fichas técnicas oficiales (restricciones/formulación).

- [x] Dexmedetomidina/propofol: conflicto guía/ficha técnica conservado; generación automática bloqueada. Ketamina continua para analgesia: pauta y concentraciones por peso verificadas con RCH; no usar como régimen universal de sedación.
- [x] Clinical QA tras ampliación de perfusiones pediátricas: **147 tests PASS**.

- [x] Registro `qa/pediatric-bolus-medications.json` + `scripts/pediatric_bolus_calculator.py` para RSI, anafilaxia, asma grave, hipoglucemia y alteraciones K/Mg; volumen solo cuando la fuente define concentración.

- [x] Analgesia pediátrica: paracetamol, ibuprofeno, fentanilo intranasal y naloxona añadidos al registro fuente-verificado; jarabes sin mL automático si la concentración comercial no está seleccionada.
- [x] Antibióticos pediátricos: regla explícita de selección por síndrome/guía actual; no tabla universal por peso.

- [x] Registro `qa/pediatric-antibiotics.json` + calculador por síndrome: sepsis, pielonefritis/ITU y celulitis con dosis NICE; meningitis conserva agente/tiempo y delega dosis exacta a BNFC, sin trasplantar dosis de sepsis.

- [x] Capa domicilio/alta pediátrica: salbutamol pMDI con spacer tras mejoría de exacerbación, dexametasona en crup grave y SRO 50 mL/kg/4 h; siempre vinculados al síndrome, no como lista genérica.

- [x] Nuevo módulo high-risk `pediatric-iv-fluid-therapy`: resucitación, mantenimiento, gastroenteritis, deshidratación por %, sepsis, cardiogénico, hemorragia, hipernatremia, hiponatremia sintomática y DKA; incluye tipo de suero, mL/kg y ventana temporal.
- [x] `scripts/pediatric_fluid_calculator.py` calcula mantenimiento, bolos, SRO, déficit por %, plan 24+24 h, hipernatremia 48 h y bolos de hiponatremia.

- [x] Nuevos módulos high-risk `pediatric-acute-asthma` (GINA 2026) y `pediatric-airway-rsi` (RCH emergency airway). Dosis pediátricas separadas de las rutas adultas.

- [x] Nuevo módulo high-risk `pediatric-electrolyte-emergencies`: hiper/hipopotasemia, hipomagnesemia, hipocalcemia sintomática, sodio e hipoglucemia con dosis pediátricas separadas de adulto.

- [x] Nuevo módulo high-risk `pediatric-blood-transfusion-major-hemorrhage`: trauma/hemorragia crítica, hematíes, plasma, plaquetas y crioprecipitado por peso; separa transfusión crítica de transfusión estable y no impone un pack masivo universal.

- [x] Nuevo módulo high-risk `pediatric-procedural-sedation`: ketamina IV/IM, óxido nitroso y fentanilo intranasal, separado de RSI y sedación UCI.

- [x] Estado real de rama tras expansión pediátrica: **127 módulos / 127 evidencia / 29 green / 98 yellow / 0 red / 147 tests PASS**.
- [x] Antibióticos pediátricos depurados: duplicados de meningitis eliminados, claritromicina oral de celulitis corregida a bandas de peso, neumonía pediátrica NICE NG250 2025 añadida.

- [x] Domicilio pediátrico ampliado: cetirizina para urticaria aislada y ondansetrón dosis única en gastroenteritis seleccionada; límites anafilaxia/QT/vómito bilioso/rehidratación preservados.

- [x] Registro canónico `qa/pediatric-antibiotics.json` + calculador por síndrome: sepsis, CAP, ITU/pielonefritis, celulitis, meningitis y neutropenia febril. Para meningitis, NICE NG240 aporta selección/urgencia y RCH/PIC aporta la dosis pediátrica explícita.

- [x] Se consolida un **registro antibiótico canónico único**: `qa/pediatric-antibiotics.json`; el calculador deja de apuntar a registros paralelos.

- [x] Conversor de líquidos domiciliarios: dosis fuente-verificada -> mL únicamente tras introducir la concentración real del frasco; no se asume una concentración comercial.

- [x] Estado real recalculado tras antibióticos + domicilio: **127 módulos / 127 evidencia / 29 green / 98 yellow / 0 red / 147 tests PASS**.

- [x] Pediatría: protocolo local Horta no requerido como gate. Se mantienen guías internacionales/SmPC + revisión humana especialista.

## Fase 5 — imagen (iniciada)
- [x] Política `qa/IMAGE_VALIDATION_POLICY.md`: workflow/docente/blinded/prospectivo separados.
- [x] Gate `scripts/validate_blinded_image_dataset.py`: fail-closed para blinding, anotaciones, referencia independiente, freeze de predicción y leakage.
- [x] Plantilla `tests/blinded-image-dataset-template.json` integrada en CI; casos publicados siguen fuera de métricas de precisión.
- [ ] Construir banco ciego autorizado y desidentificado por modalidad antes de afirmar sensibilidad/especificidad.
- [x] Gate de admisión de fuentes `qa/image-dataset-source-registry.json` + `scripts/validate_image_dataset_source.py`: licencia/DUA, redistribución, desidentificación, referencia y separación de labels son independientes y fail-closed.
- [x] Primer protocolo de intake congelado: PTB-XL fold 10, hashes paciente/estudio y referencias separadas (`qa/PTBXL_BLINDED_PROTOCOL.md`, `scripts/prepare_ptbxl_blinded_cohort.py`). PTB-XL queda intake-ready, no validado.

- [x] Generador fail-closed `scripts/create_blinded_image_dataset.py`: crea manifiestos por modalidad/target con autorización, desidentificación y referencia independiente inicialmente en falso.
- [x] Métricas ciegas v1.1: TP/FP/TN/FN, cobertura, abstención/no-diagnóstico e IC Wilson; sensibilidad/especificidad solo con cobertura binaria completa.

- [x] Fuentes candidatas de banco ciego documentadas en `qa/IMAGE_DATASET_SOURCES.md`: PTB-XL (ECG), RSNA ICH (TC), CheXpert/MIMIC-CXR (Rx tórax), EchoNet-Dynamic/EchoNet-Pediatric (eco).
- [ ] Importar/registrar casos reales únicamente tras revisar licencia/DUA y mantener los datos fuera del repo cuando corresponda.
- [x] Workflow manual `ptbxl-blinded-intake.yml` preparado para ejecutar intake real fuera del repo: descarga PTB-XL v1.0.3, renderiza fold 10, usa IDs hash y separa referencia sellada del artefacto ciego. Aún no se ha observado una ejecución real del workflow.
- [ ] Aún no existe un dataset real suficiente para calcular métricas clínicas.
