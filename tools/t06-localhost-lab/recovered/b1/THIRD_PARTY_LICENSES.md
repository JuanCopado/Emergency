# Licencias y versiones (verificadas con importlib.metadata en este entorno)
| Componente | Versión | Licencia | Uso |
|---|---|---|---|
| CPython | 3.13.18 | PSF License | runtime |
| OpenSSL (vía `ssl`) | 3.5.9 | Apache-2.0 | TLS |
| h11 | 0.16.0 | MIT | parser HTTP/1.1 (runtime) |
| cryptography | 50.0.1 | Apache-2.0 OR BSD-3-Clause | solo tests |
Descartadas: `urllib3` 2.7.0 (MIT; deadline solo por operación de socket, DNS bloqueante, redirecciones/descompresión a configurar) y `requests`/`httpx2` (mismo problema de deadline total + más superficie). Se elige h11 por ser sans-IO: no tiene timeouts ocultos ni DNS/conexiones propias.
**Licencia del código propio de G-01: NO ASIGNADA.** R6 no incluye licencia; decide el propietario del repositorio (no se inventa una).
