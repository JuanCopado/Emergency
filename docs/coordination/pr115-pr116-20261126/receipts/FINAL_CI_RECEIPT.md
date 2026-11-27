# Recibo CI · PR115 / PR116

Estado técnico de la CI del candidato: **PASS**. CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE.

## Identidad exacta

- Candidato aislado PR118: `b9f8d14fc1439a293f786e7b8353a9923a0f1156`.
- Árbol: `20e98a131f96549c50497c1ad95511fb2f240586`.
- Checkout de merge de CI: `3f491988a54a318f977019cf873b9fac3d768e41`; mismo árbol comprobado.
- PR116 corregida y conciliada: `50462b00a4c0af30889f8600be95aedd69d6c293`.
- PR115 original conservada: `82278d37dc29fe49e6afbc8db7aafe8d7e4166c1`.
- Receptor actual leído: `570aa11bfe5c9df1c4a571f1103c28030d5731ca`. Su avance PR117 fue externo; este trabajo no escribió en la rama protegida.

## Workflows del candidato

| Workflow | Resultado | Evidencia |
|---|---|---|
| Clinical QA | success | [run 45916308017](https://github.com/JuanCopado/Emergency/actions/runs/45916308017) |
| App UI QA | success | [run 45916308174](https://github.com/JuanCopado/Emergency/actions/runs/45916308174) |
| Picomatch clean installation | success | [run 45916308153](https://github.com/JuanCopado/Emergency/actions/runs/45916308153) |
| Security and quality | success | [run 45916308073](https://github.com/JuanCopado/Emergency/actions/runs/45916308073) |

Los jobs y pasos exactos constan en `CI_JOBS.json`; los metadatos y límites de procedencia, en `FINAL_RECEIPT.json`.

## Pruebas observadas

Clinical QA: 1.747 pruebas, 20 omitidas, cero fallos y siete gates PASS. App UI: 1.118 pruebas frontend PASS. Los 16 casos API/UI/JSON, los PDF/Word reales y la revisión terapéutica adulto/lactante conservan las expectativas originales y bloquean versiones editadas. Navegación: 113 estados, nueve de historial, once negativos y 514 enlaces. Los 15 hashes de fuente vigilados coinciden con el candidato.

Picomatch conserva las seis combinaciones Linux/Windows y sus guardas. T05 Windows, T06 Linux, Semgrep, Trivy, cobertura real y Sonar se acreditan por sus resultados propios; no se atribuyen resultados de otros SHA al candidato. Sonar final: quality gate PASSED, cero incidencias nuevas/aceptadas, cero riesgos nuevos de dependencias, duplicación nueva 0,0 % y cobertura nueva 90,3 %. PR116: cuatro workflows SUCCESS, Sonar PASSED y cobertura nueva 90,2 %.

## Correcciones y preservación

Se conservan los FAIL iniciales de los runs 45907530763, 45907530781 y 45907530903; el fallo Windows de 45909319401; y los quality gates fallidos de 45910128972 y 45910309712. La cancelación de un job inicial no se cuenta como PASS ni se atribuye a fail-fast: ese workflow tenía fail-fast=false.

Causas corregidas: contrato de ruta ausente; fixtures que confundían booleano con revisión terapéutica; huella alterada por CRLF Windows; y diccionarios localizados interpretados como código repetido, más cinco hallazgos concretos de fiabilidad. Los recursos localizados mantienen todos sus valores en cuatro idiomas. La ordenación explícita conserva el orden UTF-16 anterior. No se cambiaron umbrales, exclusiones, expectativas clínicas, dosis o controles médicos.

PR111 no se reaplica. PR112/113 conservan sus archivos; PR114 mantiene transporte y procedencia T06. Trece destinos PR117 coinciden exactamente con el receptor actual. Los seis archivos de expectativas/aceptación auditados son byte-idénticos a la base. Véase `COMPOSITION_PROOF.json`.

## Límites y entrega

Las referencias de ZIP y sus digests, si constan, son metadatos declarados por GitHub. Su recuperación local desde los hosts del servicio de archivos fue bloqueada por proxy 403; no se atribuye lectura o verificación local del ZIP. La evidencia de ejecución procede de logs decodificados del conector y de los archivos locales conservados. El recorrido remoto declara dirty=true tras generar evidencias; su árbol y sus hashes se comprueban. El recorrido local final parte del SHA exacto limpio.

El propietario autorizó dejar paquete y orden para recogida por Antigravity: [orden vigente](https://github.com/JuanCopado/Emergency/pull/118#issuecomment-7205465110). Recepción y dictamen externo pendientes. Las revisiones técnicas internas no los sustituyen. GMA-P1-003 permanece abierto y los 19 contratos aceptados siguen vigentes. Sin merge ni despliegue.

PR116 conserva un diagnóstico heredado de Protobuf/UTF-8 en Sonar aunque su quality gate pasa. El candidato integrado contiene la corrección y procedencia PR114; ese diagnóstico no se reproduce en su job Sonar final. Un gate PASS no se presenta como prueba de ausencia universal de diagnósticos.
