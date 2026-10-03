# HANDOFF_PROMPT — v1.36 consolidation

Fecha de corte: 03/10/2026 — estado canónico.

Pega este bloque en un chat nuevo:

> Continúa **Emergency / Competencia Médica** desde GitHub `JuanCopado/Emergency`, rama **`v1.36-consolidation`**. No modificar ni fusionar `main`. Antes de tocar código lee `clinical/AGENTS.md`, `clinical/SKILL.md`, `clinical/CURRENT_STATE.md`, `clinical/CONSOLIDATION_V1.36.md`, `clinical/VALIDATION.md`, `clinical/MODULES.md`, `clinical/qa/PHASE5_IMAGE_CLOSURE.md` y `clinical/references/evidence-registry.json`. Comprueba el repo y GitHub Actions; no uses cifras históricas como estado actual.
>
> **Estado clínico:** 127 módulos / 127 registros de evidencia / 29 green / 98 yellow / 0 red. v1.35 sigue siendo la línea clínica autoritativa; v1.36 es consolidación. Fase 4 pediátrica está técnicamente desarrollada pero high-risk permanece yellow hasta revisión humana pediatría/farmacia.
>
> **QA canónico:** **175/175 tests PASS**, `automated_status: PASS` (Clinical QA #338).
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
> **Pendientes reales restantes:** revisión humana pediatría/farmacia y de otros high-risk yellow; acceso/DUA/credenciales de datasets restringidos; validación clínica externa/prospectiva de imagen; Portugal/Azores formulary/protocol review. No son deuda técnica automatizable.

## Archivos de continuidad
- `clinical/CURRENT_STATE.md`
- `clinical/CONSOLIDATION_V1.36.md`
- `clinical/VALIDATION.md`
- `clinical/HANDOFF_PROMPT.md`
- `clinical/qa/PHASE5_IMAGE_CLOSURE.md`
- `clinical/qa/image-dataset-source-registry.json`
