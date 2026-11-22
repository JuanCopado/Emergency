# R11 · fotografías en móvil: HEIC/HEIF y tamaño (medición del guardián de imágenes)

**22/11/2026 · CLINICALLY_PENDING · evaluación técnica, sin cambio clínico ni reescalado automático**

Medido con el guardián real (`image_upload_guard`, vía `prepare_upload`) sobre imágenes **sintéticas**. No se envía nada a ningún proveedor ni se reduce ninguna imagen.

## Resultados

| Entrada sintética | Resultado | Motivo |
|---|---|---|
| `.heic` / `.heif` con cabecera ISO-BMFF `ftyp` | Rechazada | `unsupported_declared_extension` |
| Contenido HEIC con extensión `.jpg` | Rechazada | `unrecognized_type` |
| JPEG 12,2 MP (4032×3024), 5,8 MB | **Aceptada** | — |
| JPEG 12,5 MP (4080×3072) | Rechazada | `decoded_raster_too_large` |
| JPEG 15,9 MP, 16,6 MP, 17 MP, 20 MP, 49,9 MP | Rechazadas | `decoded_raster_too_large` |
| JPEG 108 MP (12000×9000) | Rechazada | `too_many_pixels` |

**Regla real** (`image_upload_guard.py`, líneas 328 y 296): se rechaza si `ancho × alto × 4 > 50 000 000` (≈ 12,5 megapíxeles) o si supera 100 millones de píxeles; el tope de transferencia es 12 MiB. Rechaza antes de decodificar por completo, como protección técnica frente a imágenes que se expanden mucho (no es un criterio clínico).

## Qué significa para el móvil

- **HEIC/HEIF no se aceptan.** Muchos iPhone guardan HEIC; al seleccionarlos desde un `<input type="file">` el sistema puede convertirlos a JPEG o no (**No verificado**, depende de la versión y de los ajustes de «Transferir a Mac o PC»/«Más compatible»). Si llega HEIC, el rechazo es explícito y seguro.
- **El límite de ≈ 12,5 MP rechaza fotos de uso habitual.** 4032×3024 (12,2 MP, iPhone en modo estándar) pasa; 4080×3072 (12,5 MP, varios Android) no pasa, ni los modos de 16, 48, 50 y 108 MP. Un clínico con un Android reciente puede ver rechazada la fotografía de una herida.
- **No hay reescalado en el cliente ni en el servidor.** Reducir una imagen cambia de forma irreversible lo que se analiza y lo que se archiva como observación; no se hace automáticamente.

## Cambio incluido (solo mensajes)

Antes, estos rechazos mostraban «O ficheiro foi recusado na verificação do nome, formato ou integridade», que no explicaba nada accionable. Ahora:

- Tamaño (`decoded_raster_too_large`, `too_many_pixels`): indica el límite (≈ 12,5 MP), que **nada se redujo ni se envió**, que si la cámara ofrece una resolución menor puede usarla y que la reducción se hace fuera de la aplicación, conservando el original, **por decisión del usuario**.
- Formato (`unsupported_declared_extension`): nombra HEIC/HEIF y pide exportar una **copia JPEG sin reducir la resolución**.
- Contenido no reconocido (`unrecognized_type`).
- Cualquier otro motivo conserva el mensaje genérico; `signature_mismatch` conserva el suyo.

Textos en pt, es, en y zh con prueba de existencia de cada traducción y una prueba que impide afirmar «verificada», «reducida automáticamente» o «guardada».

## Opciones que NO se implementan (decisión del propietario)

1. **Subir el límite de 50 MB decodificados.** Relaja una protección de seguridad frente a bombas de descompresión; hay que cuantificar el coste de memoria por petición. No se toca sin decisión.
2. **Reducir una copia con confirmación explícita y registro de procedencia** («análisis sobre copia reducida a X×Y; original no modificado»). Es técnicamente posible en el cliente, pero cambia lo que el proveedor ve y puede afectar a la interpretación; debe llevar aviso, trazabilidad y decisión médica.
3. **Aceptar HEIC/HEIF** con decodificador propio o servidor. Añade superficie de ataque (formato complejo) y dependencias; no se propone sin necesidad demostrada.

## Límites

Imágenes sintéticas de color uniforme o ruido, no fotografías reales; el consumo de memoria por petición no se midió; HEIC real de un iPhone y la conversión del selector del sistema **No verificados**; no se probó en dispositivos Android/iOS.
