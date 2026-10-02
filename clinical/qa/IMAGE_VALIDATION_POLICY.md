# IMAGE_VALIDATION_POLICY — v1.36

## Objetivo
Separar estrictamente pruebas de flujo, casos docentes y validación diagnóstica real.

## Niveles
1. **workflow_only** — escenarios sintéticos/textuales o comprobaciones de comportamiento. No evalúan visión.
2. **teaching_source_known** — imagen real con diagnóstico/fuente conocidos antes de interpretar o con anotaciones visibles. Útil para enseñanza/regresión; excluida de métricas de precisión.
3. **blinded_accuracy** — imágenes desidentificadas, intérprete ciego a diagnóstico/referencia, sin anotaciones diagnósticas visibles, referencia independiente y protocolo preespecificado. Puede contribuir a métricas exploratorias del dataset.
4. **prospective_validation** — cohorte prospectiva representativa con referencia independiente/adjudicación y protocolo congelado. Requerida antes de afirmaciones de rendimiento clínico generalizable.

## Gates obligatorios para blinded_accuracy/prospective_validation
- autorización y desidentificación;
- criterios de inclusión/exclusión preespecificados;
- modalidad/pregunta clínica definidas antes de evaluar;
- predicción registrada y congelada antes de revelar referencia;
- referencia independiente del modelo y del prompt;
- intérprete/modelo ciego a diagnóstico final, leyenda y artículo fuente;
- `annotated=false` para anotaciones diagnósticas visibles;
- ID de paciente/estudio único o agrupación explícita para evitar leakage;
- calidad/nondiagnostic incluidos, no descartados post hoc;
- normales/negativos incluidos cuando se calculen especificidad o falsa tranquilidad;
- discrepancias adjudicadas sin reescribir la predicción original.

## Métricas
No calcular sensibilidad/especificidad si:
- dataset no es `blinded_accuracy` o `prospective_validation`;
- no hay referencia independiente;
- no hay positivos y negativos para la condición objetivo;
- casos no diagnósticos fueron eliminados de forma no preespecificada;
- la predicción se modificó después de conocer la referencia.

Los casos `workflow_only` y `teaching_source_known` pueden tener resultados cualitativos de seguridad, pero nunca se suman a sensibilidad, especificidad, accuracy ni calibración clínica.

## Regla de liberación
Un PASS automatizado certifica solo integridad metodológica del registro. No equivale a validación clínica.
