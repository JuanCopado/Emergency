# PR115 · Conciliación con PR111 y PR116 · 26/11/2026

Estado: candidato aislado; CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE. Sin modificación de main, RC1, ramas protegidas, reglas C12 ni despliegue. Auditoría independiente externa sigue siendo obligatoria antes de integrar.

## Fuentes exactas y composición

- Receptor leído, sin modificar: `87a17301c395546536dce12150307a5b1474f844`, ya incorpora PR111.
- PR115 original: `82278d37dc29fe49e6afbc8db7aafe8d7e4166c1`, árbol `05c2ec1c1a8d871cfe83c05c4540e941f35d30f3`.
- PR116: primera corrección `43d62015838d0b190869482ecde645cf86b56249`; después `cd1e55e` fija LF de la fuente JSON para preservar su SHA en Windows, con prueba Git RED→GREEN.
- Conciliación de código local: `815afcd8dd5b2e402be0d36ce7e16598347a0328`, árbol `0e6f4bc229f9d449b81aa74d3b8fcc9e34a20f95`. El candidato final añade pruebas focales y los entregables; su SHA exacto se entrega en el recibo CI final.
- Rama de candidato: `codex/pr115-pr116-integrated-20261126`; worktree `/workspace/emergency-integrated`.

`git merge-tree --write-tree 87a1730 82278d3` produce exactamente `05c2ec1c1a8d871cfe83c05c4540e941f35d30f3`: incorporar la ascendencia PR111 no modifica el contenido del candidato PR115. El primer merge local conserva ambas historias. No hay cherry-pick ni segunda aplicación del delta PR111. Se preservan byte a byte sus once archivos, salvo cambios propios posteriores de PR116 donde corresponda, que se comprueban aparte.

Se mantienen todos los archivos fuente PR112/113 del manifiesto de composición de PR115. PR114 conserva transporte fail-closed, pruebas, procedencia histórica T06, original congelado, adaptación exacta del test Unicode y workflow de navegador. `SOURCE_PROVENANCE.json` no se reetiqueta. Las pruebas de procedencia rechazan alterar el origen o retirar controles.

## Incompatibilidades resueltas

1. `STATE.md`: conservar ambos cortes y anteponer un estado integrado verificable; las declaraciones históricas no se presentan como conclusiones nuevas.
2. `app/src/clinical-note/api.ts`: PR116 partía del cliente anterior a la corrección PR114. Mantener el rechazo de JSON malformado, error de red/timeout durante lectura y privacidad de cuerpos; conservar además `ClinicalApiResponseError` con HTTP status/código para invalidar correctamente una revisión terapéutica. Se reprodujeron tres fallos eligiendo solo la variante PR116; pasan al combinar ambos contratos.
3. Harness funcional de PR115: seguir comprobando los 16 diagnósticos, discriminantes, acciones visibles, MCDT pendiente, idioma y salidas reales; después obtener una pauta sintética no prescriptiva y recibo mediante UI/API. Un booleano solo continúa sin habilitar exportación. JSON coincide exactamente con la petición de UI y la única pauta revisada. PDF/Word reales conservan diagnóstico y texto de revisión.
4. Windows: integrar el atributo LF específico y dos regresiones de identidad del catálogo; conservar la huella estricta y los valores clínicos.
5. El workflow conserva el recorrido funcional de PR114, incorpora el terapéutico de PR116 y mantiene los restantes controles. Sin exclusiones o umbrales relajados.

## Evidencia y límites

Recorrido integrado Chromium/Linux ejecutado: 16/16 casos API/UI/JSON PASS; PDF y Word reales del caso representativo PASS; negativos de MCDT pendiente, revisión booleana y contexto editado. Pruebas focales de conexión/pauta/exportación: 37/37 PASS antes de añadir seis negativos de transporte específico.

La QA completa, la matriz Picomatch, T05 Windows, T06 Linux, cobertura, Semgrep/Trivy y Sonar del candidato final se identifican por SHA en el recibo final. Los resultados anteriores de PR115/PR116 no sustituyen a esa CI. Logs y artefactos locales integrados: `/workspace/receipts-integrated/`.

## Pendientes farmacológicos y auditoría

`CODEX_RESIDUAL_CLINICAL_CONTRACTS.json` delimita exclusivamente GMA-P1-003, inventario/duplicidades y decisiones clínicas nuevas documentadas por Gemini y aprobadas explícitamente por el propietario. Se conservan los 19 contratos aceptados el 16/11. No hay nueva decisión clínica aprobada en este despacho ni se inventa conciliación regulatoria de protamina.

Antigravity debe auditar el SHA final y sus recibos. El expediente anterior documenta una denegación de permisos antes de cualquier lectura, no un dictamen. El propietario autoriza dejar el paquete y la orden para recogida (26/11). Se publican en PR118; recepción y dictamen pendientes. No se sustituye esa auditoría por tests de Codex ni se declara MERGE_READY.

Graphify y Ponytail no están instalados ni expuestos como herramientas operativas en este entorno; se usa el grafo determinista de procedencia y las relaciones Git reales, sin atribuirles ejecución ficticia. El grafo no es evidencia clínica nueva.
