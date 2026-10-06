# Snapshot de continuidad v1.41 — 06/10/2026

> Este bloque prevalece para la rama `v1.41-procedures-visual`; el contenido histórico inferior conserva snapshots anteriores y no debe usarse como estado actual de esta rama.

- Rama: `v1.41-procedures-visual`.
- `main`: **no modificar ni fusionar automáticamente**.
- Último Clinical QA global verificado: **#752 SUCCESS** sobre `e2c8bedd338dd70053532d545b41226d4885f4c6`.
- Módulo Técnicas y Procedimientos: **196 técnicas canónicas + 4 alias**, 16 familias, 200 IDs textuales.
- Añadido `PROC-NEURO-005`: monitorización de PIC/PPC.
- Auditoría posterior añadió 5 huecos de alta relevancia: UVC neonatal, histerotomía resucitativa, balón uterino PPH, reimplante dental permanente y ferulización dentoalveolar.
- Fase visual: **PAUSADA**; continuar solo con texto hasta nueva orden.
- Normalización textual v1.41: **196/196 procedimientos canónicos completos** con plantilla estructurada; 4 alias permanecen como referencias cruzadas.
- Todas las técnicas permanecen **YELLOW**.
- Primera pasada de procedimientos invasivos de alto riesgo no SPECIALIST completada para RSI, CVC yugular/femoral, drenaje pleural, toracocentesis diagnóstica/terapéutica, UVC neonatal y balón uterino PPH.
- Primera revisión bibliográfica profunda de todos los procedimientos SPECIALIST completada; ver `clinical/qa/V1.41_SPECIALIST_PROCEDURE_REVIEW.md`.
- Revisión clínica profunda iniciada por procedimientos SPECIALIST; `PROC-US-007` se deduplicó como alias de `PROC-CV-006` (pericardiocentesis ecoguiada).
- Regla de gotas: solo cuentagotas y solo con factor exacto verificado.
- Handoff autoritativo: `clinical/qa/V1.41_FINAL_HANDOFF.md`.

---

# CURRENT_STATE — Competencia Médica

Fecha de comprobación documental: 02/10/2026.
Fuente de trabajo: repositorio `JuanCopado/Emergency`, rama de consolidación v1.36 basada en la propuesta v1.35. Este estado describe el repositorio; no implica que la competencia esté instalada o publicada en Plugins.

## Estado verificado
- Paquete original recibido: **v1.26 — Endocrine Emergencies**. Copia de trabajo actual: propuesta **v1.35**, no instalada.
- **106** IDs únicos en el índice del paquete; **106/106** resuelven en los bundles.
- Evidencia registrada: **106/106**; 31 green, 75 yellow, 0 red.

