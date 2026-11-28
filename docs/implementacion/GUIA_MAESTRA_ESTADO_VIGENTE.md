# Guía Maestra — estado vigente y conciliación

Alcance v1.0 **ACEPTADO por el propietario** mediante mensaje `01a222ac-1ca7-7260-b98f-4ef0c68ea3e0`: FAST manual y NOTE en rama aislada, sin cambiar cálculos/contenido clínico ni desplegar. Aceptación de alcance, no aprobación médica ni liberación asistencial.

El [texto v1.0 aceptado](GUIA_MAESTRA_FLUJO_CLINICO.md), en su representación canónica Git/UTF-8/LF, conserva exactamente SHA256 `5678ef4ea926a9dbe7fdcf116943eede68a28d4f0af0b11e36c4a1447ac8b8e2`, tal como fue publicado y auditado; un checkout Windows con CRLF puede tener otro hash físico. Su encabezado «propuesta/no aceptada» describe el corte anterior a la respuesta humana; se conserva como evidencia histórica y queda superado, para el estado, por este registro. No se reescriben los originales de agentes ni se atribuye la aceptación a su acuerdo.

## Estado por fuente

| Fuente | Estado y alcance |
|---|---|
| Receptor internacional | `d3f8a792ca1cd43d022509caa5b43f38856af3ae`, protegido. No se ha fusionado PR143. |
| Primer incremento | [PR143](https://github.com/JuanCopado/Emergency/pull/143), `a4fe1e2c509c188111c6216b31d6b592f8c4baa6`, borrador; cuatro archivos UI/tests. CI9/9 y auditoría estática exacta favorables, sin repetir pruebas en esta conciliación. |
| PR142 | `2aef298dad6816176f4286162c6d1070417c8eee`, borrador, base histórica50ef. Contiene guía0.1 y políticaMCP. No se sobrescribe ni retargetea; lease de autor sin confirmar. |
| Propuesta documental v1 publicada | `76716572222653cbb0207dd0752b7e2d9fe73766`; input de estudioecacffee, Gemini parcial y alternativaCodex explícitos, AG documental. No constituye código nuevo. |
| Esta conciliación | Rama documental propia. Reutiliza la v1 y adopta política exacta de PR142 sin duplicar módulos o colas. No introduce incremento TREATMENT/DISCHARGE/TESTS. |

## Política permanente y orquestación

Se incorpora la política MCP de PR1422aef en AGENTS.md y los campos de dispatch de ORQUESTACION.json. Priorizar conectores operativos/autorizados cuando aporten ventaja efectiva, sin consultas preventivas o instalaciones para demostrar uso. Registrar llamadas útiles y resultados con fuente, alcance y UTC observado o limitación temporal explícita. Configuración no equivale a ejecución; metadatos no equivalen a lectura científica o validación clínica. La evidencia de código/QA ya válida se reutiliza.

La [orquestación GMFC](ORQUESTACION_GUIA_MAESTRA.json) registra la aceptación, el candidato y la alternativa clínica atribuida. Se conservan los doceIDs IMP y los26registros clínicos de CENTRAL; las seis líneas de estudio y37requisitos no son otra cola. El coordinador único actualiza CENTRAL y custodia; esta rama no los sobrescribe.

## Inventario37 y siguiente paso

El [inventario](gmfc/INVENTARIO_TECNICO.json) mantiene exactamente los37IDs y sus clasificaciones:9EXISTENTE/13PARCIAL/8PENDIENTE/6RESTRINGIDO/1NO_VERIFICADO. Añade evidencia candidata PR143 a seis requisitos afectados, sin declararla integrada. FAST universal, voz, final libre exportable, persistencia/multiepisodio y conformidadWCAGglobal no quedan completados por ese incremento.

La [comparativa](gmfc/SIGUIENTE_INCREMENTO_PROPUESTO.md) recomienda **TREATMENT**, únicamente acceso y resumen del panel existente/estado de revisión. Recomendación cualitativa, sin ahorro medido ni prescripción nueva. Su implementación no está autorizada por este encargo. DISCHARGE y TESTS conservan las capacidades existentes y sus límites.

La [decisión preparada sobre PR143](gmfc/DECISION_INTEGRACION_PR143.md) separa controles técnicos favorables de la autorización de fusión aún pendiente. Las [seis fichas científicas](gmfc/COORDINACION_CIENTIFICA_RESIDUAL.md) preparan recepción de evidencia: no son seis lecturas nuevas ni aprobaciones. La búsqueda incremental de correspondencia de este corte no encontró mensajes en los corresponsales acotados; no acredita ausencia de derechos en todo el buzón ni abre fuentes restringidas.

CLINICALLY_PENDING · NOT_FROZEN_NOT_VALIDATED · NO_GO_CLINICAL_RELEASE. Sin nuevos votos médicos, cambios de last_checked, fusión o despliegue.
