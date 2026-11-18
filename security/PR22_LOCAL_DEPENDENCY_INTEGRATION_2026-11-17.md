# PR22 — propuesta completa integrada y comprobada localmente

17/11/2026. Base exacta PR22: commit793d674911b8bd1af7285b4fc45c37f95c2a2666, árbol345b62967f86f086b655c673dc571fff062a1e4c. Copia aislada nueva; el candidato original y la entrega Q5 no se editan. CLINICALLY_PENDING se conserva. No hay commit, push, merge o despliegue; integrado aquí significa aplicado y probado en esta copia, no publicado en GitHub.

## Cambios y adaptación

- app/package.json y lock: Vite6.4.4, Vitest4.1.11, overrides source-map-js1.2.2/undici8.12.2; Zod4.6.6 fijado en lock dentro del rango original.
- clinical/requirements-test.txt: pypdf6.21.4; reportlab5.0.1 runtime, PyYAML6.0.3 y jsonschema4.25.1 conservados.
- app/vite.config.ts: fs.strict=true; allow app en desarrollo y app+clinical/modules solo en test. No se abre todo el workspace.
- Se conservan los scripts npm y las tres rutas proxy originales de PR22: no se importan el script i18n ni el proxy agudo añadidos después en Q5. No se incorporan cambios clínicos, de interfaz o de impresión de otra línea.
- STATE.md y este documento registran el estado técnico. No se renuevan revisiones de evidencia ni estados clínicos.

Las versiones provienen de la propuesta completa verificada con registro oficial npm/PyPI. Se aplicó el cambio compatible sobre PR22, revisando las diferencias reales entre bases en vez de copiar indiscriminadamente package.json/configuración. Lock, scripts clínicos, contratos, catálogos, referencias, tests y traducciones permanecen dentro del alcance declarado; solo cambian dependencias/configuración y estos documentos. El lock sí cambia para las dependencias citadas.

## Comprobaciones nuevas en esta copia

| Control | Resultado observado |
|---|---|
| npm ci --ignore-scripts --no-audit --no-fund |PASS, instalación propia desde lock |
| Frontend: npm test -- --maxWorkers=2 |445/445 PASS,13 archivos; son las pruebas de PR22, no las529 del corte Q5 |
| Python: unittest discover clinical/tests |812/812 PASS |
| Privacidad/propagación del informe de seguridad |4/4 PASS |
| npm run build, typecheck, lint |PASS; compilación y TypeScript reales |
| pip check |PASS |
| Configuración Vite resuelta en dev/test |fs.strict=true y límites exactos verificados |
| Trivy original PR22, con base actual |50 registros:3 CRITICAL,16 HIGH,26 MEDIUM,5 LOW; gate localFAIL19 |
| Trivy copia integrada, misma base |13 registros:10 MEDIUM,3 LOW;0 HIGH/CRITICAL/secretos; gate localPASS0 |
| npm audit actual |0 HIGH/CRITICAL,17 MODERATE y1 LOW; exit1 se conserva |

Entorno real Windows ARM64, Node24.15.0/npm11.12.1/Python3.13.17. Trivy0.76.2 binario Windows oficial, checksum de release y digest del asset GitHub cotejados antes de ejecutarlo. Misma versión que el contenedor CI, pero no se afirma ejecución del mismo binario/imagen Linux. Base de vulnerabilidades actualizada2026-11-17T06:59:44Z, reutilizada sin actualización en la comparación de la copia original.

Se usan la configuración y el clasificador report.py originales sin modificarlos, todas las severidades, dependencias de desarrollo incluidas y tres targets exigidos. El clasificador original da exit1 antes y exit0 después, sin cambiar baseline, suprimir avisos o rebajar el gate. No se publicó el informe crudo del escáner; el paquete contiene metadatos permitidos y evidencia de comandos. Trivy detectó cero configuraciones compatibles para misconfig: no es auditoría exhaustiva de workflows. npm y Trivy emplean bases, severidades y unidades distintas; no se suman sus conteos.

La compilación regeneró cuatro JSON de app con finalesLF. Se verificó igualdad del contenido contra blobs Git y se restauraron los bytesCRLF originales de esos archivos; no se conservó un delta clínico ni se modificaron generadores o pruebas para obtener PASS. No se atribuye nueva ejecución de suites después de esa restauración solo de finales de línea o de añadir documentación.

## Pendientes delimitados

Se han eliminado los19 bloqueantes Trivy en el ensayo local real. Permanecen13 registros inferiores Trivy y18 paquetes npm con avisos inferiores, listados en los informes completos de metadatos. No se afirma seguridad global ni se actualiza masivamente a nuevas majors para borrarlos.

Sonar no se ha ejecutado sobre este árbol local: siguen pendientes sus dos incidencias de rutas CLI de report.py y cobertura no aportada, además de la advertencia de versión Python del último análisis remoto. No se cambia report.py, el quality gate, exclusions, baseline, reglas, permisos o secretos. La propuesta de dependencias no demuestra resolución de esos hallazgos. Semgrep no se repite localmente: las reglas, fuentes y tests que analizó antes no cambian por esta entrega; su PASS remoto anterior es histórico, no un nuevo PASS local.

PR22 continúa en su commit remoto original y sus gates anteriores no cambian por esta integración local. La publicación o evaluación remota de este delta no forma parte de aplicar y comprobar en copia aislada. No se extraen secretos de Actions ni se envían datos clínicos. Los próximos pasos técnicos revisables son ejecutar los controles remotos cuando esta entrega sea adoptada en una rama y tratar Sonar con su límite de confianza/cobertura real, sin fingirlos resueltos.

El informe externo INFORME_INTEGRACION_SEGURIDAD_PR22.md, IDENTIDAD_INTEGRACION_PR22.json, parches y logs identifican el árbol efectivo final y los hashes de preservación. No se modifica main, RC1/v1.43, T06 o Q4; no se cambian dosis, fórmulas, contenido clínico, aceptación o estados médicos.
