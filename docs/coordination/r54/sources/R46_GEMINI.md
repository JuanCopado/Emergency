# R46 — Auditoría Científica y Preparación de Validación Médica

* **Repositorio:** `JuanCopado/Emergency`
* **Prioridad:** P1
* **Fecha de corte científico y regulatorio:** `2026-11-24`
* **Estado de gobernanza:** `CLINICALLY_PENDING` | `NO_GO_CLINICAL_RELEASE` | `status: yellow` (`last_checked: 2026-09-17`, sin actualizar) | `R5-1 abierto` | `R5-2 pendiente` | `G05 bloqueado`
* **Autoridad de aprobación clínica:** Exclusivamente el médico propietario *(sin validación adicional de Farmacia en el flujo interno)*

---

## 1. Informe Científico y Estado Real de R5-1 / R5-2

### 1.1 Recuperación de Contratos, Decisiones Aprobadas y Estado de Inventarios

1. **Contrato de telemetría (`canonical-r27-v1.2`):** Consolidado en 41 claves literales (PR97 fusionada; referencia `25c0735d`) con retrocompatibilidad `v1` y `v1.1`. Se conserva íntegramente `role_group` (médico/enfermería) y la estratificación experimental (`sequence`, `period`, `subblock`, `set_id`, `stimulus_id`, `stimulus_hash_sha256`, `device_type`, `viewport_width_px`). La proyección analítica de 22 campos permanece `BLOCKED` para evitar fabricar `session_opaque_id`/`observation_source` o perder estratificación.
2. **Decisiones médicas ya aprobadas (coherentes y vigentes — prohibido reabrir):**
   * **`DEC-CLIN-R15-01`:** Textos literales de abstención técnica de Capa 7 en `pt-PT` (`T1–T4`).
   * **`PTBR-MOD` (R39):** Paquete de selección y compatibilidad de modalidad en `pt-BR` (`PTBR-MOD-01` a `PTBR-MOD-04` + `PTBR-MOD-UI-01` a `05`, incluyendo el ajuste médico `"está danificado"` en `PTBR-MOD-03`).
   * **Coherencia clínica:** Todas las decisiones aprobadas refuerzan un principio único: rechazo estrictamente técnico, ausencia de clasificación diagnóstica automática y no exclusión de patología.
3. **Inventarios separados de estímulos:**
   * **Receptor integrado (`codex/v144-international-scope-20261116`):** 5 estímulos de estudio + 2 QA.
   * **PR89 (banco de estudio):** 10/30 estímulos de estudio cargados *(20/30 pendientes de incorporación física; 30/30 pendientes de adjudicación médica formal)*.

### 1.2 Estado Real de R5-1 y R5-2

| Compuerta | Estado verificado | Alcance y bloqueo efectivo | Lo que no es verificable desde esta sesión |
|---|---|---|---|
| **R5-1** | **`ABIERTO` (Prioridad P1)** | Bloquea cualquier activación asistencial, reclutamiento de profesionales o uso con pacientes reales (`CLINICALLY_PENDING` / `NO_GO_CLINICAL_RELEASE`). Exige cierre de seguridad operativa y salvaguardas clínicas antes de habilitar flujos clínicos. | El diff interno de código/tickets asociado a R5-1 en el árbol local (`NOT_VERIFIED_IN_CHAT_CONTEXT`). |
| **R5-2** | **`PENDIENTE`** | Bloquea la promoción de `clinical-image-interpretation` de `YELLOW` a `GREEN` y el paso a validación clínica. Requiere: (1) cotejo literal de `clinical-images.md`, `image-modalities.md` y `src-b5e20534`, (2) banco completo de 30 estímulos adjudicado por el médico propietario y (3) métricas de seguridad verificadas (`diagnostic performance not established` en `workflow v1.4`). | El contenido literal interno de `clinical-images.md`, `image-modalities.md` y los 10 estímulos ya presentes en PR89 (`NOT_VERIFIED_IN_CHAT_CONTEXT`). |

### 1.3 Diferenciación: Evidencia Científica vs. Validación Técnica vs. Validación Clínica

