# Composición selectiva R2 E1

Base PR20: `1d0652ebcef9b5990edd9e5745b0c06f8d6b8274`, tree `1c3637918993ca548f75c38bfeade55887af59e4`. Implementador único Codex Work; no CLI, sin commit. El despacho externo vigente delimita archivos y autorizaciones.

| Fuente | Incorporación | Exclusión o conciliación |
|---|---|---|
| P3/P4 b92eb9dc | Deltas de formato, parser, recursos estáticos, pantallas y tests | Maestros históricos y catálogo generado antiguo excluidos; AcuteMedications compuesto sobre required_if, option_labels, revisión y decision_support de PR20 |
| T03 8d972d83 | Guardas numéricas, unidades totales y referencia ponderal, regresiones | No importar su estado antiguo de bloqueos/protamina/ceftriaxona. Underflow positivo→0 reproducido y corregido localmente sin alterar expresiones válidas |
| T01 96228d95 | Selector opcional en Settings, almacenamiento estricto, directorio, resolver no prescriptivo y pruebas | Alternativa98e3ccd no disponible; sin reconstruir. País exigido solo para comparar países explícitos en el directorio, nunca para consultar el núcleo |

`generatedClinicalGuides.json` se regenera con las fuentes de PR20 actuales; si resulta idéntico no se fuerza un delta. Catálogos clínicos, acceptance, evidence-registry, módulos, algoritmos agudos y fuentes canónicas se preservan. El directorio/candidatos T01 conserva SOURCE_CANDIDATES_ONLY y no activa recomendaciones ni cálculo. No constituye nueva verificación regulatoria por integrar los datos.

Las expectativas de coma en entrada, agrupación de miles y mg/kg tras multiplicar por peso quedan sustituidas por el contrato explícito vigente. Sus cifras, controles de rechazo y pruebas originales permanecen. Se mantiene la distinción por toma/día y componente. Los consumidores de bolus/antibiotic se verifican con la suite Python completa; el ambulatorio usa su contrato canónico propio y no hereda esas unidades.

Evidencias, hashes por archivo, diff binario completo, tree efectivo mediante índice temporal y resultados finales se entregan fuera del repositorio en OUTPUT_DIRECTORY. No se importa PASS de ramas previas. La impresión/exportación canónica conserva fuentes e idioma originales; las pruebas DOM no sustituyen navegador real. T06 online, secretos, respaldos y examen reservado fuera del alcance.
