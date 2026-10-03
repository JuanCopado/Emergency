# PHASE 5 IMAGE CLOSURE — v1.36

Fecha: 03/10/2026.
Rama: `v1.36-consolidation`.

## Estado global
La infraestructura automatizable de Fase 5 queda cerrada. Esto **no** significa
validación clínica. Significa que source intake, cegamiento, preprocesado visual,
freeze/reveal, leakage control, sharding y métricas fail-closed están definidos y
cubiertos por QA.

Clinical QA canónico: **175/175 tests PASS**, `automated_status: PASS`.

## ECG — PTB-XL
Estado: **benchmark exploratorio ejecutado**.

- PTB-XL fold 10 / NATURAL_500 v2 limpio.
- Render estandarizado y leakage audit.
- Baseline de ingeniería AFIB congelado antes del reveal.
- Freeze commit: `aa6649785c6dad3d9daa3838c902d3136774d624`.
- Referencia revelada después del freeze.
- Reference composition: 3 AFIB / 497 no-AFIB.
- Predicciones: 46 positive / 359 negative / 93 abstain / 2 nondiagnostic.
- Conteos clasificados: TP=3 / FP=43 / TN=359 / FN=0.
- Cobertura: 81.0%; abstención: 18.6%; no-diagnóstico: 0.4%.
- Sensibilidad/especificidad/PPV/NPV/accuracy estándar: **suprimidas por política**
  porque existen casos abstain/nondiagnostic.
- No es accuracy clínica de ChatGPT ni validación externa/prospectiva.

## TC cerebral — RSNA ICH
Estado: **pipeline técnico completo / acceso real pendiente**.

Completado:
- términos/source-level intake;
- referencia multi-reader/adjudicada fail-closed;
- exam-level grouping;
- DICOM render v1 congelado;
- brain window WW=80 / WL=40;
- HU conversion slope/intercept;
- orden IOP/IPP geométrico;
- MONOCHROME1/2;
- rechazo de mixed-series/mixed-orientation/duplicated positions;
- BurnedInAnnotation=YES bloqueado.

Pendiente externo:
- acceso/import real de la cohorte elegible con referencia multi-reader demostrable;
- interpretación ciega y freeze antes del reveal.

## Rx tórax — CheXpert
Estado: **pipeline/reference completos / acceso específico pendiente**.

Completado:
- expert test set protocol;
- majority-vote ground truth;
- training NLP labels excluidos;
- visual-input protocol congelado;
- múltiples vistas agrupadas por estudio/paciente.

Bloqueo real:
- el flujo actual Stanford AIMI/Redivis requiere completar/aceptar los términos de
  acceso aplicables al dataset. `actual_access_verified=false`.
- No marcar `intake_ready=true` hasta completar ese paso.

## Rx tórax — MIMIC-CXR 2.1.0
Estado: **source-level pipeline completo / acceso credentialed pendiente**.

Completado:
- solo labels manualmente curados de test;
- uncertain/blank excluidos preespecificadamente;
- visual-input protocol congelado.

Bloqueo real:
- PhysioNet credentialing;
- CITI;
- DUA del proyecto;
- `actual_access_verified=false`.

## Ecocardiografía — EchoNet-Dynamic
Estado: **source-level pipeline completo / acceso individual pendiente**.

Completado:
- official TEST split;
- target `lvef_below_40_percent`;
- EF reference separada;
- visual protocol congelado;
- vídeo nativo o 32 frames uniformes a lo largo del vídeo completo;
- no selección de frames dependiente de EF.

Bloqueo real:
- aceptación individual del Research Use Agreement / acceso al dataset;
- `actual_access_verified=false`.

## Gates que continúan abiertos
1. **Clinical image validation:** un benchmark público retrospectivo no equivale a
   validación prospectiva/generalizable.
2. **Human review:** los módulos clínicos high-risk yellow no pasan a green por estos
   benchmarks.
3. **External access:** los datasets restringidos no se descargan ni redistribuyen sin
   completar sus requisitos de acceso/DUA.
4. **Portugal/Azores clinical release:** stock, formulary y protocolos locales siguen
   siendo gates separados.

## Release
- `main` no se modifica.
- v1.35 sigue siendo la línea clínica vigente.
- v1.36-consolidation sigue siendo rama de consolidación.
- Fase 5 queda **técnicamente cerrada hasta que se satisfagan dependencias externas**.
