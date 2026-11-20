# Integración T05/gasometría y T06 · 19/11/2026

Autorización: petición del propietario «integrar T05/gasometría y T06». Rama de trabajo: `codex/integrate-t05-t06-20261119`. Estado clínico: **CLINICALLY_PENDING**. No constituye `GO_RELEASE` ni aceptación asistencial.

Los apartados de composición y verificación que siguen conservan el corte histórico del 19/11, incluidos los candidatos intermedios fallidos. El apartado final «Cierre técnico verificado el 20/11/2026» registra el resultado posterior de PR33, la corrección de sus cinco incidencias en PR34 y la CI del HEAD internacional inspeccionado.

## Base y material recuperado

- Base de composición: PR32, commit `abdeae442a151ce1b1fe0786725991a7d35bc558`, árbol `feabbe55ecceea886ccde20aec526ff920dcb473`. Incluye las correcciones P1 de JSON/precisión sobre la integración PR31 `2eeedfd36880e8b971c63f13f7736922cf87de1e`.
- T05: replay desde commit `1d0652ebcef9b5990edd9e5745b0c06f8d6b8274`, con árboles originales verificados `9e6ad2d55b38a3d3130a44bb574c4cdbec6694c1` → `eb9e263f36856addac2de42835c7b191c4856d41` → `0b9a2ecaab038b7624e8a0855c54f220a71882da` (R3, PAR01, FiO₂). Paquetes y manifiestos recuperados; no se reconstruyó código a partir de resúmenes.
- T06: paquete PAR02 SHA-256 `bc5dda63770a5240695bfd7bef98bc9ad86bf1cdef13c445f73ee8eff04083f1`, manifiesto 431/431. Q4 procedente del árbol `c22b755a93fbb1b4dd28dbb88a59dcc67818f9be`; este identificador es un árbol, no un commit. R6/B1 y los cinco archivos Q4 conservan bytes; detalle en `tools/t06-localhost-lab/SOURCE_PROVENANCE.json`.

Los logs y capturas históricos permanecen en sus entregas de origen. La integración incorpora código, pruebas, contratos y procedencia necesarios; no presenta esos logs como pruebas del árbol nuevo.

## Resultado de la composición

Rutas `/blood-gas` y `/t06-lab` incorporadas a la misma aplicación, con acceso desde Inicio y enlace desde la nota clínica a T05. Launcher común, dependencias reproducibles, modelo OCR con hash y licencia y límites de plataforma explícitos.

T05 conserva la revisión visual, separación de muestras, confirmación humana, revocación de resultados y trazabilidad de FiO₂. Se corrigen dos fronteras técnicas encontradas al componer: JSON con miembros duplicados y pérdida no nulo→cero, tanto en números JSON como en analitos textuales. Se reutiliza el transporte HTTP acotado; no se alteran fórmulas ni se introducen nuevos umbrales médicos.

T06 conserva el circuito real R6/B1 con TLS sintético y Q4. Su adaptador limita conexiones, tiempo, Host, Origin, framing y plataforma. Los errores son estáticos. No recibe consultas libres ni datos de pacientes; el acceso a proveedores públicos sigue fuera de este circuito.

El launcher conserva procesos separados: el audit hook de T06 nunca se instala en el servidor clínico. Vite habilita las proxies nuevas solo en modo local, comprueba la conexión y el Host de entrada, conserva Origin y añade CSP y la marca de sesión sin nuevo service worker.

## Revisión del lock de desarrollo

El nuevo middleware Vite necesita tipos Node: se añaden únicamente `@types/node` 22.20.5 y `undici-types` 6.21.0, ambos de desarrollo. Se comparó cada entrada del lock: ninguna dependencia existente ni paquete objetivo de la mitigación cambia. Los scripts, incluido el postinstall previo, se conservan. Una revisión técnica independiente confirmó este delta; se actualiza solo `lock_sha256` en la política de picomatch a `902f89eb70b96e535fb2e2870aa74c2e426ce983c8ce856f59a106a1d5c39af7`. No se cambia `policy_sha256`, targets, guardas, reglas, baseline ni severidades de seguridad. La instalación y las pruebas de la mitigación siguen siendo obligatorias.

## Verificación y límites

