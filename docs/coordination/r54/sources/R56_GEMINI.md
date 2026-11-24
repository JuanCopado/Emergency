# R56 — Cierre Científico R46/R50 y Preparación de Adjudicación

* **Repositorio:** `JuanCopado/Emergency`
* **Prioridad:** P1
* **Fecha de corte:** `2026-11-24`
* **Acceso al repositorio / Dosier Codex R51/R54:** **`NO_REPO_ACCESS`** — En esta sesión no existe acceso al repositorio GitHub ni se ha recibido el dosier literal de Codex R51/R54 (`clinical-images.md`, `image-modalities.md`, `src-b5e20534` y manifiesto con los IDs reales/archivos de los 30 estímulos). No se reconstruye ni inventa ningún texto, archivo, hash ni diagnóstico.
* **Estado de gobernanza (inalterado):** `CLINICALLY_PENDING` | `status: yellow` | `last_checked: 2026-09-17` *(NO actualizada)* | `NO_GO_CLINICAL_RELEASE` | `R5-1 ABIERTO` | `R5-2 PENDIENTE` | `G05 BLOQUEADO`

---

## 1. Informe Científico Final R56 y Registro de Decisiones Aprobadas

### 1.1 Registro Consolidado de Decisiones Médicas Aprobadas *(Prohibido reabrir o re-solicitar)*

| ID Decisión | Fecha aprobación | Alcance exacto aprobado (formulación vinculante) | Verificación de incorporación en código/docs |
|---|---|---|---|
| **`DEC-CLIN-R15-01`** | Expediente R28 | 4 mensajes oficiales de abstención técnica de Capa 7 en `pt-PT` (`T1–T4`). | Incorporado en laboratorio (`pt-PT` activo). |
| **`PTBR-MOD`** | Cierre R39 | Paquete `PTBR-MOD-01..04` + `PTBR-MOD-UI-01..05` en `pt-BR` (selección/compatibilidad de modalidad; incluye ajuste `"está danificado"`). *`PTBR-PIX` permanece separado y bloqueado.* | Pendiente verificación de diccionario i18n en repo. |
| **`MED-DEC-R46-01`** | **`2026-11-24` (`SÍ`)** | Salvaguardas clínicas vinculantes en `clinical-images.md` e `image-modalities.md` bajo **formulación corregida R50** (sin umbral $< 1.5\text{ mL}$, PoCUS bajo filosofía *rule-in* sin descartar patología por fotograma estático, DICOM volumétrico íntegro en TC/RM, examen neurovascular/tendinoso pre-anestesia en mano, sin extrapolación universal de NICE HTG746 ni generalizaciones CA-MRSA por país). | **`NOT_VERIFIED_IN_REPO`** *(pendiente dosier Codex R51/R54 y aplicación de parches de la Sección 3).* |
| **`MED-DEC-R46-02`** | **`2026-11-24` (`SÍ`)** | Protocolo definitivo y rúbrica de adjudicación del banco experimental de 30 estímulos bajo **formulación corregida R50** (`N/A` explícito en estímulos no diagnósticos y separación estricta respecto a la validación estadística de eficacia diagnóstica). | **`ACTIVE_PROTOCOL_READY`** *(fichas preparadas en Sección 4; enlace a IDs reales pendiente de manifiesto Codex R51/R54).* |

### 1.2 Determinación sobre Actualización de `last_checked` (`2026-09-17`)

* **Dictamen:** **`NO PROCEDE ACTUALIZAR last_checked EN ESTE CORTE.`**
* **Justificación:** Aunque las 19 fuentes primarias externas están verificadas en R50 y el médico propietario aprobó `MED-DEC-R46-01` y `MED-DEC-R46-02` el `2026-11-24`, actualizar `last_checked` exige verificar físicamente que el texto real de `clinical/modules/clinical-images.md`, `clinical/modules/image-modalities.md` y `src-b5e20534` no contradice dichas fuentes ni conserva omisiones.
* **Condición exacta para actualización exclusivamente documental:** Una vez Codex aporte el dosier R51/R54, aplique las correcciones exactas de la Sección 3 y se verifique el diff limpio, **sí procederá** actualizar `last_checked` a la fecha de cierre documental **manteniendo obligatoriamente** `status: yellow`, `stored_version: workflow v1.4; diagnostic performance not established`, `CLINICALLY_PENDING` y `NO_GO_CLINICAL_RELEASE`.

### 1.3 Requisitos que Continúan Impidiendo Cerrar `R5-1` y `R5-2`

| Compuerta | Estado actual | Bloqueos activos pendientes de resolución |
|---|---|---|
| **`R5-1`** | **`ABIERTO`** | 1. Ausencia de verificación sobre el repositorio real de la implementación efectiva de las salvaguardas `MED-DEC-R46-01` en `clinical-images.md` e `image-modalities.md`.<br>2. Inexistencia de evidencia de seguridad operativa con usuarios reales (piloto humano de factores humanos aún bloqueado; `PTBR-PIX` sin especificación literal ni aprobación).<br>3. Restricción regulatoria activa: cualquier función que adquiera/procese imágenes médicas queda fuera de *non-device CDS* (FDA CDS `2026-01-29`) y bajo MDR/IVDR vigente + EU AI Act Art. 50 vigente desde `2026-08-02`. |
| **`R5-2`** | **`PENDIENTE`** | 1. Cotejo literal inconcluso de `clinical-images.md`, `image-modalities.md` y `src-b5e20534` (`BLOCKED_PENDING_CODEX_R51_R54`).<br>2. Banco experimental incompleto y sin adjudicar: **10/30** estímulos en PR89 (20/30 pendientes de incorporación) y **0/30** fichas firmadas `SÍ/NO` por el médico propietario.<br>3. Ausencia total de **validación estadística de eficacia diagnóstica** (`diagnostic performance not established`), requisito indispensable para considerar cualquier salida de `YELLOW` hacia `GREEN`. |

---

## 2. Matriz de Cotejo Literal (`clinical-images.md`, `image-modalities.md` y `src-b5e20534`)

**Taxonomía R56:** `VALIDATED` · `CORRECTION_REQUIRED` · `UNSUPPORTED` · `NOT_APPLICABLE`.

