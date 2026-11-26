# Banco canónico de 30 estímulos · recepción y conciliación
26/11/2026. Base 228cd21d75d14e1012beb7f5dfe82c2c920c4ccc. Laboratorio experimental.

## Resultado
El manifiesto vigente identifica 30 posiciones, 10 archivos presentes y 20 posiciones sin archivo canónico. Composición comprobada M1=8, M2=4, M3=18. Los 30 campos clinical_adjudicator_signoff están en PENDING. Se reutilizan las aprobaciones MED-DEC-R46-01/02 del 24/11, precisadas por R50 y R54.

Los diez archivos históricos coinciden con sus hashes y tamaños. Los controles corruptos o incompatibles previstos en M2 se interpretan según su defecto intencionado. La verificación técnica no declara diez imágenes clínicas válidas. Las dos piezas QA-01/QA-02 quedan fuera de las 30 posiciones.

## Nuevo original S1-01
Se recuperó el original primario de Wikimedia, 2816 × 2112, JPEG RGB, 1.876.910 bytes. SHA-256 b4e6e7a62ba07eb996464fca80a0603562cb0a146a03d8bf00861d7cd12e548a. SHA-1 e6a0325943b887ebcca0b1e72f3c6a2b0b9dc1b0, idéntico al publicado por Commons. La fuente atribuye la obra al usuario Berteun según su declaración de titular y publica una dedicación al dominio público mundial.

Fuente primaria https://commons.wikimedia.org/wiki/File:Abrasion_on_hand_20050906.jpg

Se conserva el original intacto y un derivado JPEG RGB sin metadatos, sin recorte o reescalado, con calidad 95 y submuestreo cero. La recodificación JPEG puede cambiar valores de píxel. Su SHA-256 es 3584e973cc0545d6207c06cf494735d018636c424bde4542ef1b9024033071d0. Se adjunta representación 360 × 640. La inspección técnica observa superficie de mano con lesión abierta, sin rostro o identificadores textuales. El original contiene EXIF de cámara y no se detectó GPS. El derivado tiene cero hallazgos del escáner de metadatos.

La recepción canónica intake_r68 devuelve BYTES_VERIFIED_REVIEW_PENDING para las dos piezas. No hay SHA-256 duplicado con los diez archivos del banco. La distancia dHash de 1 frente a la copia reducida de PR110 confirma la misma línea de procedencia. El original nuevo mejora la custodia de ese candidato y no constituye otro caso ni otro slot.

Faltan acreditación de MST 2 en origen, condiciones de iluminación, realismo por dos revisores con puntuación mínima 4/5 cada uno, revisión independiente de privacidad, referencia por aplicabilidad, equivalencia con S2-01 y adjudicación del propietario. No se deriva MST ni Fitzpatrick a partir de la apariencia.

## Fuentes candidatas ya disponibles
Se cotejaron nuevamente los cuatro originales radiográficos de R86 y sus cuatro paneles preparados, con SHA-256, tamaño, decodificación y dimensiones. Sus recibos conservan autoría y licencias CC0 o CC BY-SA según archivo. Faltan las cuatro fotografías ópticas reales con móvil y sus controles específicos. Una captura de pantalla digital no acredita borde físico, inclinación o moiré óptico.

El recibo POCUS de custodia pasó intake_r68 con siete activos, incluidos cuatro originales y tres derivados. S1-12 conserva un panel preparado para monitor y falta fotografía móvil. S2-12 conserva el bloqueo de condición experimental y panel conforme, además de captura y revisión.

El catálogo DERMA independiente y sus casos con eMST documentado se mantienen como fuentes externas. Sus morfologías o condiciones no se asignan automáticamente a las 14 heridas canónicas. Las ocho posiciones M1 exigen origen sintético literal y distractores concretos. Las seis heridas M3 exigen los requisitos individuales de banda y luz. No existe material conforme acreditado para completar esas posiciones en esta ejecución.

## Matriz exacta y pendientes
MATRIZ_30_POSICIONES.json conserva las 30 especificaciones, ID, par, mecanismo, formato, MST, estado y causa específica. Se generaron 30 fichas sin firmar en la custodia local D:\ChatGPT_Trabajo\BANCO30_RECEPCION_20261126\30_FICHAS_SIN_FIRMAR usando adjudication_r54.build_dossiers.

| Grupo pendiente | Posiciones | Dependencia |
|---|---|---|
| Heridas | S1/S2 de los pares 01–07, 14 posiciones | Morfología, origen, MST y luz documentados, distractores cuando correspondan y revisiones |
| Radiografías | S1/S2 de los pares 10–11, 4 posiciones | Fotografía óptica real del monitor, privacidad y equivalencia |
| POCUS | S1/S2 del par 12, 2 posiciones | Captura física y revisiones; S2-12 necesita fuente/panel conforme |

Las 20 posiciones siguen sin archivo aceptado en el manifiesto. No se cuentan los originales candidatos, paneles o revisiones pendientes como estímulos incorporados.

## Incidencia de checkout y validación
La conversión automática LF→CRLF del checkout Windows alteró los bytes de S1-13.pdf, S2-14.pdf y S2-15.pdf. Se recuperaron del commit base los blobs exactos cuyos hashes coinciden con el manifiesto. RECUPERACION_BLOBS_PDF.json registra hashes y tamaños antes/después. Se añade una regla local de atributos *.pdf -text en bank/stimuli para conservar bytes en futuros checkouts. Los blobs históricos y el manifiesto se mantienen.

53 pruebas PASS en las suites existentes test_r68_intake, test_r54_adjudication_dossiers y test_r25_bank. La primera ejecución de dossiers usó cp1252 y falló por codificación; la repetición con PYTHONUTF8=1 pasó 12/12. PRUEBAS.json identifica las ejecuciones. El resultado de CI remoto debe comprobarse en la PR y no se atribuye a estas pruebas locales.

## Preparación de revisión
El lote individual se conserva en clinical/lab/human_factors/intake_batches/bank30-20261126/S1-01. Se incluyen receipt.json, QA_INDIVIDUAL.json, original, derivado y representación para revisión. Reutiliza las fichas y el circuito R54, con firmas pendientes. La aceptación definitiva requiere los controles y adjudicaciones correspondientes.

CLINICALLY_PENDING · NOT_FROZEN_NOT_VALIDATED · NO_GO_CLINICAL_RELEASE.
