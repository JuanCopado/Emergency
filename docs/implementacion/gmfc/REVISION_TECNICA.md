# GMFC-TECH — inventario técnico independiente

**Propuesta de estudio; no implementación ni aceptación de la guía.** Estado: CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE.

La mayor parte de los motores, catálogos, nota, exportadores y guardas es reutilizable. La superficie unificada FAST/NOTE/TREATMENT/DISCHARGE/TESTS y la continuidad multiepisodio no están implementadas como contrato integral. Conviene consolidar primero ese contrato y conservar los módulos existentes. No se necesita imponer servidores, PostgreSQL, autenticación remota, un LLM ni interoperabilidad hospitalaria al producto individual.

## Identidad, método e independencia

Fuente exacta PR142 `ecacffee5cdd67992e01e3913e8a0682b3b96ca3`, árbol `a61801d71ae5e2b1576f48c2d62d4a77d32ff5e4`, rama aislada `work/gmfc-study-20261128`. El diff frente al receptor M `50ef5ee684e85dd769255445e78f2f12c40a266c` contiene únicamente IMPLEMENTACION.md, GUIA_MAESTRA_FLUJO_CLINICO.md y ORQUESTACION_GUIA_MAESTRA.json. No es una nueva versión clínica de la aplicación. En el corte de entrada, kit H/parche `6a1dcbd971c864f06d5ee66d0989d0709f51379c` de PR141 estaba separado de M. El coordinador comunicó después la fusión autorizada; véase ADDENDUM_SCOPE.json. No se cambió el source del estudio.

Lectura de encargo, AGENTS, STATE, CODEX, instrucciones clínicas, IMPLEMENTACIÓN, ambas orquestaciones, guía y fuentes canónicas; inspección de código, JSON, rutas e informes previos. Matriz C42 sólo leída en el corte inicial; no se presenta como matriz inmutable del futuro. No se leyeron resultados nuevos Claude/Gemini, ni se compartieron conclusiones con esas dos líneas antes de esta entrega. No se ejecutaron pruebas, motores, UI, scanner, paquete o campaña de medición. No se editaron fuentes ni Git. Los hashes se calculan sobre bytes; son integridad documental, no QA clínica. Se conservaron rutas de lecturas fallidas como errores de navegación del lector, no como fallos del producto.

`STATIC_READ` demuestra contrato/código visible; `PRIOR_QA_REUSED` identifica ensayo histórico y alcance; `NO_VERIFICADO` marca cobertura que no se midió o evidencia no disponible. Ninguna lectura estática se etiqueta como PASS de ejecución. Las condiciones de aceptación siguientes son propuestas para una implementación futura, no resultados.

## Contratos y decisiones que deben conservarse

- Los **19 contratos** proceden de `clinical/qa/REVIEWED_ACUTE_CONTRACT_RELEASE_2026-11-16.md:5` (seis numéricos y trece de apoyo) y del JSON `clinical/references/acute-contract-owner-acceptance-2026-11-16.json`, que enumera los 19 IDs y la aceptación expresa. No son 19 nuevas solicitudes médicas ni implican validación prospectiva. No se reejecutaron sus motores.
- Las **45 fórmulas** están en `clinical/calculators/registry.json`; `clinical/scripts/clinical_calculator.py:87` contiene el dispatcher determinista. La decisión `clinical/qa/CALCULATOR_DECISION_20261120.md:3` y `clinical/modules/clinical-scores-calculators.md:65` distinguen 45 fórmulas, 135 escalas y **13 formularios** aprobados: no se puede presentar todo como 135 calculadoras FAST ejecutables. Los tipos externos sin contrato específico se abstienen.
- Preparaciones farmacológicas no identificadas siguen bloqueadas; no inferir insulina/labetalol originales. MED-DEC-R46-01/02, decisiones dermatológicas y dos YELLOW no se reabren aquí. No se renueva `last_checked` ni se crea una pregunta médica a partir de este inventario.
- El registro de evidencia del source normalizado UTF-8 LF coincide con el hash informado de la llamada real del coordinador a MCP: `3a60b719633ed49c16d9b05758711d5eab9e954986012625abc58d492d6d6f8c`. El snapshot MCP `3cc5139b149feef390e6ceaa7358e2425d92620a` y sus 131 módulos/129 GREEN/2 YELLOW son metadatos; no prueba de CI viva, aprobación global o disponibilidad de cada herramienta en cada distribución.

## Cuatro distinciones que la guía debe hacer inequívocas

1. **Texto final y exportación.** `FreeTextWorkspace.tsx:78` copia el final editable y `:191` avisa del límite. `ClinicalNote.tsx:505` y `:634` exportan PDF/DOCX/JSON desde el modelo canónico revisado. No son automáticamente el mismo documento. Elegir explícitamente qué versión será la revisada/exportable antes de prometer una única acción. La modificación debe invalidar la revisión pertinente, sin hacer parecer que el contenido final editado ya se exporta.
2. **Apoyo diagnóstico y YELLOW.** La guía dice «interpretación YELLOW deshabilitada» en líneas 21/40, pero `ClinicalNote.tsx:589` y `clinical_note_api.py:475,611` conservan apoyo determinista limitado y análisis con guardas. Reformular esa frase por capacidad y nivel de validación, preservando funcionalidad limitada aceptada. La recepción de archivo no equivale a interpretación, y no se habilita inferencia remota o diagnóstico validado por este estudio.
3. **Continuidad y durabilidad.** `clinical-note/draft.tsx:58` documenta un único episodio en memoria mientras vive el árbol. `settings.tsx:68–78` guarda preferencias, no historias. Guardar borrador durante una actualización o D→E→D no acredita Mi guardia, persistencia tras cerrar ni aislamiento entre pacientes A/B/A. Un futuro modelo multiepisodio necesita contrato propio, no un cambio de etiqueta sobre el estado actual.
4. **Existencia y distribución.** `backend_runtime.py:23` delimita endpoints empaquetados: agudos/scores/pediatría/nota y analyze limitado, pero no upload/interpret, T05 ni T06. `STABLE_PWA.md:31–33` distingue frontend cacheado, backend local activo y capacidades ausentes. `BloodGas.tsx:69,73,143` requiere sesión/ticket/revisión; no prueba una gasometría manual autónoma offline. `t06/T06Lab.tsx:123,131` ya explica y deshabilita el laboratorio ausente.

