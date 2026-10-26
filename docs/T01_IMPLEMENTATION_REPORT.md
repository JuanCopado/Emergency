# T01 — integración controlada de arquitectura y CI

Resultado global: **FAIL / BLOCKED para iniciar MVP**. Las correcciones técnicas y sus regresiones pasan; la auditoría de evidencia y la fidelidad PDF impiden declarar PASS global. No se modifican datos clínicos para superar estos gates.

## Base y aislamiento

- Base obligatoria: `ada519ac2f8e31ce807f397319ce260724642756` en `codex/v144-hybrid-baseline`.
- Fuente main fijada: `4f37263f581c41874fd3253147e6679b0b0685d8`.
- Worktree: `/workspace/work/Emergency-T01`; rama `codex/v144-t01-architecture-ci`.
- Ancestro común con main: `1a74e8db7f8079e1ac56249e9cd97db2f2aad8f6`.
- No merge, rebase, push, PR ni publicación. Esta entrega sólo existe en la rama aislada.
- C01 permanece en su worktree original; su cambio pendiente no se incorpora ni modifica.

## Inventario y procedencia por archivo

Se selecciona contenido técnico por SHA, sin incorporar los commits completos. El catálogo se genera de nuevo desde v1.44. Los números de origen siguientes son prefijos de los SHAs completos de la matriz posterior.

| Archivo | Origen / adaptación |
|---|---|
| `.github/workflows/app-ui-qa.yml` | T01; extender QA existente, sin copiar app-ci.yml/clinical-ci.yml de main |
| `.github/workflows/clinical-qa.yml` | T01; extender QA existente, sin copiar app-ci.yml/clinical-ci.yml de main |
| `.github/workflows/v1.40-evidence-surveillance-qa.yml` | T01; extender QA existente, sin copiar app-ci.yml/clinical-ci.yml de main |
| `.gitignore` | 3746400 |
| `.graphifyignore` | 625cd55 |
| `CLAUDE.md` | 625cd55; conciliación manual, no sustitución por documentación histórica de main |
| `README.md` | 625cd55; conciliación manual, no sustitución por documentación histórica de main |
| `STATE.md` | 625cd55, 3746400, 13ffc7d, 8f28d0f, 106a966, 990092c, 71b48f8, 6bb4c7e, 00f2975, 4f37263; conciliación manual, no sustitución por documentación histórica de main |
| `clinical/CHANGELOG.md` | 625cd55, 3746400, 13ffc7d, 8f28d0f, 106a966, 990092c, 71b48f8, 6bb4c7e, 00f2975, 4f37263; conciliación manual, no sustitución por documentación histórica de main |
| `clinical/references/evidence-source-overrides.json` | 8f28d0f, 106a966, 990092c, 71b48f8, 6bb4c7e, 00f2975, 4f37263 |
| `clinical/references/evidence-sources.json` | 13ffc7d, 8f28d0f, 106a966, 990092c, 71b48f8, 6bb4c7e, 00f2975, 4f37263; regenerado para v1.44, no copiado de main |
| `clinical/scripts/audit_evidence_coverage.py` | 3746400, 13ffc7d; HIGH_RISK de v1.44 preservado íntegramente |
| `clinical/scripts/build_project_graph.py` | 625cd55, 13ffc7d |
| `clinical/scripts/normalize_evidence_sources.py` | 13ffc7d, 8f28d0f, 71b48f8; corregida preservación de identidad canónica, componentes históricos y detección de + |
| `clinical/scripts/validate_modules.py` | 3746400 |
| `clinical/tests/test_ci_v142.py` | T01 sobre la base v1.44 |
| `clinical/tests/test_evidence_normalization_t01.py` | T01 sobre la base v1.44 |
| `clinical/tests/test_project_graph.py` | 625cd55, 13ffc7d, 8f28d0f, 106a966, 990092c, 71b48f8, 6bb4c7e, 00f2975, 4f37263; cobertura canónica 131, determinismo y mapas inválidos; componentes separados de identidad canónica |
| `clinical/tests/test_validation_hardening.py` | 3746400 |
| `docs/ARCHITECTURE.md` | 625cd55 |
| `docs/GRAPHIFY.md` | 625cd55 |
| `docs/T01_IMPLEMENTATION_REPORT.md` | T01 sobre la base v1.44 |
| `knowledge-graph/README.md` | 625cd55, 13ffc7d, 8f28d0f |
| `models/MODEL_REGISTRY.md` | 625cd55 |
| `rag/README.md` | 625cd55, 13ffc7d, 8f28d0f |

## Matriz de los diez commits

Los lotes son dependientes: arquitectura → validadores → normalización → componentes históricos. No se sustituyen módulos, registro canónico, estados o contratos clínicos.

