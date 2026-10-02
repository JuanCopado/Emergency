# PTB-XL BLINDED ECG PROTOCOL — v1.36

Fecha de congelación documental: 02/10/2026.

## Alcance
Primer protocolo de intake real para Fase 5. Evalúa ECG de 12 derivaciones derivados de PTB-XL como **benchmark exploratorio de imagen**, no como validación clínica generalizable.

## Fuente
- PTB-XL en PhysioNet.
- Licencia revisada: CC BY 4.0.
- Versión pública identificada: 1.0.3; usar la versión realmente descargada y conservar DOI/checksums.
- PTB-XL define folds estratificados a nivel paciente; folds 9 y 10 tienen mayor calidad de etiqueta y el propio dataset propone fold 10 como test.

## Cohorte preespecificada
- `strat_fold == 10`.
- Un único target SCP-ECG por ejecución.
- Positivos y negativos obligatorios.
- No excluir post hoc trazados difíciles por el resultado de la interpretación.
- Mantener todos los registros del mismo paciente agrupados mediante hash de `patient_id`.

## Blinding
1. Ejecutar `scripts/prepare_ptbxl_blinded_cohort.py`.
2. Generar un archivo de cohorte sin labels y un archivo de referencia separado.
3. Mantener el archivo de referencia fuera del contexto del intérprete/modelo.
4. Renderizar los waveforms a imagen con parámetros congelados antes de interpretar.
5. Registrar y congelar `positive / negative / abstain / nondiagnostic`.
6. Solo después revelar la referencia y construir el manifiesto completo v1.1.
7. Ejecutar `validate_blinded_image_dataset.py` y después `calculate_blinded_image_metrics.py`.

## Riesgos y límites
- PTB-XL es waveform; un render limpio no representa fotografías de papel, perspectiva, reflejos o recortes.
- La exposición del modelo a PTB-XL durante preentrenamiento no puede excluirse; por ello el resultado es un benchmark exploratorio y no una validación externa independiente del modelo.
- Las etiquetas SCP-ECG no deben reinterpretarse como una adjudicación clínica nueva.
- No informar sensibilidad/especificidad si existen abstenciones/no diagnósticos bajo la política v1.1.
- No promover módulos clínicos a green por el resultado de este benchmark.
