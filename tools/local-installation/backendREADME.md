# Backend individual sin conexión

`CLINICALLY_PENDING` · `NO_GO_CLINICAL_RELEASE`

El paquete conserva los motores y datos canónicos del commit indicado. No cambia
fórmulas, dosis ni confirmaciones clínicas. `collect_backend(repo, wheelhouse,
revision)` devuelve un mapa de rutas y bytes para incorporarlo al ZIP firmado.
Lee los scripts clínicos y su cierre de importaciones desde objetos Git exactos;
incluye los módulos del índice canónico, registros, política de privacidad y las
fuentes tipográficas con sus licencias. No incorpora originales editoriales,
préstamos documentales, imágenes de pacientes ni archivos de usuario.
Las seis identidades de wheels se cotejan obligatoriamente con
`requirements-runtime-ci.lock` leído del mismo objeto Git de entrega. Se rechazan
bytes alterados aunque conserven el nombre, versiones distintas, duplicados,
paquetes ausentes y entradas extra. Un lock creado desde el wheelhouse no es
fuente de confianza del empaquetador.

La infraestructura del lanzador se incorpora desde una lista explícita de seis
archivos de `tools/local-installation`, también desde objetos Git exactos. El
empaquetador se ejecuta después de confirmar estos archivos en el SHA de entrega.
Los hashes del manifiesto
interno prueban integridad; la autenticidad requiere verificar previamente la
firma externa y la clave pública fijada por el instalador.

## Instalación reproducible

Este primer destino requiere **Python 3.12 x64 instalado en Windows**. No es un
ejecutable autónomo ni redistribuye el intérprete de otra aplicación. Los wheels
incluidos corresponden a `win-amd64`; no se declara compatibilidad de instalación
con ARM64 nativo ni Linux. El proceso x64 funciona en el Windows ARM64 de JUAN-C.

Se crean dependencias aisladas mediante `install_runtime(release_root,
runtime_root, python_executable)`: venv independiente y pip con `--isolated`,
`--no-index`, `--require-hashes`, `--only-binary=:all:` y `--no-compile`. No modifica
paquetes ni configuración globales. No necesita descargar dependencias durante
la instalación. Los seis paquetes fijados son ReportLab 5.0.1, Pillow 13.0.0,
charset-normalizer 3.5.2, cryptography 50.0.2, cffi 2.1.1 y pycparser 3.12.
El recibo del entorno verifica versiones y bytes de la instalación; los paths de
venv son específicos del equipo, no un binario idéntico entre equipos.

Referencias de pip: [instalación sin índice](https://pip.pypa.io/en/stable/user_guide/#installing-from-local-packages)
y [modo de hashes](https://pip.pypa.io/en/stable/topics/secure-installs/).

## Sesión privada

`BackendSession(release_root, ui_port, revision, python_executable)` proporciona
`request(path, payload) -> (status, objeto JSON)`, `close()` y contexto `with`.
El llamador autentica la versión completa antes de ejecutar su código y verifica
el recibo del entorno. El trabajador escucha exclusivamente en `127.0.0.1` y usa
un token nuevo de 256 bits transmitido por stdin privado. El token no llega al
frontend, argumentos de proceso, variables, archivos ni logs.

Se conserva la comprobación canónica de Host/Origin/token. Solo se heredan las
variables mínimas de Windows; se excluyen credenciales, proxies y PYTHONPATH.
El trabajador usa `-I -B`, temporales propios y no registra contenido clínico.
Al cerrar normalmente elimina sus temporales; no elimina exportaciones que el
usuario haya guardado. En Windows, un Job Object del padre elimina al trabajador
si el lanzador termina abruptamente. Se asigna antes de transmitir configuración
o token. Los temporales se guardan en `%LOCALAPPDATA%/Emergency/PrivateWork/`
con hash de la instalación y UUID de sesión. Una marca contiene solo esquema y
UUID; el lease exclusivo del sistema está fuera del directorio de datos.
Una terminación abrupta puede dejar residuos hasta el siguiente inicio: este
elimina únicamente carpetas marcadas sin lease activo, tras verificar sus rutas
y descendientes sin enlaces/reparse points. Preserva sesiones activas y carpetas
sin marca válida. No se declara borrado seguro. Una política de auditoría Python bloquea DNS, conexiones salientes,
datagramas y creación de procesos. Es una barrera sobre código de confianza,
no un sandbox de sistema operativo para código hostil o extensiones arbitrarias.

## Capacidades y límites explícitos

Disponibles: catálogos y cálculo determinista existente de escalas, medicación
aguda y pediatría; nota clínica y terapia canónicas; preparación de documentos y
aceptación local existentes; exportación PDF, DOCX y JSON con sus revisiones
obligatorias. El límite de entrada original se conserva: 26.165.824 bytes JSON,
con un máximo de archivo binario canónico de 12 MiB. Respuesta limitada a 32 MiB;
tiempo de transporte determinista de 60 segundos.

La preparación de texto extrae documentos de texto admitidos por el código
canónico. Preparar un PDF binario no equivale a extraer su texto ni interpretarlo.
El importador de escalas conserva su pdf.js existente en el frontend. No se
ofrece proveedor remoto de visión/LLM: `upload/interpret` responde 503.

La gasometría OCR de `app/src/pages/BloodGas.tsx` depende de
`clinical/scripts/blood_gas_local.py` y de su extracción Windows/Node OCR y tickets
revisados. Ese runtime no se empaqueta en este incremento; `/api/blood-gas/*`
debe mostrar `OCR_RUNTIME_NOT_PACKAGED` mediante el lanzador, sin inventar una
calculadora manual ni sustituir fórmulas. No se declara T05/T06 ejecutado aquí.

## Verificación ejecutada

El ensayo real en JUAN-C instaló los seis wheels sin índice y verificó sus hashes
contra los publicados en PyPI. La suite nueva tiene 14 pruebas: catálogos,
cálculo NEWS2 y rechazo de revisión obsoleta, importación TXT, exportaciones
PDF/DOCX/JSON con bloqueos de revisión, aceptación de trama sintética de 21 MiB,
rechazo de sobrelímite/NaN, tokens/origen, limpieza y ausencia de bytecode/token,
entorno sin secretos, bloqueo de TCP/DNS/UDP/procesos y muerte real del trabajador
propio tras salida abrupta de su padre en Windows, limpieza posterior de su
carpeta y preservación de sesiones concurrentes/carpetas sin marca. No sustituye auditoría
clínica, pruebas del producto completo ni auditoría independiente.

Ejecución reproducible desde el repositorio, después de materializar el paquete
y su venv firmado/verificado:

```powershell
$env:EMERGENCY_BACKEND_RELEASE = 'C:\ruta\version-verificada'
$env:EMERGENCY_BACKEND_PYTHON = 'C:\ruta\runtime\Scripts\python.exe'
& $env:EMERGENCY_BACKEND_PYTHON -m unittest discover -s tools/local-installation -p test_backend_runtime.py -v
```

Sin ambas rutas las pruebas de integración se marcan SKIP, nunca PASS ficticio.
El recibo externo de entrega conserva el commit, hashes y log del ensayo.

