# HANDOFF_PROMPT — v1.36 consolidation

Fecha de corte: 02/10/2026 — estado canónico actualizado.

Pega este bloque en un chat nuevo:

> Continúa **Emergency / Competencia Médica** desde GitHub `JuanCopado/Emergency`, rama **`v1.36-consolidation`**. No modificar ni fusionar `main`. Antes de tocar código lee `clinical/AGENTS.md`, `clinical/SKILL.md`, `clinical/CURRENT_STATE.md`, `clinical/CONSOLIDATION_V1.36.md`, `clinical/VALIDATION.md`, `clinical/MODULES.md`, `clinical/references/module-index.md`, `clinical/references/router.md` y `clinical/references/evidence-registry.json`. Comprueba el repo y GitHub Actions; no uses cifras históricas como estado actual.
>
> **Estado clínico:** 127 módulos / 127 registros de evidencia / 29 green / 98 yellow / 0 red. v1.35 sigue siendo la línea clínica autoritativa; v1.36 es consolidación. Fase 4 pediátrica está técnicamente desarrollada pero high-risk permanece yellow hasta revisión humana pediatría/farmacia.
>
> **QA:** último recuento completo verificado antes del último intake: **169/169 tests PASS**, `automated_status: PASS` (Clinical QA #320). Revalidar el head actual antes de asumir esta cifra si hubo commits posteriores.
>
> **Fase 5 imagen:** política ciega v1.1, freeze/reveal, métricas fail-closed, sharding por paciente y merge de predicciones completos. PTB-XL: pilot real, NATURAL_500 y full-fold construidos; se detectó que runs anteriores imprimían prevalencia agregada en logs y por eso se clasificaron como ingeniería, no benchmark final. El builder ya suprime counts pre-reveal y se disparó un **NATURAL_500 v2 limpio con nuevo salt**. No abrir ninguna referencia sellada antes de tener predicciones reales congeladas.
>
> **Sources:** RSNA ICH source-level ready con referencia obligatoria multi-reader/adjudicada; DICOM→render debe congelarse antes de evaluación. CheXpert expert-test: referencia majority 5/8 radiólogos preparada, pero intake real sigue bloqueado hasta documentar el acuerdo específico actual de descarga. MIMIC-CXR 2.1.0 source-level ready usando solo test manualmente curado 0/1; actual access requiere PhysioNet credentialing/CITI/DUA. EchoNet-Dynamic source-level ready solo para función LV A4C / `lvef_below_40_percent`; actual access requiere Research Use Agreement individual, no redistribución y no uso clínico.
>
> **Reglas:** tests != validación clínica; no auto-green; usar fuentes actuales/primarias; preservar discrepancias; no inventar dosis/concentraciones/stock; perfusiones en mL/h solo con concentración verificada; pediatría no exige protocolo local Horta como gate.
>
> **Siguiente paso:** comprobar el NATURAL_500 v2 limpio y su leakage audit; mantener sealed reference cerrada. Sin un intérprete/modelo real ejecutado sobre el banco ciego no calcular sensibilidad/especificidad. Después avanzar RSNA/CheXpert/MIMIC/EchoNet solo cuando los gates de acceso y referencia estén realmente cumplidos.

## Archivos de continuidad
- `clinical/CURRENT_STATE.md`
- `clinical/CONSOLIDATION_V1.36.md`
- `clinical/VALIDATION.md`
- `clinical/HANDOFF_PROMPT.md`
- `clinical/qa/image-dataset-source-registry.json`
