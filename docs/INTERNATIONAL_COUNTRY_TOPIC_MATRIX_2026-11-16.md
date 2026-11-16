# INT-02 / INT-03 — Matriz internacional por país y tema (16/11/2026)

**Estado:** candidato técnico en rama aislada, NO implementado en el motor asistencial. **CLINICALLY_PENDING**. No se ha liberado ninguna pauta internacional ni modificado una dosis del núcleo.

**Base:** `codex/v144-international-scope-20261116`. **Rama:** `codex/v144-country-context-matrix-20261116`. Deriva de la directriz [INT-01](INTERNATIONAL_SCOPE.md). `main`, `v1.42-rc1` y la línea v1.43 no se modifican.

## Alcance exacto

- 14 jurisdicciones iniciales, mediante ISO 3166-1 alfa-2: **ES, PT, FR, DE, IT, GB, US, CA, MX, BR, CO, AR, CL, PE**.
- 64 temas transversales: **41 farmacológicos, 12 protocolos, 6 procedimientos, 4 diagnósticos y 1 operativo**. **896 combinaciones país–tema**, todas con revisión jurisdiccional pendiente.
- Incluye las seis familias de contratos farmacológicos agudos (amiodarona, insulina/CAD, NaCl hipertónico, estatus epiléptico, anafilaxia y reversión/antídotos), **Octaplex/PCC**, trombólisis, vasoactivos, sedoanalgesia, antibióticos, pediatría y más. No presume que los temas sean IDs canónicos de regimen: son identificadores de coordinación y futuros enlaces a contratos existentes.
- Los portales nacionales son **directorios de fuentes**. No prueban dosis, fichas concretas, versión de producto, autorización individual, presentación, comercialización, existencia local ni disponibilidad de recursos. No hay registros nacionales de revisión de producto aprobados en este lote.

## Separación de responsabilidades

| Capa | Contenido | Condición de uso |
|---|---|---|
| Núcleo clínico | ID canónico de módulo, procedimiento o régimen, lógica general, evidencia | No duplicar el núcleo por país |
| Jurisdicción | País explicitado; regulador, fichas vigentes y guías nacionales aplicables | No derivar del idioma ni de la ubicación del propietario |
| Producto | Nombre, titular/registro, presentación, concentración, diluyente, estabilidad, incompatibilidades | Verificación del producto exacto y fecha; no sustituir por otro país |
| Organización | Formulario, protocolo, stock, dispositivos, derivación y competencias | Revisión del centro y recursos constatados, no inferidos |
| Caso | Indicación y fase, población, edad, peso, embarazo, función renal/hepática, vía y entorno | Solo entradas explícitas y clínicamente pertinentes |

La **EMA** puede ser fuente de autorizaciones centralizadas de la UE, pero muchas autorizaciones siguen siendo nacionales. **Reino Unido no se modela como selección automática de la UE**. Las guías internacionales y nacionales de las sociedades científicas se guardan separadas de las fichas regulatorias; una divergencia de dosis, indicación, INR, concentración, velocidad o máximo no se promedia ni se resuelve por cercanía geográfica.

## Implementación de esta entrega

- `clinical/references/international-country-topic-matrix.json`: catálogo machine-readable de países, autoridades, URLs de consulta, temas y `country_topic_reviews: []`.
- `clinical/scripts/jurisdiction_resolver.py`: comparación documental explícita por país y tema. Devuelve únicamente estado de revisión y fuentes de consulta, **nunca dosis, preparación ni recomendación clínica**. Rechaza un país ausente o desconocido, IDs duplicados y referencias sin HTTPS. Una referencia documental revisada sigue marcada como **solo referencia, sin autorización clínica**.
- `clinical/tests/test_jurisdiction_resolver.py`: regresiones de no herencia entre países, idioma independiente, bloqueo de entradas ausentes, duplicados/conflictos y prevención de datos prescriptivos.
- Uso de consulta: `python clinical/scripts/jurisdiction_resolver.py --topic medication.octaplex-pcc --country ES --country PT`. Muestra exclusivamente el estado documental pendiente.

## Plantilla mínima de una revisión futura

Un registro documental candidato deberá definir `country_code`, `topic_id`, `indication`, `population`, `setting`, `source_url`, `source_title`, `source_version`, `source_date`, `verified_at`, `reviewer_clinical`, `reviewer_pharmacy` y estado `DOCUMENTARY_REVIEWED`. Para una medicación se necesitarán **además**, en un flujo posterior y validado, producto/registro nacional, dosis y límites indicación-población-vía, concentración y preparación, revisión de Farmacia, hospital/entorno cuando sea operativo y validación técnica de la calculadora. Este primer resolver no produce ni aprueba esos valores.

**No añadir identificadores personales, historias clínicas, contraseñas ni material confidencial** al catálogo público.

## Dos ejemplos reales adicionales a Octaplex (solo candidatos documentales)

