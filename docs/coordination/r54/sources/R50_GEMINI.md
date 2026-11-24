# R50 — Cierre Documental de Auditoría R46

* **Repositorio:** `JuanCopado/Emergency`
* **Prioridad:** P1
* **Corte de verificación primaria:** `2026-11-24`
* **Gobernanza activa (inalterada):** `status: yellow` | `last_checked: 2026-09-17` *(NO renovada)* | `R5-1 ABIERTO` | `R5-2 PENDIENTE` | `CLINICALLY_PENDING` | `NO_GO_CLINICAL_RELEASE`

## 1. Estado de Cotejo Literal del Repositorio (`clinical-images.md`, `image-modalities.md`, `src-b5e20534`)

| Artefacto | Ruta en repositorio | Estado en R50 | Motivo exacto |
|---|---|---|---|
| Reglas generales del módulo | `clinical/modules/clinical-images.md` | **`BLOCKED_NO_REPO_ACCESS` / `NOT_VERIFIED`** | El repositorio `JuanCopado/Emergency` no es accesible públicamente ni desde este entorno de chat; no se han recibido los cuerpos literales. |
| Reglas por modalidad | `clinical/modules/image-modalities.md` | **`BLOCKED_NO_REPO_ACCESS` / `NOT_VERIFIED`** | Mismo bloqueo de acceso; no se reconstruyen ni infieren afirmaciones internas. |
| Entrada de fuente compuesta | `src-b5e20534` (`clinical/references/evidence-sources.json`) | **`BLOCKED_NO_REPO_ACCESS` / `NOT_VERIFIED`** | Identificador opaco sin cuerpo JSON aportado en sesión. |
| Registro de vigencia | `clinical/references/evidence-registry.json` | **Metadatos conservados (`last_checked: 2026-09-17`)** | **Prohibido renovar `last_checked`** ni cerrar `R5-1`/`R5-2` hasta cotejar los tres cuerpos literales anteriores. |

## 2. Verificación Directa en Fuentes Primarias (Correcciones Exactas sobre R46)

Todas las referencias de R46 han sido contrastadas directamente contra sus publicaciones y registros oficiales (PubMed, PMC, NICE, FDA, EUR-Lex, CDC, ACR). Se registran explícitamente las **correcciones de fechas, DOIs, identificadores y alcance** detectadas:

