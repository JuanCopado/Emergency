# R45 · Banco de estímulos y controles técnicos

Corte del 24/11/2026 sobre `771ed2bbcc9b0457f5bb8ef75089e236fda7c1d2`. **NOT_FROZEN_NOT_VALIDATED · CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE.** Sin estudio humano ni adjudicación.

## Checklist

| Control | Resultado | Evidencia |
| --- | --- | --- |
| Manifiesto de 30 filas, 10 archivos y 0 adjudicados | PASS | SHA-256 del JSON `bb5eb46b70a652b8996bc56e0089c9923aa186f5367a6ccde1f29b62f848ce6f` |
| Bytes, tamaño, SHA-256 y procedencia de los 10 presentes | PASS | [Manifiesto canónico](../../clinical/lab/human_factors/bank/stimuli_manifest.json) y [tabla por archivo](R41_CODEX_HASH_PROVENANCE.md) |
| Duplicados | PASS | SHA‑256 físico y dHash recalculado. Sin duplicados exactos ni pares cruzados por debajo de 16 bits en los 6 rasters comparables. QA queda fuera de los 30. |
| Corrección de metadatos y dHash | PASS | Dos reproducciones fallaron en el receptor y pasan con el verificador corregido. Una tercera prueba comprueba duplicados físicos con hashes declarados obsoletos. |
| Carga, representación y navegación técnica | PASS | Chromium 154, formulario local de prueba, 6 rasters a 360/390/1280 px, 18 comprobaciones con vuelta y avance, 36 decodificaciones con dimensiones del manifiesto y sin desbordamiento. |
| PDF y control corrupto | PASS | Lectura PDF estricta de 2/1/1 páginas para S1-13/S2-14/S2-15. S1-15 se conserva como JPEG truncado deliberado y se comprueba en las pruebas E2. |
| Integridad canónica | PASS | 10 presentes verifican, 20 ausentes fallan cerrado, 24 registros históricos validan. |
| Revisión formal de privacidad y realismo | BLOCKED | Escaneo de contenedor sin hallazgos en los fixtures presentes. Permanecen pendientes inspección formal visual, revisión de derivados y adjudicación médica. |
| Adquisición de 20 estímulos | BLOCKED | Candidatos de referencia localizados. Faltan capturas o derivados concretos que cumplan el protocolo y tengan trazabilidad y revisión para publicar. |
| QA focal | PASS | 102 pruebas con `test_r25_bank test_r24_alt_b test_r25_dryrun_states test_r41_pr89_canonical_v12 test_r34_canonical_v12`. |

## Inventario y adquisición pendiente

El [inventario R41](R41_CODEX_INVENTARIO_30.md) conserva las fichas individuales, archivos, hashes y especificaciones. Los bytes de los diez presentes son procedurales y el proyecto declara CC0. Cinco son esquemas de ECG o de documento. S2-09 conserva explícitamente su limitación fisiológica. QA-01 y QA-02 son controles técnicos.

| IDs ausentes | Material exacto que falta |
| --- | --- |
| S1-01…07, S2-01…07 | 14 heridas con variedad de tono, iluminación, morfología, cierre, exudado y escenas de distracción prescritas, incluidos los componentes autorizados de las galerías. |
| S1-10, S2-10 | Capturas móviles RGB de monitor simulado con Rx PA de tórax y Rx de muñeca/tobillo, respectivamente. |
| S1-11, S2-11 | Capturas oblicua torácica/abdominal en WebP y de pelvis/tórax con moiré leve en JPEG. |
| S1-12, S2-12 | Capturas de fantoma/ecógrafo en las ventanas FAST y subxifoidea/pulmonar que satisfagan las condiciones del protocolo. |

### Fuentes identificadas para preparación

- Rx · El autor publicó una Rx PA de tórax y una Rx de muñeca procedente de autoexamen con CC0. Son fuentes de imagen candidatas para S1-10/S2-10. Quedan por producir y revisar la captura móvil de monitor y el derivado final. La licencia de copyright se registra separada de la privacidad del original y del derivado. [Tórax](https://commons.wikimedia.org/wiki/File:Normal_posteroanterior_(PA)_chest_radiograph_(X-ray).jpg) · [Muñeca](https://commons.wikimedia.org/wiki/File:X-ray_of_normal_wrist_by_dorsoplantar_projection_(crop).jpg)
- POCUS · La publicación del fantoma eFAST describe ventanas concretas y sus imágenes. Queda identificar la figura y condición exactas y obtener una captura que cumpla el protocolo. El registro interno EchoNet-Dynamic prohíbe redistribución y corresponde a ecocardiografía para otro objetivo. [Fantoma eFAST](https://pmc.ncbi.nlm.nih.gov/articles/PMC12509367/) · [Registro interno](../../clinical/qa/image-dataset-source-registry.json)
- Heridas · La fotografía de moulage bajo CC BY-SA muestra una laceración profunda simulada. Sirve para explorar una fuente de simulación, con atribución, licencia del derivado y revisión de privacidad. S-SYNTH en CC0 contiene lesiones cutáneas renderizadas. Ninguna de las dos referencias establece por sí sola las 14 combinaciones fotográficas exigidas. [Moulage](https://commons.wikimedia.org/wiki/File:Healthcare_Simulation_Moulage_Standardized_Patient_Actor_Deep_Gash_Wound_Cut_on_Wrist.jpg) · [S-SYNTH](https://doi.org/10.57967/hf/3277)

Los 20 IDs conservan archivo, procedencia efectiva y hash vacíos. Los candidatos de referencia quedan fuera del banco hasta que sus derivados se puedan verificar individualmente. PR100 continúa como expediente independiente de pt-BR pendiente de auditoría. [PR100](https://github.com/JuanCopado/Emergency/pull/100).
