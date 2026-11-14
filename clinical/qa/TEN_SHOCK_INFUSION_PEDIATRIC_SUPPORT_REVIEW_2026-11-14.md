# Shock, perfusiones y soporte pediátrico ·14/11/2026

**Diez revisados:8 GREEN de referencia y2 YELLOW. Global91 GREEN /40 YELLOW /0 RED.**

| Nº | Módulo | Resultado |
|---|---|---|
| 1 | Shock indiferenciado | 🟢 Referencia revisada |
| 2 | Shock pediátrico | 🟢 Referencia revisada |
| 3 | Perfusiones vasoactivas e inotrópicas | 🟡 Preparación pendiente |
| 4 | Sedoanalgesia continua en UCI | 🟡 Preparación pendiente |
| 5 | Medicamentos de urgencia pediátricos | 🟢 Referencia revisada |
| 6 | Fluidoterapia IV pediátrica | 🟢 Referencia revisada |
| 7 | Asma aguda pediátrica | 🟢 Referencia revisada |
| 8 | Vía aérea e intubación pediátrica | 🟢 Referencia revisada |
| 9 | Electrolitos pediátricos | 🟢 Referencia revisada |
| 10 | Transfusión y hemorragia pediátrica | 🟢 Referencia revisada |

Cambios aplicados: contexto y recursos en shock, distinción ERC/SSC, dosis de
adrenalina cuando se indica RCP, objetivo GINA2026 y SABA por gravedad, salino2,7%
frente a3%, fuente nominal de rocuronio, glucosa/insulina si hay hiponatremia,
máximo de carga de TXA y límites de peso/reloj transfusional. No se cambian
motores, contratos ni catálogos farmacológicos.

Los dos módulos de perfusión adulta siguen YELLOW: falta completar por producto
la preparación exacta, recipiente/equipo, compatibilidad, estabilidad
fisicoquímica y tiempo microbiológico de uso. La revisión de indicación y de
mL/h no permite certificar mezclas ni plazos de recambio. No se certifica firma
especialista/farmacéutica independiente o adopción local.

Alcance pediátrico: el GREEN del marco de medicamentos no revalida todas las
entradas de los catálogos. El marco de fluidos no promueve el módulo específico
de CAD ni su insulina. Los productos y capacidades locales siguen sujetos a
sus comprobaciones propias. CLINICALLY_PENDING global; navegador NO EJECUTADO.

QA PASS:664 Python,434 frontend,4/4 guías,7/7 checks;14 nuevas regresiones de seguridad y cálculo. 19 contratos bloqueados conservados. Detalle: `TEN_SHOCK_INFUSION_PEDIATRIC_SUPPORT_QA_2026-11-14.json`.

Fuentes primarias y acceso (detalle y alcance en el JSON compañero):

- [SSC adult2026](https://www.sccm.org/clinical-resources/guidelines/guidelines/surviving-sepsis-campaign-international-guidelines-for-management-of-sepsis-and-septic-shock-2026)
- [SSC children2026](https://www.sccm.org/clinical-resources/guidelines/guidelines/surviving-sepsis-campaign-international-guidelines-for-the-management-of-sepsis-and-septic-shock-in)
- [ERC Paediatric Life Support2025](https://www.erc.edu/media/03xnpjmj/gl2025-09-pls-e.pdf)
- [SCCM PADIS focused update2025](https://www.sccm.org/clinical-resources/guidelines/guidelines/focused-update-padis-guideline)
- [GINA Strategy Report2026, boxes12-4 and young-child acute treatment](https://ginasthma.org/wp-content/uploads/2026/05/GINA-2026-Strategy-Report-WMS.pdf)
- [GINA Summary Guide July2026, pp34–36](https://ginasthma.org/wp-content/uploads/2026/07/GINA-Summary-Guide-2026-WEB-WMS.pdf)
- [NICE NG29 current recommendations](https://www.nice.org.uk/guidance/ng29/chapter/Recommendations)
- [NICE CG84 current gastroenteritis guidance](https://www.nice.org.uk/guidance/cg84/chapter/Recommendations)
- [RCH Emergency airway management current](https://www.rch.org.au/clinicalguide/guideline_index/Emergency_airway_management/)
- [RCH Hyperkalaemia current](https://www.rch.org.au/clinicalguide/guideline_index/Hyperkalaemia/)
- [RCH Hypokalaemia current](https://www.rch.org.au/clinicalguide/guideline_index/Hypokalaemia/)
- [RCH Hypomagnesaemia current](https://www.rch.org.au/clinicalguide/guideline_index/Hypomagnesaemia/)
- [Calcium gluconate10% SmPC, product6264](https://www.medicines.org.uk/emc/product/6264/smpc)
- [RCH Blood product prescription current online; page notes older2016 underlying guidelines](https://www.rch.org.au/clinicalguide/guideline_index/Blood_product_prescription/)
- [RCH Intravenous fluids current](https://www.rch.org.au/clinicalguide/guideline_index/Intravenous_fluids/)
- [RCH Hypernatraemia current](https://www.rch.org.au/clinicalguide/guideline_index/Hypernatraemia/)
- [RCH Diabetic ketoacidosis current](https://www.rch.org.au/clinicalguide/guideline_index/Diabetic_Ketoacidosis/)

Limitación de acceso: no se obtuvo el PDF completo de17MB de GINA Strategy;
se contrastaron sus extractos primarios indexados y el Summary Guide oficial
completo. No se afirma auditoría íntegra de todas las monografías de perfusión,
conformidad DGS/INFARMED o nueva validación prospectiva.

Dos expectativas clínicas antiguas se corrigieron con fuentes actuales; se añadieron comprobaciones más específicas y no se retiraron pruebas. Se sincronizó la tabla de estados y se verificó la proyección de las131 guías.