- **Andexanet alfa**: la FDA comunicó el 18/12/2025 una evaluación desfavorable del balance beneficio-riesgo de Andexxa y el fin de su comercialización estadounidense el 22/12/2025. En cambio, el EPAR de **Ondexxya** de la EMA mantiene registrada una autorización condicional centralizada en la UE. La situación regulatoria no equivale a disponibilidad efectiva ni recomendación clínica. Fuentes: [FDA](https://www.fda.gov/vaccines-blood-biologics/safety-availability-biologics/update-safety-andexxa) y [EMA](https://www.ema.europa.eu/en/medicines/human/EPAR/ondexxya).
- **Tenecteplasa para ictus isquémico agudo en adultos**: la ficha estadounidense **TNKase** consultada (revisión 02/2025) limita la ventana indicada a **3 horas** desde inicio de síntomas. El EPAR europeo **Metalyse** y la SmPC británica de la presentación de ictus incluyen **4,5 horas** desde última vez conocido bien. Una guía clínica como AHA/ASA 2026 puede contemplar otra ventana y debe quedar clasificada como **guía**, no como ampliación automática de ficha estadounidense. Fuentes: [DailyMed/FDA](https://dailymed.nlm.nih.gov/dailymed/fda/fdaDrugXsl.cfm?setid=e647640d-c395-4b4b-a0be-1162f9c21d84), [EMA](https://www.ema.europa.eu/en/medicines/human/EPAR/metalyse), [SmPC UK](https://www.medicines.org.uk/emc/product/15859/smpc) y [guía AHA/ASA 2026](https://www.ahajournals.org/doi/10.1161/STR.0000000000000513).

Candidatos trazables en `clinical/references/international-crosscountry-evidence-candidates-2026-11-16.json`. **No se han aprobado sus pautas, productos, condiciones ni revisiones nacionales; no alimentan el calculador ni cambian las 896 ranuras pendientes.** Estas comparaciones acreditan por qué el selector debe distinguir jurisdicción, tipo de fuente, indicación, presentación, tiempo y estado regulatorio.

## Priorización de conciliación

1. **P0 de seguridad**: 19 contratos farmacológicos bloqueados; empezar por los seis flujos agudos y Octaplex/PCC; después trombólisis, analgosedación pediátrica, antimicrobianos críticos y perfusiones.
2. **Protocolos**: reanimación adulta y pediátrica, sepsis, ictus, SCA, CAD, vía aérea, trauma y TEV. Distinguir referencias internacionales, nacionales y recursos locales.
3. **Procedimientos, imagen y otros entornos**: material, indicaciones, recursos/rescate, POCUS, ECG e imagen; revisión por tarea, población y país.
4. **Fase de integración posterior**: selector explícito de país y centro, endpoint de aplicabilidad, bloqueos reales en calculadoras/exportaciones, tests por producto/jurisdicción y revisión clínica y farmacéutica nominal. Nada de ello queda habilitado por esta entrega.

## Fuentes-registro para el directorio

EMA: https://www.ema.europa.eu/en/about-us/what-we-do/authorisation-medicines

España — AEMPS/CIMA: https://cima.aemps.es/

Portugal — INFARMED/Infomed: https://www.infarmed.pt/

Francia — ANSM: https://base-donnees-publique.medicaments.gouv.fr/

Alemania — BfArM/AMIce: https://www.bfarm.de/DE/Arzneimittel/Arzneimittelinformationen/Arzneimittel-recherchieren/AMIce/_node.html

Italia — AIFA: https://www.aifa.gov.it/it/liste-dei-farmaci

Reino Unido — MHRA: https://products.mhra.gov.uk/

EE. UU. — FDA: https://www.accessdata.fda.gov/scripts/cder/daf/

Canadá — Health Canada: https://www.canada.ca/en/health-canada/services/drugs-health-products/drug-products/drug-product-database.html

México — COFEPRIS: https://www.gob.mx/cofepris/es/documentos/registros-sanitarios-medicamentos

Brasil — ANVISA: https://consultas.anvisa.gov.br/

Colombia — INVIMA: https://www.invima.gov.co/consulta-registros-sanitarios

Argentina — ANMAT: https://www.anmat.gob.ar/Medicamentos/basedat.asp

Chile — ISP: https://www.ispch.cl/anamed/medicamentos/registro-sanitario-de-productos-farmaceuticos/

Perú — DIGEMID: https://www.digemid.minsa.gob.pe/webDigemid/registro-sanitario/productos-farmaceuticos/

Las páginas anteriores permiten **localizar fuentes**; la vigencia de cada ficha específica exige comprobación separada. Esta documentación no reproduce fichas ni se presenta como una conciliación clínica de 14 países.

## Comprobaciones y límites

El catálogo queda **sin revisiones país–tema**. 896 ranuras pendientes no son 896 medicamentos validados. La matriz no se conecta a las calculadoras ni a la interfaz clínica de v1.44; los **19 bloqueos**, otros P1 y `CLINICALLY_PENDING` siguen intactos. La existencia de pruebas unitarias de seguridad no sustituye QA integral del proyecto ni revisión asistencial.

Continuidad: registrar el resultado de CI y la eventual recepción del trabajo por Codex/Claude/Gemini separadamente de la publicación Git; no afirmar revisión de agentes externos sin evidencia.
