# Revisión local integrada: T05 y T06

La aplicación incorpora `/blood-gas` y `/t06-lab`, accesibles desde Inicio. La nota clínica enlaza con la revisión de gasometrías. El arranque común conserva procesos separados y mantiene `CLINICALLY_PENDING`.

## Capacidades por plataforma

| Capacidad | Windows | Linux |
|---|---|---|
| Interfaz, cálculo/revisión de campos y navegación | Disponible | Disponible |
| Extracción T05 de PDF e imágenes con contención del árbol de procesos | Windows Job Objects | No disponible; la carga se bloquea |
| Circuito T06 R6 → B1 → JSON → Q4 con proveedores TLS sintéticos | No disponible | Disponible |

No existe todavía una plataforma que ejecute ambos adaptadores nativos entregados. El launcher declara esa diferencia y la interfaz impide presentar una capacidad no disponible como ejecutada. No se sustituye el worker Windows ni el transporte Linux por una ejecución sin contención.

T05 reutiliza el motor ácido-base canónico y exige revisión del original, muestra, valores, unidades y metadatos. FiO₂ admite el intervalo ya aceptado de 21–100 % o fracción 0,21–1; las correcciones conservan su procedencia. Cambiar la entrada invalida el resultado. La navegación desde la nota clínica no incorpora automáticamente un resultado ni una firma médica.

T06 admite únicamente su catálogo de 18 escenarios sintéticos. El consumidor Q4 y los componentes R6/B1 recuperados se conservan. Este circuito no habilita búsquedas libres, proveedores públicos, RAG ni cierre global G05.

## Preparación común

Requiere Node 22 y Python 3.12. Las órdenes siguientes se ejecutan en la raíz del repositorio. Los pins directos y los lockfiles están versionados.

```sh
npm ci --ignore-scripts --no-audit --no-fund --prefix app
npm run security:picomatch:apply --prefix app
npm run security:picomatch:check --prefix app
```

### Linux: T06 y revisión de capacidades T05

```sh
python3 -m venv .venv-local-review
.venv-local-review/bin/python -m pip install --only-binary=:all: --require-hashes -r security/requirements-ci.txt -r security/requirements-blood-gas-ci.txt
python3 -m venv .venv-t06
.venv-t06/bin/python -m pip install --only-binary=:all: -r tools/t06-localhost-lab/recovered/b1/requirements.lock
.venv-local-review/bin/python scripts/run_local_review.py --t06-python .venv-t06/bin/python
```

T06 usa `h11==0.16.0` y `cryptography==50.0.1` en su entorno separado. Los certificados de sus proveedores de prueba se generan para cada ejecución; no se instalan en el sistema. T05 declara que la extracción requiere Windows y no permite cargar documentos en este entorno.

### Windows: extracción nativa T05

En PowerShell:

```powershell
py -3.12 -m venv .venv-local-review
.\.venv-local-review\Scripts\python.exe -m pip install --only-binary=:all: --require-hashes -r security/requirements-ci.txt -r security/requirements-blood-gas-ci.txt
npm ci --ignore-scripts --no-audit --no-fund --prefix tools/blood-gas-ocr
.\.venv-local-review\Scripts\python.exe scripts/prepare_blood_gas_model.py
.\.venv-local-review\Scripts\python.exe scripts/run_local_review.py --ocr-model tools/blood-gas-ocr/models/eng.traineddata
```

La preparación descarga únicamente el modelo público indicado en `tools/blood-gas-ocr/MODEL.json`, comprueba tamaño y SHA-256 y conserva la licencia Apache-2.0. El procesamiento posterior usa ese modelo local. No descarga modelos durante una extracción. T06 informa que su transporte requiere Linux y permanece deshabilitado.

`RUN_LOCAL_REVIEW.cmd` permite invocar el mismo launcher desde un entorno Python previamente activado. Los launchers específicos T05 siguen disponibles; para su servidor estático se necesita antes `npm run build --prefix app`.