| Nivel | Qué acredita | Estado actual en `JuanCopado/Emergency` | ¿Permite salir de `YELLOW` o `CLINICALLY_PENDING`? |
|---|---|---|---|
| **1. Evidencia científica y normativa** | Coherencia de las reglas del módulo con guías internacionales vigentes, sociedades científicas y marcos regulatorios (MDR/IVDR, EU AI Act `CELEX:02024R1689-20260727`, FDA CDS 2026, ACR–SIIM 2026). | **En curso avanzado** (marco regulatorio cerrado; contraste por modalidad definido; pendiente cotejo literal de 3 archivos `.md`/`.json`). | **No.** Solo acredita validez documental (`last_checked`). |
| **2. Validación técnica** | Determinismo de esquema (`canonical-r27-v1.2`), integridad SHA-256, aislamiento de laboratorio (`?lab_entry=`), bloqueo de envío sin evaluación clínica (`workflow v1.4`) y pruebas E2E sintéticas. | **Completada en laboratorio** (PR95, PR96 y PR97 fusionadas en rama internacional). | **No.** Acredita seguridad de software, no eficacia diagnóstica. |
| **3. Validación clínica** | Desempeño diagnóstico y de seguridad medido sobre el **banco completo de 30 estímulos adjudicados** por el médico propietario y posterior piloto humano autorizado (sensibilidad en patología tiempo-crítica, tasa de abstención correcta, equidad por subgrupo/fototipo y control de sesgo de automatización). | **`NO ESTABLECIDA`** (`diagnostic performance not established`). | **Sí (requisito imprescindible).** Sin ella se mantiene `YELLOW` y `NO_GO_CLINICAL_RELEASE`. |

---

## 2. Auditoría Clínica por Dominio y Matriz de Evidencias

*(Se omiten los hitos regulatorios generales ya cerrados en R39–R43 salvo su aplicación directa a cada dominio).*

### 2.1 Auditoría de Criterios Diagnósticos: Heridas, Radiología y POCUS

#### A. Heridas Traumáticas e Infecciones de Piel y Partes Blandas (SSTI)
* **Indicaciones del módulo:** Soporte estructurado de triaje/documentación visual y compuertas de seguridad; **no** diagnóstico definitivo ni prescripción autónoma.
* **Contraindicaciones y limitaciones críticas:**
  1. **Lesión tendinosa o nerviosa oculta (especialmente mano):** Una fotografía superficial no descarta sección parcial/total de tendones flexores/extensores ni lesión de nervios digitales; exige exploración física neurovascular y tendinosa documentada **antes** de infiltrar anestesia local (WSES).
  2. **Cuerpo extraño retenido:** La inspección fotográfica no excluye vidrio, madera, metal ni restos orgánicos; requiere exploración instrumental y/o imagen dirigida (Rx para radiopacos; ecografía/TC para radiolúcidos).
  3. **Infección necrosante de partes blandas (NSTI):** El eritema o edema inicial en imagen puede subestimar una fascitis necrosante; dolor desproporcionado, progresión rápida, crepitación o inestabilidad hemodinámica obligan a control quirúrgico inmediato y antibiótico empírico de amplio espectro (WSES / IDSA).
  4. **Profilaxis antitetánica y antirrábica:** No puede inferirse de la imagen de la herida; depende del estado vacunal del paciente y de la clasificación de herida limpia vs. sucia/desvitalizada/mordedura (CDC 2024).

#### B. Radiología de Urgencias (Rx Tórax/MSK y TC/RM)
* **Indicaciones del módulo:** Apoyo adjunto sujeto a lectura clínica y radiológica definitiva.
* **Contraindicaciones y limitaciones críticas:**
  1. **Sesgo de automatización y satisfacción de búsqueda:** En Rx osteoarticular de urgencias, la asistencia algorítmica mejora la detección de fracturas pero puede reducir la vigilancia sobre hallazgos no fracturarios (luxaciones sutiles, derrames, lesiones líticas); el clínico debe interpretar la Rx **antes** de consultar la salida del sistema (NICE HTG739).
  2. **Exclusiones poblacionales:** Población pediátrica (cartílagos de crecimiento) y patología ósea subyacente fuera del dominio validado.
  3. **Integridad volumétrica DICOM (TC/RM):** Prohibido descartar hemorragia intracraneal de pequeño volumen ($< 1.5\text{ mL}$) o isquemia aguda sobre capturas de pantalla aisladas o series parciales no DICOM (AHA/ASA 2026; NICE HTG708; ACR–SIIM 2026).

