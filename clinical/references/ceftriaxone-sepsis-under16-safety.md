# Ceftriaxona — sepsis comunitaria en menores de 16 años

Revisión focal: 16/11/2026. Hallazgo: GMA-C-P1-001. Alcance: entrada `sepsis-community-ceftriaxone` y sus dos representaciones de catálogo. Estado global: CLINICALLY_PENDING. Referencia clínica y controles técnicos; no certificación del producto disponible ni autorización asistencial global.

## Población y selección

La referencia elegida es NICE NG254 (19/11/2025), recomendaciones 1.8.2 y 1.8.5–1.8.9. Se conserva la aritmética previamente documentada de 80 mg/kg IV una vez al día, máximo 4 g/día, en sospecha de sepsis comunitaria desde 28 días y antes del cumpleaños 16. NG51 queda como antecedente; 16–17 años se remiten a NG253. Se excluyen del cálculo genérico el foco conocido, la sepsis intrahospitalaria y antecedentes de infección/colonización resistente a ceftriaxona: requieren la pauta local del escenario.

En menores de tres meses calendáricos debe planificarse cobertura adicional activa frente a Listeria (NICE ofrece ampicilina o amoxicilina como ejemplos). Aquí no se calcula esa medicación acompañante. No convertir tres meses en 90 días ni dieciséis años en 5840 días.

## Peso y pauta adulta

Las fichas técnicas remiten a la pauta habitual adulta a partir de 50 kg. La dosis adulta depende de la indicación, la gravedad, el producto y la función orgánica: sus tablas contienen intervalos y pautas específicas. Por ello no se implanta un selector universal «2 g estándar / 4 g crítica». A partir de 50 kg este calculador devuelve ADULT_INDICATION_REGIMEN_REQUIRED sin resultado numérico. No se extrapola el techo de una infección a otra ni se cambia el peso real por un peso ideal sin evidencia específica.

## Calcio y población neonatal

No mezclar/reconstituir con soluciones cálcicas ni administrarlas simultáneamente, incluida la conexión en Y; separar accesos no elimina por sí solo esta prohibición general. En <=28 días, si se necesita o prevé calcio IV, la contraindicación persiste aunque se separen tiempos o líneas. En mayores de 28 días, la administración secuencial exige las condiciones documentadas de líneas separadas/sustituidas o lavado completo con solución compatible.

La ficha contempla una excepción experta de NPT cálcica continua, tras considerar alternativas, mediante líneas y sitios diferentes. El módulo automático excluye toda simultaneidad y deriva esa excepción a revisión: se trata de un límite deliberado del módulo, no de una prohibición regulatoria sin excepciones. No se aplica esa excepción a neonatos contraindicados.

Conservar además las contraindicaciones de prematuros hasta 41 semanas de edad posmenstrual y neonatos a término <=28 días con hiperbilirrubinemia, ictericia, hipoalbuminemia o acidosis. La edad posmenstrual declarada debe ser coherente con la edad cronológica y un nacimiento antes de 37 semanas completas; una contradicción impide calcular. El día 28 entra en el intervalo literal NICE pero todavía está incluido en las restricciones neonatales de producto. El umbral NICE neonatal de >40 semanas no anula el límite regulatorio del prematuro.

## Vía, lidocaína y volumen IM

La entrada de sepsis sigue siendo exclusivamente IV. Una solución con lidocaína nunca se administra IV. Para una indicación IM separada, las fichas limitan a 1 g por sitio; una dosis IM de 2 g requiere puntos distintos. Comprobar también las contraindicaciones de lidocaína y la formulación indicada para edad y vía.

Los 3,5 mL descritos en varias presentaciones son el disolvente de reconstitución; no constituyen un máximo universal de volumen final por sitio. La ficha Qilu documenta desplazamiento de polvo, por lo que no se extrapolan concentraciones entre marcas. Este cambio no añade una calculadora IM ni calcula mL a partir de una concentración supuesta.

## Función renal y hepática

- Renal aislada con hígado conservado: generalmente sin reducción rutinaria; la ficha introduce un techo de 2 g/día cuando CrCl <10 mL/min. Ese escenario sale del cálculo automático para selección individual; no se reduce mecánicamente una pauta de sepsis.
- Hepática aislada leve/moderada con riñón conservado: generalmente sin ajuste. La insuficiencia hepática grave carece de datos suficientes en las fichas revisadas y requiere revisión.
- Renal y hepática graves concomitantes: vigilancia estrecha e individualización. Las fichas examinadas no sostienen una regla universal de 2 g/día atribuible únicamente a esa combinación.

## Contrato de software

Se exigen fechas explícitas y contexto suficiente. Los valores desconocidos no equivalen a ausencia de riesgo. El llamador conserva `calculate(entry_id, weight_kg, path=...)` para entradas ajenas; este ID exige `context=` y la CLI admite `--context-json`.

Los controles comprueban edad, peso, contexto infeccioso, prematuridad/riesgo neonatal cuando aplica, calcio, diluyentes y función orgánica. La salida mantiene dosis en mg, coeficiente en mg/kg, fuente, salvedades y CLINICAL_REVIEW_REQUIRED / CLINICALLY_PENDING. Se rechaza una concentración añadida al registro de esta pauta: no hay preparación ni volumen validados en este contrato. Los demás antibióticos conservan su comportamiento; el hallazgo general GMA-P1-001 no queda cerrado por corregir la unidad de este ID.

## Fuentes y alcance de acceso

1. [NICE NG254](https://www.nice.org.uk/guidance/ng254/chapter/Antibiotic-therapy-intravenous-fluid-and-oxygen), 1.8.2 y 1.8.5–1.8.9. Publicación 19/11/2025. Texto oficial de recomendaciones recuperado mediante búsqueda; una apertura directa del PDF en esta sesión devolvió 403. No se presenta como revisión integral de todas las recomendaciones de sepsis.
2. [AEMPS, ceftriaxona Fresenius Kabi IV 64538](https://cima.aemps.es/cima/dochtml/ft/64538/FichaTecnica_64538.html), 4.2–4.5: población, indicación y seguridad.
3. [AEMPS, ceftriaxona Reig Jofre IM 64405](https://cima.aemps.es/cima/dochtml/ft/64405/FT_64405.html), 4.2 y 6.6: órganos, límite por sitio y reconstitución. Texto revisado abril/2024.
4. [AEMPS, ceftriaxona Qilu 83903](https://cima.aemps.es/cima/dochtml/ft/83903/FT_83903.html), 4.4 y 6.6: NPT y producto/volumen. Texto revisado mayo/2024.
5. [INFARMED, anexos armonizados de Rocephin](https://www.infarmed.pt/documents/15786/1886316/Rocephin_Anexos.pdf/dc50fd4a-1bb9-4be8-8cea-577bdcb6e21f?version=1.0), 4.2–4.5. Documento regulatorio histórico de armonización; no identifica por sí solo la ficha vigente ni la disponibilidad del producto en la jurisdicción y organización seleccionadas. Aplicar el marco de `international-context.md`.
6. [OMS, nacimiento prematuro](https://www.who.int/news-room/fact-sheets/detail/preterm-birth/), 10/05/2023: definición de prematuridad antes de 37 semanas completas, utilizada solo para comprobar la coherencia de los datos de edad.

No se afirma conformidad nacional exhaustiva ni se sustituye el protocolo local. La diferencia NICE/DGS ya documentada en pediatric-sepsis se conserva.