## Abrir, detener y repetir

El launcher imprime `http://127.0.0.1:5173`, comprueba los puertos y arranca los servicios compatibles. `--ui-port` permite otro puerto de interfaz; los backends usan 8765 (clínico), 8766 (T06) y 8767 (T05). Un puerto ocupado detiene el arranque; no se termina ningún proceso ajeno. `Ctrl+C` cierra los procesos creados por la sesión. `--check` comprueba los prerrequisitos y enumera capacidades sin arrancar servicios.

Use únicamente datos sintéticos. Los recibos y logs propios se escriben en `.local-review/`, excluido de Git. La extracción y su ticket se revocan al rechazar el documento; no se añaden originales a la nota ni a exportaciones por esta integración.

El modo local fija loopback, comprueba Host y dirección de conexión y habilita las proxies nuevas únicamente en esa sesión. Conserva Origin y la autenticación de sesión T05. Las cabeceras limitan las solicitudes de la aplicación al mismo origen y al WebSocket local de desarrollo. Esto no demuestra aislamiento de red del sistema operativo.

La API clínica general añade una credencial aleatoria de proceso por arranque. El launcher la entrega solo a Python y al proxy Vite mediante `EMERGENCY_LOCAL_API_TOKEN`; no usa una variable `VITE_*`, no la imprime ni la entrega a T05/T06 o al navegador. Vite verifica Host, Origin, dirección local y metadatos de navegador antes de añadir la credencial al envío a `127.0.0.1:8765`. La API vuelve a validar el origen y exige esa credencial en todos los POST. El chequeo de salud solo devuelve estado/versión, con Host y Origin comprobados, sin emitir credenciales. Los consumidores de nota, escalas, pediatría y farmacología conservan sus contratos y la ruta a través del mismo origen.

El arranque directo con `--allow-network` o una interfaz no local se rechaza incluso si se aportan certificados TLS. Esta autenticación identifica procesos de la sesión local, no médicos ni usuarios; no habilita uso multiusuario. Use el launcher para revisión sintética. Una distribución compartida requiere una pasarela con identidad y autorización propias; configurar `VITE_CLINICAL_NOTE_API_BASE` por sí solo no proporciona esas garantías. Los scripts de QA de navegador usan la misma frontera y una credencial efímera independiente por ejecución.

La aceptación de navegador utiliza un perfil nuevo, sin un service worker previo. La marca de sesión impide registrar uno nuevo; no afirma borrar un worker instalado anteriormente. Para una reproducción manual utilice un perfil limpio o un puerto de interfaz nuevo.

## Verificación

`Local review integration` ejecuta T05 nativo en Windows y T06 nativo en Linux. Los scripts `scripts/check_local_review.py` y `app/scripts/check-*-local-review.mjs` comprueban la aplicación compuesta, sus proxies, los recibos del backend y el cierre del launcher. No sustituyen el transporte por mocks.

`Security and quality` invoca esos jobs como workflow reutilizable y combina sus mediciones Python con las pruebas portables antes de Sonar. La combinación comprueba commit, árbol, versión y configuración; recoge también el arranque, la preparación del modelo y los subprocesos Windows. Solo publica cobertura nativa tras completar sus pruebas. La configuración conserva los datos al cierre por SIGTERM en Linux. El código de T06 bajo `tools/` permanece fuera de `sonar.sources`; sus pruebas HTTP/TLS y de navegador se informan por separado.

Las pruebas portables de T05 también se ejecutan en Clinical QA con OCR local. Las tres pruebas que requieren Windows se omiten explícitamente en Linux y se ejecutan en el job Windows. Los resultados de otra rama o de los paquetes históricos no se atribuyen a esta composición.

Procedencia: [T05](BLOOD_GAS_LOCAL.md), [T06](../tools/t06-localhost-lab/README.md) y [registro de integración](../clinical/qa/T05_T06_INTEGRATION_20261119.md).
