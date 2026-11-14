# Diez módulos pediátricos y adultos —14/11/2026

Revisión autorizada e integrada. **Los10 pasan de YELLOW a GREEN de referencia.**
Registro: **110 GREEN /21 YELLOW /0 RED**. Se conserva CLINICALLY_PENDING.

| Módulo | Evidencia | Conciliación |
|---|---|---|
| Abdomen quirúrgico pediátrico | 🟢 | Imagen negativa no excluye invaginación; cirugía y alta tras reducción |
| Trauma mayor pediátrico | 🟢 | Hemorragia: sangre/escalada; límite de carga TXA separado del tratamiento total |
| Emergencia hipertensiva pediátrica | 🟢 | Cálculo mL/h, máximos diarios, preparación y límite PCH labetalol |
| Cuerpos extraños pediátricos | 🟢 | TC de baja dosis seleccionada RCH septiembre2026; broncoscopia urgente prioritaria |
| Ahogamiento/hipotermia pediátricos | 🟢 | Pauta pediátrica ERC2025 y observación RCH diferenciadas |
| Hematología/oncología pediátricas | 🟢 | SSC2026 frente a pauta oncológica; G6PD, TLS y ajuste/TDM |
| Hemorragia digestiva alta | 🟢 | ESGE2026 y Baveno VIII; coágulo adherido y reinicio individualizado |
| Lesión renal aguda | 🟢 | KDIGO2012 publicado;2026 aún borrador; diálisis por complicaciones |
| Dermatología grave | 🟢 | SJS/NET frente a DRESS e infección necrotizante; oftalmología temprana |
| Complicaciones de dispositivos | 🟢 | HRS2026 extracción/infección; imán de DAI no corrige estimulación; LVAD |

## Alcance

GREEN significa revisión reciente del contenido de referencia. No acredita
firmas independientes, disponibilidad de laboratorio/endoscopia/TIPS/PICU ni
productos portugueses; tampoco exactitud diagnóstica prospectiva. No se cambian
los motores de cálculo ni las46 restricciones contractuales (19 bloqueadas).
La seguridad de cada preparación sigue dependiendo del producto dispensado.

Los cambios se proponen primero en la cola y se integran por la autorización
explícita del propietario. Se distinguen guías de consenso, borradores y versiones
publicadas. El consenso Baveno VIII, dispositivos y algunas guías se verificaron
mediante recomendaciones primarias indexadas: no se declara lectura integral de
sus artículos. La transición KDIGO2026 se mantiene vigilada, sin citarlo como final.

## QA

PASS:698 pruebas Python,434 frontend,4 guías y7 controles globales. Diez pruebas
nuevas cubren límites clínicos, unidades, máximos, edad/síndrome y rescate.
La expectativa histórica que prohibía TC se actualizó conforme a RCH septiembre2026,
añadiendo la prioridad de broncoscopia. No se suprimieron pruebas fallidas.
313 archivos protegidos conservados; preámbulos y secciones ajenas sin cambios.
Navegador nuevo:NO EJECUTADO. Sin merge ni push a ramas protegidas.

## Fuentes y trazabilidad

- pediatric-abdominal-surgical-emergencies: RCH Intussusception February2026 — https://www.rch.org.au/clinicalguide/guideline_index/Intussusception/
- pediatric-abdominal-surgical-emergencies: RCH acute scrotal pain2026 — https://www.rch.org.au/clinicalguide/guideline_index/Acute_scrotal_pain_or_swelling/
- pediatric-major-trauma: RCH Trauma primary survey current — https://www.rch.org.au/clinicalguide/guideline_index/Major_paediatric_trauma_the_primary_survey/
- pediatric-hypertensive-emergency: PCH Labetalol April2026 — https://www.pch.health.wa.gov.au/~/media/Files/Hospitals/PCH/General-documents/Health-professionals/MedicationMonographs/Labetalol.pdf
- pediatric-hypertensive-emergency: PCH Hydralazine October2025 — https://pch.health.wa.gov.au/~/media/Files/Hospitals/PCH/General-documents/Health-professionals/MedicationMonographs/Hydralazine.pdf
- pediatric-foreign-body-emergencies: RCH foreign body ingestion — https://www.rch.org.au/clinicalguide/guideline_index/Foreign_body_ingestion/
- pediatric-foreign-body-emergencies: ESPGHAN2026 foreign body position paper — https://onlinelibrary.wiley.com/doi/10.1002/jpn3.70485
- pediatric-foreign-body-emergencies: RCH inhaled foreign body — https://www.rch.org.au/clinicalguide/guideline_index/Foreign_bodies_inhaled.aspx
- pediatric-drowning-hypothermia: ERC/RCUK pediatric life support2025 — https://www.resus.org.uk/professional-library/2025-resuscitation-guidelines/paediatric-basic-life-support-guidelines
- pediatric-drowning-hypothermia: RCH drowning2020 current — https://www.rch.org.au/clinicalguide/guideline_index/Drowning/
- pediatric-hematology-oncology-emergencies: RCH febrile neutropenia current — https://www.rch.org.au/clinicalguide/guideline_index/febrile_neutropenia/
- pediatric-hematology-oncology-emergencies: RCH hyperleukocytosis October2025 — https://www.rch.org.au/clinicalguide/guideline_index/Oncological_emergencies__Hyperleukocytosis/
- upper-gi-bleeding: ESGE ulcer bleeding2026 primary recommendations — https://pubmed.ncbi.nlm.nih.gov/42127996/
- upper-gi-bleeding: Baveno VIII2026 primary panel5 indexed recommendations — https://www.journal-of-hepatology.eu/article/S0168-8278%2826%2902778-9/fulltext
- upper-gi-bleeding: ACG-CAG antithrombotics2022 — https://gi.org/wp-content/uploads/2022/03/ACG-CAG-Guideline.pdf
- aki-nephrology: KDIGO official AKI/AKD publication status — https://kdigo.org/guidelines/acute-kidney-injury/
- aki-nephrology: KDIGO published AKI2012 — https://kdigo.org/wp-content/uploads/2016/10/KDIGO-2012-AKI-Guideline-English.pdf
- dermatology-severe: S3 epidermal necrolysis2024 part1 — https://onlinelibrary.wiley.com/doi/full/10.1111/ddg.15515
- dermatology-severe: S3 epidermal necrolysis2024 part2 — https://onlinelibrary.wiley.com/doi/full/10.1111/ddg.15516
- dermatology-severe: Japanese SJS/TEN2025 supplement — https://onlinelibrary.wiley.com/doi/10.1111/1346-8138.70136
- dermatology-severe: International adult DRESS Delphi consensus — https://jamanetwork.com/journals/jamadermatology/fullarticle/2812063
- device-complications: HRS lead management/extraction2026 — https://www.heartrhythmjournal.com/article/S1547-5271%2826%2902264-2/fulltext
- device-complications: AHA CIED statement2024 — https://pmc.ncbi.nlm.nih.gov/articles/PMC12068544/
- device-complications: RCUK special circumstances2025 LVAD — https://www.resus.org.uk/professional-library/2025-resuscitation-guidelines/special-circumstances-guidelines

Detalle estructurado: `NEXT_TEN_PEDIATRIC_ADULT_REVIEW_2026-11-14.json`. Resultado: `NEXT_TEN_PEDIATRIC_ADULT_REVIEW_2026-11-14_QA.json`.