## Capacidad reutilizable por área

La tabla siguiente resume; la matriz JSON contiene cada requisito con fuente y localizador, guarda, límite y criterio negativo.

| Área | Situación | Reutilización y brecha principal |
|---|---|---|
| E1 FAST | PARCIAL | Rutas, buscador de catálogo, formularios y motores existentes. Pendientes router de intención universal y dictado con confirmación. |
| E2 NOTE | PARCIAL | Tres etapas, aplicación a campos y exportadores existentes. Contrato de final editable/exportación exacta y plantillas completas por consolidar. |
| E3 TREATMENT | PARCIAL | Plan con cinco secciones, source SHA y revisión. Proyección de referencia no equivale a prescriptor universal personalizado ni motor global de interacciones. |
| E4 DISCHARGE | PARCIAL | Catálogo/alertas/exportadores pediátricos. No inferir alta, edad, indicación, producto o duración; separar documento profesional e instrucciones. |
| E5 TESTS | PARCIAL / RESTRINGIDO por capacidad | PDF textual/TXT y confirmación existentes; OCR/T05/T06/modelos/ECG/DICOM dependen de contrato y distribución. |
| E6 Alertas y actualizaciones | PARCIAL | Guardas y dirty-update existentes; centro universal de alertas y seguimiento científico no acreditados. |
| E7 Mi guardia | PENDIENTE como flujo integral | Un draft en memoria no es gestor de episodios. Persistencia/transferencia selectiva deben decidirse explícitamente. |
| E8 Identidad y UX | PARCIAL | Layout, temas, idioma, ClinicalMinimal opt-in y componentes reutilizables. WCAG2.2AA/rendimiento global sin nueva medición. |

## Arquitectura y datos imprescindibles

Conservar catálogo/motor como única fuente ejecutable y adaptar entradas a IDs/revisiones existentes. Un futuro router FAST sólo seleccionaría contrato, presentaría lo detectado y pediría lo imprescindible definido por éste; no genera cifras ni decide diagnóstico. Distinguir consulta sin episodio de transferencia deliberada al episodio activo. El origen del dato —médico, extracción confirmada, motor, referencia o desconocido— debe viajar con el dato; no rellenar desconocido como negativo.

Reutilizar `therapeutic_plan_sources.py:286,329` como plan parcial de fuente y `therapeutic_plan_workflow.py:116,195,216` como revisión de identidad/contexto. Campos clínicos mínimos dependen de intención y régimen: no imponer siempre embarazo/renal/hepático/edad/peso y tampoco omitirlos cuando el contrato los requiere. Una limitación del motor de interacciones se muestra «no evaluado», no «sin interacciones».

Mantener internacional por defecto (`reference-context.ts:19,26`), sin deducir país de idioma o disponibilidad de marca. La UI traducida no prueba traducción clínica completa (`ClinicalNote.tsx:660`). Persistencia de preferencias no autoriza persistir pacientes en localStorage. Si el propietario acepta continuidad durable, definir finalidad, retención, borrado y recuperación antes de elegir almacenamiento; PostgreSQL/servidor/OIDC permanecen opcionales.

MCP es laboratorio local de ocho herramientas de metadatos y documentación (`tools/emergency-mcp/README.md:31,50,77`), no backend de pacientes ni puente universal de ejecución. RAG/interop son capacidades experimentales separadas (`INTEGRACION_TOTAL_V07.md:38–42`). No ampliar sus dependencias para resolver navegación o notas.

## Reutilización de PR139/140 y QA anterior

PR140 integró el texto libre de PR139 y reparaciones focales, conservando Unicode y contenido (`CONCILIACION_PR138_PR139.md:9,17`). Seleccionó los cambios técnicos `1f031d6` y `21f5eb9`; **excluyó `1627033`** de portada/logo/iconos. No asumir que la portada posterior de PR139 está integrada o aceptada. ClinicalMinimal es opt-in `Home.tsx:17`, no sustitución global automática.

El source registra 23 regresiones focales, QA de siete pasos y exportaciones/comparativo tablet como evidencia histórica del alcance probado. Esta revisión no repite ni amplía esos PASS. La copia C41 D→E→D y su focal de workspace son reutilizables para el código sin cambios: borradores, preferencias, stale guard y PWA instalada en la configuración ensayada. El manifiesto adjunto identifica recibos físicos y hashes; no transforma esos resultados en prueba de continuidad multiepisodio, rendimiento de guardia, WCAG o todas las plataformas.

La recuperación bootstrap H se mantiene fuera del estudio: conserva verificación estricta y E original; su estado propuesto en el corte inicial de PR141 no modifica fórmulas ni justifica reconstruir/refirmar paquetes para este inventario. No reabrir STOP histórico de E como bloqueo vigente cuando C41/C42 ya documentan recuperación aceptada en copia.

