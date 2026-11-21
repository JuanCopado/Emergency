# Informe del cotejo de Narrador en PR61

Fecha 21 de noviembre de 2026. Commit de la prueba b5918ffa42cced3befa5674e40af43adc197acd2. Estado **CLINICALLY_PENDING**.

## Resultado de la revisión

El cotejo humano permanece pendiente. La página de Edge en http://127.0.0.1:5195/fragmentos-CURB65/ muestra vacíos los campos de valor escuchado, unidad escuchada, comparador y observaciones. Las cinco filas tienen resultado «Pendiente» y el nombre de revisor está vacío. Tras recargar se recupera el mismo contenido.

La única exportación localizada en Descargas también contiene los cinco registros vacíos y pendientes. Su fecha interna es 2026-11-21T18:51:18.892Z. Esta exportación corresponde a la prueba técnica de exportación realizada al crear la página. No se ha localizado una revisión humana posterior en la página ni entre esas exportaciones.

| Campo | Valor en pantalla | Unidad en pantalla | Comparador en pantalla | Anotación de escucha | Dictamen |
|---|---|---|---|---|---|
| Urea | 6 | mmol/L | ≥ 0 | Sin registrar | Pendiente |
| Frecuencia respiratoria | 18 | /min | ≥ 0 | Sin registrar | Pendiente |
| Presión sistólica | 120 | mmHg | ≥ 0 | Sin registrar | Pendiente |
| Presión diastólica | 75 | mmHg | ≥ 0 | Sin registrar | Pendiente |
| Edad | 55 | años | ≥ 0 | Sin registrar | Pendiente |

## Alcance de la evidencia

El PDF nativo de Edge, la captura de CURB-65, la recapitulación de Narrador, las dos tomas WAV, los cinco fragmentos y las transcripciones previas se conservan. La captura recorta la ayuda bajo edad. El nombre accesible observado en aquella prueba incluye «Edad (años) Requerido · Número finito ≥ 0».

Las transcripciones automáticas previas recuperaron las cinco cifras, con diferencias en las unidades y el comparador. Esas transcripciones conservan su carácter automático. La revisión actual de las anotaciones no permite resolver la pronunciación de unidades ni de ≥.

## Preservación y trazabilidad

Las huellas de todos los archivos previos recogidos en el manifiesto y de los cinco fragmentos coinciden. Los 95 ZIP del registro R5 conservan sus huellas. Esta tarea añade el informe y evidencia de lectura de la página. Conserva los cálculos y el contenido clínico.

- [Anotaciones observadas](ANOTACIONES_OBSERVADAS_20261121.json)
- [Captura de la página revisada](ANOTACIONES_PAGINA_20261121.png)
- [Manifiesto de preservación de esta revisión](PRESERVACION_COTEJO_FINAL_20261121.json)
- [Grabación principal](CURB65-Narrador-toma2.wav)
- [Guía y fragmentos](fragmentos-CURB65/ESCUCHA.md)

El informe documenta la evidencia disponible y el resultado pendiente. Para emitir un dictamen de coincidencia o discrepancia por campo se necesitan las anotaciones de escucha correspondientes. El estado clínico permanece **CLINICALLY_PENDING**.
