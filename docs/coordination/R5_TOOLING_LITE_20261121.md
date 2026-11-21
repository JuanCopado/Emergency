# R5 · Ponytail lite y Graphify · 21/11/2026

Windows ARM64. Rama de trabajo `codex/r5-consolidation-20261121`, receptor `95c5f25f755e27628baf8e5f69f60df2b308ea92`. Corte examinado `fbe5c8d47d0f99cc5d539dccca6656049b09f757`. Tarea acotada autorizada, revisión final de la corrección S8786 y sus consumidores de impresión/exportación.

## Procedimiento aplicado

Ponytail oficial se cargó manualmente como skill en modo **lite**, fijada al [commit96608e078](https://github.com/DietrichGebert/ponytail/tree/96608e078b2d5ea607c5c3b8b5a54d1c1fba6846). SHA256 de `SKILL.md`, `9badd22a32e19cb884e46dfa8d3aae82bb81dfa5484105b8b4f0262df823a509`. No existía registro activo del plugin del host. Se descargaron la skill y su guía para aplicar su procedimiento local; no se presenta como instalación del plugin de escritorio.

Se inventariaron llamadores, pruebas, snapshots, generación de secciones y fronteras HTTP. La opción focal conserva la corrección de dos líneas en el formateador común. Se comprobaron preservación del literal de código, validación, confirmación y fidelidad previa a exportación. Se reutilizaron expresamente las19 pruebas y230 comparaciones de B. La aplicación real fue esta revisión del delta y la decisión de mantener su alcance mínimo; no se declara uso por la mera lectura de instrucciones.

Graphify **0.9.111** estaba instalado en `C:/Users/juanc/AppData/Local/Programs/Python/Python313-arm64/Scripts/graphify.exe`. El grafo anterior de la copia privada correspondía al commit621dad05 y difería en los cinco archivos comunes; faltaba la prueba TSX. Se generó un grafo nuevo de seis archivos versionados, copiados con sus bytes y exclusiones a un directorio de evidencia.

```powershell
& $g extract ./graphify-input --code-only --max-workers 1 --out .
& $g explain clinical_scripts_acute_medication_api_export_request
& $g explain clinical_scripts_acute_medication_api_calculate_request
& $g explain clinical_scripts_acute_medication_api_lines
& $g explain clinical_scripts_acute_medication_api_report_prose
& $g path app_src_pages_acutemedications_acutemedications clinical_scripts_acute_medication_api_report_prose
```

Se obtuvieron152 nodos,302 relaciones y7 comunidades mediante extracción AST local. Se usó la cadena `export_request → calculate_request → _lines → _report_prose` para confirmar el punto compartido de la corrección. Las llamadas indirectas a PDF/DOCX y el tramo HTTP se cotejaron contra el código. La consulta de ruta del navegador al formateador no devolvió ruta dirigida; no se inventó esa arista. La prueba TSX no produjo símbolos en este extractor. El grafo no sustituye las pruebas nativas ni constituye evidencia clínica.

## Evidencia y límites

Expediente externo `tools-evidence/R5_PONYTAIL_GRAPHIFY_20261121.md`, con skill original, procedencia, huellas de los seis archivos, `graphify-out/graph.json`, log de extracción y resultados de consultas. Se conserva junto al expediente R5. No se hicieron nuevas consultas públicas de datos clínicos ni se incorporaron secretos o PHI al grafo.

El plugin Ponytail de escritorio requeriría instalación/confianza de hooks y reinicio; queda fuera de la aplicación manual completada. La impresión nativa del compuesto y las locuciones literales permanecen pendientes en [la QA Windows](../../clinical/qa/R5_WINDOWS_QA_LIMITATIONS_20261121.md).
