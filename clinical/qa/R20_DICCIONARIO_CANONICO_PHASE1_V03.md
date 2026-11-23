# Contrato inactivo de Fase 1 (piel/heridas) v0.3 · diccionario canónico

**23 de noviembre de 2026 · `CLINICALLY_PENDING` · Fase 1 `PROPOSED_INACTIVE`, Fase 2 bloqueada**

Diccionario de los nombres **reales** de [`skin-wound-phase1-contract.proposed.json`](../references/skin-wound-phase1-contract.proposed.json) (`phase1-0.3-proposed`, `DEC-CLIN-R14-02`). Una prueba (`test_the_canonical_dictionary_matches_the_real_contract_fields`) falla si este documento deja de nombrar algún campo, enumerado o causa del contrato. El informe Gemini con otras denominaciones **no está en el repositorio**: la equivalencia campo por campo con esas denominaciones es **No verificada**; este diccionario fija los nombres canónicos que usan el contrato y las pruebas, y cualquier diferencia de nombre es terminológica hasta que se aporte el original y se demuestre una diferencia de semántica o de requisitos.

## Campos por signo (`observations.<signo>`)

| Campo | Valores | Semántica y requisito |
|---|---|---|
| `state` | `observable`, `not_observable`, `uncertain`, `not_assessable`, `not_applicable` | cinco estados cerrados |
| `uncertainty_causes` | `no_physical_scale`, `lighting_tint`, `shadow`, `prior_pigmentation`, `topical_product`, `dressing_residue`, `blood_clot`, `overexposure`, `oblique_angle`, `occlusion`, `other`; solo en `visible_edge_separation` además `closure_history_unavailable` | obligatorio y no vacío con `uncertain`; **prohibido** con `not_applicable` |
| `premise_absent_confirmed` | booleano | solo con `not_applicable`, debe ser `true`; un booleano aislado **no** vale |
| `premise_confirmation_source` | objeto cerrado | obligatorio con `not_applicable`; prohibido en los demás estados |
| `wound_closure_history` | `never_closed`, `previously_closed`, `unknown` | solo en `visible_edge_separation`; historial estructurado de registro, nunca inferido de la foto |

## `premise_confirmation_source`

| Campo | Valores | Semántica |
|---|---|---|
| `kind` | `clinician_entry`, `structured_clinical_record` | procedencia estructurada y trazable; **no existe** `direct_visual_fact`, ni fuente visual, de imagen o de modelo |
| `reference` | código opaco `^[A-Za-z0-9_-]{8,64}$` | permite auditar el registro de origen; sin texto libre ni datos personales |
| `recorded_at` | fecha-hora ISO 8601 con zona | cuándo se registró |
| `recorder_role` | `physician`, `nurse`, `other_health_professional` | rol de quien registró |

## Reglas por signo

- `necrotic_appearing_tissue`: `not_applicable` **prohibido**.
- `visible_edge_separation`: `not_applicable` solo con `wound_closure_history = never_closed` y fuente completa; con historial desconocido o ausente: `uncertain` con causa `closure_history_unavailable` (sin inferir de la foto).
- Resto (`chromatic_alteration`, `exudate_compatible_surface_material`, `apparent_deep_structure_exposure`): `not_applicable` solo con `premise_absent_confirmed = true` y fuente completa; ausencia de hallazgo, sombra, oclusión, mala iluminación, desenfoque o información insuficiente **no** pueden sostenerlo (sin campo de texto libre; las causas de incertidumbre son incompatibles con `not_applicable`).
- Entradas incompletas, con campos extra o con valores fuera del enumerado: fallo de validación (`additionalProperties: false`).

## Consumidores y serializadores

Inspección del repositorio: el contrato solo lo referencian su prueba, su registro de decisión y los documentos de estado; **no hay consumidores ni serializadores** en el servidor ni en la aplicación (prueba de no-conexión). No amplía permisos clínicos ni cambia ninguna salida.
