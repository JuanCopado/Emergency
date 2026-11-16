# Reversión: revisión focal de los 15 contratos pendientes

Fecha de comprobación e implementación: **16 de noviembre de 2026**.

Esta referencia acompaña a `scripts/acute_reviewed_reversal.py`. La autorización del propietario permite sustituir los bloqueos administrativos de estos 15 contratos por cálculos específicos y decisiones clínicas ejecutables. No documenta una firma de Farmacia independiente, una revisión prospectiva de resultados clínicos ni una revisión de los 131 módulos. El estado clínico general del catálogo permanece separado del estado de implementación.

## Alcance y criterios de salida

Los identificadores existentes se conservan. Tres rutas pueden devolver una dosis: PCC AVK con el perfil Octaplex UK especificado, protamina para dalteparina/Fragmin identificada y segunda tanda justificada de idarucizumab. PCC y otras HBPM también ofrecen un modo de decisión cuando no se ha seleccionado esa pauta concreta. Los otros doce contratos son apoyo de decisión especializado.

Una salida `decision_support` lleva `dose`, `dose_unit`, volumen administrado, volumen extraído y `pump_ml_h` nulos. Incluye la decisión, condiciones y siguientes acciones. Una pauta descrita como opción contextual en el texto no se convierte en una orden calculada. Los campos de los modos numéricos son condicionales; elegir otro producto no obliga a inventar peso, INR ni dosis. La ausencia de recursos puede activar escalada o traslado sin impedir leer las acciones.

Las rutas revisadas son **adultas**. No se trasladan a pediatría por peso. El núcleo clínico es internacional: gravedad, agente, tiempo, actividad residual, foco, función orgánica, tratamiento previo y capacidad de monitorización. Una tabla de producto conserva su ámbito regulatorio; no se exige un hospital concreto y tampoco se presenta una ficha británica como si fuera portuguesa.

## Decisión implementada por contrato

| Contrato | Resultado habilitado y límites clínicos | Fuentes |
|---|---|---|
| `reversal-vka-pcc` | Cálculo solo con Octaplex y ficha UK aplicable, AVK confirmado, corrección urgente, INR ≥2, peso, presentación y contraindicaciones comprobados, plan de vitamina K y sin PCC previo. Otros perfiles devuelven selección de producto; no se mezclan tablas. | OCTAPLEX_UK_2024; C05_PRIOR_2026 |
| `reversal-superwarfarin` | Hemorragia crítica: hemostasia y toxicología en paralelo. INR inicialmente normal: seguimiento de toxicidad tardía, sin vitamina K profiláctica automática. Coagulopatía: tratamiento individualizado y continuidad de controles. | CDC_BRODIFACOUM_2022; CAPQ_VITAMIN_K |
| `reversal-edoxaban` | Identificación, actividad residual y gravedad; selección de PCC y pauta completos. Distingue la ficha del fármaco y el contexto de trauma. No genera un techo de PCC inexistente ni usa INR para calcular DOAC. | EDOXABAN_EMA; TRAUMA_2023; NCS_2026 |
| `reversal-betrixaban` | Identificar exposición, actividad y aclaramiento; soporte, fuente actual aplicable y estrategia especializada. No aplica automáticamente autorización o dosis de otro anti-Xa. | BETRIXABAN_FDA_2017; NCS_2026 |
| `reversal-fondaparinux` | Distingue dosis terapéutica, profilaxis y bioacumulación. Si un ensayo fiable excluye actividad relevante, dirige a otra causa sin reversión empírica. No protamina. Las opciones no específicas descritas para HIC no se trasladan a todo sangrado. | FONDAPARINUX_LABEL; NCS_2016 |
| `reversal-other-lmwh` | Cálculo de protamina solo para dalteparina/Fragmin, dosis en UI anti-Xa confirmada, actividad relevante y hemorragia crítica. Otras HBPM: identificar producto, unidades, tiempo y pauta propia. No repetir protamina por programación. | FRAGMIN_SMPC; PROTAMINE_LABEL |
| `reversal-enoxaparin-over12` | Más de 12 h, sin efecto relevante ni sangrado persistente: normalmente no protamina. Actividad residual, insuficiencia renal o sangrado persistente: reevaluación individual; el reloj no excluye acumulación. | CLEXANE_SMPC |
| `reversal-argatroban` | Suspensión cuando corresponde, control del foco y aPTT seriado; especial atención al aclaramiento hepático. No calcula un antídoto inexistente en la ficha consultada. | ARGATROBAN_FDA_2026 |
| `reversal-bivalirudin` | Suspensión, soporte, coagulación y función renal. Posible depuración requiere decisión especializada; no es una orden automática de diálisis. | BIVALIRUDIN_LABEL |
| `reversal-other-dti` | Dirige dabigatrán, argatrobán y bivalirudina a sus rutas; para otra molécula exige identificación y ficha/estrategia propia. Idarucizumab no se extrapola a toda la clase. | NCS_2016; PRAXBIND_SMPC |
| `reversal-danaparoid` | Suspensión, foco, aclaramiento y anti-Xa apropiado. La ficha no recomienda protamina; soporte o plasmaféresis seleccionados clínicamente. | DANAPAROID_SMPC; NCS_2016 |
| `reversal-fibrinolytics` | Diferencia HIC sintomática ≤24 h y agente/indicación. AHA/ASA 2026 para alteplasa/tenecteplasa por ictus; NCS 2016 para la otra pauta contextual. No convierte unidades transfusionales en mL ni mezcla regímenes antifibrinolíticos. | AHA_AIS_2026; NCS_2016 |
| `reversal-antiplatelets` | Decisión por HIC espontánea intraparenquimatosa, trauma, aspirina y neurocirugía. Conserva incertidumbre donde la actualización 2026 no pudo recomendar. Distingue reversión farmacológica de otra indicación transfusional. | NCS_2026 |
| `reversal-unknown` | Estabilización, recuperación de exposición y selección de pruebas; escalada sin exigir agente, vía ni última dosis inventados. No emite un cóctel empírico de antídotos. | NCS_2016; TRAUMA_2023 |
| `reversal-dabigatran-repeat` | Segunda tanda de 5 g solo tras una primera completa, criterio regulatorio de repetición y prolongación pertinente de aPTT/dTT/ECT. Excluye primera/tercera tanda, INR aislado y repetición rutinaria. | PRAXBIND_SMPC |

