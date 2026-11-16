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