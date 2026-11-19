# Emergency

Proyecto internacional y ampliable de apoyo a urgencias, emergencias y cuidados agudos: conocimiento clínico, cálculos, procedimientos, imagen, documentación, formación e investigación, con validación por función y contexto.

## Entrada común

- [Alcance internacional del propietario](docs/INTERNATIONAL_SCOPE.md).
- [Política de guías internacionales y excepciones justificadas](clinical/references/international-guideline-policy.md).
- [Estado de esta línea de trabajo](STATE.md) y [reglas para colaboradores](AGENTS.md).
- [Capacidades existentes y hoja de ruta](docs/INTERNATIONAL_ROADMAP.md).
- [Coordinación y difusión de la directriz](docs/COORDINATION_INTERNATIONAL_2026-11-16.md).

El núcleo clínico global funciona sin seleccionar hospital y mantiene un mismo módulo/algoritmo canónico. Selecciona guías de amplio reconocimiento internacional por calidad, vigencia, consenso y población/indicación. Contrasta fuentes primarias y conserva pauta íntegra, procedencia, revisión y estado real; incorpora únicamente diferencias materiales justificadas de clínica, seguridad, regulación/producto o recursos. El catálogo territorial no fragmenta el producto en protocolos completos por país ni universaliza NICE/AHA. Portugal, Azores y Horta son contextos posibles; idioma y biografía no seleccionan país ni hospital.

## Componentes

- `clinical/`: fuente canónica de módulos, farmacología, calculadoras, procedimientos, evidencia y evaluación de imagen.
- `app/`: PWA React/Vite; catálogos derivados y herramientas de consulta/documentación. Los recursos de interfaz incluyen español, inglés, portugués y chino simplificado; la cobertura clínica traducida se evalúa por separado.
- [Arquitectura](docs/ARCHITECTURE.md), [procedencia](knowledge-graph/README.md) y [RAG](rag/README.md): sus documentos distinguen herramientas existentes de contratos de diseño o ampliaciones pendientes.

El proyecto mantiene `CLINICALLY_PENDING`. Una revisión técnica o aceptación de un centro no establece aprobación asistencial internacional. Las tareas nuevas deben registrar qué está implementado, qué se ha comprobado y qué falta para el escenario de uso.

## Revisión local T05 y T06

Gasometría y laboratorio T06 se abren desde Inicio. Preparación, arranque y capacidades Windows/Linux: [docs/LOCAL_REVIEW.md](docs/LOCAL_REVIEW.md). Se mantiene CLINICALLY_PENDING y uso de datos sintéticos.