## Modelos numéricos y diferencias materiales

### AVK: perfil Octaplex UK, sin mezclarlo con Portugal

Se codifica la tabla de la ficha del fabricante publicada en emc, actualizada el **16-10-2024**, apartados 2, 4.2 y 4.3:

| INR previo | Coeficiente | Peso usado | Máximo de esta dosis |
|---|---:|---:|---:|
| 2 a <4 | 25 UI/kg | Menor de peso real y 100 kg | 2500 UI |
| 4 a 6, ambos incluidos | 35 UI/kg | Menor de peso real y 100 kg | 3500 UI |
| >6 | 50 UI/kg | Menor de peso real y 100 kg | 5000 UI |

Unidades expresadas como factor IX. Las dos presentaciones verificadas son 500 UI/20 mL y 1000 UI/40 mL, ambas 25 UI/mL después de reconstitución. Se calcula dosis/25 para volumen del producto; no se redondea por viales ni se programa bomba. La ficha limita velocidad a 0,12 mL/kg/min, máximo 8 mL/min. INR <2 queda fuera de esta tabla y necesita selección de otra pauta justificada, especialmente en HIC; el algoritmo no lo redondea a 2.

Ejemplo manual: INR 4 y 70 kg → 35 ×70 = **2450 UI** → 2450/25 = **98 mL**. Peso 150 kg e INR 6,1 → 50 ×100 = **5000 UI**.

La revisión anterior C05 preserva una discrepancia real: el RCM portugués de agosto de 2020 usa bandas en mL/kg y un máximo de 3000 UI; los intervalos locales aportados no coincidían exactamente con el documento. El modo portugués conserva una decisión pendiente de selección de dosis/ficha, sin importar el máximo o la tabla UK ni elegir el punto medio de una banda. Se resuelve el acceso al flujo clínico, no esa discrepancia documental mediante una equivalencia ficticia.

### Dalteparina/Fragmin: protamina específica

