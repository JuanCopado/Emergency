# HANDOFF_PROMPT — Emergency internacional

Directriz del propietario: 16/11/2026. Continuar desde una referencia comprobada, nunca desde una rama histórica por inercia.

> Trabaja en **Emergency como proyecto internacional y ampliable** de apoyo clínico, formación, investigación y coordinación en urgencias y cuidados agudos. Lee primero `AGENTS.md`, `docs/INTERNATIONAL_SCOPE.md` y `STATE.md`, y después las instrucciones del área afectada. Separa núcleo, jurisdicción, organización/recursos y caso; no deduzcas país u hospital del idioma ni del perfil del propietario. Portugal/Azores/Horta son contextos de aplicación y experiencia, no el alcance global.
>
> Verifica repositorio, rama, commit y modificaciones existentes. Esta entrega de alcance usa `codex/v144-international-scope-20261116`, con base inspeccionada `926649ac5b3168267839f987de77a62401b5e7da`; consulta su HEAD real al retomarla. No modificar main, v1.42-rc1 ni v1.43. No asumir que esta rama integra A/B/C/D o está instalada en el PC local.
>
> Consulta `docs/INTERNATIONAL_ROADMAP.md` para ampliaciones con responsabilidades por función, dependencias y aceptación. Identifica en cada tarea lo existente, lo candidato y lo propuesto. El selector de perfiles, los conectores asistenciales y la validación multicentro siguen siendo tareas de implementación/evaluación.
>
> Conserva evidencia, dosis, fórmulas, contraindicaciones y datos desconocidos. Consulta `clinical/references/international-context.md` para aplicar fuentes y recursos pertinentes; una falta de datos locales limita la función dependiente, no toda la plataforma. Mantén CLINICALLY_PENDING, los 19 bloqueos y los procesos de revisión. Las pruebas técnicas no equivalen a validación clínica.
>
> Comunica alcance, base, cambios, comprobaciones observadas, límites y siguiente acción. No declares lectura, aceptación o integración por otros colaboradores sin evidencia de esos hechos. Registra la recepción de la directriz en la coordinación común.

## Archivo histórico

El bloque siguiente se conserva por trazabilidad. Sus cifras, pendientes portugueses y rama v1.36 no sustituyen las instrucciones vigentes anteriores.

# Histórico — handoff v1.36 (no ejecutar como instrucción vigente)

Fecha de corte histórica: 03/10/2026. Las referencias siguientes describen ese corte, no la rama ni el alcance actuales.

Pega este bloque en un chat nuevo:

> Continúa **Emergency / Competencia Médica** desde GitHub `JuanCopado/Emergency`, rama **`v1.36-consolidation`**. No modificar ni fusionar `main`. Antes de tocar código lee `clinical/AGENTS.md`, `clinical/SKILL.md`, `clinical/CURRENT_STATE.md`, `clinical/CONSOLIDATION_V1.36.md`, `clinical/VALIDATION.md`, `clinical/MODULES.md`, `clinical/qa/PHASE5_IMAGE_CLOSURE.md` y `clinical/references/evidence-registry.json`. Comprueba el repo y GitHub Actions; no uses cifras históricas como estado actual.
>
> **Estado clínico:** 127 módulos / 127 registros de evidencia / 29 green / 98 yellow / 0 red. v1.35 sigue siendo la línea clínica autoritativa; v1.36 es consolidación. Fase 4 pediátrica está técnicamente desarrollada pero high-risk permanece yellow hasta revisión humana pediatría/farmacia.
>
> **QA canónico:** **178/178 tests PASS**, `automated_status: PASS` (Clinical QA #356).
>
> **Fase 5 imagen:** infraestructura automatizable cerrada. Política ciega v1.1, source intake, leakage gates, freeze/reveal, sharding, merge y protocolos visuales están implementados. Ver `qa/PHASE5_IMAGE_CLOSURE.md`.
>
> **ECG / PTB-XL:** NATURAL_500 v2 limpio evaluado con baseline de ingeniería AFIB derivado solo del PNG. Freeze pre-reveal commit `aa6649785c6dad3d9daa3838c902d3136774d624`. Reference 3 AFIB / 497 no-AFIB. Predicciones 46 positive / 359 negative / 93 abstain / 2 nondiagnostic. Conteos clasificados TP=3 / FP=43 / TN=359 / FN=0. Coverage 81.0%. Por política, sensibilidad/especificidad/PPV/NPV/accuracy estándar están suprimidas porque existen abstain/nondiagnostic. No presentar esto como accuracy clínica de ChatGPT.
>
> **RSNA ICH:** source/reference pipeline y DICOM render congelados: brain WW80/WL40, HU slope/intercept, IOP/IPP geometry, mixed-series/orientation fail-closed. Falta acceso/import real e interpretación ciega.
>
> **CheXpert:** expert-test majority-vote y visual protocol listos. `actual_access_verified=false`; intake real sigue bloqueado hasta completar/aceptar el acceso específico AIMI/Redivis.
>
> **MIMIC-CXR:** curated test + CXR visual protocol listos. Actual access requiere PhysioNet credentialing, CITI y DUA.
>
> **EchoNet-Dynamic:** TEST split + target `lvef_below_40_percent` + visual protocol listos; vídeo nativo o 32 frames uniformes. Actual access requiere aceptación individual del Research Use Agreement.
>
> **Reglas:** tests != validación clínica; no auto-green; no inventar dosis/concentraciones/stock; preservar discrepancias; perfusiones en mL/h solo con concentración verificada; pediatría no exige protocolo local Horta como gate.
>
> **Clinical Scores & Calculators:** 134 escalas + 45 fórmulas; 45/45 fórmulas implementadas. Las escalas permanecen fail-closed para datos crudos hasta codificación fuente-a-fuente; component_sum solo suma componentes ya puntuados explícitamente. Ver `qa/PREBRANCH_AUDIT_V1.36.md`.\n>\n> **Pendientes reales restantes:** validación/codificación fuente-a-fuente de 93 escalas CORE y luego 41 SPECIALIST; revisión humana pediatría/farmacia y otros high-risk yellow; acceso/DUA/credenciales de datasets restringidos; validación clínica externa/prospectiva de imagen; Portugal/Azores formulary/protocol review.

## Archivos de continuidad
- `clinical/CURRENT_STATE.md`
- `clinical/CONSOLIDATION_V1.36.md`
- `clinical/VALIDATION.md`
- `clinical/HANDOFF_PROMPT.md`
- `clinical/qa/PHASE5_IMAGE_CLOSURE.md`
- `clinical/qa/image-dataset-source-registry.json`
