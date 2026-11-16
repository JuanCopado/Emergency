# EMERGENCY — Contrato 4/19 · Anexo pediátrico de seguridad y pruebas negativas

**Fecha:** 16/11/2026. **Estado:** \`PROPOSED / CLINICAL_REVIEW_REQUIRED / BLOCKED\`.  
**Contrato actual:** \`anaphylaxis-refractory\`. En \`clinical/scripts/acute_medication_contracts.py\` su población ejecutable todavía es **adult**. **Este anexo pediátrico NO amplía ese selector ni habilita una bomba pediátrica.** Para ampliar a pediatría, requiere contrato explícito diferenciado, revisión de producto y aprobación técnica/humana independientes.  
**Ámbito:** anafilaxia refractaria en población pediátrica, perfusión intravenosa de adrenalina bajo equipo experto. Ningún paciente real ni datos clínicos se han utilizado.  
**Aprobación del propietario:** el propietario ha autorizado preparar esta documentación y batería de casos negativos; **no** se atribuyen firmas de Farmacia, Enfermería, UCI o Calidad.

## BLOQUE A — Conciliación farmacéutica y circuito de administración

### A.1. Contexto clínico respaldado, no liberación de dosis

- **RCUK 2025 Guidelines — Paediatric emergency algorithms & resources, febrero 2026, v6, pág. 9:** considerar circuito refractario con persistencia de problemas respiratorios o circulatorios pese a **2 dosis adecuadas de adrenalina IM**. Buscar apoyo experto, vía IV periférica dedicada/IO, cristaloides y perfusión de baja dosis de adrenalina con monitorización continua. La hoja de febrero de 2026 reemplaza la versión pediátrica de julio de 2025 usada en referencias anteriores; confirmar versión vigente en cada release.
- **ASCIA Acute Management of Anaphylaxis 2026, págs. 5–6:** en anafilaxia refractaria tras **dos dosis IM**, iniciar perfusión IV/IO bajo equipo experto, optimizando fluidos. Pauta alternativa referencial **1 mL de solución 1 mg/mL en 100 mL de NaCl 0,9 %** y **0,5 mL/kg/h** como inicio de referencia; la titulación requiere observación clínica.
- Ambas referencias describen concentración aproximada de **10 microgramos/mL** para la bolsa estándar de 100 mL, **pero el volumen final exacto y el sobrellenado comercial NO están acreditados**. La elección previa del propietario para Emergency es **1 mg hasta 100 mL finales**; Farmacia ha de validar esa técnica, no dar por equivalentes «añadir a una bolsa nominal de 100 mL» y «100 mL finales medidos».
- El compendio aportado por el propietario (\`ANAFILAXIA.pdf\` + compendio Markdown; capítulos UpToDate) describe **otras preparaciones y rangos ponderales**. Es una fuente secundaria/propietaria con errores de OCR/traducción reconocidos: **no combinar 1/4/10 microgramos/mL ni extrapolar máximos sin procedimiento local confirmado**.
- La descripción «0,1–1 microgramos/kg/min» del propietario es un **rango bibliográfico orientativo de perfusión experta**, no una autorización para infundir toda esa amplitud ni evidencia de que **>1 microgramo/kg/min sea un máximo absoluto universal**. Los límites soft/hard pediátricos de la biblioteca de bomba deben ser **definidos y firmados** por el equipo local; hasta entonces cualquier tasa fuera del esquema seleccionado se envía a revisión y **ninguna bomba arranca automáticamente**.
- Los bolos IV **no son una acción del contrato de perfusión**. ASCIA 2026/RCUK 2026 **no recomiendan bolos rutinarios**, pero contemplan excepciones por especialistas en peri-parada; la **parada cardíaca** usa un algoritmo distinto. No programar una prohibición universal que interfiera con reanimación.

**Fuentes:**
- [RCUK, Paediatric emergency algorithms and resources, February 2026, v6, refractory anaphylaxis p.9](https://www.resus.org.uk/sites/default/files/2026-02/RCUK%20Paediatric%20emergency%20algorithms%20and%20resources%20Feb%2026%20V6.pdf).
- [ASCIA Guidelines for Acute Management of Anaphylaxis 2026, pp.5–6](https://www.allergy.org.au/images/ASCIA_HP_Guidelines_Acute_Management_Anaphylaxis_2026.pdf).
- [RCH Melbourne, Clinical Practice Guideline: Anaphylaxis](https://www.rch.org.au/clinicalguide/guideline_index/Anaphylaxis/).

### A.2. Tabla de aceptación de Farmacia / Enfermería / UCI

| ID | Requisito | Control de aceptación y evidencia | Estado |
|---|---|---|---|
| GAL-01 | **Producto de partida y stock local** | Identificar exactamente fabricante, presentación **1 mg/mL**, lote/RCM portugués, principio activo expresado como base/sal y vía aprobada. No suponer que Adrenalina Basi España corresponde al stock en Horta. | **PENDIENTE** |
| GAL-02 | **Segregación ×10/×100** | Separar 1 mg/mL IM de 0,1 mg/mL IV (1 mg/10 mL final) y 0,01 mg/mL (10 µg/mL) de perfusión; alertas visuales y machine-readable. La solución 0,1 mg/mL se rechaza como *producto de partida* en esta receta particular; no negar otros protocolos especializados autorizados. | **PENDIENTE** |
| GAL-03 | **Concentración estándar propuesta** | Referencia para estudio: **10 µg/mL**, 1 mg de producto 1 mg/mL + NaCl 0,9 % hasta **100 mL finales reales**; verificar la técnica, volumetría/overfill y si se puede preparar y medir ese volumen en la bolsa/jeringa disponible. | **PENDIENTE** |
| GAL-04 | **Alternativa jeringa 50 mL** | **0,5 mg/50 mL** da nominalmente 10 µg/mL, pero es **alternativa NO APROBADA**: requiere preparación/estabilidad/compatibilidad/producto/contenedor y bomba específicos, y autorización separada; no habilitarla por igualdad aritmética. | **PENDIENTE** |
| GAL-05 | **Diluyente** | El circuito revisado RCUK/ASCIA usa **NaCl 0,9 %**. Propuesta de **SG 5 %** del propietario se marca **PENDIENTE DE VALIDACIÓN producto-específica** (y cambio de protocolo); no habilitar como equivalente automático. | **PENDIENTE** |
| GAL-06 | **Estabilidad y protección** | Farmacia debe certificar **plazo desde preparación**, temperatura, luz, contenedor, compatibilidad, sustitución y concentración específica, verificando RCM/local evidence. **NO fijar 24 h por defecto**. Una ficha [DailyMed, Adrenalin](https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=b293ad8e-7055-4a95-a130-9d7d74f19eab) establece para *su formulación* 4 h a temperatura ambiente o 24 h refrigerado en diluyentes concretos: evidencia de que una regla universal de 24 h a temperatura ambiente sería insegura. La fotoprotección propuesta se verificará con la formulación y el equipo local. | **PENDIENTE** |
| GAL-07 | **Incompatibilidades/Y-site** | Vía exclusiva, sin piggy-back; no coinfundir bicarbonato ni soluciones alcalinas sin compatibilidad certificada. Identificar lumen, conectores antirreflujo y manejo del volumen residual; la bomba y etiqueta deben corresponder a la solución realmente preparada. | **PENDIENTE** |
| GAL-08 | **Vía periférica/IO y extravasación** | Inicio por acceso periférico dedicado/IO si resulta apropiado por equipo experto; valorar CVC si precisa, pero sin retrasar reanimación. Registrar inspección frecuente/continua, reconocimiento precoz de extravasación y respuesta. El intervalo **cada 15 min** es una **propuesta local**, no se afirma obligatorio de RCUK. Disponibilidad y protocolo de **fentolamina** deben comprobarse: no presumir stock ni sustituir su validación por una mención bibliográfica. | **PENDIENTE** |
| GAL-09 | **Smart pump / guardrails** | Bibliotecas adulta/pediátrica separadas, nombre completo \`ADRENALINA_IV_REFRACTARIA_10MCG_ML\`, pesos/edad, límites parametrizados por Farmacia+UCI, unidades µg/kg/min y mL/h con fuente explícita, **sin bolos desde este asistente**, sin inferir «techo universal de 1 µg/kg/min». | **PENDIENTE** |
| GAL-10 | **Equipo, monitorización y parada** | Confirmación clínica de anafilaxia refractaria; equipo de reanimación/UCI, bomba y línea dedicada, ECG/SpO2 continuos, PA frecuente (RCUK: al menos c/5 min), evaluación de respuesta, extravasación, taquiarritmias, hipertensión y plan de retirada. | **PENDIENTE** |
| GAL-11 | **Verificación/etiquetado** | Etiqueta con paciente, medicamento, producto, concentración final, cantidad, diluyente, volumen final real, vía, preparación/fecha/hora, caducidad, lote, preparador/segundo verificador, bomba/protocolo. Verificación independiente por personal cualificado según procedimiento sin retrasar atención urgente. | **PENDIENTE** |
| GAL-12 | **Reglas de alcance** | Mantener rama pediátrica diferenciada del contrato **adult** actual, de la **adrenalina IM no diluida** y de **IV 1 mg/10 mL**. No usar jeringas de reanimación de 0,1 mg/mL como si fueran perfusión 10 µg/mL. La parada cardíaca/peri-parada sigue un contrato distinto. | **PENDIENTE** |

**Conclusión galénica:** la concentración nominal de 10 µg/mL está **documentada como referencia**. Ni el plazo de 24 horas, ni SG 5 %, ni la jeringa de 50 mL ni el material específico de Horta se encuentran validados. *La ausencia de documentación nunca se traduce en un valor por defecto*.

## BLOQUE B — Casos negativos que deben causar fallo seguro

La especificación ejecutable y el origen de cada caso figuran en \`clinical/qa/C04_PEDIATRIC_NEGATIVE_CASES_2026-11-16.json\`. **Estos casos están especificados, NO EJECUTADOS**. No equiparar la existencia del JSON con pruebas PASS.

| ID | Escenario de fallo inducido | Resultado esperado, sin impedir reanimación humana |
|---|---|---|
| **NEG-01** | Perfusión como primera línea, sin 2 dosis IM adecuadas ni confirmación experta de refractariedad | Rechazar *orden electrónica del contrato 4*; remitir a valoración especializada. Excepción vital/parada se rige por contrato ajeno. |
| **NEG-02** | Entrada de preparado **0,1 mg/mL (1 mg/10 mL)** como ampolla de partida | Rechazar receta de **1 mg/mL** y alertar error ×10; no conversiones automáticas. |
| **NEG-03** | Tasa por encima del intervalo/umbral local **no aprobado** | No emitir orden ni permitir programa de bomba hasta revisión y límites locales; no afirmar que **1 µg/kg/min es techo universal**. |
| **NEG-04** | Solicitud de **bolo IV** en el asistente ordinario de perfusión pediátrica | Rechazar acción en este asistente; derivar a reanimación/peri-parada especializada, no inhabilitar otros protocolos. |
| **NEG-05** | Peso ausente, 0, negativo, no finito o imposible sin reconciliación | Bloquear cálculo y orden; obtener medición/estimación clínica documentada; sin peso implícito por edad. |
| **NEG-06** | Y-site con bicarbonato/medio alcalino sin compatibilidad o línea no dedicada | Rechazo de validación de conexión de esa perfusión; indicar lumen/línea diferente. |
| **NEG-07** | Sin hora de preparación, plazo de uso/producto o fotoprotección cuando esté exigida | Bloquear liberación de mezcla y caducidad presunta; nunca asignar 24 h por defecto. |
| **NEG-08** | Usar **SG 5 %** sin aprobación del producto y contenedor | Bloquear por diluyente fuera del protocolo seleccionado NaCl 0,9 %. |
| **NEG-09** | Bolsa nominal 100 mL más 1 mL de fármaco sin validar sobrellenado/volumen final | Bloquear y exigir preparación exacta certificada por Farmacia. |
| **NEG-10** | Proponer **0,5 mg/50 mL** por simple equivalencia aritmética | Bloquear hasta autorización específica de producto, jeringa, estabilidad y bomba. |
| **NEG-11** | Se desconoce presentación/SKU, equivalencia base-sal o compatibilidad | Bloquear preparación electrónica, no inferir propiedades de otro fabricante. |
| **NEG-12** | Bomba, vía exclusiva, monitorización ECG/SpO2/PA o profesional competente ausentes | No habilitar orden electrónica del contrato; activar ayuda experta. |
| **NEG-13** | Confusión por ×100: ampolla IM 1 mg/mL seleccionada directamente como concentración de bolsa de 10 µg/mL | Rechazo dimensional y alerta roja; no programar bomba. |
| **NEG-14** | Aplicación dispara perfusión al registrar segunda dosis IM sin decisión médica | Prohibir toda acción automática, solo alerta/solicitud de revisión experta. |
| **NEG-15** | Mezcla caducada según **límite real firmado** | Bloquear validación; no prolongar ni acelerar para terminar la mezcla. |
| **NEG-16** | Descarga/exportación genera mL/h u orden pese a \`BLOCKED\` | Rechazar exportación y registrar \`CLINICALLY_PENDING\` |
| **NEG-17** | Falla de conexión, datos incompletos o revisión de protocolo obsoleta | Degradar a estado seguro; sin receta ni confirmación falsa de PASS |
| **NEG-18** | Presión arterial elevada, arritmia o sospecha de extravasación | Alertar STOP y requerir intervención inmediata especializada; nunca ajustar dosis en automático |
| **NEG-19** | Se pretende usar el contrato **adult** para cálculo pediátrico sin ampliar el selector | Rechazar por alcance no validado |
| **NEG-20** | Estado de farmacia/enfermería \`NOT_VERIFIED\` pero código intenta marcar \`GREEN\` y \`runtime_enabled=true\` | Rechazo del cambio de estado y control de release |

### Aceptación y evidencias necesarias

**Trazabilidad de cada NEG**: entradas sintéticas versionadas, resultado obtenido, motivo de bloqueo, salida segura, interfaz, evento de auditoría, SHA del código/protocolo, responsable de ejecución, fecha y estado. Registrar resultados como \`PASS/FAIL/NOT_RUN\` después de ejecutarlos realmente; pruebas de especificación \`NOT_RUN\` por defecto.

**Antes de solicitar desbloqueo:**
1. **Farmacia**: identificación portuguesa del producto real; compatibilidad NaCl, contenedor, volumen final medido y estabilidad/caducidad **firmadas**; decidir si se permite SG 5 %, 50 mL o fotoprotección obligatoria.
2. **UCI/Pediatría/Urgencias y Enfermería**: criterios de refractariedad y excepciones clínicas, límites de bomba, venoclisis/circuito, monitorización, extravasación y disponibilidad del rescate, aprobados.
3. **Desarrollo**: contrato **pediátrico** identificado, separado del original adulto, con validación de concentración/unidades/vía, cálculo revisable, sin recetas fuera del circuito aprobado; pruebas unitarias, E2E, exportaciones y 18 bloqueos restantes.
4. **Calidad**: ejecutar **20/20 NEG en entorno de integración**, sin falsos PASS; comprobar integridad de \`main\`, cuatro P1, 19 bloqueos y \`CLINICALLY_PENDING\`. Evaluación clínica humana posterior sobre versión final.
5. **Decisión formal y fecha**: acta final con firmas/verificaciones de Farmacia, Enfermería, Dirección Clínica y QA, revisión independiente, fuente y SHA exacto. **No se levanta \`block_reason\` ni se promueve YELLOW→GREEN automáticamente.**

**Dictamen actual:** documento y batería definidos; \`ANAPHYLAXIS_REFRACTORY_PEDIATRIC\` = **PROPOSED / BLOCKED**; contrato 4 **BLOCKED**; pruebas NEG **NOT_RUN**; sin cambios en cálculo clínico, API, stock, \`main\`, RC1/v1.43 o \`CLINICALLY_PENDING\`.
