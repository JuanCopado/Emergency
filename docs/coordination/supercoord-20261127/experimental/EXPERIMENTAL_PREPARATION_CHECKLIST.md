# Preparación experimental reconciliada — 27/11/2026

Ejecutor: **Codex**, como alternativa de coordinación técnica. Este documento no es un encargo recibido ni una auditoría ejecutada por Antigravity.

Se conserva el banco de **10/30 archivos canónicos, 20 posiciones pendientes y cero adjudicaciones**. La preparación anterior ya contiene 30 registros de admisión, 30 de referencia/custodia y formulario de nombramientos sin personas asignadas. Se reutilizan esos documentos; no se regeneraron fichas, imágenes o referencias clínicas.

La nueva verificación coteja los bytes y SHA-256 de **10 archivos documentales** del manifiesto anterior y la coherencia entre IDs, recuentos, admisión y custodia: `PASS_DOCUMENTARY_RECONCILIATION_ONLY`, cero incidencias. El verificador no vuelve a decodificar ni calcular hashes de las imágenes: reutiliza el recibo Work anterior de 39 activos (10 canónicos, cinco capturas y 24 dermatológicos), atribuido expresamente. No certifica privacidad de píxeles ni utilidad diagnóstica.

Base documental canónica `5494b0037dcfe2c2565187985b862ffa8ea1d83b`; el coordinador declara receptor PR120 `2058e97179ae793914dcd016e4fd033395dbc3e2`, de árbol idéntico. Esta ejecución no volvió a consultar el remoto ni transfiere resultados de CI a un SHA nuevo.

## Cola única de las 20 posiciones pendientes

| Posiciones | Cantidad | Estado material | Trabajo siguiente y dependencia |
|---|---:|---|---|
| S1-01/S2-01 hasta S1-07/S2-07 | 14 | Requisitos históricos pendientes de adaptación | Preparar propuesta expresa de adaptación al objetivo dermatológico vigente. No reasignar automáticamente las 23 decisiones/24 imágenes de consulta. No reactivar fabricación, moulage, presupuestos ni MST digital sustituidos. |
| S1-10 | 1 | Captura física conservada y seleccionada para preparación con observaciones | Resolver alineación/perspectiva y cursor; las observaciones no prueban recorte anatómico nuevo. Conservar original; repetición física sólo si el requisito de captura lo exige. |
| S2-10 | 1 | Captura física condicional conservada | Retirar físicamente el aviso de pantalla completa para la nueva toma cuando corresponda; cotejar con fuente. No eliminarlo mediante retoque para fingir captura conforme. |
| S1-11 | 1 | WebP preparado, condicional | La igualdad RGB tras orientación EXIF fue acreditada previamente para la conversión: no demuestra encuadre, moiré o realismo suficientes. Mantener observaciones de perspectiva/moiré y revisión material pendiente. |
| S2-11 | 1 | **Bloqueado por moiré** | Repetición física necesaria para reducir bandas cromáticas prominentes. No hay vía informática que acredite haber repetido la fotografía. No promover el archivo existente ni retocarlo para simular cierre. |
| S1-12 | 1 | Captura condicional con limitaciones | Revisar detalle fino, altas luces, reflejos marginales y marca radial. Mantener selección previa del propietario; no repetir votación ni confundirla con admisión. |
| S2-12 | 1 | **Sin condición experimental/panel/permiso completos** | Obtener evidencia auténtica de la condición del montaje, ausencia de derrame requerida, panel limpio y uso permitido para preparación/fotografía móvil. No inferirlo desde fantoma basal o píxeles. |

Las cinco capturas son cuatro condicionales y una bloqueada por moiré. No son cinco nuevas posiciones canónicas. La cola de 20 incluye las 14 especificaciones históricas que precisan adaptación; no puede presentarse como 20 imágenes nuevas ya preparadas.

## Checklist de continuación

1. **Custodia y material:** conservar IDs, ficha original, fuente, licencia por uso, original y hash; registrar cada nuevo derivado sin sobrescribir el original. La fuente/diagnóstico esperado permanece bajo custodia separada del paquete ciego.
2. **Adaptación del objetivo:** para las 14 posiciones históricas, describir correspondencia nueva y efecto metodológico antes de reutilizar un activo dermatológico. La aceptación de representatividad clínica ya concedida no confiere independencia del conjunto de validación ni privacidad/licencia universal.
3. **Captura física:** resolver S2-11 y las condiciones específicas de S1-10/S2-10/S1-11/S1-12 con evidencia de una toma real cuando proceda. No atribuir ángulos o ausencia de recorte por inferencia.
4. **S2-12:** conservar los descartes primarios existentes. Breitkreutz 2013 no acredita el control negativo requerido; PMC4579714 no fue adquirido ni tiene uso derivado concreto cerrado. No repetir adquisiciones/seguimiento de autores ya hechos ni eludir restricciones.
5. **Privacidad y derechos:** comprobar cada activo y finalidad antes de transferencia o incorporación. Licencia pública no acredita por sí sola consentimiento. No incluir rostros, PHI, DICOM ni documentación restringida en paquetes externos.
6. **Referencia y admisión:** mantener las 16 referencias diagnósticas requeridas y las 14 N/A según fichas existentes. Sólo una revisión/adjudicación real y competente puede completar los campos humanos. Los controles automáticos verifican consistencia formal, no independencia real ni calidad diagnóstica.
7. **Evaluaciones aplazadas:** R5-1, R5-2 y SCA permanecen sin ejecución independiente. Pueden completarse logística, contratos, formularios y controles técnicos; no inventar participantes, nombramientos, corpus sellado, autorizaciones o resultados prospectivos. R5-2 (28 celdas de lenguaje tranquilizador) permanece separado del contrato nota/SCA.

## Dictámenes reutilizados y límites

`WORK_CIERRE_FINAL_20261127/GEMINI/DICTAMEN_IMAGEN_V2_RECIBIDO.md` registra **FAVORABLE_ALCANCE_DOCUMENTAL** de Gemini web. Cierra la preparación/trazabilidad documental A1-A8 cotejada; no es dictamen nuevo de Antigravity ni revisión de píxeles, admisión individual o adjudicación humana independiente. Los hashes de imágenes allí citados son del ejecutor Work, no cálculos propios de Gemini.

No se han iniciado participantes, nombrado revisores, adquirido/generado/alterado imágenes, transmitido datos externos ni promovido posiciones canónicas. Se preservan las aceptaciones de los 19 contratos, MED-DEC-R46-01/02 y las 45 fórmulas.

**CLINICALLY_PENDING · NOT_FROZEN_NOT_VALIDATED · NO_GO_CLINICAL_RELEASE.**

## Reproducir la verificación documental

Ejecutar `python verify_experimental_preparation.py --source-root <carpeta IMAGEN_R88 existente>`. La herramienta sólo lee el expediente fuente y escribe su informe de reconciliación junto al script. No contiene ni modifica imágenes; el JSON de coordinación no debe entregarse como paquete ciego a revisores.
