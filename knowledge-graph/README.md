# Knowledge graph

Esta capa representa **metadatos y trazabilidad**, no conocimiento clínico inferido automáticamente.

## Grafo determinista
`clinical/scripts/build_project_graph.py` genera relaciones verificables desde:
- `clinical/references/module-index.md`
- `clinical/references/evidence-registry.json`

Tipos actuales:
- `clinical_module`
- `module_bundle`
- `evidence_source`

Relaciones:
- `LOCATED_IN`
- `SUPPORTED_BY`

El generador falla si el manifiesto y el registro de evidencia no contienen exactamente los mismos IDs.

## Próxima fase
Añadir una ontología clínica controlada para:
- síndrome/diagnóstico;
- fármaco;
- dosis/preparación;
- prueba;
- hallazgo ECG/POCUS/imagen;
- procedimiento;
- contraindicación;
- recomendación;
- fuente y versión.

Las relaciones clínicas de esa segunda fase requieren revisión humana antes de incorporarse al grafo estable.
