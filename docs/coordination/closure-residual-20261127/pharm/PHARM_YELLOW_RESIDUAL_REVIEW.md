# Reconciliación residual farmacológica y dos módulos YELLOW

Fecha: 27/11/2026. Candidato PR125 `54285f88c3901c63dff017ad0413593c0e0a8271`, árbol `65f34f3f175f0b0604c5a17c875f59f564543018`. Fuente local limpia `6bb1308c3f6030fa95a43617f0075a6bc280bd16`, mismo árbol. Revisión de lectura y conciliación: no modificación del repositorio, no nuevo ensayo clínico ni repetición de QA previa.

Los 37 IDs se recuperaron del inventario existente y se comprobaron contra la proyección actual: **37/37 únicos y presentes**. Se conservan **129 GREEN y 2 YELLOW**. No se ha demostrado un nuevo defecto ejecutable en el alcance leído; tampoco se afirma ausencia universal de defectos.

## Qué significa realmente el inventario de 37

El paquete previo contiene 229 contextos documentales, no 229 tratamientos: 37 marcos paraguas, 62 remisiones, 8 cabeceras documentales/procesos, 1 contexto poblacional, 9 contextos de selección, 10 restricciones de seguridad, 51 indicaciones explícitas y 51 exposiciones/agentes. No deben generarse pautas farmacológicas para completar campos de los marcos o remisiones.

El resultado de Gemini es favorable **documental** para los 37, con recepción 15/15 partes y 8/8 focales. El inventario histórico declara 98 afirmaciones/observaciones focales heterogéneas, 115 contextos con alguna afirmación cotejada y 114 sin cotejo nuevo en esos lotes; ninguna cifra acredita lectura primaria integral de cada indicación. Los posteriores recibos PRIMARY_FOCAL_AUDIT, B2_EMA_FOCAL_AUDIT y UROLOGY_DIRECT_PRIMARY_RECEIPT resuelven afirmaciones enumeradas, no todos los campos de sus módulos. No recalcular cobertura clínica como si cada recibo cerrase un módulo entero.

El JSON adjunto conserva por ID los pendientes específicos históricos para encaminarlos sin duplicar su investigación. En particular, los pendientes históricos de CARDIO02/04/05 y de escafoides, epistaxis, KCl, rasburicasa, urología, Voraxaze/Proveblue deben leerse junto con sus adendas posteriores: no reabrir lo ya cotejado ni convertir el acceso focal en revisión integral. BSH TLS2025 y fuentes de agentes/productos restantes no quedan cerrados por una ficha EMA general.

Insulina: respuesta del propietario **SIN IDENTIFICAR**. Mantener `SHORT_ACTING_PRODUCT_UNSPECIFIED`; no atribuir marca, principio activo, concentración, país, ATC ni equivalencia. La clasificación semántica documental está hecha; la identificación operacional permanece ausente y no se resuelve investigando un producto supuesto. No alterar los 19 contratos ya aceptados ni sus controles específicos.

## Condiciones de cierre de los dos YELLOW

| Módulo | Preparación ya aprovechable | Pendiente real para cierre clínico |
|---|---|---|
| clinical-image-interpretation | Salvaguardas MED-DEC-R46-01/02 aceptadas; protocolo R54; custodia/manifestación técnica; 10/30 estímulos canónicos y 23 revisiones médicas dermatológicas separadas | Finalidad y derechos/privacidad por activo; completar los 20 estímulos con mecanismo/condición real y referencias aplicables; adjudicación independiente R5-1 según protocolo (16 referencias clínicas pendientes y 14 N/A en el expediente R54, sin rellenar firmas); conjunto independiente y autorizado, cegamiento, versión y análisis preespecificados, resultados reales y valoración del propietario dentro del alcance evaluado. Las 14 especificaciones DEV-DERM no son imágenes ni validación independiente. |
| clinical-note-diagnostic-support | Reglas y regresiones sintéticas, corrección del transporte JSON ya incorporada y corpus R5 de desarrollo; protocolo R6 nota y autorización silenciosa SCA conservada | Corpus textual ciego independiente, cuatro lenguas × siete clases conforme R5-2; custodio, tamaño/umbrales preespecificados y adjudicadores independientes por lengua más dirimente; referencia textual y clínica separadas; permisos/cohorte/ventanas para el estudio SCA cuando disponibles; análisis con denominadores, faltantes, cobertura, carga y omisiones, sin imputar eficacia a regresiones sintéticas. |

La ausencia actual de revisores aplaza adjudicación/evaluación independiente y estudio prospectivo; no impide preparar manifiestos, instrumentos, trazabilidad, controles técnicos y análisis. No se solicitan otra vez MED-DEC-R46-01/02 ni las 23 decisiones dermatológicas. Las formulaciones antiguas de R6 sobre aprobación pendiente deben interpretarse con la aceptación posterior R54; no convertirlas en votos nuevos.

Los márgenes clínicos o requisitos no cubiertos por las aceptaciones posteriores solo justificarían una pregunta nueva tras presentar propuesta concreta, evidencia y alcance; esta conciliación no crea tal decisión madura ni inventa valores.

## Discrepancias documentales para la matriz central

1. `CODEX_RESIDUAL_CLINICAL_CONTRACTS.json` y una cabecera de `clinical/CURRENT_STATE.md` aún conservan la recuperación de la formulación original CARDIO como pendiente. Los recibos posteriores la recuperan y PR125 implementa alcances 02/04/05, más los enlaces parciales 06 de PR124. Es una desactualización de resumen, no nueva aprobación necesaria ni defecto de dosis.
2. El inventario farmacológico histórico `V1.44_PHARMACOLOGY_INVENTORY.json` conserva bloqueos de un corte anterior. No restituirlos como bloqueos administrativos de los 19 contratos ya aceptados. Usar el registro vigente del propietario y separar controles actuales de producto/caso.
3. Un enlace de biblioteca, un módulo GREEN o un control técnico PASS no acredita por sí solo una pauta completa por indicación ni validación independiente del padre YELLOW.
4. No se propone ampliar léxico, cambiar reglas de prioridad, inferir país ni renombrar destinos sin regla. Las limitaciones antiguas R5 son observaciones sintéticas atribuidas, no defectos nuevos reproducidos en PR125.

## Verificación efectuada

Lectura local real de instrucciones, estado, proyección, inventario y recibos; identidad de árbol comprobada; 37 IDs presentes/únicos, 229 roles contabilizados y estados 129/2 comprobados mediante script. El JSON adjunto incluye manifiesto SHA-256 de fuentes leídas y pendientes por los 37 IDs. No se ejecutó de nuevo suite de producto porque no hubo modificación de código; resultados previos se atribuyen, no se vuelven a declarar como ejecución propia.

**CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE.** Sin promoción, merge, despliegue o publicación por este revisor.
