# T06 integrado: laboratorio de metadatos en localhost

Este componente ejecuta el cliente **R6**, el transporte **B1** y el consumidor React **Q4** recuperados. El proveedor es un servidor TLS sintético en loopback. El resultado es una prueba técnica de metadatos; no busca pacientes, no consulta proveedores públicos y no proporciona recomendaciones asistenciales. Se conserva `CLINICALLY_PENDING`; G05 global, autenticidad pública y RAG permanecen pendientes.

## Implementación incorporada

- `recovered/b1/g01_https_transport/`: transporte B1 original con su presupuesto de tiempo, worker separado y validación HTTPS.
- `recovered/b1/frozen_r6/emergency_apis/`: cliente y normalización R6 originales.
- `recovered/b1/frozen_r6/fixtures/` y `recovered/b1/tests/lab*.py`: respuestas y generación de certificados de laboratorio, con verificación de certificado y hostname activa.
- `lab/backend/loopback_worker.py`: perfil que dirige exclusivamente a `127.0.0.1`, sin resolución pública.
- `lab/backend/server.py`: adaptador del laboratorio incorporado; reutiliza `clinical/scripts/http_transport.py` para limitar globalmente los trabajadores a cuatro y el plazo de lectura a cinco segundos. Valida Host, Origin, Fetch Metadata y el encabezado fijo de la aplicación antes del transporte.
- `app/src/t06/`: los cinco archivos Q4 conservan sus bytes. La nueva página `T06Lab.tsx` incorpora petición acotada, carga, error, cancelación, descarte de respuestas anteriores y cancelación al salir de la ruta.

`SOURCE_PROVENANCE.json` identifica el paquete de origen, sus árboles históricos y cada archivo copiado. Los comentarios originales que describen consumidores aislados documentan su procedencia; esta incorporación monta Q4 solamente en el laboratorio local. El proveedor sintético sustituye al servicio público; R6, B1, TLS, normalización y Q4 sí se ejecutan realmente.

### Adaptación de prueba Unicode · 26/11/2026

El recibo histórico permanece byte-idéntico (SHA-256 `e39c0a81ea1f0af477c378053459b9563ad7e7b9496e7c00a9418e438df76929`). `CURRENT_ADAPTATIONS.json` declara una única adaptación: dos literales surrogate de `viewModel.test.ts` se construyen en ejecución para evitar strings AST no válidos en Protobuf de Sonar. Se preservan los14 controles y todas las aserciones. El original se conserva intacto en `provenance/viewModel.test.ts.original.txt`, con su SHA histórico.

La comprobación vigente exige18 destinos idénticos al recibo, la fuente original número19 conservada y exactamente la transformación revisada del test actual, con su SHA nuevo. No se presentan19 destinos actuales como byte-idénticos. Los dos adaptadores históricos siguen con su alcance previo. Pruebas negativas rechazan borrar una aserción, alterar el original o reetiquetar un hash. Los manifiestos/hashes anteriores no se sustituyen, ni se elimina la guarda de procedencia. T06 Linux debe pasar nuevamente su prueba nativa; una prueba pura local en Windows no certifica su transporte.

## Entorno separado y arranque

Mantener un entorno Python propio de T06. El lock original `recovered/b1/requirements.lock` conserva `h11==0.16.0` y `cryptography==50.0.1`. No sustituir el entorno del backend clínico ni los lockfiles Node de la aplicación.

Preparación explícita de un entorno vacío, desde la raíz del repositorio:

```sh
python3 -m venv /ruta/privada/t06-venv
/ruta/privada/t06-venv/bin/python -m pip install -r tools/t06-localhost-lab/recovered/b1/requirements.lock
```

El lock original fija las dos dependencias directas; no congela por sí solo sus transitivas, Python, OpenSSL ni el sistema operativo. En esta incorporación se ejecutó **Python 3.12.14**, h11 **0.16.0** y cryptography **50.0.1**. El autor de B1 declaró Python **3.13.18**; no se afirma reproducción de su versión de intérprete. El laboratorio histórico usó cryptography **43.0.0**, dato conservado como antecedente y no aceptado silenciosamente por el nuevo launcher.

Arranque del backend T06:

```sh
/ruta/privada/t06-venv/bin/python -B tools/t06-localhost-lab/run_local.py \
  --python /ruta/privada/t06-venv/bin/python \
  --port 8766 --ui-port 5173 \
  --evidence-dir /ruta/privada/recibos-t06
```

