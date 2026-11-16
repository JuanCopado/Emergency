# Emergency — alcance internacional del proyecto

**Directriz vigente del propietario, Juan Copado: 16/11/2026.** Identificador: `INT-01`. Esta decisión se aplica al diseño del producto, a la coordinación y a todos los colaboradores y agentes del proyecto.

## Propósito

Emergency es un proyecto internacional de apoyo a la atención urgente, las emergencias y los cuidados agudos. Su desarrollo abarca razonamiento clínico, farmacología y cálculo, procedimientos, imagen y POCUS, documentación, formación, investigación y coordinación asistencial. Debe poder crecer mediante componentes reutilizables y evaluables en diferentes países, organizaciones, poblaciones y entornos.

El producto se diseña para profesionales y equipos sanitarios; cada función debe definir sus usuarios, ámbito y requisitos de uso. Hospital da Horta, Azores y Portugal son experiencias y posibles perfiles de aplicación. Ninguno determina el alcance universal del producto ni es requisito de partida para contribuir al núcleo común.

El alcance amplio es una dirección de producto. Las capacidades existentes, los prototipos y las ampliaciones propuestas se identifican por separado. La hoja de ruta está en [INTERNATIONAL_ROADMAP.md](INTERNATIONAL_ROADMAP.md).

## Arquitectura de alcance

| Capa | Contenido | Regla de separación |
|---|---|---|
| Núcleo común | Módulos, algoritmos, principios activos, cálculos deterministas, procedimientos, evidencia y contratos reutilizables. | Un ID canónico por capacidad y procedencia centralizada; conservar múltiples referencias y sus discrepancias, sin copiar el núcleo para cada hospital. |
| Jurisdicción | País/región, referencias regulatorias y clínicas aplicables, información de producto y diferencias explícitas entre guías. | Activación por contexto declarado; ninguna autoridad nacional se considera universal. |
| Organización y entorno | Formulario, preparaciones verificadas, equipos, circuitos, derivación, competencias y recursos del servicio. | Información atribuida y fechada; no inferir existencias ni capacidades de un centro. |
| Caso y preferencias | Datos del caso, población, escenario, idioma, accesibilidad y preferencias de presentación. | El idioma, el perfil del propietario o un ejemplo histórico no seleccionan país, hospital ni régimen clínico. |

Cuando no se conoce país u organización, mantenerlos como desconocidos y continuar las funciones de referencia, formación o desarrollo que no dependan de ese dato. Solicitar o exigir contexto únicamente donde afecte a la decisión, preparación, cálculo, circuito o afirmación de disponibilidad concreta. La falta de un protocolo de Horta no bloquea por sí misma una capacidad internacional.

No existe un «protocolo mundial» que permita combinar recomendaciones discordantes sin evaluación. Cada recomendación conserva fuente, versión, fecha, población, indicación y límites. Las discrepancias se muestran y se resuelven de forma explícita en el contexto aplicable. El marco clínico operativo se desarrolla en [international-context.md](../clinical/references/international-context.md).

## Amplitud funcional

La planificación debe contemplar atención hospitalaria, prehospitalaria, transporte, servicios rurales o remotos, entornos con recursos limitados, pediatría, adultos, embarazo y otras poblaciones especiales. Las funciones se ampliarán con criterios de aceptación por escenario; no se da por disponible un recurso ni validada una población por añadirla al alcance.

La arquitectura debe permitir interfaces y contenidos en varios idiomas, módulos educativos y simulación, conectores de interoperabilidad, comparación de evidencia, trabajo en equipo, evaluación multicentro y adaptadores de IA de diferentes proveedores. Los contratos clínicos y la propiedad de los datos no deben depender de una marca de modelo. Las funciones futuras se implementarán y validarán mediante tareas concretas, no mediante declaraciones de disponibilidad.

## Seguridad y estados de validación

La ampliación internacional mantiene la verificación de dosis, unidades, concentración, diluyente, compatibilidad, estabilidad, límites de edad/peso y función orgánica cuando correspondan. Un perfil nunca elimina una contraindicación o desbloquea una pauta sin evidencia y revisión aplicables.

Distinguir siempre:

1. Verificación técnica del código y los contratos.
2. Revisión clínica de una referencia o función.
3. Aceptación operativa de un perfil, organización o entorno.
4. Evaluación prospectiva del rendimiento y seguridad en una población concreta.

Una aceptación local conserva su valor y procedencia, pero no demuestra validación internacional. Una dependencia local pendiente limita la afirmación o función que depende de ella; no transforma todas las capacidades del proyecto en bloqueadas. `CLINICALLY_PENDING`, los 19 contratos agudos bloqueados y los estados existentes se mantienen hasta sus procesos de resolución. Esta directriz no cambia dosis ni constituye aprobación asistencial.

## Instrucción común a colaboradores

GPT/coordinación, Codex, Claude, Gemini, revisores clínicos, farmacia, imagen, ingeniería y futuras contribuciones deben:

- Leer esta directriz antes de definir o ampliar una tarea.
- Identificar si la entrega afecta al núcleo, a una jurisdicción, a una organización o a un escenario.
- Separar la configuración del idioma y la elección de guía/perfil clínico.
- Conservar los ejemplos locales y la evidencia histórica con su ámbito, sin convertirlos en valores universales.
- Registrar base, cambios, pruebas ejecutadas, dependencias, estado real y criterio de aceptación.
- Proponer componentes compartidos y ampliaciones concretas antes de crear variantes duplicadas por centro.
- Distinguir una directriz publicada de su recepción, lectura e integración por cada colaborador.

## Vigencia y coordinación

La decisión del propietario sustituye cualquier formulación anterior que limite el proyecto global a un hospital o a Portugal/Azores. Se conservan las restricciones clínicas justificadas, las protecciones de ramas, la procedencia de las fuentes y la autorización específica de transferencias de datos.

El registro de esta entrega y su difusión está en [COORDINATION_INTERNATIONAL_2026-11-16.md](COORDINATION_INTERNATIONAL_2026-11-16.md). El estado técnico se obtiene de [STATE.md](../STATE.md), del registro de evidencia y de la rama/commit realmente inspeccionados. Los cortes históricos no son instrucciones para restaurar una versión anterior.
