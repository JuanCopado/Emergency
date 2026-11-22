# Emergency · R10 · registro de decisión médica (Fases A y B de R5-1)

**22 de noviembre de 2026 · Estado global `CLINICALLY_PENDING` (129 GREEN / 2 YELLOW / 0 RED) · Sin GO_RELEASE**

Registro de dos decisiones del médico propietario, Dr. Juan Copado Ceballos, sobre las fichas de la especificación técnica `R9_M10_R5_1_ESPECIFICACION_TECNICA` (§8; documento de trabajo, no incluido en el repositorio). El contexto de R5-1 y de los contratos propuestos está en [R8 · contratos propuestos](R8_M10_R5_CONTRATOS_PROPUESTOS_20261121.md) y en la [ficha residual R7](R7_M10_R5_RESIDUAL_FICHA_20261121.md). No se vuelven a solicitar. Este documento solo las registra; no modifica ningún resultado clínico.

## Origen

Las decisiones constan en la instrucción **«EMERGENCY R11 — CLAUDE CODE»** del propietario, recibida en la sesión de trabajo del 22 de noviembre de 2026 (Atlantic/Azores). Se registran tal como las comunicó, con sus ID y su alcance. El texto original no se conserva en el repositorio; la trazabilidad es esta entrada y la fecha de la sesión. Si el propietario quiere otra forma de constancia (firma o documento aparte), puede añadirla; no se presupone.

## Decisiones

| ID | Decisión | Alcance autorizado | Límites expresos |
|---|---|---|---|
| `DEC-CLIN-R10-FASE-A` | **SÍ** | Instrumentación técnica de la Fase A de R5-1: `prepared.kind_assessment` (categoría declarada, pistas del nombre de archivo, sospechas técnicas, `modality_verification=not_verified`), con HMAC, protección de datos, **equivalencia** de encaminamiento y salida clínica, CI y auditoría independiente | No modifica resultados clínicos, confianza, petición al proveedor ni abstenciones. No verifica la modalidad real de la imagen. No usa RGB, EXIF ni la ausencia de DICOM como prueba |
| `DEC-CLIN-R10-FASE-B` | **SÍ A MANTENERLA DESACTIVADA** | Solo **prototipos inactivos** de avisos visibles no diagnósticos | No se activa ningún aviso visible hasta disponer de evidencia de **falsos avisos** y de **usabilidad**. Sin avisos que aparenten haber verificado el contenido de la imagen |

## Qué no cambia

- No se decide el nivel 2 (opciones 2A–2E), la clasificación visual ni expresiones regulares nuevas: siguen pendientes de decisión médica expresa.
- R5-1 (P1) y R5-2 siguen **abiertos**: la Fase A solo aporta datos y no corrige la ausencia de filtro fuera de `skin_wound`.
- La conformidad con la Fase A no autoriza fusionar sin CI ni auditoría independiente del commit exacto, que siguen siendo condiciones de integración.
- C12, G05 y RAG siguen bloqueados o pendientes; no dependen de estas decisiones.

## Implementación vinculada

- Fase A: [PR #73](https://github.com/JuanCopado/Emergency/pull/73), candidato `c6e5c55891d420d5f561d8512c993fc7c33625f2`, en borrador a la espera de la auditoría independiente.
- Fase B: sin implementación activa. La propuesta de diseño está en `R10_FASE_B_Y_WEB_MOBILE_DISENO` (documento de trabajo, no del repositorio).
