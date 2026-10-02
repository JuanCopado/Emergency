# HANDOFF_PROMPT — v1.36 consolidation

Fecha de corte: 02/10/2026 17:06 UTC.

Pega este bloque en un chat nuevo:

> Continúa el proyecto clínico **Emergency / Competencia Médica** desde el repositorio GitHub `JuanCopado/Emergency`, rama **`v1.36-consolidation`**. Antes de modificar nada, lee `clinical/AGENTS.md`, `clinical/SKILL.md`, `clinical/CURRENT_STATE.md`, `STATE.md`, `clinical/CONSOLIDATION_V1.36.md`, `clinical/VALIDATION.md`, `clinical/MODULES.md`, `clinical/references/module-index.md`, `clinical/references/router.md` y `clinical/references/evidence-registry.json`. Comprueba el índice real y ejecuta/revisa el Clinical QA antes de asumir cifras.
>
> **Estado verificado al corte:** rama v1.36 con **127 módulos / 127 registros de evidencia / 29 green / 98 yellow / 0 red / 151 tests PASS**. El último GitHub Actions `Clinical QA` observado en este corte está en **success**. La línea v1.35 (106 módulos) sigue siendo el baseline clínico publicado/autoritativo; v1.36 es consolidación y no debe promoverse sin revisión humana.
>
> **Reglas:** no llamar validación clínica a los tests; los módulos high-risk no pasan automáticamente de yellow a green; usar guías actuales y fuentes primarias/oficiales; en pediatría **no se exige protocolo local de Horta**: usar ERC/RCUK 2025, AHA/AAP PALS 2025, SSC pediátrica 2026, NICE, GINA 2026, HSE, PANDEM/SCCM, SmPC y otras fuentes pediátricas reconocidas según el síndrome. Si las fuentes discrepan, conservar la discrepancia. No inventar dosis, concentraciones, stock ni disponibilidad. Para perfusiones dar mL/h solo con concentración verificada.
>
> **Pediatría v1.36 ya desarrollada:** medicación de emergencia por peso; perfusiones y bolos; fluidoterapia IV; asma aguda; RSI/intubación; electrolitos; hemoderivados/hemorragia masiva; sedación procedimental; analgesia/alta; antibióticos depurados por síndrome (sepsis, meningitis, ITU/pielonefritis, celulitis, neutropenia febril y neumonía). Registros canónicos: `clinical/qa/pediatric-infusion-localization.json` y `clinical/qa/pediatric-bolus-medications.json`. Calculadores: `clinical/scripts/pediatric_emergency_calculator.py`, `pediatric_pump_table.py` y `pediatric_bolus_calculator.py`.
>
> **Imagen — Fase 5 iniciada:** existe gate ciego v1.1 con hashes paciente/estudio, timestamps freeze/reveal, clases positive/negative/abstain/nondiagnostic, métricas fail-closed y generador de manifiestos por modalidad. `clinical/qa/IMAGE_DATASET_SOURCES.md` documenta candidatos PTB-XL, RSNA ICH, CheXpert/MIMIC-CXR y EchoNet. **No existe aún un banco real suficiente para afirmar sensibilidad/especificidad clínica.**
>
> **Siguiente paso recomendado:** continuar Fase 5 construyendo/importando un primer dataset real autorizado y desidentificado con referencia independiente, empezando por una modalidad con labels sólidos (ECG/PTB-XL es una opción práctica), congelar el manifest antes de revelar labels, ejecutar el pipeline ciego y registrar métricas sin claims clínicos. Alternativamente, si se prioriza pediatría, revisar los yellow high-risk y completar revisión humana/farmacéutica antes de promoción.
>
> Después de cada bloque: actualizar evidencia/estado, añadir regresiones, ejecutar `clinical/qa/qa_runner.py`/GitHub Actions y no continuar si el gate falla.

## Archivos de continuidad
- `clinical/CURRENT_STATE.md`: estado narrativo completo.
- `STATE.md`: estado resumido de repo/app.
- `clinical/CONSOLIDATION_V1.36.md`: plan y fases.
- `clinical/VALIDATION.md`: qué está y qué no está validado.
- `clinical/HANDOFF_PROMPT.md`: este handoff.