| Commit completo | Aporte | Tratamiento |
|---|---|---|
| `625cd5545f4832766807ff817ae3468054e955cc` | Consolidate project architecture with Graphify, RAG and knowledge graph | Arquitectura/grafo/documentación seleccionados; CI adaptada a workflows existentes. |
| `374640043e33b605b6dd4a988fc9df132d2ead85` | Harden manifest validation, Living Evidence and CI | Validadores seleccionados, conjunto HIGH_RISK preservado; lint añadido al workflow existente. |
| `13ffc7d41a93c2a2fd7c327d47d47e2a26634a5f` | Normalize evidence provenance for Knowledge Graph and RAG | Normalizador, grafo y contrato RAG seleccionados; catálogo regenerado. |
| `8f28d0f60aa6a11617dd9b3884250eb92405ae74` | Split and verify priority high-risk evidence sources | Componentes históricos y regresiones del lote conservados, sin sustituir la identidad canónica. |
| `106a966a7670bb88aebd57884520875bc2bf2275` | Split and verify high-risk evidence sources batch 2 | Componentes históricos y regresiones del lote conservados, sin sustituir la identidad canónica. |
| `990092cf476252489e601379cfb713fb7472e26a` | Split respiratory, POCUS and neuro evidence sources batch 3 | Componentes históricos y regresiones del lote conservados, sin sustituir la identidad canónica. |
| `71b48f8902be998bc5ec3ac6a425063df5ef52c4` | Split ECG, imaging, endocrine and neuro evidence sources batch 4 | Componentes históricos y regresiones del lote conservados, sin sustituir la identidad canónica. |
| `6bb4c7e3d172b9ebdc11d65436ceac6aea4f49ce` | Split infectious, respiratory, cardiac and pediatric evidence sources batch 5 | Componentes históricos y regresiones del lote conservados, sin sustituir la identidad canónica. |
| `00f2975ee480bdc01b92c8600730bdcdeb6eb691` | Split regulatory, orthopedic and acid-base evidence sources batch 6 | Componentes históricos y regresiones del lote conservados, sin sustituir la identidad canónica. |
| `4f37263f581c41874fd3253147e6679b0b0685d8` | Split residual high-risk evidence sources batch 7 | Componentes históricos y regresiones del lote conservados, sin sustituir la identidad canónica. |

## Decisiones y revisión independiente

1. CI: ampliar `main`, `v1.*` con `codex/**` en los tres workflows de validación. Mantener filtros de rutas, permisos y jobs actuales. Añadir rutas de arquitectura/RAG/grafo/modelos al QA clínico; añadir normalización y generación del grafo. No duplicar los dos workflows de main. PTB-XL y vigilancia programada no amplían sus disparadores.
2. Conservar los 57 IDs HIGH_RISK de v1.44 exactamente; la revisión temporal adicional puede bloquear evidencia obsoleta.
3. La revisión independiente identificó tres defectos heredados de main: colapso por URL, sustitución de referencias actuales por overrides antiguos, y falta de detección de compuestos con ` + `. Cuatro regresiones fallaron antes de corregirlos y pasan después.
4. El normalizador ahora conserva título, URL, versión y fecha histórica de cada identidad canónica; no inventa una verificación actual. Los IDs derivados reflejan esos metadatos y no son un contrato RAG publicado.
5. Los componentes importados de main se etiquetan `historical_component_pending_reconciliation`; se añaden a `canonical_registry_identity`, nunca la reemplazan. Las pruebas heredadas de los lotes comprueban sus componentes históricos; una regresión nueva exige conservar también la identidad canónica de cada uno de los 131 módulos.
6. Se corrigió además la referencia documental al workflow retenido: `clinical-qa.yml`.
7. No se cambia la fecha de revisión ni el estado GREEN para conseguir PASS. No se oculta el fallo de la prueba estructural antigua que exige cero errores del auditor completo.

Riesgo si se interpretan mal estas decisiones: más fuentes o relaciones no significan más evidencia aprobada ni cobertura clínica conciliada. RAG permanece como contrato documental; T01 no implementa recuperación semántica ni promueve modelos.

## Cobertura antes/después

