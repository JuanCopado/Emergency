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

## Contención de picomatch verificada — 18/11/2026

- Mitigación aceptada por el propietario y añadida a PR24 sobre ce808a63; código final comprobado010f12c01fde4a4058d2e856b5033373752db536.
- El build exige picomatch dev-only y rechaza su inclusión en la aplicación; CI también revisa el service worker y Workbox mediante mapas generados.
- Resultado:119 módulos de aplicación y44 entradas de fuente en2 mapas, sin picomatch. App UI QA, lint/typecheck/build, navegación/exportaciones,469 pruebas Vitest y827 PythonPASS;22 controles locales comparten casos con la nueva suite, no se suman como pruebas únicas.
- Semgrep y SonarPASS. Trivy termina el análisis y conservaFAIL con2 registros de la vulnerabilidad upstream, sin excepción, supresión ni cambio de umbral.
- Checkout de App UI QA fijado y sin credenciales persistidas; npm sin lifecycle scripts. Runner efímero, con red disponible; no se afirma aislamiento de red.
- Dependencias bloqueadas, clínica, fórmulas, contratos y estados conservados respecto a la base de esta tarea. CLINICALLY_PENDING; sin merge, despliegue ni cierre del advisory.
- Evidencia y límites: security/PICOMATCH_CONTAINMENT_2026-11-18.md y ejecuciones44318600953/44318600927/44318600973. Las últimas modificaciones posteriores al código comprobado son solo documentales.
