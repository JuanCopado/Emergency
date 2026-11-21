# R4 · Seguimiento técnico de presentación y guardado

Base internacional `66aec7781bede855f9f4403d461fe6ef119db69d`. Estado **CLINICALLY_PENDING**, 129 GREEN / 2 YELLOW / 0 RED.

El informe de farmacología presenta el énfasis de las líneas que contienen código, tablas o referencias y el cierre de negrita adyacente a una cifra. Se conservan los destinos de referencia, los literales de código, los valores numéricos y la instantánea clínica. El cotejo del catálogo cubrió 46 pautas y 17 textos fuente únicos. La suite estable tuvo 18 pruebas aprobadas. La primera pasada, ejecutada mientras cambiaba la implementación, fue rechazada por cambio de huella y quedó descartada.

La nota solicita el idioma elegido en pantalla. Se localizan siete avisos automáticos y las etiquetas mecánicas de exportación. Un cambio de idioma conserva el borrador y exige actualizar el análisis antes de exportarlo. Los textos clínicos canónicos y el texto libre conservan su idioma original. Las 60 salidas históricas completas coincidieron con la base.

Se corrigió la regresión de disponibilidad del PDF chino detectada al traducir sus cabeceras. Las fuentes CJK se distribuyen con licencia OFL, revisión y huellas verificables, pesos estáticos 400/700 y receta de reproducción. La fuente DejaVu sigue presentando los caracteres que ya cubría. Se conservan la comprobación de glifos y el rechazo de caracteres no disponibles. [Procedencia](../assets/fonts/noto-cjk-manifest.json) y [ensayos de idioma](R4_NOTE_LANGUAGE_20261121.md).

## Guardado nativo observado

La aplicación de prueba se sirvió desde la composición local en `http://127.0.0.1:4198/acute-medications`. Sobre un caso artificial de amiodarona, se abrió **Imprimir resultado**, se observó el destino integrado **Guardar como PDF** de Edge, se escribió una ruta nueva en **Guardar como** de Windows y se confirmó el guardado con teclado. Ambos diálogos se cerraron. El archivo nuevo se verificó en disco, se extrajo su texto y se renderizaron las cuatro páginas. En la primera figuran el encabezado completo y las líneas consecutivas `dose: 300` y `dose_unit: mg`.

Archivo de evidencia `emergency-native-edge-guardado.pdf`, 75.503 bytes, SHA-256 `74d2435788a29e6f8b611ac263ada99c1c259a80e92496a4b1eb140c8a60b597`. Productor y recuentos están en el recibo local de la entrega. La prueba pertenece a un único caso sintético. Las modificaciones posteriores de fuente CJK afectan al exportador Python y conservan el código de impresión del navegador verificado.

La auditoría del formato fue independiente del autor. Las verificaciones posteriores y el dictamen del árbol final se registran en la PR de entrega y sus controles. Los ZIP anteriores se conservan.
