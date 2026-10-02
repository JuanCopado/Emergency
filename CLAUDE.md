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
