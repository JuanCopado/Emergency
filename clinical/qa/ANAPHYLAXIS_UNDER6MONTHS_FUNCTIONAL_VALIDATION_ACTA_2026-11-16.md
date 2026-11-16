# EMERGENCY — Acta corregida de validación clínica, farmacéutica y funcional

**Contrato:** `anaphylaxis-under6months` (3/19)  
**Protocolo propuesto:** adrenalina (epinefrina) **intramuscular SIN DILUIR a 1 mg/mL**, dosificación ponderal para anafilaxia en **menores de seis meses**.  
**Versión del acta:** propuesta corregida 1.1 — 16/11/2026.  
**Rama de evidencia:** `review/anaphylaxis-under6months-evidence-20261116`.  
**Estado de las pruebas:** **NO EJECUTADAS**. **Dictamen:** **PENDIENTE DE VALIDACIÓN**.  
**Estado del contrato:** **`BLOCKED / CLINICAL_REVIEW_REQUIRED`**. No representa autorización para producción.

> Esta acta CORRIGE el documento inicial; no es una certificación ni un protocolo farmacológico firmado. Sus casillas, pruebas, firmantes y fechas se mantienen pendientes hasta obtener evidencias reales. La administración inmediata de adrenalina IM ante anafilaxia depende del profesional tratante y **nunca debe retrasarse por una aprobación del software**.

## 1. Decisiones clínicas ya comunicadas por el propietario

| Parámetro | Decisión para el diseño |
|---|---|
| Grupo | Lactantes con edad cronológica **menor de 6 meses**; la aplicabilidad a neonatos exige revisión pediátrica específica |
| Principio activo | Adrenalina (epinefrina) |
| Vía | **IM**, cara anterolateral del tercio medio del muslo |
| Concentración IM | **1 mg/mL sin diluir** |
| Pauta ponderal | **0,01 mg/kg = 10 microgramos/kg IM** (0,01 mL/kg de solución 1 mg/mL), como referencia para aprobación |
| Intervalo de reevaluación | Tras **5 minutos** si persisten signos; repetir únicamente por decisión clínica según protocolo |
| Preparación local diferente | **1 mg hasta un volumen FINAL de 10 mL = 0,1 mg/mL**, **solo IV**; **no pertenece a este contrato IM** |
| Regla RCUK fija 100–150 microgramos para <6 meses | Documentada como discrepancia de fuente, **no** usar de forma automática ni combinar con pauta ponderal |

**Nota:** la dosis calculada en mg debe distinguirse del volumen de la jeringa en mL. No se ha aprobado ninguna regla general de redondeo, mínimo absoluto por dosis, ni técnica de medición de microvolúmenes. **No existe un mínimo universal de 0,10 mg para este contrato**: a 5 kg, la dosis teórica ponderal es 0,05 mg.

## 2. Verificación galénica y operativa — Farmacia y Enfermería

| ID | Criterio crítico | Evidencia y aceptación necesaria | Estado |
|---|---|---|---|
| FAR-01 | Producto IM | Confirmar stock, lote/presentación **1 mg/mL** y ficha técnica aplicable a la vía IM en Portugal; la marca puede ocultarse en la UI, pero debe quedar identificada internamente | ☐ Pendiente ☐ PASS ☐ FAIL |
| FAR-02 | Separación física y digital | Segregar **1 mg/mL IM** de la preparación **0,1 mg/mL IV**; error ×10 y cruce de vías deben generar rechazo informático explícito; señalización local y doble verificación operacional | ☐ Pendiente ☐ PASS ☐ FAIL |
| FAR-03 | Excipientes y conservación | Revisar los excipientes **reales de la presentación** (p. ej., sulfitos si los contiene), caducidad, protección de luz y condiciones del fabricante; no presuponer metabisulfito en cualquier marca | ☐ Pendiente ☐ PASS ☐ FAIL |
| FAR-04 | Medición de volúmenes pequeños | Identificar jeringa y graduación verificadas, exactitud útil en los volúmenes reales de recién nacidos/lactantes, aguja IM adecuada y un método aprobado de preparación SIN diluir | ☐ Pendiente ☐ PASS ☐ FAIL |
| FAR-05 | Técnica de carga y espacio muerto | Procedimiento ensayado de aspiración, cambio de aguja cuando proceda, purga y verificación del volumen **efectivamente administrado**; no improvisar técnicas ni precargas | ☐ Pendiente ☐ PASS ☐ FAIL |
| FAR-06 | Regla de redondeo | Aprobación expresa de incremento de medición, método de redondeo, error relativo admisible y conducta si el volumen requerido **no puede medirse con precisión**; no fijar de oficio 0,01 mL como suficiente para todo peso | ☐ Pendiente ☐ PASS ☐ FAIL |