| Referencia | Identificador / DOI / Fecha verificada en fuente primaria | Corrección respecto a R46 | Aplicabilidad exacta (sin extrapolación) |
|---|---|---|---|
| **WSES / AcEMC Heridas traumáticas** | Prevaldi C et al. *World J Emerg Surg.* **18 jun 2016**;11:30. **DOI:** `10.1186/s13017-016-0084-3` · **PMID:** `27330546` · **PMCID:** `PMC4912791` | Añade coautoría AcEMC, DOI y PMID exactos omitidos en R46. | Consenso Delphi internacional sobre heridas traumáticas en urgencias (riesgo infeccioso, cuerpo extraño, exploración de mano, tétanos/rabia). |
| **WSES/GAIS/WSIS/SIS-E/AAST SSTI** | Sartelli M et al. *World J Emerg Surg.* **15 ene 2022**;17(1):3. **DOI:** `10.1186/s13017-022-00406-2` · **PMID:** `35033131` | Añade fecha exacta, DOI y PMID. | Rutas clínicas globales para infecciones de piel y partes blandas (drenaje de absceso, identificación precoz de NSTI). |
| **IDSA SSTI Guidelines** | Stevens DL et al. *Clin Infect Dis.* **15 jul 2014**;59(2):e10–e52 (resumen 147–159). **DOI:** `10.1093/cid/ciu296` · **PMID:** `24947530` | Confirmada vigencia de la actualización 2014 (antigüedad $> 12$ años; complementar siempre con WSES 2022 y guías locales). | Clasificación purulenta vs. no purulenta y gravedad clínica; **no** sustituye antibiogramas locales. |
| **CDC Profilaxis antitetánica** | *Clinical Guidance for Wound Management to Prevent Tetanus* (`cdc.gov/tetanus/hcp/clinical-guidance/index.html`). **Actualizada: 8 sep 2026** *(publicación previa: 15 may 2024)* | **Fecha corregida:** R46 citaba `15 may 2024`; la página oficial CDC muestra revisión **`8 sep 2026`**. | Heridas limpias vs. sucias/desvitalizadas, indicación de vacuna y TIG 250 UI IM; **desaconseja antibióticos** como profilaxis antitetánica. |
| **NICE HTG739** *(antes HTE20)* | *AI technologies to help detect fractures on X-rays in urgent care: EVA.* **Pub: 14 ene 2025 · Actual: 23 oct 2026** (periodo de generación de evidencia extendido) | **Alcance pediátrico corregido:** R46 generalizó exclusión pediátrica. Rec. 1.1 autoriza `Rayvolve` y `TechCare Alert` **para cualquier edad**, y `BoneView` y `RBfracture` **desde los 2 años**, solo bajo EVA NHS + DTAC. | Apoyo adjunto en fracturas en urgencias NHS; **no sustituye la lectura radiológica definitiva**. No extrapolable a otras herramientas ni a patología no fracturaria. |
| **NICE HTG696** *(antes HTE12)* | *AI-derived software to analyse chest X-rays for suspected lung cancer in primary care referrals: EVA.* **Pub: 28 sep 2023 · Actual: 10 feb 2025** | Aclaración de ámbito: migrada desde HTE12; *Red dot* retirada por falta de disponibilidad en RU. | **Exclusivamente derivaciones de atención primaria por sospecha de cáncer pulmonar.** **No aplicable** a Rx de tórax urgente aguda (neumotórax, edema, neumonía). |
| **AHA/ASA Ictus Isquémico Agudo 2026** | Prabhakaran S, Gonzalez NR, Zachrison KS et al. *Stroke.* **ago 2026**;57(8):e316–e436 (**Epub: 26 ene 2026**). **DOI:** `10.1161/STR.0000000000000513` · **PMID:** `41582814` | Confirmados volumen, páginas, Epub y PMID. Actualiza 2018/2019 e incorpora primeras recomendaciones pediátricas. | Selección multimodal de reperfusión en ictus isquémico agudo. **No fija un umbral universal de HIC $< 1.5\text{ mL}$** para software de IA. |
| **NICE HTG708** *(antes DG57)* | *AI-derived software to help clinical decision making in stroke.* **Pub: 23 ene 2024 · Actual: 2 may 2024** | Migrada de DG57; incluye Viz en Rec. 1.1. **Se elimina el umbral $< 1.5\text{ mL}$** atribuido indebidamente en R46. | Plataformas CE específicas de triaje/apoyo en TC/CTA/CTP de ictus; apoyo al especialista, nunca informe autónomo. |
| **ACEP Ultrasound Guidelines** | ACEP. *Ann Emerg Med.* **sep 2023**;82(3):e115–e155. **DOI:** `10.1016/j.annemergmed.2023.06.005` | **Fecha corregida:** Se elimina la fecha no verificada `26 ene 2026` citada en R46; la publicación primaria revisada por pares es `Ann Emerg Med. 2023`. | Marco de práctica, gobernanza y QA de ecografía clínica de urgencias. |
| **IFEM PoCUS Curriculum** | IFEM. *Point-of-Care Ultrasound Curriculum Guidelines.* **Pub: 23 nov 2021** (`ifem.cc/point_of_care_ultrasound_curriculum_guidelines`) | Verificada fecha exacta y filosofía clínica explícita (*rule-in philosophy*). | PoCUS focal suele tener mayor especificidad que sensibilidad (**regla *rule-in***): orienta confirmación, pero a menudo no permite descartar patología. |
| **AHA AI en Cardiología (ECG)** | Armoundas AA et al. *Circulation.* **2 abr 2024**;149(14):e1028–e1050 (Epub `28 feb 2024`). **DOI:** `10.1161/CIR.0000000000001201` · **PMID:** `38415358` | Confirmados PMID y fechas exactas. | La IA aumenta la decisión médica; faltan ECA centrados en desenlaces clínicos y validación externa. |
| **EHRA/HRS/ESC AI en Electrofisiología** | Svennberg E et al. *Europace.* **7 may 2025**;27(5):euaf071. **DOI:** `10.1093/europace/euaf071` · **PMID:** `40163651` | Añade artículo `euaf071`, DOI y PMID exactos. | Checklist EHRA de reporte, reproducibilidad y validación de IA en electrofisiología/ECG. |
| **NICE HTG746** *(antes HTE24)* | *AI technologies for assessing and triaging skin lesions referred to the urgent suspected skin cancer pathway: EVA.* **Pub: 1 may 2025 · Actual: 17 mar 2026** | **Ámbito acotado:** Aplica específicamente a **DERM (Skin Analytics, CE Clase III)** en teledermatología NHS en **adultos $\ge 18$ años** en vía urgente de sospecha de cáncer cutáneo. | Rec. 1.2 exige revisión por profesional sanitario en piel negra o morena (**Fitzpatrick V–VI**) **durante los 3 años de EVA de DERM** por evidencia insuficiente en esos fototipos. |
| **AAD Position Statement AuI** | AAD. *Position Statement on Augmented Intelligence (AuI)* (**2019**; comentario Kovarik et al., *JAAD* 2019) | **Fecha corregida:** Se elimina la mención no verificada `"vigente 2024–2027"` de R46. | Posicionamiento de inteligencia aumentada, validación independiente y equidad. |
| **ACR–SIIM Practice Parameter AI** | *ACR–SIIM Practice Parameter for Imaging Artificial Intelligence (AI).* **Aprobado: 5 may 2026** (ACR `DocId=217`) + marco *JACR Assess-AI* (**5 may 2026**) | Confirmados directamente en portal ACR. | Exige gobernanza, pruebas locales de aceptación con datos multiproveedor, estratificación pediátrica, monitorización de deriva y reglas de parada. |
| **Reglamento (UE) 2026/1744 (*Digital Omnibus on AI*)** | Modifica Reg. (UE) 2024/1689, 2018/1139 y 2023/1230. **DOUE: 24 jul 2026 · Vigor: 27 jul 2026** (`CELEX:32026R1744`, `ELI: .../reg/2026/1744/oj`) | **Precisión confirmada:** Art. 50(1) vigente desde `2 ago 2026`; Art. 50(2) (marcado de contenido generado por proveedores) aplazado al **`2 dic 2026`**; Anexo III al `2 dic 2027`; Anexo I (MDR/IVDR) al `2 ago 2028`. No modifica MDR/IVDR. | Marco vinculante europeo para MDAI. |
| **MDCG 2025-6 / AIB 2025-1** | *Interplay between MDR/IVDR and the AI Act.* **Pub: 19 jun 2025** (`mdcg_2025-6_en.pdf`) | **Fecha corregida:** R40/R46 indicaban `26 jun 2025`; la fecha real de publicación es **`19 jun 2025`**. | Guía conjunta (no vinculante) sobre expediente integrado MDR/IVDR + AI Act y supervisión humana efectiva. |
| **FDA CDS Final Guidance** | *Clinical Decision Support Software.* **Ene 2026** (vigente `29 ene 2026`; Docket `FDA-2017-D-6569`; CDRH Town Hall `11 mar 2026`) | Confirmado directamente en FDA. | El software que adquiere, procesa o analiza imágenes médicas o señales incumple el Criterio 1 (*device software function*). |
| **INVIMA Colombia / ANVISA Brasil** | **INVIMA:** Decreto 4725 (**26 dic 2005**, mod. Decreto 582 de 2017, Art. 30). **ANVISA:** **RDC nº 657, de 24 mar 2022** (DOU `30 mar 2022`, vigor `1 jul 2022`). | Añadidas fechas oficiales exactas de publicación y entrada en vigor. | Regulación local de dispositivos médicos y SaMD en Colombia y Brasil. |

