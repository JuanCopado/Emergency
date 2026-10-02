Continúa la Competencia Médica `emergency-medicine` desde el estado real de la rama `v1.36-consolidation` del repositorio `JuanCopado/Emergency`.

Lee primero:
1. `clinical/AGENTS.md`
2. `clinical/CURRENT_STATE.md`
3. `clinical/MODULES.md`
4. `clinical/CONSOLIDATION_V1.36.md`
5. `clinical/SKILL.md`
6. `clinical/references/module-index.md`
7. `clinical/references/evidence-registry.json`
8. `clinical/VALIDATION.md`
9. las actualizaciones recientes de `clinical/updates/`.

Estado comprobado al 02/10/2026:
- rama de trabajo: `v1.36-consolidation`;
- línea clínica vigente: v1.35 hasta revisión humana/promoción;
- v1.36: **127 módulos / 127 evidencia / 29 green / 98 yellow / 0 red / 151 tests PASS**;
- no volver a cifras históricas 85, 93, 98, 104, 106 o 107 como total actual;
- QA automático/regresiones no equivalen a validación clínica prospectiva.

Trabajo consolidado:
- QA transversal y release gates fail-closed;
- revisión de módulos high-risk adultos;
- reconciliación TCE con protocolo Hospital da Horta + NICE/BTF, manteniendo discrepancias explícitas;
- pediatría ampliada: PCR/arritmias/shock/status, medicación por peso, perfusiones, bolos, fluidoterapia IV, asma, RSI, electrolitos, transfusión/hemorragia masiva, sedación procedimental, antibióticos por síndrome y medicación de alta;
- pediatría usa guías internacionales/SmPC; **no requiere protocolo local de Horta como gate**;
- registro antibiótico pediátrico canónico: `qa/pediatric-antibiotics.json`;
- Fase 5 imagen iniciada: política ciega, generador/validador de manifiestos, métricas fail-closed y fuentes candidatas documentadas; todavía no existe dataset real suficiente para claims de precisión.

Reglas:
- no duplicar módulos;
- comprobar índice/registro antes de crear un ID;
- para perfusiones: dosis, concentración, cálculo y mL/h;
- no inventar stock, concentraciones ni protocolos locales;
- si guías discrepan, conservar la discrepancia;
- high-risk no pasa yellow->green solo por tests;
- validación médica corresponde a Juan/equipo humano;
- para imagen no afirmar sensibilidad/especificidad hasta banco ciego real, autorizado/desidentificado y con referencia independiente.

Próximo bloque recomendado:
1. cerrar deuda documental v1.36 y revisar yellow de alto riesgo;
2. completar/revisar pediatría pendiente sin duplicar rutas;
3. Fase 5: preparar importación de datasets autorizados por modalidad tras revisar licencia/DUA; no subir datos clínicos identificables al repo;
4. mantener `main` sin cambios clínicos high-risk hasta revisión humana.

Al terminar cada bloque: actualizar CURRENT_STATE/VALIDATION/CONSOLIDATION, ejecutar Clinical QA y comprobar el workflow final en GitHub.
