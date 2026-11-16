# Emergency — instrucciones comunes de colaboración

## Directriz de ejecución vigente — contratos revisados, 16/11/2026

El propietario médico ha confirmado que el trabajo ya está validado por él y ha ordenado incorporarlo y desbloquearlo. Aplicar `clinical/qa/REVIEWED_ACUTE_CONTRACT_RELEASE_2026-11-16.md` y la aceptación registrada en `clinical/references/acute-contract-owner-acceptance-2026-11-16.json`. Esta instrucción posterior sustituye la conservación histórica de los 19 bloqueos de GMA-P2-004 dentro de ese alcance. No volver a pedir la aceptación ya concedida ni restablecer bloqueos administrativos por leer un corte anterior. Mantener los controles reales de cada caso/producto y distinguir cálculo de apoyo de decisión sin dosis.

Rama de entrega autorizada: `codex/v144-reviewed-contracts-enable-20261116`, base verificada `062d890b4fc92369b83c87664bb4bb0205ccb33f` de la rama internacional. Se permite implementar, comprobar y publicar esta entrega sin modificar ramas protegidas. GMA-P2-001 incluye corrección del motor numérico y regresiones. Esta instrucción no cierra otros P1/P2 ni certifica un despliegue o ensayo prospectivo.

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