## 3. Reglas clínicas — protocolo exclusivo de menores de seis meses

| ID | Criterio crítico | Regla corregida / límite de seguridad | Estado |
|---|---|---|---|
| CLI-01 | Dosis ponderal | Referencia **0,01 mg/kg IM** con adrenalina **1 mg/mL SIN diluir**. El resultado nominal es `0,01 × peso_kg` en mg y el mismo número en mL. Sin mínimo de 0,10 mg ni pauta fija por edad por defecto | ☐ Pendiente ☐ PASS ☐ FAIL |
| CLI-02 | Peso no disponible | No ofrecer automáticamente **0,15 mg a todos los menores de 6 años**: podría exceder notablemente la pauta ponderal en un lactante. Mostrar alerta para estimación clínica rápida y decisión del equipo, sin impedir la atención urgente | ☐ Pendiente ☐ PASS ☐ FAIL |
| CLI-03 | Edad y población | Admitir únicamente **edad <6 meses** y registrar edad exacta en días/meses y peso. Un paciente de **6 meses exactos** o mayor debe salir de este contrato y pasar al circuito pediátrico pertinente; nunca aplicar dosis adultas aquí | ☐ Pendiente ☐ PASS ☐ FAIL |
| CLI-04 | Vía y lugar | Exclusivamente **IM anterolateral del muslo**. Rechazar vía IV, SC, glútea o cualquier concentración distinta de 1 mg/mL dentro del cálculo IM | ☐ Pendiente ☐ PASS ☐ FAIL |
| CLI-05 | Doble comprobación sin retraso | Comprobar identidad, peso, concentración, dosis/volumen, jeringa y vía, preferiblemente con una segunda persona si está disponible de inmediato. La imposibilidad de registrar dos firmas **no debe bloquear ni retrasar la medicación urgente**; documentar verificación retrospectiva | ☐ Pendiente ☐ PASS ☐ FAIL |
| CLI-06 | Repetición | Reevaluar síntomas ABCDE a los **5 minutos** y alertar si persisten. No programar dosis automáticas ni imponer un bloqueo rígido de 5 minutos frente a una decisión médica urgente documentada | ☐ Pendiente ☐ PASS ☐ FAIL |
| CLI-07 | Escalada | Persistencia de compromiso respiratorio/circulatorio pese a **dos dosis IM apropiadas**: activar **alerta para equipo experto/UCI y protocolo de anafilaxia refractaria**. **No iniciar automáticamente ni mostrar ajustes de perfusión IV** en este contrato | ☐ Pendiente ☐ PASS ☐ FAIL |
| CLI-08 | Seguridad global | Datos faltantes, valores no numéricos, concentración errónea, vía equivocada, redondeo no validado o imposibilidad de medir volumen → **NO generar orden farmacológica**; mantener orientación clínica y activación de emergencias | ☐ Pendiente ☐ PASS ☐ FAIL |
| CLI-09 | No retrasar tratamiento | El sistema no exigirá confirmaciones administrativas para que el profesional pueda tratar la anafilaxia; la validación del software es separada de la atención inmediata | ☐ Pendiente ☐ PASS ☐ FAIL |

