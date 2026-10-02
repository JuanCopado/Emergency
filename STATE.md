# STATE — 02/10/2026

## Clínico (`clinical/`) — línea clínica v1.35 + consolidación v1.36 en rama separada
- Línea clínica v1.35: 106 IDs; 106/106 evidencia (31 green, 75 yellow, 0 red); 63/63 tests.
- Rama v1.36-consolidation: 110 IDs; 110/110 evidencia (31 green, 79 yellow, 0 red); **94 tests PASS** tras la ampliación pediátrica.
- v1.35: `vasoactive-inotrope-infusions` (cardiovascular.md) y `icu-sedation-analgesia-infusions` (procedures-pharmacology.md). Nota: `updates/icu-infusions-review-2026-09-29.md`.
- Pendiente v1.35: revisión UCI/cardio/farmacia; noradrenalina base vs tartrato en producto PT; diluyentes y concentraciones estándar locales; política vasopresor periférico; disponibilidad angiotensina II/levosimendán en Azores; SSC 2026 y ESC 2023 texto completo no accesibles.
- Consolidación v1.36 avanzada: QA transversal, revisión de high-risk, localización Portugal/Azores y Fase 4 pediátrica en curso. `pediatric-iv-fluid-therapy` cubre resucitación, mantenimiento, déficit y tiempos por síndrome. `pediatric-emergency-medications` añade cálculo seguro por peso/bolos/fluidos/mL-h con concentraciones y escalas verificadas por fuentes pediátricas/SmPC; no depende de protocolo local de Horta. No promover cambios clínicos sin revisión humana.

## App (`app/`) — Sprint 1
- PWA React+Vite+TS, i18n en (maestro)/es (defecto)/pt/zh, tema claro/oscuro, offline.
- 17 fármacos adultos de perfusión desde v1.35; calculadora mL/h directa/inversa con aritmética y tabla de titulación.
- 126 tests; build/lint/typecheck OK. Nombre provisional "Emergency" (`src/config/brand.ts`).
- Sprint 2: perfusiones pediátricas, bolos/ISR, catálogo completo de módulos, pipeline de contenido con versiones, flujo de revisión clínica.

## Reglas fijas
Validación médica: Juan y equipo humano. No llamar validación clínica a los tests.

- Pediatría v1.36: rutas específicas añadidas para fluidoterapia IV, asma aguda y RSI/intubación.
