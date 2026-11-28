# Emergency — instrucciones comunes de colaboración

## Decisión clínica del propietario · 20/11/2026

La decisión clínica final del proyecto corresponde exclusivamente al Dr. Juan Copado Ceballos. Investiga a fondo cada propuesta antes de presentarla. Entrega el cambio concreto y su alcance, fuentes primarias vigentes con versión y localizador, discrepancias, incertidumbre e impacto. Formula una pregunta que Juan pueda responder SÍ o NO. Farmacia puede aportar información técnica sobre el producto cuando sea pertinente. Su firma no es requisito de validación del proyecto. Solo una respuesta explícita de Juan acepta el alcance presentado. Si falta evidencia sustantiva, continúa investigando o documenta el límite antes de pedir decisión.

Registrar ID, versión, alcance, respuesta y fecha. Un NO mantiene la propuesta sin aprobar. Conservar las aceptaciones previas en su alcance. Las comprobaciones del producto, la seguridad, la privacidad, los procedimientos locales y la QA siguen aplicándose según el caso. Plantilla común: `clinical/qa/HUMAN_REVIEW_TEMPLATE.md`.

## Directriz de ejecución vigente — contratos revisados, 16/11/2026

El propietario médico ha confirmado que el trabajo ya está validado por él y ha ordenado incorporarlo y desbloquearlo. Aplicar `clinical/qa/REVIEWED_ACUTE_CONTRACT_RELEASE_2026-11-16.md` y la aceptación registrada en `clinical/references/acute-contract-owner-acceptance-2026-11-16.json`. Esta instrucción posterior sustituye la conservación histórica de los 19 bloqueos de GMA-P2-004 dentro de ese alcance. No volver a pedir la aceptación ya concedida ni restablecer bloqueos administrativos por leer un corte anterior. Mantener los controles reales de cada caso/producto y distinguir cálculo de apoyo de decisión sin dosis.

Rama de entrega autorizada: `codex/v144-reviewed-contracts-enable-20261116`, base verificada `062d890b4fc92369b83c87664bb4bb0205ccb33f` de la rama internacional. Se permite implementar, comprobar y publicar esta entrega sin modificar ramas protegidas. GMA-P2-001 incluye corrección del motor numérico y regresiones. Esta instrucción no cierra otros P1/P2 ni certifica un despliegue o ensayo prospectivo.

## Alcance vigente

**Directriz del propietario 27/11/2026 — uso individual e IMPLEMENTACIÓN.** Priorizar utilidad, fiabilidad, agilidad y facilidad de uso del emergencista. Mantener núcleo internacional y diferencias nacionales materialmente justificadas. Integración hospitalaria, investigación multicéntrica y perfiles institucionales no bloquean capacidades individuales que no dependen de ellos; conservar requisitos clínicos, regulatorios y de privacidad que sí apliquen. Consultar el plan vivo [IMPLEMENTACIÓN](docs/IMPLEMENTACION.md) y [ORQUESTACIÓN](docs/implementacion/ORQUESTACION.json). Preparar infraestructura en paralelo al cierre clínico; no expandir indefinidamente el producto ni confundir QA con autorización clínica.

Emergency es un proyecto internacional y ampliable de apoyo clínico, formación, investigación y coordinación en urgencias y cuidados agudos. Aplicar [docs/INTERNATIONAL_SCOPE.md](docs/INTERNATIONAL_SCOPE.md), directriz del propietario del 16/11/2026, a todas las tareas.

Mantener un núcleo clínico global coherente y un mismo módulo/algoritmo canónico. El núcleo funciona sin seleccionar país ni hospital. No inferirlos del idioma, de la biografía del propietario o de un ejemplo. Portugal/Azores/Horta son contextos posibles; preservar sus decisiones con procedencia y alcance propios.

Aplicar [la política de guías internacionales](clinical/references/international-guideline-policy.md): seleccionar guías de amplio reconocimiento internacional por calidad, vigencia, consenso y población/indicación. Contrastar fuentes primarias e incorporar únicamente diferencias materialmente justificadas de clínica, seguridad, regulación/producto o recursos, manteniendo pauta íntegra, procedencia, revisión clínica y estado real. El catálogo territorial permite contrastar excepciones; no impone prioridades geográficas ni protocolos completos por país. No universalizar NICE, AHA ni otra fuente por su origen.

## Política transversal de optimización MCP — 28/11/2026

Directriz del propietario: Work, Codex, Gemini y Antigravity (y los demás colaboradores cuando corresponda) deben priorizar MCP operativos y autorizados en PR142 y en todos los pendientes actuales y futuros de Emergency **cuando aporten una ventaja efectiva**. Reutilizar evidencias y contexto canónico por versión/SHA; evitar transferencias manuales, lecturas repetidas y duplicación de contexto. No imponer llamadas redundantes, comprobaciones preventivas ni reejecuciones sólo para acreditar uso o ahorro. Si el MCP no aporta ventaja o no está disponible/autorizado, usar una alternativa permitida y registrar el límite cuando afecte al resultado.

| MCP | Uso preferente, dentro del alcance autorizado |
|---|---|
| Emergency MCP | Contexto, estado, fuentes y metadatos canónicos; snapshots vigentes y procedencia verificada. Servicio de laboratorio/desarrollo, no activación clínica. |
| GitHub MCP | Repositorio, PR, SHA, CI y evidencias; ninguna escritura o fusión fuera del permiso aplicable. |
| Chrome DevTools MCP | Navegador y pruebas funcionales sintéticas, sin eludir controles. |
| SonarQube MCP | Calidad y seguridad, con el alcance real del análisis y sus exclusiones. |
| Amass y conectores científicos autorizados | Investigación clínica focal; metadatos no equivalen a lectura íntegra ni a aprobación médica. |
| Context7 | Documentación técnica actual de las dependencias relevantes. |

Work aplica esta política antes de despachar cada encargo, sin crear nuevas tareas ni repetir las cerradas. Registrar las llamadas útiles efectivamente realizadas en los recibos existentes: ID de tarea, agente, servidor/herramienta y finalidad, hora UTC, versión/SHA o fuente cuando corresponda, resultado, evidencia y límites; no guardar secretos, PHI ni contenidos restringidos. Distinguir configurado, operativo, llamado, recibido y verificado; una instalación no acredita uso, una consulta no acredita despacho a otro agente y un acuse no acredita ejecución. No inventar métricas de ahorro: sólo informar mediciones existentes y beneficio neto demostrado.

MCP no concede permiso para transmitir datos, originales restringidos, imágenes no admitidas o claves ciegas; preservar privacidad, derechos, separación de revisores, autorizaciones, guardas y estados clínicos. No activar nuevos servicios, conectores, despliegues o capacidades clínicas por esta directriz. Mantener `CLINICALLY_PENDING` y `NO_GO_CLINICAL_RELEASE`.

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
