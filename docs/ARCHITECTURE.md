# Emergency — arquitectura consolidada

## Objetivo
Desarrollar una plataforma internacional y ampliable para urgencias y cuidados agudos, conforme a [INTERNATIONAL_SCOPE.md](INTERNATIONAL_SCOPE.md). Consolidar competencia clínica, PWA, validación, evidencia, grafo y ampliaciones multimodales sin duplicar contenido ni fijarlo a una organización.

## Contexto independiente del núcleo

Separar cuatro capas: núcleo compartido; jurisdicción; organización/recursos; y caso/preferencias. El idioma no selecciona país, guía ni hospital. Los perfiles son datos explícitos y versionados; nunca pueden sobrescribir silenciosamente una contraindicación o promover estados de validación. La fase 2 de INT-01 ya incorpora un selector opcional de contexto en Ajustes, con esquema y resolución comprobados en las [pruebas de contexto](../app/src/context/reference-context.test.ts) y de [interfaz](../app/src/test/reference-context.test.tsx). Describe recursos declarados; no selecciona automáticamente una pauta ni acredita conformidad regional.

Una configuración regional pendiente limita su función dependiente; el núcleo de referencia, docencia y desarrollo puede continuar con contexto desconocido y límites explícitos. Preservar evidencia local sin extenderla a todos los destinos. Consultar [el marco clínico internacional](../clinical/references/international-context.md) y [la hoja de ruta](INTERNATIONAL_ROADMAP.md).

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
- `.github/workflows/clinical-qa.yml`: validación automática.

## Estado histórico documentado de T01

Base v1.44: 131 módulos canónicos. La normalización y el grafo son herramientas técnicas de procedencia; RAG, agentes y capas multimodales describen arquitectura o componentes sujetos a sus validaciones independientes. T01 no implementa retrieval semántico ni una API RAG. Los cuatro P1 farmacológicos permanecen abiertos y los 19 contratos agudos bloqueados permanecen bloqueados. CLINICALLY_PENDING.

Ese párrafo conserva el corte histórico de T01. Para el estado vigente, aplicar [AGENTS.md](../AGENTS.md), [STATE.md](../STATE.md) y la [aceptación del 16/11/2026](../clinical/references/acute-contract-owner-acceptance-2026-11-16.json): los 19 bloqueos permanentes de ese alcance se sustituyeron por los contratos revisados y sus controles específicos. No restaurar los bloqueos históricos ni inferir el cierre de los restantes P1.

La auditoría comprueba ventanas de revisión y puede bloquear CI aunque el código sea correcto. No renovar fechas ni promover GREEN por resultados automatizados.
