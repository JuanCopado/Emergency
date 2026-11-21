# Cotejo acústico de CURB-65 en PR61

21 de noviembre de 2026. Commit b5918ffa42cced3befa5674e40af43adc197acd2. CLINICALLY_PENDING.

La segunda toma es la evidencia principal. Windows WASAPI capturó únicamente el árbol del proceso Narrator.exe (PID 25016, modo INCLUDE). El WAV conserva los primeros 84 segundos de la toma, en mono PCM a 16 kHz. SHA-256 AAB02BD4A8BCA18B3C2F664D0C205C7C500B75015C2070C95915C1897BBED509.

Dos transcripciones locales del mismo audio con faster-whisper-base, en portugués y en español, sin proporcionar las respuestas esperadas. El cotejo es automático. El historial nativo y la pantalla del ensayo anterior documentan el texto de referencia. La primera toma tiene dos lecturas interrumpidas.

| Inicio en WAV | Campo en pantalla | Cifra recuperada en portugués | Unidad recuperada inequívocamente |
|---|---|---:|---|
| 00:04 | Urea (mmol/L) | 6 | Pendiente |
| 00:23 | Frecuencia respiratoria (/min) | 18 | Pendiente |
| 00:39 | Presión sistólica (mmHg) | 120 | Pendiente |
| 00:55 | Presión diastólica (mmHg) | 75 | Pendiente |
| 01:11 | Edad (años) | 55 (50 e 5) | Pendiente |

Resultado parcial. La transcripción recupera las cinco cifras. Las dos pasadas deforman las unidades o las omiten. También transcriben el comparador visible ≥ como «menor o igual». El audio requiere escucha humana para atribuir la discrepancia al lector o al reconocimiento. Los 95 ZIP coincidieron con sus huellas R5 y el árbol Git probado estaba limpio.
