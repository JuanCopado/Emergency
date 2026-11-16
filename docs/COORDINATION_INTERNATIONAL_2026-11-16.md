# INT-01 — coordinación del alcance internacional

Fecha: 16/11/2026. Decisión del propietario: Juan Copado solicita que todos los colaboradores conozcan el carácter internacional de Emergency, que el proyecto tenga el mayor alcance útil posible y que se corrija su presentación como una solución de un hospital concreto.

## Directriz y entrega

La definición vigente está en [INTERNATIONAL_SCOPE.md](INTERNATIONAL_SCOPE.md). Esta entrega aplica la decisión a la gobernanza, la continuidad, el contexto clínico y la presentación del producto. La hoja de ruta [INTERNATIONAL_ROADMAP.md](INTERNATIONAL_ROADMAP.md) organiza doce capacidades con roles propuestos, dependencias y aceptación.

- Repositorio: `JuanCopado/Emergency`.
- Base exacta inspeccionada: `926649ac5b3168267839f987de77a62401b5e7da`.
- Árbol base: `db23f644ae5e54c8c33416bf978122b40a0ef7e7`.
- Rama de esta entrega: `codex/v144-international-scope-20261116`.
- Relación con otras tareas: conserva el candidato de ceftriaxona; no constituye integración A/B/C/D, actualización del PC local ni merge en main/RC/v1.43.

## Modificaciones concretas

1. Directriz canónica y puntos de entrada comunes para GPT/coordinación, Codex, Claude y Gemini. Los documentos específicos remiten al mismo alcance.
2. Estado resumido vigente y handoff actualizado. Los cortes v1.36, v1.42 y T01 quedan identificados como antecedentes, sin destruir sus resultados históricos.
3. Marco de contexto internacional: núcleo, jurisdicción, organización/recursos, entorno, caso e idioma. No se presume Portugal a partir del idioma o del propietario.
4. Corrección de instrucciones generales de farmacología, toxicología y estatus pediátrico que imponían contexto portugués o Horta; la referencia de ceftriaxona también expresa la disponibilidad según el contexto seleccionado. Se conservan dosis, fuentes, comparaciones DGS y decisiones de alcance local.
5. Presentación de Home/About y descripción de marca ampliadas a las capacidades del proyecto; accesos principales traducidos mediante los recursos existentes es/en/pt/zh.
6. Avisos de alcance corregidos: la herramienta de perfusión adulta no define toda la pediatría del producto; las funciones que necesitan un servicio no se describen como universales sin servidor/offline.
7. Hoja de ruta con funciones existentes diferenciadas de ampliaciones propuestas: perfiles, evidencia por jurisdicción, farmacología, procedimientos, entornos, idiomas, imagen, interoperabilidad, educación, validación multicentro, despliegue y adaptadores de IA.

## Difusión y recepción

Canal común de esta entrega: incidencia de coordinación titulada **[INT-01] Emergency internacional: directriz común y ampliación funcional** en el repositorio. La comunicación de cierre incluye su URL y el commit realmente publicados.

| Destinatario | Acción y estado acreditable |
|---|---|
| Propietario/coordinación | Directriz recibida de la instrucción del propietario; aplicada a esta entrega. |
| Agentes activos de este trabajo | Directriz entregada y aplicada por los tres colaboradores de alcance, mapa funcional y revisión independiente; sus resultados se incorporan. |
| Vigilancia evidencia semanal | Instrucciones actualizadas y confirmadas por el servicio; horario y activación conservados. La recepción por una futura ejecución no se presupone. |
| Revisar guías de emergencias | Instrucciones actualizadas y confirmadas por el servicio; horario y activación conservados. Se exige distinguir versiones del repositorio y copias de la competencia. |
| Codex | Instrucciones del repositorio actualizadas; recepción e integración en otras sesiones pendientes de confirmación. |
| Claude | Entrada del repositorio actualizada; no se presupone lectura ni actualización de otra instalación. |
| Gemini/auditoría | Entrada común creada; no se ha transferido un paquete a una sesión externa de Gemini. |
| Equipo clínico, farmacia, imagen e ingeniería | Directriz disponible en el canal común; no se registra lectura ni asignación nominal sin respuesta. |

Publicado, comunicado, leído e integrado son estados diferentes. Un mensaje en el repositorio no acredita que todos sus colaboradores o todos los chats lo hayan leído. La publicación tampoco instala automáticamente una copia de la competencia clínica en otra herramienta.

Las dos tareas programadas mantienen su finalidad original, fuentes fiables, criterio de notificación y revisión clínica. Se añadió únicamente la directriz de alcance y procedencia; no se ejecutaron de nuevo, no se cambiaron sus horarios y no se alteró la tarea de respaldo.

### Encargo común para el siguiente colaborador

> Lee `AGENTS.md`, `docs/INTERNATIONAL_SCOPE.md` y `STATE.md`. Confirma la referencia de trabajo inspeccionada y si tu entrega afecta al núcleo, a una jurisdicción, a una organización o a un escenario. Conserva fuentes y límites clínicos; no impongas el perfil del propietario. Elige la tarea de la hoja de ruta, declara dependencias y aceptación, y registra recepción y resultados en la coordinación común. No declares implementada una capacidad que todavía sea propuesta.

## Verificación observada

Revisión independiente de alcance, contexto clínico, instrucciones, hoja de ruta y textos de interfaz: **PASS focal**. Se corrigió la expresión «una fuente canónica» para que la centralización de procedencia no se confunda con imponer una sola guía clínica.

Comprobaciones estructurales del coordinador: **PASS**.

- Los cuatro idiomas contienen el mismo conjunto normalizado de **220 claves**; no hay cadenas vacías ni discrepancias de variables de interpolación. Las nuevas claves de Home/About resuelven.
- En los dos módulos clínicos editados se conservan exactamente la secuencia de valores numéricos, IDs de sección y URLs de fuentes.
- Scripts, pruebas, catálogos y pendientes clínicos materializados permanecen idénticos a la base; también el registro completo de evidencia. No se renuevan fechas de revisión.
- El estado breve tiene 18 líneas. El frontmatter de la competencia clínica sigue siendo válido. La hoja de ruta contiene INT-01 a INT-12.
- La construcción del árbol de entrega debe preservar todos los blobs ajenos a los archivos enumerados; su comprobación remota se realiza antes de publicar la rama.

No se ejecutaron la suite global, el build de frontend ni una inspección visual de la aplicación; el cambio de interfaz es de presentación/traducción y se comprobó estructuralmente. No hay nuevos resultados de validación clínica ni de rendimiento diagnóstico. Las 28 pruebas de ceftriaxona pertenecen a la entrega anterior, no se cuentan como una nueva ejecución de INT-01.

## Estado y próxima implementación

El registro conserva **131 módulos: 117 GREEN y 14 YELLOW**, sus fechas, los **19 contratos bloqueados** y `CLINICALLY_PENDING`. Ampliar el alcance del producto no cambia estos estados.

La fase de alcance y coordinación queda implementada en esta rama. La siguiente ampliación técnica definida es el esquema, resolución y selector explícitos de perfiles, con referencia sin centro elegido y dos contextos sintéticos independientes. Todavía no hay un selector de país/organización implementado por esta entrega, interoperabilidad asistencial nueva ni validación multicentro acreditada.
