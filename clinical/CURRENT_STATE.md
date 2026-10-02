# CURRENT_STATE — Competencia Médica

Fecha de comprobación documental: 02/10/2026.
Fuente de trabajo: repositorio `JuanCopado/Emergency`, rama de consolidación v1.36 basada en la propuesta v1.35. Este estado describe el repositorio; no implica que la competencia esté instalada o publicada en Plugins.

## Estado verificado
- Paquete original recibido: **v1.26 — Endocrine Emergencies**. Copia de trabajo actual: propuesta **v1.35**, no instalada.
- **106** IDs únicos en el índice del paquete; **106/106** resuelven en los bundles.
- Evidencia registrada: **106/106**; 31 green, 75 yellow, 0 red.

## Estado de trabajo v1.36
- Rama `v1.36-consolidation`: **127 IDs**, **127/127** registros de evidencia, **29 green / 98 yellow / 0 red**. Último `Clinical QA` verificado: **162/162 tests PASS**, `automated_status: PASS`.
- El nuevo módulo separa selección clínica de aritmética: `scripts/pediatric_emergency_calculator.py` solo calcula dosis/volúmenes/mL/h con entradas ya validadas.
- Jerarquía pediátrica v1.36: ERC/RCUK 2025, AHA/AAP PALS 2025, SSC pediátrica 2026, NICE, HSE 2025, PANDEM y fichas técnicas oficiales. No se exige guía local de Horta para pediatría.
- Perfusiones pediátricas fuente-verificadas ya cargadas para adrenalina, noradrenalina, dopamina con restricción de fuente, dobutamina, milrinona, fentanilo y midazolam.
- `pediatric-iv-fluid-therapy` añade selección de tipo de suero, volumen y tiempo por escenario; separa shock, deshidratación, gastroenteritis, sepsis, DKA y trastornos del sodio. Dexmedetomidina y propofol permanecen bloqueadas para generación automática por conflicto guía/ficha técnica; ketamina continua permanece pendiente de una pauta pediátrica explícita.

- Antibióticos pediátricos v1.36 depurados por síndrome: sepsis, meningitis, pielonefritis/ITU, celulitis, neutropenia febril y neumonía; se eliminaron duplicados y se preservan bandas de edad/peso cuando la guía no permite una conversión universal mg/kg.

- Fase 5 de imagen: gate ciego v1.1 activo con hashes paciente/estudio, timestamps de congelación/revelado, clases positive/negative/abstain/nondiagnostic, cálculo fail-closed de métricas y generador de manifiestos por modalidad. `qa/IMAGE_DATASET_SOURCES.md` documenta PTB-XL, RSNA ICH, CheXpert/MIMIC-CXR y EchoNet como candidatos. Existe un pilot PTB-XL real validado para ingeniería de pipeline (sin métricas); el fold 10 completo de prevalencia natural está en construcción. No existe todavía una evaluación diagnóstica ciega finalizada que permita afirmar sensibilidad/especificidad.

## Estado autoritativo actual
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


## Punto de continuidad — 02/10/2026 17:06
- Rama: `v1.36-consolidation`.
- Estado recalculado: **127 módulos / 127 registros de evidencia / 29 green / 98 yellow / 0 red**.
- Último estado QA verificado al corte: **151 tests PASS**; último workflow `Clinical QA` observado: **success**.
- Fase 4 pediátrica ampliamente desarrollada: medicación por peso, perfusiones/bolos, fluidoterapia, asma, RSI, electrolitos, hemoderivados, sedación procedimental, antibióticos por síndrome y alta.
- Pediatría no requiere protocolo local de Horta como gate; se apoya en guías internacionales vigentes, SmPC y fuentes pediátricas reconocidas.
- Fase 5 imagen iniciada con contrato ciego v1.1, métricas fail-closed, generador de manifiestos y candidatos PTB-XL, RSNA ICH, CheXpert/MIMIC-CXR y EchoNet. Aún no existe dataset real suficiente para claims de precisión.
- Handoff para nuevo hilo actualizado en `clinical/HANDOFF_PROMPT.md`.
- Siguiente paso recomendado: primer dataset real autorizado/desidentificado con referencia independiente, freeze de manifest antes de labels y ejecución ciega; o revisión humana de high-risk yellow si se prioriza consolidación clínica.


## Avance Fase 5 — 02/10/2026
- Nuevo gate de admisión de fuentes: `qa/image-dataset-source-registry.json` + `scripts/validate_image_dataset_source.py`.
- PTB-XL queda **intake-ready** tras congelar protocolo fold 10 y separación de referencia: `qa/PTBXL_BLINDED_PROTOCOL.md` + `scripts/prepare_ptbxl_blinded_cohort.py`.
- No se han importado todavía casos reales al banco final y no se calculan métricas clínicas.
- Estado clínico/evidencia sin cambios: **127 módulos / 127/127 evidencia / 29 green / 98 yellow / 0 red**.
- El archivo de tests contiene **159 funciones de test** tras este bloque. El último run completo previamente confirmado sigue siendo **151 PASS**; los nuevos tests requieren confirmación por GitHub Actions antes de documentarlos como PASS.
- Fase 4 pediátrica sigue bloqueada únicamente por revisión humana pediatría/farmacia; se añadió `qa/PEDIATRIC_HUMAN_REVIEW_READINESS.md` sin auto-promoción a green.

- Workflow manual real añadido: `.github/workflows/ptbxl-blinded-intake.yml`. Descarga metadatos PTB-XL v1.0.3, valida el gate de fuente, genera salt efímero si no hay secreto configurado, descarga solo los waveforms seleccionados y separa artefacto ciego de referencia sellada.
- Render digital congelado con divisiones 0,04 s / 0,1 mV; no se afirma calibración física mm/s o mm/mV.
- PR draft de validación creado: **#12 — v1.36 consolidation — validation only (do not merge)**. No modifica ni promueve `main`.
- GitHub todavía no expone un run de Clinical QA para el nuevo head; por tanto el último run completo confirmado sigue siendo **151 PASS**.

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