## 3. Corrección de Epidemiología Antimicrobiana por País (Eliminación de Generalizaciones de R46)

Las afirmaciones comparativas de R46 sobre CA-MRSA por país (*"tasas bajas en España/Portugal vs. alta circulación en Colombia y presencia relevante en centros urbanos de Brasil"*) **se eliminan por carecer de respaldo homogéneo en heridas ambulatorias de urgencias**:

1. **Incompatibilidad de fuentes de vigilancia:** El informe **ECDC EARS-Net AER 2025** (publicado el **18 nov 2026**) vigila aislamientos invasivos (hemocultivos/LCR), **no** infecciones de piel y partes blandas (SSTI) comunitarias de urgencias. Además, revisiones recientes (*JAC-Antimicrobial Resistance*, **30 jul 2026**, `dlag152`) señalan que en cohortes pediátricas españolas de infecciones cutáneas por SARM más del $70\%$ portaban PVL, lo que invalida generalizaciones simplistas para España.
2. **Heterogeneidad extrema en Latinoamérica:** La revisión sistemática de CG-MRSA en CO-SSTI en Latinoamérica (`PMC9392117`) documenta rangos de $0\%$ a $88\%$ según país y cohorte; específicamente, **Brasil presentó una de las tasas más bajas publicadas en la región ($4.5\%$–$25\%$)**, contradiciendo la generalización previa de R46. Aunque en Colombia se han descrito tasas elevadas de SARM asociadas al clon USA300-LV en bacteriemias/estudios locales (*JAC-AMR* 2026), los datos de bacteriemia no se extrapolan automáticamente a heridas ambulatorias no seleccionadas.
3. **Regla normativa corregida (sin generalización):** La epidemiología de SSTI varía sustancialmente según hospital, edad, comorbilidad y perfil local de resistencias. El módulo de imágenes **no emitirá recomendaciones de antibioterapia empírica ni esquemas vacunales** y remitirá siempre a las guías locales/institucionales y antibiogramas vigentes.

