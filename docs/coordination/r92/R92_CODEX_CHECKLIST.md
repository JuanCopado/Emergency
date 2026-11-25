# R92 · Checklist

Estado: **NOT_VERIFIED** hasta completar la CI del candidato publicado.
Este checklist es el corte de publicación; el recibo final identifica SHA,
árbol, resultados y pendientes de auditoría sin modificar el árbol auditado.

- PASS: receptor y HEAD actuales PR104/105 comprobados.
- PASS: deltas completos sin solapamiento; historia conservada mediante merges.
- PASS: test S2187 explícito y significativo; seis casos compartidos conservados.
- PASS: pruebas Node, Vitest, React y controles de mutación/reproducción.
- PASS: paracetamol → fluticasona → Atrás/Adelante, recarga y enlace interno.
- PASS: rechazos HTTP 404, soft-404, controles ausentes, error y fallo de carga.
- PASS: frontend completo, lint, tipos, compilación y catálogo canónico intacto.
- NOT_VERIFIED en este corte: conclusión Sonar de 7017c7d y CI del candidato.
- NOT_VERIFIED en este corte: recibo final de Clinical QA local.
- BLOCKED: auditoría independiente del SHA final y cualquier integración en receptor.

Informes: [S2187](R92_CODEX_SONAR_S2187.md),
[regresión pediátrica](R92_CODEX_PEDIATRIC_REGRESSION.md),
[composición](R92_CODEX_PR104_PR105_COMBINED.md), [CI/QA](R92_CODEX_CI_QA.md).

main, RC1, producción y C12 sin modificaciones. Sin cambio de dosis, pautas,
fórmulas, catálogo, reglas, banco, sellos ni last_checked. No se cierran R5-1,
R5-2 o G05. CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE.