## Secuencia propuesta, usando los doce IDs existentes

1. **IMP-00 / IMP-02:** consolidar matriz de capacidad y resolver lenguaje de los cuatro contratos ambiguos anteriores; separar requisito directo del propietario de sugerencia. Sin nueva cola ni decisiones clínicas repetidas.
2. **IMP-10:** guía v1 propuesta con decisiones ADOPTAR/REFORMULAR/APLAZAR/DESCARTAR; revisión de los tres estudios independientes y Antigravity de esa síntesis exacta. Este informe no selecciona diseño ni da aceptación del propietario.
3. Después de aceptación, reutilizar rutas/componentes para el menor flujo completo seleccionado. Adaptador de intención sólo a contratos ya existentes; no desplegar simultáneamente FAST universal y persistencia multiepisodio sin contrato. La secuencia es criterio de reutilización, no autorización de desarrollo.
4. **IMP-09:** negativos y comparación acotada del flujo que cambie; **IMP-03** sólo si cambia el paquete/instalación. IMP-04–08 remotos permanecen condicionales; no imponerlos. **IMP-11** conserva autorización separada; nada de este informe permite promoción clínica o despliegue.

## Criterios medibles futuros, sin campaña innecesaria

- FAST: suficiente/incompleto/ambiguo; comparación exacta contra ID/revisión/resultado manual; sin cifra con preparación o unidad crítica desconocida. Voz exige readback antes del motor y fallback manual.
- NOTE: original íntegro, negación, Unicode, unidades, texto largo, deduplicación sólo exacta según contrato, edición revoca revisión, reaplicar no pierde contenido. PDF/DOCX se cotejan contra la versión explícitamente elegida, no contra una copia distinta.
- TESTS: muestra/página/fecha/unidad y discrepancias; valores dudosos no pasan al cálculo sin confirmación. Indisponibilidad no deja spinner permanente ni simula análisis.
- Episodios: A/B/A, consulta rápida fuera de nota, transferencia selectiva y dos pestañas; cero mezcla en los casos ensayados. No extrapolar ausencia de mezcla a durabilidad o certificación universal.
- UX: misma tarea/datos/configuración; tiempo inicio→primer resultado útil, acciones, correcciones, errores y carga percibida. Comparación sólo con mediciones comparables, contando preparación/llamadas/salida; sin SLA o porcentaje inventado. No recolectar PHI/audio real para medir.
- Accesibilidad: teclado/lector/foco, contraste, texto además de color, tamaño táctil, escritorio/tablet/móvil y temas. Lo existente (skiplink/focus/reduced-motion) es base, no dictamen AA.

## Disposición técnica

**ADOPTAR:** reutilizar contratos, fuentes, exportadores canónicos, guardas, layout y preferencias; trazabilidad y abstención específica por capacidad.

**REFORMULAR:** final libre vs exportación, YELLOW vs apoyo determinista limitado, continuidad vs persistencia, y offline vs backend ausente. Son contradicciones de contrato/documentación, no autorizaciones para cambiar clínica.

**APLAZAR:** proveedores de voz/LLM, infraestructura remota, persistencia durable y nuevas plantillas no imprescindibles hasta aceptar alcance y demostrar utilidad. No son requisitos hospitalarios del núcleo individual.

**DESCARTAR:** duplicar motores/catálogos, generar dosis, inferir preparación original o país, declarar conformidad global por pruebas focales y pedir de nuevo aprobaciones ya concedidas.

No se encontró un impedimento técnico que exija reconstruir Emergency; sí hay brechas reales de flujo integral. La guía debe quedarse como propuesta hasta las otras entregas, síntesis, auditoría y aceptación del propietario. No se emite GO clínico, MERGE_READY ni nueva pregunta médica en esta revisión.

## Requisitos detallados

### E1.01 — Acceso rápido a herramientas existentes

**EXISTENTE · STATIC_READ · ADOPTAR.** Rutas separadas de fármacos, calculadora, agudos, pediatría, procedimientos, nota, gasometría y guías. No constituyen una pantalla FAST universal ni clasifican intención clínica libre.

Fuentes: `app/src/App.tsx:31`; `app/src/pages/Home.tsx:63`; `app/src/pages/DrugList.tsx:32`.

Criterio propuesto, no ejecutado: Comparar entradas actuales con un acceso conceptual sin duplicar motores; conservar navegación directa. Vinculación: IMP-00, IMP-09, IMP-10.

### E1.02 — Texto libre a intención y contrato ejecutable

**PENDIENTE · STATIC_READ · REFORMULAR.** Buscador filtra catálogo; APIs aceptan identificadores y entradas explícitas. No existe un router clínico universal de lenguaje natural; un helper aritmético no prueba este flujo.

Fuentes: `app/src/pages/DrugList.tsx:32`; `clinical/scripts/acute_medication_api.py:265`; `clinical/scripts/clinical_scores_api.py:92`.

Criterio propuesto, no ejecutado: Intención suficiente resuelve ID canónico/revisión/inputs; ambigüedad o dato crítico ausente bloquea cifra y muestra causa. Igual salida que entrada manual. Vinculación: IMP-00, IMP-09, IMP-10.

### E1.03 — Voz con confirmación de cifras y unidades

**PENDIENTE · STATIC_READ · REFORMULAR.** Entrada manual y formularios existentes; búsqueda acotada no halló SpeechRecognition/MediaRecorder/getUserMedia en app/src ni clinical/scripts. No se verificó micrófono, proveedor ni soporte del navegador. No hay transcripción universal acreditada.

