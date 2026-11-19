# T05 — revisión local de gasometrías sintéticas

Estado: **CLINICALLY_PENDING**. La integración y sus pruebas técnicas no conceden
autorización asistencial ni `GO_RELEASE`. No cargar documentos de pacientes.

## Procedencia

Se reconstruyeron y comprobaron tres árboles consecutivos desde el commit
`1d0652ebcef9b5990edd9e5745b0c06f8d6b8274`:

| Paquete y delta | Árbol comprobado después de aplicar |
|---|---|
| T05 R3, `BLOOD_GAS_R3.patch` | `9e6ad2d55b38a3d3130a44bb574c4cdbec6694c1` |
| PAR01, `GASOMETRIA_P2_DELTA.patch` | `eb9e263f36856addac2de42835c7b191c4856d41` |
| FiO₂ corregida, `FIO2_DELTA.patch` | `0b9a2ecaab038b7624e8a0855c54f220a71882da` |

La integración toma sus archivos propios sobre PR32
`abdeae442a151ce1b1fe0786725991a7d35bc558`, árbol
`feabbe55ecceea886ccde20aec526ff920dcb473`. Conserva los avances de PR32 y el
motor canónico `acid_base_hyperglycemia.py`. Las evidencias históricas de los
paquetes no se contabilizan como pruebas de este árbol integrado.

El intervalo de admisión de FiO₂ aprobado por el propietario médico el
19/11/2026 es **21–100 %**, o **0,21–1 como fracción**, incluidos los extremos.
La comparación se realiza con el decimal original y la unidad original. El
valor `0.4 %` representa `0.004` y se bloquea; no se corrige automáticamente.
Una corrección conserva el literal, la unidad, la razón y el cotejo visual.

## Capacidad por plataforma

El servidor de revisión puede arrancar en Windows y Linux. La extracción de
documentos de la aplicación requiere **Windows Job Objects**. El worker
original conserva sus límites de memoria, CPU, tiempo y salida; no existe un
fallback de extracción sin esa contención.

`GET /api/blood-gas/session` declara `synthetic_only: true`, un token efímero,
`required_platform: "win32"` y `extraction_available: true` solo en Windows.
La interfaz exige un booleano real y deshabilita la carga cuando la capacidad
no está disponible o el contrato de sesión es incompleto. La declaración de
plataforma no sustituye la instalación de dependencias ni acredita que el
worker haya procesado un documento.

Las pruebas de funciones puras pueden ejecutar OCR/PDF sintético directamente
en Linux. Eso **no demuestra** extracción contenida a través de la aplicación
en Linux. La CSP limita solicitudes de la página; no acredita aislamiento de
red del navegador ni del sistema operativo.

## Instalación reproducible

Usar un entorno Python virtual compatible con los requisitos clínicos de la
base. Los requisitos de T05 están fijados en
`clinical/requirements-blood-gas.txt`: Pillow 13.0.0, pypdf 6.21.4,
pypdfium2 5.13.0 y reportlab 5.0.1. El pin de reportlab coincide con PR32.

Desde la raíz del repositorio, con ese entorno activado:

```sh
python -m pip install -r clinical/requirements-blood-gas.txt
npm ci --ignore-scripts --prefix tools/blood-gas-ocr
python scripts/prepare_blood_gas_model.py
```

El paquete Node tiene su propio `package-lock.json`; fija `tesseract.js` y
`tesseract.js-core` 7.0.0 sin modificar el lockfile de `app`.