El apartado 4.9 de Fragmin relaciona **1 mg de protamina con 100 UI anti-Xa de dalteparina**. Esta administración inicial se limita a **50 mg administrados durante al menos 10 minutos**, conforme a la etiqueta de protamina Fresenius Kabi/DailyMed; si el producto real exige una velocidad más lenta se conserva esa restricción. El cálculo usa `min(UI anti-Xa relevantes /100, 50)`; exige que el clínico haya comprobado dosis reciente a neutralizar, tiempo, actividad, producto y ausencia de una dosis previa de protamina en ese episodio. No se interpreta una dosis en mg como si fueran UI anti-Xa. El límite no se presenta como dosis acumulada máxima de todo el tratamiento ni cierra otra discrepancia de un perfil que exija estrictamente menos de 5 mg/min.

Se conserva la neutralización anti-Xa incompleta descrita para este producto (aproximadamente 25–50%) y vigilancia de hipotensión/anafilaxia. No se calcula volumen sin la concentración real ni se automatiza repetición. No se usa esta fórmula para enoxaparina, otra HBPM o danaparoide.

### Idarucizumab: solo segunda tanda

Praxbind, apartado 4.2: puede considerarse otra tanda de **5 g** ante reaparición de sangrado clínicamente relevante, riesgo de resangrado vital o segunda cirugía/procedimiento urgente, **con prolongación pertinente de aPTT, dTT o ECT**. Son dos administraciones consecutivas de 2,5 g/50 mL; cada perfusión dura 5–10 minutos, o se emplean bolos consecutivos conforme al producto. El contrato exige exactamente una tanda completa previa. La dosis diaria máxima no está estudiada; no se autoriza una tercera por repetición automática.

### Pautas que deben mantenerse separadas

**Edoxabán:** la ficha de Lixiana contempla PCC de cuatro factores **50 UI/kg** para sangrado vital no controlado con hemostasia/transfusión. La guía europea de trauma 2023 recoge **25–50 UI/kg** y sugiere inicialmente 25 UI/kg en ese contexto. El flujo exige decidir el régimen entero; no mezcla la dosis del fármaco con un techo de AVK ni presenta ambas como una misma pauta universal. Tampoco convierte la espera de un resultado de laboratorio o del fracaso secuencial de medidas en un requisito para estabilizar una hemorragia crítica.

**Fibrinólisis:** AHA/ASA 2026, tabla 5, se aplica a HIC sintomática dentro de las 24 h posteriores a alteplasa/tenecteplasa por ictus adulto. Incluye crioprecipitado inicial 10 U en 10–30 min y objetivo de fibrinógeno ≥150 mg/dL; si el componente no puede usarse a tiempo, describe TXA 1000 mg IV en 10 min. El algoritmo identifica esta pauta. La alternativa NCS/SCCM 2016 de TXA 10–15 mg/kg en 20 min se mantiene como régimen contextual diferente; no se fusionan dosis y duración. La identidad/equivalencia del componente transfusional debe confirmarse antes de una orden numérica.

**Antiagregantes:** se usa la actualización NCS/SCCM publicada el **24-09-2026**. Para HIC intraparenquimatosa espontánea sin neurocirugía sugiere evitar plaquetas para reversión de antiagregación; en aspirina con cirugía sugiere transfundir. No pudo recomendar plaquetas en HIC traumática ni desmopresina para este fin. Estas incertidumbres no se convierten en dosis automáticas. Una indicación transfusional independiente, como trombocitopenia relevante, se evalúa por separado.

## Fuentes primarias, versión y sección

Todas se consultaron para esta revisión el 16-11-2026. Cuando el recurso no muestra una fecha inequívoca de revisión en el contenido recuperado, se registra la fecha de consulta sin atribuirle una actualización inexistente.