> *Nota de rigor:* Las filas con artefactos no recibidos en esta sesión se etiquetan con el prefijo `PENDING_CODEX_R51_R54` junto a la clasificación verificada del requisito normativo R50 que determinará su estado al recibir el volcado literal.

| # | Archivo / Fuente | Bloque / Afirmación auditada | Fuente primaria verificada en R50 | Clasificación R56 | Observación y verificación de alcance `MED-DEC-R46-01` |
|---|---|---|---|---|---|
| 1 | `evidence-registry.json` | `status: yellow`, `priority: high`, `stored_version: workflow v1.4; diagnostic performance not established` | ACR–SIIM (`2026-05-05`), FDA CDS (`2026-01-29`), MDR / Reg. (UE) `2026/1744` | **`VALIDATED`** | Metadatos veraces y conservadores; coherentes con `NO_GO_CLINICAL_RELEASE`. |
| 2 | `evidence-registry.json` | `last_checked: 2026-09-17` (68 días $>$ límite 30 días) | Política interna de vigencia (30 días) | **`CORRECTION_REQUIRED`** *(bloqueada hasta cotejo literal)* | Vencida; solo actualizable tras cotejar `.md`/`src-b5e20534` y aplicar parches de Sección 3. |
| 3 | `evidence-sources.json` (`src-internal-image-safety-workflow` y `src-internal-clinical-image-reference-set`) | Clasificación de artefactos internos frente a evidencia clínica externa | ACR–SIIM (`2026-05-05`), `MDCG 2025-6` (`2025-06-19`) | **`NOT_APPLICABLE`** *(como evidencia diagnóstica)* / `PENDING_CODEX_R51_R54` | Son controles técnicos/de referencia internos; no acreditan eficacia diagnóstica. |
| 4 | `evidence-sources.json` (`src-b5e20534`) | Entrada compuesta multi-modalidad | 19 fuentes primarias verificadas en R50 (Sección 3.3) | **`CORRECTION_REQUIRED`** *(pendiente volcado JSON Codex)* | Debe desagregarse por modalidad con fechas/DOIs/ámbitos exactos R50 y sin referencias obsoletas o extrapoladas. |
| 5 | `clinical-images.md` | No autonomía diagnóstica, abstención técnica de Capa 7, transparencia IA (Art. 50) y prohibición de excluir patología urgente | FDA CDS (`2026-01-29`), EU AI Act Art. 50 (`2026-08-02`), `MDCG 2025-6` (`2025-06-19`), ACR–SIIM (`2026-05-05`) | **`PENDING_CODEX_R51_R54`** *(objetivo: `VALIDATED` tras parche 3.1)* | Comprobar literalidad al recibir dosier; incorporar cláusula aprobada `MED-DEC-R46-01`. |
| 6 | `image-modalities.md` — **Radiografía (Rx)** | Apoyo adjunto en urgencias, no sustitución de lectura radiológica definitiva, orden de lectura clínica previa, alcance pediátrico exacto | **NICE HTG739** (actual. `2026-10-23`), **NICE HTG696** (actual. `2025-02-10`, *solo AP cáncer pulmón*), ACR–SIIM (`2026-05-05`) | **`PENDING_CODEX_R51_R54`** *(revisar `CORRECTION_REQUIRED` si generaliza HTG739/HTG696)* | No generalizar exclusión pediátrica ni aplicar HTG696 a Rx tórax urgente aguda. |
| 7 | `image-modalities.md` — **ECG** | Aumento de decisión clínica, confirmación médica directa, límites por artefactos/calibración | **AHA** (*Circulation* `2024-04-02`, PMID `38415358`), **EHRA/HRS/ESC** (*Europace* `2025-05-07`, PMID `40163651`) | **`PENDING_CODEX_R51_R54`** | Verificar que toda alerta algorítmica exige lectura médica y correlación clínica. |
| 8 | `image-modalities.md` — **POCUS** | Naturaleza dinámica a pie de cama, dependencia de operador, filosofía *rule-in*, imposibilidad de descartar patología aguda con fotograma estático aislado | **ACEP** (*Ann Emerg Med* `2023-09`, DOI `10.1016/j.annemergmed.2023.06.005`), **IFEM** (`2021-11-23`) | **`PENDING_CODEX_R51_R54`** *(objetivo: `VALIDATED` tras parche 3.2)* | Incorporar redacción exacta R50 de `MED-DEC-R46-01` (sin prohibir archivo QA de capturas estáticas). |
| 9 | `image-modalities.md` — **TC / RM** | Series volumétricas DICOM íntegras, lectura especialista, sin informe autónomo, **sin umbral no validado $< 1.5\text{ mL}$** | **AHA/ASA AIS 2026** (*Stroke* `2026-08`, Epub `2026-01-26`, PMID `41582814`), **NICE HTG708** (`2024-05-02`), ACR–SIIM (`2026-05-05`) | **`PENDING_CODEX_R51_R54`** *(cualquier cita a $< 1.5\text{ mL}$ = **`UNSUPPORTED`**)* | Verificar ausencia de umbrales inventados y exigencia de DICOM íntegro (`MED-DEC-R46-01`). |
| 10 | `image-modalities.md` — **Heridas traumáticas / SSTI** | Examen neurovascular/tendinoso pre-anestesia en mano, sospecha de cuerpo extraño/NSTI, remisión a guías locales para tétanos/rabia y antibióticos | **WSES/AcEMC** (`2016-06-18`, PMID `27330546`), **WSES/GAIS** (`2022-01-15`, PMID `35033131`), **IDSA** (`2014-07-15`, PMID `24947530`), **CDC** (`2026-09-08`) | **`PENDING_CODEX_R51_R54`** *(cualquier generalización CA-MRSA por país = **`UNSUPPORTED`**)* | Prohibido emitir pauta antibiótica o vacunal desde imagen; eliminar generalizaciones nacionales CA-MRSA. |
| 11 | `image-modalities.md` — **Dermatología** | Inteligencia aumentada, brecha de evidencia en piel oscura (**Fitzpatrick V–VI**), revisión clínica directa sin extrapolar NICE HTG746 fuera de DERM/NHS | **NICE HTG746** (actual. `2026-03-17`, ámbito: DERM en adultos $\ge 18$ años NHS), **AAD AuI** (`2019`) | **`PENDING_CODEX_R51_R54`** *(si generaliza HTG746 como contraindicación universal = **`CORRECTION_REQUIRED`**)* | Incorporar salvaguarda R50 exacta de `MED-DEC-R46-01`. |

