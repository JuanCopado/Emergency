# PR115 · Conciliación con PR111 y PR116 · 26/11/2026

Estado: candidato aislado; CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE. Sin modificación de main, RC1, ramas protegidas, reglas C12 ni despliegue. Auditoría independiente externa sigue siendo obligatoria antes de integrar.

## Fuentes exactas y composición

- Receptor inicial leído `87a17301c395546536dce12150307a5b1474f844` (PR111); avance externo posterior PR117 a `570aa11bfe5c9df1c4a571f1103c28030d5731ca`, incorporado solo en las ramas aisladas. Este trabajo no modificó el receptor.
- PR115 original: `82278d37dc29fe49e6afbc8db7aafe8d7e4166c1`, árbol `05c2ec1c1a8d871cfe83c05c4540e941f35d30f3`.
- PR116: primera corrección `43d62015838d0b190869482ecde645cf86b56249`; después `cd1e55e` fija LF con prueba Git RED→GREEN y `31358266149a5dc52c589d094e09558479493009` separa datos localizados y hace explícito el orden canónico para resolver los cinco hallazgos Sonar, sin cambiar valores clínicos.
- Conciliación de código local: `815afcd8dd5b2e402be0d36ce7e16598347a0328`, árbol `0e6f4bc229f9d449b81aa74d3b8fcc9e34a20f95`. El candidato final añade pruebas focales y los entregables; su SHA exacto se entrega en el recibo CI final.
- Rama de candidato: `codex/pr115-pr116-integrated-20261126`; worktree `/workspace/emergency-integrated`.

`git merge-tree --write-tree 87a1730 82278d3` produce exactamente `05c2ec1c1a8d871cfe83c05c4540e941f35d30f3`: incorporar la ascendencia PR111 no modifica el contenido del candidato PR115. El primer merge local conserva ambas historias. No hay cherry-pick ni segunda aplicación del delta PR111. En el primer corte se preservaron sus once archivos byte a byte. En el corte vigente, ocho de ellos recogen la actualización posterior PR117; los trece destinos PR117 coinciden exactamente con el receptor actual, sin repetir el delta PR111.

Se mantienen todos los archivos fuente PR112/113 del manifiesto de composición de PR115. PR114 conserva transporte fail-closed, pruebas, procedencia histórica T06, original congelado, adaptación exacta del test Unicode y workflow de navegador. `SOURCE_PROVENANCE.json` no se reetiqueta. Las pruebas de procedencia rechazan alterar el origen o retirar controles.

## Incompatibilidades resueltas

1. `STATE.md`: conservar ambos cortes y anteponer un estado integrado verificable; las declaraciones históricas no se presentan como conclusiones nuevas.
2. `app/src/clinical-note/api.ts`: PR116 partía del cliente anterior a la corrección PR114. Mantener el rechazo de JSON malformado, error de red/timeout durante lectura y privacidad de cuerpos; conservar además `ClinicalApiResponseError` con HTTP status/código para invalidar correctamente una revisión terapéutica. Se reprodujeron tres fallos eligiendo solo la variante PR116; pasan al combinar ambos contratos.
3. Harness funcional de PR115: seguir comprobando los 16 diagnósticos, discriminantes, acciones visibles, MCDT pendiente, idioma y salidas reales; después obtener una pauta sintética no prescriptiva y recibo mediante UI/API. Un booleano solo continúa sin habilitar exportación. JSON coincide exactamente con la petición de UI y la única pauta revisada. PDF/Word reales conservan diagnóstico y texto de revisión.
4. Windows: integrar el atributo LF específico y dos regresiones de identidad del catálogo; conservar la huella estricta y los valores clínicos.
5. El workflow conserva el recorrido funcional de PR114, incorpora el terapéutico de PR116 y mantiene los restantes controles. Sin exclusiones o umbrales relajados.

## Seguimiento Sonar

El primer integrado `55c53dd` superó App UI, Clinical QA, seis combinaciones Picomatch y cinco jobs de seguridad/cobertura, pero Sonar rechazó duplicación 10,3 % y fiabilidad D. No se declara PASS global. El diagnóstico exacto identifica diccionarios localizados y cinco incidencias concretas; el delta fuente `3135826` se incorpora sin repetir los deltas anteriores. Los textos son idénticos en los cuatro idiomas, salvo el nombre técnico de una clave. La CI completa se vuelve a ejecutar sobre el árbol final. La orden para Antigravity debe usar el SHA actualizado y no el corte anterior `55c53dd`.

## Evidencia y límites

Recorrido integrado Chromium/Linux ejecutado: 16/16 casos API/UI/JSON PASS; PDF y Word reales del caso representativo PASS; negativos de MCDT pendiente, revisión booleana y contexto editado. Pruebas focales de conexión/pauta/exportación: 37/37 PASS antes de añadir seis negativos de transporte específico.

La QA completa, la matriz Picomatch, T05 Windows, T06 Linux, cobertura, Semgrep/Trivy y Sonar del candidato final se identifican por SHA en el recibo final. Los resultados anteriores de PR115/PR116 no sustituyen a esa CI. Logs y artefactos locales integrados: `/workspace/receipts-integrated/`.

## Pendientes farmacológicos y auditoría

`CODEX_RESIDUAL_CLINICAL_CONTRACTS.json` delimita exclusivamente GMA-P1-003, inventario/duplicidades y decisiones clínicas nuevas documentadas por Gemini y aprobadas explícitamente por el propietario. Se conservan los 19 contratos aceptados el 16/11. No hay nueva decisión clínica aprobada en este despacho ni se inventa conciliación regulatoria de protamina.

Antigravity debe auditar el SHA final y sus recibos. El expediente anterior documenta una denegación de permisos antes de cualquier lectura, no un dictamen. El propietario autoriza dejar el paquete y la orden para recogida (26/11). Se publican en PR118; recepción y dictamen pendientes. No se sustituye esa auditoría por tests de Codex ni se declara MERGE_READY.

Graphify y Ponytail no están instalados ni expuestos como herramientas operativas en este entorno; se usa el grafo determinista de procedencia y las relaciones Git reales, sin atribuirles ejecución ficticia. El grafo no es evidencia clínica nueva.

## Receptor vigente tras actualización externa

PR117 se fusionó externamente en `570aa11bfe5c9df1c4a571f1103c28030d5731ca`. Se concilia su delta de trece archivos de catálogo sin conflictos y se conserva byte a byte. PR116 queda en `50462b00a4c0af30889f8600be95aedd69d6c293`, que incorpora ese receptor y la corrección Sonar `3135826`. El candidato incluye esa ascendencia y repite CI completa; no se atribuyen al árbol final los checks del corte anterior.
