# EMERGENCY — CONTRATO 4/19: CONCILIACIÓN DE ANAFILAXIA REFRACTARIA

**Fecha:** 2026-11-16  
**ID canónico:** `anaphylaxis-refractory`  
**Versión de referencia:** snapshot `761f42d9afc8a7b7202d18bb0fd506d721dd4e50`.  
**Ámbito ejecutable original:** población adulta, vía IV, soporte experto. No extender automáticamente a pediatría, aunque RCUK incluya adultos y niños.  
**Estado:** `BLOCKED / CLINICAL_REVIEW_REQUIRED`; `CLINICALLY_PENDING` global. **Este expediente NO autoriza la perfusión ni habilita prescripción, mL/h o dosis de bolo en la API.**

## 1. Conciliación con el contrato canónico

La fuente de contratos `clinical/scripts/acute_medication_contracts.py` registra:

> Activar soporte experto, monitorización y protocolo de perfusión IV. No hay preparación/velocidad IV local verificada; evitar bolos IV no monitorizados.

`clinical/qa/V1.44_MEDICATION_PRODUCT_PROTOCOL_RECONCILIATION.json` identifica bloqueo por categorías **A** (producto local), **C** (dilución/estabilidad), **D** (administración) y **G** (protocolo/evidencia local). El producto `ADRENALINE_BASI_1` y preparado `PREP_ADRENALINE_REFRACTORY` permanecen propuestas y no están habilitados.

**No se cambia ningún fichero canónico, campo `block_reason`, `runtime_enabled`, concentración ni dosis de producción.**

## 2. Evidencia clínica y decisión de referencia existente

| Tema | Criterio / fuente | Estado de conciliación |
|---|---|---|
| Definición operativa | Compromiso persistente de vía aérea, respiración o circulación después de **dos dosis apropiadas de adrenalina IM**, conforme a RCUK 2021 y ASCIA 2026 | **Evidencia confirmada**, no equivale a orden IV automática |
| Escalada | Reanimación/UCI/experto, acceso periférico dedicado o IO, cristaloides según evaluación, oxigenación y evaluación continua | **Ruta de referencia documentada**, dotación local no certificada |
| Preparación | **1 mg de adrenalina hasta 100 mL FINALES de NaCl 0,9 %** = **10 microgramos/mL** | **Referencia previamente aceptada por propietario 2026-11-13**, no aprobada galénica/producto/estabilidad por Farmacia |
| Velocidad de referencia | RCUK **0,5–1 mL/kg/h**, titulación según respuesta; con 10 microgramos/mL corresponde nominalmente a **0,083–0,167 microgramos/kg/min** | Fuente corroborada; **NO GENERAR mL/h para pacientes** hasta release |
| Comparación | ERC 2025 indica referencia de inicio de **0,1 microgramos/kg/min** en áreas monitorizadas por personal entrenado | Compatible en orden de magnitud con 10 microgramos/mL, pero no autoriza intercambiar algoritmos automáticamente |
| Infusión y monitorización | Bomba, vía exclusiva, no hacer piggy-back sin dispositivo anti-reflujo; evitar brazo del manguito de PA; ECG/SpO2 continuos y PA **al menos cada 5 min**, inspección de extravasación y titulación por especialista | Requisitos de aceptación operacional |
| Retraso en preparación | Continuar dosis IM según protocolo mientras se establece perfusión, **sin esperar a que el software esté disponible** | Atención urgente independiente de la API |
| Bolo IV | **No utilizar de manera automática** como sustituto de perfusión; reanimación en parada o peri-parada especializada posee circuitos distintos | Bloqueo de conversión entre indicaciones |
| Desescalada | Descenso progresivo según respuesta bajo supervisión y monitorización; documentar protocolo de retirada y vigilancia | Falta protocolo local aprobado para motor automático |