Fuentes: `app/src/pages/Home.tsx:70`; `docs/implementacion/GUIA_MAESTRA_FLUJO_CLINICO.md:30`.

Criterio propuesto, no ejecutado: Mantener entrada manual; antes de cálculo confirmar decimal, unidad, edad/peso, vía y negación; medir dispositivo real después de aceptar alcance. Vinculación: IMP-00, IMP-09, IMP-10.

### E1.04 — Datos mínimos y abstención por contrato

**EXISTENTE · STATIC_READ · ADOPTAR.** Agudos valida revisión, campos permitidos y requisitos; pediatría usa guardas propias. No exigir todos los campos a todos los casos ni inventar la preparación original de insulina/labetalol.

Fuentes: `clinical/scripts/acute_medication_api.py:115`; `clinical/scripts/acute_medication_api.py:269`; `clinical/scripts/pediatric_outpatient_alert_engine.py:70`.

Criterio propuesto, no ejecutado: Reutilizar contrato exacto; casos incompleto, unidad incompatible, preparación no identificada y revisión obsoleta no emiten una cifra accionable. Vinculación: IMP-00, IMP-02, IMP-09.

### E1.05 — 45 fórmulas disponibles desde FAST

**PARCIAL · STATIC_READ · REFORMULAR.** Registro contiene 45 fórmulas de motor y 135 escalas; API de scores expone 13 formularios aprobados. 45 fórmulas implementadas no significa 45 formularios ni 135 calculadoras universales disponibles.

Fuentes: `clinical/calculators/registry.json:1`; `clinical/scripts/clinical_calculator.py:87`; `clinical/scripts/clinical_scores_api.py:47`; `clinical/qa/CALCULATOR_DECISION_20261120.md:3`.

Criterio propuesto, no ejecutado: Mapear únicamente fórmulas/formularios existentes a inputs conocidos; identificador no expuesto o regla externa sin contrato se abstiene. Vinculación: IMP-00, IMP-09, IMP-10.

### E2.01 — Original / propuesta / final de texto libre

**EXISTENTE · STATIC_READ · ADOPTAR.** Workspace conserva tres etapas y propone aplicación separada a campos canónicos. Estructuración por encabezados no interpreta clínicamente todo texto libre ni completa datos ausentes.

Fuentes: `app/src/clinical-note/FreeTextWorkspace.tsx:23`; `app/src/clinical-note/textStructuring.ts:91`; `app/src/pages/ClinicalNote.tsx:532`.

Criterio propuesto, no ejecutado: Preservar original, cifras, Unicode y negación; reaplicar no elimina fragmentos por substring ni sobrescribe sin decisión. Vinculación: IMP-00, IMP-09, IMP-10.

### E2.02 — Edición final y exportación exacta revisada

**PARCIAL · STATIC_READ · REFORMULAR.** Final editable se copia con clipboard; PDF/DOCX/JSON se generan desde campos canónicos revisados. El final libre editado no es automáticamente el documento exportado. No afirmar igualdad entre ambas superficies.

Fuentes: `app/src/clinical-note/FreeTextWorkspace.tsx:78`; `app/src/clinical-note/FreeTextWorkspace.tsx:191`; `app/src/pages/ClinicalNote.tsx:505`; `app/src/pages/ClinicalNote.tsx:634`; `clinical/scripts/clinical_note_exporter.py:338`.

Criterio propuesto, no ejecutado: Elegir contrato explícito antes de implementar: canónico revisado o nuevo final revisado. Ensayar igualdad de contenido del documento elegido y aviso inequívoco para copia en borrador. Vinculación: IMP-00, IMP-09, IMP-10.

### E2.03 — Revisión invalidada por edición

**EXISTENTE · STATIC_READ · ADOPTAR.** touch invalida revisiones; cambios y regeneración exigen confirmación en workspace. No acredita invalidación transitiva universal entre futuros módulos o episodios.

Fuentes: `app/src/pages/ClinicalNote.tsx:230`; `app/src/clinical-note/FreeTextWorkspace.tsx:53`; `app/src/clinical-note/FreeTextWorkspace.tsx:71`.

Criterio propuesto, no ejecutado: Editar dato dependiente retira revisión/feedback anterior; una propuesta vieja no vuelve a figurar como aceptada. Vinculación: IMP-00, IMP-09, IMP-10.

### E2.04 — Plantillas de todos los tipos de nota

**PARCIAL · STATIC_READ · REFORMULAR.** Existe nota con historia, exploración, pruebas, problemas, plan, exportación y campos de episodio. No está acreditado un catálogo completo de ocho plantillas ni deshacer/restaurar histórico general.

Fuentes: `app/src/pages/ClinicalNote.tsx:238`; `app/src/clinical-note/draft.tsx:6`; `app/src/clinical-note/textStructuring.ts:131`.

Criterio propuesto, no ejecutado: Usar mismo modelo canónico; documentar variaciones de plantilla sin inferir exploración normal ni negativos no aportados. Vinculación: IMP-00, IMP-09, IMP-10.

### E2.05 — Adjuntos con procedencia y confirmación

**PARCIAL · STATIC_READ · REFORMULAR.** Prepare/accept de adjuntos y datos fuente; UI acepta varios formatos con revisión. Aceptar extensión o extraer metadatos no valida estructura PDF/DICOM, diagnóstico ni admisión del activo al banco.

Fuentes: `clinical/scripts/clinical_note_api.py:580`; `clinical/scripts/clinical_note_api.py:603`; `app/src/pages/ClinicalNote.tsx:371`; `app/src/pages/ClinicalNote.tsx:551`.

