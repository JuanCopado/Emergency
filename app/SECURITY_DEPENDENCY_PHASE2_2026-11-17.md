# Emergency — Fase 2 de seguridad de dependencias frontend

Fecha: 2026-11-17. Rama aislada: `codex/security-deps-phase2-20261117`.

## Referencias y alcance
- Base: fase 1 de seguridad `2d3d982c727480a535e854b6d38f619cdcf583e0`.
- Resolución y pruebas: [GitHub Actions 44052782676](https://github.com/JuanCopado/Emergency/actions/runs/44052782676) — SUCCESS.
- Commit de dependencias: `bfa9ab5f4c2a009d9526e383cd5634bd6a996221`.
- Sin cambios en `main`, protocolos clínicos, aritmética, evidencia ni liberación asistencial.

## Correcciones
- `vite`: 5.4.21 → 6.4.6 (versión exacta).
- `vitest`: 2.1.9 → 4.1.12 (versión exacta).
- `@vitest/mocker`: 2.1.9 → 4.1.12 (dependencia transitiva).
- `tinypool`: la versión 1.1.1 deja de instalarse con la nueva resolución.
- `package-lock.json` regenerado por npm 11.21.2, luego verificado con `npm ci`.
- `app/vite.config.ts`: acceso a Markdown de `clinical/modules` permitido exclusivamente en modo test, sin relajar el servidor normal de desarrollo.
- El workflow temporal para generar y publicar los dos manifiestos se elimina en el cierre de esta tarea.

## Comprobaciones observadas
- 13/13 suites frontend y 445/445 tests PASS.
- Generación/validación de guías, procedimientos y catálogo pediátrico PASS.
- ESLint, TypeScript, compilación Vite y comprobación de ausencia de deriva en catálogos clínicos PASS.
- La generación del lockfile solo se publicó tras superar estas comprobaciones.

## Controles pendientes
- Repetir App UI QA, Clinical QA, Semgrep, Trivy y Sonar sobre el SHA final de esta rama.
- Cuantificar los hallazgos restantes: especialmente undici, source-map-js, bibliotecas transitivas y React Router 6→7.
- No considerar resuelta una vulnerabilidad hasta confirmar el nuevo escaneo; no reducir ni silenciar gates para obtener verde.
- `CLINICALLY_PENDING` y revisiones humanas permanecen independientes de las pruebas técnicas.
