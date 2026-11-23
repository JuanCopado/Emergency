# Emergency · R16 · registro de la decisión médica DEC-CLIN-R14-01

**Decisión recibida el 22 de noviembre de 2026 hacia las 23:55 UTC (23/11/2026 en horario peninsular español; la zona horaria del propietario no consta: No verificado) · Estado global `CLINICALLY_PENDING` (129 GREEN / 2 YELLOW / 0 RED) · Sin GO_RELEASE**

Registro de una decisión del médico propietario, Dr. Juan Copado Ceballos, tal como la comunicó. No se vuelve a solicitar. Solo registra; no modifica ningún resultado clínico ni las aprobaciones anteriores ([R10](R10_DECISION_MEDICA_FASE_A_B_20261122.md), [R12](R12_DECISION_MEDICA_R8_20261122.md), [R15](R15_DECISION_MEDICA_R14_02_20261122.md)).

## Origen y procedencia

Instrucción **«EMERGENCY R16 — CLAUDE CODE»** (misión 1), sesión de trabajo del 22/11/2026 (UTC): aprobación médica confirmada («SÍ») de los cinco textos clínicos exactos de la sección 1.2 del expediente Gemini R15, exclusivamente para prototipos inactivos y pruebas de factores humanos. El expediente Gemini R15 **no está en el repositorio**; la procedencia de los textos es la instrucción que los reproduce. No existe firma física ni documento aparte.

## Decisión

| ID | Decisión | Alcance |
|---|---|---|
| `DEC-CLIN-R14-01` | **SÍ** | Cinco textos fijos de limitación (piel/heridas, ECG, radiografía, POCUS, documentos) en es, pt y en, solo para el prototipo R5-1 inactivo y las pruebas de factores humanos. |

## Conciliación de fecha, identificador y procedencia

- **Fecha registrada:** `2026-11-22` (UTC), coherente con `approved_on` del recurso. El nombre del archivo conserva `20261123` por haberse creado ya en el día siguiente UTC; no es la fecha de la decisión.
- **Identificador:** `DEC-CLIN-R14-01`. Aprueba **solo** estos cinco textos; no atribuye aprobación a ningún otro texto, a otros idiomas ni a `DEC-CLIN-R15-01` (capa 7, **no aprobada**).
- **Procedencia de la cadena literal:** transcrita de la instrucción R16; el expediente Gemini R15 no está en el repositorio, por lo que la comparación 15/15 contra ese expediente corresponde a la auditoría independiente (huella SHA-256 de los textos en el encargo de auditoría).

## Implementación (PR #82)

- Recurso determinista [`app/src/clinical-note/r51-limitations.approved.json`](../../app/src/clinical-note/r51-limitations.approved.json): texto literal, sin generación ni reescritura. Una copia independiente en la prueba `r51-prototype.test.tsx` falla ante cualquier edición.
- Se muestra solo en el prototipo inactivo (bandera apagada por defecto; ignorada en producción). `r51:flag-check` comprueba que ni el código ni estos textos viajan en un paquete de producción con la bandera a 1.
- Núcleo portugués común conforme al AO90; no se crean variantes regionales (no hay variantes terminológicas aprobadas). zh no tiene texto aprobado: muestra el inglés.
- Si falta decisión, fecha o algún idioma, la interfaz vuelve al texto provisional (fail-closed).

## Qué no cambia

Sin activación en producción; sin cambio de servidor, encaminamiento, filtros ni abstenciones; la confirmación humana sigue sin verificar el contenido; R5-1 (P1) y R5-2 siguen abiertos; capa 7 no implementada (DEC-CLIN-R15-01 pendiente). Una aprobación de texto no es validación clínica ni autoriza fusionar sin CI ni auditoría independiente del commit exacto.