Criterio propuesto, no ejecutado: Vincular campo confirmado a página/fecha/unidad/origen cuando exista; conflictos no se sobrescriben. No afirmar retención del binario original cuando el contrato sólo conserva recibo/referencia. Vinculación: IMP-00, IMP-09, IMP-10.

### E2.06 — Diagnóstico determinista y módulos YELLOW

**RESTRINGIDO · STATIC_READ · REFORMULAR.** analyze y apoyo diagnóstico determinista están presentes; la API añade guarda de seguridad de medicamentos. La guía dice deshabilitar YELLOW, pero eso no describe fielmente toda la UI existente. No ampliar a diagnóstico validado o inferencia remota ni deshabilitar por estudio capacidades limitadas ya aceptadas.

Fuentes: `app/src/pages/ClinicalNote.tsx:589`; `clinical/scripts/clinical_note_api.py:475`; `clinical/scripts/clinical_note_api.py:611`; `docs/implementacion/GUIA_MAESTRA_FLUJO_CLINICO.md:21`.

Criterio propuesto, no ejecutado: Reformular guía diferenciando apoyo determinista limitado, extracción, inferencia nueva y aprobación clínica. Mantener exactamente los gates vigentes y dos YELLOW. Vinculación: IMP-00, IMP-02, IMP-10.

### E3.01 — Plan para diagnóstico establecido

**PARCIAL · STATIC_READ · REFORMULAR.** Plan organiza initial_actions, medications, monitoring, reassessment, disposition desde fuentes identificadas. Es proyección conservadora de fuente, no plan personalizado completo para cualquier diagnóstico.

Fuentes: `clinical/scripts/therapeutic_plan_sources.py:20`; `clinical/scripts/therapeutic_plan_sources.py:286`; `clinical/scripts/therapeutic_plan_sources.py:329`.

Criterio propuesto, no ejecutado: Distinguir referencia, plan parcial y propuesta individualizada; diagnóstico establecido por médico no equivale a diagnóstico generado. Vinculación: IMP-00, IMP-09, IMP-10.

### E3.02 — Procedencia y revisión del plan

**EXISTENTE · STATIC_READ · ADOPTAR.** Fuentes se atan a SHA; validación comprueba identidad, selección, alergias y confirmaciones. No transportar aprobación a una fuente cambiada ni extrapolar a todos los planes.

Fuentes: `clinical/scripts/therapeutic_plan_sources.py:194`; `clinical/scripts/therapeutic_plan_workflow.py:116`; `clinical/scripts/therapeutic_plan_workflow.py:195`; `clinical/scripts/therapeutic_plan_workflow.py:216`.

Criterio propuesto, no ejecutado: Cambio de fuente/contexto relevante exige revalidación; IDs diagnósticos no coincidentes se rechazan. Vinculación: IMP-00, IMP-09, IMP-10.

### E3.03 — Interacciones y seguridad global de medicación

**PARCIAL · STATIC_READ · REFORMULAR.** Motor pediátrico contempla alergias, conciliación y datos mínimos; existe medication/preflight central. Cobertura global de interacciones de cualquier medicamento/diagnóstico no demostrada. Ausencia de alerta no significa sin interacciones.

Fuentes: `clinical/scripts/pediatric_outpatient_alert_engine.py:89`; `clinical/scripts/pediatric_outpatient_alert_engine.py:95`; `clinical/scripts/clinical_note_api.py:622`.

Criterio propuesto, no ejecutado: Mostrar evaluado/no evaluado por cobertura real; no ocultar STOP y no añadir cifras fuera de contrato. Vinculación: IMP-00, IMP-02, IMP-09.

### E3.04 — 19 contratos clínicos previamente aceptados

**EXISTENTE · STATIC_READ · ADOPTAR.** Recepción explícita del propietario: seis contratos numéricos y trece de apoyo; JSON enumera 19 IDs. No exigir otra aprobación médica general ni tratar los 19 como nuevas dosis. No implica validación prospectiva.

Fuentes: `clinical/qa/REVIEWED_ACUTE_CONTRACT_RELEASE_2026-11-16.md:5`; `clinical/qa/REVIEWED_ACUTE_CONTRACT_RELEASE_2026-11-16.md:9`; `clinical/references/acute-contract-owner-acceptance-2026-11-16.json:1`.

Criterio propuesto, no ejecutado: Conservar IDs, cifras, guardas y aceptación; comprobar equivalencia sólo si futura integración modifica su contrato. Vinculación: IMP-00, IMP-02, IMP-09.

### E4.01 — Alta pediátrica sobre catálogo existente

**PARCIAL · STATIC_READ · REFORMULAR.** Ruta pediátrica, calculadores, alertas y exportador propios disponibles. No es un generador universal de alta. Peso solo no establece edad, indicación, producto, duración ni destino.

Fuentes: `app/src/App.tsx:39`; `clinical/scripts/pediatric_outpatient_api.py:1`; `clinical/scripts/pediatric_outpatient_alert_engine.py:70`; `clinical/scripts/pediatric_outpatient_calculator.py:1`.

Criterio propuesto, no ejecutado: Caso sintético 7 kg conserva edad desconocida y no inventa antibiótico/preparación; usar sólo régimen autorizado y revisión de datos pertinentes. Vinculación: IMP-00, IMP-02, IMP-09.

### E4.02 — Instrucciones paciente vs informe profesional

**PENDIENTE · STATIC_READ · REFORMULAR.** Nota y exportadores clínicos reutilizables; alertas por régimen. No consta contrato integral de dos documentos separados para toda alta, educación y signos de alarma multilingües.