---

## 3. Propuesta de Correcciones Documentales Exactas para Codex

*(Exclusivamente correcciones documentales en Markdown/JSON que implementan **`MED-DEC-R46-01` aprobada el `2026-11-24`** sin modificar lógica productiva, sin cambiar `status: yellow` y sin levantar `CLINICALLY_PENDING` / `NO_GO_CLINICAL_RELEASE`.)*

### 3.1 Bloque Normativo Exacto para `clinical/modules/clinical-images.md`

~~~markdown
## Límites Clínicos y Salvaguardas Obligatorias (MED-DEC-R46-01 — Aprobada 2026-11-24)

- **Estado de validación:** Este módulo opera bajo `workflow v1.4; diagnostic performance not established`, `status: yellow`, `CLINICALLY_PENDING` y `NO_GO_CLINICAL_RELEASE`. No constituye un sistema de diagnóstico autónomo ni sustituye el juicio clínico ni la lectura especialista.
- **No exclusión de patología:** Ninguna salida del sistema, ausencia de alerta o mensaje de abstención técnica (Capa 7) permite descartar patología urgente o tiempo-crítica.
- **Transparencia y supervisión humana:** De conformidad con el Art. 50 del Reglamento (UE) 2024/1689 (consolidado por Reg. (UE) 2026/1744) y las recomendaciones MDCG 2025-6 / ACR–SIIM (2026), el profesional debe realizar valoración clínica independiente y revisar la imagen/paciente sin delegar decisiones en la herramienta.
- **Prescripción y profilaxis:** El módulo no recomienda antibioterapia empírica ni esquemas de profilaxis antitetánica o antirrábica a partir de imágenes; toda conducta terapéutica o vacunal debe seguir los protocolos nacionales e institucionales y antibiogramas locales vigentes.
~~~

### 3.2 Bloques Normativos Exactos por Modalidad para `clinical/modules/image-modalities.md`

~~~markdown
### Radiografía (Rx de urgencias)
- Uso estrictamente adjunto; nunca sustituye la lectura radiológica definitiva.
- Para mitigar el sesgo de automatización y la omisión de hallazgos no fracturarios, el profesional debe interpretar la radiografía antes de revisar cualquier salida asistida.
- Las evaluaciones tempranas de tecnologías específicas (p. ej., NICE HTG739 en fracturas de urgencias o NICE HTG696 en derivaciones de atención primaria por sospecha de cáncer pulmonar) no son extrapolables a este módulo ni validan su desempeño en Rx torácica aguda o población pediátrica.

### ECG
- Toda salida o alerta algorítmica es meramente orientativa y exige lectura médica directa, correlación clínica y verificación de calidad técnica y calibración del trazado (AHA, *Circulation* 2024; EHRA/HRS/ESC, *Europace* 2025).

### POCUS (Ecografía clínica a pie de cama)
- PoCUS es un procedimiento clínico dinámico dependiente del operador que opera habitualmente bajo una filosofía *rule-in* integrada en la atención aguda (ACEP 2023; IFEM 2021).
- Una captura estática aislada —aunque sea válida para archivo de control de calidad (QA)— **no permite descartar patología aguda** (p. ej., líquido libre, taponamiento, neumotórax o TVP) ni sustituye una exploración PoCUS dinámica completa y correlacionada clínicamente.

### TC / RM (Neuroimagen y estudios seccionales)
- La valoración diagnóstica urgente exige **series volumétricas DICOM íntegras** y lectura por especialista (AHA/ASA 2026; NICE HTG708; ACR–SIIM 2026).
- Queda prohibido descartar hemorragia intracraneal, ictus isquémico agudo u otra patología crítica a partir de cortes aislados, capturas de pantalla comprimidas o series incompletas.

### Heridas traumáticas e infecciones de piel y partes blandas (SSTI)
- Una fotografía superficial no descarta lesión tendinosa, lesión nerviosa, cuerpo extraño retenido ni infección necrosante de partes blandas (NSTI) (WSES/AcEMC 2016; WSES/GAIS 2022).
- Toda herida en mano exige exploración neurovascular y tendinosa documentada **antes** de administrar anestesia local.
- La profilaxis antitetánica/antirrábica y la selección antimicrobiana dependen del historial vacunal, contexto clínico y guías/antibiogramas locales (CDC 2026), nunca de la imagen aislada.

### Dermatología (Lesiones cutáneas)
- La precisión de modelos de análisis de imagen en piel negra o morena (**fototipos Fitzpatrick V–VI**) no puede asumirse sin validación estratificada propia (brecha de evidencia documentada en NICE HTG746 para DERM en adultos del NHS y posicionamiento AAD AuI 2019).
- Toda lesión cutánea en fototipos Fitzpatrick V–VI requiere valoración clínica presencial y/o dermatoscópica directa obligatoria; ninguna salida del sistema excluye malignidad.
~~~

### 3.3 Desagregación Exacta de `src-b5e20534` para `clinical/references/evidence-sources.json`

Reemplazar la referencia compuesta opaca `src-b5e20534` (manteniendo trazabilidad en `supersedes: ["src-b5e20534"]`) por registros atómicos verificados en R50:

