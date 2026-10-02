# RSNA ICH 2019 — BLINDED CT PROTOCOL v1.0

Fecha de congelación: 02/10/2026.

## Alcance
Benchmark exploratorio de TC craneal sin contraste para una sola pregunta:
> ¿Existe hemorragia intracraneal aguda en este examen?

No mezclar subtipos con el target primario. Si se evalúan subtipos, crear datasets separados.

## Fuente
RSNA / ASNR Intracranial Hemorrhage Detection Challenge 2019.

- Dataset desidentificado.
- Uso permitido por RSNA para investigación/educación y otros fines no comerciales, con requisitos de atribución y prohibición de reidentificación.
- No interpretar estas condiciones como asesoramiento jurídico; conservar términos descargados y fecha de revisión.

Fuentes:
- https://www.rsna.org/artificial-intelligence/ai-image-challenge/rsna-intracranial-hemorrhage-detection-challenge-2019
- https://www.rsna.org/-/media/files/rsna/education/ai-resources-and-training/ai-image-challenge/rsna_ich_ai_challenge_2019_terms_of_use_and_attribution_final.pdf
- Flanders AE et al. Radiology: Artificial Intelligence. 2020;2(3):e190211.

## Referencia preespecificada
Para métricas de accuracy se admiten únicamente exámenes cuya procedencia de referencia pueda verificarse como:
1. lectura independiente por tres neurorradiólogos con consenso mayoritario 2/3; o
2. adjudicación por neurorradiólogo sénior cuando el protocolo fuente requirió adjudicación.

El paper RSNA describe 3.528 exámenes triple-read y 525 exámenes adjudicados por discrepancias. Los exámenes con una sola lectura no se aceptan automáticamente como referencia independiente de este benchmark.

Fail-closed: si los archivos disponibles no permiten demostrar qué examen pertenece a la cohorte multi-reader/adjudicada, ese examen no entra en blinded_accuracy.

## Unidad de análisis
- Unidad primaria: examen/estudio, no slice.
- Todas las imágenes de un mismo StudyInstanceUID permanecen juntas.
- No dividir slices del mismo examen entre shards.
- Si existe identificador de paciente reutilizable, todos sus estudios permanecen en el mismo grupo de evaluación.

## Target
any_acute_ich
- positivo: referencia experta de hemorragia intracraneal aguda presente en el examen;
- negativo: referencia experta de ausencia de ICH aguda;
- subtipos no modifican el target primario.

## Imagen / DICOM
- Mantener DICOM originales fuera del repositorio.
- El model-facing dataset nunca contiene tags identificativos fuente.
- Antes de evaluación visual debe congelarse un render DICOM -> imagen reproducible.
- v1.0 no impone una ventana CT inventada. Se debe usar una estrategia VOI/window documentada y congelada antes de predicciones.
- Ninguna selección/eliminación de slices puede depender del diagnóstico conocido.

## Cegamiento
1. Ingesta y hashing de estudio/paciente.
2. Crear manifiesto ciego de exámenes y slices sin labels.
3. Separar referencia en archivo sellado.
4. Interpretar examen completo.
5. Registrar positive / negative / abstain / nondiagnostic.
6. Congelar predicción y timestamp.
7. Solo después revelar referencia.
8. Ejecutar gate v1.1 y métricas.

## Límites
- Benchmark retrospectivo público: posible exposición previa del modelo al dataset.
- No equivale a validación prospectiva.
- No promover módulos a green por este benchmark.
