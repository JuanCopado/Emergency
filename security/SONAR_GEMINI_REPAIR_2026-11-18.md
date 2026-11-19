# Reparación de Sonar y auditoría Gemini — 18/11/2026

Base: `99b9a71fe132d92f8d5f93b2d605e9b2efc2e2a7`, rama internacional. Trabajo aislado; original, main, líneas cerradas y ZIP anteriores se conservan. Alcance técnico internacional, sin selección territorial ni cambios de aritmética, registros clínicos o validación.

## Problema y cambios

El análisis posterior a PR25 falló en Sonar: cobertura nueva72,8%, seguridadE, fiabilidadD. La PR había comparado otro alcance; su PASS no demostraba el gate de la rama. No se cambia la comparación, umbral, baseline, exclusiones ni configuración de Trivy.

- Excepciones JSON ordenadas, errores y logs HTTP sin reflejar datos privados; JSON mantiene valores Unicode/markup como datos con escapes JSON, CSP y nosniff.
- Exportadores eligen rutas constantes dentro de temporales privados; JSON de nota se serializa en memoria conservando su contenido y el gate de exportación.
- Vigilancia: destinos literales revisados, HTTPS con certificados verificados, sin redirects/proxy ambiental, DNS global y conexión a la IP validada con SNI del host original. Rechazo explícito de multicast/reservadas/IPv4 mapped privadas/IPv6 scoped. No se ha activado vigilancia ni contacto con fuentes clínicas para las pruebas.
- Capacidad de rutas para22 CLI: resolve y pertenencia a raíces confiables antes de E/S. El manifiesto de imagen también limita cada image_file a su raíz antes del decodificador. Los cálculos y reglas de clasificación permanecen intactos.
- QA usa comprobaciones explícitas que no desaparecen con Python-O. Parsers sin cuantificadores ambiguos; separadores Markdown limitados a32 espacios/tabuladores. Las200 cabeceras y proyección de ingredientes actuales conservan resultados.
- CI instala wheels con versiones/hashes; curl restringe HTTPS y redirects HTTPS. PTB-XL cuenta con lock transitivo propio incluido como quinto manifiesto obligatorio de Trivy. El primer lock detectó Pillow12.2.0 vulnerable; se conserva el resultado FAIL y se corrige con Pillow13.0.0 oficial, sin ignorarlo.
- La cobertura mide el QA unificado real y sus subprocesos, además de tests frontend/build y las capturas V8 de la mitigación existente. No hay cobertura fabricada ni fuentes nuevas excluidas. El constructor de guías incorpora --check para revisar sin escribir.

## Contrato CLI

El lanzador confiable elige `EMERGENCY_CLI_INPUT_ROOT` y `EMERGENCY_CLI_OUTPUT_ROOT`; cada una usa `EMERGENCY_CLI_ROOT` o cwd como respaldo. Se admite una ruta absoluta solo dentro de su raíz. Para datasets en otro disco, conceder la carpeta de lectura y una carpeta de salida separada; no conceder / o toda una unidad como atajo. Los registros internos predeterminados siguen siendo constantes del programa. Los argumentos no amplían las raíces.

Esto protege frente a control de argv y manifiestos, NO frente a quien pueda cambiar entorno/cwd, ejecutar shell, sustituir enlaces durante E/S o crear hard links dentro del árbol autorizado. ACL y aislamiento del lanzador siguen siendo necesarios en un puente remoto. Las API no aceptan rutas de archivos desde HTTP ni invocan los CLI. El helper no debe usarse como sustituto de autorización HTTP.

El servidor HTTP loopback se conserva para desarrollo/CI. Un bind de red exige --allow-network y ambos --tls-cert/--tls-key, TLS>=1.2. Esta entrega no expone el servidor ni lo convierte en servidor de producción con autenticación multiusuario.

## Auditoría externa real

Solicitada en la sesión Gemini del propietario: https://gemini.google.com/app/486e3e02340e34da?hl=es . Paquete revisado `3cc5f34e9a24c5fbe328849c8ac6788bfb1fccaafbd599ab5a948c3ba19afa58`,43 fuentes completas y diff públicos; sin PHI/credenciales.

Gemini revisó estáticamente, no ejecutó tests. Su primera lectura contenía errores de conteo y atribución; se corrigieron con el listado de74 incidencias. Su revisión del candidato incluyó un hallazgo ALTO de ruta derivada image_file, que se corrigió con rechazo antes de decodificación y regresiones sintéticas. La recomendación de rechazar todas las unidades Windows se acotó a rutas relativas a unidad: las absolutas autorizadas se conservan. La aprobación estática no equivale a cierre de CI. Falta su dictamen sobre el commit final y sus recibos.

