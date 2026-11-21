# R7 · M10 R5-1 / R5-2 · reproducción y ficha de cambio · 21/11/2026

Estado global **CLINICALLY_PENDING**; módulo padre `clinical-image-interpretation` YELLOW. Base `c6f33ad8024906ba91ce1c30c7bddf37785d2741`, árbol `5853eb43d1afc9a625beea2d6a3bfb8d1823f12a`. Reproducción con cadenas sintéticas y proveedor simulado; sin red, proveedor real ni datos de pacientes.

## R5-1 · dependencia de la categoría (reproducido)

La misma salida simulada («Benign lesion, no signs of infection.», impresión «Safe to observe.», confianza `high`) se envió con distintas categorías:

| Archivo / categoría explícita | Categoría resuelta | Resultado |
|---|---|---|
| `herida.png` / `skin_wound` | `skin_wound` | Abstención, `reassurance_language`, confianza retirada |
| `foto_lesion.png` / ninguna | `skin_wound` (pista del nombre) | Abstención, `reassurance_language`, confianza retirada |
| `herida.png` / `other_image` | `other_image` | **Interpretación mostrada**, confianza `high`, sin avisos |
| `IMG_0001.png` / ninguna | `other_image` | **Interpretación mostrada**, confianza `high`, sin avisos |
| `photo.png` / `xray` | `xray` | **Interpretación mostrada**, confianza `high`, sin avisos |

La categoría la elige el cliente (`explicit_kind`) o se infiere del nombre del archivo. Una foto de piel sin pista en el nombre o con categoría distinta queda fuera del filtro. El filtro no se aplica a otras modalidades por diseño (`guard_not_applied_to_other_kinds`).

## R5-2 · variantes (reproducido)

Con la expresión regular vigente (`_REASSURANCE`), sobre texto sintético:

- **Detectadas:** las formas canónicas EN/ES y la forma negada «cannot be excluded» (sobremarca intencionada).
- **No detectadas por codificación (corregido en esta rama):** cero ancho dentro de la palabra, guion blando, letras de ancho completo, acentos descompuestos (NFD).
- **No detectadas por homoglifos:** letra cirílica en lugar de latina. No corregido.
- **No detectadas por redacción (no corregido):** «sin evidencia de infección», «sem evidência de infeção», «no hay signos de infección», «aspecto normal», «bajo riesgo», «low risk», «unremarkable», «no concerning features», «looks healthy», «not suspicious for cellulitis», «consistent with a harmless rash», y el equivalente en chino («良性»).

## Corrección técnica incluida (sin criterio clínico)

`_fold()`: NFKC y eliminación de caracteres de formato invisibles antes de aplicar el mismo léxico. No añade expresiones, no cambia el ámbito (solo `skin_wound`) ni los umbrales. Efecto: las mismas frases ya definidas se detectan también con esas codificaciones. Pruebas: `clinical/tests/test_m10_reassurance_normalization.py`; incluye que otras categorías siguen sin filtro y que el texto descriptivo limpio no se marca. Las etiquetas de proveedor y modelo con caracteres invisibles ya se rechazaban (502).

## Cambios que requieren decisión médica (no implementados)

Evidencia primaria sobre qué expresiones tranquilizadoras no sustentadas deben activar abstención en fotografía de piel: **no recopilada** en esta ficha. Según `AGENTS.md`, no se formula todavía una pregunta SÍ/NO. Candidatos para investigación:

1. Ampliar el léxico con las paráfrasis y los idiomas reproducidos arriba. Riesgo de sobreabstención sobre texto descriptivo legítimo; riesgo de seguridad si no se amplía.
2. Resolver el filtro por contenido y no por la categoría elegida por el cliente, o aplicarlo a más modalidades. En radiología, «normal» es un hallazgo legítimo; requiere definición por modalidad.
3. Tratar homoglifos con una tabla de confusables.

Cada uno cambia el alcance de abstención o de seguridad y requiere fuente vigente, revisión y respuesta explícita del Dr. Juan Copado Ceballos antes de cualquier cambio.
