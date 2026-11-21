# PR61 · PDF nativo y cotejo de Narrador

21 de noviembre de 2026. Estado **CLINICALLY_PENDING**, registro 129 GREEN / 2 YELLOW / 0 RED.

## Versión y alcance

Prueba sobre el HEAD de PR61, commit b5918ffa42cced3befa5674e40af43adc197acd2 y árbol 227fb55cc648503542fd340a35f1a15d82c9807b. Registro preparado desde el merge aae5242b61badbcca924cb0c13f44d2ab3c80d56. Alcance internacional del producto conservado, caso artificial de farmacología y cinco campos numéricos de CURB-65 en interfaz española. Esta entrada complementa el corte histórico de [limitaciones R5](R5_WINDOWS_QA_LIMITATIONS_20261121.md).

## PDF nativo

Edge 158.0.4370.33 abrió Imprimir resultado, Guardar como PDF y el cuadro Guardar como de Windows. Se guardó un archivo nuevo de cuatro páginas, 75.330 bytes, productor Skia/PDF m158. La primera página contiene consecutivamente dose: 300 y dose_unit: mg. Los 10.037 caracteres del informe coinciden mediante pypdf al excluir espacios y cabeceras/pies de Edge. La inspección de cajas de caracteres encontró cero caracteres fuera de página. Las entradas y el resultado del caso artificial coinciden con R4.

PDFium devolvió U+0002 para dos guiones de una URL partida. Ambos guiones son visibles en la página 3 y pypdf recupera el texto original. La prueba acredita este caso y este commit. [PDF](evidence/pr61-native-20261121/PR61-amiodarona-Edge.pdf) · [Recibo](evidence/pr61-native-20261121/recibo.json) · [Cuatro páginas](evidence/pr61-native-20261121/PDF-cuatro-paginas.png).

## Narrador y cotejo aportado

Se conservaron el historial nativo de voz, dos tomas y cinco fragmentos. La segunda toma se capturó mediante WASAPI, incluyendo únicamente el árbol de Narrator.exe, PID 25016. Las transcripciones automáticas ES/PT contienen discrepancias en unidades y comparador. El usuario aportó posteriormente el JSON de cotejo guardado el 21 de noviembre a las 18:58:59.392 UTC, con cinco resultados «Coincide». El nombre de revisor está vacío en el JSON. La atribución procede de su entrega directa en el chat.

| Campo | Cifra en pantalla y anotada | Unidad en pantalla | Unidad anotada | Comparador anotado | Dictamen del usuario |
|---|---|---|---|---|---|
| Urea | 6 | mmol/L | mm/l | ≥ 0 | Coincide |
| Frecuencia respiratoria | 18 | /min | min | En pantalla ≥ 0 | Coincide |
| Presión sistólica | 120 | mmHg | mmHg | ≥ 0 | Coincide |
| Presión diastólica | 75 | mmHg | mmhg | ≥ 0 | Coincide |
| Edad | 55 | años | años | ≥ 0 | Coincide |

Las grafías mm/l, min y mmhg se conservan tal como se aportaron. El cotejo acredita cinco coincidencias declaradas y cinco cifras verificadas contra pantalla. Las unidades y el comparador carecen de transcripción humana de las palabras pronunciadas. Esa precisión literal continúa limitada. El historial acredita el texto emitido por Narrador. La captura recorta la ayuda bajo edad, cuyo nombre accesible observado incluye «Número finito ≥ 0». La revisión R2 documenta esos límites. [Informe R2](evidence/pr61-native-20261121/INFORME_FINAL_COTEJO_PR61_20261121_R2.md) · [JSON del usuario](evidence/pr61-native-20261121/PR61-cotejo-CURB65-2026-11-21T18-58-59-392Z.json) · [Audio](evidence/pr61-native-20261121/CURB65-Narrador-toma2.wav) · [Captura](evidence/pr61-native-20261121/CURB65-pantalla.png) · [Recapitulación](evidence/pr61-native-20261121/Narrador-CURB65.png).

## Preservación y pendientes

Las copias incluidas coinciden byte a byte con los originales locales. El manifiesto identifica tamaño y SHA-256 de cada archivo. Los 95 ZIP históricos coinciden con sus huellas R5. Los informes anteriores y sus resultados pendientes se conservan como cortes históricos. [Manifiesto de QA](evidence/pr61-native-20261121/QA_MANIFEST.json).

Esta actualización registra el nuevo guardado nativo y el cotejo aportado. La revisión gráfica compuesta completa, el recorrido visual Windows de imagen pequeña y los restantes límites clínicos y de G05 continúan según sus registros. Los cálculos, módulos, referencias, aceptaciones, contenido clínico y estados de módulos conservan su alcance. **CLINICALLY_PENDING**.
