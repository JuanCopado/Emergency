# Emergency · R20 · registro de la decisión médica DEC-CLIN-R19-01

**Decisión recibida el 23 de noviembre de 2026 a las 00:43:56 UTC (22/11/2026 23:43:56 Atlantic/Azores) · Estado global `CLINICALLY_PENDING` (129 GREEN / 2 YELLOW / 0 RED) · Sin GO_RELEASE**

Registro de una decisión del médico propietario, Dr. Juan Copado Ceballos. No se vuelve a solicitar. Solo registra; no ejecuta ningún estudio ni modifica resultados clínicos.

## Procedencia

[Comentario de PR #83](https://github.com/JuanCopado/Emergency/pull/83#issuecomment-7088594775) («DEC-CLIN-R19-01: SÍ», respuesta a la ficha única del informe `R19_GEMINI_INFORME_CONSOLIDADO_FINAL`, parte IV), y la instrucción R20 del propietario que la enumera entre las decisiones aprobadas. Los informes Gemini R19 **no están en el repositorio**. Es un **registro de instrucción médica: no es firma física ni aprobación del producto**.

## Decisión y alcance: plan de factores humanos en dos etapas

1. **Etapa 1 · formativa y de estimación:** estudio independiente con profesionales representativos e **imágenes sintéticas, sin PII/PHI**; mide errores de selección, bypass, confirmaciones erróneas, falsas cancelaciones en `ECG`/`Rx`/`POCUS`, experiencia y legibilidad móvil, tiempo de interacción, tasa basal y correlación intraparticipante `rho`. FDA/IEC 62366-1 como referencia de planificación formativa, **no** como umbral clínico ni tamaño confirmatorio automático. Se ejecuta **después de verificar localmente PR82 y PR83**.
2. **Etapa 2 · confirmatoria (solo planificación diferida):** tamaño muestral, análisis confirmatorio y criterios numéricos de aceptación se determinarán después, con la evidencia de la Etapa 1 y sujetos a **una nueva decisión médica explícita**. **No se aprueban ahora `N`, márgenes, umbrales ni supuestos de potencia.**

**Salvaguarda estadística:** «dos etapas» son fases del programa (formativa → confirmatoria); **no** un pretest de carryover con cambio condicional a un análisis del primer periodo. El diseño cruzado AB/BA y sus modelos se preespecifican sin esa selección sesgada; la estimación respeta la agrupación por participante, distingue ensayos de participantes, y cero eventos no significa riesgo cero.

## Qué no autoriza

No activa PR82/PR83, la capa 7 ni Fase B/Fase 2; no ejecuta ni da por realizado el estudio; no autoriza `GO_RELEASE`, uso asistencial, datos reales de pacientes, cambios de dosis, nuevas reglas clínicas, G05/RAG/APIs externas, ni fusiones sin CI y auditoría independiente de los HEAD finales.

## Infraestructura técnica preparada (PR #83)

`clinical/scripts/human_factors_tools.py` (solo stdin/stdout): manifiesto versionado de escenarios sintéticos, asignación AB/BA equilibrada por códigos seudónimos, validación de registros cerrados, análisis agrupado y exportación reproducible con huellas. Detalle y límites: [protocolo](R14_PROTOCOLO_FACTORES_HUMANOS_R5_1.md), sección «Etapa 1». **No se reclutan participantes, no se fija tamaño muestral ni umbral y el estudio sigue `NOT_EXECUTED`.**
