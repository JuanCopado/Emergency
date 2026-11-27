# Seguimiento de decisiones del propietario — 27/11/2026

Registro documental suplementario, no modificación de expedientes históricos ni de fuentes de runtime. Base receptora comprobada: `2058e97179ae793914dcd016e4fd033395dbc3e2`, integración PR120, árbol `78e27cb900f7dd901eb5aeb48026276dc48b942c`. La rama aislada de seguimiento no es el receptor.

## Integración técnica

PR120 fusionada el 27/11/2026 a las 06:20:35 UTC. Los tres workflows push del commit integrado fueron consultados y tienen conclusión success:
- [Clinical QA](https://github.com/JuanCopado/Emergency/actions/runs/45951237634)
- [App UI QA](https://github.com/JuanCopado/Emergency/actions/runs/45951237801)
- [Security and quality](https://github.com/JuanCopado/Emergency/actions/runs/45951237683)

Estos resultados pertenecen al receptor indicado, no se transfieren al nuevo commit documental. No se declara despliegue o nueva validación clínica.

## Decisiones clínicas del propietario

La procedencia de las decisiones nuevas es la conversación de PROYECTO EMERGENCY del 27/11/2026, tras el expediente WORK del día anterior. Se registran alcances resumidos y horas UTC, no se presentan las paráfrasis como transcripciones literales. Los expedientes y la conversación originales conservan autoridad. No reabrir las 19 aceptaciones del 16/11 ni MED-DEC-R46-01/02 del 24/11.

**MED-RES-PROT-01 v1**, 06:14:21 UTC — SÍ. Respuesta explícita: «SÍ. Apruebo ... en su alcance original: clasificar PROTAMINE_HOSPIRA_10 como histórico revocado en España, mantener runtime_enabled=false, preservar el límite histórico estricto y no modificar las rutas activas ni sustituir automáticamente el producto.» La elipsis indica una abreviación, no cita íntegra. El cierre es de aceptación del perfil histórico, no de implementación ni de otros productos. No modificar universalmente límites de velocidad ni seleccionar una alternativa activa por inferencia. GMA-P1-003: respuesta recibida; queda reconciliación documental/técnica en su alcance.

**MED-RES-CARDIO-01..06 v1**, 06:12:33 UTC — aceptación conjunta explícita de las seis propuestas estructurales, sin habilitar dosis no revisadas ni liberar clínicamente el proyecto. Los siguientes son resúmenes de alcance, no nuevos protocolos:
- 01: router de monitorización y cuatro circuitos de reanimación existentes, conservar decisiones ARR-SELECTOR y excepciones pediátricas; no cambiar dosis ni algoritmos.
- 02: circuitos diferenciados por lesión valvular y situación hemodinámica; no pauta universal.
- 03: circuitos específicos de dispositivo y complicación, con monitorización y especialista cuando corresponda; no pauta universal.
- 04: objetivos de presión arterial diferenciados según indicación, preservar vías específicas; la secuencia general requiere la fuente exacta y no sustituye las vías específicas.
- 05: selección por indicación, contraindicaciones, producto y jurisdicción; no habilitar cálculos con productos no verificados.
- 06: dolor torácico no coronario por causa, no antitrombótico genérico ni alta automática por una sola prueba/puntuación.

La implementación queda pendiente de aplicar y verificar las fichas originales. Este registro no incorpora cifras nuevas, dosis, umbrales o reglas ejecutables.

## Banco dermatológico de consulta/desarrollo

Identidad: manifiesto DERMATOLOGIA_CASOS_HEREDADO.json y entrega del banco dermatológico gratuito del 26/11/2026. 23/23 casos revisados por el propietario, 24 fotografías inventariadas, 0 rechazos. Dos decisiones restringidas a representatividad clínica y 21 de consulta/desarrollo bajo límites aplicables. No se acredita consentimiento, licencia de cualquier uso, confirmación etiológica, rendimiento diagnóstico, incorporación al producto ni adjudicación experimental. Las condiciones de privacidad y licencia se mantienen para todos los activos. No se publican fotografías, datos de pacientes ni rutas privadas en este registro.

Todas las decisiones corresponden a v1 y a 27/11/2026 UTC. La columna alcance es una síntesis fiel, no cita textual. Todas fueron afirmativas en su alcance específico.

| ID | Caso | Hora UTC | Alcance |
|---|---|---|---|
| MED-RES-DERMA-FRONTIERS_1048480_F1 | Angioedema hereditario | 06:23:15 | Consulta y desarrollo exclusivamente; privacidad de reutilización no aprobada. |
| MED-RES-DERMA-CDC_2874_24913_24914 | Erisipela facial | 06:23:56 | Solo representatividad clínica; incorporación y redistribución bloqueadas hasta resolver privacidad. |
| MED-RES-DERMA-CDC_27799 | Forunculosis frontal | 06:24:14 | Solo representatividad clínica; incorporación y redistribución bloqueadas hasta resolver privacidad. |
| MED-RES-DERMA-CASE_CDC_PHIL_5153 | Impétigo | 06:24:48 | Consulta/desarrollo, condicionado a revisión de privacidad. |
| MED-RES-DERMA-CASE_CDC_PHIL_6478 | Herpes zóster | 06:25:09 | Consulta/desarrollo, condicionado a revisión de privacidad. |
| MED-RES-DERMA-CASE_CDC_PHIL_6482 | Herpes simple | 06:25:37 | Consulta/desarrollo, condicionado a revisión de privacidad. |
| MED-RES-DERMA-CASE_CDC_PHIL_24379 | Tiña corporal | 06:26:18 | Consulta/desarrollo, condicionado a privacidad; respuestas repetidas cuentan una vez. |
| MED-RES-DERMA-CASE_CDC_PHIL_28632 | Reacción a mosquito | 06:27:05 | Consulta/desarrollo, condicionado a revisión de privacidad. |
| MED-RES-DERMA-CASE_CDC_PHIL_1337 | Meningococemia (gangrena de mano) | 06:27:31 | Consulta/desarrollo, manifestación avanzada; condicionado a privacidad. |
| MED-RES-DERMA-CASE_CDC_PHIL_2332 | Carbunco cutáneo | 06:28:06 | Consulta/desarrollo; conservar limitaciones; condicionado a privacidad. |
| MED-RES-DERMA-CASE_PMC7176330 | Espectro SJS/TEN | 06:28:31 | Un solo caso con figuras 2 y 3; consulta/desarrollo y privacidad; sin inferir superficie desprendida. |
| MED-RES-DERMA-CASE_PMC11585283 | DRESS | 06:28:50 | Consulta/desarrollo, condicionado a privacidad; no confirmar causalidad a partir de la imagen. |
| MED-RES-DERMA-CASE_PMC8203330 | Vasculitis leucocitoclástica | 06:29:16 | Consulta/desarrollo, conservar limitaciones y condicionar a privacidad. |
| MED-RES-DERMA-CASE_PMC11619809 | Fascitis necrosante | 06:29:50 | Consulta/desarrollo como imagen posterior al desbridamiento, no presentación inicial; privacidad. |
| MED-RES-DERMA-COMMONS_CASE_5de1c08f376aedda | Escabiosis | 06:30:15 | Consulta/desarrollo, conservar limitaciones y condicionar a privacidad. |
| MED-RES-DERMA-SCIN_CASE_-3768594983498155183 | Urticaria | 06:30:46 | Consulta/desarrollo, condicionado a privacidad. |
| MED-RES-DERMA-SCIN_CASE_3083550471820565612 | Eccema | 06:31:09 | Consulta/desarrollo, condicionado a privacidad. |
| MED-RES-DERMA-SCIN_CASE_2600794538114860588 | Dermatitis alérgica de contacto | 06:31:34 | Consulta/desarrollo, condicionado a privacidad. |
| MED-RES-DERMA-SCIN_CASE_3730083867318674656 | Celulitis | 06:33:01 | Consulta/desarrollo, condicionado a privacidad. |
| MED-RES-DERMA-SCIN_CASE_579682856480983647 | Absceso | 06:33:19 | Consulta/desarrollo, condicionado a privacidad. |
| MED-RES-DERMA-SCIN_CASE_3689862615752795245 | Foliculitis | 06:33:43 | Consulta/desarrollo, condicionado a privacidad. |
| MED-RES-DERMA-SCIN_CASE_-3518984822601104202 | Erupción farmacológica | 06:34:08 | Consulta/desarrollo, condicionado a privacidad; sin establecer causalidad. |
| MED-RES-DERMA-SCIN_CASE_-3902972343084754168 | Eccema, segundo caso | 06:34:31 | Consulta/desarrollo, condicionado a privacidad. |

La decisión finaliza la revisión de representatividad/consulta del propietario. No equivale a habilitación clínica o permiso de redistribución. Preservar originales y hashes; no alterar el manifiesto histórico. Integrar este registro en la reconciliación de metadatos por activo, sin repetir las votaciones. Conservar el banco de desarrollo fuera de conjuntos reservados y evaluación diagnóstica independiente. No crear un banco de heridas como objetivo independiente.

## Diseño y dependencia organizativa

- 06:37:53 UTC: «Apruebo la propuesta de diseño Clinical Minimal como base para la futura interfaz de EMERGENCY. Siguiente validación.» Repetición a 06:38:10 UTC: una sola decisión. Alcance exclusivamente visual; prototipo no desplegado, UX2 se conserva hasta cambio implementado, probado y auditado.
- 06:38:38 UTC: «Por ahora no dispongo de revisores independientes. Continuar con todas las tareas técnicas y científicas que no dependan de ellos.» No se nombra custodio, jueces, redactores ni revisores independientes. No se acredita ausencia universal futura ni aprobación institucional.

## Continuidad ejecutable sin revisores externos

1. Documentación: reconciliar este registro con WORK_PENDIENTES_REALES.json y los manifiestos, sin sustituir sus versiones históricas. Cerrar solo la dependencia de respuesta del propietario en protamina, conservar controles técnicos y clínicos pendientes. Mantener el inventario de 23 casos y 24 imágenes, revisión de privacidad/derechos por activo y veto a publicación de rostros no resueltos.
2. Interfaz: preparar implementación incremental Clinical Minimal en rama de tarea; conservar funciones y contratos de UX2, ES/PT/EN/ZH, accesibilidad, identidad de rutas, exportación, navegación y pruebas negativas. No declarar agentes clínicos operativos.
3. Ciencia: continuar especialización por indicación de los 37 módulos sin binding de la biblioteca de 59 referencias. Reusar 16 no prescriptivos y seis vinculados a 131 registros, y los lotes ya preparados. Resolver exclusivamente deltas/lagunas reales de fuentes, derechos, IFEM, AHA/ASA, CDC, WSES, identidad del producto insulina y src-b5e20534; no inferir dosis, unidades, producto ni reemplazar lecturas primarias por síntesis no autorizadas. No repetir adquisiciones ni 15/18 revisiones previas.
4. Imagen: preparar material y comprobaciones técnicas pendientes de R86/S2-11/S2-12, sin inventar activos ni adjudicaciones. El banco de desarrollo no sustituye al banco experimental. No exponer conjuntos ciegos a participantes que pudieran integrar el desarrollo.
5. Investigación: preparar logística y documentación de R5-1/R5-2/R4-SCA, criterios y expedientes sin afirmar que existen revisores, cohorte, aprobación institucional, corpus sellado, independencia o resultados prospectivos. R5-1 conserva 10/30 archivos técnicos y 0 adjudicaciones en el corte de Work; 20 pendientes según el mismo corte. No modificar este recuento por revisar el banco dermatológico.
6. G05: seguir dentro del laboratorio, aclarar consumidor, derechos, retención y contrato de píxeles antes de una nueva propuesta de alcance. No usar datos reales ni activar interfaz pública sin controles.
7. Validar cada delta con QA pertinente y auditoría técnica de su SHA. No confundir revisión automatizada con adjudicación clínica humana independiente.

Bloqueados por requisitos externos: evaluación independiente R5-1/R5-2, autorización y cohorte prospectiva R4-SCA, derechos o aclaraciones editoriales pendientes, y cualquier actividad que requiera consentimiento/privacidad no resueltos. La falta de revisores no bloquea la preparación técnica compatible.

**Estado global: CLINICALLY_PENDING · NOT_FROZEN_NOT_VALIDATED · NO_GO_CLINICAL_RELEASE.** Ningún cambio de runtime, dosis, fuente clínica, catálogo, estados, main, rama protegida o producción autorizado por este registro. Aprobación de propietario no es autorización de liberación clínica.
