# STATE â€” contratos revisados habilitados, 16/11/2026

- Directriz vigente: aceptaciÃ³n mÃ©dica del propietario y ejecuciÃ³n de lo ya revisado; ver `AGENTS.md`.
- Alcance: nÃºcleo internacional coherente, guÃ­as reconocidas y diferencias materiales; sin hospital obligatorio.
- Base inspeccionada: `062d890b4fc92369b83c87664bb4bb0205ccb33f`, rama internacional con ceftriaxona e INT-02A.
- Rama de entrega: `codex/v144-reviewed-contracts-enable-20261116`.
- GMA-P2-004: 19 bloqueos permanentes sustituidos por 6 contratos capaces de cÃ¡lculo y 13 de apoyo de decisiÃ³n.
- CatÃ¡logo:46 IDs conservados,0 block_reason; controles reales de caso/producto permanecen.
- AceptaciÃ³n: `clinical/references/acute-contract-owner-acceptance-2026-11-16.json`; no volver a pedirla.
- Estatus: carga inicial adulta de fenitoÃ­na con modos dosis/preparaciÃ³n; refractario con EEG, escalada y traslado.
- Anafilaxia: IM ponderal <6 meses y perfusiÃ³n refractaria; intervalos <5 min dan orientaciÃ³n sin dosis automÃ¡tica.
- ReversiÃ³n:15 rutas; productos/tablas y contextos de hemorragia diferenciados segÃºn fuentes primarias.
- GMA-P2-001: corregido overflow/underflow en doseToRate/rateToDose;9 regresiones nuevas.
- Correcciones relacionadas: riesgo IM sin contraindicaciÃ³n absoluta ficticia; enoxaparinaâ‰¤8/>8 h y lÃ­mite de cada administraciÃ³n lenta de protamina.
- Cuatro etiquetas de guÃ­as sincronizadas con GREEN ya aceptado14/11:vasoactivos,sedaciÃ³n UCI,ambulatorio pediÃ¡trico,marco POCUS.
- Registro de evidencia conservado:131 mÃ³dulos,117 GREEN/14 YELLOW/0 RED; sin nueva promociÃ³n automÃ¡tica.
- QA local:812 pruebas Python y7/7 controles globales PASS;445 frontend,4 guÃ­as,9 procedimientos PASS.
- Typecheck,lint,build,catÃ¡logo normalizado y grafo PASS;61 casos nominales/46 IDs PASS.
- Navegador local:BLOCKED_ENVIRONMENT por socket EPERM antes de abrir pÃ¡gina;0 casos, sin PASS ficticio.
- Navegador real en GitHub: 21/21 casos, 19/19 contratos, JSON/PDF/DOCX/impresiÃ³n y controles negativos PASS.
- Clinical QA, App UI QA y Evidence surveillance guardrails PASS en push y PR #20.
- GMA-P2-004 y GMA-P2-001 resueltos dentro del alcance documentado; los demÃ¡s hallazgos conservan su estado.
- PublicaciÃ³n verificada: PR #20, commit de implementaciÃ³n `04c52c91cb5c07c5cbcaadcf9b2f9e519b1b4e22`; integraciÃ³n trazada en https://github.com/JuanCopado/Emergency/pull/20.
- Matriz/evidencia: `clinical/qa/REVIEWED_ACUTE_CONTRACT_RELEASE_2026-11-16.md` y JSON asociado.
- Fuentes/evidencia/firma tÃ©cnica diferenciadas; no se inventa firma independiente de Farmacia ni validaciÃ³n prospectiva.
- CLINICALLY_PENDING global; no se declaran cerrados otros P1/P2, stock internacional ni instalaciÃ³n en el PC.
- Proteger main y lÃ­neas cerradas RC1/v1.43; no afirmar integraciÃ³n por publicar una rama.
- Los documentos anteriores que conservaban19 bloqueos describen sus cortes histÃ³ricos y quedan superados en este alcance.

## ContinuaciÃ³n de seguridad PR22 â€” 17/11/2026, copia aislada

- Propuesta completa de dependencias aplicada sobre793d674911b8bd1af7285b4fc45c37f95c2a2666 en una nueva copia local. No se incorporan deltas clÃ­nicos/UI/PDF de Q5 ni se cambia PR22 remoto.
- Trivy0.76.2 real, misma base de vulnerabilidades: original50 registros/19 bloqueantes; copia integrada13 inferiores/0 bloqueantes, gate localPASS sin supresiÃ³n.
- npm audit:0 HIGH/CRITICAL,17 MODERATE y1 LOW pendientes.812 Python,445 frontend y4 pruebas del informePASS; build/typecheck/lint/pip checkPASS.
- Sonar y Semgrep no ejecutados de nuevo sobre este Ã¡rbol; los gates remotos anteriores conservan su estado. Sin commit/push/merge/despliegue; original y ZIPs Q5 preservados.
- Detalle de versiones, alcance y lÃ­mites: security/PR22_LOCAL_DEPENDENCY_INTEGRATION_2026-11-17.md. CLINICALLY_PENDING conservado, sin cambios de cÃ¡lculos o contenido clÃ­nico.

