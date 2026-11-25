# R92 · CI y QA

Estado: **NOT_VERIFIED** para la CI remota del SHA que publicará este corte.
El recibo final de la PR y los informes finales entregados registran los
resultados observados del SHA exacto, sin reusar resultados de sus padres.

| Control local observado | Estado |
| --- | --- |
| Node route-identity, seis casos originales | PASS |
| Vitest route-identity, siete casos incluido S2187 | PASS |
| React pediatría, diez casos | PASS |
| Prueba S2187 frente a guarda HTTP desactivada en copia temporal | PASS: detecta la mutación |
| Regresión de historial frente a componente original en copia temporal | PASS: reproduce el defecto |
| Frontend completo, 1.044 pruebas / 54 archivos | PASS |
| Lint, tipos y compilación | PASS |
| Navegador combinado: 106 positivos, nueve estados de historial, once negativos | PASS |
| Catálogo 89 pautas / 52 familias y 513 enlaces | PASS |
| Cinco escenarios pediátricos existentes con API real | PASS |
| Clinical QA del árbol combinado | NOT_VERIFIED hasta su recibo de ejecución |
| Cobertura, Semgrep, Trivy, T05/T06 y Sonar remotos del candidato | NOT_VERIFIED hasta completar CI |

Comandos desde app: `npm test`, `npm run lint`, `npm run typecheck`,
`npm run build`, `npm run pediatrics:browser-check`,
`node scripts/check-route-navigation.mjs` con ROUTE_QA_OUTPUT fuera del árbol.
Desde clinical: `python qa/qa_runner.py`, con OCR y fuente de pruebas verificados.
Los logs y hashes de fuente/compilación se incluyen en la entrega reproducible.

App UI QA ya ejecuta el arnés ampliado y publica su JSON en Actions; no se crea
un verificador paralelo. Sus errores y negativos no producen PASS de módulo.
La CI conserva las dependencias fijadas y todos los gates existentes.

No inferir cero incidencias de un gate aprobado. El cierre de S2187 requiere el
reanálisis del SHA PR105 y su correspondiente evidencia Sonar, y después el del
candidato combinado. No se cambian exclusiones ni umbrales para pasar.

Auditoría independiente: **BLOCKED**, pendiente del candidato publicado;
no se afirma dictamen favorable por superar CI. Sin fusión ni despliegue.
CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE.
