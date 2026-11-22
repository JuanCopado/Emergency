# Revisión focal de Sonar y cobertura de la frontera local — 22/11/2026

## Contexto observado

PR70, revisión `c5d329bcf120da705d877c7b9ac8532b03416888`, conserva la
frontera local introducida en `a23b1bd8416bfb043ed753183716ae6bbae3aea5`.
El análisis informó S5332 en `clinical_http_boundary.py` al construir el
origen de la interfaz mediante un host interpolado. No se observó una
exposición externa: el bind, la dirección de conexión, Host/Origin y la
credencial entre procesos siguen limitando el servicio a la sesión local.
El gate remoto también detectó cobertura insuficiente del código nuevo.

## S5332: orígenes loopback explícitos

La [documentación primaria S5332 publicada por SonarSource](https://github.com/SonarSource/sonar-python/blob/master/python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S5332.html)
incluye un apartado **Exceptions**: no informa el uso de URLs cuyos hosts
solo resuelven dentro del entorno privado de ejecución, entre ellos los
hosts loopback. Se consultó el 22/11/2026. La documentación explica además
el riesgo real de interceptación y modificación del tráfico HTTP fuera de
esa excepción; una red interna compartida no equivale a loopback.

La actualización enumera directamente `http://127.0.0.1:{ui_port}` y
`http://localhost:{ui_port}`. Mantiene la comprobación previa de que el puerto
sea un entero válido, y no recibe un host configurable o derivado de la
petición. Expresa la frontera admitida sin esconder el esquema, concatenar
fragmentos para evitar la regla ni añadir exclusiones. El listener local
continúa siendo HTTP, y el TLS opcional del backend conserva su contrato.
El resultado de una nueva ejecución remota de Sonar queda pendiente.

## S1313: dirección IPv4 representada en IPv6

`::ffff:127.0.0.1` permanece como literal en la lista exacta de direcciones
de conexión admitidas en `clinical-api-boundary.mjs`. Es la representación
IPv4-mapped de loopback, conforme a [RFC 4291, apartados 2.2 y 2.5.5.2](https://datatracker.ietf.org/doc/html/rfc4291#section-2.5.5.2).
No es una IP de infraestructura privada, un secreto ni una dirección de
destino configurable. Se compara con `request.socket.remoteAddress`, no con
`X-Forwarded-For` ni otra cabecera que el cliente pueda elegir. Los controles
de Host/Origin y la credencial siguen siendo independientes de esa comparación.

La [implementación primaria S1313 de SonarJS consultada](https://github.com/SonarSource/SonarJS/blob/master/packages/analysis/src/jsts/rules/S1313/rule.ts)
contiene excepciones para `127.` y `::1`; su comprobación específica de prefijo
IPv4 en IPv6 usa `::ffff:0:`. Ese prefijo no coincide con el literal anterior.
Esta diferencia explica por inspección que el literal se marque para revisión;
no demuestra una conexión insegura ni justifica cambiar la dirección admitida
para silenciar el analizador. No se ha ocultado, excluido ni cerrado el hotspot
remotamente. Esta revisión tampoco habilita uso multiusuario o acceso por red.

## Cobertura funcional añadida

Los siete tests que cargan la configuración real de Vite se conservan. Se
añaden cuatro tests en `clinical-api-boundary-direct.test.ts`, que pasan el
plugin importado directamente a Vite con `configFile:false`. Esto permite que
Vitest mida ese mismo middleware, en lugar de una copia de la configuración
cargada fuera de su instrumentación. Las peticiones recorren sockets reales
Vite→Python y verifican las cuatro familias API, sustitución de credenciales
del navegador, rechazo de Host/Origin/duplicados/Fetch Metadata y spoofing de
cabeceras de proxy, health mínimo, rutas ajenas y fallo `503` sin sesión.

Python añade tres regresiones sobre la configuración efectiva: rechazo de
direcciones no loopback, puertos de interfaz inválidos y credenciales de tipo
o formato incorrectos. Los dos últimos casos usan la factoría real, que cierra
su socket al rechazar la configuración. También se comprueban ambos orígenes
locales admitidos y nombres de host engañosos.

## Resultados locales observados

| Comando | Resultado |
| --- | --- |
| `python -m unittest discover -s clinical/tests -p test_clinical_http_boundary.py -v` | 9/9 PASS. |
| En `app`: `npm run test:coverage -- scripts/clinical-api-boundary.test.ts scripts/clinical-api-boundary-direct.test.ts --coverage.reportsDirectory=<directorio-temporal>` | 11/11 PASS. Se conserva la configuración de cobertura del proyecto; solo cambia el destino del informe de esta ejecución focal. |
| En `app`: `./node_modules/.bin/eslint scripts/clinical-api-boundary-direct.test.ts` | PASS. |
| En `app`: `./node_modules/.bin/tsc -b --noEmit` | PASS. |
| `git diff --check` | PASS. |

Medición V8 observada de **`clinical-api-boundary.mjs`**: 34/34 líneas,
39/39 instrucciones y 9/9 funciones cubiertas; 43/45 ramas (95,55%). Es
cobertura del middleware en esta ejecución focal, no una nueva cifra de
cobertura global de PR70. No se modifican umbrales, exclusiones ni políticas
de Sonar. Solo se utilizaron datos sintéticos y procesos locales.
