# IMP-03 · Instalación local estática acotada

Este incremento reutiliza el build existente de Emergency; no reconstruye el frontend ni modifica motores, fórmulas, fuentes o decisiones. Usa únicamente la biblioteca estándar Python. **CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE.** No es despliegue público, backend clínico, gateway productivo, autenticación OIDC ni garantía de funcionamiento offline de todas las funciones.

## Qué incluye

- Paquete determinista del `dist` compilado con manifiesto de tamaños/SHA-256 y SHA fuente.
- Recepción acotada, versiones separadas, selección atómica y rollback de archivos revalidado.
- Servidor estático dedicado exclusivamente `127.0.0.1`, sin Vite runtime ni proxy clínico.
- Directorio de instalación privado elegido por el usuario, sin modificar configuración global, cookies, perfiles o servicios.

El paquete contiene solo recursos del frontend y su manifiesto. El lanzador revisado se distribuye por separado como parte de este código. **No se incluye Python, el backend, secretos, cuentas ni datos de pacientes.** El equipo receptor necesita una instalación Python compatible previamente disponible. Los runtimes de construcción Node/Python siguen siendo necesarios para generar el build, no para servir la referencia estática.

## Construcción y custodia

Construir desde un checkout limpio del SHA elegido mediante los comandos revisados del proyecto (`npm ci --ignore-scripts`, postinstall explícito y `npm run build:security`). Reutilizar dependencias instaladas solo cuando plataforma, lock e integridad estén comprobados. No instalar dependencias nuevas para este empaquetador.

El empaquetador verifica checkout limpio, SHA Git, presencia del SHA en JavaScript, inventario y ausencia de variables `VITE_*`/override local en su propio proceso y de archivos Vite `.env` de producción. Ignora configuración Git de sistema/global y redirecciones `GIT_*`, usa `core.autocrlf=false` para cotejar bytes de fuente coherentemente con el build. No altera esa configuración.

**Esto no atestigua de forma independiente cómo se compiló un `dist` anterior.** Conservar el comando, entorno efectivo, stdout/stderr, versiones de herramientas y SHA-256 de los inputs/artifactos del build real; cotejarlos antes de aceptar el paquete. La comprobación de un SHA embebido no prueba que cada byte provenga de ese checkout. Los archivos `.map` de auditoría se excluyen; los módulos `.mjs`, incluido el worker PDF existente, se conservan con MIME JavaScript.

Desde la raíz del repositorio; reemplazar los valores de ejemplo por los observados:

```powershell
python tools/local-installation/local_installation.py package --dist C:\laboratorio\build-source\app\dist --source-root C:\laboratorio\build-source --output C:\laboratorio\salida\emergency.zip
```

La salida JSON contiene `version`, `manifest_sha256`, `zip_sha256`, número de archivos y `source_sha`. El ZIP debe ser una ruta nueva; el proceso no sobrescribe paquetes existentes. Guardar el JSON por un canal confiable separado del ZIP.

**Un manifiesto dentro de un ZIP no autentica al editor.** `--expected-manifest-sha256` debe venir de una fuente confiable independiente. El hash emitido por el mismo paquete y copiado sin verificar detecta corrupción posterior, pero no demuestra autoría. No se afirma firma criptográfica, certificado ni cadena de confianza de publicación.

## Recepción, activación y rollback

```powershell
python tools/local-installation/local_installation.py install C:\laboratorio\salida\emergency.zip --root C:\laboratorio\instalacion --expected-manifest-sha256 HASH_CONFIABLE
python tools/local-installation/local_installation.py activate VERSION_OBSERVADA --root C:\laboratorio\instalacion --expected-manifest-sha256 HASH_CONFIABLE
python tools/local-installation/local_installation.py serve --root C:\laboratorio\instalacion
```

El servidor imprime una URL y su identidad. No abre, cambia ni recarga ventanas. Detener con Ctrl+C. La recepción **no activa** automáticamente. La activación afecta solo al próximo proceso servidor; las pestañas y episodios abiertos conservan su versión y origen. Un escritor único protege la recepción, el puntero y el ledger. Un lock abandonado bloquea operaciones hasta revisión manual de su causa; no se elimina por temporizador.

Para volver a una versión ya recibida:

```powershell
python tools/local-installation/local_installation.py rollback VERSION_ANTERIOR --root C:\laboratorio\instalacion --expected-manifest-sha256 HASH_ANTERIOR_CONFIABLE
python tools/local-installation/local_installation.py serve --root C:\laboratorio\instalacion
```