Fuentes: `clinical/scripts/clinical_note_exporter.py:128`; `clinical/scripts/pediatric_result_exporter.py:1`.

Criterio propuesto, no ejecutado: Separar documento profesional de instrucciones legibles; no asumir decisión de alta ni alta automática a partir de cálculo. Vinculación: IMP-00, IMP-09, IMP-10.

### E4.03 — Conversión segura a mL y formulaciones

**RESTRINGIDO · STATIC_READ · ADOPTAR.** Contratos exigen preparación/producto cuando corresponde y bloquean datos insuficientes. Preparaciones no identificadas continúan bloqueadas; no inferir originales de insulina/labetalol por versiones genéricas.

Fuentes: `clinical/scripts/acute_medication_api.py:63`; `clinical/scripts/acute_medication_api.py:115`; `clinical/scripts/pediatric_outpatient_alert_engine.py:70`.

Criterio propuesto, no ejecutado: Sin concentración/producto necesarios no mostrar mL accionables; conservar equivalencia dimensional y fuente. Vinculación: IMP-00, IMP-02, IMP-09.

### E5.01 — Importación de analítica PDF textual/TXT

**EXISTENTE · STATIC_READ · ADOPTAR.** ScoreDocumentInput extrae texto PDF/TXT, muestra fuente y candidatos antes de aplicación. PDF escaneado requiere alternativa manual; extracción no equivale a interpretación o precisión clínica validada.

Fuentes: `app/src/components/ScoreDocumentInput.tsx:32`; `app/src/components/ScoreDocumentInput.tsx:42`; `app/src/components/ScoreDocumentInput.tsx:61`; `clinical/qa/CALCULATOR_DECISION_20261120.md:18`.

Criterio propuesto, no ejecutado: Valores, unidades y muestra se revisan; discrepancia de unidad o múltiples resultados no selecciona silenciosamente. Vinculación: IMP-00, IMP-09, IMP-10.

### E5.02 — Gasometría T05 en instalación individual

**RESTRINGIDO · STATIC_READ · REFORMULAR.** Página y servicio local T05 existen; exige sesión Windows, revisión de filas, muestra y confirmación médica. No está empaquetado en E. Esta página no demuestra calculadora manual autónoma offline: requiere ticket/sesión del servicio.

Fuentes: `app/src/pages/BloodGas.tsx:69`; `app/src/pages/BloodGas.tsx:73`; `app/src/pages/BloodGas.tsx:143`; `app/src/pages/BloodGas.tsx:261`; `tools/local-installation/backend_runtime.py:23`.

Criterio propuesto, no ejecutado: Mostrar capacidad real; no intentar servicio ausente. Si se propone alternativa manual, identificar su motor/contrato y autorización por separado. Vinculación: IMP-00, IMP-09, IMP-10.

### E5.03 — T06 en paquete y plataforma incompatible

**RESTRINGIDO · STATIC_READ · ADOPTAR.** Meta de instalación individual deshabilita botón y avisa de backend ausente; Linux condicionado en otros modos. No ampliar laboratorio opcional ni repetir control ya acreditado de indisponibilidad.

Fuentes: `app/src/t06/T06Lab.tsx:59`; `app/src/t06/T06Lab.tsx:123`; `app/src/t06/T06Lab.tsx:131`.

Criterio propuesto, no ejecutado: Conservar aviso y cero solicitud cuando runtimeUnavailable; no presentar laboratorio listo en paquete E. Vinculación: IMP-00, IMP-09, IMP-10.

### E5.04 — ECG/TAC/DICOM e interpretación de imágenes

**RESTRINGIDO · STATIC_READ · REFORMULAR.** Hay recepción técnica, apoyos documentales y referencia a imágenes. Upload/interpret no está en allowlist del backend individual. Original/miniatura/derivado, aceptación técnica y adjudicación médica son estados distintos.

Fuentes: `app/src/pages/ClinicalNote.tsx:390`; `clinical/scripts/clinical_note_api.py:596`; `tools/local-installation/backend_runtime.py:23`; `docs/implementacion/INTEGRACION_TOTAL_V07.md:41`.

Criterio propuesto, no ejecutado: No mostrar diagnóstico validado por extensión aceptada; exponer capacidad exacta, abstención y procedencia; mantener cuarentena y admisiones previas. Vinculación: IMP-00, IMP-09, IMP-10.

### E5.05 — POCUS, RAG y referencias

**PARCIAL · STATIC_READ · REFORMULAR.** POCUS dispone de referencias; RAG es laboratorio de recuperación sin generación clínica ni endpoint de pacientes. No hay justificación para extender RAG a prescriptor ni incorporar originales restringidos. Cifras históricas del banco no son reconciliación nueva.

Fuentes: `docs/implementacion/INTEGRACION_TOTAL_V07.md:38`; `docs/implementacion/INTEGRACION_TOTAL_V07.md:41`; `docs/implementacion/INTEGRACION_TOTAL_V07.md:65`.

Criterio propuesto, no ejecutado: Acceso a referencia con fuente/estado; no promover imagen a admitida ni una recuperación documental a consejo clínico validado. Vinculación: IMP-00, IMP-02, IMP-10.

### E6.01 — Alertas clínicas existentes y revisión

**PARCIAL · STATIC_READ · REFORMULAR.** Guardas de contrato, alergias, datos mínimos y revisión de medicamentos existen en módulos. No consta un centro universal de alertas por episodio con deduplicación y invalidación entre todas las herramientas.

