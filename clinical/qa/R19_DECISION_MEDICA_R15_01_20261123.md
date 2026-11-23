# Emergency · R19 · registro de la decisión médica DEC-CLIN-R15-01

**Decisión recibida el 23 de noviembre de 2026 a las 00:29:57 UTC (22/11/2026 23:29:57 Atlantic/Azores) · Estado global `CLINICALLY_PENDING` (129 GREEN / 2 YELLOW / 0 RED) · Sin GO_RELEASE**

Registro de una decisión del médico propietario, Dr. Juan Copado Ceballos. No se vuelve a solicitar. Solo registra; no modifica ningún resultado clínico ni las aprobaciones anteriores ([R14-01](R16_DECISION_MEDICA_R14_01_20261123.md), [R14-02](R15_DECISION_MEDICA_R14_02_20261122.md)).

## Procedencia

- **Textos literales (R20):** el propietario comunicó en la instrucción R20 (23/11/2026) los cuatro mensajes exactos del expediente R18 y su correspondencia con los disparadores; se incorporan sin reescritura.
- Registro de la decisión: [comentario de PR #83](https://github.com/JuanCopado/Emergency/pull/83#issuecomment-7088406106) («DEC-CLIN-R15-01: SÍ. Apruebo exclusivamente la especificación inactiva descrita en el expediente R18, sin activación clínica ni GO_RELEASE»), y la instrucción R19 del propietario que la confirma en la conversación de trabajo.
- Es un **registro de instrucción: no es firma física ni revisión independiente del código**. El expediente `R18_GEMINI_DECISION_CLINICA_FINAL` (v1.0, apartado 1) **no está en el repositorio**: sus textos literales **no se han recibido**.

## Decisión y alcance (solo especificación/prototipo INACTIVO de la capa 7)

1. Cuatro disparadores cerrados: `T7-01_UNDECLARED_MODALITY`, `T7-02_UNKNOWN_CONTRACT`, `T7-03_CORRUPT_UNPROCESSABLE`, `T7-04_FORMAT_CONTAINER_MISMATCH`.
2. Cuatro mensajes neutros exactos en ES/PT AO90/EN, sin generación dinámica de texto clínico.
3. Protección del flujo clásico y de documentos de PR82 (`document_legacy_bridge`, `kind=null`): `T7-01` y `T7-02` no crean bloqueos nuevos.
4. Sin abstención basada en RGB, EXIF, nombre de archivo, ausencia de DICOM, extensión aislada ni sospecha clínica no demostrada.
5. Sin forzar el envío ante corrupción o incompatibilidad técnica objetiva; capa 7 apagada tras bandera.

## Implementación (PR #83, contrato `layer7-0.2-proposed`)

[`modality-abstention-layer7.contract.proposed.json`](../references/modality-abstention-layer7.contract.proposed.json): disparadores cerrados con su evidencia exigida (T7-01 sin modalidad declarada; T7-02 tipo declarado fuera del registro de contratos; T7-03 error de análisis del contenedor; T7-04 firma del contenedor emparejada con formato declarado, nunca extensión sola), flujos protegidos, `send_allowed=false` en toda abstención, evidencia prohibida cerrada y bandera `VITE_R51_LAYER7` apagada (ignorada en producción). 14 pruebas (negativas por disparador y flujo; mutación verificada).

**Textos incorporados (R20), literales, es/pt AO90/en** (`x-message-texts`, prueba de igualdad con copia independiente):

| Mensaje | Disparador(es) | Contenido |
|---|---|---|
| `MSG_T7_A` | T7-01 y T7-02 (comparten texto) | no se ha seleccionado una modalidad admitida; el sistema no identifica el tipo automáticamente |
| `MSG_T7_B` | T7-04, variante incompatibilidad de modalidad (firma del contenedor frente al formato declarado) | archivo no compatible con la modalidad; contenido no evaluado |
| `MSG_T7_C` | T7-03 (archivo dañado) | archivo dañado o no procesable; sin evaluación clínica |
| `MSG_T7_D` | T7-04, variante formato global no admitido (`container_format_unsupported`) | formato no admitido por la función; contenido no analizado |

T7-04 tiene dos variantes que fija **la causa técnica objetiva** (evidencia exigida distinta), nunca una inferencia clínica. Provenance de los textos: expediente R18 comunicado por el propietario; el expediente no está en el repositorio.

## Qué no cambia

Sin conexión al producto ni a salidas clínicas activas; sin producción, `GO_RELEASE`, regex ni filtros nuevos; R5-1 (P1) abierto; R5-2 pendiente; capa 8 sin estudio ejecutado; Fase B, Fase 2, G05, RAG y APIs externas bloqueados; `CLINICALLY_PENDING`.