* `src-rx-nice-htg739` (NICE HTG739, pub. `2025-01-14`, actual. `2026-10-23`, ámbito: EVA NHS fracturas urgencias)
* `src-rx-nice-htg696` (NICE HTG696, pub. `2023-09-28`, actual. `2025-02-10`, ámbito: EVA AP cáncer pulmón — **no** Rx urgencias agudas)
* `src-ecg-aha-2024` (Armoundas et al., *Circulation* `2024-04-02`, DOI `10.1161/CIR.0000000000001201`, PMID `38415358`)
* `src-ecg-ehra-2025` (Svennberg et al., *Europace* `2025-05-07`, DOI `10.1093/europace/euaf071`, PMID `40163651`)
* `src-pocus-acep-2023` (ACEP, *Ann Emerg Med* `2023-09`;82(3):e115–e155, DOI `10.1016/j.annemergmed.2023.06.005`)
* `src-pocus-ifem-2021` (IFEM PoCUS Curriculum Guidelines, `2021-11-23`)
* `src-ct-aha-asa-2026` (Prabhakaran et al., *Stroke* `2026-08`, Epub `2026-01-26`, DOI `10.1161/STR.0000000000000513`, PMID `41582814`)
* `src-ct-nice-htg708` (NICE HTG708, pub. `2024-01-23`, actual. `2024-05-02`)
* `src-wounds-wses-2016` (Prevaldi et al., *WJES* `2016-06-18`, DOI `10.1186/s13017-016-0084-3`, PMID `27330546`)
* `src-ssti-wses-2022` (Sartelli et al., *WJES* `2022-01-15`, DOI `10.1186/s13017-022-00406-2`, PMID `35033131`)
* `src-ssti-idsa-2014` (Stevens et al., *CID* `2014-07-15`, DOI `10.1093/cid/ciu296`, PMID `24947530`)
* `src-tetanus-cdc-2026` (CDC Wound Management / Tetanus, actual. `2026-09-08`)
* `src-derm-nice-htg746` (NICE HTG746, pub. `2025-05-01`, actual. `2026-03-17`, ámbito: EVA DERM adultos $\ge 18$ años NHS)
* `src-derm-aad-2019` (AAD Position Statement on AuI, `2019`)
* `src-gov-acr-siim-2026` (ACR–SIIM Practice Parameter for Imaging AI, `2026-05-05`, DocId 217)
* `src-reg-fda-cds-2026` (FDA CDS Software Final Guidance, `2026-01-29`, Docket `FDA-2017-D-6569`)
* `src-reg-eu-2026-1744` (Reg. UE `2026/1744`, DOUE `2026-07-24`, vigor `2026-07-27`, `CELEX:02024R1689-20260727`)
* `src-reg-mdcg-2025-6` (MDCG 2025-6 / AIB 2025-1, `2025-06-19`)

---

## 4. Protocolo Definitivo de Adjudicación Médica (`MED-DEC-R46-02` Aprobada) y 30 Fichas Individuales SÍ/NO

### 4.1 Verificación del Protocolo Definitivo

* **Naturaleza del banco:** Banco experimental de **factores humanos y seguridad de abstención** ($N = 30$: Set 1 = 15, Set 2 = 15; por set: $\text{M1} = 4$, $\text{M2} = 2$, $\text{M3} = 9$). **No equivale a validación estadística de eficacia diagnóstica.**
* **Regla estricta de `N/A`:**
  * Todos los **`M2` (4 fichas)** se pre-marcan obligatoriamente con diagnóstico **`N/A`** (abstención técnica pura: archivo corrupto, formato no admitido o `kind=null`).
  * Todos los **`M1` (8 fichas)** se pre-marcan con diagnóstico **`N/A`** salvo que el escenario del manifiesto incorpore una bandera roja clínica explícita; requieren adjudicación de `expected_modality` real y desajuste adversarial inequívoco.
  * Los **`M3` (18 fichas)** requieren adjudicación diagnóstica y verificación de bandera roja si son imágenes clínicas, o **`N/A`** si corresponden a documentos clínicos/administrativos no diagnósticos.
* **Enlace al manifiesto real:** Al no haberse recibido el manifiesto de Codex R51/R54 en esta sesión, los campos de archivo físico, ID literal del manifiesto, `stimulus_hash_sha256` e imagen/referencia independiente se dejan explícitamente como `<PENDIENTE_MANIFIESTO_CODEX_R51_R54>` (cero invención).

### 4.2 Fichas Individuales de Adjudicación para Respuesta `SÍ / NO` del Médico Propietario (Slots 01–30)

#### SET 1 — Estímulos 01 a 15 (`M1`: 01–04 · `M2`: 05–06 · `M3`: 07–15)

