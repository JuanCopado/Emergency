# Primera fuente canónica propia con contenido recuperable

Se admite exclusivamente `src-internal-image-safety-workflow` para ensayo local, reutilizando la autorización expresa del propietario ya existente y el binding canónico cotejado. No se solicita otro permiso ni se infieren derechos para otras fuentes. **CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE**.

La copia es `clinical/modules/clinical-images.md` en Git `1f0fed8d731f65168ac338b5ddb18f451fccc6d6`, SHA256 UTF-8 LF `ec1e12141ee3cdc864f1c2e1071a1877dd859634ac1157bf882448db1167780a`. Sólo se indexan los spans3–15 y35–47; sus hashes y el permiso coinciden con una tabla fija del adaptador. La indexación conserva coordenadas originales: no reenumera líneas ni permite ampliaciones del manifiesto fuera de esos spans. El resto del módulo no se introduce en el índice.

El join comprobado es source_id→`module_sources/clinical-image-interpretation/1`→relación SUPPORTED_BY y LOCATED_IN del grafo→línea96 de `module-index.md`→archivo exacto. Se cotejan el hash del índice de módulos, el del archivo y los de spans sobre el snapshot ya fijado. No se usa semejanza del título. Los dos documentos de gobernanza y fixtures previos conservan sus permisos.

Las citas declaran `source_class=project_owned_workflow`, `scope=internal_workflow_not_primary_evidence`, versión de copia `git:1f0...` y hash completo, con `source_hash_mode=utf8_lf_normalized`. A la vez preservan `declared_canonical_version=null`, `binding_role=historical_component_pending_reconciliation`, claim_scope literal y estado YELLOW. La versión de copia no rellena ni corrige el campo null del catálogo. El rol histórico no se promueve a identidad canónica clínica o reconciliación integral.

```powershell
python -B -X utf8 clinical/scripts/rag_content_retrieval.py index --graph knowledge-graph/generated/project-graph.json --as-of 2026-11-27 --output knowledge-graph/generated/rag-content-index.json
python -B -X utf8 clinical/scripts/rag_content_retrieval.py retrieve --graph knowledge-graph/generated/project-graph.json --index knowledge-graph/generated/rag-content-index.json --query rag/examples/canonical-workflow-query.json
python -B -X utf8 -m unittest discover -s clinical/tests -p test_rag_canonical_workflow.py -v
```

El índice pasa de58a64fragmentos. `audit-rights` admite1fuente canónica para sus spans de workflow local y mantiene253restringidas por su situación real. La ausencia de campo de permisos o versión declarada no es por sí sola una denegación cuando ya existe autorización del propietario y copia exacta: este adaptador resuelve precisamente ese caso, sin autorización universal.

Las8pruebas nuevas de binding cubren citas reales, coordenadas, escape de spans, binding falso, versión null/rol histórico preservados, hashes de spans, auditoría1/253 y NoAuthorityPromptInjectionScope. Un noveno negativo verifica el rechazo estático de RecursionError ante un índice JSON de10000arrays/20001bytes, en proceso hijo con límite de recursión200, preflight real del decodificador y timeout5s, sin traceback ni fuzz adicional. Las16de contenido y13de metadatos se ejecutan sólo como regresiones del cambio de fuente, separadas de las nuevas. `qa_runner.py` descubre la nueva suite `test_*.py` sin cambiar workflows.

El contenido continúa siendo dato no confiable: cita escapada, sin LLM, herramientas/URLs activadas o prescripción. La autoridad documental del workflow no se convierte en autoridad de instrucciones o validación clínica. Índice y respuestas con extractos permanecen LOCAL_ONLY; código/tests/manifiestos y recibos sin extractos pueden entregarse para CI y revisión. No se cambia catálogo, registro, fuente, dosis o `last_checked`.
