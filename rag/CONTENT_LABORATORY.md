# RAG extractivo local · contenido propio y fixtures separados

ID existente: `F4-RAG-FHIR-HL7-PACS-AGENTES-G05`. Base `1f0fed8d731f65168ac338b5ddb18f451fccc6d6`. **CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE**.

Este incremento añade indexación persistente y respuestas extractivas sobre contenido real propio del proyecto. La autorización expresa del propietario, comunicada en esta orden de laboratorio del27/11/2026, cubre únicamente indexación, recuperación y cita local de `docs/INTERNATIONAL_SCOPE.md` y `docs/coordination/r5-g05-20261126/G05_REQUISITOS.json`. Se fijan archivo, versión/commit y SHA256. Su alcance es **gobernanza, no evidencia clínica primaria**. No se concede redistribución, entrenamiento, procesamiento externo, licencia general del repositorio ni uso clínico.

Las flags false delimitan consumo y corpus RAG generado, no publicación del código de laboratorio o de fixtures sintéticos originales autorizados por el propietario para revisión/CI. No revocan la publicación de documentos propios ya públicos ni modifican licencias externas. Índice y respuestas con extractos quedan LOCAL_ONLY; código, pruebas, permisos/manifiestos, fixtures originales y recibos sin extractos pueden entregarse para publicación y QA.

## Corpus y derechos

`content-laboratory.json` registra permisos por archivo, uso, versión y hash. El código restringe las fuentes propias a esos dos archivos canónicos y sus hashes del commit autorizado. Los textos inventados en `fixtures/content/` tienen otra clase, IDs, permisos y citas; no se añaden al catálogo clínico o al grafo. `PERMISSION.txt` expresa el permiso de ensayo, sin atribuir una licencia externa nueva.

El índice observado contiene58fragmentos de dos documentos propios y un fixture vigente. Otro fixture está caducado y el adversarial conocido queda en cuarentena. Las254entradas del catálogo clínico se auditan individualmente y permanecen bloqueadas para recuperación textual hasta disponer de permiso literal por contenido/uso. Esto no impide recuperar los dos documentos propios expresamente autorizados.

Se revisaron los dos registros `license_status=verified`: `src-internal-image-safety-workflow` carece de versión y localizador literal del contenido bajo esta autorización; `src-who-meningitis-2025` conserva versión2025, pero su relación histórica sigue pendiente y el catálogo no contiene una concesión de indexación/cita de su texto por uso. No se descargaron ni indexaron esos originales ni se infirieron permisos de la etiqueta verified. El auditado no sustituye una evaluación jurídica externa.

## Indexación y consulta

Desde la raíz, usando el grafo397/417 ya existente y copiado sin regeneración a su carpeta excluida de Git:

```powershell
python -B -X utf8 clinical/scripts/rag_content_retrieval.py index --graph knowledge-graph/generated/project-graph.json --as-of 2026-11-27 --output knowledge-graph/generated/rag-content-index.json
python -B -X utf8 clinical/scripts/rag_content_retrieval.py retrieve --graph knowledge-graph/generated/project-graph.json --index knowledge-graph/generated/rag-content-index.json --query rag/examples/content-query.json
python -B -X utf8 clinical/scripts/rag_content_retrieval.py audit-rights --graph knowledge-graph/generated/project-graph.json
```

Las rutas CLI usan las capacidades existentes `cli_paths`: no se amplía la carpeta autorizada mediante el payload. Se admiten sólo consultas de ensayo con términos del vocabulario acotado, versión opcional y fecha explícita; se rechazan campos de paciente, identificadores numéricos, emails, texto no contemplado y tamaños excesivos. Esto no es un detector general de PHI ni una interfaz para preguntas clínicas.

La búsqueda lexical exige todos los términos y ordena determinísticamente, con máximo3citas. El resultado devuelve texto extractivo escapado, archivo/líneas exactas, versión y hash. Cada cita propia conserva el commit; las citas de fixtures declaran su condición inventada y carecen de commit clínico atribuido. No hay inferencia, consejo terapéutico o promoción de estados.

## Integridad, vigencia e inyección documental

Cada consulta vuelve a leer archivos y permisos y reconstruye los fragmentos esperados. Se cotejan texto, posiciones, versión, exclusiones, manifiesto y hashes del snapshot con el índice almacenado. Alterar un índice y recalcular un hash propio no autoriza contenido. El hash fijo de cada documento propio impide envenenarlo y reautorizarlo mediante un manifiesto alterado. CRLF sólo se normaliza a los bytes Git LF; no se modifica el texto.

Las citas etiquetan `source_hash_mode=utf8_lf_normalized`: SHA256 de UTF-8 con CRLF→LF, equivalente a los bytes fuente Git de los documentos propios fijados. No es el SHA crudo de un archivo Windows con CRLF. Los valores OWN no se renuevan por merge o nueva fecha.

La ventana27/11–04/12/2026 es una política conservadora de revalidación del snapshot de laboratorio, no una fecha de publicación, expiración jurídica o revisión clínica. Se abstiene fuera de esa ventana, ante versión discordante y ante fuentes caducadas, incluso si caducan después de crear el índice. Ninguna fecha `last_checked` se renueva.

El límite principal frente a prompt injection es arquitectónico: no existe LLM, intérprete de instrucciones, ejecución de herramientas, cliente de red ni renderizador HTML/Markdown. Texto e instrucciones del programa permanecen separados; los documentos son datos no confiables. Las citas neutralizan HTML, sintaxis de enlaces Markdown y esquemas URI; cualquier consumidor posterior debe mostrarlas como texto, sin activar enlaces. Una cuarentena de marcadores conocidos es sólo defensa adicional: no pretende reconocer toda inyección. Las pruebas incluyen sintaxis adversarial fuera del detector y comprueban que permanece dato escapado, sin herramientas o URLs activadas.

Límites:64KiB por fuente,1600caracteres por fragmento,256fragmentos,512KiB de índice,2KiB por archivo de consulta y3citas por respuesta. No hay descarga remota, embeddings, servidor o cambios de configuración global. El operador que controla código/manifiesto puede modificarlos; esto no autentica un consumidor público ni aísla el sistema operativo.

## Pruebas y recepción

```powershell
python -B -X utf8 -m unittest discover -s clinical/tests -p test_rag_content_retrieval.py -v
```

Las16pruebas nuevas cubren citas reales/líneas/versiones, separación de fixtures, poisoning de archivo/índice/manifiesto, inyección conocida y desconocida, caducidad posterior al índice, permisos, rutas, límites y entradas malformadas. `clinical/qa/qa_runner.py` descubre `test_*.py`, incluyendo esta suite sin modificar workflows. Se repitieron aparte13regresiones de metadatos tras separar su función en helpers, sin cambio de conducta; no cuentan como pruebas nuevas. Las14del grafo no se repitieron.

La entrega mantiene el árbol staged anterior, aporta delta y parche conjunto revisables, y recibos de CLI real. No duplica el arnés127, no modifica centrales ni ramas protegidas, no hace push/merge y no habilita servicios clínicos. G05 y las aceptaciones clínicas previas conservan su alcance.