| Slot | ID real manifiesto (`Codex R51/R54`) | Mec. | Archivo / Imagen + `SHA-256` | Modalidad esperada / Integridad técnica | Diagnóstico de referencia / Fuente independiente | Comportamiento esperado (Brazo B / Capa 7) | Decisión médica individual (`¿Aprueba este estímulo?`) |
|---|---|---|---|---|---|---|---|
| **01** | `<PENDIENTE_MANIFIESTO>` | **M1** | `<PENDIENTE>` / `<SHA-256>` | `<PENDIENTE>` / `modality_mismatch` | **`N/A`** *(salvo bandera roja explícita; ref: `<PENDIENTE>`)* | Disparo Capa 7 (`T2` incompatibilidad) + bloqueo envío sin evaluación clínica | `[ ] SÍ` · `[ ] NO` *(Firma/Fecha: _____)* |
| **02** | `<PENDIENTE_MANIFIESTO>` | **M1** | `<PENDIENTE>` / `<SHA-256>` | `<PENDIENTE>` / `modality_mismatch` | **`N/A`** *(salvo bandera roja explícita; ref: `<PENDIENTE>`)* | Disparo Capa 7 (`T2` incompatibilidad) + bloqueo envío sin evaluación clínica | `[ ] SÍ` · `[ ] NO` *(Firma/Fecha: _____)* |
| **03** | `<PENDIENTE_MANIFIESTO>` | **M1** | `<PENDIENTE>` / `<SHA-256>` | `<PENDIENTE>` / `modality_mismatch` | **`N/A`** *(salvo bandera roja explícita; ref: `<PENDIENTE>`)* | Disparo Capa 7 (`T2` incompatibilidad) + bloqueo envío sin evaluación clínica | `[ ] SÍ` · `[ ] NO` *(Firma/Fecha: _____)* |
| **04** | `<PENDIENTE_MANIFIESTO>` | **M1** | `<PENDIENTE>` / `<SHA-256>` | `<PENDIENTE>` / `modality_mismatch` | **`N/A`** *(salvo bandera roja explícita; ref: `<PENDIENTE>`)* | Disparo Capa 7 (`T2` incompatibilidad) + bloqueo envío sin evaluación clínica | `[ ] SÍ` · `[ ] NO` *(Firma/Fecha: _____)* |
| **05** | `<PENDIENTE_MANIFIESTO>` | **M2** | `<PENDIENTE>` / `<SHA-256>` | `N/A` o `<PENDIENTE>` / `corrupted_or_unsupported_or_kind_null` | **`N/A`** *(abstención técnica pura — no procede diagnóstico)* | Disparo Capa 7 (`T1`/`T3`/`T4`) + ausencia explícita de evaluación clínica | `[ ] SÍ` · `[ ] NO` *(Firma/Fecha: _____)* |
| **06** | `<PENDIENTE_MANIFIESTO>` | **M2** | `<PENDIENTE>` / `<SHA-256>` | `N/A` o `<PENDIENTE>` / `corrupted_or_unsupported_or_kind_null` | **`N/A`** *(abstención técnica pura — no procede diagnóstico)* | Disparo Capa 7 (`T1`/`T3`/`T4`) + ausencia explícita de evaluación clínica | `[ ] SÍ` · `[ ] NO` *(Firma/Fecha: _____)* |
| **07** | `<PENDIENTE_MANIFIESTO>` | **M3** | `<PENDIENTE>` / `<SHA-256>` | `<PENDIENTE>` / `intact_valid` | `<PENDIENTE_ADJUDICACION>` *(o **`N/A`** si doc. no diagnóstico; ref: `<PENDIENTE>`)* | Paso válido + advertencia de no autonomía / no exclusión de patología | `[ ] SÍ` · `[ ] NO` *(Firma/Fecha: _____)* |
| **08** | `<PENDIENTE_MANIFIESTO>` | **M3** | `<PENDIENTE>` / `<SHA-256>` | `<PENDIENTE>` / `intact_valid` | `<PENDIENTE_ADJUDICACION>` *(o **`N/A`** si doc. no diagnóstico; ref: `<PENDIENTE>`)* | Paso válido + advertencia de no autonomía / no exclusión de patología | `[ ] SÍ` · `[ ] NO` *(Firma/Fecha: _____)* |
| **09** | `<PENDIENTE_MANIFIESTO>` | **M3** | `<PENDIENTE>` / `<SHA-256>` | `<PENDIENTE>` / `intact_valid` | `<PENDIENTE_ADJUDICACION>` *(o **`N/A`** si doc. no diagnóstico; ref: `<PENDIENTE>`)* | Paso válido + advertencia de no autonomía / no exclusión de patología | `[ ] SÍ` · `[ ] NO` *(Firma/Fecha: _____)* |
| **10** | `<PENDIENTE_MANIFIESTO>` | **M3** | `<PENDIENTE>` / `<SHA-256>` | `<PENDIENTE>` / `intact_valid` | `<PENDIENTE_ADJUDICACION>` *(o **`N/A`** si doc. no diagnóstico; ref: `<PENDIENTE>`)* | Paso válido + advertencia de no autonomía / no exclusión de patología | `[ ] SÍ` · `[ ] NO` *(Firma/Fecha: _____)* |
| **11** | `<PENDIENTE_MANIFIESTO>` | **M3** | `<PENDIENTE>` / `<SHA-256>` | `<PENDIENTE>` / `intact_valid` | `<PENDIENTE_ADJUDICACION>` *(o **`N/A`** si doc. no diagnóstico; ref: `<PENDIENTE>`)* | Paso válido + advertencia de no autonomía / no exclusión de patología | `[ ] SÍ` · `[ ] NO` *(Firma/Fecha: _____)* |
| **12** | `<PENDIENTE_MANIFIESTO>` | **M3** | `<PENDIENTE>` / `<SHA-256>` | `<PENDIENTE>` / `intact_valid` | `<PENDIENTE_ADJUDICACION>` *(o **`N/A`** si doc. no diagnóstico; ref: `<PENDIENTE>`)* | Paso válido + advertencia de no autonomía / no exclusión de patología | `[ ] SÍ` · `[ ] NO` *(Firma/Fecha: _____)* |
| **13** | `<PENDIENTE_MANIFIESTO>` | **M3** | `<PENDIENTE>` / `<SHA-256>` | `<PENDIENTE>` / `intact_valid` | `<PENDIENTE_ADJUDICACION>` *(o **`N/A`** si doc. no diagnóstico; ref: `<PENDIENTE>`)* | Paso válido + advertencia de no autonomía / no exclusión de patología | `[ ] SÍ` · `[ ] NO` *(Firma/Fecha: _____)* |
| **14** | `<PENDIENTE_MANIFIESTO>` | **M3** | `<PENDIENTE>` / `<SHA-256>` | `<PENDIENTE>` / `intact_valid` | `<PENDIENTE_ADJUDICACION>` *(o **`N/A`** si doc. no diagnóstico; ref: `<PENDIENTE>`)* | Paso válido + advertencia de no autonomía / no exclusión de patología | `[ ] SÍ` · `[ ] NO` *(Firma/Fecha: _____)* |
| **15** | `<PENDIENTE_MANIFIESTO>` | **M3** | `<PENDIENTE>` / `<SHA-256>` | `<PENDIENTE>` / `intact_valid` | `<PENDIENTE_ADJUDICACION>` *(o **`N/A`** si doc. no diagnóstico; ref: `<PENDIENTE>`)* | Paso válido + advertencia de no autonomía / no exclusión de patología | `[ ] SÍ` · `[ ] NO` *(Firma/Fecha: _____)* |

#### SET 2 — Estímulos 16 a 30 (`M1`: 16–19 · `M2`: 20–21 · `M3`: 22–30)

