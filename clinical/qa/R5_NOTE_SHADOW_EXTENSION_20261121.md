# R5 · Nota clínica: ampliación silenciosa SCA

Estado: **CLINICALLY_PENDING**. Ensayo offline, exclusivamente sintético. No activa ninguna marca en el producto ni altera reglas, pesos, umbrales, recomendaciones, alertas, cálculos o estados clínicos.

## Identidad y ejecución

Producto examinado: `95c5f25f755e27628baf8e5f69f60df2b308ea92`; árbol `8dae69dad71b0b917a2caa35b81a286e4bbf5c74` (internacional tras PR60). El script extrae ese árbol mediante `git archive` a una carpeta temporal; no importa el árbol de trabajo, no instala dependencias y escribe exclusivamente en una nueva carpeta externa. Rechaza identidad de árbol distinta y directorio de salida existente.

Reproducción, desde un clon que conserve ese commit, con Python 3.9 o posterior:

```powershell
python clinical/scripts/run_r5_note_shadow_study.py --repo . --output ../R5-note-study-new
python -m unittest discover -s clinical/tests -p test_diagnostic_observations.py
python clinical/scripts/run_clinical_note_diagnostic_cases.py
python clinical/scripts/run_clinical_note_diagnostic_closure_cases.py
python clinical/scripts/run_clinical_note_pediatric_routing_cases.py
```

Pruebas ejecutadas: **153/153 salidas completas idénticas antes/después del observador y de una segunda ejecución**, **60/60 expectativas aceptadas** (47 generales +8 cierre +5 pediátricas), **12/12 pruebas de observación**. Las 60 entradas originales se obtienen del corpus aceptado sin recortarlas; solo cambia el identificador sintético del encuentro. `study.json` conserva entrada y ambas salidas completas por caso, no únicamente las puntuaciones.

Composición: 60 originales +12 controles R4 +72 pares (3 síndromes ×3 idiomas ×8 contextos) +9 sondas de relaciones no evaluables. Contextos: afirmado, negado, incierto, histórico, otra persona, afirmado+negado, incierto+negado, incierto+hallazgo acompañante.

Artefacto final externo: `A-study-final/study.json` (4.925.302 bytes); SHA256 `1d219bdd7ef8ca8a3f4f0fca4ad464faac4987e4ad2a0a9691fb6e986f7de44b`. Agregado de las 153 salidas canónicas: `b3e9aede69db36ca2ebda3018c76719ca3e8a2be7f0bddbe3c9f4ff5802fbfa1`. No se compara este hash con una versión clínica anterior: «antes/después» significa mismo producto antes/después de observar y repetir.

## Hechos reproducidos

| Hallazgo | Resultado | Interpretación limitada |
|---|---|---|
| SCA: ST posible + náusea, ES/PT/EN | 6 =5 inciertos +1 restante; HIGH condicionado | Cumple el predicado del estudio autorizado; no confirma SCA |
| 12 controles R4 | 4 marcas, igual lógica previa | No hubo cambio de umbral ni ampliación de marca a otros síndromes |
| Nuevos pares SCA | 3 marcas, una por idioma | Total de marcas offline: 7/153; ninguna en los 60 originales |
| ST negado, histórico u otra persona, sin otros hallazgos | Sin activación SCA en los tres idiomas | Prueba acotada de alcance contextual |
| ST afirmado + ST negado | SCA 5, evidencia en contra visible; lista global de contradicciones vacía | No resuelve cuál afirmación es válida; requiere revisión médica |
| Taponamiento original | 9 =6 inciertos +3 restantes | Conservado; eliminar incertidumbre alteraría su categoría |
| Endocarditis original | 7 =5 inciertos +2 restantes | Conservada; no extrapolar la marca SCA a este síndrome |
| «taponamiento cardíaco» / «endocarditis infecciosa», ES | Términos no incluidos; aislados puntúan 0 | Cobertura léxica incompleta real; no se añadió vocabulario |
| Posible endocarditis + «positive blood cultures», EN | 0; el acompañante no está en ese catálogo | No equivale en cobertura a PT «hemoculturas positivas», que da 7 |

