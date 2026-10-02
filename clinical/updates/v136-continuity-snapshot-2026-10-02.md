# SNAPSHOT DE CONTINUIDAD — v1.36 — 02/10/2026

## Estado
- Repositorio: `JuanCopado/Emergency`
- Rama: `v1.36-consolidation`
- Línea clínica vigente: v1.35
- Rama de consolidación: **127 módulos**
- Evidencia: **127/127**
- Semáforo: **29 green / 98 yellow / 0 red**
- QA: **151 tests PASS**
- Regla: tests técnicos != validación clínica.

## Bloques completados en v1.36
1. QA transversal con gates fail-closed y CI.
2. Revisión de high-risk adulto: reanimación/arritmias, shock, vasoactivos, sedación UCI, TEP, reversión anticoagulación, antibióticos, status, sodio, obstetricia, toxicología, anafilaxia, Ca/Mg, hemorragia mayor, respiratorio y seguridad de medicación.
3. TCE: protocolo actualizado del Hospital da Horta integrado como capa local y comparado con NICE/BTF; discrepancias conservadas; módulo yellow.
4. Pediatría:
   - PCR/arritmias/shock/status;
   - `pediatric-emergency-medications`;
   - perfusiones y tablas mL/h fuente-verificadas;
   - bolos y cálculo dosis/volumen;
   - `pediatric-iv-fluid-therapy`;
   - `pediatric-acute-asthma`;
   - `pediatric-airway-rsi`;
   - `pediatric-electrolyte-emergencies`;
   - `pediatric-blood-transfusion-major-hemorrhage`;
   - `pediatric-procedural-sedation`;
   - antibióticos por síndrome con registro canónico;
   - medicación de domicilio/alta vinculada a síndrome.
5. Imagen:
   - política de validación;
   - manifiesto ciego v1.1;
   - generador y validador fail-closed;
   - TP/FP/TN/FN, cobertura, abstención/no-diagnóstico e IC Wilson;
   - fuentes candidatas PTB-XL, RSNA ICH, CheXpert/MIMIC-CXR y EchoNet;
   - sin dataset real suficiente: no claims de precisión.

## Reglas de continuidad
- No crear módulos sin comprobar primero el índice.
- No reutilizar cifras históricas como estado actual.
- Pediatría: guías internacionales/SmPC; Horta local no es requisito general.
- Adulto Portugal/Azores: DGS/INFARMED/local cuando la afirmación dependa de producto, stock o protocolo.
- No inventar concentraciones, disponibilidad o compatibilidad.
- Conservar discrepancias entre fuentes.
- High-risk permanece yellow hasta revisión humana.
- Imagen: casos docentes/regresión no cuentan como validación diagnóstica.

## Siguiente trabajo
- Prioridad 1: auditoría de coherencia final de v1.36 y deuda documental.
- Prioridad 2: revisar los yellow high-risk restantes y decidir cuáles están listos para revisión humana.
- Prioridad 3: preparar Fase 5 para datasets reales únicamente tras licencia/DUA, autorización, desidentificación y referencia independiente.
- No fusionar v1.36 a main por pasar QA.
