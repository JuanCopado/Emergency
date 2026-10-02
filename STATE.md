# STATE — 02/10/2026

## Clínico (`clinical/`) — borrador v1.35, no instalado
- 106 IDs; 106/106 evidencia (31 green, 75 yellow, 0 red); 63 tests previos en main.
- v1.35: `vasoactive-inotrope-infusions` y `icu-sedation-analgesia-infusions`.
- Pendiente: revisión UCI/cardio/farmacia, RCM/INFARMED Portugal, concentraciones locales y perfusiones pediátricas.

## App (`app/`) — Sprint 1
- PWA React+Vite+TS, i18n en/es/pt/zh, tema claro/oscuro, offline.
- 17 fármacos adultos de perfusión; calculadora mL/h directa/inversa.
- 126 tests previos; build/lint/typecheck OK.

## Consolidación de proyecto
- Arquitectura maestra documentada en `docs/ARCHITECTURE.md`.
- Graphify preparado con `.graphifyignore` y `docs/GRAPHIFY.md`.
- Grafo determinista módulo→bundle→fuente añadido; 106/106 manifiesto/registro coinciden.
- Capas RAG y registro de modelos externas preparadas sin activar decisiones clínicas autónomas.
- GitHub Actions valida manifiesto, evidencia, tests y construcción del grafo.

## Reglas fijas
Validación médica: Juan y equipo humano. No llamar validación clínica a los tests.
