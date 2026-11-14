# TCE y ocho módulos pediátricos — revisión14/11/2026

Completada la actualización solicitada de TCE y, después, los ocho módulos
pediátricos. **100 GREEN /31 YELLOW /0 RED**. Los9 cambios YELLOW→GREEN son
revisiones de referencia autorizadas por el propietario; TCE adulto ya era GREEN.
No equivalen a firmas independientes ni validación clínica prospectiva.

| Módulo | Evidencia | Resultado de la conciliación |
|---|---|---|
| Sedación procedimental pediátrica | 🟢 | Máximos/concentración de fentanilo IN, capnografía/rescate/recuperación y seguridad nitroso |
| Soporte respiratorio agudo pediátrico | 🟢 | HFNO: deterioro no espera2h/4h; oxígeno y escalada por causa |
| Infecciones del SNC pediátricas | 🟢 | Vancomicina por edad/riñón; límite ceftriaxona0–2meses; dexametasona RCH4d |
| Toxicología pediátrica | 🟢 | Paracetamol: tiempo, formulaciones especiales, intensificación y volumen total |
| Cetoacidosis diabética pediátrica | 🟢 | Sin bolo; K/insulina/lesión cerebral; solapamiento30–60min solo rápida SC |
| Quemaduras pediátricas | 🟢 | Fórmula desde lesión, volumen previo y métodos de mantenimiento distintos |
| Sepsis pediátrica | 🟢 | SSC2026 y recursos; NICE/DGS por separado, sin mezclar dosis |
| Crisis suprarrenal pediátrica | 🟢 | Pauta RCH identificada; no esperar K>7 y ECG juntos; corrección Na |
| TCE pediátrico | 🟢 | Biomarcadores adultos no extrapolables; GCS<=8 y deterioro>=2; CBI-M |
| TCE adulto | 🟢 | Ensayos12/24h; falsos negativos; consenso PT2026 y CBI-M2026; Horta/urgencia conservados |

## TCE: decisiones de integración

- Conservados los criterios urgentes de TC, objetivos de perfusión, rescate y
  derivación neuroquirúrgica, con la capa Horta diferenciada.
- Biomarcadores por plataforma, matriz y tiempo; sin regla de alta automática.
  No se activa exclusión de TC pediátrica ni se trasladan umbrales de adultos.
- Añadidos CBI-M y la evaluación de octubre2026; no se implementa una predicción
  pronóstica individual. GCS no evaluable se documentaNT, sin suma ficticia.
- Consenso portugués julio2026 comparado, con su circuito diferenciado y acceso
  parcial declarado; no se infiere adopción del algoritmo íntegro por Horta.
- Anexo clínico: `../references/tbi-biomarkers-cbim-2026.md`.

## Límites y seguridad

El GREEN corresponde al contenido de referencia revisado. La revisión de
sedación no acredita equipos ni personal; la de toxicología no habilita un
catálogo universal de dosis de antídotos. Los registros de productos,
preparaciones y46 contratos (19 bloqueados) mantienen sus propias restricciones.

En sepsis se conservan atribuciones separadas SSC2026, NICE y DGS014/2018; no se
mezclan sus dosis de antibióticos ni sus condiciones de fluidoterapia/oxígeno.
La pauta endocrinológica seleccionada sigue RCH, sin mezclar sus grupos de edad
con otras tablas. En quemaduras, el cálculo inicial no contabiliza sueros ya
administrados y los métodos de mantenimiento no son matemáticamente idénticos.

Adjuntos originales preservados. Del texto extenso se analizaron las secciones
pertinentes; no se afirma auditoría íntegra. Los estudios/consenso con acceso a
resumen o extractos primarios se identifican así en el registro. No se afirma
conformidad DGS general, autorización INFARMED ni disponibilidad de un ensayo
local. **CLINICALLY_PENDING** global.

## Comprobaciones

**PASS:688 pruebas Python,434 frontend,4 guías y7 controles globales.** Diez
regresiones nuevas cubren falsos negativos/edad, TC urgente, GCS, sedación,
vancomicina infantil, tóxicos, CAD, quemaduras y escalada por recursos/ECG.
Dos expectativas históricas se corrigieron conforme a RCH; no se omitieron
pruebas fallidas.313 archivos protegidos idénticos; preámbulos y módulos ajenos
al alcance conservados. Sin comprobación nueva en navegador, merge ni push.

- Registro, fuentes y procedencia: `TBI_AND_EIGHT_PEDIATRIC_REVIEW_2026-11-14.json`.
- Resultado QA: `TBI_AND_EIGHT_PEDIATRIC_REVIEW_2026-11-14_QA.json`.

## Fuentes verificadas por módulo

