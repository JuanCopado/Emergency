# STATE — contratos revisados habilitados, 16/11/2026

- Directriz vigente: aceptación médica del propietario y ejecución de lo ya revisado; ver `AGENTS.md`.
- Alcance: núcleo internacional coherente, guías reconocidas y diferencias materiales; sin hospital obligatorio.
- Base inspeccionada: `062d890b4fc92369b83c87664bb4bb0205ccb33f`, rama internacional con ceftriaxona e INT-02A.
- Rama de entrega: `codex/v144-reviewed-contracts-enable-20261116`.
- GMA-P2-004: 19 bloqueos permanentes sustituidos por 6 contratos capaces de cálculo y 13 de apoyo de decisión.
- Catálogo:46 IDs conservados,0 block_reason; controles reales de caso/producto permanecen.
- Aceptación: `clinical/references/acute-contract-owner-acceptance-2026-11-16.json`; no volver a pedirla.
- Estatus: carga inicial adulta de fenitoína con modos dosis/preparación; refractario con EEG, escalada y traslado.
- Anafilaxia: IM ponderal <6 meses y perfusión refractaria; intervalos <5 min dan orientación sin dosis automática.
- Reversión:15 rutas; productos/tablas y contextos de hemorragia diferenciados según fuentes primarias.
- GMA-P2-001: corregido overflow/underflow en doseToRate/rateToDose;9 regresiones nuevas.
- Correcciones relacionadas: riesgo IM sin contraindicación absoluta ficticia; enoxaparina≤8/>8 h y límite de cada administración lenta de protamina.
- Cuatro etiquetas de guías sincronizadas con GREEN ya aceptado14/11:vasoactivos,sedación UCI,ambulatorio pediátrico,marco POCUS.
- Registro de evidencia conservado:131 módulos,117 GREEN/14 YELLOW/0 RED; sin nueva promoción automática.
- QA local:812 pruebas Python y7/7 controles globales PASS;445 frontend,4 guías,9 procedimientos PASS.
- Typecheck,lint,build,catálogo normalizado y grafo PASS;61 casos nominales/46 IDs PASS.
- Navegador local:BLOCKED_ENVIRONMENT por socket EPERM antes de abrir página;0 casos, sin PASS ficticio.
- Navegador real en GitHub: 21/21 casos, 19/19 contratos, JSON/PDF/DOCX/impresión y controles negativos PASS.
- Clinical QA, App UI QA y Evidence surveillance guardrails PASS en push y PR #20.
- GMA-P2-004 y GMA-P2-001 resueltos dentro del alcance documentado; los demás hallazgos conservan su estado.
- Publicación verificada: PR #20, commit de implementación `04c52c91cb5c07c5cbcaadcf9b2f9e519b1b4e22`; integración trazada en https://github.com/JuanCopado/Emergency/pull/20.
- Matriz/evidencia: `clinical/qa/REVIEWED_ACUTE_CONTRACT_RELEASE_2026-11-16.md` y JSON asociado.
- Fuentes/evidencia/firma técnica diferenciadas; no se inventa firma independiente de Farmacia ni validación prospectiva.
- CLINICALLY_PENDING global; no se declaran cerrados otros P1/P2, stock internacional ni instalación en el PC.
- Proteger main y líneas cerradas RC1/v1.43; no afirmar integración por publicar una rama.
- Los documentos anteriores que conservaban19 bloqueos describen sus cortes históricos y quedan superados en este alcance.

## Continuación de seguridad PR22 — 17/11/2026, copia aislada