## ContinuaciÃ³n local seguridad â€” 18/11/2026

- Nueva copia desde0858e29â€¦; correcciones dirigidas de avisos inferiores y rutas CLI del informe. CÃ³digo/cÃ¡lculos/contenido clÃ­nico intactos; CLINICALLY_PENDING.
- Cobertura real XML/LCOV generada:812 Python,445 frontend y8 del informePASS; build/typecheck/lint/pip check/actionlintPASS. Python76,95% y frontend71,11% de lÃ­neas; no se declara gate Sonar80%PASS.
- Con base Trivy actual, la copia anterior tiene2HIGH+13inferiores y la nueva2HIGH+0inferiores. Son dos registros del mismo picomatch/CVE-2026-112366 sin versiÃ³n oficial corregida. npm conserva25 paquetesHIGH por ese Ãºnico advisory;0moderados/bajos. Gate de dependenciasFAIL conservado.
- Workflow preparado para cobertura medida antes de Sonar, acciones fijadas y clasificador por stdin/stdout sin rutas arbitrarias. No hay anÃ¡lisis remoto nuevo, supresiÃ³n, publicaciÃ³n o cambios a PR22 remoto.
- Estado vigente y lÃ­mites: security/PR22_SECURITY_CONTINUATION_2026-11-18.md. Documentos del17/11 conservan su contexto histÃ³rico.


## 18/11/2026 — evaluación local de mitigación temporal de picomatch

Copia aislada derivada de `af87ff815665884103689c771ac0807b751a5883`; no publicada ni integrada en PR22/PR23. Ver `security/PICOMATCH_TEMPORARY_MITIGATION_2026-11-18.md`. Defensa conservadora por rechazo de extglobs repetidos, con control de hashes en cinco copias de picomatch. Pruebas específicas 6/6, 1.800 rechazos esperados, 18.000 comparaciones habituales idénticas, frontend 445/445, lint y build PASS; los 26 archivos compilados son idénticos a la base. Lock y política Trivy conservados; el CVE mantiene su condición pendiente y no se acepta una excepción por la mitigación. No se atribuye el Sonar anterior a este árbol. Sin cambios de cálculos, fuentes o contenido clínico; `CLINICALLY_PENDING` conservado. Candidato original y entregas anteriores conservados.


## 18/11/2026 — PM-02: propuesta de comprobación de instalaciones limpias

Nueva copia aislada desde el árbol mitigado `4a6e5114c65a48d3611bc172c203aa535752b303`, con base Git `af87ff815665884103689c771ac0807b751a5883`. Se prepara una matriz de instalación automática y con scripts desactivados en Windows y Linux, usando el lock sin cambios. El comprobador exige error visible si falta la defensa y verifica sus cinco copias y la idempotencia. Los resultados observados de cada ejecución se registrarán externamente; preparar la matriz no significa que ya haya pasado. Trivy y sus cuatro manifiestos/umbrales permanecen intactos; los dos HIGH conocidos siguen pendientes. No se modifica PR22, PR23, el candidato original, los ZIP anteriores, los cálculos o el contenido clínico. Se conserva CLINICALLY_PENDING.


### PM-02 — corrección de hallazgos de la primera CI

La primera matriz remota aprobó los cuatro casos y Trivy conservó dos HIGH. Sonar señaló bootstrap npm bajo demanda, comparadores de ordenación, aserciones de preparación y cobertura ausente del proceso separado. Se corrige la propuesta usando el npm del runner, comparadores explícitos y before de node:test. Se amplían a nueve pruebas reales de errores de argumentos/inventario y reversión ante escritura fallida o corrupta. La cobertura de procesos separados se mide con NODE_V8_COVERAGE y las bibliotecas ya fijadas por Vitest y se incorpora al LCOV sin cambiar exclusiones, umbrales ni otros registros. Medición local: 100% líneas, 91,22% ramas del aplicador. Nueva CI pendiente de resultado externo sobre el árbol revisado; no se afirma aprobación por preparar esta corrección. Fuentes clínicas, app/src, lock y política de Trivy intactos.


### PM-02 — instalación CI con scripts de dependencias desactivados

La segunda matriz aprobó los cuatro casos y la cobertura nueva Sonar subió a 97,2%; fiabilidad y mantenibilidad A. Quedó un aviso de seguridad por permitir lifecycle scripts en npm ci. Se ajusta CI para instalar siempre con --ignore-scripts y, en el caso postinstall, ejecutar únicamente el hook conocido del proyecto mediante npm run postinstall --ignore-scripts. El autoenganche de npm ci ya se comprobó localmente y en las matrices anteriores; esta revisión no afirma ejecutarlo automáticamente en CI. El caso explícito mantiene su comprobación de ausencia y bloqueo previo. No se descarta el hallazgo: se elimina la ejecución amplia de scripts que lo originó. La nueva revisión queda pendiente de su resultado remoto. Trivy continúa bloqueando y no cambian fuentes clínicas, lock o cálculos.
