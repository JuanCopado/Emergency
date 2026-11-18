# Incorporación de seguridad al proyecto — 18/11/2026

El propietario autorizó incorporar el arreglo después de resolverse el bloqueo. Destino: `codex/v144-international-scope-20261116`, base `1d0652ebcef9b5990edd9e5745b0c06f8d6b8274`. No se modifica main ni las líneas cerradas.

Se combinan la PR25 actual (`fc1c0cf87e45ee8d5ecf193b571f6f864955613e`, Trivy/Sonar PASS) y la ampliación de PR26 (`5e37949e7702f33648fa30979a3dd0fd828f1fbd`). Se conserva el origen oficial GHCR de la DB Trivy y su metadato, las acciones fijadas, el texto UTF-8 reparado y los 18 hooks de producto. No se relajan avisos, severidades, exclusiones, umbrales ni objetivos de análisis.

La defensa conjunta cubre cinco copias independientes de picomatch y seis parsers de los cuatro bundles Rollup (14 archivos), permite repeticiones legítimas revisadas, restringe regex cruda y verifica el presupuesto de trabajo. Las escrituras usan temporales propios exclusivos, fsync, verificación antes y después de rename, bloqueo y diario con recuperación hacia delante. Una colisión nunca elimina el temporal ajeno. Pruebas mutantes solo en fixtures privados; comprobación de cobertura ligada a fuentes y fuzz limitado por proceso. La matriz Windows/Linux conserva el hook revisado, la aplicación explícita y la instalación automática completa en carpeta independiente con scripts de instalación revisados.

La PR26 se valida contra la PR25 actual; después se incorpora en PR25 y esta en la rama internacional. La identidad final y los resultados se acreditan con los commits reales de merge y sus ejecuciones de CI, no por publicar una rama. Se conservan candidatos y ZIP anteriores.

Los informes anteriores describen su revisión y fecha. Los dos HIGH históricos no se reetiquetan como PASS: la DB oficial posterior retiró los registros. El guard sigue siendo una mitigación temporal, no un arreglo universal del lenguaje glob. Son aplicables los límites de `PM03_AUDIT_FIX_2026-11-18.md`, salvo el bloqueo Trivy histórico ya superado en la revisión fc1c0cf.

Fuentes clínicas, app/src, lock, datos y estados clínicos se conservan respecto a la PR25 recibida. La configuración de pruebas clínicas incorporada por la cadena de seguridad es infraestructura de QA, no una modificación clínica. CLINICALLY_PENDING no se promueve. No se declara despliegue.