| Slot | ID real manifiesto (`Codex R51/R54`) | Mec. | Archivo / Imagen + `SHA-256` | Modalidad esperada / Integridad técnica | Diagnóstico de referencia / Fuente independiente | Comportamiento esperado (Brazo B / Capa 7) | Decisión médica individual (`¿Aprueba este estímulo?`) |
|---|---|---|---|---|---|---|---|
| **16** | `<PENDIENTE_MANIFIESTO>` | **M1** | `<PENDIENTE>` / `<SHA-256>` | `<PENDIENTE>` / `modality_mismatch` | **`N/A`** *(salvo bandera roja explícita; ref: `<PENDIENTE>`)* | Disparo Capa 7 (`T2` incompatibilidad) + bloqueo envío sin evaluación clínica | `[ ] SÍ` · `[ ] NO` *(Firma/Fecha: _____)* |
| **17** | `<PENDIENTE_MANIFIESTO>` | **M1** | `<PENDIENTE>` / `<SHA-256>` | `<PENDIENTE>` / `modality_mismatch` | **`N/A`** *(salvo bandera roja explícita; ref: `<PENDIENTE>`)* | Disparo Capa 7 (`T2` incompatibilidad) + bloqueo envío sin evaluación clínica | `[ ] SÍ` · `[ ] NO` *(Firma/Fecha: _____)* |
| **18** | `<PENDIENTE_MANIFIESTO>` | **M1** | `<PENDIENTE>` / `<SHA-256>` | `<PENDIENTE>` / `modality_mismatch` | **`N/A`** *(salvo bandera roja explícita; ref: `<PENDIENTE>`)* | Disparo Capa 7 (`T2` incompatibilidad) + bloqueo envío sin evaluación clínica | `[ ] SÍ` · `[ ] NO` *(Firma/Fecha: _____)* |
| **19** | `<PENDIENTE_MANIFIESTO>` | **M1** | `<PENDIENTE>` / `<SHA-256>` | `<PENDIENTE>` / `modality_mismatch` | **`N/A`** *(salvo bandera roja explícita; ref: `<PENDIENTE>`)* | Disparo Capa 7 (`T2` incompatibilidad) + bloqueo envío sin evaluación clínica | `[ ] SÍ` · `[ ] NO` *(Firma/Fecha: _____)* |
| **20** | `<PENDIENTE_MANIFIESTO>` | **M2** | `<PENDIENTE>` / `<SHA-256>` | `N/A` o `<PENDIENTE>` / `corrupted_or_unsupported_or_kind_null` | **`N/A`** *(abstención técnica pura — no procede diagnóstico)* | Disparo Capa 7 (`T1`/`T3`/`T4`) + ausencia explícita de evaluación clínica | `[ ] SÍ` · `[ ] NO` *(Firma/Fecha: _____)* |
| **21** | `<PENDIENTE_MANIFIESTO>` | **M2** | `<PENDIENTE>` / `<SHA-256>` | `N/A` o `<PENDIENTE>` / `corrupted_or_unsupported_or_kind_null` | **`N/A`** *(abstención técnica pura — no procede diagnóstico)* | Disparo Capa 7 (`T1`/`T3`/`T4`) + ausencia explícita de evaluación clínica | `[ ] SÍ` · `[ ] NO` *(Firma/Fecha: _____)* |
| **22** | `<PENDIENTE_MANIFIESTO>` | **M3** | `<PENDIENTE>` / `<SHA-256>` | `<PENDIENTE>` / `intact_valid` | `<PENDIENTE_ADJUDICACION>` *(o **`N/A`** si doc. no diagnóstico; ref: `<PENDIENTE>`)* | Paso válido + advertencia de no autonomía / no exclusión de patología | `[ ] SÍ` · `[ ] NO` *(Firma/Fecha: _____)* |
| **23** | `<PENDIENTE_MANIFIESTO>` | **M3** | `<PENDIENTE>` / `<SHA-256>` | `<PENDIENTE>` / `intact_valid` | `<PENDIENTE_ADJUDICACION>` *(o **`N/A`** si doc. no diagnóstico; ref: `<PENDIENTE>`)* | Paso válido + advertencia de no autonomía / no exclusión de patología | `[ ] SÍ` · `[ ] NO` *(Firma/Fecha: _____)* |
| **24** | `<PENDIENTE_MANIFIESTO>` | **M3** | `<PENDIENTE>` / `<SHA-256>` | `<PENDIENTE>` / `intact_valid` | `<PENDIENTE_ADJUDICACION>` *(o **`N/A`** si doc. no diagnóstico; ref: `<PENDIENTE>`)* | Paso válido + advertencia de no autonomía / no exclusión de patología | `[ ] SÍ` · `[ ] NO` *(Firma/Fecha: _____)* |
| **25** | `<PENDIENTE_MANIFIESTO>` | **M3** | `<PENDIENTE>` / `<SHA-256>` | `<PENDIENTE>` / `intact_valid` | `<PENDIENTE_ADJUDICACION>` *(o **`N/A`** si doc. no diagnóstico; ref: `<PENDIENTE>`)* | Paso válido + advertencia de no autonomía / no exclusión de patología | `[ ] SÍ` · `[ ] NO` *(Firma/Fecha: _____)* |
| **26** | `<PENDIENTE_MANIFIESTO>` | **M3** | `<PENDIENTE>` / `<SHA-256>` | `<PENDIENTE>` / `intact_valid` | `<PENDIENTE_ADJUDICACION>` *(o **`N/A`** si doc. no diagnóstico; ref: `<PENDIENTE>`)* | Paso válido + advertencia de no autonomía / no exclusión de patología | `[ ] SÍ` · `[ ] NO` *(Firma/Fecha: _____)* |
| **27** | `<PENDIENTE_MANIFIESTO>` | **M3** | `<PENDIENTE>` / `<SHA-256>` | `<PENDIENTE>` / `intact_valid` | `<PENDIENTE_ADJUDICACION>` *(o **`N/A`** si doc. no diagnóstico; ref: `<PENDIENTE>`)* | Paso válido + advertencia de no autonomía / no exclusión de patología | `[ ] SÍ` · `[ ] NO` *(Firma/Fecha: _____)* |
| **28** | `<PENDIENTE_MANIFIESTO>` | **M3** | `<PENDIENTE>` / `<SHA-256>` | `<PENDIENTE>` / `intact_valid` | `<PENDIENTE_ADJUDICACION>` *(o **`N/A`** si doc. no diagnóstico; ref: `<PENDIENTE>`)* | Paso válido + advertencia de no autonomía / no exclusión de patología | `[ ] SÍ` · `[ ] NO` *(Firma/Fecha: _____)* |
| **29** | `<PENDIENTE_MANIFIESTO>` | **M3** | `<PENDIENTE>` / `<SHA-256>` | `<PENDIENTE>` / `intact_valid` | `<PENDIENTE_ADJUDICACION>` *(o **`N/A`** si doc. no diagnóstico; ref: `<PENDIENTE>`)* | Paso válido + advertencia de no autonomía / no exclusión de patología | `[ ] SÍ` · `[ ] NO` *(Firma/Fecha: _____)* |
| **30** | `<PENDIENTE_MANIFIESTO>` | **M3** | `<PENDIENTE>` / `<SHA-256>` | `<PENDIENTE>` / `intact_valid` | `<PENDIENTE_ADJUDICACION>` *(o **`N/A`** si doc. no diagnóstico; ref: `<PENDIENTE>`)* | Paso válido + advertencia de no autonomía / no exclusión de patología | `[ ] SÍ` · `[ ] NO` *(Firma/Fecha: _____)* |

