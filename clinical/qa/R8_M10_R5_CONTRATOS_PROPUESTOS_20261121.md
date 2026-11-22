# R8 · M10 R5-1/R5-2 · contratos propuestos (INACTIVOS) y corpus sintético · 21/11/2026

Estado global **CLINICALLY_PENDING**; módulo padre `clinical-image-interpretation` YELLOW. Base `0e68e5ee654e7be452cbb7cb5e5fb22b8b1127ed`, árbol `81a5cc74e41aa70deb6a9a70211fd8ce70c32cb7`. Documento de **especificación**: nada de lo que sigue está conectado al producto ni autoriza cambios clínicos. La propuesta científica de partida es Gemini `R7-CONCILIACION-SEGURIDAD-DECISIONES v1.3`; **no es una aprobación médica**. Decisiones pendientes: `DEC-CLIN-R7-03` y `DEC-CLIN-R7-06`, del Dr. Juan Copado Ceballos.

## 1. Lo ya implementado (solo transparencia, PR de R8)

`prepare_upload` informa de `kind_source` y la tarjeta muestra la categoría efectiva y su origen. No verifica la modalidad real y no cambia encaminamiento, filtros, abstenciones, confianza ni petición al proveedor.

| `kind_source` | Significado |
|---|---|
| `explicit` | El cliente envió una categoría |
| `inferred_from_filename` | Una pista del nombre de archivo (subcadena) |
| `inferred_from_container` | `.dcm`, `.pdf` o MIME equivalente |
| `default_unclassified` | Ni categoría ni pista; se trata como `other_image` |

Límite honesto: la interfaz envía `undefined` cuando el selector está en «Outro». «Outro» elegido a propósito y «Outro» por defecto son indistinguibles para el servidor; ambos aparecen como `default_unclassified`.

## 2. Contrato futuro de categoría (propuesto, no activado)

| Elemento | Campo propuesto | ¿Comprobable hoy con metadatos? | ¿Requiere sistema adicional? |
|---|---|---|---|
| 1. Categoría explícita | `kind_explicit` | Sí: lo envía el cliente | No |
| 2. Categoría inferida | `kind_inferred`, `kind_source` | Sí: nombre y contenedor (ya existe `kind_source`) | No |
| 3. Modalidad no verificable | `modality_verification` ∈ `not_verified` / `metadata_consistent` / `classifier_verified` | Solo `not_verified`. `metadata_consistent` solo sería honesto con DICOM (`Modality`); PDF y PNG/JPEG/WebP no la declaran | `classifier_verified` exige un clasificador de imagen propio, con validación, riesgo fuera de distribución y su propia ficha |
| 4. Discordancia entre categorías | `kind_discordance` ∈ `none` / `explicit_vs_inferred` / `name_hint_conflicts_with_effective` / `unknown` | Parcial: se puede detectar por nombre (p. ej. categoría explícita `other_image` con pista de piel). Con falsos positivos: la pista es una subcadena | Para discordancia con el contenido real, sí (clasificador) |
| 5. Decisión de abstención | `abstention.decision` ∈ `none` / `abstain_modality_doubt` / `abstain_quality` / `abstain_provider` / `abstain_contradiction` | La parte técnica (calidad, proveedor) ya existe. `abstain_modality_doubt` **depende de definir «dudosa»** | Decisión médica `DEC-CLIN-R7-06` |
| 6. Procedencia de la salida | `provenance` ∈ `provider_structured` / `clinician_entry` | Sí | No |
| 7. Motivo de revisión humana | `human_review_reasons[]` (códigos cerrados) | Sí, para los motivos técnicos | Los clínicos, tras la decisión |

**Definiciones alternativas de «categoría dudosa»** (para `DEC-CLIN-R7-06`, sin elegir ninguna):

| Definición | Efecto previsible |
|---|---|
| A. Sin categoría enviada y sin pista en el nombre (`default_unclassified`) | Toda subida con el selector por defecto se abstendría; cubre el caso `IMG_xxxx.jpg`, pero también todas las no cutáneas |
| B. `kind_discordance ≠ none` | Menos abstenciones; no cubre fotos de piel con nombre neutro ni con la categoría errónea sin pista |
| C. Contenido de aspecto cutáneo enviado como otra modalidad | Es la única que ataca la causa; **no es posible con metadatos** y exige clasificador |
| D. Combinación A+B con aviso (sin abstención) | Solo transparencia reforzada; no cambia la seguridad del texto |

Qué NO se hace aquí: clasificación automática de la imagen, confirmaciones nuevas ni abstención por modalidad dudosa.

