# Emergency · R22 · registro de la decisión médica DEC-CLIN-R22-01

**Decisión recibida el 23 de noviembre de 2026 a las 09:41:28 UTC (08:41:28 Atlantic/Azores) · Estado global `CLINICALLY_PENDING` (129 GREEN / 2 YELLOW / 0 RED) · Sin GO_RELEASE**

Registro de una decisión del médico propietario, Dr. Juan Copado Ceballos. No se vuelve a solicitar. Solo registra; no activa la capa 7, no autoriza estudio con participantes ni modifica resultados clínicos.

## Procedencia

[Comentario de PR #83](https://github.com/JuanCopado/Emergency/pull/83#issuecomment-7096984774) («DEC-CLIN-R22-01: SÍ. Apruebo exclusivamente la alternativa B: arnés determinista de simulación de Capa 7 en laboratorio aislado, previa auditoría independiente, sin producción ni autorización de estudio con profesionales»), respuesta a la ficha única `DEC-CLIN-R22-01` del informe `R22_GEMINI_DECISION_CAPA7` (no está en el repositorio: la comparación contra el original sigue **No verificada**). Es un **registro de instrucción médica: no es firma física ni certificado de implementación**.

## Decisión y alcance: Alternativa B (solo laboratorio aislado)

Arnés determinista de simulación de la capa 7 **únicamente en el brazo experimental B** de la Etapa 1 formativa, en rama y directorio separados del producto (`clinical/lab/human_factors/layer7_harness.py`):
- Cuatro disparadores cerrados `T7-01_UNDECLARED_MODALITY`, `T7-02_UNKNOWN_CONTRACT`, `T7-03_CORRUPT_UNPROCESSABLE`, `T7-04_FORMAT_CONTAINER_MISMATCH` con sus causas técnicas objetivas y los cuatro textos literales de `DEC-CLIN-R15-01` (es/pt/en; sin reescritura ni reglas nuevas).
- `classic_upload` y `document_legacy_bridge` con `kind=null` protegidos; prohibido decidir por RGB, EXIF, nombre, extensión aislada, ausencia de DICOM, píxeles o sospecha no demostrada; cero bloqueos sobre fotos válidas de ECG/Rx/POCUS.
- Resultados rotulados `SIMULATED_LAYER7_HARNESS_LAB_ONLY`. Análisis separados: bypass B/C/D (selector), comprensión/recuperación E1/E2 (capa 7), F (no interferencia).
- **Auditoría independiente de Antigravity, con pruebas y SHA exacto, obligatoria antes de usar el arnés con personas.**

## Qué no autoriza

No activa la capa 7 en producción (`VITE_R51_LAYER7` inerte), no es `GO_RELEASE`, uso asistencial ni cierre de `R5-1`; **no autoriza reclutar profesionales ni la Etapa 1 con participantes** (faltan validación técnica independiente, banco sintético congelado con SHA-256, dictamen o exención ética/institucional, consentimiento y privacidad); no usa pacientes ni PHI/PII; Etapa 2, tamaños muestrales y márgenes siguen pendientes. R5-2, Fase B, Fase 2, G05, RAG y APIs externas siguen bloqueados. No se declara `READY_FOR_HUMAN_STUDY`.