La prioridad candidata significa **revisar un hallazgo no confirmado**, no que el motor deba elevar la prioridad asistencial, cambiar el orden o diagnosticar SCA. `confidence` sigue siendo una categoría de puntuación determinista; la certeza clínica no se establece en este ensayo. La marca solo existe en el JSON de investigación.

## Cuatro destinos sin regla y nueve aristas

Se hicieron nueve sondas nuevas que activan cada regla de origen con vocabulario ya existente. Las nueve muestran el identificador no evaluable en limitaciones y no crean una tarjeta diagnóstica para él. No se añadieron reglas, alias ni atajos que sustituyan una entidad clínica por otra.

| Destino no evaluable | Orígenes comprobados | Registro de módulo |
|---|---|---|
| `acute-chest-syndrome` | `sickle-cell-acute-emergency` | No consta como ID registrado |
| `arrhythmias-cardiac-arrest` | `potassium-emergencies`, `adult-arrhythmias`, `toxicology` | Sí, guía cardiovascular; sin regla del mismo ID |
| `pediatric-electrolyte-emergencies` | `pediatric-dka` | Sí, guía poblaciones especiales; sin regla del mismo ID |
| `traumatic-intracranial-mass-effect` | `spontaneous-intracerebral-hemorrhage`, `major-trauma`, `traumatic-head-injury`, `pediatric-head-injury` | Sí, guía neurológica; sin regla del mismo ID |

Son **nueve reglas de origen**, no cinco. Que tres destinos tengan guía registrada no demuestra que exista una regla ejecutable ni que sea clínicamente correcto renombrarlos. La limitación solo se presenta cuando el origen participa entre los cinco primeros síndromes; no constituye vigilancia exhaustiva de todas las relaciones.

## Matriz de riesgos y propuesta inactiva

| Riesgo | Prioridad propuesta | Evidencia / condición | Acción pendiente, no ejecutada |
|---|---|---|---|
| Confundir HIGH con confirmación | P1 clínico | SCA posible+náusea 6, dependiente de incertidumbre | Médico independiente adjudica omisiones y falsas prioridades en un banco ciego; mantener modo silencioso |
| Omisión por idioma | P1 clínico | ES taponamiento/endocarditis y acompañante EN no reconocidos | Propuesta INACTIVA: revisar equivalentes clínicos y validar pares completos antes de añadir términos; no sustituirlos silenciosamente |
| Contradicción no resuelta | P1 clínico | Afirmación+negación conserva score; evidencia en contra sí visible | Propuesta INACTIVA: especificar resolución/aviso de contradicción con médico; sin cancelar automáticamente evidencia ni pesos |
| Destino urgente sin evaluación | P1 clínico | Cuatro destinos/nueve sondas; limitación visible | Determinar si corresponde regla nueva, guía solamente o enlace incorrecto; aprobación clínica y casos antes de implementación |
| Eliminar contribuciones inciertas indiscriminadamente | P1 clínico | Históricos taponamiento9/endocarditis7 dependen de ellas | Mantener conducta actual; cualquier alternativa requiere estudio de regresión médico |
| Interpretar pares sintéticos como precisión clínica | P2 metodológico | Banco construido, sin referencia adjudicada | No publicar sensibilidad, especificidad ni tasa de falsos positivos de estos datos |

No se ha encontrado en este frente un defecto técnico que pueda corregirse sin modificar el comportamiento clínico material. Los hallazgos anteriores no se ocultan ni se marcan resueltos: quedan como decisiones clínicas explícitas. No se modifica ningún estado de validación ni el recuento de módulos.

## Límites y cierre del frente

Extensión del consentimiento previo `R4-SCA-SILENT-20261121 v1`; no solicita otra autorización. No hay pacientes, cohortes externas, PHI, credenciales, despliegue, nuevas alertas ni recomendaciones. No mide precisión médica ni sustituye revisión independiente. Las equivalencias lingüísticas del banco son textos de prueba, no una afirmación de igualdad de cobertura del catálogo. No es fuzz exhaustivo. No se repiten CI/Trivy/Sonar en este frente porque solo se añade un script offline y este informe; la conciliación e integración corresponden al orquestador R5. No se ha hecho push ni creado PR.