#### C. POCUS (Point-of-Care Ultrasound en Urgencias)
* **Indicaciones del módulo:** Asistencia documental/flujo en exploración ecográfica clínica a pie de cama.
* **Contraindicaciones y limitaciones críticas:**
  1. **Dependencia del operador y naturaleza dinámica:** POCUS es un procedimiento clínico en tiempo real integrado en la reanimación o en algoritmos por síntoma/signo (ACEP 2023/2026; IFEM). Una imagen estática aislada **no** acredita ventana acústica completa ni ausencia de líquido libre (eFAST), taponamiento pericárdico, neumotórax, aneurisma de aorta abdominal o TVP.
  2. **Correlación clínica obligatoria:** Un hallazgo ecográfico negativo con alta probabilidad pretest exige imagen consultiva (TC/ecografía reglada) o monitorización seriada.

### 2.2 Matriz de Evidencias Clínicas Verificables (Corte: `2026-11-24`)

| Dominio | Fuente primaria / Sociedad científica | Fecha / Identificador verificable | Calidad / Nivel | Aplicabilidad y restricción para el proyecto |
|---|---|---|---|---|
| **Heridas traumáticas en urgencias** | **WSES** — *Management of traumatic wounds in the Emergency Department* (*World J Emerg Surg* 2016;11:30) | 18 jun 2016 (`PMC4912791`) | Consenso internacional de sociedad científica | Aplica directamente: estratificación de riesgo de infección, búsqueda de cuerpo extraño (Rx/US/TC), examen previo a anestesia en mano y profilaxis antitetánica. |
| **Infecciones de piel y partes blandas (SSTI / NSTI)** | **WSES / GAIS / WSIS / SIS-E / AAST** — *Global Clinical Pathways for SSTIs* (*World J Emerg Surg* 2022;17:3) & **IDSA** *Practice Guidelines for SSTIs* (*Clin Infect Dis* 2014;59:e10–e52) | 2022 (`WJES 17:3`) / 15 jul 2014 (`DOI: 10.1093/cid/ciu296`) | Guías clínicas de sociedades científicas (GRADE) | Aplica directamente: drenaje como pilar en absceso simple; diagnóstico precoz y cirugía urgente en NSTI; ecografía/TC como apoyo en paciente inestable. |
| **Profilaxis antitetánica en heridas** | **CDC** — *Clinical Guidance for Wound Management to Prevent Tetanus* | Actualizada 15 may 2024 (`cdc.gov/tetanus/hcp/clinical-guidance`) | Guía oficial de agencia sanitaria | Aplica como referencia estructural: distingue herida limpia/menor vs. sucia/mayor y exige historial vacunal + TIG 250 UI según estado inmune. |
| **Radiografía en urgencias (MSK y Tórax)** | **NICE HTG739** *(fracturas en urgencias, EVA)* & **NICE HTG696** *(Rx tórax cáncer pulmón, EVA)* | Pub. 14 ene 2025, actual. **23 oct 2026** / Actual. **10 feb 2025** | Evaluación HTA (Early Value Assessment) | Aplica con restricción: uso exclusivamente adjunto, lectura clínica previa a IA, vigilancia de hallazgos no fracturarios y límites pediátricos. No extrapolar a otras herramientas. |
| **TC / RM en ictus agudo y neuroimagen** | **AHA/ASA** *2026 Guideline for Early Management of Acute Ischemic Stroke* (*Stroke* 2026) & **NICE HTG708** | 2026 (`DOI: 10.1161/STR.0000000000000513`) / Actual. 2 may 2024 | Guía de práctica clínica (COR/LOE) + HTA | Aplica directamente: posprocesado CTP/DWI-PWI como apoyo (COR 2a, LOE B-R); lectura especialista obligatoria y serie DICOM completa. |
| **POCUS en urgencias** | **ACEP** *Ultrasound Guidelines: Emergency, Point-of-Care, and Clinical Ultrasound Guidelines in Medicine* & **IFEM** *PoCUS Curriculum Guidelines* | 2023 (pub. portal ACEP **26 ene 2026**) / 23 nov 2021 | Política/guía oficial de sociedades de urgencias | Aplica directamente: POCUS es acto clínico dinámico a pie de cama; prohíbe validar diagnósticos negativos sobre fotogramas estáticos descontextualizados. |
| **Dermatología y fototipos** | **NICE HTG746** *(triaje lesiones cutáneas, EVA)* & **AAD** *Position Statement on Augmented Intelligence (AuI)* | Pub. 1 may 2025, actual. **17 mar 2026** / Vigente 2024–2027 | Evaluación HTA + Posicionamiento sociedad | Aplica directamente: revisión médica obligatoria en piel oscura (**Fitzpatrick V–VI**) por evidencia insuficiente y riesgo de falsos negativos. |
| **Gobernanza IA en imagen médica** | **ACR–SIIM** *Practice Parameter for Imaging AI* & marco *JACR Assess-AI* | **5 may 2026** (ACR DocId 217) | Parámetro de práctica profesional | Aplica directamente: exige validación local previa, monitorización de deriva (*drift*), reglas de parada y auditoría de casos discordantes. |