**Fuentes principales verificadas:**
1. [RCUK Emergency treatment of anaphylaxis, guía completa mayo 2021, secciones 6.5–6.6](https://www.resus.org.uk/sites/default/files/2021-05/Emergency%20Treatment%20of%20Anaphylaxis%20May%202021_0.pdf). Página 36 (algoritmo) y página 37 (preparación, inicio, titulación y retirada). La página oficial de RCUK continúa describiendo la edición de 2021 como la guía **completa** más reciente: [índice oficial](https://www.resus.org.uk/library/additional-guidance/guidance-anaphylaxis/emergency-treatment-anaphylactic-reactions).
2. [ERC Guidelines 2025 — Special Circumstances](https://www.erc.edu/media/wwufbysp/gl2025-06-spec-circ-e.pdf), apartado anaphylaxis.
3. [ASCIA Guidelines — Acute Management of Anaphylaxis, 2026, página 5](https://www.allergy.org.au/images/ASCIA_HP_Guidelines_Acute_Management_Anaphylaxis_2026.pdf): después de dos dosis IM, infusión con 1 mg en 100 mL NaCl 0,9 %; inicio 0,5 mL/kg/h, titulación y acceso dedicado.
4. **Fuente aportada por el propietario:** `ANAFILAXIA.pdf` (255 páginas), compendio `compendio_cl_nico_diagn_stico_manejo_de_emergencia_y_prevenci_n_de_la_anafilaxia.md`, Topic 392 v74.0, apartado de perfusiones IV. Describe alternativas adultas de **1 microgramo/mL** y **4 microgramos/mL** y concentración pediátrica de 10 microgramos/mL, además de una definición de refractaria que menciona >=3 dosis IM; estas alternativas **no sustituyen la pauta RCUK ya aceptada**, ni deben mezclarse con la fórmula de bomba. Tiene artefactos de OCR/traducción reconocidos por el propio compendio; no importarlo íntegramente.
5. [Laboratórios Basi, catálogo oficial de productos Portugal 2025](https://www.basi.pt/wp-content/uploads/2025/09/PT_EN_2.pdf): **Adrenalina Basi 1 mg/mL**, ampollas de 1 mL, indicada para anafilaxia/reanimación. La presentación portuguesa existe en documentación de fabricante, pero **no está verificada como stock de Hospital da Horta**, ni constituye certificación de que 1 mg/100 mL tenga estabilidad o compatibilidad validada por el fabricante en el hospital.

## 3. ERROR CRÍTICO DE CONCENTRACIONES: PROHIBIR CRUCE IV

| Identificador candidato de solución | Concentración real NOMINAL | Contexto | Decisión del contrato 4 |
|---|---:|---|---|
| `REFRACTORY_INFUSION_1MG_100ML_FINAL` | **10 microgramos/mL** | Referencia IV con bomba para anafilaxia refractaria | **SOLO REFERENCIA**, pendiente de producto y estabilidad |
| `IV_SMALL_VOLUME_1MG_10ML_FINAL` | **100 microgramos/mL** | Preparación IV de 1 mg en 10 mL finales comunicada por el propietario al revisar contrato 3 | **NUNCA reutilizar con las tasas del contrato 4** |
| `IM_ANAPHYLAXIS_1MG_ML` | **1.000 microgramos/mL** | Adrenalina IM sin diluir de contratos 3 y otros | **NO VÁLIDA para administración IV sin dilución** |
| `OTHER_RESEARCH_CONCENTRATION` | 1 o 4 microgramos/mL, etc. | Alternativas del compendio aportado | No usar sin seleccionar explícitamente protocolo compatible |

**Factor de riesgo:** sustituir 10 por 100 microgramos/mL con la misma tasa de bomba multiplica la dosis por **10**. Sustituir 10 por 1.000 microgramos/mL la multiplica por **100**. Los contratos, UI, etiquetas, impresos y exportaciones tienen que identificar ruta, indicación, concentración, preparador y protocolo.

**Volumen final y sobrellenado:** RCUK/ASCIA usan lenguaje tipo «1 mg en 100 mL de NaCl 0,9 %». El módulo de Emergency registra decisión del propietario de **100 mL FINALES**. La Farmacia debe acreditar método de preparación, gestión de sobrellenado y volumen real; **no convertir silenciosamente «añadir 1 mL a bolsa de 100 mL» en «100 mL finales»**. Hasta conciliar volumen real y estabilidad, no generar mL/h.

## 4. Producto y estabilidad: límites conocidos y evidencias faltantes

**Categoría A:** demostrar qué producto de adrenalina 1 mg/mL, fabricante, RCM portugués, equivalencia sal/base y presentación se utilizan de verdad. BD/RCM español previo no acredita el almacén de Horta; catálogo Basi Portugal es referencia candidata.

**Categoría C:** aprobación galénica nominal para concentración preparada de **10 microgramos/mL**, diluyente NaCl 0,9 %, contenedor/material, mezcla y conservación (luz, temperatura), tiempo desde preparación, límite de uso y sustitución; no inferir vida útil de la ampolla cerrada para la mezcla diluida. Producto `PREP_ADRENALINE_REFRACTORY` en el registro tiene estabilidad `null`.

**Categoría D:** bomba controlada, vía dedicada, cebado/volumen residual, método de etiquetado y comprobación independiente, monitorización ECG/SpO2/PA, detección de extravasación, responsable de titulación y criterios STOP documentados.

**Categoría G:** registrar versión de protocolo, autoridad clínica y Farmacia, autorizaciones nominales fechadas; asegurarse de que la decisión de seguir RCUK para la fase «tras dos dosis IM» está reconocida separadamente del compendio que usa >=3 para su clasificación descriptiva.

## 5. Casos negativos y matriz QA propuesta (NOT_RUN)

Se propone probar en árbol de integración, sin pacientes reales, que:
- Rechaza 1 mg/10 mL IV (100 microgramos/mL) en un formulario de bomba diseñado para 10 microgramos/mL.
- Rechaza ampolla IM sin diluir 1 mg/mL como solución de bomba.
- Rechaza error de unidades mg/microgramos y concentración ×10/×100.
- Rechaza NaCl distinto de 0,9 %, volumen final no definido, sobrellenado no reconciliado y estabilidad/fecha de preparación ausentes.
- Rechaza producto no identificado, envase incompatible y tiempo tras preparación superior al aprobado.
- No activa IV automáticamente al registrar la segunda dosis IM ni por signos cutáneos aislados; el especialista confirma persistentemente compromiso ABC.
- No exporta orden si faltan monitorización, vía dedicada, bomba, personal competente o verificación doble cuando esta sea posible sin retrasar tratamiento.
- Alertas por hipertensión, arritmia, extravasación y perfusión fallida; nunca acelera automáticamente ni realiza bolos IV de rescate.
- Prueba fronteras por edad/peso, reacciones graves solo respiratorias y fallo de conexión; sin inventar protocolos pediátricos locales.
- Todos los demás 18 contratos permanecen BLOCKED, 4 P1 intactos, `CLINICALLY_PENDING` global y no YELLOW→GREEN automático.

**QA de este expediente:** solo revisión documental. **No se han ejecutado las pruebas anteriores, no se ha probado la bomba ni una perfusión local y no hay QA de integración.**

## 6. Decisión y siguiente acción

- `ANAPHYLAXIS_REFRACTORY_REFERENCE_REVIEWED`: evidencia clínica **documentada**.
- `LOCAL_10_MCG_ML_PRODUCT_AND_STABILITY`: **PENDIENTE DE FARMACIA**.
- `LOCAL_PUMP_AND_MONITORING_SIGNOFF`: **PENDIENTE DE URGENCIAS/UCI/ENFERMERÍA**.
- `INTEGRATED_NEGATIVE_TESTS`: **NOT_RUN**.
- `anaphylaxis-refractory`: **BLOCKED / CLINICAL_REVIEW_REQUIRED**.
- **No tocar `main`, v1.42-rc1 ni v1.43; no abrir I02, no modificar contratos anteriores ni otros módulos.**

**Confirmación imprescindible del siguiente paso:** documentación de Farmacia que valide **el preparado final de 1 mg/100 mL para perfusión en anafilaxia refractaria y su estabilidad/tiempo máximo de uso** con el producto realmente disponible. La declaración previa de 1 mg/10 mL IV tiene **otro uso y concentración**.
