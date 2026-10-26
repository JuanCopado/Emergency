# Emergency

App clínica urgencias/UCI. Estado: `STATE.md`. Reglas de trabajo: `CLAUDE.md`.

- `clinical/`: fuente canónica clínica; 131 módulos en la base v1.44, pendientes de revisión humana.
- `app/`: PWA React/Vite; sus catálogos se generan desde las fuentes canónicas.

Contenido pendiente de validación clínica humana.

Arquitectura técnica: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).
Procedencia: [knowledge-graph/README.md](knowledge-graph/README.md).
RAG: [rag/README.md](rag/README.md), contrato de diseño; no constituye un motor de recuperación implementado.
T01 incorpora infraestructura de normalización/grafo y cobertura CI; no valida contenido clínico.