El modelo `eng.traineddata` procede del repositorio oficial
[tesseract-ocr/tessdata_fast, tag 4.1.0](https://github.com/tesseract-ocr/tessdata_fast/tree/4.1.0).
El SHA-256 de la descarga oficial coincide con el del modelo del
paquete T05. Tiene 4.113.088 bytes y SHA-256
`7d4322bd2a7749724879683fc3912cb542f19906c83bcc1a52132556427170b2`.
Su licencia Apache-2.0 se conserva en
`tools/blood-gas-ocr/TESSDATA_LICENSE`; las URLs y hashes constan en
`tools/blood-gas-ocr/MODEL.json`. El modelo se instala fuera del control de
versiones. El worker comprueba el nombre y el hash antes de iniciar OCR y no
descarga modelos durante la revisión.

Variables del proceso:

| Variable | Valor o función |
|---|---|
| `BG_OCR_MODEL` | Ruta absoluta a `tools/blood-gas-ocr/models/eng.traineddata` |
| `NODE_PATH` | Ruta absoluta a `tools/blood-gas-ocr/node_modules` |
| `BG_TEST_FONT` | Ruta absoluta a `clinical/assets/fonts/DejaVuSans.ttf`, fuente versionada para las imágenes de prueba |
| `BG_PYTHON` | Intérprete opcional para los launchers `.cmd`; por defecto usan `python` en el entorno activado |

## Servidor y conexión de la interfaz

En modo standalone se sirve el build existente de `app/dist` y se elige un
puerto loopback aleatorio:

```sh
python clinical/scripts/blood_gas_local.py
```

`RUN_BLOOD_GAS.cmd` conserva este modo. El HTML servido incluye la marca
`blood-gas-local` para desactivar el registro de service worker en la sesión
efímera. La integración de `main.tsx` debe respetarla.

Para la interfaz común en `http://127.0.0.1:5173`:

```sh
python clinical/scripts/blood_gas_local.py --port 8767 --ui-port 5173
```

El proxy de la interfaz dirige `/api/blood-gas` al backend y conserva el
`Origin` original. `--ui-port` admite únicamente un entero entre 1 y 65535 y
añade solo `http://127.0.0.1:<puerto>` a la lista de orígenes; `localhost`, otros
puertos, HTTPS u orígenes remotos no se infieren. Todas las mutaciones
requieren además `X-Session` y el `Host` exacto del backend. No se habilita
CORS abierto. El servidor reutiliza el transporte acotado de PR32.

`/extract` recibe bytes del documento. `/regions`, `/review` y `/reject`
reciben `application/json` con encuadre inequívoco. El decoder rechaza claves
duplicadas, constantes no finitas y números JSON no nulos que se perderían
como cero al convertirlos. La misma protección contra pérdida no nulo→cero
se aplica a los literales de analitos extraídos o transcritos; conserva el
cero explícito y no añade mínimos fisiológicos. Los errores HTTP usan JSON
estático, sin reflejar líneas de solicitud, y conservan las cabeceras de
privacidad.

## Pruebas y límites

Con dependencias, modelo y fuente configurados:

```sh
python -B -m unittest discover -s clinical/tests -p 'test_blood_gas_*.py' -v
python -B -m unittest discover -s clinical/tests -p 'test_acid_base_review.py' -v
cd app
npm test -- src/pages/BloodGas.test.tsx
npm run typecheck
```

`test_blood_gas_geometry.py`, `test_blood_gas_multiformat.py` y parte de
`test_blood_gas_par01.py` necesitan OCR/PDF real, modelo y fuente. Las pruebas
de frontera HTTP, seguridad numérica, metadatos y revocación usan datos
sintéticos y no acreditan rendimiento diagnóstico.

Estos tres métodos necesitan el worker Windows real y llevan un `skipUnless`
explícito fuera de Windows:

- `Validation.test_contained_worker`.
- `Validation.test_http_confirmation_and_revocation`.
- `ReviewContract.test_multiformat_extraction_review_and_revocation_without_socket`.

El job Windows de integración debe ejecutarlos sin omitirlos, junto con el
recorrido de navegador. Un resultado Linux con esos tres métodos omitidos no
equivale a una verificación del worker. La tipografía y el rasterizador son
parte de la evidencia de OCR: cualquier diferencia de campos debe registrarse
como fallo y revisarse, sin rebajar la expectativa para obtener un PASS.

Los hallazgos P3 históricos, las limitaciones de calidad de imagen y la
validación prospectiva siguen requiriendo adjudicación propia. Esta entrega
no declara `BLOOD_GAS_IMAGE_TECHNICALLY_COMPLETE` ni cierra los hallazgos que
no haya vuelto a verificar.
