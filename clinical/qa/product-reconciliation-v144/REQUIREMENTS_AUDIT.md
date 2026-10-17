# Auditoría de cumplimiento — 17/10/2026

Objetivo: conciliar producto, preparación y protocolo antes de habilitar ramas.
El objetivo completo **no está alcanzado**: faltan documentos locales y revisión
humana. Se completó el trabajo documental y la regresión técnicamente ejecutable.

| Fase solicitada | Evidencia actual | Resultado / límite |
|---|---|---|
| 0. Estado | Rama v1.44, HEAD inicial 08ff5ab2501ec2b4b84e3a95617f565ea952047d; status inicial vacío; log -15 inspeccionado | Verificado; comprobación final tras commit en chat |
| 1. Inventario | Dossier JSON, 19 contratos y tabla separada de gates/limitaciones | Completado; no confundir 46 contratos con 58 escenarios |
| 2. Tres capas | Recomendación canónica por módulo/anchor/hash, perfiles de producto, preparación/protocolo separados | Completado documentalmente; no equivalencias implícitas |
| 3. Fuentes | 29 consultas con URL/fecha/resultado; fichas EMA/AEMPS y RCM en portugués | Parcial: accesos fallidos y ausencia de documentación institucional específica registrados |
| 4. Producto | 18 perfiles independientes, campos farmacéuticos y fuentes | Candidatos documentados; producto/stock de Horta no verificado |
| 5. Preparación | 11 referencias con campos definidos o desconocidos explícitos | Pendiente aprobación local y evidencia de estabilidad/compatibilidad donde falta; no se derivan mezclas |
| 6. Protocolo local | Checklist local sin firma, localización pendiente, página pública CFT; override=null | BLOCKED: documento aprobado, versión, vigencia y responsables no aportados |
| 7. Seis flujos | Tablas de amiodarona, insulina, sodio, status, anafilaxia y reversión | Revisados; bloqueos heterogéneos distinguidos |
| 8. Modelo | Dossier no ejecutable con producto/preparación/protocolo/locale/fuente/estado | No se integra modelo terapéutico sin conciliación humana |
| 9. Tests | QA_RESULTS y cuatro informes nuevos de navegador | Contratos existentes probados; tests de producto A/B, nuevo protocolo y exportación de perfiles NO EJECUTADOS: funcionalidad no habilitada |
| 10. Estados | TECHNICALLY_VALIDATED limitado a regresión; 0 PROFESSIONALLY_RECONCILED; revisión pendiente y ejecución bloqueada | No se confunde PASS con aprobación |
| 11. Documento | V1.44_MEDICATION_PRODUCT_PROTOCOL_RECONCILIATION.md y JSON | Creado con todas las secciones solicitadas |
| 12. Revisión humana | Checklist REVIEW/BLOCKED; revisores/fechas/evidencia=null | Checklist creado; aprobación humana pendiente y no automatizada |
| 13. Implementación | Hashes del motor/UI/módulos coinciden con el estado inicial | No procede implementar terapéuticamente antes de cumplir 6/12; solo infraestructura de QA nueva |
| 14. QA | 578 Python, 376 frontend, Clinical QA 7/7, 58 E2E agudos, 1061 pediátricos, exports, lint/typecheck/build | PASS nuevo del 17/10/2026 para el alcance existente; intento fallido de entorno preservado |
| 15. Cierre | Localización y firmas pendientes; 19 contratos bloqueados | v1.44 NO funcionalmente cerrable; CLINICALLY_PENDING |

## Evidencia externa necesaria para continuar

Para cada rama afectada: producto realmente usado y RCM exacto; preparación
institucional con volumen final, estabilidad, compatibilidad, material y
conservación; protocolo aprobado con versión/vigencia, indicación, dosis,
monitorización y excepciones; decisiones de los especialistas pertinentes;
revisión nominal y fechada de farmacia y responsable clínico. Las ramas sin
antídoto universal requieren decisión clínica, no una receta de dilución.

No existe un permiso técnico que sustituya esos datos ni autoriza el cambio de
estado por sí solo. No se contactó a terceros ni se inventó una aprobación.

## Entrega y conservación

El informe principal contiene productos/preparaciones, fuentes, discrepancias,
prioridades P0/P1/P2/P3, resultados nuevos y lista exacta de archivos. El chat
final identifica commit/HEAD, rama y estado limpio observados. BASELINE.json y
VERIFICATION.json preservan referencias y hashes; ninguna promoción YELLOW,
merge o push. El objetivo de resolver las ramas queda pendiente de evidencia
local y humana; esta auditoría no redefine ese objetivo como simple QA.
