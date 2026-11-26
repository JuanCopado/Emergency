# Corticoides sistémicos — referencia y comparación

Versión CORT-20261126 v2 · 26/11/2026. Ámbito existente: `medication-selection-safety`. No añade un módulo clínico ni cambia las 45 fórmulas de `calculators/registry.json`. Estado general: **CLINICALLY_PENDING**.

## Catálogo y uso

La fuente estructurada es [corticosteroids.json](../pharmacology/corticosteroids.json). La interfaz de consulta y comparación está en `/corticosteroids`. El generador `scripts/build_corticosteroid_catalog.py` proyecta literalmente el catálogo; `--check` detecta divergencias.

El comparador conserva la fuente seleccionada, medicamento de origen, cantidad en **mg**, vía sistémica oral/IV y tipo de cantidad (una dosis o total de 24 h). Calcula:

`cantidad destino = cantidad origen × equivalencia destino / equivalencia origen`

La equivalencia es una aproximación antiinflamatoria, no una selección de tratamiento, intervalo, duración, retirada o sustitución en crisis suprarrenal. No representa equivalencia mineralocorticoide. No convertir porcentajes de cremas, potencia tópica, inhaladores, colirios, formulaciones intraarticulares/depot, sales o concentraciones de producto. No convertir la pauta adulta a pediatría; el comparador no recibe edad, peso o superficie corporal ni genera mg/kg, mg/m² o mL.

## Dos fuentes separadas