## 4. Refinamiento de Restricciones Clínicas (Sin Extrapolaciones Injustificadas)

| Área | Extrapolación corregida de R46 | Formulación precisa respaldada por evidencia primaria |
|---|---|---|
| **POCUS estático** | Se matiza la prohibición absoluta sobre cualquier imagen estática (en práctica clínica las capturas fijas se archivan válidamente para QA y ciertos hallazgos *rule-in* documentados). | Según **ACEP (2023)** e **IFEM (2021)**, PoCUS opera bajo una **filosofía *rule-in*** integrada en la exploración dinámica a pie de cama: **una captura estática aislada sin adquisición en tiempo real, ventanas completas ni correlación clínica no permite descartar patología aguda** ni sustituye un examen PoCUS completo. |
| **Neuroimagen DICOM (TC/RM)** | **Eliminado el umbral numérico $< 1.5\text{ mL}$** atribuido indebidamente a AHA/ASA 2026 y NICE HTG708 (no es un corte universal de guía). | Según **AHA/ASA (2026)**, **NICE HTG708** y **ACR–SIIM (2026)**, la valoración de neuroimagen urgente exige **series volumétricas DICOM íntegras y lectura especialista**; un corte aislado, captura de pantalla comprimida o serie incompleta no excluye hemorragia intracraneal ni isquemia aguda. El software de IA en ictus solo aplica como apoyo/triaje para productos específicamente validados. |
| **Fototipos Fitzpatrick V–VI** | Se evita extrapolar **NICE HTG746** (evaluación EVA específica para **DERM** en vía urgente de sospecha de cáncer cutáneo en adultos $\ge 18$ años en el NHS) como contraindicación universal de cualquier software dermatológico. | La precisión diagnóstica de modelos de IA en piel negra o morena (**Fitzpatrick V–VI**) **no puede asumirse sin validación estratificada propia**; ante la brecha de evidencia documentada (NICE HTG746 Rec. 1.2; AAD AuI), ninguna salida de IA en lesiones cutáneas en estos fototipos sustituye la revisión clínica directa y debe garantizarse diversidad de fototipos en futuras validaciones clínicas. |

