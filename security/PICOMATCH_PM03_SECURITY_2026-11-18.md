# PM-03: corrección de la auditoría de seguridad de PM-02

Base: `fba27dcc898b6b42893f46823efd3f8385a06432`, árbol `ca602f9d102f996f65bdf5bc27fef8f1d4ebf548` (PR #25). Rama de trabajo aislada: `codex/picomatch-pm03-security-20261118`. Alcance: instalación, herramientas de desarrollo y comprobaciones de seguridad de Emergency. Núcleo internacional, cálculos y contenido clínico conservados; `CLINICALLY_PENDING`.

El informe independiente aportado es evidencia de un corte anterior. Sus recomendaciones se contrastaron con el código y las fuentes oficiales; no constituyen instrucciones adicionales del propietario.

## Correcciones

| Hallazgo | Resolución |
| --- | --- |
| PM02-F01 | App UI instala con `npm ci --ignore-scripts --no-audit --no-fund` y ejecuta exclusivamente el `postinstall` revisado con `npm run postinstall --ignore-scripts`. Acciones fijadas a SHA y checkout sin credenciales persistentes. |
| PM02-F02 | Temporales exclusivos aleatorios en el directorio del parser, modo conservado, `fsync`, comprobación SHA-256 antes de `rename` y verificación posterior. Cada rollback se intenta aunque otro falle; los errores se notifican. Ninguna escritura parcial se publica como parser. Una interrupción entre archivos puede dejar un árbol mixto de archivos completos: `--check` lo rechaza. |
| PM02-F03 | Se conserva el rechazo de extglobs repetidos en las cinco copias inventariadas. Se revisan por separado las fronteras de confianza y los límites indicados a continuación; no se afirma una corrección universal de expresiones regulares. |
| PM02-F04 | Los 18 comandos de producto tienen guardia previa, incluidos los 11 secundarios que faltaban. El comprobador de instalación ejecuta cada hook sobre una instalación sin defensa y exige error antes de aplicar la guardia. |
| PM02-F05 | Fixture de junction en el volumen del proyecto, fuera de `node_modules`; prueba real en Windows sin omisión. Un entorno que prohíba todos los enlaces seguirá fallando explícitamente. |
| PM02-F06 | Descripción de `package.json` y 33 líneas históricas de `STATE.md` reparadas mediante conversión reversible CP1252/UTF-8. No se cambian hechos históricos. |

## Fronteras de confianza y límites de PM02-F03

No hay llamadas productivas de `app/src` o `app/scripts` que conviertan entradas clínicas, formularios o datos de red en patrones de picomatch, estados de parser o regex. Los patrones relevantes son literales de configuración local: `app/vite.config.ts` (assets, Workbox y cobertura), `app/tailwind.config.js`, `app/eslint.config.js` y pruebas. Las cinco entradas de picomatch del lock tienen `dev: true`.

Consumidores revisados tras instalación limpia: `tinyglobby/dist/index.mjs`, `@rollup/pluginutils/dist/es/index.js`, `anymatch/index.js`, `micromatch/index.js`, `readdirp/index.js` y las llamadas de Vitest a filtros de configuración. Las rutas normales pasan strings al parser; las opciones observadas no activan `regex: true`. Esto por sí solo no garantiza seguridad ante patrones arbitrarios: algunos grupos con operadores regex, por ejemplo `+` dentro de paréntesis, se admiten también con opciones por defecto y no pasan por `extglobOpen`. La evaluación depende de los patrones locales confiables revisados. Los nombres de archivos se cotejan como muestras; no se convierten en patrones aportados por usuarios.

Rollup también contiene código picomatch **embebido** en sus bundles (`dist/shared/rollup.js`, `dist/shared/watch.js`, `dist/es/shared/node-entry.js` y `dist/es/shared/watch.js`). Ese código no es uno de los cinco paquetes parcheados. Sus filtros usan configuración local de build/watch; no se atribuye a la guardia protección sobre esos bytes. Una futura función que acepte globs externos, plugins o configuración de repositorios no fiables necesita otra revisión y aislamiento.

`toRegex`, `compileRe`, estados fabricados y `regex: true` no quedan protegidos en general. Las invocaciones directas de Node y `npm --ignore-scripts` pueden evitar los hooks. La defensa presupone un checkout y un escritor locales confiables, no un atacante con permiso para modificar código o dependencias. Continúa siendo una restricción temporal incompatible con extglobs repetidos legítimos; no se presenta como parche upstream.

## Cambio de la fuente oficial y estado de los escáneres

El 18/11/2026 a las **15:38:56 UTC**, GitHub retiró [GHSA-fc5q-39xc-vjpf](https://github.com/advisories/GHSA-fc5q-39xc-vjpf). El [registro oficial JSON](https://github.com/github/advisory-database/blob/main/advisories/github-reviewed/2026/10/GHSA-fc5q-39xc-vjpf/GHSA-fc5q-39xc-vjpf.json) contiene `withdrawn: 2026-11-18T15:38:56Z`. El [comentario del mantenedor](https://github.com/micromatch/picomatch/pull/235#issuecomment-6315749381) disputa la clasificación y exige que usuarios no fiables no definan expresiones. La retirada cambia la clasificación; no elimina el comportamiento exponencial reproducido.

El [registro npm](https://registry.npmjs.org/picomatch) sigue publicando `4.0.7` como latest y `2.3.2` en la rama 2.x. No se inventa una versión corregida ni se renombra un fork para ocultar detecciones. `npm audit` consultado de nuevo devuelve **0 vulnerabilidades**.

El escaneo local real Trivy 0.76.2 consulta los cuatro manifiestos obligatorios, incluye dependencias de desarrollo y mantiene `vuln,secret,misconfig`, `--ignore-unfixed=false`, todos los niveles y el clasificador original. La DB oficial disponible inicialmente (`UpdatedAt: 2026-11-18T13:03:23.615586156Z`) era anterior a la retirada; mirror y GHCR canónico entregaban los mismos datos. Con esa DB se mantuvieron **2 HIGH / 0 inferiores**, ambos de fuente `ghsa`, y el gate falló. No hay supresión, cambio de baseline, exclusión ni relajación de umbral.

Se esperó a la publicación oficial del [run 44365408511](https://github.com/aquasecurity/trivy-db/actions/runs/44365408511). La nueva DB canónica tiene `UpdatedAt: 2026-11-18T19:07:09.82030288Z` y se descargó en un caché local nuevo a las 19:27:54 UTC. El escaneo completo con esa base y el clasificador original devuelve **PASS, cuatro manifiestos, cero hallazgos de cualquier severidad**. El registro npm se volvió a consultar: últimas ramas 2.3.2, 3.0.2 y 4.0.7, sin versión corregida inventada.

La repetición remota de `44362811807`, intento 2, todavía descargó `mirror.gcr.io/aquasec/trivy-db:2` y conservó dos hallazgos, mientras el origen oficial ya daba cero. Por esa discrepancia se fija explícitamente **el origen oficial `ghcr.io/aquasecurity/trivy-db:2`** en CI, sin cambiar el escáner, los cuatro manifiestos, los niveles, las dependencias de desarrollo ni el clasificador. Se publica además `trivy.version.json` con la fecha real de la DB, mediante una lectura sin red del mismo caché. No se publica el informe crudo ni se añaden excepciones. Los resultados de la CI de esta revisión se acreditan por los runs asociados a su HEAD y por el informe de entrega.

## Verificación observada y trazabilidad

- Instalación Windows con scripts desactivados: ausencia de guardia y bloqueo previo comprobados; aplicación explícita, inventario de cinco copias e idempotencia PASS.
- Los 18 hooks previos rechazan una instalación sin defensa; 22 pasos del comprobador PASS.
- Frontend con cobertura real: **445/445 pruebas, 13/13 archivos PASS**.
- Lint y build, incluido TypeScript y generación de la PWA: **PASS**.
- Clasificador de seguridad original: **8/8 pruebas PASS**; HIGH continúa bloqueando y cada manifiesto es obligatorio.
- Controlador final: **11/11 pruebas PASS**, cero omitidas. Incluye escritura fallida/corrupta, `fsync`, `rename`, colisión `EEXIST`, conservación de temporales ajenos y rollback que continúa tras un error. Se reproducen seis casos upstream en procesos terminables; la guardia rechaza 1.800 compilaciones y conserva 18.000 comparaciones habituales.
- Cobertura del controlador medida desde subprocesos reales `NODE_V8_COVERAGE`: 90/90 líneas, 18/18 funciones y 62/69 ramas, sin exclusiones ni hits sintéticos. Artefacto remoto verificado: 62 registros LCOV, con los mismos resultados del controlador.
- CI de la implementación `670a42ee542fca32ac1dfe1f6f4273a5747d1564`: [matriz limpia 4/4 PASS](https://github.com/JuanCopado/Emergency/actions/runs/44359605847), [App UI con navegador/PDF PASS](https://github.com/JuanCopado/Emergency/actions/runs/44359605799), [Clinical QA PASS](https://github.com/JuanCopado/Emergency/actions/runs/44359606153), [Semgrep y cobertura PASS](https://github.com/JuanCopado/Emergency/actions/runs/44359605892). Sonar PASS con 97,4% de cobertura nueva y cero issues; revisión exacta confirmada en logs. Trivy es el único job FAIL, con los dos HIGH descritos.
- Los siete ZIP de matriz/cobertura/metadatos se descargaron y verificaron contra sus digest SHA-256 de GitHub. El merge commit de PR #27, `809b16d27c8bbf6c3a430c1f1df5266a34279d98`, tiene el mismo árbol `1bc8f43b254589eb5526b22921e2a73bafc9eede` que la implementación local. El ZIP de fuente conserva los 1.056 blobs Git exactos, sin conversión CRLF.
- Trivy con la DB canónica nueva: **PASS local, cero hallazgos, cuatro manifiestos**. Los FAIL iniciales y del mirror se conservan como ejecuciones históricas; no se reetiquetan como aprobados.

`clinical/`, `app/src/`, `app/package-lock.json`, `security/trivy.yaml`, `security/baseline.json` y `scripts/security/report.py` se contrastan contra la base y deben conservar sus blobs Git. No hay merge a ramas protegidas ni despliegue. Los documentos PM-02 anteriores conservan su fecha y estado histórico; este registro identifica los cambios posteriores.