[Endotext, actualización 19/10/2018, tabla 1](https://www.ncbi.nlm.nih.gov/sites/books/NBK279156/) y [ESE/Endocrine Society 2024, tabla 1, G28](https://academic.oup.com/ejendo/article-pdf/190/5/G25/57417666/lvae029.pdf) coinciden para hidrocortisona, cortisona, prednisona/prednisolona y metilprednisolona/triamcinolona. Difieren materialmente para dexametasona y betametasona, y en los rangos de semivida biológica. Sus valores completos permanecen separados en el catálogo y visibles en la interfaz; ninguna selección de idioma elige una tabla.

La actividad mineralocorticoide relativa procede exclusivamente de Endotext y se muestra con esa atribución incluso cuando se consulta la tabla ESE. No entra en la ecuación. Semivida biológica no equivale a semivida plasmática ni determina automáticamente la frecuencia de administración. No se promedian las dos tablas.

## Pautas cortas: Bell, asma, EPOC y crup

La sección `bell-palsy` pertenece al módulo existente `ent-emergencies`; el catálogo conserva ese vínculo. [AAO-HNSF 2013, aún enlazada por la sociedad en la consulta del 26/11/2026](https://pubmed.ncbi.nlm.nih.gov/24189771/) recomienda corticoides orales desde los 16 años si se inician dentro de 72 horas. La ficha usa una pauta completa del ensayo de [Sullivan et al., NEJM 2007](https://doi.org/10.1056/NEJMoa072006): **prednisolona 25 mg cada 12 horas durante 10 días**. No se combina con otros esquemas ni se obtiene del comparador. Para el borrador de esta aplicación, el ámbito adulto comienza a los 18 años; el acceso de 16–17 años es de referencia y decisión manual.

La presentación requiere diagnóstico clínico, protección ocular y valoración de causas alternativas. El patrón periférico o la afectación frontal no descartan por sí solos una lesión pontina: [serie primaria de Min y Jung, 2019](https://pmc.ncbi.nlm.nih.gov/articles/PMC6710861/). La sospecha de Ramsay Hunt, otitis/mastoiditis o [Lyme según exposición y signos clínicos](https://www.idsociety.org/practice-guideline/lyme-disease/) cambia el manejo. Los signos neurológicos u oculares nuevos obligan a reevaluar, y la recuperación incompleta a los 3 meses requiere derivación.

La ficha pediátrica no ofrece una dosis automática. [RCH, febrero 2023](https://www.rch.org.au/clinicalguide/guideline_index/Facial_weakness_and_Bells_palsy/) señala insuficiencia de evidencia y una transición incierta a la evidencia adulta. [BellPIC, Babl et al., Neurology 2022](https://pubmed.ncbi.nlm.nih.gov/36008143/) incluyó 187 menores de 18 años, sin demostrar beneficio en la recuperación completa al mes y sin precisión suficiente para excluir un beneficio o daño importante. Esa incertidumbre no se convierte en una contraindicación absoluta ni en una recomendación pediátrica rutinaria.

[ESE/Endocrine Society 2024, R2.1](https://www.endocrine.org/clinical-practice-guidelines/glucocorticoid-induced-adrenal-insufficiency) sugiere no reducir progresivamente una exposición sistémica verdaderamente corta, menor de 3–4 semanas. Revisar tratamiento previo, exposición acumulada y riesgo suprarrenal; no suspender por esta regla una sustitución o tratamiento crónico. La indicación concreta sigue determinando la duración.

Asma adulta (`acute-severe-asthma`), exacerbación de EPOC (`copd-exacerbation`), asma pediátrica (`pediatric-acute-asthma`) y crup (`croup`) se enlazan de forma explícita. Conservan sus propias pautas, criterios de gravedad, edad y selección del producto; no se duplican sus motores ni se genera un curso intercambiando potencias.

La actualización explicita también la banda de **12–17 años** dentro de asma pediátrica. [GINA 2026, Box 9-2](https://ginasthma.org/wp-content/uploads/2026/05/GINA-2026-Strategy-Report-WMS.pdf) identifica el curso habitual de prednisona/prednisolona en adolescentes como **40–50 mg/día durante 5–7 días** cuando está indicado un corticoide sistémico. Las bandas ≤5, 6–11 y 12–17 se mantienen diferenciadas; son alternativas y el médico selecciona la correspondiente al caso. Su presencia en la referencia no significa que el programa haya calculado o elegido una dosis individual.

## Hidrocortisona: indicaciones diferenciadas

### Adulto

- **Crisis suprarrenal:** conservar `adrenal-crisis` y su aceptación existente; la tarjeta reproduce sus cantidades y remite al módulo completo. Fuente: [Society for Endocrinology, Management summary](https://www.endocrinology.org/clinical-practice/clinical-guidance/adrenal-crisis/). La consulta de urgencia no espera confirmación bioquímica.
- **Shock séptico:** completar `sepsis-shock` con [SSC 2026, recomendación 79](https://sccm.org/clinical-resources/guidelines/guidelines/surviving-sepsis-campaign-international-guidelines-for-management-of-sepsis-and-septic-shock-2026). La recomendación de corticoides IV es condicional, con certeza baja. El régimen frecuente de hidrocortisona procede de [SCCM 2024, tabla 4](https://doi.org/10.1097/CCM.0000000000006172), sin convertirlo en pauta universal de sepsis ni fijar duración sin reevaluación.
- **Otros contextos:** mantener las pautas diferenciadas de `thyroid-storm` y `myxedema-coma`; para asma/EPOC, consultar sus módulos. La tabla de potencia no demuestra intercambiabilidad de todas las indicaciones.

### Pediatría

- **Crisis suprarrenal:** conservar la pauta RCH ya aceptada en `pediatric-adrenal-crisis`. Fuente [RCH/PIC, octubre 2024, Treatment → Severely unwell/in crisis](https://www.rch.org.au/clinicalguide/guideline_index/Adrenal_crisis_and_acute_adrenal_insufficiency/). Priorizar el plan individual. El catálogo reproduce las bandas de crisis, sin seleccionar una por edad. El apartado Surgery de la misma página tiene una frontera diferente a los 6 años; no mezclarlo.
- **Shock séptico:** [SSC pediátrica 2026, Corticosteroid](https://sccm.org/clinical-resources/guidelines/guidelines/surviving-sepsis-campaign-international-guidelines-for-the-management-of-sepsis-and-septic-shock-in) desaconseja hidrocortisona si líquidos y vasoactivos restauran la estabilidad. En inestabilidad persistente no permite recomendar a favor o en contra por falta de evidencia. La insuficiencia suprarrenal sospechada/documentada sí requiere cobertura de estrés. No aplicar el régimen adulto.
- Prednisolona/dexametasona en asma, dexametasona en crup o infección SNC permanecen en sus módulos y, cuando corresponda, en el catálogo pediátrico existente. No se crean pautas copiando una equivalencia adulta.

### Anafilaxia, ambas poblaciones

[RCUK 2021, sección 5.5, página 33](https://www.resus.org.uk/sites/default/files/2021-05/Emergency%20Treatment%20of%20Anaphylaxis%20May%202021_0.pdf) desaconseja corticoides de rutina. Pueden valorarse después de la reanimación inicial si existe reacción refractaria o asma/shock persistentes; no sustituyen ni retrasan la adrenalina. La interfaz enlaza el módulo `anaphylaxis` con sus aceptaciones previas y sin restaurar bloqueos.

## Producto, seguridad y límites

Verificar indicación, alergia, tratamiento esteroideo previo, vía, producto y concentración exactos. La necesidad de ajuste o precauciones depende de la indicación, evolución y comorbilidades; vigilar glucosa, electrolitos, circulación y complicaciones. Para una perfusión prescrita, usar concentración verificada y aritmética trazable: `mL/h = mg/h ÷ mg/mL`. Este comparador no inventa preparación, diluyente, estabilidad o volumen.

Los textos clínicos canónicos se presentan en español; controles y nombres están disponibles en ES/PT/EN/ZH. Esto no acredita traducción clínica profesional completa. La implementación y sus pruebas no promueven evidencia ni equivalen a validación prospectiva. Las aceptaciones anteriores conservan su alcance.
