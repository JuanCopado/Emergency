# STATE — 02/10/2026

## Clínico (`clinical/`) — borrador v1.35, no instalado
- 106 IDs; 106/106 evidencia (31 green, 75 yellow, 0 red); 73 tests clínicos verificados en CI.
- v1.35: `vasoactive-inotrope-infusions` y `icu-sedation-analgesia-infusions`.
- Pendiente: revisión UCI/cardio/farmacia, RCM/INFARMED Portugal, concentraciones locales y perfusiones pediátricas.

## App (`app/`) — Sprint 1
- PWA React+Vite+TS, i18n en/es/pt/zh, tema claro/oscuro, offline.
- 17 fármacos adultos de perfusión; calculadora mL/h directa/inversa.
- 126 tests previos; build/lint/typecheck OK. CI dedicado añadido en esta revisión.

## Consolidación y seguridad
- Arquitectura maestra: `docs/ARCHITECTURE.md`; Graphify: `docs/GRAPHIFY.md`.
- Grafo determinista módulo→bundle→fuente; 106/106 manifiesto/registro coinciden. Catálogo normalizado: 123 identidades de fuente para 106 módulos; 31 identidades compuestas restantes. Este segundo lote separa UCI/PADIS, hipertensión, fluidos pediátricos, sangrado intestinal y neurotrauma; Grafo: 239 nodos / 244 relaciones.
- Validador detecta IDs/secciones duplicadas y usa coincidencia exacta en el router.
- Living Evidence hace cumplir ventanas 30/90/180 días; un green vencido bloquea CI.
- Artefactos Graphify/Knowledge Graph/RAG y secretos locales quedan fuera de Git.
- Clinical CI y App CI protegen las dos capas principales del proyecto.

## Reglas fijas
Validación médica: Juan y equipo humano. No llamar validación clínica a los tests.