## Evidencia y estado

Resultados parciales observados:453 frontend PASS,9 procedimientos PASS,4 guías PASS,15 pruebas de la mitigación PASS y fuzz acotado230/230 sondas PASS; actionlint/lint/typecheck/build PASS. QA unificado:7/7 controles PASS y848 Python PASS con1SKIP de creación de symlinks Windows. Se repite la captura del QA tras fijar cwd a la raíz del repositorio, para que los subprocesos generen rutas de cobertura coherentes sin aliases/exclusiones. Las pruebas nuevas verifican fronteras de red/E/S, nombres Windows,200 fichas, regeneración sin escritura y el banco público de1061 escenarios sintéticos con expectativas independientes.

Trivy local tras corregir Pillow: PASS,0 hallazgos,5 manifiestos. Se conservan las salidas FAIL previas. Sonar/CI del nuevo commit todavía pendientes: NO se declara resuelto el gate ni se integra hasta comprobarlo. No hay excepción de Trivy ni cambio de umbral de Sonar.

CLINICALLY_PENDING permanece. QA técnico y auditoría de IA no son revisión clínica independiente ni validación prospectiva.

### Primera CI de PR29 y repetición

En a5cf990: App UI QA, Trivy y Semgrep PASS; Clinical QA y cobertura fallaron en la prueba nueva por el SHA del registro al cambiar LF/CRLF. Se verifica ahora el hash real de la regeneración y que el histórico corresponde exactamente a LF o CRLF del mismo contenido; todos los demás campos se comparan íntegros. No se modifica el banco ni el registro. Se añaden pruebas offline de selección/hash/separación de etiquetas y render de una señal fabricada para el pipeline PTB-XL; sus wheels bloqueados son obligatorios en la captura Linux. Los hosts locales sin extras omiten esa clase expresamente; la CI falla si faltan los extras. Sonar todavía no ejecutado sobre el parche: no declarar PASS.

### Resultado de Sonar sobre5fb1878 y corrección siguiente

QA,AppUI,Trivy,Semgrep y captura de coberturaPASS. SonarPR29FAIL:fiabilidadA,seguridadE, cobertura nueva76,7%;3flujos de escritura pendientes en evidence_surveillance/urgent_safety_triage. Los destinos se validan ahora explícitamente a Path en main y los datos se pasan por parámetro data de write_text; se comprueban también ambos CLI por argv real, rechazando salida externa antes del procesamiento y manteniendo requires_human_review/auto_apply. Se publican4pruebas del controlador QA también verificadas bajoPython-O. El flujo de CI conserva análisis de rama yPR separados: antes la PR cancelaba la ejecución de rama, lo que no permitía verificar su alcance contra main antes de incorporar. Se mantienen los límites y el gateFAIL hasta nueva evidencia. Windows: una junction nativa probada bloqueó lectura/escritura externas sin alterar el testigo sintético.75ZIP y3176archivos de3candidatos verificados por hash sin diferencias.

### Análisis completo de rama18dc y validación explícita

La PR29 pasó Sonar con82,5% y seguridad/fiabilidadA; el análisis independiente de rama contra main falló:79,03%,31incidencias (28S8707,1S5131,2S8786). No se acepta el verde de PR como cierre. Se validan ahora todos los argumentos de rutas inmediatamente después de parse_args, incluido cada elemento nargs; los defaults internos permanecen constantes. Se añaden subprocess tests de cada argumento de22CLI (21 locales por ausencia de wfdb). Se sustituyen los dos parsers ambiguos restantes por análisis estructural/lineal y se neutraliza markup con html.escape y escapes Unicode JSON reversibles, probando entidades literales y contenido anidado.

Prueba local del delta: QA7/7PASS;863Python,7SKIP explícitos (6extras científicos no instalados y1symlink Windows); frontend460/460PASS, lint/typecheckPASS. Las6pruebas científicas sí se ejecutaron obligatoriamente en CI Linux anterior; Gemini no ejecutó pruebas. Las7pruebas nuevas de exportación usan notas sintéticas, verifican payload íntegro, revisión invalidada al editar y fallos sin descarga. Los resultados negativos anteriores se conservan. CI y dictamen Gemini del delta pendientes: no se integra todavía.
