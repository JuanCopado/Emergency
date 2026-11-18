# PR22 — continuación de seguridad, 18/11/2026

**Estado: implementado y probado localmente; gate de dependencias FALLA por un advisory upstream sin versión corregida. Sonar remoto no ejecutado. CLINICALLY_PENDING.**

Base remota793d674911b8bd1af7285b4fc45c37f95c2a2666; continuación de la copia0858e29d8d25d97a8f23c6add1724220168759b8 del17/11. Es una copia nueva, sin modificar los candidatos ni ZIP anteriores, sin commit/push/merge/despliegue. La fuente clínica, contratos, tests clínicos, fórmulas, catálogos y traducciones conservan sus bytes.

## Correcciones

Versiones oficiales verificadas: Vite6.4.6, Vitest4.1.12, typescript-eslint8.73.0, React Router DOM7.18.5; fast-uri3.1.9, postcss-selector-parser6.1.5, serialize-javascript7.1.3, glob14.0.2 y minimatch11.0.1 mediante overrides dirigidos. Se conserva el resto de la propuesta del17/11. No se usa npm audit fix ni se aceptan sus downgrades sugeridos a paquetes antiguos. La migración Router6→7 y las dos sustituciones transitivas de major se verifican con tests, lint/build y prueba de cinco rutas reales en Edge headless. No se modifica un componente de producto para hacerlas pasar. El navegador de prueba/servidor4208 se cerraron.

El clasificador scripts/security/report.py elimina los argumentos raw/output/--baseline: JSON por stdin y metadatos por stdout, estado humano por stderr. No abre ni escribe rutas proporcionadas por argumentos. Baseline fija al repositorio, sin rebajar sus reglas o severidades. Las redirecciones pertenecen al workflow y usan archivos fijos de RUNNER_TEMP. Se conservan fallos por informe malformado, targets ausentes, HIGH/CRITICAL y cualquier secreto. Las8 pruebas incluyen privacidad, errores, destinos ausentes, JSON inválido y rechazo de rutas/opciones antiguas sin tocar archivos externos. No se descartan incidencias Sonar: se aporta una corrección estructural cuya aceptación remota aún no está comprobada.

## Cobertura real y workflow

Se añade coverage7.17.3 y @vitest/coverage-v8 4.1.12 como dependencias de pruebas. coverage.py mide Python y subprocess; Vitest mide frontend, incluyendo archivos no ejecutados dentro de su alcance. Solo se excluyen rutas que ya son pruebas en Sonar, no código ejecutable para mejorar el gate. XML/LCOV registran la cobertura observada, sin umbral rebajado ni porcentaje inventado.

Workflow: job coverage separado, Node22/Python3.12, tests antes de artefactos; Sonar necesita únicamente ese job y descarga XML/LCOV antes de analizar. Trivy no cancela Sonar por un finding. Las acciones nuevas se fijan a SHA oficial verificado y se registran en toolchain.lock.json. Se conservan permisos mínimos, checkout sin credenciales, controles fork/Dependabot, secreto solo en pasos Sonar y gate80/A sin modificación. Configuración Python de Sonar declara3.12, conforme a CI. actionlint1.7.12PASS con shellcheck/pyflakes no disponibles. No se ejecutó el workflow completo Linux ni un nuevo análisis Sonar/Semgrep.

812 pruebas PythonPASS,445 frontendPASS,8 del informePASS; build/TypeScript/lint/pip checkPASS. Segunda campaña frontend445 solo para corregir la raíz de rutas LCOV; no son890 tests únicos. Cobertura: Python7555/9818 líneas (76,95%), ramas65,28%; frontend1066/1499 líneas (71,11%), ramas68,38%. report.py64/64 líneas,23/24 ramas. Estas cifras globales no son la métrica Sonar de código nuevo ni prueban que el gate80% pase. XML y61 rutas LCOV se resolvieron contra fuente; solo se normalizaron separadores/raíz de archivos, con contadores inalterados.

## Escáneres actuales y bloqueo upstream

Comparación con la misma base Trivy actual: la copia del17/11 produce15 registros (2HIGH+13inferiores); esta continuación produce2HIGH y0inferiores, ambos de CVE-2026-112366/picomatch ya presente en la copia anterior. No se reinterpreta el0HIGH observado con la base del17/11 como resultado actual. En npm, los32 paquetes afectados del corte anterior (19HIGH/12moderados/1bajo) quedan en25HIGH/0moderados/0bajos. Los25HIGH son propagación de UN advisory por el grafo, no25 CVE; seis dependientes extra proceden de herramientas de cobertura añadidas. npm y Trivy no se suman ni equiparan.

GitHub Advisory GHSA-fc5q-39xc-vjpf indica versiones afectadas<=4.0.7 y patched versions None. El registro oficial devuelve latest4.0.7 y404 para4.0.8/5.0.0 al comprobarlo. No se instala un fork no verificado, se elimina el scanner, se ignora el finding ni se cambia baseline/gate para aparentar verde. Los nodos picomatch del lock son dev=true; esto delimita exposición de tooling y no elimina el aviso ni certifica ausencia de explotación. No se ejecutó una prueba de explotación independiente.

Fuentes: https://github.com/advisories/GHSA-fc5q-39xc-vjpf ; https://github.com/micromatch/picomatch/issues/247 ; registro oficial npm y PyPI en OFFICIAL_FIX_METADATA.json/PICOMATCH_OFFICIAL_STATUS.json. Docs oficiales: https://docs.sonarsource.com/sonarqube-cloud/analyzing-source-code/test-coverage/python-test-coverage y https://vitest.dev/guide/coverage.html .

## Preservación y pendientes

Se restauran únicamente finales de línea de cuatro JSON regenerados por build, tras comprobar igualdad de contenido y hash original; no queda un delta clínico. Las1.045 fuentes de la entrega anterior, los originales Q5 y todos los ZIP anteriores permanecen intactos. La nueva identidad y parches se entregan fuera de la copia, sin autoincluir su propio hash en este documento.

Pendientes reales: versión oficial corregida/solución revisada de picomatch y rescan, y adopción en una rama para ejecutar los gates remotos y confirmar resolución/importación Sonar. Los porcentajes globales observados se conservan aunque sean inferiores a80; no se ocultan archivos para subirlos. La publicación no se realizó en esta continuación aislada. Los informes17/11 dentro del árbol son historia, no estado vigente de seguridad. No hay cambios médicos ni activación T06/Q4.
