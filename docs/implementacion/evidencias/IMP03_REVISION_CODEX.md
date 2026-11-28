# Revisión independiente Codex · paquete local IMP-03

Revisor: Codex, distinto del escritor del código. **No es una revisión de Claude ni un dictamen Antigravity.** Alcance: `local-package/tools/local-installation/local_installation.py` y pruebas, incremento estático parcial; no API clínica local, identidad remota, producción ni liberación clínica.

Estado final de la revisión por bytes: **REVIEWED_BOUNDED_NO_OPEN_FINDINGS**. HallazgoP2 original corregido y verificado de forma independiente. Fuente final SHA-256 `3079b98ccf9900da7044178a52896eddd2ee755bcae21a3ed545de0a880fb42f`; pruebas SHA-256 `c06788d2e1bc923409dd84dda1d5a2ce607a1fd51a31d7929b40ad608e951270`; README SHA-256 `d48917d157b7728c8c25ff17b6629fe3b12b773455aa144e714d99b48c9d7291`. Rama `feat/implementation-local-package-20261127`; modificación puntual todavía sin commit sobre `be35743b750a1fc0e9dd62dcca838f0eaa1fd249` al verificar estos bytes. No es auditoría del futuro commit ni dictamen externo de liberación. No se editó el código del escritor.

Se preserva a continuación el hallazgo y su prueba antes de la corrección: fuente histórica `62300323c6dd6eefd400aba4ce58c9a1fa7c6715349da92afe357777102df153`.

## Hallazgo material reproducido

**P2 · La cantidad de entradas ZIP se limita después de materializar su directorio completo.** En `install`, `zipfile.ZipFile(archive_path)` analiza el directorio central antes del bucle que rechaza más de `MAX_FILES+1` entradas. La comprobación de tamaño comprimido y los límites durante extracción protegen disco y bytes extraídos, pero no impiden la asignación previa de metadatos de todas las entradas.

Probe sintético temporal `revision_codex_probe.py`: archivo ZIP de2.327.906bytes con25.001entradas; se observaron25.001objetos materializados antes de validación y14.536.100bytes de pico `tracemalloc`. La operación fue rechazada con `Archive expansion limit`, sin crear `active.json`; fuente antes/después idéntica. No se ejecutó archivo gigante ni se extrapoló una medición deOOM. La admisión actual permite archivos comprimidos mucho mayores, por lo que el riesgo real es consumo evitable de memoria/tiempo al recibir un ZIP hostil, aunque su manifiesto no llegue a validarse.

Recomendación concreta: preflight acotado del EOCD y límites de cantidad/tamaño/offset del directorio antes de construir `ZipFile`; rechazar ZIP64/multidisco si no son necesarios. Deben permanecer las verificaciones posteriores, pues el preflight no autentica ni sustituye al parser. Añadir negativo que demuestre que `ZipFile` no se construye para un número declarado excesivo o un directorio central de tamaño no permitido.

**Resolución verificada:** `preflight_zip` ejecuta antes de `ZipFile` una lecturaEOCD de22bytes, limita el directorio a1MiB y la cantidad declarada a2.049entradas, valida offset/final exactos, recorre y cuenta registros reales dentro de ese buffer acotado y exige igualdad de cantidades. Rechaza ZIP64/multidisco/comentarios/extras/descriptoresstreaming/cifrado y formatos de compresión fueraSTORE/DEFLATE. Se conservan las verificaciones de extracción e identidad. Nuevo test con tres casos (cantidad excesiva, tamaño excesivo y cantidad mentida) comprueba `ZipFile.assert_not_called()`.

El mismo probe independiente de25.001entradas fue repetido sobre los bytes finales: rechaza con `ZIP entry count limit` **antes de entrar al constructor observado**; no hay objetos de entradas materializados por él ni puntero activo. Resultado `REVISION_CODEX_PROBE_AFTER.json`; el recibo anterior no fue sobreescrito. No se extrapolan garantías frente a un actor local que pueda sustituir archivos mientras el proceso los lee.

## Verificación ejecutada

Antes del fix: `python -m unittest discover -s tools/local-installation -p test_local_installation.py -v` sobre la copia del escritor:18pruebas contadas, **17PASS y1SKIP**; duración4,577s. El omitido fue creación nativa de symlinkWindows, error1314; el control nativo de junctionWindows sí pasó. No denominar18PASS.

Tras el fix, el revisor repitió la suite: **19pruebas contadas,18PASS y1SKIP**, duración4,891s. Incluye el nuevo test de preflight y `.mjs` servido con `Content-Type:text/javascript`. El mismo control nativo de symlinkWindows sigue omitido por privilegio1314; junctionWindows síPASS. No denominar19PASS ni confundirlo con la ejecución separada del escritor.

### Delta final focal, sin repetir la revisión completa

Sobre los tres hashes finales indicados arriba, se releen y verifican dos correcciones nuevas y los cambios de custodia/documentación:

1. **Hash CSP de script inline:** el navegador normalizaCRLF yCR aislado aLF al preprocesarHTML. `InlineScripts.handle_endtag` realiza ahora esas dos sustituciones únicamente al calcular el hash, conservando los bytes del artefacto. Se ejecutó el test de las tres variantes;PASS.
2. **LocatorZIP64:** `ZipFile` puede usar el locator situado20bytes antes deEOCD incluso sin sentinels32bits. El preflight ahora rechaza su firma antes del parser, conservando los límites del directorio; el test con `ZipFile.assert_not_called()` se ejecutó y pasó.
3. Se relee el productor: elimina redirecciones/configuraciónGit heredada por comando, usa `core.autocrlf=false`, rechaza archivosVite`.env` de producción y conserva la advertencia de noattestation. Se ejecutó el test de paquete limpio/determinista con negativos deenv implícito,override remoto,archivo inesperado yfuente sucia;PASS.