Fuentes: `clinical/scripts/acute_medication_api.py:276`; `clinical/scripts/pediatric_outpatient_alert_engine.py:64`; `app/src/pages/ClinicalNote.tsx:670`.

Criterio propuesto, no ejecutado: Crítica, precaución e información deben conservar texto y acción; deduplicar sin ocultar advertencia obligatoria, con alcance de episodio explícito. Vinculación: IMP-00, IMP-09, IMP-10.

### E6.02 — Actualización PWA con borrador abierto

**EXISTENTE · STATIC_READ · ADOPTAR.** Aviso bloquea actualización con contenido; guard preserva instancia en navegación y evita rutas inéditas stale. No confundir guard de actualización con persistencia tras cierre del navegador o durabilidad ante fallo del SO.

Fuentes: `app/src/components/LocalUpdateNotice.tsx:30`; `app/src/components/LocalUpdateNotice.tsx:32`; `app/src/components/IndividualRouteGuard.tsx:39`; `app/src/components/IndividualRouteGuard.tsx:70`.

Criterio propuesto, no ejecutado: Reutilizar evidencia C41 para código sin cambios; futuros cambios sólo verifican transición afectada y no pierden borrador/prefs. Vinculación: IMP-00, IMP-03, IMP-09.

### E6.03 — Avisos de nueva guía o cambios científicos

**PENDIENTE · STATIC_READ · REFORMULAR.** Fuentes canónicas y revisiones/hash permiten reconocer identidad. No consta servicio universal de alertas científicas ni revisión automática autorizada. No renovar last_checked por estudio.

Fuentes: `clinical/scripts/therapeutic_plan_sources.py:176`; `docs/implementacion/GUIA_MAESTRA_FLUJO_CLINICO.md:99`.

Criterio propuesto, no ejecutado: Nueva versión se muestra como pendiente de revisión, no reemplaza pauta vigente ni crea aprobación implícita. Vinculación: IMP-00, IMP-02, IMP-10.

### E6.04 — Privacidad local, sesiones y red

**PARCIAL · STATIC_READ · REFORMULAR.** Host/Origin/nonce, loopback, worker privado y temporales marcados; privacidad/exportación preflight. Loopback no aísla frente a cualquier proceso del mismo usuario. Limpieza normal no equivale a borrado seguro ni a eliminar exportaciones guardadas.

Fuentes: `tools/local-installation/STABLE_PWA.md:29`; `tools/local-installation/backend_runtime.py:46`; `tools/local-installation/backend_runtime.py:71`; `clinical/scripts/clinical_note_api.py:573`.

Criterio propuesto, no ejecutado: No datos identificables remotos por defecto; reutilización de datos necesita origen, episodio, finalidad y selección explícitos. Vinculación: IMP-00, IMP-02, IMP-09.

### E7.01 — Mi guardia: múltiples episodios y retorno A/B/A

**PENDIENTE · STATIC_READ · REFORMULAR.** Provider usa un único draft en memoria, con reset y beforeunload. No hay gestor multiepisodio acreditado. A/B/A de versiones PWA no es A/B/A de pacientes.

Fuentes: `app/src/clinical-note/draft.tsx:55`; `app/src/clinical-note/draft.tsx:58`; `app/src/clinical-note/draft.tsx:60`; `app/src/clinical-note/draft.tsx:69`.

Criterio propuesto, no ejecutado: Modelo de episodio explícito, aislamiento A/B/A y prohibición de arrastre automático; probar cambio de paciente y consulta rápida sin episodio después de aceptación. Vinculación: IMP-00, IMP-09, IMP-10.

### E7.02 — Persistencia de notas entre sesiones

**PENDIENTE · STATIC_READ · REFORMULAR.** Preferencias se guardan; draft clínico se destruye al cerrar la página. Memoria React no es recuperación durable ni almacenamiento cifrado de episodios. PostgreSQL no es requisito automático.

Fuentes: `app/src/clinical-note/draft.tsx:58`; `app/src/state/settings.tsx:68`; `app/src/state/settings.tsx:74`.

Criterio propuesto, no ejecutado: Decidir por separado persistencia, retención y eliminación con privacidad; no almacenar pacientes en localStorage por reutilizar preferencias. Vinculación: IMP-00, IMP-02, IMP-10.

### E7.03 — Offline de funciones compatibles

**PARCIAL · STATIC_READ · REFORMULAR.** PWA cachea frontend; APIs deterministas locales funcionan si runtime loopback sigue activo sin WAN. Cerrar backend no deja todas las funciones operativas; offline no incorpora OCR/modelos/servicios ausentes.

Fuentes: `app/vite.config.ts:140`; `tools/local-installation/STABLE_PWA.md:31`; `tools/local-installation/STABLE_PWA.md:33`; `tools/local-installation/backend_runtime.py:23`.

Criterio propuesto, no ejecutado: Matriz por función: frontend cacheado, API local, dependencia externa o ausente; distinguir WAN desconectada de loopback deshabilitado. Vinculación: IMP-00, IMP-09, IMP-10.

### E7.04 — Consulta rápida sin episodio y transferencia selectiva

**PENDIENTE · STATIC_READ · REFORMULAR.** Herramientas independientes accesibles; nota tiene acción explícita de aplicar propuesta. No hay contrato universal de transferencia selectiva a episodio activo entre todos los módulos.

Fuentes: `app/src/App.tsx:31`; `app/src/pages/ClinicalNote.tsx:225`.

Criterio propuesto, no ejecutado: Consulta aislada no se añade a nota automáticamente; transferencia muestra origen, paciente/episodio destino y campos seleccionados. Vinculación: IMP-00, IMP-09, IMP-10.

