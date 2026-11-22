# Frontera HTTP de la API clínica general — 22/11/2026

## Alcance y base

Corrección técnica autorizada de la API existente, sobre
`0e68e5ee654e7be452cbb7cb5e5fb22b8b1127ed`, en
`codex/current-http-boundary-20261122`. Aplica al núcleo internacional y no
depende de país u hospital. No cambia aritmética, recomendaciones, estados
clínicos ni contratos de nota, escalas, pediatría o farmacología. Las ediciones
de dos pruebas M10 solo configuran su fixture HTTP para atravesar la nueva
frontera; no alteran el comportamiento del módulo ni sus trabajos pendientes.

## Comportamiento implementado

- El launcher genera una credencial aleatoria de 256 bits por ejecución y la
  entrega exclusivamente al backend general y al proceso Node de Vite mediante
  `EMERGENCY_LOCAL_API_TOKEN`. No la entrega al navegador, no usa `VITE_*`, no la
  imprime ni la comparte con los procesos T05/T06.
- En desarrollo y en `vite preview`, el proxy verifica la dirección local del
  cliente, el Host exacto de su puerto real, el Origin exacto de la interfaz y
  Fetch Metadata. Rechaza metadatos duplicados, Origin `null` y orígenes ajenos.
  No confía en `X-Forwarded-*`. Después de esa comprobación añade su credencial
  privada, sustituyendo cualquier credencial enviada por el cliente.
- Python repite las comprobaciones de Host/Origin y exige la credencial en
  todos los POST antes de leer el cuerpo o ejecutar `dispatch`. Una llamada
  directa con origen válido pero sin credencial obtiene `401`; un origen/Host
  ajeno obtiene `403`. La comparación de la credencial usa `hmac.compare_digest`.
- El chequeo de salud sigue disponible sin credencial, comprueba Host/Origin
  y solo devuelve estado y versión. No genera ni revela credenciales.
- `--allow-network` y cualquier bind no local se rechazan incluso con
  certificados TLS. TLS local sigue disponible. Los límites de cuerpo,
  conexiones, plazo total de lectura/escritura y mensajes de error existentes
  se conservan.
- Los cuatro harnesses de navegador existentes comparten la misma provisión
  efímera con su backend y proxy; el harness común también añade Origin a las
  llamadas HTTP sintéticas hechas fuera del contexto de página.

Esta es **autenticación entre procesos de una sesión local**, no identidad de
un médico, control multiusuario ni aislamiento frente a otro proceso con los
privilegios del mismo usuario del sistema. Un despliegue compartido requiere
una pasarela con identidad y autorización propias. No se ha autorizado ni
implementado ese despliegue en esta entrega.

## Arranque

Prepare los requisitos de `docs/LOCAL_REVIEW.md` y ejecute desde la raíz, con el entorno Python correspondiente activado. En Linux:

```bash
python scripts/run_local_review.py --t06-python .venv-t06/bin/python
```

En Windows, indique el modelo local verificado: `python scripts/run_local_review.py --ocr-model tools/blood-gas-ocr/models/eng.traineddata`.

El launcher admite `--ui-port` y provisiona ambos procesos sin copiar secretos
al navegador. `npm run dev` o `npm run preview` por separado siguen sirviendo
la interfaz estática; el proxy de la API general responde `503` si no dispone
de la sesión privada. Los scripts QA de navegador preparan su propia sesión.
El cambio reemplaza la antigua opción de exponer directamente esta API con
`--allow-network`; no modifica la arquitectura de los módulos en construcción.

## Verificación observada

Entorno local: Python 3.12.14 y Node 24.22.3. CI fija Node 22; no se atribuye a
esta entrega un resultado remoto todavía no observado. Solo datos sintéticos
y sockets de loopback; no llamadas clínicas externas.

| Comprobación | Resultado observado |
| --- | --- |
| `python -m unittest discover -s clinical/tests -p test_clinical_http_boundary.py -v` | 6/6 PASS: contrato legítimo, credenciales, Host/Origin/duplicados, familias API, health y rechazo de red. |
| `python -m unittest discover -s clinical/tests -p test_http_transport_security.py -v` | 18/18 PASS, incluidas las pruebas TLS y de disponibilidad existentes. |
| `python -m unittest discover -s clinical/tests -p test_clinical_note_http_privacy.py -v` | 9/9 PASS. |
| `python -m unittest discover -s clinical/tests -p test_m10_provider_errors_provenance.py -v` | 9/9 PASS. |
| `python -m unittest discover -s clinical/tests -p test_m10_skin_wound_image_audit.py -v` | 63/63 PASS; regresiones existentes tras adaptar el fixture. |
| `python -m unittest discover -s security/tests -p test_r3_http_privacy_socket.py -v` | 3/3 PASS. |
| `python -m unittest discover -s security/tests -p test_local_review_health.py -v` | 2/2 PASS. |
| Tres métodos CLI afectados de `test_security_io_boundaries.HttpTransportTests` | 3/3 PASS: rechazo de red, TLS local y bind local con credencial. |
| En `app`: `npm test -- scripts/clinical-api-boundary.test.ts` | 7/7 PASS con Python y sockets reales; carga la configuración de producto en dev y preview, prueba las cuatro familias API, rechazo de metadatos ajenos y health. Preview usa un directorio de salida temporal vacío: prueba el proxy, no renderizado visual. |
| En `app`: ESLint focal y `./node_modules/.bin/tsc -b --noEmit` | PASS. |
| En `app`: `npm run build` | PASS; aviso existente de chunks mayores de 500 kB. |
| `git diff --check` | PASS. |
| En `app`: `node scripts/check-pediatric-outpatient.mjs` | BLOQUEADO antes de navegar: Chromium termina con `socket() failed: Operation not permitted (1)` al arrancar. No equivale a aceptación funcional del navegador. Los procesos sintéticos fueron cerrados. |

Los tres métodos CLI se ejecutaron desde `clinical/tests` con:

```bash
python -m unittest test_security_io_boundaries.HttpTransportTests.test_network_bind_is_rejected_before_constructing_server test_security_io_boundaries.HttpTransportTests.test_local_tls_passes_explicit_context_to_private_server test_security_io_boundaries.HttpTransportTests.test_local_development_binding_remains_loopback -v
```

ESLint focal se ejecutó desde `app` con:

```bash
./node_modules/.bin/eslint vite.config.ts scripts/clinical-api-boundary.mjs scripts/clinical-api-boundary.test.ts scripts/clinical-test-session.mjs scripts/functional-harness.mjs scripts/check-pediatric-outpatient.mjs scripts/check-functional-v144.mjs scripts/check-ui-demo-v143.mjs
```

Total focal observado: **113 pruebas Python y 7 Vitest superadas**. Los
harnesses completos de Chromium quedan pendientes de un entorno que permita
arrancarlo; esta QA no sustituye validación clínica ni aceptación de producción.
