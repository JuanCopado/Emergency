# Emergency · R15 · registro de la decisión médica DEC-CLIN-R14-02

**22 de noviembre de 2026 · Estado global `CLINICALLY_PENDING` (129 GREEN / 2 YELLOW / 0 RED) · Sin GO_RELEASE**

Registro de una decisión del médico propietario, Dr. Juan Copado Ceballos, tal como la comunicó. No se vuelve a solicitar. Solo registra; no modifica ningún resultado clínico ni las aprobaciones anteriores ([R10](R10_DECISION_MEDICA_FASE_A_B_20261122.md), [R12](R12_DECISION_MEDICA_R8_20261122.md)).

## Origen

Instrucción **«EMERGENCY R15 — CLAUDE CODE»**, sesión del 22 de noviembre de 2026. El texto original no se conserva en el repositorio; la trazabilidad es esta entrada y la fecha. No existe firma física ni documento aparte.

## Decisión

| ID | Decisión | Texto comunicado |
|---|---|---|
| `DEC-CLIN-R14-02` | **SÍ, con precisión** | `not_applicable` solo con ausencia de premisa confirmada y procedencia verificable; prohibido para tejido superficial de aspecto necrótico; para separación de bordes, solo con historial estructurado de herida nunca cerrada; el resto, sin inferir de la imagen. |

## Alcance (implementado solo en el contrato inactivo, enmienda 0.3)

[`skin-wound-phase1-contract.proposed.json`](../references/skin-wound-phase1-contract.proposed.json), `phase1-0.3-proposed`:

1. `not_applicable` exige `premise_absent_confirmed=true` **y** `premise_confirmation_source`; un booleano aislado no vale.
2. Fuente: `kind` ∈ {`clinician_entry`, `structured_clinical_record`}, `reference` (código opaco), `recorded_at`, `recorder_role`. Nunca imagen, modelo ni ausencia de hallazgo.
3. `necrotic_appearing_tissue`: `not_applicable` prohibido.
4. `visible_edge_separation`: `not_applicable` solo con `wound_closure_history="never_closed"`. Si falta el historial no se infiere de la foto: `uncertain` con causa `closure_history_unavailable`.
5. Resto de signos: `not_applicable` no puede sostenerse en ausencia de hallazgo, sombra, oclusión, mala iluminación, desenfoque o información insuficiente (sin texto libre; causas de incertidumbre incompatibles con `not_applicable`).

## Qué no cambia

Fase 1 sigue `PROPOSED_INACTIVE`; Fase 2 bloqueada; sin conexión al producto; sin cambio de salida clínica, filtros ni abstenciones; las premisas por signo siguen pendientes de redacción médica. Ninguna decisión autoriza fusionar sin CI ni auditoría independiente del commit exacto.
