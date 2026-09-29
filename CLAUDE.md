# Emergency — reglas de sesión (leer SOLO este archivo al empezar)

Idioma: español. Respuestas breves, sin introducción ni resumen final.

## Arranque mínimo
1. Leer `STATE.md` (estado vivo, ≤30 líneas). No leer CHANGELOG, VALIDATION ni updates/ salvo que la tarea lo exija.
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

## Seguridad clínica (no se recorta nunca)
Dosis, unidades, diluyente, concentración, aritmética, mL/h, máximos, contraindicaciones y avisos se mantienen íntegros. Contenido = borrador hasta revisión humana. Protocolo local y DGS/INFARMED prevalecen.

## Verificar antes de cerrar (solo lo afectado)
- Clínico: `cd clinical && python3 scripts/validate_modules.py && python3 scripts/audit_evidence_coverage.py | tail -3 && python3 -m unittest discover -s tests -q`
- App: `cd app && npm test && npm run build`
- Al terminar: actualizar `STATE.md` (sustituir, no añadir histórico) y una línea en `clinical/CHANGELOG.md`.