## 5. Distinción Crítica: Banco Experimental de 30 Estímulos vs. Validación Estadística de Eficacia Diagnóstica

| Dimensión | Banco experimental de 30 estímulos (PR89 / PR96) | Validación estadística de eficacia diagnóstica (requisito SaMD / `GREEN` clínico) |
|---|---|---|
| **Objetivo científico** | Evaluar **factores humanos, usabilidad, seguridad de abstención (Capa 7) y telemetría** en diseño cruzado (`S1a–S4b`: $2\text{ sets} \times 15\text{ estímulos}$; $\text{M1}=4$, $\text{M2}=2$, $\text{M3}=9$ por periodo). | Estimar con precisión estadística **sensibilidad, especificidad, VPN/VPP, calibración y seguridad diagnóstica** frente a patrón oro clínico. |
| **Tamaño muestral y potencia** | $N = 30$ estímulos (fijos, sintéticos/curados; 4 estímulos M2 ni siquiera admiten diagnóstico). **Sin potencia estadística** para métricas de precisión diagnóstica por patología o subgrupo. | Requiere cálculo muestral prospectivo por modalidad/patología, prevalencia representativa, variabilidad de equipos/centros y análisis por subgrupos (edad, fototipo) según **ACR–SIIM (2026)** y **MDCG 2025-6**. |
| **Impacto en gobernanza** | Su adjudicación completa ($30/30$) habilita únicamente la **preparación del laboratorio de factores humanos**. | **Imprescindible** para superar `diagnostic performance not established`. Adjudicar $30/30$ estímulos **NO valida eficacia diagnóstica ni autoriza `GO_RELEASE`**. |

## 6. Estado de las Decisiones Médicas `MED-DEC-R46-01` y `MED-DEC-R46-02`

* **`MED-DEC-R46-01` (Salvaguardas clínicas en `clinical-images.md` / `image-modalities.md`):** **`PENDING_OWNER_APPROVAL` — NO INCORPORADA.** No consta aprobación formal firmada (`SÍ`) en el expediente. Además, su texto queda actualizado con las precisiones de la Sección 4 de R50 (sin umbral $< 1.5\text{ mL}$, con precisión *rule-in* en PoCUS y alcance exacto de Fitzpatrick V–VI) antes de someterla a firma cuando se cotejen los archivos `.md` reales.
* **`MED-DEC-R46-02` (Rúbrica de adjudicación del banco de 30 estímulos):** **`PENDING_OWNER_APPROVAL` — NO INCORPORADA.** Actualizada en la Sección 7 de R50 para distinguir expresamente `N/A` en estímulos sin adjudicación diagnóstica y separar banco experimental de validación de eficacia diagnóstica.
* **Decisiones ya aprobadas (NO se vuelven a solicitar):** `DEC-CLIN-R15-01` (`pt-PT`) y `PTBR-MOD` (R39).

## 7. Criterios de Referencia por Estímulo (`N/A` Explícito) y Fichas Individuales de Adjudicación

### 7.1 Regla de Adjudicación por Mecanismo (Banco de 30 Estímulos: Set 1 = 15, Set 2 = 15)

