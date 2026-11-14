# Delirium, abstinencia y alteración de conciencia — revisión · 14/11/2026

**58 GREEN /73 YELLOW /0 RED.** Tres referencias adultas revisadas/aceptadas en el flujo autorizado por el propietario. La solicitud repetida de alteración de conciencia corresponde a una sola revisión.

| Área | Resultado |
|---|---|
| Delirium | Detección, precipitantes, tratamiento de causas y límites farmacológicos por contexto. |
| Abstinencia | Regímenes supervisados, tiamina por fase y escalada. |
| Conciencia | Causas reversibles/estructurales, imagen selectiva, rescate y destino. |

Se corrige la rutina4AT: ejecución fallida/rechazo y prueba imposible tienen categorías distintas. Se rechazan cantidades negativas, fraccionarias o fuera de rango. Los resultados siguen sujetos a valoración clínica; no se promociona el catálogo global de escalas ni se afirma una nueva interfaz desplegada.

Las diferencias NICE/PADIS se mantienen explícitas. El esquema de tiamina elegido procede del documento UK más reciente y no se mezcla con la alternativa preventiva de ASAM. Los preparados parenterales precisan verificación individual de producto/dilución/tiempo; no se inventa una preparación local.

Sin nuevas firmas profesionales o disponibilidad hospitalaria atribuida. Se conservan19 contratos farmacológicos bloqueados y CLINICALLY_PENDING global.

## Fuentes

### delirium

- [NICE CG103](https://www.nice.org.uk/guidance/cg103/chapter/Recommendations) — Published2010; assessment update2023-01-18; checked2026-11-14. Official indexed recommendation text and PDF excerpts; direct overview403. No new2026 edition claimed.
- [4AT developer user guide](https://www.the4at.com/userguide) — Current official scoring guide. Official guide full text retrieved.
- [ICU Delirium and Cognitive Impairment Study Group monitoring resources](https://www.icudelirium.org/medical-professionals/delirium/monitoring-delirium-in-the-icu) — Current CAM-ICU/ICDSC resources; training manual2016 and flowsheet2023 listed. Official page retrieved; linked CDN manual/flowsheet downloads failed, not claimed fully read.
- [MHRA haloperidol delirium safety reminder](https://www.gov.uk/drug-safety-update/haloperidol-haldol-reminder-of-risks-when-used-in-elderly-patients-for-the-acute-treatment-of-delirium) — 2021-12-10; current official safety page. Official safety communication retrieved.
- [SCCM PADIS focused update](https://sccm.org/clinical-resources/guidelines/guidelines/focused-update-padis-guideline) — 2025-02-20. Official recommendation page retrieved.
- [CIMA haloperidol product contraindications](https://cima.aemps.es/cima/dochtml/ft/58345/FichaTecnica_58345.html) — Current retrieved product information. Official indexed SmPC text retrieved.

### alcohol-withdrawal

- [ASAM alcohol withdrawal management](https://www.asam.org/docs/default-source/quality-science/the_asam_clinical_practice_guideline_on_alcohol-1.pdf) — 2020; current official guideline listing. Official PDF and relevant recommendations retrieved.
- [UK DHSC alcohol treatment chapter10](https://www.gov.uk/guidance/clinical-guidelines-for-alcohol-treatment/10-pharmacological-interventions) — Published2025; current manual updated2026. Official current chapter retrieved.
- [UK DHSC alcohol treatment chapter16](https://www.gov.uk/guidance/clinical-guidelines-for-alcohol-treatment/16-alcohol-care-in-acute-hospitals) — Published2025-11-28; updated2026-04-17. Official current chapter and relevant dose sections retrieved.

### altered-consciousness

- [ACR Altered Mental Status, Coma, Delirium and Psychosis](https://acsearch.acr.org/docs/3102409/Narrative/) — 2024 update; DOI10.1016/j.jacr.2024.08.018. Official indexed variants/summary and primary publication abstract retrieved; direct narrative/PDF403.
- [AHA adult and pediatric special circumstances of resuscitation](https://cpr.heart.org/en/resuscitation-science/cpr-and-ecc-guidelines/adult-and-pediatric-special-circumstances-of-resuscitation/) — 2025. Official recommendation tables and supporting text retrieved.
- [ASAM glucose/thiamine timing](https://www.asam.org/docs/default-source/quality-science/the_asam_clinical_practice_guideline_on_alcohol-1.pdf) — 2020 recommendationV.7. Official exact recommendation retrieved.

## QA

QA PASS:622/622 Python,434/434 frontend,4/4 generación y7/7 comprobaciones globales. Integridad131/131; catálogo220 fuentes normalizado y auditoría sin errores. Cinco pruebas específicas nuevas verifican el cambio4AT y las tres guías.

Una aserción inicial exigía el texto de una barrera heredada de abstinencia; se conservó antes del PASS completo. Tras condensar redacción sin cambiar dosis/reglas se repitieron421 pruebas principales,5 específicas y4 de generación, todas PASS. No se ha ejecutado una nueva prueba de navegador.

Registro: `DELIRIUM_WITHDRAWAL_CONSCIOUSNESS_QA_2026-11-14.json`.

Datos: `DELIRIUM_WITHDRAWAL_CONSCIOUSNESS_REVIEW_2026-11-14.json`.
