# Emergency — reglas de sesión (leer SOLO este archivo al empezar)

Idioma: español. Respuestas breves, sin introducción ni resumen final.

## Arranque mínimo
1. Leer `STATE.md` (estado vivo, ≤30 líneas). No leer CHANGELOG, VALIDATION ni updates/ salvo que la tarea lo exija.
2. No abrir bundles enteros: localizar con `grep -n "^## <id>" clinical/modules/*.md` y leer solo esa sección.
3. Índice autoritativo: `clinical/references/module-index.md`.

## Mapa
- `clinical/`: competencia, evidencia, scripts y tests.
- `app/`: PWA.
- `knowledge-graph/`: grafo determinista; nunca fuente de recomendaciones nuevas.
- `rag/`: contrato de recuperación de evidencia.
- `models/`: candidatos externos y estado de validación.
- `docs/ARCHITECTURE.md`: arquitectura maestra.
- `docs/GRAPHIFY.md`: Graphify opcional para navegación del repositorio.

## Herramientas
- Usar Graphify para navegación/relaciones técnicas cuando esté instalado; no tratar relaciones inferidas como evidencia clínica.
- Sin subagentes ni listas de tareas salvo petición expresa o trabajo clínico de alto riesgo.
- Web solo para dosis/guías cambiantes; nunca para lo que ya está en el repo.
- No leer: `node_modules/`, `dist/`, `package-lock.json`, `*.zip`, `screenshots/`, `SOURCE_SHA256.json`, `evidence-registry.json` completo (usar grep/jq).

## Seguridad clínica
Dosis, unidades, diluyente, concentración, aritmética, mL/h, máximos, contraindicaciones y avisos se mantienen íntegros. Contenido = borrador hasta revisión humana. Protocolo local y DGS/INFARMED prevalecen. No incorporar PHI a RAG, grafos, logs o datasets.

## Verificar antes de cerrar
- Clínico: `cd clinical && python3 scripts/validate_modules.py && python3 scripts/audit_evidence_coverage.py | tail -3 && python3 -m unittest discover -s tests -q`
- Grafo: `python3 clinical/scripts/build_project_graph.py --output /tmp/project-graph.json`
- App: `cd app && npm test && npm run build`
- Al terminar: actualizar `STATE.md` y una línea en `clinical/CHANGELOG.md`.

## Optimización Automática de Tokens (RTK + Graphify + Ponytail)

1. **Exploración con Graphify:** Antes de buscar o leer múltiples archivos en un proyecto, verifica si existe `graphify-out/GRAPH_REPORT.md`. Si existe, léelo primero. Si estás en un repositorio de código y `graphify-out/` no existe todavía, ejecuta `/graphify .` automáticamente al inicio para generar el mapa.
2. **Minimalismo con Ponytail:** Aplica siempre por defecto las reglas de `/ponytail` en modo `lite` (escribe el cambio completo más pequeño posible, reutiliza código existente y evita explicaciones largas). Nunca pases a modo `ultra` ni elimines tests o validaciones salvo petición explícita.
3. **Comandos con RTK:** Usa siempre comandos estándar de terminal para que los hooks de RTK compriman la salida automáticamente.