- FDA i-STAT TBI whole blood K234143 — 2024 clearance; administrative correction2024-08-05: https://www.accessdata.fda.gov/cdrh_docs/pdf23/K234143.pdf
- FDA i-STAT TBI Plasma K201778 — 2021 clearance: https://www.accessdata.fda.gov/cdrh_docs/reviews/K201778.pdf
- Whole-blood point-of-care GFAP/UCH-L1 after TBI — 2026;61:101539: https://pubmed.ncbi.nlm.nih.gov/42746312/
- NIH-NINDS TBI classification CBI-M — 2025;24:512-523: https://pubmed.ncbi.nlm.nih.gov/40409315/
- CBI-M CENTER-TBI/TRACK-TBI evaluation — 2026-10-20: https://pubmed.ncbi.nlm.nih.gov/42899481/
- Mild TBI National Consensus Clinical Recommendations — 2026-07-20 ahead of print: https://www.actamedicaportuguesa.com/revista/index.php/amp/article/view/24437
- Age-dependent GFAP differences in children without TBI — 2024: https://www.neurology.org/doi/full/10.1212/WNL.0000000000209651
- Glasgow Coma Scale official FAQ — current online: https://www.glasgowcomascale.org/faq/
- Head injury — current online: https://www.rch.org.au/clinicalguide/guideline_index/Head_injury/
- Pediatric mild TBI guidance — 2025 online guidance: https://www.cdc.gov/traumatic-brain-injury/hcp/clinical-guidance/pediatric-mtbi.html
- Pediatric sedation monitoring and management — reaffirmed June2025; reference updates: https://www.aapd.org/globalassets/media/policies_guidelines/bp_monitoringsedation25.pdf
- Ketamine procedural sedation — current online: https://www.rch.org.au/clinicalguide/guideline_index/Ketamine_use_for_procedural_sedation/
- Intranasal fentanyl — current online: https://www.rch.org.au/clinicalguide/guideline_index/intranasal_fentanyl/
- Nitrous oxide oxygen mix — December2021 current online: https://www.rch.org.au/clinicalguide/guideline_index/Nitrous_Oxide_Oxygen_Mix/
- Paediatric life support — 2025: https://www.resus.org.uk/professional-library/2025-resuscitation-guidelines/paediatric-basic-life-support-guidelines
- High flow nasal prong therapy — current online: https://www.rch.org.au/rchcpg/hospital_clinical_guideline_index/High_flow_nasal_prong_%28HFNP%29_therapy/
- Meningitis and encephalitis — current online: https://www.rch.org.au/clinicalguide/guideline_index/Meningitis_encephalitis/
- Vancomycin — July2024 current online: https://www.rch.org.au/clinicalguide/guideline_index/Vancomycin/
- Paracetamol poisoning — current online: https://www.rch.org.au/clinicalguide/guideline_index/paracetamol_poisoning/
- Tricyclic antidepressant poisoning — current online: https://www.rch.org.au/clinicalguide/guideline_index/Tricyclic_Antidepressant_%28TCA%29_Poisoning/
- Diabetic ketoacidosis — July2025: https://www.rch.org.au/clinicalguide/guideline_index/Diabetic_ketoacidosis/
- Burns acute management — April2026: https://www.rch.org.au/clinicalguide/guideline_index/Burns/
- Burn fluid resuscitation — February2026: https://aci.health.nsw.gov.au/networks/burn-injury/resources/patient-management/fluid-resuscitation
- Transfer and retrieval of burn patients — November2026: https://aci.health.nsw.gov.au/__data/assets/pdf_file/0004/162634/ACI-Transfer-and-retrieval-of-burn-patients-cpg.pdf
- Pediatric sepsis and septic shock — 2026: https://www.sccm.org/clinical-resources/guidelines/guidelines/surviving-sepsis-campaign-international-guidelines-for-the-management-of-sepsis-and-septic-shock-in
- Suspected sepsis under16 NG254 — 2025; current PDF retrieved: https://www.nice.org.uk/guidance/ng254/resources/suspected-sepsis-in-under-16s-recognition-diagnosis-and-early-management-pdf-66144017065669
- PAI Febre de Curta Duracao em Idade Pediatrica014/2018 — 2018-08-03; targeted passages/index only: https://www.dgs.pt/directrizes-da-dgs/normas-e-circulares-normativas/norma-n-0142018-de-03082018-pdf.aspx
- Adrenal crisis and acute adrenal insufficiency — October2024: https://www.rch.org.au/clinicalguide/guideline_index/Adrenal_crisis_and_acute_adrenal_insufficiency/
- Hyperkalaemia — current online: https://www.rch.org.au/clinicalguide/guideline_index/Hyperkalaemia/
- Activated charcoal in poisonings — June2017 current online: https://www.rch.org.au/clinicalguide/guideline_index/Use_of_Activated_Charcoal_in_Poisonings/
- CPAP and NIV: acute-care boundary — current online; chronic-care scope plus acute PICU boundary: https://www.rch.org.au/rchcpg/hospital_clinical_guideline_index/Continuous_positive_airway_pressure_(CPAP)_and_non-invasive_ventilation_(NIV)/