| Indicador | Base v1.44 | main de origen | T01 final |
|---|---:|---:|---:|
| Módulos del registro canónico | 131 | 106 en catálogo | 131 |
| Estados v1.44 | 29 GREEN / 102 YELLOW | no se trasladan | idénticos |
| Catálogo normalizado | ausente | 154 fuentes / 106 módulos | 220 fuentes / 131 módulos |
| Relaciones módulo-fuente | sin catálogo | históricas | 249 |
| Identidades compuestas pendientes | sin catálogo | no extrapolar a v1.44 | 77 |
| Grafo | herramienta ausente | snapshot histórico | 363 nodos / 380 aristas |
| HIGH_RISK v1.44 | 57 | no sustituir | 57, conjunto idéntico |
| Workflows QA con push codex/** | 0 | 0 | 3, sujetos a paths |
| Pruebas de configuración CI | 6 | no aplicable | 8 |
| Tests Python de QA | 578 PASS | no ejecutado | 603 ejecutados; 1 fallo |

La primera generación provisional (176 fuentes / 15 compuestos) fue descartada tras la revisión de procedencia. No es el resultado final ni un dato histórico clínico que deba preservarse.

## Validaciones observadas

| Comando / control | Resultado |
|---|---|
| `python -m unittest discover -s clinical/tests -p test_ci_v142.py -v` | 8/8 PASS; dos pruebas nuevas observadas RED antes de la corrección |
| actionlint 1.7.7 sobre todos los workflows | exit 0; comprobación Actions, shellcheck externo desactivado |
| `python clinical/scripts/normalize_evidence_sources.py --check` | PASS, 220 fuentes / 131 módulos |
| `python clinical/scripts/validate_modules.py` | PASS, 131 módulos resueltos |
| `python -m unittest discover -s clinical/tests -p test_evidence_normalization_t01.py -v` | 4/4 PASS, antes 4 FAIL con implementación importada |
| `python -m unittest discover -s clinical/tests -p test_project_graph.py -v` | 14/14 PASS |
| `python -m unittest discover -s clinical/tests -p test_validation_hardening.py -v` | 5/5 PASS |
| `python clinical/scripts/build_project_graph.py --output ...` | PASS; determinismo y rechazo de mapas inválidos cubiertos |
| `python clinical/scripts/audit_evidence_coverage.py` | FAIL: tres GREEN fuera de ventana; datos conservados |
| `cd clinical && python qa/qa_runner.py` | BLOCKED: auditoría y una regresión dependiente del auditor; demás checks pasan |
| `npm test -- --maxWorkers=2 --minWorkers=1` | 376/376 PASS en 10 archivos |
| `npm run lint` | PASS |
| `npm run typecheck` | PASS |
| `npm run build` | PASS |
| `npm run guides:test`, `npm run procedures:test`, `npm run pediatrics:check` | PASS; 89 regímenes pediátricos preservados |
| `node --test scripts/write-qa-evidence.node-test.mjs` y ejecución directa | PASS; 2 tests de la base; C01 no incorporado |
| `CHROMIUM_PATH=/usr/bin/chromium npm run pediatrics:browser-check` | PASS, 4 casos con API real |
| `CHROMIUM_PATH=/usr/bin/chromium npm run guides:print-check` | FAIL, texto canónico ausente de PDF en /clinical/airway-rsi |
| Hashes protegidos y C01 | 673/673 archivos idénticos; C01 pendiente idéntico |
| `git diff --check` | PASS |

Las dependencias frontend se copiaron de la instalación existente a la copia aislada; no se cambiaron package.json ni lockfiles. Chromium y Python disponibles se usaron para navegador y PDF. No se instaló ni ejecutó Graphify externo; sí el generador determinista propio. No se lanzó Actions remoto ni se acredita ejecución real por push.

## Fallos, riesgos y gates pendientes

- Auditoría a fecha 2026-10-26: `acute-ischemic-stroke`, `acute-coronary-syndrome` y `sepsis-shock` llevan 42 días frente a ventana de 30. Advertencias adicionales para soft-tissue-infections y clinical-image-interpretation. La revisión corresponde a responsables clínicos; T01 no cambia las fuentes ni fechas.
- `test_skill.ModularCoreTests.test_all_declared_high_risk_modules_have_evidence_records` falla porque exige `errors == []` del auditor completo y recibe esas tres caducidades. No se elimina ni debilita el gate para declarar PASS.
- PDF: la línea sobre conservar mg/mL y factores de gotas no aparece íntegra en el texto extraído. Mismo fallo reproducido en una extracción limpia de `app/` y `clinical/` del SHA base, compilada aparte con las mismas dependencias y Chromium. No se atribuye a T01; no se modifica presentación/contenido clínico para resolverlo en este encargo.
- 77 identidades compuestas y los componentes históricos requieren conciliación documental antes de uso clínico/RAG. Las licencias desconocidas siguen desconocidas.
- Runtime de CI remoto aún no observado; los patrones de rutas pueden omitir cambios ajenos a sus filtros deliberados. La revisión estática no equivale a un job GitHub ejecutado.
- Persisten los cuatro P1 originales `GMA-P1-001`, `GMA-P1-002`, `GMA-P1-003`, `GMA-C-P1-001`; los 19 contratos agudos bloqueados permanecen inalterados. CLINICALLY_PENDING.

## Entrega y propuesta de revisión

Cambios técnicos revisables exclusivamente en `codex/v144-t01-architecture-ci`; sin integración a la base compartida. Revisar el inventario, las regresiones de procedencia y el diff completo. Resolver los gates clínicos/documentales y PDF mediante encargos autorizados separados antes de declarar aptitud para MVP. No realizar push, PR ni publicación sin autorización posterior.

Evidencia local completa: `/workspace/work/T01-evidence/` (baseline, logs, manifests SHA256, comparación protegida, fuentes de commits, patch y ledger). El PASS técnico de componentes no constituye validación clínica. **Resultado global T01: FAIL / BLOCKED por validaciones pendientes.**