El launcher comprueba las dependencias y termina con un error concreto si faltan o difieren. No instala paquetes automáticamente. Mantiene el intérprete del venv y solo abre el backend en `127.0.0.1`. Los certificados y claves sintéticos se generan temporalmente para cada ejecución y no se guardan en Git. Ctrl+C detiene el backend propio.

El transporte B1 entregado depende de grupos de procesos y selectores de pipes POSIX. El launcher y la entrada directa del servidor exigen Linux; no hay portabilidad Windows acreditada. La página siempre muestra este requisito. Cuando el modo local declara una plataforma diferente mediante `meta[name="emergency-local-platform"]`, desactiva la ejecución sin hacer peticiones al circuito. La ausencia del metadato no acredita un backend disponible: si no existe un backend Linux con el proxy previsto, se presenta un error controlado.

La ruta React de la composición es `/t06-lab`. El coordinador incorpora el proxy local de la aplicación, sin añadir T06 al dispatcher clínico:

| Entrada desde la aplicación | Destino fijo |
|---|---|
| `/api/t06-lab/search?scenario=<catálogo>` | `http://127.0.0.1:8766/api/search?scenario=<catálogo>` |
| `/api/t06-lab/lab-status` | `http://127.0.0.1:8766/api/lab-status` |

El proxy usa `changeOrigin: true`. El consumidor envía `X-Emergency-T06-Lab: synthetic-loopback`; es una guarda contra solicitudes simples ajenas a la aplicación, no una credencial. Los Origin permitidos son los de localhost/127.0.0.1 en el puerto UI indicado y el propio puerto backend. El navegador y el backend deben compartir el mismo entorno de red. Un build estático sin el proxy local no crea un servicio T06.

## Contrato y verificaciones

La entrada consiste exclusivamente en un catálogo cerrado de 18 escenarios. Se rechazan consultas libres, parámetros adicionales/repetidos, cuerpos GET, encuadre ambiguo, origen indebido y métodos de escritura. Se conservan los límites de R6/Q4, incluido el máximo de 2.000.000 bytes para leer la respuesta en la página. Los errores no reflejan contenido del proveedor. Al cancelar o cambiar de ruta/escenario se invalida el resultado anterior.

Pruebas focales desde la raíz:

```sh
/ruta/privada/t06-venv/bin/python -B tools/t06-localhost-lab/test_integration.py
cd app
npm test -- src/t06 --maxWorkers=2
npm run typecheck
```

El test backend utiliza HTTP y TLS reales contra puertos loopback efímeros; comprueba circuitos válidos, el límite Unicode agregado, rechazos antes del transporte y errores de proveedor. Los tests React comprueban Q4 y el nuevo ciclo de vida de la página; por sí solos no sustituyen la comprobación del navegador y del proxy de la composición final. Los resultados de otros árboles o del laboratorio histórico no se heredan como un PASS nuevo.

Con la aplicación compuesta ya iniciada en modo local y sin otro cliente T06 concurrente, ejecutar desde la raíz:

```sh
CHROMIUM_PATH=/ruta/a/chromium \
T06_APP_URL=http://127.0.0.1:5173/ \
T06_BACKEND_EVIDENCE_DIR=/ruta/de/la/sesion/t06 \
T06_BROWSER_OUT=/ruta/privada/qa-t06-browser \
node app/scripts/check-t06-local-review.mjs
```

El script navega Inicio → T06, ejecuta los 18 escenarios por los controles reales y comprueba cancelación, cambio de escenario, vuelta a Inicio y recuperación. No sustituye respuestas. Correlaciona los identificadores visibles con los recibos del backend y sus registros TLS. Los abortos previos a cabeceras se asocian por escenario y ventana aislada, sin atribuirles un identificador visible inexistente. Guarda resultados JSON, HAR sin cuerpos, recibos sintéticos y una captura. Las peticiones y WebSockets instrumentados se limitan al origen local; esto no acredita aislamiento de todo el host.

Los hooks Python limitan las operaciones instrumentadas del backend y del worker a loopback. No acreditan aislamiento exhaustivo del navegador, sus extensiones o todo el sistema operativo. Los enlaces canónicos de metadatos se conservan en Q4, pero no se siguen durante las pruebas sintéticas.
