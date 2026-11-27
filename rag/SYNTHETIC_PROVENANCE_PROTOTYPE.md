# Recuperación RAG · primer incremento de procedencia sintética

ID existente: `F4-RAG-FHIR-HL7-PACS-AGENTES-G05`, matriz v8. Base internacional `1f0fed8d731f65168ac338b5ddb18f451fccc6d6`. **CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE**.

La CLI `clinical/scripts/rag_provenance_retrieval.py` implementa el primer paso de recuperación: consulta sintética por `module_id`, `source_id` opcional y versión exacta opcional. Resuelve la relación canónica del catálogo/grafo, contrasta su identidad con el registro y devuelve metadatos literales con una cita verificable. No es un sistema clínico generativo completo: no recupera textos de guías, interpreta pacientes, selecciona tratamientos, crea embeddings o usa un LLM.

Reutiliza `evidence-sources.json`, `evidence-registry.json` y el grafo397nodos/417relaciones. No crea otro catálogo, grafo, motor numérico, servicio o conector. Las250licenciasunknown,2restricted y2verified del catálogo no acreditan por sí mismas permisos RAG por campo/uso. `synthetic-provenance-consumer.json` limita la lectura a los metadatos locales existentes solicitados para este prototipo y concede cero permisos sobre contenido fuente o producción. G05-01..06 permanecen abiertos; PTBR-PIX no se habilita.

## Ejecución

El operador debe disponer del grafo existente dentro de su carpeta de entrada autorizada. La recepción copió, sin regenerarlo, `architecture-delivery/project-graph.json` a `knowledge-graph/generated/project-graph.json`, excluido de Git. SHA256 `78c3fd153c44bebf4434a6456fb320819a1bfa3cf1e7ade160eddb52afd0112d`.

Desde la raíz:

```powershell
python -B -X utf8 clinical/scripts/rag_provenance_retrieval.py --graph knowledge-graph/generated/project-graph.json --query rag/examples/provenance-query.json
```

Reutiliza `cli_paths.input_file`: los argumentos no pueden ampliar la carpeta elegida por el operador. Otra carpeta requiere el mecanismo existente `EMERGENCY_CLI_INPUT_ROOT`, sin convertir ese permiso local en autorización de datos clínicos. La CLI sólo lee entradas y escribe stdout; guardar una salida es una acción explícita del operador para el laboratorio sintético. No inicia comunicaciones, procesos, servicios o retención automática de pacientes.

Éxito: `RETRIEVED_METADATA`, código0. Abstención: `ABSTAIN`, código2 y cero citas. Los errores de lectura/estructura usan mensajes estáticos sin reflejar cuerpos privados.

## Citas y abstención

La salida contiene el commit canónico; SHA256 de catálogo, registro, grafo y contrato; versión literal; nulls desconocidos; localizadores JSON de fuente y relación; hash del registro fuente completo. La URL del catálogo fija el commit consultado. DOI/URL es un dato del catálogo: no se sigue ni acredita una revisión externa actual.

Para catálogo/registro se comparan los bytes Git LF, tolerando únicamente CRLF del checkout Windows. El grafo externo conserva su hash de bytes exactos. Cambiar valores sigue rechazándose; no se fuerza una configuración global para ejecutar el prototipo.

El ejemplo ACS devuelve `src-b3266402`, `/sources/110`, versión `ESC ACS 2023 (2024 correction); ACC/AHA 2025 currency comparison`. `license_status=unknown` permanece unknown; green es el estado bibliográfico existente. La salida conserva `can_answer_clinical_question=false`, `source_content_retrieved=false`, `clinical_generation_performed=false` y `runtime_activation_authorized=false`.

Se abstiene ante consulta no sintética/campos libres, IDs no vinculados, identidad compuesta, componente histórico no conciliado, versión ausente/distinta, bytes alterados, discrepancia catálogo/registro/grafo o contrato ampliado a textos, generación clínica o consumidores externos. No hace coincidencia aproximada ni sustituye la identidad canónica por un componente histórico. `src-who-meningitis-2025` conserva verified, pero su relación histórica pendiente no se vuelve fuente actual de `cns-infection`.

El contrato es una frontera local, no firma legal o autenticación de consumidor público. Un operador con control del código/carpeta puede cambiar el programa; no se afirma aislamiento frente a ese operador. Recuperar contenido clínico necesita permisos específicos por fuente/campo/uso y otro alcance revisado.

## Comprobación

```powershell
python -B -X utf8 -m unittest discover -s clinical/tests -p test_rag_provenance_retrieval.py -v
```

Pruebas focales: cita/versión exactas, histórico/compuesto, deriva de estados/relaciones/registro, privacidad, derechos no ampliables, hashes y ausencia de mutación. El fixture pequeño vive en memoria y no materializa otro grafo del proyecto. La recepción funcional usa el grafo397/417 real, con recibos separados.

No se repiten las14pruebas del grafo, CI integrado, WindowsClinicalMinimal ni suites globales. No se modifican evidencia, dosis, fechaslast_checked, fuentes, estados clínicos, matriz única o documentos centrales. El siguiente incremento exige un contrato de contenido autorizado y evaluación sintética de citas/abstención antes de generación clínica.