---

## 3. Protocolo de Adjudicación Médica del Banco de 30 Estímulos

> *Regla estricta:* Ningún caso se adjudica en este documento en nombre del médico propietario. Este esquema constituye la plantilla oficial de adjudicación para el propietario sobre los 10 estímulos existentes en PR89 y los 20 estímulos pendientes de incorporación.

### 3.1 Estructura del Banco (30 Estímulos)
* **Distribución experimental obligatoria (PR96):** 2 conjuntos independientes (**Set 1**: 15 estímulos; **Set 2**: 15 estímulos), cubriendo por periodo: **M1 = 4** (adversarial / incompatibilidad de modalidad), **M2 = 2** (fallo técnico / corrupción / disparo Capa 7) y **M3 = 9** (válidos / flujo estándar).
* **Cobertura clínica exigida:** Heridas traumáticas/SSTI, Radiología de urgencias (Rx MSK/tórax y cortes TC), POCUS (clips/ventanas estandarizadas), ECG y documentos clínicos, incluyendo variantes de calidad degradada (`kind=null`, archivo corrupto, formato no soportado) y diversidad de subgrupos (edad/fototipo).

### 3.2 Rúbrica Obligatoria por Estímulo (`STIM-01` a `STIM-30`)

Para que un estímulo sea válido para el banco adjudicado (requisito de salida de `YELLOW`), el médico propietario debe completar y firmar los siguientes campos:

| Campo de adjudicación | Valores / Criterio exigido |
|---|---|
| **`stimulus_id` y `stimulus_hash_sha256`** | Identificador único + SHA-256 binario exacto del archivo físico (garantía de inmutabilidad). |
| **`set_id` y `mechanism_id`** | `Set 1` o `Set 2` \| `M1` (adversarial), `M2` (abstención técnica) o `M3` (válido). |
| **`clinical_domain` y `expected_modality`** | Dominio (`wound`, `radiology_rx`, `radiology_ct`, `pocus`, `ecg`, `dermatology`, `document`) y modalidad verdadera verificable. |
| **`clinical_ground_truth` (Diagnóstico de referencia)** | Diagnóstico clínico confirmado y hallazgos críticos (*red flags*: p. ej., fractura oculta, NSTI, cuerpo extraño, líquido libre, HIC) acreditados por fuente independiente al sistema. |
| **`technical_integrity_label`** | `intact_diagnostic_quality` \| `corrupted_unreadable` \| `unsupported_format` \| `incomplete_series_or_static_frame` \| `wrong_modality_fixture`. |
| **`expected_system_behavior`** | Conducta normativa esperada en Brazo B (`Layer 7 trigger + abstención técnica` vs. `paso válido con advertencia de no autonomía`). |
| **`adjudication_status` y firma** | `ADJUDICATED_APPROVED` \| `REJECTED_REPLACE_STIMULUS` + Identificador y fecha del médico propietario. |