## 4. Matriz de pruebas sintéticas — NO EJECUTADAS

Los ejemplos son **valores nominales para pruebas de software**, no prescripciones ni aprobación del redondeo. La columna «obtenido» está vacía porque no se han ejecutado ensayos.

| ID | Caso de simulación | Resultado esperado del contrato 3 | Obtenido | Estado |
|---|---|---|---|---|
| TC-01 | **5 kg; 2 meses; 1 mg/mL IM** | Valor nominal **0,05 mg = 0,05 mL**; no aplicar «mínimo 0,10 mg»; verificar medición autorizada | — | NOT_RUN |
| TC-02 | **7,6 kg; 5 meses** | Valor bruto **0,076 mg = 0,076 mL**. El candidato **0,08 mL** solo puede mostrarse si Farmacia aprueba ese redondeo y el margen de error | — | NOT_RUN |
| TC-03 | **3,2 kg; recién nacido** | Valor nominal **0,032 mg = 0,032 mL**; no imponer 0,03 mL automáticamente; activar revisión neonatal y de precisión | — | NOT_RUN |
| TC-04 | **7,6 kg; 6 meses exactos** | **Fuera del contrato** (<6 meses). Remitir a circuito pediátrico correspondiente | — | NOT_RUN |
| TC-05 | **Sin peso conocido; 4 meses** | No atribuir dosis fija de 0,15 mg por edad; mostrar alerta de estimación/decisión profesional **sin retrasar asistencia** | — | NOT_RUN |
| TC-06 | **0,1 mg/mL seleccionada + vía IM** | **RECHAZAR** por concentración IV en ruta IM; advertir error ×10 | — | NOT_RUN |
| TC-07 | **1 mg/mL seleccionada + vía IV** | **RECHAZAR** en el contrato 3; remitir a circuito IV independiente, sin conversión automática | — | NOT_RUN |
| TC-08 | **Peso 0, negativo, NaN, infinito, texto, unidades erróneas** | Rechazo de cálculo/orden y aviso de datos inválidos | — | NOT_RUN |
| TC-09 | **Segunda dosis 2 min tras primera** | Aviso de evaluación/intervalo habitual; sin autoadministración ni bloqueo de actuación médica urgente | — | NOT_RUN |
| TC-10 | **Persisten signos ABC tras dos dosis IM** | Solicitar ayuda especializada y mostrar circuito de anafilaxia refractaria, **sin perfusión IV automática** | — | NOT_RUN |
| TC-11 | **Microvolumen no medible** | Bloquear **generación automática de volumen/prescripción**, mostrar necesidad de decisión por equipo y Farmacia; no bloquear tratamiento manual | — | NOT_RUN |
| TC-12 | **Jeringa/fabricante desconocido o redondeo no aprobado** | No mostrar volumen final de inyección como validado ni permitir orden electrónica | — | NOT_RUN |
| TC-13 | **Error de conversión mg ↔ microgramos o mL** | Prueba de invariantes dimensionales; diferencia ×10/×1000 → rechazo y alerta | — | NOT_RUN |
| TC-14 | **Intento de usar autoinyector 0,15 mg en un lactante sin peso verificado** | No asignación automática; decisión clínica y etiquetado específico del dispositivo por separado | — | NOT_RUN |
| TC-15 | **Prueba de usabilidad real por personal de Urgencias/Enfermería** | Medir errores de selección, lectura y preparación; establecer umbrales de aceptación **antes** del ensayo, sin declarar «<15 s, 0 errores» como hecho | — | NOT_RUN |
| TC-16 | **Intento de exportar una orden IM/IV desde el preflight en estado BLOCKED** | Sin órdenes ni mL/h; conservar `CLINICALLY_PENDING` y mensajes de derivación humana | — | NOT_RUN |

