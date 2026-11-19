# Transporte HTTP: correcciones de disponibilidad y framing

Base: internacional `a1a1ae245d03662fff2508804c7c1112a0e238a9`. Su Sonar está en verde y tiene0incidencias abiertas. Esta entrega añade defensa sobre fallos reales no señalados por ese análisis; no inventa incidencias Sonar pendientes.

## Hechos reproducidos

- P2, disponibilidad TLS: al envolver el socket de escucha, un cliente TCP que no inicia TLS bloquea accept. Otro cliente TLS verificado agota su timeout; cerrar el primero recupera200en health. Condición: acceso al puerto HTTPS habilitado explícitamente por el operador.
- P2, disponibilidad HTTP: socket sin timeout y lectura de body por Content-Length retienen un worker con cuerpo incompleto. ThreadingHTTPServer no limita los workers. Incluso loopback permite agotamiento por procesos locales; el binding de red amplía alcance.
- P2, frontera de peticiones: no se comprueba longitud recibida tras EOF, se aceptan longitudes/transfer encodings ambiguos y JSON bajo text/plain. Las APIs son sin persistencia de notas en este adaptador; no se afirma robo de sesiones ni request smuggling en un proxy que no se ha probado.

## Cambio

`http_transport.py` usa la biblioteca estándar:16workers como máximo, timeout TLS15s en cada worker y presupuesto absoluto15s para cabeceras+cuerpo. El lector recalcula el tiempo restante antes de cada recv; un goteo de bytes no renueva el presupuesto. Se cierra el exceso de conexiones y se libera la plaza al finalizar, también ante fallo de TLS/cliente. El accept principal no realiza handshakes.

Las respuestas de error del parser son JSON estático, sin reflejar la línea privada ni perder los headers de seguridad; HEAD conserva cuerpo vacío. Se rechazan también Content-Encoding duplicados. Los logs inesperados conservan solo el nombre del tipo de excepción.

El POST exige un Content-Length único, decimal ASCII, positivo y dentro del mismo máximo previo (2*12MiB+1000000). Rechaza Transfer-Encoding, tipos simples o ambiguos, codificación no soportada, Fetch Metadata cross-site y cuerpos truncados. El frontend ya envía application/json; la metadata same-origin del proxy Vite sigue admitida. Clientes CLI deben enviar Content-Type:application/json. Esto es defensa para navegador, no autenticación. El JSON aceptado y el dispatch clínico permanecen iguales. Las respuestas cierran la conexión y conservan privacidad/headers.

## Pruebas y evidencia

18 pruebas nuevas con conexiones reales en127.0.0.1: TLS verificado con certificado efímero sintético, cliente TLS inactivo, recuperación tras handshake fallido, body parcial y goteo en headers/body, límite concurrente y recuperación, errores privados, framing, prefijo JSON truncado y roundtrip íntegro. OpenSSL genera claves de prueba solo en temporales fuera del árbol; no se incluyen claves/certificados ni credenciales de producción. CI exige EMERGENCY_REQUIRE_TLS_TESTS=1; su ausencia causa fallo en vez de SKIP silencioso.

QA completo, revisión externa y resultados remotos se registran por SHA en la PR y en el informe final externo. No cambiar umbrales, exclusiones, referencias o avisos de Trivy/Sonar. El candidato/ZIP anteriores permanecen intactos.

## Límites

No es un gateway de producción, autenticación, autorización multiusuario ni un límite de CPU/memoria por cálculo. TLS cifra, no autentica a los clientes. Bajo saturación se cierra la conexión, sin prometer un HTTP503 en un TLS aún no negociado. El plazo absoluto cubre lectura; el procesamiento clínico no se interrumpe ni cambia su aritmética. Siguen vigentes los límites CLI/TOCTOU y la mitigación temporal picomatch/Rollup. CLINICALLY_PENDING no cambia.

Fuentes primarias: [Python http.server](https://docs.python.org/3.12/library/http.server.html), [Python ssl](https://docs.python.org/3.12/library/ssl.html), [Python io](https://docs.python.org/3.12/library/io.html), [OWASP: evitar content types simples y usar Fetch Metadata](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html).

## Contraste de auditoría externa

[Gemini](https://gemini.google.com/app/85fe7282598ff279?hl=es) revisó el código sin ejecutar pruebas. Se aceptan cabeceras Content-Encoding duplicadas, errores HTML reflejados y diagnóstico por categoría; se amplían regresiones de TLS a goteo, respuesta a lector lento y fallo de creación de hilo. Sus avisos de timeout infinito en do_handshake/sendall no se aceptan: Python>=3.5 aplica duración total por operación, según [ssl](https://docs.python.org/3.12/library/ssl.html#ssl.SSLSocket.do_handshake) y [socket](https://docs.python.org/3.12/library/socket.html#socket.socket.sendall), contrastado con sockets reales. Tampoco se reproduce la fuga por fallo al crear hilo: [BaseServer._handle_request_noblock](https://github.com/python/cpython/blob/3.12/Lib/socketserver.py) cierra la petición al propagarse el error; la regresión prueba cierre y recuperación. Content-Length0 ya se rechazaba en la base y no se ha demostrado una regresión de exportación. El plazo de lectura no se confunde con límite de CPU de cálculo.