Las pruebas nuevas se ejecutan sobre la composición, conservando las regresiones de PR32. Los resultados locales y los enlaces a CI se registran en el informe de entrega de este encargo. El workflow `Local review integration` exige extracción real T05 en Windows y circuito real T06 en Linux, con navegador y recibos propios; no se atribuye aquí un PASS futuro.

La primera CI detectó dos defectos del verificador T05: lectura del cuerpo desde una caché CDP que ya lo había expulsado y un selector de metadatos que también coincidía con una sección. Se comprueban ahora las dos muestras y el resultado mostrado por la aplicación, y se restringe el selector al control correspondiente. Se conservan los HTTP y las aserciones de cálculo, corrección y revocación.

Sonar detectó inicialmente cobertura nueva de 73,4 % y seguridad E. La captura combina ahora las ejecuciones portables y nativas reales del mismo árbol antes del análisis, incluidos modelo, launcher y worker Windows. En el candidato `9e1b173a6e9ca6803079c5ddb8ae6f5645827047`, árbol `9a59a1a8b304a5e29b3ac695bed1055fbbc7774c`, la [CI de PR33](https://github.com/JuanCopado/Emergency/actions/runs/44538357335) confirmó T05 Windows (73 pruebas y 7 comprobaciones de navegador), T06 Linux (6 pruebas y 18 escenarios más 4 transiciones de navegador) y combinación de cobertura. El análisis completado pasó la cobertura nueva con 87,5 %, pero mantuvo seguridad E.

La consulta de diagnóstico de solo lectura recuperó diez incidencias: serialización de respuestas y orígenes HTTP de T05, archivos temporales y rutas CLI del worker, redirecciones en comprobaciones de salud y declaración TLS del propio diagnóstico. El [recibo de consulta](https://github.com/JuanCopado/Emergency/actions/runs/44539904128) está asociado a PR33 y fue recogido después del análisis anterior; el SHA del helper identifica la consulta, no un análisis nuevo. Las correcciones técnicas se someten de nuevo a CI; este registro no les atribuye un PASS futuro. Se retira el workflow temporal de diagnóstico y se conserva la recogida acotada de metadatos cuando falla el gate normal.

El candidato siguiente separa JSON de archivos estáticos y conserva sus valores mediante escapes reversibles; expresa el host loopback literal y exige configuración de orígenes. El padre crea las entradas del worker de forma exclusiva y concede únicamente su directorio temporal al validador CLI existente, manteniendo cwd y Job Objects. Las sondas de salud conectan directamente con loopback, sin proxies ni redirecciones. El diagnóstico declara explícitamente la verificación de certificado y nombre TLS. Las regresiones emplean datos sintéticos, archivos temporales y servidores loopback reales; no constituyen validación clínica.

No se cambian umbrales, baseline, exclusiones ni el resultado original de un gate fallido. El cierre requiere observar los análisis de PR y rama del candidato final. T06 bajo `tools/` no está incluido en el alcance Sonar vigente y dispone de evidencia nativa propia.

El worker T05 requiere Windows Job Objects. El transporte B1 T06 requiere Linux/POSIX. No se ha portado ninguno ni eliminado su contención; no existe una plataforma única que ejecute ambos adaptadores nativos entregados. Un HTTP200 de sesión no se considera prueba de extracción. Una ejecución de navegador no acredita aislamiento de red del SO ni validación clínica.

El registro de evidencia y sus fechas clínicas se conservan sin promoción. Los 19 contratos aceptados y 46 IDs se mantienen; no se restablecen bloqueos históricos. No se modifica `main`, las referencias congeladas ni v1.43. Uso y comandos: `docs/LOCAL_REVIEW.md`.

## Cierre técnico verificado el 20/11/2026

Actualización documental mediante lectura de las PR, check-runs, jobs, logs y diferencias de GitHub, contrastados con el repositorio. No se ejecutan nuevas suites ni se relanza CI para esta actualización. Los resultados siguientes pertenecen a los commits y ámbitos indicados; los fallos de los cortes anteriores se conservan como antecedentes.

### PR33: integración y gates finales del 19/11

[PR33](https://github.com/JuanCopado/Emergency/pull/33) se fusionó el **19/11/2026 a las 14:38:46 UTC** en `codex/v144-international-scope-20261116`. Su HEAD final fue `982c73c579db70a0c7dac3d648b88a19c0be9e1c`, árbol `81111edf80771b9f9a3fe5517e2ed6b7ad5aa819`; el merge es `a02d50578424d509cd25747efa001bcd7a2d4823`.

| Ámbito del mismo HEAD | Evidencia de Sonar | Resultado observado | Cobertura de código nuevo |
|---|---|---|---|
| PR33 | [Run 44543684735, job 135631460900](https://github.com/JuanCopado/Emergency/actions/runs/44543684735/job/135631460900) | `QUALITY GATE STATUS: PASSED`, 14:32:59 UTC | 88,2 % |
| Rama de integración | [Run 44543669249, job 135631298064](https://github.com/JuanCopado/Emergency/actions/runs/44543669249/job/135631298064) | `QUALITY GATE STATUS: PASSED`, 14:33:26 UTC | 81,9 % |

Ambos runs de seguridad terminaron en `success`, incluidas las pruebas nativas T05 Windows y T06 Linux, la cobertura real y su combinación con identidad verificada, Semgrep y Trivy. Los logs de estos dos analizadores registran cero hallazgos. El [resumen de PR33](https://github.com/JuanCopado/Emergency/pull/33#issuecomment-7012144979) y los [checks del HEAD final](https://api.github.com/repos/JuanCopado/Emergency/commits/982c73c579db70a0c7dac3d648b88a19c0be9e1c/check-runs?filter=all&per_page=100) conservan **cinco incidencias nuevas y cero aceptadas**. El PASS de PR33 no se registra como cero incidencias; su identificación y corrección corresponden al corte posterior de PR34.

### PR34: identificación y corrección de las cinco incidencias

El [diagnóstico de lectura del 20/11, run 44686887315, job 136123229873](https://github.com/JuanCopado/Emergency/actions/runs/44686887315/job/136123229873) recuperó las cinco anotaciones y su clasificación. Todas eran `CODE_SMELL`: cuatro `MAJOR` por retroceso superlineal de expresiones regulares y una `MINOR` por una dirección IP literal. Las ubicaciones de la tabla son las señaladas en PR33.

| ID Sonar | Regla y severidad | Ubicación y corrección de PR34 |
|---|---|---|
| `AaHz-wmeCO9ADCe2c95g` | `python:S8786`, MAJOR | `clinical/scripts/blood_gas_review.py:39`: encabezado corto separado mediante `partition(":")` y validación de etiqueta. |
| `AaHz-wmeCO9ADCe2c95h` | `python:S8786`, MAJOR | `clinical/scripts/blood_gas_review.py:41`: el mismo tratamiento para encabezados de metadatos. |
| `AaHz-wmeCO9ADCe2c95i` | `python:S8786`, MAJOR | `clinical/scripts/blood_gas_review.py:114`: reconocimiento final de `[measured/calculated]` con `rstrip()` y patrón sin la repetición de espacios que provocaba retroceso. |
| `AaHz-wugCO9ADCe2c95r` | `typescript:S8786`, MAJOR | `app/src/lib/format.ts:30`: recorrido explícito de ceros finales en la normalización decimal. |
| `AaHz-wuuCO9ADCe2c95s` | `typescript:S1313`, MINOR | `app/vite.config.ts:67`: representación IPv4 mapeada derivada del mismo host loopback y conjunto cerrado de pares locales. |

[PR34](https://github.com/JuanCopado/Emergency/pull/34) contiene el commit `b0d8eba6dc806731a6cfd05301e22b3a0d177dcf` y se fusionó el **20/11/2026 a las 06:37:07 UTC**, merge `4f2f1a16b3f58e351290c06a9dc511af1eb3f22d`. Su [diff de cinco archivos](https://github.com/JuanCopado/Emergency/pull/34/files) añade regresiones de precisión entera, literalidad de metadatos y procedencia del analito; no modifica fórmulas, umbrales del gate, baseline ni exclusiones.

Los [18 checks del commit de PR34](https://api.github.com/repos/JuanCopado/Emergency/commits/b0d8eba6dc806731a6cfd05301e22b3a0d177dcf/check-runs?filter=all&per_page=100), correspondientes a seis ejecuciones de CI —tres de PR y tres de push—, finalizaron en `success`. Los dos gates de Sonar aprobaron: [PR34, run 44687095951, job 136125863251](https://github.com/JuanCopado/Emergency/actions/runs/44687095951/job/136125863251) y [rama, run 44687072922, job 136125810287](https://github.com/JuanCopado/Emergency/actions/runs/44687072922/job/136125810287). Ambos resúmenes registran **cero incidencias nuevas y cero aceptadas**, con cobertura nueva de **89,7 % en PR34** y **81,9 % en su rama**. El [bot de PR34](https://github.com/JuanCopado/Emergency/pull/34#issuecomment-7032275238) confirma además cero hotspots y cero riesgos nuevos de dependencias. El pendiente de identificar y corregir las cinco incidencias queda cerrado en este alcance.

### Corte internacional observado el 20/11

HEAD inspeccionado: `cdca8e34013bba891a1c49f5ea859f933fcbea63`, árbol `977ec9cd9443bf0e7a284de13e00f242ea80ef92`, de `codex/v144-international-scope-20261116`. Se comprobó en Git la ascendencia de los merges de PR33 y PR34 respecto de este commit. Este corte incluye trabajo posterior a ambas entregas; sus funciones, decisiones clínicas y resultados se conservan en sus propios registros.

| Control sobre `cdca8e34013bba891a1c49f5ea859f933fcbea63` | Evidencia | Resultado observado |
|---|---|---|
| Clinical QA | [Run 44733479337](https://github.com/JuanCopado/Emergency/actions/runs/44733479337) | `success` |
| App UI QA | [Run 44733479273](https://github.com/JuanCopado/Emergency/actions/runs/44733479273) | `success` |
| Security and quality | [Run 44733479342](https://github.com/JuanCopado/Emergency/actions/runs/44733479342) | `success`; cobertura real y combinación verificadas |
| T05 nativo Windows | [Job 136278881204](https://github.com/JuanCopado/Emergency/actions/runs/44733479342/job/136278881204) | `success` |
| T06 nativo Linux | [Job 136278881439](https://github.com/JuanCopado/Emergency/actions/runs/44733479342/job/136278881439) | `success` |
| Semgrep | [Job 136278880497](https://github.com/JuanCopado/Emergency/actions/runs/44733479342/job/136278880497) | PASS; cero hallazgos |
| Trivy | [Job 136278880773](https://github.com/JuanCopado/Emergency/actions/runs/44733479342/job/136278880773) | PASS; cero hallazgos |
| Sonar de la rama internacional | [Job 136281818006](https://github.com/JuanCopado/Emergency/actions/runs/44733479342/job/136281818006) | `QUALITY GATE STATUS: PASSED`, 12:18:34 UTC |

Los [checks de este HEAD](https://api.github.com/repos/JuanCopado/Emergency/commits/cdca8e34013bba891a1c49f5ea859f933fcbea63/check-runs?filter=all&per_page=100) registran tres workflows y nueve checks en `success`. El check Sonar `136282987624` publica cero incidencias nuevas, cero aceptadas, cero hotspots, **83,1 % de cobertura de código nuevo** y **0,2 % de duplicación de código nuevo**. No queda un gate pendiente o fallido en las ejecuciones enumeradas. Las cifras de cobertura pertenecen al ámbito y revisión indicados; no son cobertura global ni métricas de exactitud clínica.

### Límites que conserva este cierre

- T05 continúa necesitando Windows Job Objects para su extracción protegida; T06/B1 necesita Linux/POSIX. La CI verifica cada adaptador en su plataforma. No acredita una plataforma única con ambos adaptadores nativos ni aislamiento de red del sistema operativo.
- T06 permanece limitado al laboratorio sintético local, sin consultas libres, proveedores públicos, RAG ni cierre global G05. Su runtime bajo `tools/` continúa fuera del alcance Sonar; los resultados nativos se citan por separado.
- Se mantienen las decisiones clínicas ya aceptadas en su alcance y el estado global **CLINICALLY_PENDING**. La decisión clínica corresponde al Dr. Juan Copado Ceballos conforme a `AGENTS.md`; este cierre técnico no concede `GO_RELEASE`, aceptación asistencial ni validación prospectiva.
- Esta actualización conserva fechas y estados de evidencia. No renueva revisiones clínicas ni atribuye a los candidatos históricos los resultados de commits posteriores.