## 5. Resolución de discrepancias del acta original

| ID original | Incidencia corregida | Decisión |
|---|---|---|
| CLI-01 | Indicaba mínimo 0,10 mg pero TC-01 esperaba 0,05 mg | **Eliminar mínimo 0,10 mg**; conservar dosis ponderal nominal; revisar redondeo/volúmenes pequeños |
| CLI-02 | Proponía 0,15 mg por edad en <6 años sin peso | **No aplicar en <6 meses** ni usarlo como sustituto automático del peso |
| CLI-03 | Incluía ≥50 kg/adultos en contrato 3 | **Fuera de alcance**; otro circuito clínico |
| CLI-05 | Doble firma obligatoria antes del fármaco | Establecer verificación rápida cuando sea posible, **sin retrasar adrenalina IM** |
| CLI-06 y TC-08 | Activación automática de perfusión IV tras 2–3 dosis | Sustituir por **alerta de escalada especializada**, sin prescripción IV |
| TC-02 | Niño de 6 meses incluido como menor de 6 meses; 0,08 mL tomado como válido | Cambiar caso a **5 meses**, considerar redondeo solo tras validación y agregar prueba de frontera de 6 meses |
| FAR-02 | Llamaba 0,1 mg/mL «exclusivamente IV en PCR» | Es **preparación local IV separada**; no asumir una indicación IV específica ni permitirla por la ruta IM |
| FAR-03 | Presuponía metabisulfito en todas las presentaciones | Revisar excipientes y condiciones de la **marca realmente disponible** |
| TC-09 | Exigencia «<15 s, 0 errores» sin protocolo de estudio | Convertir en **objetivo prospectivo pendiente**, no resultado aprobado |
| Firmas/resultado | Campos vacíos y sin pruebas ejecutadas | Estado **PENDIENTE**, sin firmas ni aprobación inventada |

## 6. Requisitos para retirar el bloqueo del contrato 3

1. **Decisión pediátrica nominal y fechada:** aprobar que **0,01 mg/kg IM con 1 mg/mL sin diluir** se aplica a <6 meses, incluyendo definición de neonatos, máximo, repetición y relación con el algoritmo RCUK fijo alternativo. La selección del propietario está documentada, pero **no sustituye** la revisión profesional formal.
2. **Farmacia:** identificar la presentación IM concreta y ficha técnica portuguesa, confirmar stock, almacenamiento, manejo de ampollas, jeringas disponibles y **medición fiable de microvolúmenes**, con política de redondeo y de valores no medibles. Resolver la concentración IM/IV segregada.
3. **Enfermería:** documentar verificación rápida y procedimiento real de carga, aguja, espacio muerto, volúmenes pequeños y vía IM **sin retrasos de emergencia**.
4. **Implementación y QA:** modificar únicamente el contrato 3 en rama aislada y con alcance explícito; probar todos los casos sintéticos anteriores, errores dimensionales, límites de edad y exportaciones; ejecutar regresión de los otros 18 contratos y controles P1. En estado BLOCKED no debe generarse una orden.
5. **Auditoría y aprobación final:** obtener firmas/atestaciones trazables de Farmacia, pediatría/Urgencias, Enfermería y QA, con fecha, referencia de protocolo, **SHA exacto** de código probado y dictamen independiente, antes de quitar `block_reason` o permitir prescripción. Esto **no autoriza automáticamente producción** ni cambia `CLINICALLY_PENDING`.

**Dictamen de esta acta:** DOCUMENTO CORREGIDO, **NO VALIDADO**. Contrato 3 **BLOCKED**.

## 7. Registro de ejecuciones y firmas — pendiente