### E8.01 — Clinical Minimal, navegación y componentes existentes

**PARCIAL · STATIC_READ · ADOPTAR.** Home opt-in ClinicalMinimal, Layout compartido, modos claro/oscuro y navegación responsive. La portada/logo/iconos de PR139 commit1627033 se excluyeron de PR140. No están aprobados ni integrados por este estudio.

Fuentes: `app/src/pages/Home.tsx:17`; `app/src/pages/ClinicalMinimalIntro.tsx:5`; `app/src/components/Layout.tsx:44`; `docs/implementacion/CONCILIACION_PR138_PR139.md:17`.

Criterio propuesto, no ejecutado: Comparar misma tarea con diseño existente; reutilizar componentes, no asumir que propuesta visual equivale a funcionalidad clínica. Vinculación: IMP-00, IMP-09, IMP-10.

### E8.02 — Idiomas y país

**PARCIAL · STATIC_READ · REFORMULAR.** Controles y preferencias de idioma; contexto internacional por defecto no deduce país. Texto clínico canónico no está traducido íntegramente. Idioma no equivale a jurisdicción, hospital ni producto comercial.

Fuentes: `app/src/state/settings.tsx:40`; `app/src/context/reference-context.ts:19`; `app/src/context/reference-context.ts:26`; `app/src/pages/ClinicalNote.tsx:660`.

Criterio propuesto, no ejecutado: Conservar fuente/idioma de contenido clínico; selección de país explícita y recursos desconocidos no se completan por intuición. Vinculación: IMP-00, IMP-09, IMP-10.

### E8.03 — WCAG2.2AA y rendimiento global

**NO_VERIFICADO · STATIC_READ · REFORMULAR.** Existen skiplink, foco visible, main, reduced-motion y layout adaptable. No se ejecutó nueva auditoría WCAG, contraste, Lighthouse, WebVitals ni carga. Marcado parcial no prueba conformidad global.

Fuentes: `app/src/components/Layout.tsx:44`; `app/src/components/Layout.tsx:91`; `app/src/index.css:51`; `app/src/index.css:56`.

Criterio propuesto, no ejecutado: Sobre flujo elegido: teclado completo, foco/lector/contraste/táctil, móvil y tablet sin overflow; métricas reales por tarea/dispositivo, sin porcentajes o SLA inventados. Vinculación: IMP-00, IMP-09, IMP-10.

### E8.04 — Medición de utilidad y carga bajo interrupción

**PENDIENTE · STATIC_READ · REFORMULAR.** QA histórica contiene recorridos sintéticos y comparativo focal tablet; no ensayo de guardia global. Número de clics de un recorrido previo no es benchmark universal ni prueba de beneficio clínico.

Fuentes: `docs/implementacion/CONCILIACION_PR138_PR139.md:17`; `docs/implementacion/GUIA_MAESTRA_FLUJO_CLINICO.md:92`.

Criterio propuesto, no ejecutado: Registrar tiempo de inicio/resultado útil, acciones, correcciones y errores con tareas comparables, misma configuración y coste de preparación/llamadas; no registrar PHI. Vinculación: IMP-00, IMP-09, IMP-10.

### X.01 — Emergency MCP como integración clínica universal

**RESTRINGIDO · STATIC_READ · ADOPTAR.** Ocho herramientas de metadatos/documentación en stdio; llamada real get_project_state reportada por coordinador y registry coincide. No lee pacientes, prescribe, escribe, lanza herramientas arbitrarias ni verifica CI/Drive en vivo; registro no prueba conexión de cada host.

Fuentes: `tools/emergency-mcp/README.md:29`; `tools/emergency-mcp/README.md:31`; `tools/emergency-mcp/README.md:50`; `tools/emergency-mcp/README.md:77`.

Criterio propuesto, no ejecutado: Reutilizar para evidencia y estado con snapshot visible; no usar como nuevo backend clínico ni convertirlo en requisito del flujo. Vinculación: IMP-00, IMP-10.

### X.02 — Arquitectura local frente a remota

**EXISTENTE · STATIC_READ · ADOPTAR.** Plan permanente local principal e híbrido opcional; OIDC/DB/infra remota son condicionales. Guía de flujo no autoriza servidores, proveedores, cuentas remotas ni datos de pacientes remotos.

Fuentes: `docs/implementacion/ORQUESTACION.json:1`; `docs/IMPLEMENTACION.md:1`.

Criterio propuesto, no ejecutado: Mantener 12 IDs; estudio en IMP00/02/09/10, paquete en IMP03 sólo si cambia, IMP04–08 condicionales e IMP11 separado. Vinculación: IMP-00, IMP-01, IMP-10.


Totales de clasificación de requisitos locales: EXISTENTE=9, PARCIAL=13, PENDIENTE=8, RESTRINGIDO=6, NO_VERIFICADO=1. No son nuevas tareas IMP.

## Adenda de alcance recibida durante la congelación

El coordinador comunicó la integración autorizada de PR141 en `d3f8a792ca1cd43d022509caa5b43f38856af3ae`, árbol `68f62be8c34212d164625d20d18312bb7004f9d4`, padres M50ef y parche6a1; CI push aún en curso al aviso. Esa comunicación es evidencia del coordinador, no una nueva verificación GitHub realizada por este agente. La fuente exacta de este estudio sigue siendo ecacffee y no se reescribió. El delta informado son dos archivos del instalador; no cambia UI, motores ni los hallazgos de flujo. No se hereda el CI de 6a1 al merge. Véase ADDENDUM_SCOPE.json.
