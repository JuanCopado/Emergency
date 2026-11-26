# R5-1 / R5-2 / G05 · cierre funcional acotado

Base internacional: `228cd21d75d14e1012beb7f5dfe82c2c920c4ccc`, confirmada el 26/11/2026. Rama aislada `fix/r5-g05-functional-20261126`. Alcance internacional, datos sintéticos, sin cambio de algoritmos, dosis, fórmulas ni contratos médicos.

## Incidencia reproducida y corregida

El cliente compartido de nota clínica capturaba cualquier error de `response.json()` y lo convertía en un objeto resuelto. Tras HTTP 200, un cuerpo JSON inválido, un corte durante la lectura o la cancelación por timeout se devolvían como respuesta válida al consumidor. No se demostró una aceptación clínica consumada: el defecto comprobado es la resolución incorrecta de la promesa y pérdida de la clasificación del error.

`app/src/clinical-note/api.ts` rechaza ahora esos fallos. Los de red y timeout conservan `ClinicalApiConnectionError`; un fallo de parseo produce un mensaje técnico fijo sin reflejar el cuerpo. No hay reintento automático. Se conservan 60 s para llamadas deterministas y 200 s para proveedor. Las negativas HTTP con JSON válido conservan su error.

Tres regresiones nuevas fallaron antes del cambio; después pasan. La suite focal React de conexión, fallo de interpretación, aceptación y exportación: **25 pruebas PASS**, incluidas las tres nuevas. Python: **20 pruebas de nota/procedencia/HTTP PASS** y **96 M10 PASS**, sin proveedor externo.

Los logs iniciales también conservan dos dificultades del entorno: la mitigación Picomatch rechaza un `node_modules` de tipo junction, por lo que se copió la instalación existente a una carpeta ordinaria; Vitest necesitó el nombre físico C: de este espacio D: mapeado. No se cambiaron guardas para eludirlas ni se modificó la instalación original.

## Conciliación de trabajo integrado

PR108 fusionada en `f67523e2838ab057b50218dde0a3eaa9709247c8`: navegación, identidad de rutas y Atrás/Adelante pediátrico. PR109 fusionada en `a3b05dee88e43e9cf51e81054e4b0fbd5eeec69d`: registro de integración R96 y C12. PR110 fusionada en la base actual: CLI intake y candidato S1-01. Metadatos consultados de nuevo; no se vuelven a implementar esos deltas.

La revisión independiente Antigravity postmerge de PR110 confirma integración técnica y conserva un límite sobre Protobuf/Sonar. El log real del job `139852866904` contiene el error de UTF-8 de Protobuf, seguido de 193/193 fuentes JS/TS analizadas y Quality Gate PASSED. Estos contadores no permiten demostrar ausencia de impacto en consumidores AST ni identificar el archivo. No se declara resuelto por ver un gate verde. No se alteran exclusiones, reglas o umbrales de Sonar para ocultarlo.

## Requisitos y bloqueos reales

`G05_REQUISITOS.json` desglosa los seis requisitos R88, conserva la evidencia exigida y asigna estado, evidencia disponible, acción y autoridad de aceptación. La definición completa procede de los expedientes G05/R6, RELEASE_GATES y R88; G05 global sigue BLOCKED.

- R5-1: modalidad real de una foto no demostrable por nombre/selector. Política aprobada, prototipos inactivos y laboratorio no equivalen a seguridad clínica validada. Banco canónico 10/30, veinte posiciones pendientes, cero adjudicaciones individuales; PR113 mantiene un candidato recibido fuera del manifiesto. Faltan banco admisible y firmado, dos notas ≥4, referencias 16/NA14, institución/consentimiento, participantes y datos prospectivos. No se repiten MED-DEC-R46-01/02 ni otras aceptaciones vigentes. Etapa 2 depende de resultados de Etapa 1.
- R5-2: corpus textual ciego independiente del equipo que conoce el filtro, cuatro lenguas × siete clases, custodio, tamaño de celdas y umbral preespecificados, dos adjudicadores por lengua y tercero dirimente. El banco de imágenes de 30 posiciones no sustituye este corpus. Los casos R8 son regresiones de desarrollo, no validación independiente. No se amplía el léxico ni se infieren decisiones por los resultados sintéticos.
- G05: laboratorio Q4/R6/B1 local no habilita proveedor público ni RAG. Faltan alcance público y derechos por campo/uso, licencia del código propio, privacidad y auditoría del mismo candidato; PTBR-PIX conserva contrato literal y aprobación específicos pendientes. T05 exige Windows, T06 Linux; no se declara plataforma única certificada.
- Nota clínica: prioridad diagnóstica no equivale a diagnóstico confirmado; la extensión silenciosa R5 conserva sus límites y requiere el circuito independiente correspondiente.
- C12: se conserva el ruleset y sus seis checks de la auditoría PR110. El PASS del commit base no se atribuye al candidato nuevo. No se cambia protección ni se realiza merge.

## Verificación y dictamen

El recibo externo de entrega identifica el SHA publicado y resultados posteriores de build, tipos, lint, navegador, PDF, accesibilidad y CI. Los resultados que aún no se hayan observado se registran PENDING/NOT_EXECUTED, nunca PASS. T05 Windows y T06 Linux, Semgrep, Trivy y Sonar deben consultarse en las ejecuciones del candidato exacto.

Auditoría independiente del nuevo delta pendiente antes de integración. El propietario conserva exclusivamente la decisión clínica final; Farmacia puede asesorar sin constituir firma obligatoria. No hay una nueva decisión clínica sustantiva en este parche de transporte que requiera pregunta SÍ/NO.

**NO-GO para cierre global R5/G05 o liberación clínica.** El delta de manejo de errores es una corrección técnica preparada para QA y revisión independiente. `CLINICALLY_PENDING` · `NO_GO_CLINICAL_RELEASE`.