---

## 4. Discrepancias Internacionales y Adaptación por País

El ámbito internacional del proyecto abarca **España (`es-ES`)**, **Colombia (`es-CO`)**, **Portugal (`pt-PT`)** y **Brasil (`pt-BR`, solo laboratorio)**.

| Dimensión | España (`es-ES`) y Portugal (`pt-PT`) — UE | Colombia (`es-CO`) | Brasil (`pt-BR`) | Regla de adaptación en el proyecto |
|---|---|---|---|---|
| **Marco regulatorio SaMD / IA** | **MDR (UE) 2017/745** (Regla 11) + **EU AI Act (`CELEX:02024R1689-20260727`)**: transparencia Art. 50 vigente desde `2026-08-02`; alto riesgo Art. 6(1)/Anexo I aplicable desde `2028-08-02`. | **INVIMA** (Decreto 4725 de 2005 y lineamientos SaMD como dispositivo médico según finalidad diagnóstica/terapéutica). | **ANVISA** (**RDC nº 657/2022**, regulación específica de Software como Dispositivo Médico — SaMD). | Mantener `CLINICALLY_PENDING` y `NO_GO_CLINICAL_RELEASE` en las 4 jurisdicciones; prohibir toda afirmación de marcado CE o registro sanitario mientras no exista evaluación de conformidad. |
| **Profilaxis antitetánica y rabia en heridas** | Esquemas calendario nacional SNS (España) / SNS (Portugal); rabia terrestre autóctona prácticamente ausente en península (salvo murciélagos/viajeros). | Protocolos INS / MinSalud Colombia; **riesgo endémico de rabia** en mordeduras animales y mayor variabilidad en cobertura vacunal previa / disponibilidad de TIG. | Protocolos Ministério da Saúde (Brasil); **profilaxis antirrábica** obligatoria en algoritmo de mordeduras y esquema antitetánico con dT/SAT/IGHAT. | El módulo **nunca** debe emitir pautas cerradas de vacunación o inmunoglobulina solo a partir de la foto de la herida; debe exigir verificación del protocolo nacional e historial vacunal. |
| **Epidemiología antimicrobiana (SSTI)** | Predominio de *S. aureus* sensible a meticilina (MSSA) en comunidad; tasas bajas de CA-MRSA respecto a América. | Alta circulación comunitaria de **CA-MRSA** en SSTI purulentas y abscesos complicados. | Presencia relevante de CA-MRSA en centros urbanos y protocolos hospitalarios diferenciados. | Abstenerse de recomendar antibioterapia empírica desde el módulo de imagen; delegar siempre a guía clínica local y gravedad sistémica. |
| **Localización lingüística (`pt-PT` vs `pt-BR`)** | `pt-PT` aprobado (`DEC-CLIN-R15-01`) y activo en laboratorio. | `es-CO` alineado con `es-ES` en términos técnicos de seguridad. | `PTBR-MOD` aprobado en R39; `PTBR-PIX` bloqueado hasta especificación literal completa. `pt` genérico $\rightarrow$ `HARD_FAIL`. | Prohibido mezclar cadenas `pt-PT` y `pt-BR` o usar `pt` genérico sin variante regional. |

---

## 5. Checklist Clínica de Auditoría