| Mecanismo | Conteo en banco (Set 1 + Set 2) | ¿Requiere verdad de modalidad (`expected_modality`)? | ¿Requiere adjudicación diagnóstica clínica (`clinical_ground_truth`)? | Criterio obligatorio de aprobación por el médico propietario |
|---|---|---|---|---|
| **M1** *(Adversarial / incompatibilidad de modalidad)* | **8** *(4 en Set 1 + 4 en Set 2)* | **SÍ** *(obligatorio verificar modalidad real vs. declarada errónea)* | **`N/A`** *(salvo que el escenario incluya explícitamente una bandera roja clínica a preservar)* | Confirmar modalidad real, ausencia de PHI/PII y que el desajuste adversarial es inequívoco. |
| **M2** *(Abstención técnica / Capa 7: corrupto, `kind=null`, formato no admitido)* | **4** *(2 en Set 1 + 2 en Set 2)* | **SÍ** *(o `N/A` si es archivo corrupto/`kind=null` sin modalidad recuperable)* | **`N/A`** *(prohibido adjudicar diagnóstico sobre archivo corrupto o no procesable)* | Confirmar defecto técnico real, código de disparo Capa 7 esperado (`T1–T4`) y ausencia de PHI/PII. |
| **M3** *(Flujo válido estándar)* | **18** *(9 en Set 1 + 9 en Set 2)* | **SÍ** *(coincidencia exacta con modalidad declarada)* | **SÍ** para imágenes clínicas (Rx, ECG, POCUS, TC/RM, herida/dermatología); **`N/A`** para documentos administrativos/técnicos no diagnósticos | Confirmar calidad técnica suficiente, verdad diagnóstica / hallazgos críticos (si aplica), ausencia de PHI/PII y metadatos de subgrupo (edad/fototipo si procede). |

### 7.2 Plantilla de Ficha Individual de Adjudicación (`STIM-01` a `STIM-30`)

> *Sin adjudicaciones prellenadas en nombre del médico. Inventario actual sin alterar: $10/30$ presentes en PR89 ($20/30$ pendientes de incorporación física).*

> **FICHA DE ADJUDICACIÓN — `[STIM-XX]`**
> * **Set / Mecanismo / Inventario:** `Set 1 | Set 2` · `M1 | M2 | M3` · `En PR89 | Pendiente incorporación`
> * **Archivo y huella criptográfica:** `<ruta_archivo>` · `stimulus_hash_sha256: <PENDIENTE>`
> * **Ausencia de PHI/PII verificada (metadatos EXIF/DICOM y píxeles):** `[ ] SÍ` · `[ ] NO`
> * **Dominio y `expected_modality`:** `<rx | ecg | pocus | ct_mri | wound | dermatology | document | N/A>`
> * **Integridad técnica:** `intact_valid | corrupted_unreadable | unsupported_format | kind_null | modality_mismatch`
> * **Adjudicación diagnóstica (`clinical_ground_truth`):** `<Diagnóstico de referencia + red flags>` *(o marcar **`N/A`** en todos los M2, M1 sin objetivo diagnóstico y M3 documentales)*
> * **Subgrupo relevante (si aplica):** `<Adulto / Pediátrico / Fototipo Fitzpatrick / N/A>`
> * **Comportamiento normativo esperado (Brazo B):** `<Paso válido | Abstención Capa 7 (T1/T2/T3/T4)>`
> * **Dictamen del médico propietario:** `[ ] ADJUDICATED_APPROVED` · `[ ] REJECTED_REPLACE`
> * **Firma / Fecha:** `PENDIENTE`

### 7.3 Matriz de Seguimiento de las 30 Fichas Individuales

| Ficha | Set | Mecanismo | Adjudicación diagnóstica aplicable | Estado de incorporación / adjudicación |
|---|---|---|---|---|
| `STIM-01` a `STIM-04` | Set 1 | **M1** (4) | `N/A` *(verificar `expected_modality` + desajuste)* | `0/4 adjudicadas` *(verificar vínculo con 10/30 de PR89)* |
| `STIM-05` a `STIM-06` | Set 1 | **M2** (2) | **`N/A`** *(abstención técnica pura)* | `0/2 adjudicadas` |
| `STIM-07` a `STIM-15` | Set 1 | **M3** (9) | **SÍ** (imágenes clínicas) / **`N/A`** (docs no diagnósticos) | `0/9 adjudicadas` |
| `STIM-16` a `STIM-19` | Set 2 | **M1** (4) | `N/A` *(verificar `expected_modality` + desajuste)* | `0/4 adjudicadas` |
| `STIM-20` a `STIM-21` | Set 2 | **M2** (2) | **`N/A`** *(abstención técnica pura)* | `0/2 adjudicadas` |
| `STIM-22` a `STIM-30` | Set 2 | **M3** (9) | **SÍ** (imágenes clínicas) / **`N/A`** (docs no diagnósticos) | `0/9 adjudicadas` |

