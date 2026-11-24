# R54 · Continuación del inventario pendiente de R45

No se incorpora un archivo al banco sin bytes, origen/licencia, privacidad,
congruencia con la especificación y revisión. No se sustituye fotografía clínica
por dibujo o imagen médica inventada. Los sellos históricos quedan intactos.

| IDs reales pendientes | Material requerido y siguiente condición verificable |
|---|---|
| S1-01, S2-01 | Herida superficial sin cierre, piel clara y luz neutra; fotografía sintética autorizada o abierta conforme. |
| S1-02, S2-02 | Suturas/exudado o grapas/cambio perilesional; piel media y luz cálida. |
| S1-03, S2-03 | Costra oscura o exudado/borde irregular; piel oscura, sombra leve; revisión de fototipo y realismo, sin atribuir diagnóstico desde especificación. |
| S1-04, S2-04 | Galerías de cuatro miniaturas con herida sintética y ECG; licencia y privacidad de todos los componentes. |
| S1-05, S2-05 | Herida suturada/laceración sintética con nombre confusor prescrito. |
| S1-06, S2-06 | Herida/lesión de fondo oscuro con miniaturas Rx; no adjudicar necrosis/NSTI desde el texto de diseño. |
| S1-07, S2-07 | Herida/hematoma o apósito parcial con capturas ecográficas; luz tenue, sin control de contenido por Capa 7. |
| S1-10, S2-10 | Captura móvil RGB de monitor simulado con Rx PA de tórax o muñeca/tobillo. |
| S1-11, S2-11 | Rx toracoabdominal oblicua WebP o pelvis/tórax JPEG con moiré leve. |
| S1-12, S2-12 | Captura de ecógrafo simulado/fantoma FAST o subxifoidea/pulmonar; referencia del fantoma, no «examen negativo» por fotograma. |

## Avance documental observado el 24/11/2026

Se abrieron las páginas fuente de los dos candidatos Rx citados en R45 mediante
la herramienta web. Ambas declaran **CC0-1.0** y autor Mikael Häggström:

- [Rx PA de tórax](https://commons.wikimedia.org/wiki/File:Normal_posteroanterior_(PA)_chest_radiograph_(X-ray).jpg): original descrito como JPEG, 1929×2207. Candidato S1-10; falta captura de monitor simulada conforme y revisión de original/derivado.
- [Rx de muñeca](https://commons.wikimedia.org/wiki/File:X-ray_of_normal_wrist_by_dorsoplantar_projection_(crop).jpg): original descrito como JPEG, 690×980, autoexamen. Candidato S2-10; falta captura conforme y revisión de original/derivado.

La licencia de copyright no demuestra desidentificación, autorización de datos
ni validez diagnóstica. No se copian datos personales de las descripciones a las
fichas ni se infiere edad del estímulo futuro. La descarga por API de Wikimedia
desde el entorno de ejecución falló con `Tunnel connection failed: 403 Forbidden`.
Las páginas consultadas no proporcionan bytes locales ni un SHA-256 verificable:
por ello ambos candidatos permanecen fuera del banco, con hash físico pendiente.

Fuentes de referencia de R45 para POCUS y heridas conservadas, pendientes de
derivado concreto y revisión: [fantoma eFAST](https://pmc.ncbi.nlm.nih.gov/articles/PMC12509367/),
[moulage](https://commons.wikimedia.org/wiki/File:Healthcare_Simulation_Moulage_Standardized_Patient_Actor_Deep_Gash_Wound_Cut_on_Wrist.jpg),
[S-SYNTH](https://doi.org/10.57967/hf/3277). No se afirma haberlas descargado o
validado en R54. EchoNet mantiene su restricción de redistribución y no se usa
como sustituto del estímulo FAST/pulmonar requerido.

Resultado físico: **10 presentes / 20 pendientes / 0 adjudicados**. Los 20 casos
conservan el impedimento específico en su ficha, sin diagnóstico, archivo ni SHA
inventado. Completarlos requiere materiales conformes y la revisión individual;
la autorización del protocolo no aprueba automáticamente dichos materiales.
