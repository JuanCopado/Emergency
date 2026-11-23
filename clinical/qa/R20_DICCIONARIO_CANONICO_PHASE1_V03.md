# Contrato inactivo de Fase 1 (piel/heridas) v0.3 · diccionario canónico

**23 de noviembre de 2026 · `CLINICALLY_PENDING` · Fase 1 `PROPOSED_INACTIVE`, Fase 2 bloqueada**

Diccionario de los nombres **reales** de [`skin-wound-phase1-contract.proposed.json`](../references/skin-wound-phase1-contract.proposed.json) (`phase1-0.3-proposed`, `DEC-CLIN-R14-02`). Una prueba (`test_the_canonical_dictionary_matches_the_real_contract_fields`) falla si este documento deja de nombrar algún campo, enumerado o causa del contrato. Los informes Gemini R19/R20 (denominaciones `clinician_structured_input`, `verified_structured_clinical_record`, `prior_closure_unconfirmed`) se aportaron al coordinador y se han contrastado con el JSON real (sección siguiente); este diccionario fija los nombres canónicos que usan el contrato y las pruebas.

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

## Equivalencia con las denominaciones de Gemini (R19/R20, matriz de la sección 8)

| Denominación Gemini | Nombre canónico (contrato real) | Equivalencia |
|---|---|---|
| `clinician_structured_input` | `clinician_entry` | terminológica: entrada estructurada de un profesional, con `reference`, `recorded_at` y `recorder_role` |
| `verified_structured_clinical_record` | `structured_clinical_record` | terminológica: registro clínico estructurado auditable por `reference` |
| `prior_closure_unconfirmed` | `closure_history_unavailable` | terminológica: causa específica y cerrada de `uncertain` en `visible_edge_separation` cuando falta el historial de cierre |
| `wound_closure_history == "never_closed"` | `wound_closure_history = never_closed` | idéntica |

**Foco A (fuentes estructuradas): se cumplen todos los criterios de diferencia meramente terminológica.** (1) Solo fuentes estructuradas (`kind` cerrado a dos valores); (2) correspondencia semántica 1:1 de arriba; (3) fuente visual, de imagen, de modelo, texto libre, `null` o vacío: fallo de validación (pruebas con `direct_visual_fact`, `visual_inspection`, `photo`, `image`, `model`, `classifier`, `unverified`); (4) `premise_absent_confirmed = true` exigido, `not_applicable` prohibido en necrosis, y en separación de bordes solo con `never_closed`; sin consumidores ni serializadores que romper.
**Foco B (historial ausente): se cumplen todos.** Con historial ausente o `unknown` el contrato exige `uncertain` con la causa específica `closure_history_unavailable` (separada de las causas visuales como `shadow` o `blood_clot`); `not_applicable`, `not_assessable` y `not_observable` no sustituyen a `uncertain`; forzar `not_applicable` con historial ausente o `unknown` falla la validación.
**Dictamen:** diferencia meramente terminológica; se congela este diccionario como fuente única de nombres (sin nueva decisión médica ni cambio del contrato). Si el esquema de Gemini (`CRF-B`) usa otros literales, deben alinearse a estos.
