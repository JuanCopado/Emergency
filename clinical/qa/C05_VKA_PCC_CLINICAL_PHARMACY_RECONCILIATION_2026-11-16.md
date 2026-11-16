# EMERGENCY — CONTRATO 5/19 · REVERSIÓN URGENTE DE AVK: VITAMINA K + 4F-PCC
**Fecha:** 2026-11-16. **Contrato canónico:** \`reversal-vka-pcc\`. **Estado:** \`BLOCKED / CLINICAL_REVIEW_REQUIRED\`. **Ámbito de referencia:** adulto; no extrapolar a neonatos o pediatría. Documento independiente, no modifica código farmacológico ni permite emitir órdenes.

## 1. Identidad y bloqueo original
**Fuente verificada:** \`clinical/qa/V1.44_MEDICATION_PRODUCT_PROTOCOL_RECONCILIATION.json\`, snapshot \`761f42d9afc8a7b7202d18bb0fd506d721dd4e50\`, blob \`b0167196c22264583047d9d1a553a14bc62c1568\`.
- ID \`reversal-vka-pcc\`; categorías de bloqueo **A** producto local, **B** presentación/dosis, **D** administración y **H** selección clínica.
- Productos **candidatos pero NO stock validado**: \`BERIPLEX_500\`, \`BERIPLEX_1000\`, \`OCTAPLEX_500\`, \`OCTAPLEX_1000\`, \`KONAKION_ADULT\`.
- Preparaciones candidatas \`PREP_BERIPLEX\`, \`PREP_OCTAPLEX\`, \`PREP_KONAKION\`; todas \`BLOCKED\` y \`runtime_enabled=false\`.
- El campo de fuente de alto nivel del contrato original apunta genéricamente a **EMA Praxbind**: esa ficha es del reversor de dabigatrán, **NO es una fuente específica válida para dosis de PCC/AVK**. Este expediente añade fuentes pertinentes sin alterar la cita heredada hasta que se revise en integración.

## 2. Indicación y separación obligatoria de rutas clínicas
**Incluir**: hemorragia mayor/potencialmente mortal o en órgano crítico en persona tratada con AVK (p. ej., warfarina, acenocumarol/Sintrom), o intervención urgente con necesidad documentada de reversión rápida. Registrar agente AVK, gravedad, localización, última dosis si conocida, **INR cercano a la administración**, peso medido/confirmado, coagulopatía concurrente, función hepática, riesgo trombótico y posibilidad de control anatómico del sangrado. Suspender AVK y activar control del foco según necesidad. No retrasar la reanimación por la aplicación.
**Excluir del cálculo PCC general**: INR elevado aislado sin hemorragia grave, sangrado menor, corrección electiva no urgente; DOAC (dabigatrán, apixabán, rivaroxabán, edoxabán); sobredosis de superwarfarinas (contrato 6) y déficit congénito de factores sin especificación independiente.
**No mezclar**: cuadro de hemorragia intracerebral (HIC) con pauta general por INR del fabricante; la HIC con INR 1,3–1,9 requiere ruta diferenciada y revisión de posibles usos fuera de la tabla general.

## 3. Tabla de ficha técnica de PCC: SOLO fuente de referencia por producto
Tanto [Beriplex P/N SmPC](https://www.medicines.org.uk/emc/product/6236/smpc) como [Octaplex SmPC](https://www.medicines.org.uk/emc/product/6566/smpc) dan una tabla general con unidades **de factor IX** (no mL ni UI de heparina):

| INR inicial | Beriplex / Octaplex (UI de factor IX/kg) | Dosis única máxima con peso limitado a 100 kg | Aplicabilidad |
|---|---:|---:|---|
| **2,0 a 3,9** (Octaplex 2,0 a <4,0) | **25 UI/kg** | **2.500 UI** | Solo urgencia elegible y producto exacto validado |
| **4,0 a 6,0** | **35 UI/kg** | **3.500 UI** | Igual |
| **>6,0** | **50 UI/kg** | **5.000 UI** | Igual |
| **<2,0** | **SIN TABLA GENERAL DEL PRODUCTO** | No inferir | Necesita ruta clínica distinta si existe HIC |

La tabla **no es orden de administración**; se presenta para contraste y validación de producto local. La unidad UI/kg se refiere **a factor IX**; su equivalencia en **mL** depende de concentración exacta tras reconstitución y ficha del producto. Los productos candidatos registran 25 UI de factor IX/mL con disolventes suministrados (500 UI/20 mL; 1000 UI/40 mL), **pero no autoriza intercambiar marcas o sistemas de transferencia**. Nunca redondear automáticamente al vial ni pedir dosis extra para vaciar viales.

### HIC AVK: ruta específica ESO/EANS 2025
El [consenso experto ESO/EANS 2025 para hemorragia intracerebral espontánea](https://pmc.ncbi.nlm.nih.gov/articles/PMC12098356/) indica:
- **INR >=2,0:** **4F-PCC 30–50 UI/kg**, junto con **vitamina K intravenosa 10 mg**.
- **INR 1,3–1,9:** **4F-PCC 10 UI/kg**, junto con **vitamina K IV 10 mg**, según ese consenso experto.
- Se expresa incertidumbre sobre los efectos netos de PCC vs plasma en desenlaces clínicos por baja certeza. No confundir consenso con evidencia de alta calidad ni atribuir al fabricante las reglas 10 UI/kg para INR<2,0.
- **Nunca hacer un híbrido** del 10 UI/kg de HIC con tablas 25/35/50 de la ficha general. Las decisiones de indicación, umbral, peso, objetivo INR y producto requieren aprobación de hematología/neurocríticos.

### Vitamina K: evitar dosis universal
- La [ficha técnica UK de Konakion MM 10 mg/mL](https://www.medicines.org.uk/emc/product/9755/smpc) distingue hemorragia **mayor (5 mg IV)**, **potencialmente mortal (5–10 mg IV)** y situaciones menos graves, de modo que **10 mg IV no es una orden universal para cualquier INR elevado**. La ruta HIC ESO/EANS sí menciona 10 mg IV.
- A diferencia del PCC, la vitamina K tarda horas en hacer efecto; cuando hay reversión urgente grave puede ser necesaria **junto con** PCC para prevenir rebote.
- El etiquetado, modo de administración, mezcla/compatibilidad y presentación de vitamina K difieren entre marcas/jurisdicciones. La misma ficha UK contiene instrucciones que deben aclararse con el **RCM del producto portugués**; **no usar una dilución por defecto ni combinar automáticamente con otros inyectables**.
- **No administrar IM** a pacientes anticoagulados ni extrapolar ruta pediátrica; contraindicación y riesgo de hematoma según la ficha UK. Precaución con válvulas mecánicas y estrategia de re-anticoagulación.
- **No** incluir aquí el tratamiento prolongado de superwarfarinas, que corresponde al contrato 6.

## 4. Seguridad y diferencias entre productos
| Aspecto | Beriplex | Octaplex | Requisito de release |
|---|---|---|---|
| Composición | 4 factores II/VII/IX/X, proteínas C/S y heparina; componentes específicos del fabricante | 4 factores II/VII/IX/X, proteínas C/S y heparina | Confirmar presentación exacta, heparina, lote, ficha/RCM portugués |
| Contraindicaciones | Comprobar alergias y **HIT**, antecedentes trombóticos y otros factores del SmPC | La ficha UK explicita alergia a heparina/**HIT** e IgA con anticuerpos anti-IgA | Evaluación individual documentada; sin equivalencias automáticas |
| Reconstitución | Disolvente suministrado y dispositivo **Mix2Vial** según la ficha consultada | Disolvente suministrado y dispositivo **Nextaro** en ficha UK consultada; otras versiones/mercados pueden diferir | Verificar equipo realmente suministrado, no mezclar ni diluir arbitrariamente |
| Velocidad IV | Ficha UK: **no >8 mL/min**, y para determinados pesos referencia menor | Ficha UK: **0,12 mL/kg/min hasta 8 mL/min** | No convertir a bomba sin marca y producto validado |
| Estabilidad tras reconstitución | Estabilidad fisicoquímica demostrada **24 h <=25ºC**, pero **uso microbiológico inmediato** | Estabilidad fisicoquímica **8 h a 25ºC**, pero **uso microbiológico inmediato** | **No declarar 24 h de uso clínico universal; Farmacia fija plazo real** |
| Riesgos | Tromboembolismo, reacciones alérgicas, HIT según producto | Tromboembolismo, reacciones alérgicas, HIT según producto | Consentimiento/indicación y vigilancia según urgencia, producto y guías |

**Fuente de comparación:** [Beriplex SmPC UK](https://www.medicines.org.uk/emc/product/6236/smpc), [Octaplex SmPC UK](https://www.medicines.org.uk/emc/product/6566/smpc). Fuentes portuguesas secundarias (prospectos reproducidos) sugieren autorización de ambas marcas en Portugal, **pero NO acreditan inventario de Horta ni RCM vigente identificado**. La fuente de cada concentración, estabilidad y velocidad debe conservarse separada por producto y país.

## 5. Verificación y pruebas negativas propuestas — todas NOT_RUN
La [matriz estructurada C05](C05_VKA_PCC_NEGATIVE_CASES_2026-11-16.json) contiene 22 ensayos de seguridad contra indicación inapropiada, confusión de anticoagulante, límites de INR/peso, dosis y unidades, HIT, mezcla, velocidad, estabilidad, vitamina K, exportación y regresión de bloqueos. **Ninguno de esos 22 casos se ha ejecutado** en un motor clínico integrado; no atribuir PASS.

**Aceptación previa a cualquier desbloqueo:**
1. **Farmacia Horta:** nombre comercial exacto y SKU/lote de PCC activo (Beriplex/Octaplex/otro) y vitamina K, RCM portugués, contenido real en factor IX, reconstitución, velocidad, estabilidad, heparina/HIT y stock, firmados y fechados.
2. **Responsable de Urgencias/Hematología y, si HIC, neurocríticos:** protocolo nominal que diferencia hemorragia vital, cirugía urgente, INR aislado, HIC con INR 1,3–1,9, umbrales y dosis de vitamina K; criterios de control hemostático, INR objetivo y riesgo trombótico.
3. **Enfermería:** procedimiento por producto, reconstitución aséptica, doble chequeo, etiqueta de IU de factor IX frente a mL, infusión, monitorización y registro de lote.
4. **Desarrollo/QA:** contrato de selección por indicación y producto concreto, campos tipados para INR/peso, bloqueo de valores imposibles/unidades, pruebas adversariales y de exportación, auditoría de registros, preservación de otras 18 ramas BLOCKED y cuatro P1.
5. **Aprobación humana independiente** vinculada a SHA de código realmente probado. No cambiar \`CLINICALLY_PENDING\`, no promover GREEN ni eliminar \`block_reason\` por documentar la fuente.

**Dictamen:** conciliación bibliográfica **documentada**, sin aprobación local de producto ni validación funcional. \`reversal-vka-pcc\` **BLOCKED**. Sin cambios de \`main\`, RC1, v1.43, I02 o contratos anteriores.
