# Emergency — Fase 3 de seguridad: dependencias transitivas

Fecha: 17/11/2026. Rama: `codex/security-deps-phase3-20261117`.

## Alcance
- Base: `codex/security-deps-phase2-20261117` en `1a5c138547f564e58c15441956fda91ad9ef7ef4`.
- Solo actualización de `app/package-lock.json`, sin alterar fórmulas, dosis, protocolos clínicos ni estados de revisión.
- Instalación en GitHub Actions con npm 11.21.2, Node 22 y npm ci reproducible.
- [Ejecución que genera y valida el lockfile](https://github.com/JuanCopado/Emergency/actions/runs/44053549612): SUCCESS; 445 tests frontend en 13 suites PASS, lint, TypeScript, build, guías/procedimientos y catálogo pediátrico PASS.
- Commit del lockfile: `30bc95bbbf518bfa11cfae7ed43cf7846ba99fec`.

## Paquetes actualizados
- undici: 8.11.2 → 8.12.4.
- source-map-js: 1.2.1 → 1.2.2.
- fast-uri: 3.1.8 → 3.1.9.
- postcss-selector-parser: 6.1.4 → 6.1.6.
- serialize-javascript: 7.1.2 → 7.1.4.
- Vite 6.4.6 y Vitest 4.1.12 se conservan de la fase 2.
- El workflow temporal de actualización se elimina de esta rama al cerrar el candidato.

## Pendientes antes de integración
- Validar con Trivy sobre el SHA final que desaparecen las alertas correspondientes; no anticipar el recuento.
- Comprobar Clinical QA, App UI QA, Semgrep y SonarQube sobre el SHA final.
- Revisar por separado dependencias que requieren migración mayor (`react-router` 6→7, `glob` 11→14, `minimatch` 10→11 si sigue presente en una ruta transitiva).
- No aceptar, silenciar ni excluir CVEs para obtener un gate verde.
- Mantener `CLINICALLY_PENDING`; tests técnicos no equivalen a validación asistencial.