- Propuesta completa de dependencias aplicada sobre793d674911b8bd1af7285b4fc45c37f95c2a2666 en una nueva copia local. No se incorporan deltas clínicos/UI/PDF de Q5 ni se cambia PR22 remoto.
- Trivy0.76.2 real, misma base de vulnerabilidades: original50 registros/19 bloqueantes; copia integrada13 inferiores/0 bloqueantes, gate localPASS sin supresión.
- npm audit:0 HIGH/CRITICAL,17 MODERATE y1 LOW pendientes.812 Python,445 frontend y4 pruebas del informePASS; build/typecheck/lint/pip checkPASS.
- Sonar y Semgrep no ejecutados de nuevo sobre este árbol; los gates remotos anteriores conservan su estado. Sin commit/push/merge/despliegue; original y ZIPs Q5 preservados.
- Detalle de versiones, alcance y límites: security/PR22_LOCAL_DEPENDENCY_INTEGRATION_2026-11-17.md. CLINICALLY_PENDING conservado, sin cambios de cálculos o contenido clínico.

## Continuación local seguridad — 18/11/2026

- Nueva copia desde0858e29…; correcciones dirigidas de avisos inferiores y rutas CLI del informe. Código/cálculos/contenido clínico intactos; CLINICALLY_PENDING.
- Cobertura real XML/LCOV generada:812 Python,445 frontend y8 del informePASS; build/typecheck/lint/pip check/actionlintPASS. Python76,95% y frontend71,11% de líneas; no se declara gate Sonar80%PASS.
- Con base Trivy actual, la copia anterior tiene2HIGH+13inferiores y la nueva2HIGH+0inferiores. Son dos registros del mismo picomatch/CVE-2026-112366 sin versión oficial corregida. npm conserva25 paquetesHIGH por ese único advisory;0moderados/bajos. Gate de dependenciasFAIL conservado.
- Workflow preparado para cobertura medida antes de Sonar, acciones fijadas y clasificador por stdin/stdout sin rutas arbitrarias. No hay análisis remoto nuevo, supresión, publicación o cambios a PR22 remoto.
- Estado vigente y límites: security/PR22_SECURITY_CONTINUATION_2026-11-18.md. Documentos del17/11 conservan su contexto histórico.


## 18/11/2026 — evaluación local de mitigación temporal de picomatch

Copia aislada derivada de `af87ff815665884103689c771ac0807b751a5883`; no publicada ni integrada en PR22/PR23. Ver `security/PICOMATCH_TEMPORARY_MITIGATION_2026-11-18.md`. Defensa conservadora por rechazo de extglobs repetidos, con control de hashes en cinco copias de picomatch. Pruebas específicas 6/6, 1.800 rechazos esperados, 18.000 comparaciones habituales idénticas, frontend 445/445, lint y build PASS; los 26 archivos compilados son idénticos a la base. Lock y política Trivy conservados; el CVE mantiene su condición pendiente y no se acepta una excepción por la mitigación. No se atribuye el Sonar anterior a este árbol. Sin cambios de cálculos, fuentes o contenido clínico; `CLINICALLY_PENDING` conservado. Candidato original y entregas anteriores conservados.


## 18/11/2026 — PM-02: propuesta de comprobación de instalaciones limpias

Nueva copia aislada desde el árbol mitigado `4a6e5114c65a48d3611bc172c203aa535752b303`, con base Git `af87ff815665884103689c771ac0807b751a5883`. Se prepara una matriz de instalación automática y con scripts desactivados en Windows y Linux, usando el lock sin cambios. El comprobador exige error visible si falta la defensa y verifica sus cinco copias y la idempotencia. Los resultados observados de cada ejecución se registrarán externamente; preparar la matriz no significa que ya haya pasado. Trivy y sus cuatro manifiestos/umbrales permanecen intactos; los dos HIGH conocidos siguen pendientes. No se modifica PR22, PR23, el candidato original, los ZIP anteriores, los cálculos o el contenido clínico. Se conserva CLINICALLY_PENDING.


### PM-02 — corrección de hallazgos de la primera CI

