# PRE-BRANCH AUDIT — v1.36 consolidation

Fecha: 03/10/2026.
Rama auditada: `v1.36-consolidation`.

## Estado canónico
- Módulos: **128**
- Evidencia: **128/128**
- Green: **29**
- Yellow: **99**
- Red: **0**
- Clinical QA: **178/178 tests PASS**
- `automated_status: PASS`
- QA run: **#356 / 37085788461**
- `main`: no modificado
- Línea clínica vigente: **v1.35**
- v1.36: consolidación, no release clínico

## Clinical Scores & Calculators
Módulo canónico: `clinical-scores-calculators`.

Archivos centrales:
- `modules/clinical-scores-calculators.md`
- `calculators/registry.json`
- `scripts/clinical_calculator.py`

### Catálogo
- **134 escalas/reglas**
  - 93 CORE
  - 41 SPECIALIST
- **45 fórmulas**
- Total: **179 herramientas canónicas**
- IDs de escalas duplicados: 0
- IDs de fórmulas duplicados: 0
- Solapamiento escala/fórmula: 0

### Motor de fórmulas
Estado: **45/45 implementadas** en el motor determinista.

Incluye, entre otras:
- MAP / Shock Index / Modified Shock Index
- anion gap / corrected AG / delta ratio / Winter
- osmolalidad / tonicidad / sodio y calcio corregidos
- Cockcroft-Gault / CKD-EPI 2021 / Schwartz / FENa / FEUrea
- P/F / S/F / ROX / PAO2 / A-a
- compliance / driving pressure / ventilación minuto
- BSA / BMI / Devine IBW
- Holliday-Segar / 4-2-1 / déficit / Parkland
- dosis por peso / concentración final / conversiones a mL/h
- QTc Bazett / Fridericia
- CaO2 / DO2 / cardiac index / SVR
- Maddrey
- MELD-Na legado con gate explícito; no se presenta como MELD 3.0 actual.

### Motor de escalas
Estado deliberadamente fail-closed:
- 67 `component_sum`: suma determinista de **componentes ya puntuados explícitamente**.
- 67 herramientas `criteria/rule/ordinal/official_table/formula_external/formula/nomogram`: metadata/regla externa pendiente de codificación fuente-a-fuente.
- El motor central no convierte todavía hallazgos clínicos crudos a puntos NIHSS/HEART/SOFA/NEWS2/etc. sin una tabla específica validada.
- Esto evita inventar reglas o cambiar silenciosamente versiones.

### Routing
Corregido: todas las rutas de escalas pasan por `clinical-scores-calculators` con `calculator_id`, en lugar de tratar NIHSS/HEART/Wells/etc. como module IDs.

### Regresiones
- Se reconciliaron tres asserts antiguos con el contenido clínico actual de anticoagulación/toxicología.
- Se añadieron tests de cobertura 45/45 de fórmulas.
- Se añadieron tests para CKD-EPI 2021, PAO2/A-a, IBW Devine, concentración final, DO2 y MELD-Na legado.
- Se añadió gate para impedir que el motor de escalas invente puntuaciones a partir de texto/hallazgos no codificados.

## Fuentes clave revisadas antes del corte
- NIDDK: CKD-EPI 2021 race-free creatinine equation.
- Merck Manual: alveolar gas equation / A-a gradient.
- FDA/Devine historical formula reference.
- OPTN/HRSA: current MELD policy; current adult allocation uses MELD 3.0, por lo que el MELD-Na clásico se mantiene etiquetado como legado.

## Pendientes que deben pasar a la nueva rama
No son fallos del corte v1.36:
1. Codificar y validar fuente-a-fuente las **93 escalas CORE**, empezando por NIHSS, GCS, NEWS2, SOFA, HEART, GRACE, CHA2DS2, Wells/PERC/YEARS, GBS, CURB-65 y Phoenix.
2. Después extender a las 41 SPECIALIST.
3. Mantener versiones/variantes explícitas y no mezclar reglas incompatibles.
4. Revisión humana de high-risk yellow.
5. Dependencias externas de imagen/acceso/DUA ya descritas en `qa/PHASE5_IMAGE_CLOSURE.md`.

## Gate de ramificación
**PASS.**
La rama está apta para servir como base de una nueva rama de trabajo, siempre que la nueva rama no se interprete como release clínico.