| # | Ítem de verificación clínica y de gobernanza | Estado | Evidencia / Criterio |
|---|---|---|---|
| 1 | Prohibición explícita de diagnóstico autónomo en todas las modalidades | **`PASS` (en contrato `workflow v1.4`)** | Confirmado en `evidence-registry.json` y textos R15-01; cotejo literal de `.md` pendiente. |
| 2 | Abstención técnica ante modalidad ausente, incompatible, corrupta o no soportada | **`PASS` (en laboratorio)** | Textos `pt-PT` (`DEC-CLIN-R15-01`) y `PTBR-MOD` (R39) cerrados. |
| 3 | Coherencia de decisiones médicas aprobadas (sin duplicar solicitudes) | **`PASS`** | `DEC-CLIN-R15-01` y `PTBR-MOD` preservadas intactas; `PTBR-PIX` aislada. |
| 4 | Cotejo literal de `clinical-images.md`, `image-modalities.md` y `src-b5e20534` | **`NOT_VERIFIED`** | Archivos localizados en R42/R43; cuerpo literal pendiente de extracción. |
| 5 | Vigencia de registro de evidencia (`last_checked: 2026-09-17`, 68 días $>$ 30) | **`FAIL` (vencido — mantenido intencionadamente)** | No se renueva automáticamente hasta cotejo literal y revisión médica. |
| 6 | Completitud física del banco de estudio (30/30 estímulos) | **`BLOCKED` (10/30 en PR89; 5+2 QA en receptor)** | Faltan 20 estímulos de estudio por incorporar al banco. |
| 7 | Adjudicación médica independiente del banco de 30 estímulos | **`PENDING` (0/30 adjudicados)** | Requiere firma del médico propietario sobre la rúbrica de la Sección 3. |
| 8 | Rendimiento diagnóstico y métricas de seguridad establecidas | **`BLOCKED`** | `stored_version: workflow v1.4; diagnostic performance not established`. |
| 9 | Estado del registro de evidencia (`status: yellow`) | **`PASS` (bloqueo activo)** | Prohibida promoción automática a `GREEN`. |
| 10 | Compuertas globales `R5-1`, `R5-2`, `CLINICALLY_PENDING` y `NO_GO_CLINICAL_RELEASE` | **`PASS` (bloqueos vigentes)** | Sin pacientes reales ni reclutamiento autorizado. |

---

## 6. Discrepancias Resueltas Documentalmente y Riesgos Clínicos Pendientes

### 6.1 Discrepancias Resueltas Documentalmente (Sin Decisión Pendiente del Propietario)
1. **Colisión nominal `T1–T4` en `pt-BR`:** Resuelta separando `PTBR-MOD` (aprobado R39) de `PTBR-PIX` (acceso a píxeles, bloqueado R40).
2. **Aprobación redundante de `PTBR-MOD`:** Resuelta declarando vigente `APPROVED_MEDICAL_R39` y prohibiendo reabrirla.
3. **Inferencia de error humano por inactividad (`false_cancellation_human`):** Resuelta declarando la variable `NON_OBSERVABLE` por DOM puro en la app actual; la ausencia de confirmación nunca se etiqueta como error humano.
4. **Contaminación conductual por intentos de envío bloqueados (`force_submit_attempts_count`):** Resuelta separando el contador técnico del arnés de las métricas conductuales humanas.
5. **Preservación de estratificación clínica (`role_group`):** Resuelta protegiendo los 41 campos maestros de `canonical-r27-v1.2` y bloqueando la proyección de 22 campos.
6. **Fechas regulatorias EU AI Act vs. MDR/IVDR:** Resuelta mediante el texto consolidado `CELEX:02024R1689-20260727` (Art. 50 vigente desde `2026-08-02`; Anexo I/MDR aplazado a `2028-08-02`; MDR/IVDR sin cambios).

### 6.2 Registro de Riesgos Clínicos Actuales (Clasificados por Gravedad)

