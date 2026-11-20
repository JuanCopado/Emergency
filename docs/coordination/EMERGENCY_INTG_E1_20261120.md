# Candidato técnico local E1 · 20/11/2026

Encargo del propietario: EMERGENCY-INTG-20261116-E1. Repositorio JuanCopado/Emergency. Rama local `codex/v144-intg-e1-20261120`; base `9b4f705dcfac0d52c10205f7c46c91f7b5b876df`, árbol base `898596eba6e8e07158571f0092258835a180fce1`. Sin commit, merge, rebase, cherry-pick, push, publicación ni ejecución remota. No se modifican main, RC1 ni v1.43. Los archivos originales y los worktrees anteriores se conservan.

## Selección y procedencia

La base internacional ya integra R2 (T01/P3/T03), las guardas posteriores de JSON/precisión, T05/T06, el selector manual aceptado y las decisiones documentales T02/tenecteplasa del 20/11. Es preferible al corte 1d0652 para evitar regresiones demostradas de entradas, traducciones y aceptaciones. Los objetos fuente T01/T03/T07 no accesibles no se presentan como recuperados: su funcionalidad integrada se inspecciona en esta base. No se importa el contexto alternativo 0a501269, que duplicaría selector/esquema.

PR19 está cerrado sin merge desde el 20/11: sus archivos territoriales ya están incorporados; issue18 permanece abierto para cobertura material adicional. La matriz es inventario, no validación de 896 protocolos. No se vuelven a importar los maestros históricos del borrador.

Delta local concreto:

- T07: asociación de unidad y descripciones visibles en NumberField; radios nativos de dirección; idioma español del contenido canónico de Procedures y conservación del idioma del panel territorial. Regresiones DOM y navegador sintético, sin cambiar cálculos ni textos clínicos.
- Generación: el estado procede del registro de evidencia y debe coincidir con MODULES; falta, invalidez, duplicación o discrepancia detiene la proyección. No se modifica ningún estado. Los catálogos se regeneran desde las fuentes finales.
- T00: se recuperan tres aserciones de avisos About de c9990d9bc51a21cd4b8775024b844a92e359884a, conservando las expectativas numéricas actuales.
- Imagen: 12 archivos de código, prueba, esquema, requisito y documentación del worktree multimodal 062d890, preservado por ZIP SHA256 `e09ee8c0843ce69857bdd8544561b46f5c36271dff3f9bbc855971980fb9e0e0`. Diez archivos conservan bytes; dos documentos identifican esta integración y una demo externa opcional. No se incorpora ni lee el banco reservado, medios o resultados históricos. Se reutilizan las métricas y congelación canónicas. Pillow13.0.0 coincide con el pin vigente; se declara también en requirements-test sin rebajar dependencias actuales.
- APIs: se conserva un adaptador por proveedor del circuito R6/B1/Q4. No se importa interop1075ef6 ni su CLI live: duplicaría adaptadores y degradaría el plazo absoluto existente. ESummary, consulta directa PMID/CVE y licencias por registro del piloto antiguo quedan como diferencias documentadas para una ampliación selectiva; no se anuncian como presentes.

## Reproducción y evidencia

Anexos de entrega externos al repositorio: inventarios UI, farmacología e imagen/API; manifiestos y parches; registros inmutables de cada comando; versiones y dependencias; manifiesto final por archivo y árbol efectivo calculado con índice temporal. No se suman suites históricas solapadas ni se sustituyen logs fallidos.

En Windows, la preparación nativa usa Python3.12.16 ABI win-amd64 y los hashes ya versionados en `security/requirements-ci.txt` y `security/requirements-blood-gas-ci.txt`; el host es ARM64. El intento ARM inicial rechazó el hash de la rueda específica de plataforma: no se relajó el lock. Node local24.15.0 difiere del Node22 de CI y se declara esa diferencia. Instalación npm desde lock; no actualización de versiones.

Órdenes principales desde la raíz, con el entorno aislado activo y UTF-8:

```text
uv pip install --python <venv>/Scripts/python.exe --only-binary=:all: --require-hashes -r security/requirements-ci.txt -r security/requirements-blood-gas-ci.txt
npm ci --no-audit --no-fund --prefix app
npm ci --ignore-scripts --no-audit --no-fund --prefix tools/blood-gas-ocr
python scripts/prepare_blood_gas_model.py
npm test --prefix app -- --maxWorkers=2
npm run lint --prefix app
npm run typecheck --prefix app
npm run build --prefix app
npm run guides:test --prefix app
npm run procedures:test --prefix app
npm run i18n:browser-check --prefix app
python clinical/scripts/normalize_evidence_sources.py --check
python clinical/scripts/build_project_graph.py --output <evidence>/project-graph.json
python clinical/qa/qa_runner.py
```

Para las pruebas OCR: BG_OCR_MODEL apunta al modelo local verificado, BG_TEST_FONT a clinical/assets/fonts/DejaVuSans.ttf y NODE_PATH a tools/blood-gas-ocr/node_modules. CHROMIUM_PATH apunta a Chrome local para el navegador. No se usan perfiles personales, cuentas, cookies ni datos de pacientes. Ver `LOCAL_REVIEW.md` para las capacidades nativas T05 Windows y T06 Linux, que no se sustituyen entre sí.

## Límites que permanecen

Los 19 contratos aceptados conservan 6 cálculos condicionados y13 orientaciones sin dosis automática; permanecen los controles reales de caso/producto. Los cuatro P1 tienen correcciones focales y límites en sus registros, sin un nuevo cierre global E1. Se conservan las decisiones posteriores y 118 GREEN/13 YELLOW; SCORE-REF no tiene aceptación global acreditada en esta base. QA técnico no resuelve una decisión médica pendiente.

La infraestructura multimodal es local y sintética: no añade inferencia clínica, rutas PWA, red ni entrenamiento. La separación lógica no implementa custodia/ACL independiente del examen. Codecs y temporales no tienen la contención nativa de T05/B1; no se habilitan archivos hostiles ni datos reales. FFmpeg/ffprobe locales y su procedencia/versiones constan en los anexos. No se ejecuta una demo adicional para obtener métricas.

No se activan proveedores públicos, búsquedas libres, RAG ni proxy global. El transporte B1 requiere Linux; una ejecución Windows no acredita su validación nativa. La revisión lingüística profesional, evaluación prospectiva y precisión multimodal no están establecidas por estos tests. CLINICALLY_PENDING permanece.

La decisión de publicación debe basarse en los anexos finales del árbol exacto y los bloqueos observados; este documento no es autorización de publicar, activar CI o modificar ramas protegidas.
