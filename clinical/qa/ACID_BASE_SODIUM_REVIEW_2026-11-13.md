# Revisión ácido-base y sodio · 13/11/2026

**Estado conservado:54 GREEN /77 YELLOW /0 RED.** Los dos módulos revisados permanecen YELLOW por los puntos concretos indicados abajo; CLINICALLY_PENDING global.

## Ácido-base

Comprobadas convenciones de anión gap, corrección por albúmina, compensaciones aproximadas y aplicación del cociente delta. Se identifica explícitamente qué cálculo incluye potasio y qué referencia excluye potasio. Las reglas de compensación requieren reconocer primero el componente metabólico; un bicarbonato bajo aislado no autoriza etiquetar un trastorno mixto.

El calculador admite presión en mmHg o kPa y albúmina en g/dL o g/L, rechaza campos duplicados con unidades alternativas y entradas imposibles/no finitas. Informa la base del cociente delta y deja condicionada la interpretación de Winter cuando falta confirmación del componente metabólico. Los ejemplos de prueba son sintéticos, con valores diferentes del informe aportado.

Del ejemplo se conserva únicamente metainformación de unidades y el intervalo de gap7–17mmol/L. No se archivan identificador, resultados exactos vinculados a fecha, firma o identidad del validador analítico. La unidad de hemoglobina no permite inferir la de albúmina. La validación del resultado analítico no se convierte en firma de validación de software.

**Pendiente local:** confirmar el analizador, la fórmula del gap con/sin potasio y su intervalo correspondiente. Tipo de muestra, albúmina y fechas de columnas son necesarios para interpretar el caso completo, pero no se inventan ni se usan para bloquear aritmética genérica.

## Sodio

Se mantiene la pauta publicada SfE2022/Europa2014, con vigilancia más explícita de la natremia y diuresis, rescate dirigido por especialista y separación entre hiponatremia e hipernatremia. El límite acumulado nunca se trata como objetivo. Las referencias de rescate son intervenciones reevaluadas, no órdenes automáticas ni una pauta ciega de desmopresina.

Se localiza un PDF oficial ESE/ERA2026 cuyo nombre indica draft/for review. La página ERA menciona el proyecto2026, pero no acredita en este contraste una publicación final que sustituya a la guía previa. Se registra como candidato y no se incorpora su dosificación. El artículo NDT2024 tiene correcciones posteriores identificadas; no se adopta como referencia única sin conciliar sus versiones.

**Pendiente:** verificar la publicación final2026 y confirmar el producto3% listo para administrar o la preparación de Farmacia (concentración de origen/diluyente/volumen final/envase/condiciones), junto con la aceptación del circuito de controles y rescate. No se declara validación local de una receta no aportada.

## Fuentes

### acid-base-emergencies

- [SRLF/SFMU metabolic acidosis recommendations](https://pmc.ncbi.nlm.nih.gov/articles/PMC6695455/) — 2019. Gap conventions, albumin correction, distinguish respiratory compensation; indexed primary recommendation text retrieved, full PMC page returned captcha.
- [ATS Interpretation of ABGs](https://site.thoracic.org/assemblies/cc/clinical-education/interpretation-of-abgs) — Current official educational page; not a new2026 guideline. Winter and mixed-disorder framework; do not copy displayed AG/osmolality typography errors into code.
- [MSD primary changes and compensation table](https://www.msdmanuals.com/professional/multimedia/table/primary-changes-and-compensations-in-simple-acid-base-disorders) — Current professional manual table; reviewed2026-11-13. Approximate compensation ranges; selected0.7 alkalosis slope lies in published0.6-0.75 range.
- [NIST units table](https://www.nist.gov/system/files/documents/2025/12/30/appc-26-HB44-20251222.pdf) — Handbook44 AppendixC2026. Pressure conversion based on1mmHg=133.3224Pa.
- [BICARICU-2 randomized clinical trial](https://pubmed.ncbi.nlm.nih.gov/41159812/) — JAMA2025; DOI10.1001/jama.2025.20231. No day90 mortality benefit in studied severe metabolic acidemia plus moderate/severe AKI; no blanket bicarbonate indication inferred.

### sodium-emergencies

- [Society for Endocrinology hyponatraemia emergency guidance](https://www.endocrinology.org/media/xhrhxhxm/emergency-management-of-severe-and-moderately-severely-symptomatic-hyponatraemia-in-adult-patients-2022.pdf) — 2022. Published intermittent bolus/initial-response and correction-ceiling approach.
- [European hyponatraemia clinical practice guideline](https://academic.oup.com/ejendo/article/170/3/G1/6668028) — 2014; published final reference, not relabelled2026. Monitoring, water-diuresis alert and specialist-directed rescue; primary indexed text retrieved, direct fetch fails publisher CDN redirect.
- [Evaluation and management of hypernatremia in adults: clinical perspectives](https://pmc.ncbi.nlm.nih.gov/articles/PMC10175862/) — 2023. Conventional chronic/unknown correction reference, limits of adult evidence, different approach to excessive correction.
- [Adult hypernatremia correction systematic review](https://pubmed.ncbi.nlm.nih.gov/39765195/) — 2025; PMID39765195. Adult observational heterogeneity; does not establish a universal faster correction order.
- [ESE/ERA hyponatraemia candidate guideline](https://www.ese-hormones.org/media/nfca3mga/hyponatraemia-joint-guideline-draft-for-review.pdf) — Official PDF named draft/for review; final replacement not verified. Candidate only, not adopted into stable doses.
- [ERA guideline collaboration directory](https://www.era-online.org/era-guidance/) — Current listing names2026 ESE-ERA project. Listing without verified final publication link for this project; not proof that draft is final.
- [ESE published guideline directory entry](https://www.ese-hormones.org/publications/directory/ese-clinical-guideline-for-the-management-of-hyponatraemia/) — 2014 published entry. Published entry identified separately from newer candidate.

## QA

PASS:615/615 Python (9 casos sintéticos nuevos),434/434 frontend,4/4 generación y7/7 comprobaciones globales. Integridad131/131; auditoría sin errores; catálogo220 fuentes normalizado.

Una comprobación inicial falló por capitalización de un encabezado heredado; corregida antes del PASS completo. Tras aclarar el contexto de la evaluación urinaria de hipernatremia se repitieron las419 pruebas del bundle y4 de generación, también PASS; sin cambios de código posteriores a la ejecución615.

Las19 ramas automáticas bloqueadas y sus contratos se conservan. Nueva prueba de navegador no ejecutada. Registro: `ACID_BASE_SODIUM_QA_2026-11-13.json`.

Datos estructurados: `ACID_BASE_SODIUM_REVIEW_2026-11-13.json`.