| ID | Fuente y versión comprobable | Sección que respalda la implementación |
|---|---|---|
| OCTAPLEX_UK_2024 | [Octaplex, ficha del fabricante/emc UK, actualización 16-10-2024](https://www.medicines.org.uk/emc/product/6566/smpc) | 2: unidades/concentración; 4.2: INR/peso/techo y velocidad; 4.3–4.4: heparina/HIT, IgA, reacciones y riesgo trombótico. |
| C05_PRIOR_2026 | [RCM Octaplex Portugal, agosto 2020, fabricante](https://www.octapharma.pt/api/download/x/291a94e4c6/rcm-octaplex.pdf); revisión de proyecto C05 de 16-11-2026 | Tabla portuguesa histórica y conflicto de equivalencia. No se afirma que el PDF histórico sea por sí mismo la última autorización portuguesa. |
| PRAXBIND_SMPC | [Praxbind, ficha del fabricante/emc UK](https://www.medicines.org.uk/emc/product/5073/smpc); [información regulatoria EMA](https://www.ema.europa.eu/en/documents/product-information/praxbind-epar-product-information_en.pdf) | 4.1–4.2: población, indicaciones, repetición y administración; 4.4: riesgos, rebote y valoración de hipersensibilidad/fructosa. La lectura posterior del PDF EMA devolvió límite 429; se contrastó con la ficha emc, sin afirmar una descarga nueva exitosa. |
| EDOXABAN_EMA | [Lixiana, información de producto EMA](https://www.ema.europa.eu/en/documents/product-information/lixiana-epar-product-information_en.pdf); [ficha del fabricante/emc](https://www.medicines.org.uk/emc/product/6907/smpc) | 4.9: hemorragia, PCC 50 UI/kg y ausencia de un máximo universal de PCC en esa recomendación. Portal EMA: actualización de información del producto 27-08-2025. |
| TRAUMA_2023 | [Guía europea de hemorragia y coagulopatía en trauma, sexta edición, 2023](https://doi.org/10.1186/s13054-023-04327-7) | Recomendaciones 34–35 y justificación: ensayos calibrados y opciones por agente; régimen de PCC en trauma. |
| NCS_2026 | [NCS/SCCM, actualización focal, publicada 24-09-2026](https://link.springer.com/article/10.1007/s12028-026-02601-4) | Recomendaciones PICO 1–3 y tablas 1–2. La tabla 2 reproduce recomendaciones de 2016 no reevaluadas en esta actualización; no se etiquetan como nuevas de 2026. |
| NCS_2016 | [NCS/SCCM, resumen ejecutivo, 2016](https://doi.org/10.1097/CCM.0000000000002057); [registro PubMed](https://pubmed.ncbi.nlm.nih.gov/26714677/) | Pentasacáridos, otros DTI, HBPM/danaparoide y fibrinolíticos en HIC. Evidencia limitada; el código acota indicación y no las convierte en fórmulas universales. |
| AHA_AIS_2026 | [AHA/ASA, guía de ictus isquémico agudo, publicada 26-01-2026](https://www.ahajournals.org/doi/10.1161/STR.0000000000000513) | Tabla 5: HIC sintomática dentro de 24 h de alteplasa/tenecteplasa en adultos tratados por ictus. |
| FRAGMIN_SMPC | [Fragmin 7500 UI/0,3 mL, ficha del fabricante/emc](https://www.medicines.org.uk/emc/product/4248/smpc) | 4.9: relación 1 mg/100 UI anti-Xa, administración lenta y neutralización parcial. |
| PROTAMINE_LABEL | [Protamine sulfate injection USP, Fresenius Kabi, etiqueta DailyMed](https://www.dailymed.nlm.nih.gov/dailymed/fda/fdaDrugXsl.cfm?setid=e1964129-33f4-4e4e-86e3-8e6a4e65bd83&type=display) | Dosage and Administration; Warnings: IV muy lenta durante 10 min, dosis no superior a 50 mg y riesgo de reacciones graves. El enlace Pfizer 4316 inicialmente consultado pertenece a heparina y contiene información de reversión; no se usa como identidad de una ficha de protamina. |
| CLEXANE_SMPC | [Clexane Forte, ficha del fabricante/emc](https://www.medicines.org.uk/emc/product/1695/smpc) | 4.9: tiempo desde enoxaparina, posibilidad de no precisar protamina >12 h y neutralización anti-Xa incompleta. |
| ARGATROBAN_FDA_2026 | [Argatroban, FDA, etiqueta 2026/022434s014](https://www.accessdata.fda.gov/drugsatfda_docs/label/2026/022434s014lbl.pdf) | 10: sobredosis, suspensión y ausencia de antídoto; recuperación de coagulación y prolongación por disfunción hepática. |
| BIVALIRUDIN_LABEL | [Bivalirudin, etiqueta DailyMed, SPL 15-04-2025](https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=50975be1-6d1f-497c-b989-1825a0fae1a7) | 8.6, 10 y 12.3: insuficiencia renal, suspensión por sobredosis, ausencia de antídoto y dializabilidad. |
| FONDAPARINUX_LABEL | [Fondaparinux, etiqueta DailyMed](https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=d3b30c68-cf45-4b46-8ba6-72090f7ba01a) | 10: suspensión y soporte ante sobredosis; no existe antídoto conocido en la ficha consultada. |
| DANAPAROID_SMPC | [Danaparoid sodium, ficha del fabricante/emc](https://www.medicines.org.uk/emc/product/13201/smpc) | 4.9: soporte, posible plasmaféresis en sangrado no controlado y ausencia de recomendación de protamina. |
| BETRIXABAN_FDA_2017 | [Bevyxxa, FDA, etiqueta original revisada 06-2017](https://www.accessdata.fda.gov/drugsatfda_docs/label/2017/208383s000lbl.pdf) | 5.1 y 10: efecto prolongado y ausencia de pauta específica de reversión establecida. Fuente histórica, no prueba de comercialización actual ni de autorización universal de un reversor. |
| CDC_BRODIFACOUM_2022 | [CDC/MMWR, brodifacoum y coagulopatía, 2022](https://www.cdc.gov/mmwr/volumes/71/wr/mm7140a5.htm) | Experiencia de exposición y necesidad de tratamiento/seguimiento prolongado; no se deriva una dosis universal de una serie de intoxicaciones. |
| CAPQ_VITAMIN_K | [Centre antipoison du Québec, vitamina K1](https://www.ciusss-capitalenationale.gouv.qc.ca/en/antidotes/vitamin-k1) | Selección según INR/sangrado, evitar profilaxis indiscriminada y coordinación toxicológica. |

## Trabajo previo recuperado y preservado

Base de integración: `062d890b4fc92369b83c87664bb4bb0205ccb33f`. Se inspeccionó la rama previa `review/reversal-vka-pcc-c05-20261116`, revisión `3402646b340c8f2ad4e4b1fc2cb19ba902eb2791`, incluidos:

- `clinical/qa/C05_VKA_PCC_CLINICAL_PHARMACY_RECONCILIATION_2026-11-16.md`.
- `clinical/qa/C05_OCTAPLEX_PORTUGAL_RCM_CONFLICT_2026-11-16.md`.
- `clinical/scripts/octaplex_pt_c05_preflight.py` y su diseño de controles de seguridad.
- `clinical/qa/REVERSAL_GENERIC_PCC_OWNER_ACCEPTANCE_2026-11-13.md`.

Esos documentos ya distinguían tablas y presentaciones, pero el preflight no calculaba dosis y seguía devolviendo bloqueo. Sus pruebas previamente declaradas `NOT_RUN` no se reclasifican como ejecutadas. Esta implementación añade un perfil numérico verificado y mantiene explícita la limitación portuguesa. No altera esos originales ni fabrica una aceptación de terceros.

Las pautas existentes de protamina para heparina no fraccionada y enoxaparina permanecen fuera de estos tres archivos. La nueva ruta de otras HBPM añade la pauta específica de dalteparina y la de >12 h aporta decisiones para actividad residual; no demuestra por sí misma la corrección de todas las ramas previas.

## Verificación focal y límites

`clinical/tests/test_acute_reviewed_reversal.py` contiene **15 ejemplos completos con expectativas calculadas manualmente**, reutilizables por la revisión independiente de API/navegador. La ejecución focal final pasó **24 pruebas**: identificadores, ausencia de campos activos, fronteras de INR y peso, techo de protamina, concordancia de producto, segunda tanda de idarucizumab, funciones de decisión sin dosis, escalada por recursos, ausencia fiable de actividad de fondaparinux y separación de recomendaciones de 2016/2026.

Cinco de esas pruebas usan el validador real de API: los 15 ejemplos, datos ausentes, contraindicaciones/producto/repeticiones, tipos no válidos y frontera de 12 h, y cambio de modo con rechazo de campos numéricos residuales. Pasar estas pruebas técnicas no equivale a validación clínica prospectiva ni a confirmación de disponibilidad de productos. No se activa una señal GREEN global.
