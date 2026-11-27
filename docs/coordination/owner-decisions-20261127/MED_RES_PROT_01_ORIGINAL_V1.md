# Decisiones médicas pendientes

Cero decisiones nuevas maduras en este corte. Se conserva únicamente MED-RES-PROT-01 v1, previamente preparada. No se ha localizado respuesta explícita en los canales revisados (registros locales, documento central vigente y chats indicados en CIENCIA/MED_PROT_COMPROBACION_RECEPCION.json); no es una afirmación de ausencia universal. Si existe respuesta posterior identificable, debe conciliarse antes de volver a presentar la pregunta.

**Pregunta original v1:** ¿Aprueba clasificar PROTAMINE_HOSPIRA_10 (registro AEMPS 45777) como HISTORICAL_REVOKED_ES_NOT_FOR_PRODUCT_SELECTION, excluido de toda nueva selección operativa, manteniendo runtime_enabled = false y preservando su límite estricto < 5 mg/min únicamente en su alcance histórico, sin sustitución automática por LEO/Prosulf y sin modificar globalmente ≤ 5 → < 5 en las rutas activas del 16/11?

**Recomendación del informe: SÍ.** No es aprobación de Juan. Evidencia: [AEMPS CIMA 45777](https://cima.aemps.es/cima/dochtml/ft/45777/FT_45777.html), FT §4.2, y clinical/qa/V1.44_MEDICATION_PRODUCT_PROTOCOL_RECONCILIATION.json. El registro Hospira español está revocado/comercialización suspendida según el expediente;50 mg/10 min = 5 mg/min no satisface<5. No universalizar ese estado a Portugal u otros productos.

- SÍ: clasificación histórica limitada a PROTAMINE_HOSPIRA_10, conservando runtime_enabled=false, los límites históricos y las rutas aceptadas.
- NO: propuesta sin aprobar, perfil inactivo y GMA-P1-003 abierto; sin sustitución ni activación automática. Una alternativa necesita evidencia y decisión propias.

No se vuelven a solicitar los 19 contratos ni MED-DEC-R46-01/02. Farmacia es consultiva; no firma física obligatoria. CDC, derechos documentales e insulina no se convierten en votaciones médicas. CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE.


## Cotejo de este ciclo

Se revisó el documento central vigente y el handoff indicado: no se localizó respuesta posterior expresa a MED-RES-PROT-01 v1 en esos canales. Los cotejos de labetalol, RCUK y drepanocitosis preparan conciliaciones documentales y no demuestran por sí solos una nueva decisión médica madura. No se agrupan aprobaciones ni se solicitan de nuevo MED-DEC-R46-01/02 o los19contratos. La autorización técnica de merge se registra aparte y no constituye aprobación clínica.