La primera matriz remota aprobó los cuatro casos y Trivy conservó dos HIGH. Sonar señaló bootstrap npm bajo demanda, comparadores de ordenación, aserciones de preparación y cobertura ausente del proceso separado. Se corrige la propuesta usando el npm del runner, comparadores explícitos y before de node:test. Se amplían a nueve pruebas reales de errores de argumentos/inventario y reversión ante escritura fallida o corrupta. La cobertura de procesos separados se mide con NODE_V8_COVERAGE y las bibliotecas ya fijadas por Vitest y se incorpora al LCOV sin cambiar exclusiones, umbrales ni otros registros. Medición local: 100% líneas, 91,22% ramas del aplicador. Nueva CI pendiente de resultado externo sobre el árbol revisado; no se afirma aprobación por preparar esta corrección. Fuentes clínicas, app/src, lock y política de Trivy intactos.


### PM-02 — instalación CI con scripts de dependencias desactivados

La segunda matriz aprobó los cuatro casos y la cobertura nueva Sonar subió a 97,2%; fiabilidad y mantenibilidad A. Quedó un aviso de seguridad por permitir lifecycle scripts en npm ci. Se ajusta CI para instalar siempre con --ignore-scripts y, en el caso postinstall, ejecutar únicamente el hook conocido del proyecto mediante npm run postinstall --ignore-scripts. El autoenganche de npm ci ya se comprobó localmente y en las matrices anteriores; esta revisión no afirma ejecutarlo automáticamente en CI. El caso explícito mantiene su comprobación de ausencia y bloqueo previo. No se descarta el hallazgo: se elimina la ejecución amplia de scripts que lo originó. La nueva revisión queda pendiente de su resultado remoto. Trivy continúa bloqueando y no cambian fuentes clínicas, lock o cálculos.

### PM-03 — corrección de auditoría, 18/11/2026

Copia aislada desde `fba27dcc898b6b42893f46823efd3f8385a06432`. App UI instala sin scripts de terceros; reemplazo atómico de parsers con rollback individual; 18 comandos de producto protegidos; prueba de junction Windows sin omisión y mojibake histórico reparado. Controlador 11/11, frontend 445/445, clasificador 8/8, lint y build PASS locales. Matriz Windows/Linux 4/4, App UI/navegador/PDF, Clinical QA, Semgrep, cobertura y Sonar PASS sobre las implementaciones verificadas; Sonar 97,4% de cobertura nueva y cero issues. Límites de regex y picomatch embebido en Rollup documentados, sin entradas externas convertidas en patrones. GitHub retiró GHSA-fc5q-39xc-vjpf a las 15:38:56 UTC; npm audit devuelve 0 vulnerabilidades. Trivy con DB anterior bloqueó dos HIGH; se esperó a la publicación oficial de la DB de las 19:07:09 UTC y el escaneo completo devuelve PASS local, cero hallazgos y cuatro manifiestos. La CI que aún recibía el mirror antiguo pasa a consultar el origen oficial GHCR y publicar fecha/versión de DB. Política, manifiestos, clasificador y umbrales intactos; los resultados remotos finales se identifican en la entrega. Ver `security/PICOMATCH_PM03_SECURITY_2026-11-18.md`. Fuentes clínicas, app/src y lock preservados; `CLINICALLY_PENDING`, ramas protegidas intactas y sin despliegue.


## 18/11/2026 — incorporación autorizada de las correcciones de seguridad

El propietario pide incorporar el arreglo al proyecto tras la resolución real del bloqueo. La revisión recibida de PR25, `fc1c0cf87e45ee8d5ecf193b571f6f864955613e`, tiene matriz, App UI, Clinical QA, Trivy y Sonar PASS. Se combina con PR26 para conservar también la defensa de Rollup, el fuzz acotado y la procedencia de cobertura, manteniendo los 18 hooks y el origen oficial de la DB. Detalle y secuencia: `security/INTEGRACION_SEGURIDAD_2026-11-18.md`. Los resultados e identidad de la incorporación se acreditan con el SHA y los runs de las PR25/26. Los informes de bloqueos anteriores conservan su fecha histórica. Sin cambios de cálculos, contenido o validación clínica; CLINICALLY_PENDING. Main y las líneas cerradas permanecen protegidas; esto no declara un despliegue.
