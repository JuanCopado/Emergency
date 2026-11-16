# Emergency

Proyecto internacional y ampliable de apoyo a urgencias, emergencias y cuidados agudos: conocimiento clínico, cálculos, procedimientos, imagen, documentación, formación e investigación, con validación por función y contexto.

## Entrada común

- [Alcance internacional del propietario](docs/INTERNATIONAL_SCOPE.md).
- [Estado de esta línea de trabajo](STATE.md) y [reglas para colaboradores](AGENTS.md).
- [Capacidades existentes y hoja de ruta](docs/INTERNATIONAL_ROADMAP.md).
- [Coordinación y difusión de la directriz](docs/COORDINATION_INTERNATIONAL_2026-11-16.md).

El núcleo compartido se separa de la jurisdicción, la organización y los recursos disponibles. Portugal, Azores y Hospital da Horta son perfiles posibles de aplicación; el idioma no selecciona país ni hospital. Las funciones generales pueden desarrollarse sin un centro elegido; cada función clínica conserva sus requisitos y límites.

## Componentes

- `clinical/`: fuente canónica de módulos, farmacología, calculadoras, procedimientos, evidencia y evaluación de imagen.
- `app/`: PWA React/Vite; catálogos derivados y herramientas de consulta/documentación. Los recursos de interfaz incluyen español, inglés, portugués y chino simplificado; la cobertura clínica traducida se evalúa por separado.
- [Arquitectura](docs/ARCHITECTURE.md), [procedencia](knowledge-graph/README.md) y [RAG](rag/README.md): sus documentos distinguen herramientas existentes de contratos de diseño o ampliaciones pendientes.

El proyecto mantiene `CLINICALLY_PENDING`. Una revisión técnica o aceptación de un centro no establece aprobación asistencial internacional. Las tareas nuevas deben registrar qué está implementado, qué se ha comprobado y qué falta para el escenario de uso.
