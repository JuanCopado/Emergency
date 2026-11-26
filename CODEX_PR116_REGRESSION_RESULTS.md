# PR116 · Regresiones y causas raíz · 26/11/2026

Estado: CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE. Núcleo internacional; sin selección automática de jurisdicción. Ninguna dosis, concentración, fórmula, expectativa diagnóstica, aceptación médica o estado de evidencia se ha cambiado para pasar QA.

## Identidad y evidencia inicial

- HEAD comunicado: `8b970c1fe24c2972b2074a76c1ecaf498075a06c`.
- HEAD remoto al comenzar: `d2e6967c6f0e075ab812d374f7c8a4f6628c07f5`; su corrección previa de ruta se conserva.
- Primera corrección publicada en PR116: `43d62015838d0b190869482ecde645cf86b56249`, árbol `70a855c9c98c960b2fb553226648ce1b1e32d565`.
- Runs iniciales: [App UI](https://github.com/JuanCopado/Emergency/actions/runs/45907530763), [Clinical QA](https://github.com/JuanCopado/Emergency/actions/runs/45907530781), [Picomatch](https://github.com/JuanCopado/Emergency/actions/runs/45907530903). Los FAIL históricos no se reetiquetan.

## Causas y correcciones ejecutadas

| Fallo | Causa comprobada | Corrección / regresión |
|---|---|---|
| Missing functional contract `/corticosteroids` | Ruta registrada sin contrato de identidad en el HEAD observado. | `d2e6967` ya registra controles y regiones reales, rechaza páginas incompletas y comprueba interacción. Se conserva. |
| 16 fallos del banco de notas | El arnés antiguo confunde revisión general mediante booleano con revisión terapéutica de una versión. El gate nuevo rechaza correctamente esa salida. | El arnés solicita generación y revisión por la API real con cinco secciones explícitamente sintéticas y no prescriptivas. No se cambian fixtures clínicos ni sus expectativas. |
| 5 formatos inválidos | El fixture no había pasado el nuevo gate de tratamiento; nunca alcanzaba la validación del formato. | Completar la revisión real en el fixture; mantener las cinco expectativas de rechazo de formato. |
| JSON y notas históricas | Una pauta revisada sustituye tres salidas antiguas; exigir igualdad contra las dos pautas juntas contradice el contrato nuevo. | Comparar íntegramente el contenido salvo las tres salidas sustituidas; verificar la misma pauta/recibo, diagnósticos intactos y bloqueo al editar contexto. Las notas sin tratamiento mantienen JSON idéntico y PDF/DOCX legítimos. |
| Picomatch | Mitigación, fuzz y controles del parser pasan; falla la prueba de ruta de la aplicación. Un job hermano se cancela por fail-fast. | Corregir el contrato de ruta; conservar guardas, política de seguridad y matriz de instalación. No se atribuye el fallo al parser. |
| Navegador real | Playwright incluye opciones/contenido en algunas búsquedas `getByLabel` exactas; además se leía el color antes de acabar la transición CSS. | Buscar rol y nombre accesible exactos y esperar el estado verde con condición acotada; mantener aserciones de color, fuentes, población y bloqueo. Añadir el recorrido terapéutico al workflow existente. |

## Fallo adicional de Windows detectado en la nueva CI

El run Picomatch `45909319401` pasó las tres combinaciones Linux y falló las tres Windows en `corticosteroids:check`, después de pasar pruebas y guardas. El checkout Windows convirtió a CRLF el JSON fuente y alteró su SHA-256 embebido; no era un fallo del parser. Se reprodujo con un repositorio Git temporal y `core.autocrlf=true`: la prueba falla antes y pasa después. `.gitattributes` fija LF exclusivamente para `clinical/pharmacology/corticosteroids.json`. El generador conserva su verificación estricta de bytes; no se normalizan ni ignoran cambios de la fuente. Un negativo verifica que modificar metadatos sigue invalidando la proyección. Nueve pruebas focales PASS. La corrección posterior de PR116 es `cd1e55e`; su SHA completo y la repetición de la matriz están en los recibos finales.

## Regresiones positivas y negativas

`test_legacy_note_export_regression.py` comprueba notas históricas sin tratamiento en JSON/PDF/DOCX; privacidad y revisión general obligatorias; los 16 casos históricos requieren recibo real; se bloquean pauta omitida, recibo falso, contexto obsoleto y edición posterior en la API y en los tres exportadores directos.

El helper de revisión está exclusivamente en `clinical/qa/`: simula al operador con contenido no prescriptivo. No migra ni valida automáticamente historias reales. La API, sus firmas y sus controles clínicos no se debilitan. La afirmación de revisión médica en una prueba es simulada, no una aprobación clínica.

## Resultados observados del candidato PR116

- Reproducción local antes del arreglo: los mismos 21 fallos en `test_functional_v144.py`.
- Después: 4 pruebas del arnés PASS, banco completo 20/20; 4 regresiones nuevas PASS, con subcasos de formatos, notas y alteraciones.
- Clinical QA completa: 1.745 pruebas, 16 omitidas, cero fallos; siete gates PASS. Registro 131 módulos, 129 GREEN / 2 YELLOW / 0 RED.
- Frontend: 1.098 pruebas PASS; identidad de ruta Node 7/7; lint y TypeScript PASS.
- Build de seguridad PASS con `EMERGENCY_SECURITY_AUDIT=1`. Primer intento local sin esa variable falló por falta de `sw.js.map`; se conserva el log y no se cuenta como PASS.
- Chromium 154/Linux: navegación completa PASS, 514 enlaces; comparación Endotext/ESE, edición/reinicio, revisión terapéutica adulto/lactante, rojo/verde, descarga real y bloqueo tras edición PASS. Capturas 1366/360 px, solo casos sintéticos.
- Seguridad local: 39 pruebas PASS. La ejecución Windows y Sonar se acreditan solo mediante la CI remota del SHA correspondiente.

CI remota histórica de `43d6201` (incluye el FAIL Windows que originó la segunda corrección): [App UI](https://github.com/JuanCopado/Emergency/actions/runs/45909319215), [Clinical](https://github.com/JuanCopado/Emergency/actions/runs/45909319221), [Picomatch](https://github.com/JuanCopado/Emergency/actions/runs/45909319401), [Security](https://github.com/JuanCopado/Emergency/actions/runs/45909319195). Sus conclusiones y las del candidato integrado se registran en el recibo final, sin extrapolar PASS locales.

Logs originales y locales: `/workspace/receipts-pr116/`. Los recorridos iniciales declaran `dirty=true`; la CI remota identifica el checkout exacto. Recibo final y SHA del árbol integrado en `CODEX_PR115_RECONCILIATION.md` y el paquete de auditoría.
