# Reconciliación del propietario · 27/11/2026

Base: `2058e97179ae793914dcd016e4fd033395dbc3e2` (PR120). Registro recibido: `9018e14bb058c6ebb6f8bf1224924997ba3109a7`, incorporado sin alterar su texto. Rama aislada: `codex/owner-decisions-20261127`. Estado: **CLINICALLY_PENDING · NOT_FROZEN_NOT_VALIDATED · NO_GO_CLINICAL_RELEASE**.

## Resultado aplicado

GMA-P1-003 queda **RESOLVED_HISTORICAL_PROFILE_SCOPE**, exclusivamente según MED-RES-PROT-01 v1. La disposición vigente está en `clinical/references/owner-decisions-2026-11-27.json`; `CODEX_RESIDUAL_CLINICAL_CONTRACTS.json` ya no solicita una respuesta que fue recibida. PROTAMINE_HOSPIRA_10 queda `HISTORICAL_REVOKED_ES_NOT_FOR_PRODUCT_SELECTION`, España/AEMPS 45777, `runtime_enabled=false`, sin producto sustituto. Su límite histórico sigue siendo estrictamente `<5 mg/min`. No se cambia globalmente el límite inclusivo de las rutas activas ni se selecciona LEO/Prosulf.

Se recuperó el [expediente original de Drive](https://docs.google.com/document/d/1yIPlybffYNeucGu3y8_mHIwpLRLtWc36/edit). Su texto completo se conserva en `MED_RES_PROT_01_ORIGINAL_V1.md` con SHA-256 en el registro. Sus menciones a respuesta pendiente pertenecen al corte anterior y quedan superadas por el SÍ del 27/11, 06:14:21 UTC. No es una nueva pregunta al propietario. La ficha primaria [CIMA 45777](https://cima.aemps.es/cima/dochtml/ft/45777/FT_45777.html), advertencia inicial y §4.2, confirma revocación/suspensión y el límite histórico. Lectura focal, sin atribuir revisión integral ni renovar fechas del registro de evidencia.

Los expedientes históricos de octubre no se reescriben. La nueva disposición es su actualización fechada, no una autorización operativa. El cierre no se extiende a otros productos, jurisdicciones o controles individuales.

## Cardiovascular: aprobación conservada y comparación preparada

Las seis decisiones v1 tienen **SÍ estructural** a las 06:12:33 UTC. No falta aprobación médica. `CARDIO_DOCUMENTARY_COMPARISON.json` vincula cada ID con su módulo, referencias y localizador de la [documentación canónica de Drive](https://drive.google.com/file/d/1a1Hm5taErhZW_O4KxvSgyuSdGX4SAXHo/view). El JSON de Drive y el del receptor son semánticamente iguales; difieren en serialización. Se conservan los textos canónicos, las cuatro rutas ARR-SELECTOR y sus excepciones pediátricas.

La formulación íntegra del mensaje original del 27/11 a las **06:10:21 UTC** no se ha recuperado en esta ejecución. El registro 9018e14 y los localizadores no lo sustituyen. Incidencia: **EXPEDIENT_TRACEABILITY**, con aprobación ya recibida. Se revisaron los registros accesibles de Work y las búsquedas de Drive; esto no acredita ausencia universal del original. Computer Use falló al inicializarse con `the gaas-browser node_repl sandbox cannot be disabled`.

Por instrucción expresa posterior del propietario, no se aplica ningún cambio clínico sustantivo cuya formulación aprobada exacta no pueda recuperarse. Work debe conservar el mensaje íntegro, su ID, fecha, hash y vínculo al SÍ de las 06:12:33 UTC, y contrastarlo antes de ese delta. No reconstruirlo ni repetir las seis aprobaciones.

## Aprobaciones y límites preservados

El registro programático conserva los 23 IDs dermatológicos v1, sus fechas y alcances: dos de representatividad clínica y 21 de consulta/desarrollo condicionados. Las 24 fotografías siguen siendo un inventario, sin nueva publicación, permiso de redistribución, incorporación al producto o adjudicación experimental. No se incluyen fotografías ni rutas privadas. La conciliación física de hashes, privacidad y derechos por activo pertenece al carril de imagen y sigue pendiente aquí.

Clinical Minimal conserva una sola aprobación como base visual futura; la repetición no cuenta como otra decisión. UX2 continúa vigente en esta entrega. Implementación visual incremental y auditoría corresponden a una entrega separada. Los 19 contratos aceptados el 16/11, MED-DEC-R46-01/02 y el registro clínico no se reabren ni se promueven.

`WORK_PENDIENTES_REALES_OVERLAY.json` concilia el corte recuperado de Work sin sobrescribir documentos compartidos que otra sesión actualiza. Se cierra la dependencia de respuesta de protamina; quedan trazabilidad cardiovascular, privacidad/derechos de activos, implementación visual y auditoría del candidato. Los requisitos científicos/experimentales de otros carriles conservan sus expedientes propios. La falta actual de revisores humanos independientes no se sustituye por una revisión automatizada.

## Verificación y auditoría

Regresiones positivas y negativas: `clinical/tests/test_owner_decision_reconciliation.py`. Control ejecutable: `python clinical/scripts/owner_decision_reconciliation.py`. Comprueba rechazo de reactivación, sustitución, jurisdicción ampliada, límite inclusivo, ficha sustituida, duplicación de casos y ampliación de derechos/validación/despliegue.

Los resultados locales observados, la preservación y la CI del SHA publicado se registran en los recibos de esta entrega. No se atribuye al candidato la CI de PR120. Antigravity debe emitir su propio dictamen sobre el SHA exacto; la orden preparada no acredita recepción ni auditoría realizada. No merge ni despliegue.