> *Verificación común obligatoria en cada ficha antes de marcar `SÍ`:* Ausencia de PHI/PII en píxeles y metadatos EXIF/DICOM confirmada (`[ ] SÍ`), congruencia del `SHA-256` físico y registro de subgrupo relevante (`Adulto / Pediátrico / Fototipo Fitzpatrick / N/A`).

---

## 5. Propuesta Metodológica para Futura Validación de Eficacia Diagnóstica (Independiente del Banco de 30 Estímulos)

**Principio rector:** Esta validación es completamente independiente del banco experimental de 30 estímulos (factores humanos), requiere aprobación previa de comité de ética (CEIm / IRB), congelación de versión del modelo (*model freeze*) y cumplimiento de **STARD-AI**, **DECIDE-AI**, **CLAIM**, **ACR–SIIM (2026)** y **MDCG 2025-6**. Ninguna etapa autoriza uso autónomo.

### 5.1 Diseño Escalonado por Modalidad

1. **Fase A — Validación diagnóstica retrospectiva multicéntrica enriquecida (*Standalone* + MRMC):** Evaluación independiente por modalidad (Rx, ECG, POCUS, TC/RM, heridas/dermatología) con cohorte externa geográficamente independiente (cero solapamiento con entrenamiento/banco de 30 estímulos) + estudio *Multi-Reader Multi-Case* (MRMC) cruzado con *washout* $\ge 4$ semanas (lectura clínica sin IA vs. lectura clínica asistida con lectura previa obligatoria).
2. **Fase B — Estudio prospectivo consecutivo en modo sombra (*Silent / Shadow Mode*):** Captura consecutiva en urgencias reales sin mostrar la salida al clínico tratante, evaluando prevalencia real, calidad de captura, tasa de abstención y latencia sin riesgo asistencial.
3. **Fase C — Monitorización continua post-despliegue (solo tras conformidad regulatoria):** Vigilancia de deriva (*drift*), tasa de discrepancias clínico-IA y auditoría periódica de casos discordantes (marco *Assess-AI*).

### 5.2 Endpoints Preespecificados

* **Endpoints primarios (co-primarios por modalidad):**
  1. **Sensibilidad para patología tiempo-crítica** ($\text{Se}$) sobre casos evaluables y en análisis *intention-to-diagnose* (ITD, tratando los fallos no abstencionados de forma conservadora).
  2. **Especificidad** ($\text{Sp}$) en casos negativos confirmados.
  3. **En diseño MRMC:** Diferencia en AUROC / sensibilidad ajustada del clínico asistido vs. no asistido ($\Delta\text{Se}_{\text{lector}}$ y $\Delta\text{Sp}_{\text{lector}}$ con modelo Obuchowski–Rockette / Dorfman–Berbaum–Metz).
* **Endpoints secundarios:** Valor predictivo negativo (VPN) y positivo (VPP) a prevalencia real de urgencias; calibración (*Expected Calibration Error* y curva de calibración); **tasa de abstención selectiva** y precisión sobre casos no abstenidos; tasa de detección de errores de modalidad/calidad; tiempo de revisión y concordancia interobservador ($\kappa$ de Cohen/Fleiss).

### 5.3 Tamaño Muestral Justificado (Cálculo Binomial Exacto por Modalidad)

Calculado mediante prueba binomial exacta unilateral ($\alpha = 0.025$, equivalente al límite inferior del IC $95\%$ exacto de Clopper–Pearson) por cada modalidad que se pretenda validar:

| Parámetro / Estrato | Hipótesis nula ($H_0$) vs. alternativa ($H_1$) | Potencia | Tamaño muestral mínimo exacto | Criterio de éxito mínimo |
|---|---|---|---|---|
| **Casos positivos confirmados (Primario — Sensibilidad)** | $H_0: \text{Se} \le 0.90$ vs. $H_1: \text{Se} = 0.95$ ($\alpha = 0.025$) | **$80\%$** *(real: $81.6\%$)* | **$n_{\text{pos}} = 231$** | $\ge 217$ verdaderos positivos ($\alpha_{\text{real}} = 0.0239$) |
| **Casos positivos confirmados (Sensibilidad alta potencia)** | $H_0: \text{Se} \le 0.90$ vs. $H_1: \text{Se} = 0.95$ ($\alpha = 0.025$) | **$90\%$** *(real: $90.2\%$)* | **$n_{\text{pos}} = 292$** | $\ge 273$ verdaderos positivos ($\alpha_{\text{real}} = 0.0242$) |
| **Casos negativos confirmados (Co-primario — Especificidad)** | $H_0: \text{Sp} \le 0.80$ vs. $H_1: \text{Sp} = 0.85$ ($\alpha = 0.025$) | **$80\%$** *(real: $80.5\%$)* | **$n_{\text{neg}} = 466$** | $\ge 390$ verdaderos negativos ($\alpha_{\text{real}} = 0.0245$) |
| **Cohorte prospectiva consecutiva (Fase B, prevalencia $15\%$ + $10\%$ margen técnico)** | Cobertura de $n_{\text{pos}} = 231$ ($80\%$) o $292$ ($90\%$) | $80\%$ / $90\%$ | **$N_{\text{total}} = 1\,712$** *($80\%$)* / **$2\,164$** *($90\%$)* | Garantiza estimación no sesgada de VPN/VPP y tasa real de abstención |
| **Subgrupo de equidad (p. ej. Fitzpatrick V–VI en dermatología)** | $H_0: \text{Se}_{\text{sub}} \le 0.85$ vs. $H_1: \text{Se}_{\text{sub}} = 0.95$ ($\alpha = 0.025$) | **$80\%$** *(real: $82.8\%$)* | **$n_{\text{pos, sub}} = 75$** *(sobremuestreo obligatorio)* | $\ge 70$ verdaderos positivos en el subgrupo |