**Fecha real de ejecución:** ____________________  
**Rama/commit/árbol de código evaluado:** ____________________  
**Entorno y versión del software:** ____________________  
**Tests ejecutados y artefactos SHA-256:** ____________________  
**Resultado:** ☐ PASS ☐ PASS_WITH_FINDINGS ☐ FAIL ☐ NOT_RUN (actual)  
**Decisión autorizada de liberación:** ☐ Aprobar condicionalmente tras requisitos ☐ NO-GO (actual)

| Rol | Nombre/ID profesional | Firma o atestación verificable | Fecha | Decisión |
|---|---|---|---|---|
| Farmacia Hospitalaria | Pendiente | Pendiente | Pendiente | Pendiente |
| Pediatría / Urgencias | Pendiente | Pendiente | Pendiente | Pendiente |
| Supervisión de Enfermería | Pendiente | Pendiente | Pendiente | Pendiente |
| Responsable técnico / QA independiente | Pendiente | Pendiente | Pendiente | Pendiente |

## 8. Fuentes revisadas

- [ERC — European Resuscitation Council Guidelines 2025, Paediatric Life Support, apartado Anaphylaxis, p. 20](https://www.erc.edu/media/03xnpjmj/gl2025-09-pls-e.pdf): IM 0,01 mg/kg con 1 mg/mL, repetición a 5 min, evaluación ABCDE y consulta experta tras más de dos dosis.
- [Direção-Geral da Saúde, Norma 014/2012 actualizada a 18/12/2014 — Anafilaxia: Abordagem Clínica](https://www.dgs.pt/directrizes-da-dgs/normas-e-circulares-normativas/norma-n-0142012-de-16122012.aspx): marco portugués de referencia.
- [RCUK — Anaphylaxis algorithm, Paediatric emergency algorithms, julio 2025, v3.1](https://www.resus.org.uk/sites/default/files/2025-07/RCUK%20Paediatric%20emergency%20algorithms%20and%20resources%20Jul%2025%20V3.1.pdf): concentraciones IM, banda alternativa 100–150 microgramos en <6 meses, escalada si persiste compromiso tras dos dosis.
- Compendio de anafilaxia aportado por el propietario (UpToDate recopilado, octubre–noviembre 2026): material de apoyo; incluye errores de traducción/OCR y **no** sustituye ficha técnica, guías primarias ni la validación de Farmacia.

---
**Protección:** No modificar `main`, no cambiar `CLINICALLY_PENDING`, los cuatro P1, los otros 18 bloqueos, ni iniciar I02. No promover GREEN ni retirar `BLOCKED` por una acta en blanco.

## 9. Anexo FAR-04/FAR-05/FAR-06 — Selección de jeringa y espacio muerto (información aportada por el propietario)

**Fecha de incorporación:** 16/11/2026. **Estado de todos los criterios: NO VALIDADO FÍSICAMENTE / NOT_RUN.**
El propietario ha aportado una tabla de capacidades y graduaciones de jeringas, junto con una propuesta de manejo de agujas y espacio muerto. Se registra como **evidencia de diseño y propuesta operativa**, no como autorización farmacéutica ni como ensayo ejecutado. El ámbito de esta acta sigue siendo **adrenalina 1 mg/mL sin diluir por vía IM en menores de seis meses**, con dosis ponderal **0,01 mg/kg**.

### FAR-04 — Dispositivos candidatos y excluidos del circuito 3

| Dispositivo | Graduación declarada por el propietario | Decisión para este contrato | Evidencia por aportar |
|---|---|---|---|
| Jeringa de tuberculina de 1 mL, escala en **mL** | 0,01 mL por marca fina | **CANDIDATO PREFERENTE, NO VALIDADO**. La graduación visual no acredita que entregue exactamente 0,025–0,08 mL | Modelo, ficha técnica, error volumétrico en el intervalo de interés, técnica y aguja real |
| Jeringa de insulina U-100 | Equivalencia nominal de marcas de volumen 100 unidades de insulina/mL; algunos modelos tienen doble escala | **EXCLUIR DEL FLUJO POR DEFECTO**. No presentar las marcas de unidades de insulina como unidades de dosis de adrenalina; el riesgo de confusión mg/mL/unidades y de aguja SC es crítico. Solo reconsiderar con autorización específica, documentación mL inequívoca y estudio de conjunto | Modelo, agujas intercambiables, etiquetado inequívoco, SOP y revisión independiente |
| Jeringa estándar 2–3 mL | Habitualmente 0,1 mL, según modelo | **NO APTA para microvolúmenes del contrato 3** | No procede como dispositivo candidato |
| Jeringa estándar 5 mL | Escala variable por fabricante, a menudo 0,2 mL | **NO APTA para microvolúmenes del contrato 3** | No extrapolar a decisiones de dosis adulta fuera de alcance |

**No convertir marcas U-100 en unidades clínicas de adrenalina ni incorporarlas al software o a etiquetas.** La identidad dimensional básica de U-100 solo sería una propiedad de esa escala volumétrica y es fácil de malinterpretar como actividad farmacológica. [ISMP Guidelines for Optimizing Safe Subcutaneous Insulin Use](https://www.ismp.org/sites/default/files/attachments/2018-09/ISMP138D-Insulin%20Guideline-090718.pdf) documenta riesgos de confusión entre unidades de insulina y mL; no atribuirle una prohibición universal de jeringas de doble escala sin una fuente explícita.

**El problema no se resuelve eligiendo 1 mL con rayas de 0,01 mL.** La investigación [Development of Guidelines for Accurate Measurement of Small Volume Parenteral Products Using Syringes](https://pmc.ncbi.nlm.nih.gov/articles/PMC8114303/) muestra diferencias relevantes de exactitud/reproducibilidad y riesgo superior de error cuando se mide menos del 20 % de la capacidad nominal de la jeringa. Los objetivos del contrato (p. ej., 0,025 / 0,032 / 0,05 / 0,076 mL) se encuentran por debajo de ese 20 % en una jeringa de 1 mL. Se requieren mediciones reales o alternativa formalmente validada; el ensayo citado no establece por sí solo una prohibición universal ni un error máximo farmacéutico específico.

### FAR-05 — Aguja y volumen muerto

- La propuesta de aguja IM de 16–25 mm / calibre 23–25 G se acepta **solo como rango de referencia a evaluar**, NO como indicación automática. Seleccionar según edad gestacional y cronológica, masa muscular, sitio y técnica. El [CDC](https://www.cdc.gov/vaccines/hcp/administration/during.html) ofrece, **para vacunación IM**, una referencia distinta para neonatos (16 mm, 22–25 G) y lactantes de 1–12 meses (25 mm, 22–25 G); **no debe transformarse mecánicamente en una orden de adrenalina**.
- La cifra aportada de **0,05–0,08 mL de espacio muerto** es plausible en algunas combinaciones, pero **NO es un valor fijo para todas las jeringas y agujas**. Los datos sobre diseños y tolerancias en [ISO 7886-1:2017, revisión](https://pmc.ncbi.nlm.nih.gov/articles/PMC9750608/) revelan gran variación; puede ser proporcionalmente mayor que la dosis buscada. Se necesita caracterización del **conjunto real jeringa+aguja**.
- No aprobar de modo universal «purgar hasta la punta antes de enrasar» ni otra técnica de cambio de aguja como si fuera clínicamente validada. Farmacia/Enfermería deben redactar y ensayar un **procedimiento estéril reproducible**, medir el **volumen entregado** y excluir retención/pérdida accidental. No compensar espacio muerto añadiendo una cantidad empírica de fármaco y no diluir la solución IM sin nueva conciliación.
- La técnica y la capacitación se auditan **sin utilizar pacientes ni adrenalina real en el ensayo inicial**; emplear sustituto no farmacológico, dispositivo autorizado y medición trazable. Después corresponderá la aceptación farmacéutica de aplicabilidad al producto real.

### FAR-06 — Prueba prospectiva de precisión y redondeo, todavía NO EJECUTADA

**Preparación del ensayo:** obtener inventario del fabricante y modelo de jeringa, lote, escala, compatibilidad Luer/aguja IM, método de carga, aguja de extracción, presencia de aire, control de volumen muerto y equipamiento de medición calibrado.

**Desafíos sintéticos representativos:** volúmenes teóricos 0,025; 0,032; 0,050; 0,076 mL y valores de frontera de la técnica. El valor de 0,025 mL redondeado matemáticamente a 0,03 mL produce **+20 %** de error, sin contar variabilidad del dispositivo. No inferir que 0,03 ni 0,08 mL estén aprobados para administración.

**Datos a registrar para cada combinación:** volumen diana, volumen entregado medido, error absoluto/relativo por repetición, dispersión entre observadores, efectos de cambio de aguja, purga y cebado; registrar también casos que no se pueden medir. Definir **ANTES DEL ENSAYO** número de repeticiones, límites de error aceptables, criterios de STOP, incertidumbre instrumental y responsables aprobadores. No presentar resultados teóricos como observados.

**Criterio de aceptación:** Farmacia y Enfermería aprueban un dispositivo y una técnica específicos con evidencia experimental, incluyendo manejo seguro de volúmenes que no alcancen precisión suficiente. Si no hay dispositivo verificado, el **motor de prescripción sigue bloqueado**; la actuación clínica urgente no debe retrasarse por la aplicación.

### Decisión de calidad / responsable

- Conformidad del propietario/clinico **Juan Copado** con la pauta teórica y la continuación de la revisión: **declarada por el propietario**, no firma inventada de Farmacia/Enfermería.
- Microvolúmenes, espacio muerto y agujas: **FAR-04/FAR-05/FAR-06 PENDIENTES de ensayo físico**.
- Las 20 pruebas de preflight son sintéticas (lógica no prescriptiva); **no equivalen a 16 pruebas integradas, estudio de precisión ni aprobación de producción**.
- Estado del contrato: \`anaphylaxis-under6months\` **BLOCKED**; conservar \`CLINICALLY_PENDING\`, los otros 18 contratos, cuatro P1 e I02 NO-GO.

**Anexo de fuentes:** también [Small-Volume Injections: Evaluation of Volume Administration Deviation](https://pubmed.ncbi.nlm.nih.gov/28338490/), ensayo ex vivo de medición/administración de pequeños volúmenes.


## 10. Registro de candidatos reales de jeringa, declaración del responsable (16/11/2026)

**Fuente local:** el responsable informa que el hospital dispone de jeringas de tuberculina **1 mL con aguja**, comercializadas en cajas «100 Un.», de las marcas **BD Plastipak**, **dicoTUBER (ZARYS)** y **Terumo**. Es una declaración de marcas/familias de producto, **NO una confirmación de referencia SKU, aguja, lote, graduación física o exactitud de la jeringa utilizada en cada acto**. «100 Un.» describe presumiblemente **100 unidades por caja**, NO una escala U-100 de insulina; comprobar la etiqueta real.

### Documentación técnico-comercial contrastada

| Familia comunicada | Identificación documental orientativa, NO atribuida aún al stock | Graduación descrita | Riesgo pendiente |
|---|---|---|---|
| **BD Plastipak 1 mL Tuberculin** | Catálogo BD: ref. **303172** sin aguja, Luer slip 0,01 mL; **303175** y **303176** con agujas 25G/10 mm y 26G/10 mm respectivamente. Existen también tipos de aguja integrada. [BD product catalogue](https://www.bd.com/documents/international/catalogs/medication-delivery-solutions/MDS_Medication-Delivery-Solutions-Product-Catalogue_CT_EN.pdf) | **0,01 mL** | Determinar modelo en el hospital, aguja fija/intercambiable, longitud para IM, espacio muerto y reproducibilidad |
| **ZARYS dicoTUBER** | Catálogo de fabricante **TU-U20-1-BL**, aguja independiente **26G × 13 mm**, conector Luer. [ZARYS 2026 catalogue](https://zarys.pl/wp-content/uploads/2026/01/2026_Sprzet-jednorazowy-PL-REV.-IV-01.2026.pdf) | **0,01 mL según fabricante** | Algunos distribuidores muestran 0,05 mL para aparentemente la misma familia; comprobar visualmente cada raya del modelo real. Longitud de aguja IM pendiente |
| **Terumo 1 mL tuberculin** | Ficha del fabricante: **SS-01T** sin aguja; **SS-01T2516**, **SS-01T2609**, **SS-01T2713** con agujas extraíbles de 16, 9, 13 mm. Variantes portuguesas también pueden llevar códigos distintos (p. ej. MDSS01S2613E). [Terumo product sheet](https://www.terumotmp.com/content/dam/terumo-www/proprietary/terumo-tmp/en-us/product-assets/Terumo-Needle/Conventional-Needles-and-Syringes-sellsheet.pdf) | **0,01 mL** | Determinar referencia europea exacta, tipo de aguja y espacio muerto. Una ficha de distribuidor portugués para 26G/13 mm informa de espacio muerto <0,07 mL, **NO de volumen realmente entregado ni de precisión garantizada para 0,03 mL** |

**Problema físico crítico:** algunas jeringas llevan aguja fija corta, por lo que «jeringa de tuberculina con aguja» no demuestra idoneidad para inyección **intramuscular** anterolateral del muslo en un lactante. Una graduación de 0,01 mL tampoco demuestra exactitud para 0,025–0,076 mL, ni compensa el espacio muerto. La aguja de carga, el cambio a una aguja IM de longitud indicada y la purga requieren un procedimiento validado para el **conjunto real**.

### Procedimiento de ensayo de FAR-04/FAR-05/FAR-06: pendiente de ejecución

1. Inventariar del hospital **código de referencia/SKU, fabricante, lote y modelo** de cada jeringa en uso y sus agujas, a partir del envase original. Registrar por separado aguja fija, desmontable y conector Luer.
2. Obtener ficha técnica e instrucciones de uso de cada referencia, datos del volumen muerto/retención, graduación y tolerancias; documentar cualquier discordancia entre fabricante y distribuidor.
3. Farmacia y Supervisión de Enfermería seleccionarán **ANTES de ensayar** el protocolo de medición, método de verificación gravimétrico o volumétrico calibrado, criterios de aceptación de error y precisión, límites por microvolumen y técnica de purga/aguja, sin utilizar pacientes ni fármaco en el ensayo inicial.
4. Comparar resultados reales para dosis teóricas de 0,025, 0,032, 0,050, 0,076 mL con repetición/operadores predefinidos, contemplando ausencia de alternativa segura cuando el dispositivo no sea fiable. **No suponer que todas las marcas se comportan igual ni sustituir una validación por otra.**
5. Registrar acta de ejecución, instrumentación, datos crudos, errores absolutos/relativos, desviación entre operadores, responsables, firmas, fecha, límites alcanzados y criterios de STOP.

**Estado de este anexo:** dispositivos candidatos identificados / **FAR-04, FAR-05, FAR-06 NOT_VERIFIED; ensayos físicos NOT_RUN**. No añadir por ello un mínimo de dosis, redondeos automáticos, sustituciones por escala U-100, órdenes de administración ni velocidades. **El contrato 3 continúa BLOCKED.**

**Precaución sobre ámbito:** los nombres de marca son datos aportados por el propietario, no evidencia directa de SKU. Esta comparación bibliográfica no habilita físicamente la administración de adrenalina a través de una aguja de tuberculina ni valida la dosis entregada. La urgencia clínica nunca debe retrasarse por el bloqueo del software.