Ejecución propia de este delta: **dos tests focalesPASS en0,015s y unoPASS en0,685s**. Son tres pruebas, no una nueva suite completa de21. El escritor/coordinador comunica su ejecución final separada de21contadas/20PASS/1SKIP1314; ese resultado no se atribuye al revisor. Se conserva la ejecución independiente completa anterior sobre sus hashes previos.

El coordinador informa además Chrome158 real con buildA81→B170→A81 en tres orígenes frescos, SWcontrolador, cálculo5,3, API503, cero erroresCSP/página/peticionesexternas, y recargaoffline tras detener servidor con cálculo5,3 y rechazoAPI; pestañaA existente intacta. **Es evidencia ejecutada por Work, no por este revisor**; sus recibos/SHA debuild deben acompañar el expediente. No amplía este dictamen aAPIclínica, toda laPWA, migración de preferencias ni publicación. ElREADME final explicita ledger por raíz y `browser_activation=PENDING_ACTUAL_PAGE_IDENTITY_VERIFICATION` hasta verificar la página realmente cargada.

### Corrección posterior de CIWindows: identidad del checkout y alias8.3

El coordinador comunica **FAIL real de Windows en `be35743b750a1fc0e9dd62dcca838f0eaa1fd249`**, con LinuxPASS: GitWindows expande un alias8.3 como `RUNNER~1` y la comparación anterior de cadenas lo confundía con otro checkout. Se conserva eseFAIL; las pruebas locales anteriores no pasan a certificar esta nueva versión.

Cambio focal releído: el productor conserva el requisito de`.git` propio y valida con `no_links` tanto `source_root` como el toplevel devuelto porGit. Solo después compara identidad de directorios mediante `os.path.samefile`; no elimina el veto a symlinks/junctions ni acepta una subcarpeta como raíz del checkout. Esto compara el objeto del sistema de archivos, admitiendo únicamente dos representaciones del mismo directorio existente.

Se ejecutaron independientemente **dos tests focalesPASS,0,260s**: fixtureGit real con `GetShortPathNameW` nativo y paquete desde esa ruta; negativos de directorio sincheckout, raízGit distinta y carpeta anidada. El negativo de raíz distinta sustituye únicamente la respuesta deGit por un directorio físico diferente; el positivo usa laAPIWindows yGit reales. No se cambió la configuración del volumen ni se crearon enlaces para el positivo.

El escritor comunica una suite final separada de23contadas/22PASS/1SKIP1314; **no es una suite completa ejecutada por este revisor**. CI y el nuevo recorridoChrome sobre los bytes corregidos deben recogerse por el futuroSHA, sin heredar su PASS de `be35743` ni del núcleo anterior `0d27c632…`. La revisión por bytes permanece favorable en el alcance acotado; CI final aún pendiente en este corte.

Además se ejecutó el probe independiente de metadatos ZIP descrito arriba; resultado físico `REVISION_CODEX_PROBE.json`.

## Controles examinados y límites

- Digest del manifiesto requerido desde una fuente de confianza separada; descriptor cerrado, hashes/tamaños/tipos, nombres portablesWindows y colisiones casefold/archivo-directorio.
- Extracción manual, límites por entrada/total/ratio y conjunto exacto; rechazo de ZIPsymlink y reparsepoints del árbol local. Verificación antes de instalar/activar y rehash de bytes servidos.
- Escritor único, puntero atómico y conservación de versiones; fallo de selección no altera puntero previo. Esto no equivale a garantía de recuperación ante cualquier fallo de hardware ni protege frente a un actor con control de escritura del usuario.
- Servidor solo127.0.0.1, Host exacto, Origin/Fetch-Site,16workers y timeout de socket; sin logs de ruta/query/cuerpo, sin CORS permisivo. No hay servicio público ni autenticación individual.
- Cabeceras no-store/CSP/nosniff/no-referrer/CORP; scripts inline autorizados por hash delHTML verificado. `/api` devuelveJSON503, nunca shell clínico. Métodos/rutas negativos cubiertos.
- Puntero de versión se aplica al siguiente launcher; episodios ya abiertos preservan su versión. Ledger de puertos es **por raíz de instalación**, no inventario global de orígenes usados por cualquier programa/restauración. No migra PWA/bookmarks/preferencias ni garantiza limpieza del navegador. La prueba real de navegador del padre debe expresar ese alcance.
- El productor comprueba checkoutlimpio y revisión incrustada, pero **no certifica que ese dist provenga de ese build** ni autentica al editor. Conservar buildlog y expectativa de hash confiable; no llamarlo attestation o firma.
- Primera lectura no admitía`.mjs`; el padre identificó el workerPDF y el escritor lo corrigió. Los bytes finales lo admiten en empaquetado/revisión incrustada y lo sirven comoJavaScript; test HTTP independiente pasó. Eso no declara cubierta la funcionalidadPDF ni la API excluida.

La suficiencia de18controles sintéticos depende de mantener este alcance estático parcial. La prueba de navegador sobre artefacto real debe demostrar carga de recursos, ausencia de egreso no permitido y aislamiento de versión tras actualizar/rollback; no acredita todos los flujos clínicos, accesibilidad global ni funcionamiento de una API excluida.

`CLINICALLY_PENDING` · `NO_GO_CLINICAL_RELEASE`. Sin modificación de motores, ramas protegidas, permisos, infraestructura externa ni producción por este revisor.