Rollback y activate comparten la misma selección revalidada. No borran versiones anteriores ni cambian el contenido bajo un servidor ya abierto. No incluyen rollback de base de datos o datos clínicos: no existe esa persistencia en este incremento.

## PWA, cachés y alcance del rollback

Cada arranque usa un puerto efímero no usado antes **según `used-ports.json` de esta instalación**. El origen permanece fijo durante ese proceso y su snapshot no cambia al seleccionar otra versión. Si no consigue un puerto nuevo o el ledger es inválido, falla cerrado. No acepta elegir un puerto manual que pueda reemplazar una PWA anterior. No borra caches, cookies, preferencias o borradores.

Esto evita reutilizar orígenes dentro de una instalación conservada, pero **no garantiza globalmente un navegador limpio**. Otra instalación, una copia/restauración antigua del directorio, eliminación del ledger, otro servicio local o un navegador previamente usado podrían haber ocupado ese puerto. Conservar íntegro el ledger y un único directorio de instalación; no crear otro para sortear el control. Una restauración antigua requiere revisar esta condición, no asumirla resuelta por el hash de archivos.

Antes de cualquier aceptación técnica de la activación, comprobar en la página realmente cargada su build SHA y estado limpio frente a `/__local_release__`, usando navegador real. Mientras esa comprobación no exista, `browser_activation` se publica como **PENDING_ACTUAL_PAGE_IDENTITY_VERIFICATION**. Si el navegador entrega una versión distinta, **BLOCKED_SAFE**: detener esa aceptación; no afirmar rollback completo ni forzar recarga de un episodio. Las pruebas HTTP de archivos no sustituyen esa medición del navegador/service worker.

Los marcadores, instalación PWA, caché offline y preferencias pertenecen al origen anterior; no migran automáticamente al puerto nuevo. La PWA instalada antigua conserva su artefacto y no recibe una actualización remota. La referencia offline continúa condicionada al precache y a las rutas que el arnés existente verifica; análisis/exportación de nota y cálculos dependientes de API no se vuelven offline al distribuir `dist`.

## Frontera de ejecución

- Host exacto `127.0.0.1:puerto`, peer loopback y Origin del propio servidor; sin CORS abierto. No escucha en LAN ni acepta localhost como alias.
- Solo archivos del manifiesto; se vuelve a comprobar tamaño/hash al servir. Sin listados, enlaces/reparse points, archivos extra, `.git`, secretos o rutas fuera del artefacto. Fallback de SPA solo para navegación HTML sin extensión.
- `/api` y `/api/*` responden **503 JSON estático**, incluso en GET/POST/HEAD/OPTIONS; nunca HTML de la aplicación. No hay lectura ni almacenamiento de cuerpos clínicos, proveedor remoto o procesado de casos por el lanzador.
- CSP de scripts `self` más hashes SHA-256 de los scripts inline fijos del `index.html` verificado. Sin `unsafe-inline` para scripts ni `unsafe-eval`; `connect-src 'self'`, workers propios, objetos/frame/base/form cerrados. Styles permiten `unsafe-inline` por los estilos existentes de React; no se proclama prohibición total de estilos inline. Links de navegación externos no equivalen a `fetch` y no se certifican como bloqueo de todo egreso del sistema.
- No imprime URL/query/cuerpo/header del request en logs o errores. Timeout de socket de cinco segundos y máximo de dieciséis workers concurrentes; respuestas sin cache HTTP. El service worker puede mantener los recursos que el propio producto precachea.
- La instalación es para un usuario local confiable. No es un sandbox contra malware o un administrador que altere el ejecutable, la raíz o los hashes confiables. Las revalidaciones detectan alteración, no impiden que el propietario del disco escriba.

## Verificación reproducible

```powershell
python -m unittest discover -s tools/local-installation -p "test_*.py" -v
```

Los tests usan ZIP, checkout Git y servidor HTTP reales con fixtures inertes en carpetas temporales; cubren manipulación, rutas Windows/ADS/traversal, duplicados/casefold, expansión ZIP, junction NTFS nativa, selección/rollback, fallo atómico, Host/Origin duplicados y API sin HTML. La prueba de symlink nativo puede omitirse si Windows deniega crearlo (1314); la prueba de symlink ZIP y la de junction son independientes. Declarar la omisión real, no PASS de ese caso.

El coordinador registra resultados y SHA exacto del código más navegador del build real por separado. No hay CI, Sonar, auditoría externa, firma ni eficacia clínica implícitos por ejecutar esta suite.