| ID Riesgo | Descripción del riesgo clínico | Gravedad | Propuesta de resolución justificada |
|---|---|---|---|
| **RSK-CLIN-01** | **Falsa tranquilidad clínica por capturas estáticas o series incompletas** en POCUS (eFAST/cardíaco) o TC craneal (HIC pequeña $< 1.5\text{ mL}$ / ictus agudo), interpretando ausencia de alerta técnica como exclusión de patología grave. | **`CRITICAL`** | Incorporar regla explícita en `image-modalities.md` y en el banner de Capa 7 que prohíba descartar patología aguda sobre fotogramas estáticos POCUS o series parciales no DICOM (ver Ficha `MED-DEC-R46-01`). |
| **RSK-CLIN-02** | **Sesgo de equidad y falsos negativos en dermatología** por infrarrepresentación de fototipos oscuros (**Fitzpatrick V–VI**) o variabilidad de iluminación/enfoque en heridas y lesiones cutáneas. | **`HIGH`** | Exigir advertencia obligatoria de revisión clínica presencial/dermatoscópica en fototipos V–VI (NICE HTG746) e incluir estratificación por fototipo en el banco de 30 estímulos. |
| **RSK-CLIN-03** | **Sesgo de automatización y omisión de lesiones asociadas** en Rx de urgencias (fracturas ocultas no señaladas o patología no fracturaria) y lesiones tendinosas/nerviosas en heridas de mano no detectables por foto. | **`HIGH`** | Establecer en `image-modalities.md` la secuencia obligatoria de lectura clínica previa a la salida del sistema y checklist de exploración neurovascular/tendinosa pre-anestesia en heridas de mano. |
| **RSK-CLIN-04** | **Validación experimental sesgada por banco incompleto o sin adjudicar** (10/30 estímulos en PR89; 0/30 con firma de adjudicación médica), invalidando la validez clínica del piloto. | **`HIGH`** | Completar los 30/30 estímulos y ejecutar el protocolo de adjudicación médica (Ficha `MED-DEC-R46-02`) antes de cerrar `R5-2` o autorizar piloto humano. |
| **RSK-CLIN-05** | **Divergencia terapéutica internacional** en profilaxis antitetánica/antirrábica y antibioterapia empírica de heridas entre España, Colombia, Portugal y Brasil. | **`MEDIUM`** | Mantener el módulo estrictamente circunscrito a clasificación técnica/triaje visual y remitir toda pauta vacunal o antimicrobiana al protocolo nacional local. |

---

## 7. Fichas de Decisión Médica Materialmente Pendientes

*(Exclusivamente decisiones materiales nuevas para el médico propietario. No se incluyen decisiones ya aprobadas como `PTBR-MOD` ni paquetes sin especificación literal completa como `PTBR-PIX`).*

### Ficha 1 — `MED-DEC-R46-01`
* **Identificador:** `MED-DEC-R46-01`
* **Problema clínico:** El módulo `clinical-image-interpretation` (`workflow v1.4`) carece actualmente de rendimiento diagnóstico establecido (`diagnostic performance not established`) y existe riesgo clínico crítico de que un usuario utilice una captura estática de POCUS, una serie parcial de TC o una fotografía superficial de herida para excluir patología urgente (hemorragia intracraneal pequeña, líquido libre/taponamiento, sección tendinosa/nerviosa en mano o melanoma en fototipos oscuros).
* **Evidencia científica:** Las guías internacionales vigentes establecen que: (1) POCUS es un procedimiento dinámico a pie de cama cuya validez depende de la adquisición en tiempo real y correlación clínica (ACEP 2023/2026; IFEM 2021); (2) la neuroimagen en ictus/hemorragia exige serie volumétrica DICOM íntegra y lectura especialista (AHA/ASA 2026; NICE HTG708); (3) las heridas de mano requieren examen neurovascular/tendinoso previo a anestesia y búsqueda de cuerpo extraño (WSES 2016/2022); y (4) las herramientas de imagen dermatológica requieren revisión médica obligatoria en fototipos Fitzpatrick V–VI (NICE HTG746, marzo 2026).
* **Fuente verificable y fecha:**
  * *ACEP Ultrasound Guidelines* (2023; publicación oficial ACEP `2026-01-26`).
  * *AHA/ASA 2026 Guideline for Early Management of Acute Ischemic Stroke* (*Stroke* `2026`; DOI `10.1161/STR.0000000000000513`).
  * *NICE HTG746* (actualizada `2026-03-17`) y *NICE HTG739* (actualizada `2026-10-23`).
  * *WSES Management of traumatic wounds in the ED* (*World J Emerg Surg* `2016-06-18`; `PMC4912791`).
