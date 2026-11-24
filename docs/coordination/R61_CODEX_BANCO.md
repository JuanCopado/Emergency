# R61 · Adquisición, lote ECG y checklist de 30 estímulos

**CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE · NOT_FROZEN_NOT_VALIDATED.** Base internacional `203237400698d9f5073c459202df59d0b8eb7ed4`. PR100 está incorporada. PR101 conserva su auditoría independiente. [PR102](https://github.com/JuanCopado/Emergency/pull/102) contiene las decisiones médicas aprobadas y las fichas individuales. La aprobación del protocolo y las salvaguardas conserva su alcance.

## Lote ECG

S2-09 se sustituye por un esquema RGB de 12 derivaciones calculado localmente. El generador usa una señal periódica de 950 ms, cinco componentes por latido, derivaciones frontales derivadas de I/II y progresión precordial R/S modelada. Representa una pantalla clínica simulada con rejilla, rótulos por derivación, reflejo leve e indicación visible de simulación. Escala nominal en la rejilla 25 mm/s y 10 mm/mV; el tamaño físico depende de la pantalla. No hay material de pacientes ni fuente de imagen de terceros. CC0 consta como declaración del proyecto.

- Candidato · 1120 × 572 px, JPEG RGB, 218418 bytes, SHA-256 `e55d2d35203147e3f92c95c61e464a80dca4a28f08a7de495dd46648a21fa077`.
- Origen · generador versionado `bank_r23.py`. Derivado · rejilla, gráfica y simulación de pantalla reproducibles sobre ese modelo y codificación JPEG.
- PASS técnico · 109 pruebas focales, incluida identidad de miembros, 12 señales distintas, progresión R/S, 24 sellos históricos y 8 sellos pt-BR. No se cambian los archivos de los sellos. El escaneo de contenedor no encontró metadatos identificativos. Ningún SHA-256 duplicado. Mínimo dHash entre sets 25 bits frente a umbral 16.
- PASS de representación · Chromium decodificó las seis imágenes válidas en 360×640, 390×640 y 1280×640 y comprobó dimensiones, vista contenida y navegación. 18 recorridos, 36 decodificaciones con regreso y avance.
- **PENDING** · el modelo no acredita validez fisiológica clínica ni equivalencia de dificultad con S1-09. Dos revisores independientes deben puntuar realismo 1–5 a 360×640 y registrar reconocimiento de la modalidad, legibilidad, efecto del reflejo y equivalencia experimental con S1-09. Umbral ≥4/5 para cada revisor. Aplicar tercero si discrepan. Pendientes la revisión visual formal de privacidad, los nombres/firmas, puntuaciones y adjudicación del propietario. Conservar la referencia al hash previo de S2-09 `555d6c5717edac86b4b7a30352cca8638e52c3df1ac3c826493144ee8dbe0ce2`.

## Fuentes por modalidad y bloqueos

- **S1-10 / S2-10.** Copyright CC0 confirmado en las dos páginas de los originales PA de tórax y muñeca. El derivado exigido es una fotografía RGB de monitor. No se pudo obtener el original por la ruta de ejecución disponible ni se dispone de una captura móvil del entorno. Aún se deben inspeccionar sus rótulos, procedencia del derivado y privacidad antes de incorporarlo. [Tórax PA](https://commons.wikimedia.org/wiki/File:Normal_posteroanterior_(PA)_chest_radiograph_(X-ray).jpg) · [Muñeca](https://commons.wikimedia.org/wiki/File:X-ray_of_normal_wrist_by_dorsoplantar_projection_(crop).jpg)
- **S1-11 / S2-11.** Se localizó una fotografía real de una radiografía de tórax en monitor bajo CC BY-SA 4.0. Es candidata a evaluación, con autoría y licencia del derivado por registrar. Falta descargar e inspeccionar los bytes, verificar la oblicuidad y el encuadre para S1-11 o el moiré leve para S2-11. Cada estímulo requiere una fuente visual distinta. [Fotografía de pantalla](https://commons.wikimedia.org/wiki/File:A_chest_X-ray.jpg)
- **S1-12 / S2-12.** El fantoma eFAST de 2023 ofrece ventanas abdominales y pulmonares, pero excluye la ventana subxifoidea. El fantoma modular de 2025 es una segunda fuente, con artículo CC BY 4.0. Falta identificar y verificar el fotograma concreto de condición sin líquido o derrame, su licencia a nivel de figura y su captura de ecógrafo. Los fantomas genéricos de ecografía y los datasets de otros órganos no sustituyen estas ventanas. [Fantoma de 2023](https://doi.org/10.3389/fbioe.2023.1244616) · [Fantoma modular de 2025](https://doi.org/10.1186/s12938-025-01448-8)
- **S1-01…07 / S2-01…07.** El moulage disponible representa una herida profunda simulada y no acredita combinaciones de piel, luz, cierre y distractores. S-SYNTH ofrece lesiones generadas bajo CC0, sin demostrar la morfología ni las escenas fotográficas requeridas en estas posiciones. El informe de simulación adicional aporta referencias de fabricación y fotografía pero no una serie de 14 derivados que satisfaga las fichas y permisos a nivel de cada imagen. Las alternativas siguen pendientes por caso. Las galerías requieren origen y revisión de cada distractor. [Moulage](https://commons.wikimedia.org/wiki/File:Healthcare_Simulation_Moulage_Standardized_Patient_Actor_Deep_Gash_Wound_Cut_on_Wrist.jpg) · [S-SYNTH](https://doi.org/10.57967/hf/3277) · [Informe de simulación](https://usaarl.health.mil/assets/docs/techReports/2025-05.pdf)

Wikimedia, PMC, Frontiers y Hugging Face devolvieron HTTP 403 del túnel para la recuperación de bytes en el entorno. La lectura documental sí permitió cualificar candidatos. Las licencias de copyright no acreditan anonimización ni confirman por sí solas el cumplimiento del protocolo. El manifiesto conserva nulos los archivos y hashes de los 20 IDs pendientes.

## Checklist físico

10 archivos, 20 ausentes, 0 adjudicados. M1=8, M2=4 y M3=18. QA-01/QA-02 quedan fuera de las 30 filas. SHA-256 del [manifiesto](../../clinical/lab/human_factors/bank/stimuli_manifest.json) · `d486fcf73e13b43fbda9f8c9dd814e582b0ea6881f56fb17e1cb83c3fdc712fc`.

| ID | Mecanismo | Modalidad | Archivo y SHA‑256 | Estado |
| --- | --- | --- | --- | --- |
| S1-01 | M3 | skin_wound | — | BLOCKED · fuente y derivado conformes pendientes |
| S2-01 | M3 | skin_wound | — | BLOCKED · fuente y derivado conformes pendientes |
| S1-02 | M3 | skin_wound | — | BLOCKED · fuente y derivado conformes pendientes |
| S2-02 | M3 | skin_wound | — | BLOCKED · fuente y derivado conformes pendientes |
| S1-03 | M3 | skin_wound | — | BLOCKED · fuente y derivado conformes pendientes |
| S2-03 | M3 | skin_wound | — | BLOCKED · fuente y derivado conformes pendientes |
| S1-04 | M1 | skin_wound | — | BLOCKED · fuente y derivado conformes pendientes |
| S2-04 | M1 | skin_wound | — | BLOCKED · fuente y derivado conformes pendientes |
| S1-05 | M1 | skin_wound | — | BLOCKED · fuente y derivado conformes pendientes |
| S2-05 | M1 | skin_wound | — | BLOCKED · fuente y derivado conformes pendientes |
| S1-06 | M1 | skin_wound | — | BLOCKED · fuente y derivado conformes pendientes |
| S2-06 | M1 | skin_wound | — | BLOCKED · fuente y derivado conformes pendientes |
| S1-07 | M1 | skin_wound | — | BLOCKED · fuente y derivado conformes pendientes |
| S2-07 | M1 | skin_wound | — | BLOCKED · fuente y derivado conformes pendientes |
| S1-08 | M3 | ecg | `stimuli/S1-08.jpg` · `e1ef94da909021ada458d5f501b07d978c2fdc59bfc97ccfa613a69bcf957620` | PASS técnico · revisión pendiente |
| S2-08 | M3 | ecg | `stimuli/S2-08.jpg` · `6b7ec6456cbdd04eee1dbed3357042199afbb4e08f6d34636087d7a22db32acd` | PASS técnico · revisión pendiente |
| S1-09 | M3 | ecg | `stimuli/S1-09.webp` · `38ff1bdd9a07434f017b01d74272dc1e1a38263f54a8e62aa493a7088ce79ebc` | PASS técnico · revisión pendiente |
| S2-09 | M3 | ecg | `stimuli/S2-09.jpg` · `e55d2d35203147e3f92c95c61e464a80dca4a28f08a7de495dd46648a21fa077` | PASS técnico · revisión pendiente |
| S1-10 | M3 | xray | — | BLOCKED · fuente y derivado conformes pendientes |
| S2-10 | M3 | xray | — | BLOCKED · fuente y derivado conformes pendientes |
| S1-11 | M3 | xray | — | BLOCKED · fuente y derivado conformes pendientes |
| S2-11 | M3 | xray | — | BLOCKED · fuente y derivado conformes pendientes |
| S1-12 | M3 | pocus | — | BLOCKED · fuente y derivado conformes pendientes |
| S2-12 | M3 | pocus | — | BLOCKED · fuente y derivado conformes pendientes |
| S1-13 | M3 | document | `stimuli/S1-13.pdf` · `2c61bbdf6e1f6b002218320f17abf57a5df1d615acfc4f86899bc07f98b27aa1` | PASS técnico · revisión pendiente |
| S2-13 | M3 | document | `stimuli/S2-13.jpg` · `dab1bfeb66cba747b16927d245178e8d2cfdc8efcc9ab1c94aac9f835899d3de` | PASS técnico · revisión pendiente |
| S1-14 | M2 | — | `stimuli/S1-14.png` · `3279ec6a55f2630d6f2996bb1600b3f426c3953e5f1aaf91cea847c39467de84` | PASS técnico · revisión pendiente |
| S2-14 | M2 | — | `stimuli/S2-14.pdf` · `281353c78416bdd33faf21b3ca1db707f8894948db1b7013b11a77286fabd745` | PASS técnico · revisión pendiente |
| S1-15 | M2 | — | `stimuli/S1-15.jpg` · `611db5fe62c256dcf243ecd9a54aa04bd07e9885ae15e88e8b5ee79379a43eca` | PASS técnico · revisión pendiente |
| S2-15 | M2 | — | `stimuli/S2-15.pdf` · `01212969ab9691e1b7b44436f9b0ae54fdca9ae983dcd5ded241d06543b9cede` | PASS técnico · revisión pendiente |
