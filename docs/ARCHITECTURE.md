# Emergency — arquitectura consolidada

## Objetivo
Consolidar en un único repositorio la competencia clínica, la PWA, validación, recuperación de evidencia, grafo de conocimiento y futuras integraciones multimodales sin duplicar contenido clínico.

## Fuente maestra
- `clinical/`: competencia emergency-medicine. El manifiesto autoritativo es `clinical/references/module-index.md`.
- `app/`: PWA.
- `STATE.md`: estado vivo del repositorio.
- El contenido clínico sigue siendo borrador hasta revisión humana.

## Capas
1. **Clinical core** — módulos, seguridad, calculadoras y living evidence.
2. **Deterministic engines** — cálculos reproducibles para dosis, perfusiones y fórmulas.
3. **Knowledge graph** — relaciones explícitas entre módulos, bundles y fuentes; no genera recomendaciones.
4. **RAG** — recuperación de guías y documentación autorizada con trazabilidad de fuente.
5. **Multimodal** — ECG, POCUS, radiología y otras imágenes bajo validación separada.
6. **Agents** — router, evidencia, farmacología, cálculo, imagen, seguridad y auditoría.
7. **Application layer** — PWA/API; nunca debe convertirse en fuente clínica primaria.
8. **Validation/CI** — regresiones estructurales y clínicas documentadas; no equivalen a validación clínica prospectiva.

## Principios
- No duplicar módulos ni mantener dos fuentes maestras.
- No incorporar PHI/datos identificables al grafo, RAG, logs o datasets.
- Toda recomendación de alto riesgo debe conservar fuente, fecha y estado de evidencia.
- Los cálculos críticos deben ejecutarse en código determinista, no depender del LLM.
- Modelos externos se integran primero en modo de evaluación y no se consideran clínicamente validados.
- Los cambios clínicos entran por revisión humana; la infraestructura puede automatizar detección, pruebas y trazabilidad.

## Flujo
```
caso clínico
  -> router
  -> módulos exactos
  -> evidencia/RAG
  -> calculadoras deterministas
  -> razonamiento asistido
  -> safety gate
  -> salida con incertidumbre, dosis y fuentes
```

## Carpetas nuevas
- `knowledge-graph/`: ontología y grafo metadata/evidencia.
- `rag/`: contrato del pipeline RAG.
- `models/`: registro de modelos externos y estado de validación.
- `docs/GRAPHIFY.md`: uso de Graphify sobre el repositorio.
- `.github/workflows/clinical-ci.yml`: validación automática.