* **Riesgo clínico:** **CRÍTICO (`CRITICAL`)** — Falsa tranquilidad clínica y retraso diagnóstico/quirúrgico en patología tiempo-crítica ante imágenes parciales, estáticas o subgrupos infrarrepresentados.
* **Solución propuesta:** Incorporar como regla clínica obligatoria en `clinical/modules/clinical-images.md` y `clinical/modules/image-modalities.md` (manteniendo `CLINICALLY_PENDING` y sin activar uso asistencial) que: (a) ninguna salida o abstención del sistema excluye patología urgente, (b) queda prohibido evaluar POCUS sobre fotogramas estáticos aislados o TC/RM sin serie DICOM completa, (c) toda herida de mano exige exploración neurovascular/tendinosa directa, y (d) toda lesión cutánea en fototipos Fitzpatrick V–VI requiere valoración presencial/dermatoscópica obligatoria.
* **Pregunta concreta:** **¿Aprueba incorporar estas cuatro salvaguardas clínicas vinculantes en la documentación normativa del módulo (`clinical-images.md` e `image-modalities.md`) como requisito previo para cerrar `R5-2`, manteniendo `CLINICALLY_PENDING` y `NO_GO_CLINICAL_RELEASE`?**
  * [ ] **SÍ**
  * [ ] **NO**

---

### Ficha 2 — `MED-DEC-R46-02`
* **Identificador:** `MED-DEC-R46-02`
* **Problema clínico:** El banco de referencia experimental cuenta actualmente con 10/30 estímulos en PR89 (y 5+2 QA en el receptor integrado), sin adjudicación clínica firmada por el médico propietario (`0/30` adjudicados) y con `diagnostic performance not established`, lo que impide avanzar hacia la validación clínica y mantiene bloqueada la transición de `YELLOW` a `GREEN`.
* **Evidencia científica:** Tanto el parámetro de práctica profesional ACR–SIIM (mayo 2026) como los marcos de evaluación temprana NICE EVA (HTG739/HTG746) y los requisitos de gobernanza de dispositivos médicos con IA (`MDCG 2025-6`) establecen que la validez documental del flujo técnico no sustituye la adjudicación clínica independiente de un conjunto de referencia representativo con diagnóstico de verdad conocido, estratificado por modalidad y subgrupos de riesgo, antes de realizar pruebas con clínicos reales.
* **Fuente verificable y fecha:**
  * *ACR–SIIM Practice Parameter for Imaging Artificial Intelligence* (`2026-05-05`, ACR DocId 217) y marco *JACR Assess-AI* (`2026-05-05`).
  * *MDCG 2025-6 / AIB 2025-1: Interplay between MDR/IVDR and the AI Act* (`2025-06-26`).
* **Riesgo clínico:** **ALTO (`HIGH`)** — Ejecutar un piloto humano o promover el estado del módulo sin un banco completo de 30 estímulos adjudicados introduciría sesgo de referencia y ocultaría fallos de seguridad en escenarios adversariales (`M1`) o de abstención (`M2`).
* **Solución propuesta:** Aprobar el **Protocolo y Rúbrica de Adjudicación Médica de los 30 Estímulos** (Sección 3 de este informe) como único estándar válido para auditar los 10 estímulos existentes en PR89 y los 20 estímulos restantes, manteniendo `status: yellow`, `last_checked: 2026-09-17`, `CLINICALLY_PENDING` y `NO_GO_CLINICAL_RELEASE` hasta que los 30/30 estímulos cuenten con firma de adjudicación del médico propietario y métricas de seguridad verificadas.
* **Pregunta concreta:** **¿Aprueba la Rúbrica de Adjudicación Médica de los 30 Estímulos (Sección 3) como criterio vinculante para validar el banco completo antes de autorizar cualquier cierre de `R5-2` o promoción fuera de `YELLOW`?**
  * [ ] **SÍ**
  * [ ] **NO**