## 8. Checklist Final R50 y Discrepancias Pendientes

### 8.1 Checklist Final de Cierre Documental

| \# | Requisito R50 | Estado | Verificación |
|---|---|---|---|
| 1 | Cotejo literal de `clinical-images.md`, `image-modalities.md` y `src-b5e20534` | **`BLOCKED`** | Sin acceso al repositorio en esta sesión (`NOT_VERIFIED`). |
| 2 | Verificación en fuentes primarias de fechas, DOIs, identificadores y aplicabilidad de R46 | **`PASS`** | 19 fuentes verificadas; corregidas 6 imprecisiones de R46 (CDC `8 sep 2026`, ACEP `2023`, MDCG `19 jun 2025`, AAD `2019`, NICE HTG739 pediatría, NICE HTG696 ámbito AP). |
| 3 | Eliminación de generalizaciones sobre epidemiología antimicrobiana por país | **`PASS`** | Eliminadas generalizaciones sobre España/Portugal/Colombia/Brasil; reemplazada por remisión a guías/antibiogramas locales. |
| 4 | Refinamiento sin extrapolaciones de POCUS estático, DICOM y Fitzpatrick V–VI | **`PASS`** | Eliminado umbral $< 1.5\text{ mL}$; acotado PoCUS (*rule-in*) y ámbito exacto de NICE HTG746 (DERM / NHS). |
| 5 | Separación explícita entre banco de 30 estímulos y validación de eficacia diagnóstica | **`PASS`** | Documentada en Sección 5. |
| 6 | Control de incorporación de `MED-DEC-R46-01` y `MED-DEC-R46-02` | **`PASS`** | Mantenidas como `PENDING_OWNER_APPROVAL` (NO incorporadas). |
| 7 | Criterios de referencia (`N/A` explícito) y fichas individuales para los 30 estímulos | **`PASS`** | Entregados en Sección 7 (`0/30` adjudicadas por IA). |
| 8 | Protección de decisiones ya aprobadas (`DEC-CLIN-R15-01`, `PTBR-MOD`) | **`PASS`** | Conservadas sin solicitar nueva firma. |
| 9 | Integridad de compuertas (`last_checked`, `YELLOW`, `R5-1`, `R5-2`, `CLINICALLY_PENDING`) | **`PASS`** | `last_checked=2026-09-17` sin renovar; `YELLOW`, `R5-1`, `R5-2`, `CLINICALLY_PENDING` y `NO_GO_CLINICAL_RELEASE` intactos. |

### 8.2 Discrepancias Pendientes (Bloqueos Reales para Cierre Definitivo)

1. **Bloqueo técnico (acceso a repositorio):** Aportar el texto literal de `clinical/modules/clinical-images.md`, `clinical/modules/image-modalities.md` y la entrada `src-b5e20534` de `clinical/references/evidence-sources.json` para completar el cruce $1:1$ antes de renovar `last_checked` (`2026-09-17`).
2. **Bloqueo de aprobación médica (`MED-DEC-R46-01` y `MED-DEC-R46-02`):** Pendientes de revisión y firma `SÍ/NO` del médico propietario con las precisiones metodológicas de R50.
3. **Bloqueo de inventario y adjudicación:** Completar los 20 estímulos faltantes del banco ($10/30$ actuales en PR89) y ejecutar la firma médica de las 30 fichas individuales (`STIM-01` a `STIM-30`).
4. **Bloqueo de promoción a `GREEN` / `GO_RELEASE`:** El cierre del banco de 30 estímulos **no** sustituye la validación estadística de eficacia diagnóstica; `diagnostic performance not established`, `R5-1`, `R5-2`, `CLINICALLY_PENDING` y `NO_GO_CLINICAL_RELEASE` permanecen activos.