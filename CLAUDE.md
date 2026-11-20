# Emergency — reglas de sesión

La validación clínica del proyecto corresponde al Dr. Juan Copado Ceballos. Preparar la evidencia y presentar una pregunta SÍ/NO por decisión según `AGENTS.md`. Farmacia es consultiva.

Idioma: español. Respuestas breves, sin introducción ni resumen final.

## Arranque mínimo
1. Leer `AGENTS.md`, `docs/INTERNATIONAL_SCOPE.md` y `STATE.md` (estado vivo, ≤30 líneas). Emergency mantiene un núcleo clínico global coherente, utilizable sin hospital seleccionado. No inferir país ni hospital del idioma o la biografía. Leer CHANGELOG, VALIDATION o updates/ solo cuando la tarea lo requiera.
2. No abrir bundles enteros: localizar con `grep -n "^## <id>" clinical/modules/*.md` y leer solo esa sección (offset/limit).
3. Índice de IDs: `grep -oE '^## [a-z0-9-]+' clinical/modules/*.md`.

## Mapa
- `clinical/` competencia emergency-medicine (módulos .md, `references/`, `scripts/`, `tests/`).
- `app/` PWA React+Vite+TS; datos en `app/src/data/drugs.json`, motor en `app/src/lib/infusion.ts`, textos en `app/src/i18n/locales/`.

## Herramientas
- Sin subagentes ni listas de tareas salvo petición expresa o trabajo clínico de alto riesgo.
- Web solo para dosis/guías cambiantes; nunca para lo que ya está en el repo.
- Editar con Edit; nunca reescribir archivos completos. Mostrar solo fragmentos cambiados.
- No leer: `node_modules/`, `dist/`, `package-lock.json`, `*.zip`, `screenshots/`, `SOURCE_SHA256.json`, `evidence-registry.json` completo (usar grep/jq).

## Arquitectura y procedencia
- `docs/ARCHITECTURE.md`: límites entre contenido canónico, app, grafo y futuro RAG.
- `clinical/references/evidence-registry.json` y `module-index.md` siguen siendo canónicos.
- Regenerar metadatos con `python3 clinical/scripts/normalize_evidence_sources.py`; comprobar con `--check`.
- El catálogo derivado y el grafo no pueden promover evidencia ni modificar decisiones clínicas.
- RAG y modelos externos son contratos/candidatos; no declararlos implementados o validados.

## Seguridad clínica (no se recorta nunca)
Aplicar `clinical/references/international-guideline-policy.md`: guías internacionales reconocidas seleccionadas por calidad, vigencia, consenso y población/indicación; mismo módulo canónico. Contrastar fuentes primarias y aplicar solo excepciones materiales justificadas de clínica, seguridad, regulación/producto o recursos, con pauta íntegra, procedencia, revisión y estado real. El catálogo territorial no genera protocolos completos por país ni prioridades automáticas; no universalizar NICE/AHA.

Dosis, unidades, diluyente, concentración, aritmética, mL/h, máximos, contraindicaciones y avisos se mantienen íntegros. Mantener el estado de revisión de cada componente y CLINICALLY_PENDING global. Aplicar la información de producto y el protocolo verificados para el contexto seleccionado, conservando discrepancias y contraindicaciones; DGS/INFARMED corresponden al perfil portugués. Una aceptación local no certifica uso internacional. Leer `clinical/references/international-context.md` cuando la tarea dependa de jurisdicción o recursos.

## Verificar antes de cerrar (solo lo afectado)
- Clínico: `cd clinical && python3 scripts/validate_modules.py && python3 scripts/audit_evidence_coverage.py | tail -3 && python3 -m unittest discover -s tests -q`
- App: `cd app && npm test && npm run build`
- Al terminar: actualizar `STATE.md` (sustituir, no añadir histórico) y una línea en `clinical/CHANGELOG.md`.