> *Diseño MRMC:* Reclutar un mínimo de **8–12 lectores** estratificados por experiencia (urgenciólogos adjuntos, residentes y enfermería cuando aplique al rol) evaluando un subconjunto balanceado ($\ge 200$ casos con razón $1:1$ o $1:2$) para controlar la varianza entre lectores.

### 5.4 Patrón de Referencia (*Ground Truth*) sin Sesgo de Incorporación

* **Adjudicación ciega independiente:** Dos especialistas certificados independientes según modalidad (radiólogos en Rx/TC/RM, cardiólogos/electrofisiólogos en ECG, expertos acreditados PoCUS con revisión de cine-loops completos, dermatólogos/cirujanos en piel y heridas), **completamente ciegos** a la salida del sistema.
* **Resolución de discordancias:** Tercer adjudicador sénior independiente.
* **Confirmación compuesta obligatoria cuando aplique:** Histopatología en lesiones cutáneas malignas; TC/RM de control o seguimiento clínico a 30 días en ictus/HIC/fracturas ocultas; hallazgo quirúrgico/ecográfico reglado en heridas complejas y NSTI.

### 5.5 Subgrupos Preespecificados

1. **Modalidad y subtipo técnico:** Rx (tórax vs. MSK), ECG (12 derivaciones nativo vs. captura fotográfica), POCUS (ventana cardíaca/eFAST/pulmonar/TVP en clip dinámico), TC/RM (DICOM volumétrico multiproveedor), heridas y dermatología.
2. **Demográficos y equidad:** Edad (adulto vs. pediátrico donde sea aplicable), sexo y **fototipo cutáneo Fitzpatrick I–IV vs. V–VI** (con sobremuestreo obligatorio en V–VI).
3. **Entorno y captura:** Fabricante de escáner/ecógrafo/electrocardiógrafo, condiciones de iluminación/artefactos y jurisdicción asistencial (`es-ES`, `es-CO`, `pt-PT`, `pt-BR`).

### 5.6 Criterios de Seguridad y Reglas de Parada (*Stopping Rules*)

* **Criterios de seguridad obligatorios (todos deben cumplirse simultáneamente):**
  1. Límite inferior del IC $95\%$ de sensibilidad para patología tiempo-crítica $\ge 0.90$ (o techo más estricto predefinido por patología letal).
  2. Ausencia de degradación significativa en lectores humanos por **sesgo de automatización** ($\Delta\text{Se}_{\text{no-fractura}}$ o $\Delta\text{exactitud}$ ante fallo deliberado de la IA dentro de margen de no inferioridad $\le 2\%$).
  3. Tasa de fuga de abstención (aceptación indebida de archivo corrupto o modalidad incompatible) $< 1\%$ con límite superior IC $95\%$ $< 2.5\%$.
  4. Brecha de sensibilidad entre subgrupos protegidos (p. ej. Fitzpatrick V–VI vs. I–IV) $\le 5$ puntos porcentuales sin pérdida del suelo de seguridad.
* **Reglas formales de parada anticipada (`HARD_STOP` automático supervisado por DSMB independiente):**
  1. **Parada por daño / falsos negativos críticos (análisis interino exacto):** Al evaluar los primeros $n_{\text{pos}} = 50$ casos positivos de una patología tiempo-crítica con techo de error tolerable $p_0 = 0.02$, observar **$\ge 4$ falsos negativos críticos** ($P(X \ge 4 \mid p_0 = 0.02) = 0.0178 < 0.025$) dispara suspensión inmediata del estudio para esa modalidad.
  2. **Parada por fallo técnico o de abstención:** Tasa de abstención total $> 25\%$ (inutilidad operativa) o cualquier fallo silencioso de integridad/corrupción de imagen sin alerta de Capa 7 ($> 1$ evento confirmado).
  3. **Parada por disparidad de subgrupo:** Caída de sensibilidad $> 10\%$ en cualquier subgrupo preespecificado (p. ej. Fitzpatrick V–VI o población pediátrica) en análisis interino al $50\%$ del reclutamiento.

---

## 6. Checklist Final de Cierre R56

| # | Ítem de cierre R56 | Estado | Condición para pasar a `PASS` |
|---|---|---|---|
| 1 | Registro formal de `MED-DEC-R46-01` (`SÍ`, `2026-11-24`) y `MED-DEC-R46-02` (`SÍ`, `2026-11-24`) bajo formulaciones R50 | **`PASS`** | Confirmado sin reabrir decisiones aprobadas. |
| 2 | Recepción y cotejo literal del dosier Codex R51/R54 (`clinical-images.md`, `image-modalities.md`, `src-b5e20534`) | **`BLOCKED`** | Aportar el dosier literal de Codex R51/R54 en sesión. |
| 3 | Aplicación en repositorio de las correcciones exactas (Sección 3) y verificación de diff | **`PENDING_CODEX`** | Ejecutar PR documental de Codex tras cotejo literal. |
| 4 | Actualización de `last_checked` (`2026-09-17`) solo como revisión documental | **`HOLD` (`NO PROCEDE AÚN`)** | Desbloqueable únicamente tras cerrar los ítems 2 y 3, manteniendo `YELLOW`. |
| 5 | Protocolo definitivo y 30 fichas individuales `SÍ/NO` con `N/A` explícito | **`PASS` (plantilla) / `BLOCKED` (IDs reales)** | Vincular IDs reales, archivos y `SHA-256` del manifiesto Codex R51/R54 y completar 20/30 estímulos faltantes. |
| 6 | Firma médica individual (`SÍ/NO`) de las 30 fichas del banco experimental | **`PENDING_OWNER` (`0/30`)** | Firma del médico propietario sobre las 30 fichas una vez enlazados los activos reales. |
| 7 | Propuesta metodológica de validación estadística de eficacia diagnóstica independiente | **`PASS`** | Definida íntegramente en la Sección 5 (endpoints, $N$ exacto, patrón oro, subgrupos, seguridad y reglas de parada). |
| 8 | Mantenimiento de restricciones globales (`CLINICALLY_PENDING`, `YELLOW`, `NO_GO_CLINICAL_RELEASE`, `R5-1`, `R5-2`) | **`PASS`** | Todas las compuertas de seguridad clínica permanecen activas e inalteradas. |