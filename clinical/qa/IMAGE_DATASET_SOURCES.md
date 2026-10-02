# IMAGE_DATASET_SOURCES — candidatos para banco ciego v1.36

Fecha de revisión: 02/10/2026.

## Regla
Estos datasets son **fuentes candidatas**, no resultados de validación. Antes de incorporar cualquier caso:
1. revisar licencia/DUA y condiciones de redistribución;
2. mantener imágenes fuera del repositorio cuando la licencia prohíba redistribuir;
3. generar hashes paciente/estudio;
4. definir una única modalidad + target por dataset;
5. congelar la predicción antes de revelar la referencia;
6. documentar el tipo de referencia independiente.

## ECG — PTB-XL / PhysioNet
- Dataset abierto de ECG de 12 derivaciones, con identificadores de paciente/ECG y anotaciones SCP-ECG.
- Licencia pública: CC BY 4.0 en PhysioNet.
- Una gran fracción de registros fue validada por un segundo cardiólogo; todos pasaron control técnico.
- **Uso propuesto:** crear un benchmark de ECG renderizado a imagen manteniendo la referencia separada del prompt.
- **Límite:** PTB-XL es señal/waveform; un render limpio no evalúa robustez a fotografía, perspectiva, reflejos, recortes o papel real.
- Fuente oficial: https://physionet.org/content/ptb-xl/

## Radiografía de tórax — CheXpert
- Dataset de radiografías de tórax con etiquetas de incertidumbre y comparación con expertos.
- **Uso propuesto:** targets binarios separados (p. ej. neumotórax, edema, derrame) en un subset con referencia experta apropiada.
- **Límite:** no convertir todas las etiquetas automáticas/derivadas en referencia independiente sin revisar su procedencia.
- Fuente oficial: https://stanfordmlgroup.github.io/competitions/chexpert/

## Radiografía de tórax — MIMIC-CXR v2.1.0
- Base desidentificada con DICOM/informes radiológicos; acceso credentialed y DUA en PhysioNet.
- Versión pública vigente identificada: 2.1.0 (2024).
- **Uso propuesto:** evaluación ciega con imágenes originales y referencia construida desde informe/adjudicación independiente.
- **Límite:** las etiquetas estructuradas disponibles en variantes JPG pueden derivarse de herramientas NLP; no deben asumirse automáticamente como gold standard.
- No redistribuir datos fuera de lo permitido por la DUA.
- Fuente oficial: https://physionet.org/content/mimic-cxr/

## TC cerebral — RSNA Intracranial Hemorrhage Detection
- Más de 25.000 exámenes de TC cerebral de múltiples instituciones.
- Anotaciones realizadas por más de 60 radiólogos voluntarios de RSNA/ASNR para presencia y subtipos de hemorragia intracraneal.
- **Uso propuesto:** primera cohorte de TC para un target binario preespecificado como hemorragia intracraneal aguda presente/ausente; subtipos en datasets separados si se desea.
- **Ventaja metodológica:** referencia experta y heterogeneidad multiinstitucional.
- **Límite:** revisar términos actuales de acceso/uso antes de importar imágenes.
- Fuente oficial: https://www.rsna.org/artificial-intelligence/ai-image-challenge/rsna-intracranial-hemorrhage-detection-challenge-2019

## Ecocardiografía / POCUS cardiaco — EchoNet-Dynamic
- Más de 10.000 vídeos apicales de 4 cámaras de pacientes únicos.
- Incluye fracción de eyección, volúmenes y trazados realizados por sonógrafo avanzado y revisados por cardiólogo de imagen.
- **Uso propuesto:** target estrecho de función ventricular izquierda/categoría preespecificada, no como sustituto de un dataset general de POCUS de urgencias.
- **Límite:** no cubre de forma representativa eFAST, pulmón, DVT, aorta o múltiples ventanas de POCUS de urgencias.
- Uso sujeto al acuerdo de investigación de Stanford; no redistribuir el dataset.
- Fuente oficial: https://aimi.stanford.edu/datasets/echonet-dynamic-cardiac-ultrasound

## Ecocardiografía pediátrica — EchoNet-Pediatric
- 7.643 vídeos etiquetados con anotaciones expertas en pacientes de 0 a 18 años.
- **Uso propuesto:** futura cohorte pediátrica de función ventricular, separada del benchmark adulto.
- Fuente oficial: https://aimi.stanford.edu/datasets/echonet-pediatric

## Orden práctico de construcción
1. **ECG:** PTB-XL -> render estandarizado + target individual, conservando folds/paciente para evitar leakage.
2. **TC cerebral:** RSNA ICH -> hemorragia sí/no como primer target de imagen transversal.
3. **Rx tórax:** CheXpert o MIMIC-CXR -> target único por dataset y referencia experta/adjudicada.
4. **POCUS cardiaco:** EchoNet-Dynamic -> solo tareas compatibles con vista/labels del dataset.
5. Expandir después a otras modalidades únicamente cuando exista dataset con referencia adecuada.

## No hacer
- no usar imágenes conocidas de artículos docentes como test ciego;
- no mezclar entrenamiento/enseñanza con test final;
- no convertir etiquetas NLP en referencia experta sin documentarlo;
- no excluir post hoc imágenes difíciles/no diagnósticas;
- no subir datasets con DUA/licencia restrictiva al repositorio;
- no informar sensibilidad/especificidad hasta pasar `IMAGE_VALIDATION_POLICY.md`.


## Estado de intake — 02/10/2026
- **PTB-XL:** licencia CC BY 4.0 verificada en PhysioNet; protocolo preespecificado en `qa/PTBXL_BLINDED_PROTOCOL.md`; separación de labels/hashes implementada en `scripts/prepare_ptbxl_blinded_cohort.py`. Estado: **intake-ready**, no validado.
- **RSNA ICH 2019:** términos RSNA revisados; protocolo de referencia/label isolation congelado en `qa/RSNA_ICH_BLINDED_PROTOCOL.md`. Solo multi-reader majority/adjudicated verified; single-reader fail-closed. Estado: **raw intake-ready**, evaluación visual aún requiere congelar DICOM→render.
- **CheXpert:** expert test protocol frozen (`qa/CHEXPERT_EXPERT_TEST_PROTOCOL.md`): 500 studies/500 unseen patients, majority vote of 5/8 board-certified radiologists; training NLP/rule-based labels excluded as expert truth. Still blocked on dataset-specific current AIMI/Redivis license/download terms.\n- **MIMIC-CXR 2.1.0:** source-level intake protocol complete using only the manually curated test-set labels; automated CheXpert/NegBio labels excluded. Credentialed PhysioNet access, CITI training and signed DUA remain required before actual download; no restricted files in repo.\n- **EchoNet-Dynamic:** source-level intake protocol complete for `lvef_below_40_percent` on official TEST split only. Research Use Agreement verified: personal/non-commercial, no redistribution, no clinical use. Individual registration/agreement still required before download.
- `intake-ready` significa únicamente que la fuente puede entrar al pipeline de preparación. **No implica sensibilidad/especificidad ni validación clínica.**