## Estado de trabajo v1.36
- Rama `v1.36-consolidation`: **128 IDs**, **128/128** registros de evidencia, **29 green / 99 yellow / 0 red**. Último `Clinical QA` verificado: **178/178 tests PASS**, `automated_status: PASS` (run #356).
- El nuevo módulo separa selección clínica de aritmética: `scripts/pediatric_emergency_calculator.py` solo calcula dosis/volúmenes/mL/h con entradas ya validadas.
- Jerarquía pediátrica v1.36: ERC/RCUK 2025, AHA/AAP PALS 2025, SSC pediátrica 2026, NICE, HSE 2025, PANDEM y fichas técnicas oficiales. No se exige guía local de Horta para pediatría.
- Perfusiones pediátricas fuente-verificadas ya cargadas para adrenalina, noradrenalina, dopamina con restricción de fuente, dobutamina, milrinona, fentanilo y midazolam.
- `pediatric-iv-fluid-therapy` añade selección de tipo de suero, volumen y tiempo por escenario; separa shock, deshidratación, gastroenteritis, sepsis, DKA y trastornos del sodio. Dexmedetomidina y propofol permanecen bloqueadas para generación automática por conflicto guía/ficha técnica; ketamina continua permanece pendiente de una pauta pediátrica explícita.

- Antibióticos pediátricos v1.36 depurados por síndrome: sepsis, meningitis, pielonefritis/ITU, celulitis, neutropenia febril y neumonía; se eliminaron duplicados y se preservan bandas de edad/peso cuando la guía no permite una conversión universal mg/kg.

- Fase 5 de imagen: gate ciego v1.1 activo con hashes paciente/estudio, timestamps de congelación/revelado, clases positive/negative/abstain/nondiagnostic, cálculo fail-closed de métricas y generador de manifiestos por modalidad. `qa/IMAGE_DATASET_SOURCES.md` documenta PTB-XL, RSNA ICH, CheXpert/MIMIC-CXR y EchoNet como candidatos. Existe un pilot PTB-XL real validado para ingeniería de pipeline (sin métricas); el fold 10 completo de prevalencia natural está en construcción. No existe todavía una evaluación diagnóstica ciega finalizada que permita afirmar sensibilidad/especificidad.

- Toxicología v1.36 ampliada y sometida a banco clínico de regresión: **24/24 casos estructurados PASS** (no equivalen a tests Python ni validación prospectiva). Incluye drogas recreativas/simpaticomiméticas, tóxicos farmacológicos/industriales y reversión ampliada de anticoagulantes; `toxicology` y `anticoagulation-reversal` permanecen yellow hasta revisión humana y localización Portugal/Azores.\n\n- Nuevo módulo central **Clinical Scores & Calculators**: 134 escalas activas cribadas (CORE/SPECIALIST) + 45 fórmulas en un registro único, sin duplicar escalas por patología. Soporta entradas editables, autocompletado solo desde datos conocidos, salida con valor/categoría + interpretación breve + procedencia, y motor determinista para fórmulas. Estado yellow hasta validación fuente-a-fuente y revisión humana.\n\n## Estado autoritativo actual
- **v1.35** sigue siendo la línea clínica vigente; **v1.36-consolidation** es una rama de trabajo documental/validación y no una liberación clínica.
- **v1.35** es el estado clínico vigente de este repositorio: **106 IDs**, **106/106** registros de evidencia, **31 green / 75 yellow / 0 red** y **63/63** pruebas unitarias.
- Cualquier cifra inferior (por ejemplo **93/93**, **98 IDs** o **104/104**) que aparezca más abajo pertenece a un **snapshot histórico de la versión indicada** y no debe interpretarse como estado actual.
- Línea base v1.26: **58 pruebas unitarias** y **27 regresiones con fuentes**. En la propuesta v1.35 pasan 63 pruebas unitarias; las 106 rutas resuelven y la auditoría de cobertura registra 106/106 (31 green, 75 yellow, 0 red). El test de manifiesto incluye las trece rutas incorporadas desde v1.26; cada ejemplo de mL/h de las perfusiones nuevas se comprueba por prueba unitaria. Estos controles no equivalen a validación clínica prospectiva.
- Los casos de regresión y las pruebas estructurales no son evaluación ciega de
  respuestas, validación clínica prospectiva ni prueba de precisión de imágenes.
- Flujos de imagen: puerta de entrada común y **9 IDs de modalidad** (radiografía
  musculoesquelética y torácica, POCUS, ECG, gasometría, piel/herida, TC/RM,
  oftalmología y otra imagen); no hay un modelo diagnóstico entrenado propio.

## Regla de continuidad
El índice de la competencia instalada manda. **No volver al paquete de 63** ni
fijar 85 como el total actual. La cifra 85 está documentada en v1.20; las versiones
v1.21–v1.26 añadieron módulos. Si se cambia el código, recalcular total y cobertura.

## Decisiones clínicas y de presentación
- Responder en español salvo petición de otro idioma.
- Para perfusiones: dosis, dilución compatible (100 o 200 mL si procede),
  concentración final, aritmética, **mL/h**, titulación y monitorización.
- Para bolos/intermitentes: dosis, volumen y tiempo; no convertirlos artificialmente
  en perfusión continua. Verificar peso, función renal, alergias y contraindicaciones.
- Ofrecer alternativas según síndrome y disponibilidad local comprobada.
  **Nimodipino no sustituye a nicardipino** como antihipertensivo general.
- En Portugal/Azores consultar DGS, INFARMED y protocolo regional/local antes de
  afirmar conformidad o disponibilidad; el acceso previo al portal DGS dio 403.
- Las recomendaciones clínicas cambiantes requieren cotejo actualizado antes de
  presentarlas como definitivas; las modificaciones pasan por revisión humana.

## Trabajo clínico reciente y continuación
- v1.20: hemorragia intracerebral espontánea, compresión medular, cola de caballo.
- v1.21: selección de antihipertensivos IV cuando no haya nicardipino.
- v1.22: grandes quemados e inhalación de humo.
- v1.23–v1.24: hemorragia digestiva baja, isquemia mesentérica y reconciliación
  focal con ESVS 2025 / ESGE 2026.
- v1.25: flujo para verificar fuentes DGS/INFARMED y contexto portugués.
- v1.26: crisis suprarrenal, tormenta tiroidea y coma mixedematoso.
- Trabajo completado en la copia de trabajo, propuesta v1.27: reconciliación focal con consensos conjuntos
  ETA/BTA/Society for Endocrinology/Welsh Endocrine and Diabetes Society de 2026
  para tormenta tiroidea (ETJ-26-0043) y coma mixedematoso (ETJ-26-0044). En la
  tormenta se añadió la pauta de hidrocortisona del consenso, separada de ATA 2016,
  seguridad hepática/PTU, control de potasio y escalada. En coma mixedematoso, las
  pautas IV cotejadas concuerdan con el módulo; no se añadió pauta enteral no
  verificada. Snapshot histórico de esa versión: 93/93 resuelven; evidencia 93/93 (34 green,
  59 yellow, 0 red); 58/58 pruebas pasan. Detalle: `updates/endocrine-consensus-review-2026-09-27.md`.
- Pendientes inmediatos: revisión clínica humana del borrador; comprobación local
  DGS/INFARMED/formulario Azores y disponibilidad; detalle enteral de levotiroxina
  si no hay IV. El portal DGS previamente devolvió 403; ninguna norma individual
  consta aquí como revisada.
- Propuesta v1.28: revisión ampliada de hemorragia digestiva integrada en las rutas existentes. `upper-gi-bleeding` ahora incluye estabilización/riesgo, vía aérea selectiva, procinéticos selectivos, estigmas Forrest, hemostasia/rescate y vía variceal separada. La ruta existente `lower-gi-bleeding` fue cotejada: CTA/embolización, colonoscopia no urgente tras estabilización, reversión selectiva y TXA no rutinario ya cubiertos. Sin módulo nuevo; en ese snapshot histórico el índice seguía en 93. Ver `updates/gi-bleeding-review-2026-09-28.md`.
- Pendientes GI: revisión clínica humana, protocolo/formulario/stock local de Portugal-Azores, conciliación detallada del reinicio/reversión antitrombótico y diagnóstico de intestino delgado tras endoscopia alta/baja negativa. Mantener distinción entre recomendaciones de guías y protocolo local.
- Propuesta v1.29: revisión focal de anticoagulación en isquemia mesentérica aguda con ESVS 2025/WSES 2022. Clarifica UFH/LMWH para MVT, duración 3–6 meses y terapia prolongada según riesgo, escalada por peritonitis/deterioro, distinción NOMI/arterial y ausencia de nomograma UFH universal en esas guías. No inventa dosis o mL/h. Se conserva el ID existente. Ver updates/mesenteric-anticoagulation-review-2026-09-28.md. Quedan validación humana y protocolo local de dosis/monitorización/procedimientos.
- Propuesta v1.30: revisión focal de la alternativa enteral en coma mixedematoso. No se añadió dosis: el consenso conjunto 2026 conserva carga IV y contempla transición oral al recuperar plenamente la conciencia; una serie unicéntrica retrospectiva (14 casos, edades 11–82) no basta para adoptar la carga oral/taper como pauta general adulta. Se mantiene revisión especialista y local. Ver updates/myxedema-enteral-review-2026-09-28.md.
- Propuesta v1.31: reconciliación focal de reversión/reinicio antitrombótico en hemorragia digestiva, usando módulos existentes (sin ID duplicado). Se anotan diferencias ESGE/ACG-CAG sobre reversión DOAC (certeza baja/muy baja), algoritmo selectivo según gravedad/efecto residual y reglas de aspirina/DAPT; el momento de reiniciar anticoagulación queda individualizado y específico por fuente. Ver `updates/gi-antithrombotic-review-2026-09-28.md`. Revisión clínica humana y protocolo/formulario local pendientes.
- Propuesta v1.32: extensión de diagnóstico del intestino delgado tras endoscopias alta/baja no diagnósticas, integrada en `lower-gi-bleeding` sin crear duplicado. Se distingue hemorragia inestable (reanimación/CTA-angiografía) de paciente estable (cápsula precoz, idealmente <48 h si segura), riesgo de retención, enteroscopia dirigida y conducta tras cápsula negativa. La rama de imagen aguda ACG procede de guía 2015 y requiere revisión local GI/IR. Ver `updates/small-bowel-bleeding-review-2026-09-28.md`.
- Propuesta v1.33: se crean cinco rutas pediátricas específicas dentro del bundle existente `special-populations.md`: lactante febril ≤90 días, bronquiolitis, crup, deshidratación/choque y estatus epiléptico convulsivo (1 mes–18 años). El índice sube de 93 a 98 IDs; se mantiene `pediatric-emergencies` genérico. Fuentes/alcances, exclusiones y pendientes locales están en `updates/pediatric-pathways-review-2026-09-28.md`. Revisión humana y protocolos/formulario Portugal-Azores pendientes.
- Rutas pediátricas específicas incorporadas desde v1.33: lactante febril ≤90 días, bronquiolitis, crup, deshidratación/choque y estatus epiléptico pediátrico. No duplicarlas. En v1.36 se añade `pediatric-emergency-medications` como capa transversal de dosis, bolos, fluidos y cálculo de perfusiones. Para pediatría se usa verificación por guías/ficha técnica/fuente farmacológica reconocida; no se exige protocolo local de Horta. Sigue pendiente revisión humana pediátrica/farmacéutica.

- Propuesta v1.34: auditoría de shock y reanimación. Causas de shock cubiertas en módulos existentes: hipovolémico/hemorrágico (`trauma-major-hemorrhage`, `pediatric-dehydration-shock`), distributivo (séptico, anafiláctico, suprarrenal; neurogénico referido con cautela), cardiogénico, obstructivo (TEP, taponamiento, neumotórax a tensión) y mixto. Se añadió un módulo de evaluación/ruta para shock indiferenciado y otro marco pediátrico que deriva a causas existentes. El módulo único previo `arrhythmias-cardiac-arrest` era breve y no separaba edad ni algoritmos; se añadieron `adult-arrhythmias`, `adult-cardiac-arrest`, `pediatric-arrhythmias` y `pediatric-cardiac-arrest`, conservando el ID anterior como puerta de selección. ERC/RCUK 2025 comprobados; revisión humana, dosis/energías de tarjetas locales y protocolos Portugal/Azores pendientes. Ver `updates/shock-arrhythmia-arrest-review-2026-09-28.md`.

- Propuesta v1.35: perfusiones continuas de adulto. Nuevos IDs `vasoactive-inotrope-infusions` (noradrenalina, vasopresina, adrenalina, dopamina —no primera línea en shock séptico—, dobutamina, milrinona, levosimendán, fenilefrina y angiotensina II solo si disponible) y `icu-sedation-analgesia-infusions` (analgesia primero con fentanilo, remifentanilo, morfina, hidromorfona; propofol, dexmedetomidina, midazolam, ketamina adyuvante; RASS/CPOT/BPS, sedación ligera, interrupción diaria, PRIS, triglicéridos, bradicardia por dexmedetomidina, acumulación de benzodiacepinas/delirium). Cada perfusión trae dilución, concentración final, aritmética y mL/h para 70 kg. Se conservó `sedoanalgesia` (procedimental) con una línea de remisión. Fuentes: SSC 2026/2021, PADIS 2018/2025, fichas FDA y SmPC EMA/UK; no accesibles: texto completo SSC 2026, tabla ESC 2021, RCM INFARMED. Discrepancias clave: vasopresina 0,01 U/min (ficha EE. UU.) frente a 0,03 U/min fija; noradrenalina base frente a tartrato; vía periférica (SSC) frente a vía central (SmPC UK). Ver `updates/icu-infusions-review-2026-09-29.md`. Pendientes: revisión humana UCI/cardiología/farmacia, concentraciones estándar y RCM locales Portugal/Azores; perfusiones pediátricas como siguiente paso.

## Casos y límites
Los casos de hematoma subdural, neumotórax a tensión, IAMCEST, TEP, sepsis,
hemorragia digestiva e infección grave ayudaron a definir reglas y regresiones.
No atribuir a todos ellos una evaluación independiente o real de respuestas.
Nunca describir la interpretación visual como clínicamente validada. La copia
actualizada de este ZIP es un borrador de trabajo, no una instalación publicada.

- v1.36 añade `pediatric-acute-asthma` y `pediatric-airway-rsi` para evitar heredar dosis adultas en crisis asmática e intubación pediátrica.

- `pediatric-electrolyte-emergencies` añade dosis pediátricas específicas para K/Mg/Ca/Na/glucosa y evita heredar pautas adultas.

- `pediatric-blood-transfusion-major-hemorrhage` añade soporte transfusional pediátrico por peso y preserva la variabilidad entre protocolos de hemorragia masiva.

- `pediatric-procedural-sedation` separa sedación procedimental de RSI y perfusiones UCI, con ketamina/nitroso/fentanilo y criterios de recuperación.


## Punto de continuidad — 02/10/2026 17:06 — HISTÓRICO (no usar como estado actual)
- Rama: `v1.36-consolidation`.
- Estado recalculado: **127 módulos / 127 registros de evidencia / 29 green / 98 yellow / 0 red**.
- Snapshot histórico de ese corte: **151 tests PASS**. Estado actual: ver `Estado canónico actual` al final.
- Fase 4 pediátrica ampliamente desarrollada: medicación por peso, perfusiones/bolos, fluidoterapia, asma, RSI, electrolitos, hemoderivados, sedación procedimental, antibióticos por síndrome y alta.
- Pediatría no requiere protocolo local de Horta como gate; se apoya en guías internacionales vigentes, SmPC y fuentes pediátricas reconocidas.
- Fase 5 imagen iniciada con contrato ciego v1.1, métricas fail-closed, generador de manifiestos y candidatos PTB-XL, RSNA ICH, CheXpert/MIMIC-CXR y EchoNet. Aún no existe dataset real suficiente para claims de precisión.
- Handoff para nuevo hilo actualizado en `clinical/HANDOFF_PROMPT.md`.
- Siguiente paso recomendado: primer dataset real autorizado/desidentificado con referencia independiente, freeze de manifest antes de labels y ejecución ciega; o revisión humana de high-risk yellow si se prioriza consolidación clínica.


## Avance Fase 5 — 02/10/2026
- Nuevo gate de admisión de fuentes: `qa/image-dataset-source-registry.json` + `scripts/validate_image_dataset_source.py`.
- PTB-XL queda **intake-ready** tras congelar protocolo fold 10 y separación de referencia: `qa/PTBXL_BLINDED_PROTOCOL.md` + `scripts/prepare_ptbxl_blinded_cohort.py`.
- Snapshot histórico: en ese momento aún no se habían importado casos reales. Posteriormente se construyeron NATURAL_500 y full-fold; ver estado canónico.
- Estado clínico/evidencia sin cambios: **127 módulos / 127/127 evidencia / 29 green / 98 yellow / 0 red**.
- Snapshot histórico: el archivo llegó a 159 tests; posteriormente la suite fue ampliada y revalidada.
- Fase 4 pediátrica sigue bloqueada únicamente por revisión humana pediatría/farmacia; se añadió `qa/PEDIATRIC_HUMAN_REVIEW_READINESS.md` sin auto-promoción a green.

- Workflow manual real añadido: `.github/workflows/ptbxl-blinded-intake.yml`. Descarga metadatos PTB-XL v1.0.3, valida el gate de fuente, genera salt efímero si no hay secreto configurado, descarga solo los waveforms seleccionados y separa artefacto ciego de referencia sellada.
- Render digital congelado con divisiones 0,04 s / 0,1 mV; no se afirma calibración física mm/s o mm/mV.
- PR draft de validación creado: **#12 — v1.36 consolidation — validation only (do not merge)**. No modifica ni promueve `main`.
- Snapshot histórico: inicialmente el wrapper no exponía el run; después se verificaron directamente los GitHub Actions REST runs.

- Gate freeze/reveal añadido: `scripts/finalize_blinded_image_dataset.py` + `qa/BLINDED_PREDICTION_FREEZE.md`.
- El finalizador exige coincidencia exacta de IDs entre artefacto ciego, predicciones y referencia sellada; bloquea duplicados, clases inválidas y cualquier predicción congelada en/tras el timestamp de revelado.
- La salida final v1.1 elimina identificadores fuente y conserva `abstain/nondiagnostic`, permitiendo que el calculador suprima sensibilidad/especificidad estándar cuando la cobertura no es binaria completa.
- El archivo de tests contiene ahora **159 funciones de test**. `Clinical QA` run #285 fue verificado directamente en GitHub Actions: **159/159 tests PASS**, `automated_status: PASS`.

- **PTB-XL real pilot run #6: SUCCESS** (GitHub Actions run 37042742831).
- Blind artifact verified locally: 10 rendered ECG PNG + `blinded_manifest.json`; target `AFIB`; no `target_positive`, `source_ecg_id` or `patient_id` present.
- Blinded artifact digest: `sha256:080bf99e0937637074377b11eb900d4699decdbc0f82168da661e426a5e97350`.
- Sealed-reference artifact was created separately (digest `sha256:63c01ab13bb0e8d1ca8702a4d4c389b83daa598b245fe3e6492aa5747b23a850`) and was **not opened/downloaded for interpretation**.
- Visual QA of one rendered ECG: 12 leads + 10 s lead-II rhythm strip visible; no label/source leakage observed.
- This pilot was deliberately balanced 5 positive / 5 negative for pipeline engineering and has `performance_metrics_allowed=false`; its known prevalence makes it unsuitable for diagnostic-performance claims.


- Full natural-prevalence PTB-XL fold-10 intake launched as GitHub Actions **run #9 / 37043554986**, target `AFIB`, trigger mode `FULL_FOLD`.
- At the latest verified checkpoint the run had passed setup, metadata download, source gate, salt creation and intake-mode selection; `Build blinded fold-10 ECG benchmark` was still in progress with no reported failure.
- The sealed reference for the full-fold run has not been opened or used. Diagnostic metrics remain blocked until predictions are frozen and the run completes.

- Pipeline de evaluación por lotes añadido para el full-fold: sharding determinista por paciente, plantilla de predicción por shard y merge fail-closed.
- Clinical QA run #295 verificado: **161/161 tests PASS**, `automated_status: PASS`.
- Full-fold PTB-XL AFIB run #9 continúa en `Build blinded fold-10 ECG benchmark`; sin error reportado y referencia aún sellada.

- Estado de tests actualizado tras sharding/merge: **161 PASS**.

- Clinical QA #297 y #298: SUCCESS; suite actual **162/162 PASS**.
- Builder PTB-XL optimizado con descarga concurrente y render multiproceso determinista; no cambia selección, referencia ni protocolo.
- Full-fold acelerado activo: run #11 / 37050506581, target AFIB, mode FULL_FOLD; referencia sellada.

## Cierre banco ECG ciego — PTB-XL AFIB NATURAL_500
- GitHub Actions run #13 / `37051568918`: **SUCCESS**.
- Cohorte: `natural_label_agnostic_systematic_500`, fold 10, target AFIB, selección sistemática independiente del diagnóstico.
- Artefacto ciego: **500 ECG PNG / 500 IDs únicos / 500 study hashes únicos / 488 pacientes**.
- Agrupación: 11 pacientes aportan >1 ECG (máximo 3); **0 pacientes cruzan shards**.
- Evaluación escalable: **11 shards + 11 prediction templates**; IDs de shards/templates coinciden exactamente con el manifiesto.
- Leakage audit: no aparecen `target_positive`, `source_ecg_id`, `source_patient_id`, `scp_codes`, `patient_id` ni `filename_lr` en el paquete ciego.
- Referencia sellada ausente del paquete ciego y **no descargada/abierta**.
- Digest artefacto ciego: `sha256:c932d356b5fddf19f4e41417ac9320656a0d6d8af7f3219730cff916291ee6be`.
- Digest referencia sellada (solo metadata GitHub, sin abrir contenido): `sha256:eb45838c51863ce1512a906f56d639fe2a368d608de5b0f552c6232709571c34`.
- QA visual distribuido sobre 9 ECG del banco: layout 12 derivaciones + tira II íntegro, sin texto diagnóstico/IDs fuente visibles.
- Este banco **sí queda apto metodológicamente para evaluación ciega exploratoria**, pero no existen métricas hasta ejecutar un intérprete/modelo real y congelar predicciones antes del reveal.

## Estado canónico actual — 02/10/2026
- Rama de trabajo: `v1.36-consolidation`; `main` no promovida.
- Estado clínico/evidencia: **127 módulos / 127/127 evidencia / 29 green / 98 yellow / 0 red**.
- Clinical QA verificado: **175/175 tests PASS**, `automated_status: PASS` (run #338).
- Fase 4 pediátrica: desarrollo técnico completo; gate pendiente exclusivamente humano pediatría/farmacia. Sin auto-promoción.
- Fase 5 ECG: PTB-XL pilot real, NATURAL_500 y full-fold construidos; los bancos previos a v2 se clasifican como ingeniería porque logs antiguos mostraban prevalencia agregada.
- PTB-XL NATURAL_500 v2 limpio fue disparado tras suprimir cualquier count positivo/negativo pre-reveal. Referencia permanece sellada.
- RSNA ICH: source-level intake-ready; referencia multi-reader/adjudicada exigida; DICOM→render aún debe congelarse antes de evaluación real.
- MIMIC-CXR 2.1.0: source-level intake-ready; acceso real requiere credentialing, CITI y DUA; solo test manualmente curado, no labels automáticos.
- EchoNet-Dynamic: source-level intake-ready para `lvef_below_40_percent` en TEST; acceso real requiere aceptación individual del Research Use Agreement.
- CheXpert: referencia expert-test y label isolation completos; source intake sigue bloqueado únicamente hasta verificar documentalmente el acuerdo específico de descarga actual.
- No existen todavía métricas diagnósticas válidas porque no se ha ejecutado/fijado un intérprete ciego real sobre un banco limpio antes del reveal.


## Cierre exploratorio ECG — PTB-XL NATURAL_500 v2 / AFIB baseline v1
- Banco ciego limpio: GitHub Actions run #14 / `37054176049`, 500 ECG, target AFIB.
- Baseline pre-reveal congelado en commit `aa6649785c6dad3d9daa3838c902d3136774d624` a `2026-10-03T00:07:32.888774Z`.
- Freeze: 46 positive / 359 negative / 93 abstain / 2 nondiagnostic; SHA-256 predicciones completas `ae7f25704b9a8a43994346406d2fabb43f786c8a49b7c4987bd40f2df1cd6663`.
- Referencia sellada revelada después del freeze a `2026-10-03T00:08:41.803705165Z`: 3 AFIB / 497 no-AFIB.
- Conteos clasificados: TP 3 / FP 43 / TN 359 / FN 0; cobertura **81.0%**; abstención **18.6%**; no-diagnóstico **0.4%**.
- Por política v1.1, sensibilidad/especificidad/PPV/NPV/accuracy estándar permanecen **suprimidas** porque 95/500 casos no tuvieron predicción binaria.
- Resultado almacenado en `qa/results/PTBXL_NATURAL500_V2_AFIB_BASELINE_V1_RESULT.json`.
- Interpretación: baseline de ingeniería sobre render ECG; **no** es precisión clínica de ChatGPT, no es validación externa/prospectiva y no promueve módulos a green.


## Cierre canónico Fase 5 — 03/10/2026
- Infraestructura automatizable de imagen cerrada: ver `qa/PHASE5_IMAGE_CLOSURE.md`.
- ECG/PTB-XL: benchmark exploratorio real completado con freeze pre-reveal y resultado post-reveal; métricas binarias estándar suprimidas por abstain/nondiagnostic.
- RSNA ICH: referencia + DICOM render WW80/WL40 + orden IOP/IPP congelados; falta acceso/import real e interpretación ciega.
- CheXpert: expert-test + visual protocol congelados; acceso específico AIMI/Redivis aún no verificado en este workspace.
- MIMIC-CXR: curated-test + visual protocol congelados; acceso real requiere credentialing/CITI/DUA.
- EchoNet-Dynamic: TEST split + visual protocol congelados; acceso real requiere aceptación individual del Research Use Agreement.
- Estado clínico/evidencia sigue **127 módulos / 127/127 evidencia / 29 green / 98 yellow / 0 red**.
- **175/175 tests PASS** es la cifra QA vigente; cifras menores anteriores son snapshots históricos.
- Fase 4 pediátrica continúa bloqueada únicamente por revisión humana pediatría/farmacia.
- v1.35 permanece línea clínica vigente; v1.36-consolidation no se promociona automáticamente.


## Corte pre-rama — 03/10/2026
- Auditoría canónica: `qa/PREBRANCH_AUDIT_V1.36.md`.
- Clinical QA: **178/178 PASS**, `automated_status: PASS`, run #356.
- Módulo central `clinical-scores-calculators`: **134 escalas + 45 fórmulas**.
- Fórmulas: **45/45 implementadas** en `scripts/clinical_calculator.py`.
- Escalas: 67 component-sum soportadas solo con componentes ya puntuados explícitamente; 67 herramientas rule/criteria/table/etc. permanecen fail-closed hasta codificación fuente-a-fuente.
- Routing corregido para usar `clinical-scores-calculators` + `calculator_id`; NIHSS/HEART/Wells/etc. ya no se interpretan como module IDs.
- La rama queda **apta como base técnica para ramificar**, pero v1.35 sigue siendo la línea clínica vigente y v1.36 no es release.


## v1.37 — primera tanda de escalas CORE — 03/10/2026
- Rama activa: `v1.37-scores-formulas-validation`.
- Estado detallado: `qa/V1.37_SCORES_VALIDATION_STATE.md`.
- **14/93 CORE** fuente-codificadas o wrapper oficial validado; **79 CORE restantes**.
- Primera tanda completada: NIHSS, Glasgow Coma Scale, NEWS2, SOFA-1, HEART, GRACE 2.0 wrapper, CHA2DS2-VASc, CHA2DS2-VA, Wells PE, PERC, YEARS, Glasgow-Blatchford, CURB-65 y Phoenix Sepsis Score.
- Fórmulas: **45/45** implementadas.
- Último QA confirmado antes del commit documental: **195/195 PASS**, run #369.
- No se promueve `clinical-scores-calculators` a green; continúa yellow hasta completar CORE, SPECIALIST y revisión humana.


## SOFA-2 incorporado — 03/10/2026
- Nuevo calculator_id: `sofa-2`, separado de `sofa` (SOFA-1/Sepsis-3).
- Registro: **135 escalas totales / 94 CORE / 41 SPECIALIST**.
- CORE fuente-codificadas o wrapper oficial: **15/94**; pendientes CORE: **79**.
- Fuente primaria: JAMA 2025, doi:10.1001/jama.2025.20516.
- Clinical QA run #375: **198/198 PASS**, `automated_status: PASS`.


## v1.37 — CORE scores complete — 03/10/2026
- Registro actual: **135 escalas / 45 fórmulas**.
- CORE: **94/94 implementadas**, pendientes CORE: **0**.
- SPECIALIST: **41 pendientes**.
- Estados ejecutables CORE: dedicated source-encoded, validated official wrapper o central formula alias.
- QA global de cierre CORE: **262/262 tests PASS**, `automated_status: PASS` (run #422).
- Nuevos cierres incluyen NNUH-MEOWS v7, Bishop, Rule of Nines, Lund-Browder, Bedside PEWS, Pediatric Trauma Score, SIPA, FLACC, Wong-Baker official wrapper, PRAM, Westley Croup, Clinical Dehydration Scale, Pediatric Appendicitis Score, PECARN Head Injury, PECARN Febrile Infant, Step-by-Step y APGAR.
- Estado detallado: `qa/V1.37_SCORES_VALIDATION_STATE.md`.
- `clinical-scores-calculators` permanece **yellow**: todavía faltan 41 SPECIALIST y revisión humana final.


## v1.37 — all scores/formulas technically complete — 03/10/2026
- Registry: **135 scales + 45 formulas**.
- CORE: **94/94 implemented**.
- SPECIALIST: **41/41 implemented**.
- Pending registered scales: **0**.
- Last code QA before documentation synchronization: **289/289 tests PASS**, `automated_status: PASS` (run #442).
- `clinical-scores-calculators` remains yellow pending human review; implementation completeness is not clinical release.
- Next queued work is a separate pediatric outpatient/home medication module and should proceed on a separate branch.


## v1.38 — pediatric outpatient/home medications — 04/10/2026
- Rama activa: `v1.38-pediatric-outpatient-medications`.
- Nuevo módulo: `pediatric-outpatient-medications`.
- Total clínico: **129 módulos**; el nuevo módulo está **yellow**.
- Registry ambulatorio expandido: **89 regímenes**.
- Motor fail-closed: `scripts/pediatric_outpatient_calculator.py`.
- Calcula peso de dosificación explícito, mg/toma, máximo, concentración verificada -> mL/toma, dosis/día, duración, total de dosis y volumen total estimado.
- No devuelve mL con concentración no verificada.
- Conserva diferencias entre guías/regímenes en entradas separadas.
- Estado/handoff: `qa/V1.38_PEDIATRIC_OUTPATIENT_STATE.md`.
- Pendiente: ampliar formulario ambulatorio, reconciliar presentaciones Portugal/Azores y revisión humana pediatría/farmacia.


## v1.38 outpatient expansion complete — 04/10/2026
- `pediatric-outpatient-medications`: **89 diagnosis-specific regimens**.
- Families: oral antibiotics/allergy alternatives, analgesia/antipyresis, selected antiemesis, antihistamines, asthma rescue/controllers, dermatology, ORS/constipation, antiparasitics, antivirals, ENT/ophthalmology, allergic rhinitis/conjunctivitis, migraine and anaphylaxis discharge.
- Calculator supports mg/kg, fixed age/weight bands, variable-day schedules, repeated fixed schedules, fixed liquid-volume bands, ORS volume/kg, sachet schedules, devices and topical/drop metadata.
- Exact concentration remains mandatory for automatic mL calculation; unverified substitutions fail closed.
- Portugal presentation reconciliation exists; **real-time Azores stock is not claimed**.
- Integrity QA for 89-regimen registry: #482 SUCCESS.
- Module remains yellow pending pediatric/pharmacy human review.

- v1.38 pediatric outpatient decision: **Azores stock is not a release gate**. Required localization is limited to Portugal INFOMED/RCM product-strength verification; exact dispensed concentration remains mandatory for mL arithmetic.


## v1.38 medication safety alert system — 04/10/2026
- Central alert engine added for `pediatric-outpatient-medications`.
- Severities: **STOP / ALERT / CAUTION / INFO**.
- STOP blocks routine calculation through structured `MedicationSafetyStop`.
- Alert families include allergy/class cross-reactivity, duplicates, major interactions, renal/hepatic incompatibility, age/weight, missing safety context, concentration mismatch and clinical red flags invalidating outpatient treatment.
- Missing allergy review or medication reconciliation produces REVIEW_REQUIRED rather than being silently treated as negative.
- Documentation: `qa/PEDIATRIC_OUTPATIENT_ALERT_SYSTEM.md`.
- Last alert-engine QA before documentation synchronization: **#510 SUCCESS**.


## v1.38 pediatric clinical review complete — 04/10/2026
- `pediatric-outpatient-medications`: **89/89 regimens reviewed** in an AI-assisted pediatric clinical audit.
- Outcomes: **41 PASS / 40 PASS_AFTER_CORRECTION / 8 PASS_WITH_NONCRITICAL_NOTE / 0 unresolved CHANGE_REQUIRED**.
- Review focused on indication, age/source scope, outpatient/discharge suitability, red flags, follow-up and separation of hospital/step-down pathways.
- Major gates added for bites, orbital cellulitis, pyelonephritis/UTI, CAP/cellulitis/preseptal, asthma/croup, anaphylaxis discharge, ORS age scope, gastroenteritis red flags, constipation red flags, red eye/headache, varicella/HSV/oseltamivir and home paracetamol.
- Review files: `qa/PEDIATRIC_OUTPATIENT_PEDIATRIC_CLINICAL_REVIEW.json` and `qa/PEDIATRIC_OUTPATIENT_PEDIATRIC_CLINICAL_REVIEW.md`.
- This is not human pediatrician sign-off; module remains **yellow**.


## v1.39 clinical note diagnostic support — 04/10/2026
- Active branch: `v1.39-clinical-note-diagnostic-support`.
- Project now has **131 modules**.
- New modules: `clinical-note-diagnostic-support` and `final-human-review-gate`.
- Structured clinical-note workspace created with timeline, provenance-aware MCDT integration, diagnostic/differential/test/treatment output contract and privacy-gated DOCX/PDF/JSON export.
- All yellow modules are dynamically deferred to a final human-review queue; no automatic yellow->green promotion.
- Privacy design uses pseudonymous encounter ID and blocks direct identifiers in exports; pseudonymization is not treated as anonymization.
- v1.39 state: `qa/V1.39_CLINICAL_NOTE_STATE.md`.
- Clinical QA #586: **363/363 PASS**, 131/131 registered, 29 green / 102 yellow / 0 red.

- Executable diagnostic-support engine added to v1.39: 92 emergency/acute-care syndromes, transparent rule hits, qualitative confidence, differential/must-not-miss, test suggestions and treatment-module routing. Synthetic diagnostic scenarios 60/60 PASS. Clinical QA #586: 363/363 PASS.

- Diagnostic coverage closure: 115/131 registered modules are directly covered/routed; the remaining 16 are explicitly classified non-diagnostic support/infrastructure. Unexpected diagnostic gaps: 0. Coverage gate is enforced in Clinical QA.

## v1.39 final diagnostic-support closure — 06/10/2026
- Active branch: `v1.39-clinical-note-diagnostic-support`; `main` remains untouched.
- Registered modules: **131/131**.
- Evidence state: **29 green / 102 yellow / 0 red**.
- Clinical-note module provides structured history, serial timeline, vitals/exam, MCDT routing, provenance, problem list, diagnostic synthesis, tests/treatment/disposition suggestions and privacy-gated DOCX/PDF/JSON export.
- Executable diagnostic engine: **92 acute-care syndromes** with age applicability routing and transparent rule hits.
- Synthetic diagnostic regression: **60/60 scenarios PASS**, including adult, pediatric, specialty and coverage-closure banks.
- Diagnostic coverage audit: **115/131 modules directly covered/routed**; remaining **16/131** are explicitly classified as image/procedure/treatment/safety/infrastructure/governance modules; **0 unexpected clinical gaps**.
- Coverage classification is now enforced by Clinical QA; a future registered module that is neither routed nor explicitly exempted fails QA.
- Privacy scanner false positives for clinical acronyms and words containing `name` were corrected using explicit word-boundary/label rules.
- Final human-review policy: every yellow module remains pending end-of-project human specialist review; no AI/automated yellow→green promotion.
- Last verified pre-handoff QA: **Clinical QA #587 SUCCESS**, **364/364 tests PASS**, `automated_status: PASS`.
- Canonical handoff: `qa/V1.39_FINAL_HANDOFF.md`.

## v1.39 clinical-note API/E2E integration — 06/10/2026

Canonical continuation after the UI-only milestone:

- trusted local backend: `clinical/scripts/clinical_note_api.py`;
- typed frontend contract: `app/src/clinical-note/types.ts` + `app/src/clinical-note/api.ts`;
- upload preflight is fail-closed: direct-identifier STOP, binary/image/PDF/DICOM manual privacy review, burned-in identifier review where applicable;
- original uploaded files are not retained or embedded in exports by this adapter;
- only clinician-accepted MCDT results enter `complementary_tests` and the clinical timeline;
- editing/rejecting a previously accepted UI result removes it from persisted note state and invalidates clinician sign-off;
- diagnostic support runs only on the accepted structured note and any new analysis resets clinician validation;
- treatment output remains non-actionable until the central medication-safety pathway is satisfied; the existing pediatric outpatient alert engine can be invoked for structured pediatric outpatient regimens;
- DOCX/PDF/JSON export is wired to the central privacy/clinician-review gate;
- DOCX/PDF structure now follows the agreed clinical order and preserves official report and AI interpretation as separate, provenance-labelled fields;
- generic Rx, gasometry, microbiology and PDF upload routes are registered centrally;
- schema/runtime drift for `language` and `routed_modules` was corrected.

Validation:
- Clinical QA #606: **SUCCESS**.
- Python regression functions: **370**.
- App UI QA #13: **SUCCESS** (TypeScript typecheck, Vitest, Vite build).
- Registered modules: **131/131**.
- Evidence state remains **29 green / 102 yellow / 0 red**.
- No yellow module was auto-promoted.

Known production boundary:
- binary ECG/Rx/TC/RM/POCUS/PDF/DICOM content is routed to the correct central module but is not autonomously interpreted by the local stdlib API. A trusted deployment adapter/model must provide that extracted/interpretive result; clinician accept/edit/reject remains mandatory.
- the agreed clinical section order is implemented. No exact institutional visual template/masthead was available in the repository or recoverable project files, so no hospital-specific layout was invented.

### Filename and red-flag hardening — final v1.39 delta
- upload privacy preflight scans the filename together with any safely extracted text;
- burned-in identifier review is required for binary image/PDF/DICOM media, not for plain-text reports;
- objective diagnostic signals/red flags returned by the central diagnostic engine are exposed in the typed frontend contract and rendered separately from must-not-miss diagnoses;
- engine-suggested active problems are visible as review-required suggestions, not silently merged into the clinician problem list;
- Clinical QA #606: **SUCCESS**, **370** Python test functions;
- App UI QA #13: **SUCCESS** (typecheck, Vitest, Vite build).


## v1.39 production vision adapter — 06/10/2026
- Production-facing binary interpretation adapter implemented: `clinical/scripts/clinical_note_vision_adapter.py`.
- End-to-end circuit is now `privacy review -> configured HTTPS provider -> proposal -> clinician Accept/Edit/Reject -> persistence`.
- Provider calls fail closed unless required metadata/burned-in identifier review is complete.
- Prepared upload payloads are HMAC-signed; client tampering with routing/privacy/prepared state is rejected.
- Original filenames and source SHA-256 are not sent to the external provider; provider receives a generic filename and central routed module IDs.
- Redirects are rejected, provider response size is capped, provider output is rescanned for direct identifiers, and confidence remains qualitative only.
- AI-generated image content cannot be labeled as an official report; official-report extraction is reserved for document/PDF workflows.
- React UI exposes `Interpretar com módulo IA` only after privacy checks and keeps interpreted results pending until explicit medical acceptance.
- Clinical QA #614: **SUCCESS**, **376/376 tests PASS**.
- App UI QA #19: **SUCCESS** (TypeScript typecheck, Vitest, Vite build).
- Evidence state unchanged: **131/131 modules, 29 green / 102 yellow / 0 red**; no auto-promotion.
- Canonical implementation note: `qa/V1.39_VISION_ADAPTER_STATE.md`.
- Remaining deployment boundary: bind `CLINICAL_VISION_PROVIDER_URL`/credentials to the chosen trusted medical image/document service and run authorized modality-specific E2E validation. The repository intentionally does not invent or bundle a clinical vision model.
