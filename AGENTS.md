# Emergency — instrucciones comunes de colaboración

## Alcance vigente

Emergency es un proyecto internacional y ampliable de apoyo clínico, formación, investigación y coordinación en urgencias y cuidados agudos. Aplicar [docs/INTERNATIONAL_SCOPE.md](docs/INTERNATIONAL_SCOPE.md), directriz del propietario del 16/11/2026, a todas las tareas.

Mantener un núcleo clínico global coherente y un mismo módulo/algoritmo canónico. El núcleo funciona sin seleccionar país ni hospital. No inferirlos del idioma, de la biografía del propietario o de un ejemplo. Portugal/Azores/Horta son contextos posibles; preservar sus decisiones con procedencia y alcance propios.

Aplicar [la política de guías internacionales](clinical/references/international-guideline-policy.md): seleccionar guías de amplio reconocimiento internacional por calidad, vigencia, consenso y población/indicación. Contrastar fuentes primarias e incorporar únicamente diferencias materialmente justificadas de clínica, seguridad, regulación/producto o recursos, manteniendo pauta íntegra, procedencia, revisión clínica y estado real. El catálogo territorial permite contrastar excepciones; no impone prioridades geográficas ni protocolos completos por país. No universalizar NICE, AHA ni otra fuente por su origen.

## Entrada y trabajo

1. Leer esta directriz, `docs/INTERNATIONAL_SCOPE.md` y `STATE.md`.
2. Verificar repositorio, rama, commit y cambios existentes antes de editar. Usar el dispatch de la tarea; nunca restaurar una rama porque un handoff histórico la mencione.
3. Leer `CODEX.md`, `CLAUDE.md` o `GEMINI.md` según el colaborador, y las instrucciones del área afectada (`clinical/AGENTS.md` para contenido clínico).
4. Usar `docs/INTERNATIONAL_ROADMAP.md` para ampliar funcionalidades mediante entregas con alcance, dependencias y aceptación explícitos.
5. Consultar fuentes vigentes cuando la tarea cambie recomendaciones clínicas. La revisión del alcance no autoriza inventar evidencia ni cambiar aritmética para pasar QA.

No modificar `main`, `v1.42-rc1` ni la línea cerrada v1.43. Conservar cambios ajenos y usar ramas de tarea verificadas. No declarar integración por crear o publicar una rama.

## Calidad y comunicación

No duplicar módulos, procedimientos o fórmulas. Mantener dosis, preparaciones y contraindicaciones con su fuente y contexto. No promover estados clínicos automáticamente. Mantener `CLINICALLY_PENDING` cuando corresponda; QA técnico no equivale a validación clínica.

Al cerrar una entrega, actualizar el estado y la trazabilidad que realmente cambian, comprobar lo afectado y declarar límites. No renovar fechas de revisión de evidencia por editar documentación de producto. No ampliar pruebas sin un riesgo concreto pendiente.

Toda entrega identifica alcance internacional/perfil, base de trabajo, funciones existentes frente a previstas y pruebas observadas. La recepción de una directriz por otros colaboradores se registra solo cuando se comunica o confirma efectivamente; no afirmar que todos los chats o agentes externos se han actualizado.
