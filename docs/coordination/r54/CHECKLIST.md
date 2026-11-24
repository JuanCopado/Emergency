# R54 · Checklist de entrega

| Encargo | Estado verificable |
|---|---|
| Leer instrucciones/estado/handoff/QA/decisiones y verificar receptora | PASS; base final 2032374, rama aislada R54. |
| MED-DEC-R46-01 y MED-DEC-R46-02 | APPROVED_MEDICAL_OWNER, SÍ, 24/11/2026; referencia expresa registrada. |
| Extracción documental pendiente R51 | PASS; dos módulos íntegros antes/después, src-b5e20534 literal, registro y manifiesto; SHA por artefacto. |
| Salvaguardas corregidas R50 | PASS; padre, modalidades y proyección de 131 guías. |
| Protocolo de adjudicación | PASS documental; R50 §§5/7 con discrepancia M1 de R56 identificada. |
| Distribución y IDs reales | PASS; 8 M1, 4 M2, 18 M3; 4/2/9 por set; sin asignar por numeración. |
| Fichas individuales | PASS preparación de 30; 10 archivos con bytes/SHA verificados; 16 diagnósticos pendientes y 14 N/A. |
| Continuación R45 | Avance documental de fuentes Rx y requisitos por ID; 20 archivos conformes aún ausentes, sin inventar hashes. |
| Regresiones R54 | PASS, 21; incluye carga real de módulos, precisiones R50, SHA de artefactos, fechas/estados conservados, distribución, IDs opacos, N/A, ausencia de archivos, discrepancia M1 y rutas fuera del banco. |
| Proyección | PASS, 12 pruebas de guías y generador de 131 guías. |
| App sobre receptora con PR100 | PASS, 1.036 pruebas; build/typecheck y exclusión de laboratorio se registran en la evidencia de ejecución. |
| Seguridad local | PASS, 39 pruebas de informes/fronteras; reglas y umbrales sin cambios. |
| Navegador real | PASS, suite de laboratorio de 11 pruebas con ≥100 comprobaciones reales; corregido file:// bloqueado mediante cuatro assets estáticos por loopback. |
| Clinical QA / CI / Sonar / Semgrep / Trivy / T05 / T06 | Resultados definitivos por SHA en los checks y recibo de la PR; no heredar PASS de PR101 u otros commits. |
| Adjudicaciones individuales | PENDING, 0/30; no se crean decisiones ni firmas del propietario. |
| Auditoría independiente Antigravity y cotejo Gemini | Paquete preparado; recepción/dictamen pendientes de evidencia externa. |
| last_checked / estados | PASS conservación: padre yellow y 2026-09-17; 129 GREEN / 2 YELLOW; CLINICALLY_PENDING y NO_GO_CLINICAL_RELEASE. |
| R5-1, R5-2, G05 | ABIERTO / PENDIENTE / BLOQUEADO. Sin cierre, estudio humano, producción ni modificación de main. |

Las pruebas estructurales y de software no acreditan exactitud diagnóstica. El
cotejo de las 19 fuentes primarias y la desagregación de src-b5e20534 continúan
pendientes de revisión científica propia; no se renueva last_checked.

## Reproducción local

Instalar dependencias según los workflows y aplicar el postinstall de seguridad
de npm (`npm run security:picomatch:apply` si se usó `--ignore-scripts`). Preparar
el OCR con `npm ci --ignore-scripts --prefix tools/blood-gas-ocr` y
`python3 scripts/prepare_blood_gas_model.py`. Configurar `BG_OCR_MODEL`,
`BG_TEST_FONT` y `NODE_PATH` con las rutas del modelo verificado, la fuente
DejaVuSans incluida y los módulos del OCR. Se utilizó Chromium del entorno
porque la descarga de Playwright devolvió 403; la adaptación de ruta del ejecutable
solo afecta a la caché local, sin cambio de versión en el repositorio.

```sh
python3 -m unittest discover -s clinical/tests -p 'test_r54*.py' -q
python3 clinical/qa/qa_runner.py
python3 clinical/scripts/normalize_evidence_sources.py --check
python3 -m unittest discover -s security/tests -p 'test_*.py' -q
node --test app/scripts/build-clinical-guides.node-test.mjs
cd app
npm test
npm run build
npm run lint
npm run check:lab-exclusion
```

Primera QA sin preparación: 1 fallo de navegador y 19 errores OCR/fuente (1.649
pruebas, 15 omitidas). Se conserva ese fallo observado; no se cuenta como PASS.
Las regresiones focales del entorno preparado pasan. La suite completa y los
checks remotos se distinguen y se cierran con su resultado observado por SHA.