## 3. Contrato de Fase 1 (piel y heridas) · borrador inactivo

Archivo: `clinical/references/skin-wound-phase1-contract.proposed.json` (JSON Schema 2020-12; `x-status: PROPOSED_INACTIVE`).

- **Cinco observaciones** (`chromatic_alteration`, `exudate_compatible_surface_material`, `necrotic_appearing_tissue`, `visible_edge_separation`, `apparent_deep_structure_exposure`) con estados cerrados `observable` / `not_observable` / `uncertain` / `not_assessable`.
- `uncertain` exige al menos una causa de un catálogo cerrado (sin escala, tinte de iluminación, sombra, pigmentación previa, producto tópico, resto de apósito, coágulo, sobreexposición, ángulo oblicuo, oclusión, otra).
- **Sin texto libre y sin Fase 2**: `additionalProperties: false` rechaza `impression`, clases de alarma o cualquier campo no listado.
- **Cláusula anti-exclusión como texto fijo de la interfaz**, referida por `fixed_clause_id`; el modelo nunca la genera. El español es la redacción propuesta en `R7-CONCILIACION-METODOLOGICA v1.2`, **sin aprobar**. pt-PT, pt-BR y en están a `null`: requieren redacción médica nativa, no traducción automática.
- La Fase 2 (clasificación de signos de alarma o priorización) permanece **bloqueada**.

**Estado real que este contrato no cambia.** Hoy el proveedor devuelve texto libre (`ai_interpretation`, `findings`, `impression`, `limitations`). Existe una cláusula parcial en inglés (`SKIN_WOUND_FIXED_LIMITATIONS`) que no se añade en las abstenciones del proveedor.

**Plan de migración propuesto (nada ejecutado):**
1. Esta especificación y el esquema, con pruebas de validez (hecho; sin conexión al producto).
2. Validador offline que compruebe salidas simuladas contra el esquema.
3. Campo aditivo opcional `phase1` en la respuesta, con la salida libre intacta y detrás de una bandera desactivada. Exige compatibilidad con proveedores que no lo emitan y revisión del `contract_version`.
4. Modo sombra: validar y registrar sin mostrar, con revisión independiente.
5. Presentación y retirada gradual de la salida libre **solo** tras aprobar `DEC-CLIN-R7-03`, con plan de migración y compatibilidad verificada.

Coste real: cambia el contrato con el proveedor, la interfaz y las pruebas. No es un ajuste menor.

## 4. R5-2 · corpus sintético congelable

Archivos: `clinical/qa/corpus/r8_reassurance_synthetic_corpus_v0.json` y su `.sha256` (`bf00cde1fd51dc60c0d4e66726e01c0aba158f4552e422e21bfff27277593405`). 80 casos, 4 estratos (es-ES, pt-PT, pt-BR, en) y 7 clases: tranquilidad explícita, paráfrasis, advertencia negada (controles negativos duros), descripción neutra, variante Unicode, homoglifo y contradicción.

**Las etiquetas son de construcción de ingeniería, no adjudicación médica** (`UNADJUDICATED_ENGINEERING_DRAFT`). No estiman sensibilidad ni especificidad. No se activa ningún disparador nuevo.

Línea base del filtro vigente (`scripts/run_r8_reassurance_baseline.py`; no cuenta las 4 contradicciones):

| Medida | Resultado |
|---|---|
| Falsos negativos (tranquilizadoras sin interceptar) | **27 de 52** |
| Falsos positivos (advertencias negadas o neutras interceptadas) | **6 de 24** |
| Variantes Unicode interceptadas | 16 de 16 |
| Homoglifos interceptados | 0 de 4 |
| Por idioma, FN | es-ES 7/13 · pt-PT 7/13 · pt-BR 7/13 · en 6/13 |
| Por idioma, FP | es-ES 2/6 · pt-PT 1/6 · pt-BR 1/6 · en 2/6 |

Las pruebas verifican integridad (hash), estratificación y que las variantes Unicode se interceptan; **no** afirman que las paráfrasis se detecten.

## 5. Dependencias de decisión médica

- `DEC-CLIN-R7-06`: política de abstención ante categoría dudosa y definición de «dudosa».
- `DEC-CLIN-R7-03`: Fase 1 descriptiva, contrato de cinco signos y cláusula fija (redacción nativa).
- `DEC-CLIN-R7-01`: portugués como estrato; antes de adjudicar el corpus.
- Adjudicación ciega del corpus por médicos competentes en cada idioma, con tercero dirimente, antes de usar sus cifras como algo más que regresión.
- Sin decisión: clasificador de imagen, filtro por contenido, ampliación del léxico y homoglifos.
