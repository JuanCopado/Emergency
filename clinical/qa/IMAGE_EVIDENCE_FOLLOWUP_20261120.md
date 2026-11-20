# Seguimiento documental de evidencia de imagen · 20/11/2026

**Expediente:** `IMG-EVIDENCE-20261120`, versión 1. **Estado:** preparación documental focal; `CLINICALLY_PENDING`. **Base examinada:** `cdca8e34013bba891a1c49f5ea859f933fcbea63`, árbol `977ec9cd9443bf0e7a284de13e00f242ea80ef92`.

## 1. Alcance y resultado

Se revisan fuentes y trazabilidad de `clinical-image-interpretation`, `ct-mri-screenshot` y `ophthalmology-image`, y la conciliación documental de `final-human-review-gate` con PR35. Se identifican documentos concretos para referencias que todavía se presentan como colecciones o identidades compuestas. El acceso obtenido permite contrastes focales, pero **no acredita una revisión íntegra de las guías ni una renovación completa de estos módulos**.

Este expediente no cambia recomendaciones, código, registro, fechas, estados ni cola. No incluye nuevos casos, imágenes de pacientes, medición de exactitud, pruebas de visión ni ejecución de QA. No expresa ni infiere un SÍ del propietario. Las aceptaciones anteriores conservan su alcance; la regla de Juan como único validador clínico ya está aceptada y no se vuelve a someter a decisión.

## 2. Registro de partida y trazabilidad pendiente

Lectura de [`evidence-registry.json`](../references/evidence-registry.json) y [`evidence-sources.json`](../references/evidence-sources.json) en la base indicada. La antigüedad es la diferencia entre 20/11/2026 y `last_checked`; los cuatro registros tienen `priority: high`, ventana de 30 días y `status: yellow`.

| Módulo | `last_checked` / antigüedad | Identidad canónica en la base | `stored_version` vigente en la base |
|---|---|---|---|
| `clinical-image-interpretation` | 2026-09-17 / 64 días | `src-b5e20534` | `workflow v1.4; diagnostic performance not established` |
| `ct-mri-screenshot` | 2026-09-27 / 54 días | `src-6f0c0d80` | `current online criteria; workflow v1.17` |
| `ophthalmology-image` | 2026-09-27 / 54 días | `src-fc28192f` | `current PPP collection; workflow v1.17` |
| `final-human-review-gate` | 2026-10-06 / 45 días | `src-4a787db0` | `v1.39 final governance gate 2026-10-06` |

Las cuatro identidades canónicas de esta tabla tienen `url: null`, `persistent_id: null`, `compound_identity: true` y procedencia `legacy_evidence_registry`. Eso describe el catálogo, no demuestra que las fuentes reales carezcan de identificador. Existen componentes más precisos, pero su relación histórica consta como `historical_component_pending_reconciliation`:

| Módulo | Componentes ya presentes que se deben conservar y conciliar |
|---|---|
| `clinical-image-interpretation` | `src-internal-image-safety-workflow`; `src-internal-clinical-image-reference-set` |
| `ct-mri-screenshot` | `src-acr-criteria-collection-2026`; `src-acr-ams-2024`; `src-internal-image-safety-workflow` |
| `ophthalmology-image` | `src-aao-ppp-collection-2026`; `src-aao-angle-closure-2026`; `src-internal-image-safety-workflow` |

El catálogo fecha esos componentes el 02/10/2026. No se interpreta esa fecha como verificación actual ni como prueba de que una guía está obsoleta por su año de publicación. El componente del conjunto de referencia interno no aporta por sí solo un inventario de casos, adjudicaciones o resultados que demuestre validación representativa.

## 3. Fuentes concretas y acceso real

Consultas realizadas el **20/11/2026**. «Fragmento indexado» significa texto devuelto por el buscador desde el dominio primario; no equivale a abrir y leer el documento completo. Las aperturas fallidas se mantienen como límites de esta revisión. No se eludieron controles de acceso. Las versiones son las identificadas en estas consultas, sin afirmar una búsqueda exhaustiva de toda posible actualización.

| Ref. | Fuente y versión identificada | URL y localizador útil | Acceso observado y límite |
|---|---|---|---|
| W1 | OMS, *Regulatory considerations on artificial intelligence for health*, 19/10/2023; ISBN 978-92-4-007887-1 | [Ficha editorial](https://www.who.int/publications/i/item/9789240078871); [PDF oficial](https://iris.who.int/bitstream/handle/10665/373421/9789240078871-eng.pdf). §§5.3.2–5.3.4; figura 11 | Ficha y resumen editorial abiertos; pasajes del PDF disponibles en el índice. IRIS devolvió 403. No se leyó el PDF íntegro. La propia ficha define una recopilación de consideraciones, no una guía, norma o política regulatoria. |
| M1 | STARD-AI, Sounderajah y colaboradores, 15/09/2025, *Nature Medicine* 31:3283–3289; DOI `10.1038/s41591-025-03953-8` | [Artículo primario](https://www.nature.com/articles/s41591-025-03953-8). Sección sobre la declaración y tabla 2: ítems 7, 11–15b, 25, 28 y 40b | Pasajes del artículo y de la tabla indexados. HTML/PDF directos redirigieron a autenticación y no se recuperaron íntegros. Es un método de comunicación de estudios, no un resultado de Emergency. |
| M1c | Corrección de autor de STARD-AI, 13/07/2026; DOI `10.1038/s41591-026-04570-9` | [Corrección primaria](https://www.nature.com/articles/s41591-026-04570-9), párrafo de corrección | Texto de la corrección indexado; apertura directa bloqueada por la misma redirección. Añade a Melissa McCradden al consorcio. El aviso no declara cambios metodológicos. |
| C1 | ACR, alteración del estado mental, coma, delirium y psicosis, revisión 2024; DOI `10.1016/j.jacr.2024.08.018` | [Narrativa oficial](https://acsearch.acr.org/docs/3102409/Narrative/). Consideraciones especiales, definición de imagen inicial y variante 1, adulto con sospecha intracraneal o déficit focal | Fragmentos de narrativa y tablas oficiales indexados; apertura directa 403. Corresponde a `src-acr-ams-2024`; la colección general no sustituye este documento específico. |
| C2 | ACR–ASNR–SPR, parámetro para TC de cráneo, revisión 2025, resolución 20 | [Documento oficial](https://gravitas.acr.org/PPTS/GetDocumentView?docId=76); [PDF oficial](https://gravitas.acr.org/PPTS/DownloadPreviewDocument?DocId=76&ReleaseId=2). §IV y §IV.B, imagen cerebral | Cabecera de versión y pasajes técnicos indexados; aperturas directas 403. Candidato a componente específico adicional, sin incorporarlo aquí al catálogo. |
| O1 | AAO, *Primary Angle-Closure Disease Preferred Practice Pattern*, PPP 2025 publicada en línea el 09/02/2026; DOI `10.1016/j.ophtha.2025.12.030` | [Ficha AAO](https://www.aao.org/education/preferred-practice-pattern/primary-angle-closure-disease-ppp); [artículo primario](https://www.aaojournal.org/article/S0161-6420(25)00816-4/fulltext). Apartados de gonioscopia y otros componentes de evaluación inicial; recomendaciones destacadas | Pasajes del artículo indexados; AAO y revista devolvieron 403 al abrir. Corresponde a `src-aao-angle-closure-2026`. No se revisó la colección PPP completa. |

Se localizó además un documento ACR sobre comunicación de hallazgos en [esta URL histórica](https://www.acr.org/-/media/ACR/Files/Practice-Parameters/CommunicationDiag.pdf). La apertura redirigió a Sitecore y no se confirmó su versión. **No se utiliza como fundamento versionado de esta revisión.**

## 4. Contraste focal con el contenido canónico

### 4.1 `clinical-image-interpretation`

**Texto examinado:** [`clinical-images.md`](../modules/clinical-images.md), preámbulo y sección del módulo, incluidos sus límites de evidencia. Ya distingue observación de inferencia, calidad insuficiente, abstención, estudios incompletos y rendimiento no medido. No permite convertir casos de texto o docencia en una afirmación de exactitud visual.

**Contraste externo.** W1 vincula la evaluación al uso previsto, población y contexto, y distingue validación analítica de evaluación clínica. M1 pide trazabilidad de datos, anotaciones, dispositivo, particiones, prueba índice, referencia y representatividad. Esos elementos concuerdan con documentar el estudio y sus límites; no prueban que el flujo de Emergency sea seguro o exacto en una población concreta. [W1], [M1].

**Resultado propio.** La ausencia de una estimación de rendimiento sigue siendo coherente con el expediente disponible. Las reglas sobre instrucciones incrustadas, datos personales y herramientas son controles internos del flujo; no se atribuyen en bloque a W1 o M1. No se identificó en esta revisión un nuevo conjunto de imágenes independientes con adjudicación, denominadores y resultados que cierre la laguna.

**Trabajo documental que falta.** Vincular cada afirmación de rendimiento futura a un protocolo y un conjunto identificables, usando la [`IMAGE_VALIDATION_POLICY.md`](IMAGE_VALIDATION_POLICY.md) existente. La [`hoja de ruta de imagen`](IMAGE_VALIDATION_ROADMAP_2026-11-14.md) ya cita STARD-AI: se conserva esa línea y se añade trazabilidad de su corrección bibliográfica, sin crear otro marco paralelo. Cumplimentar una lista de reporte no sustituye realizar el estudio ni decidir el alcance clínico.

### 4.2 `ct-mri-screenshot`

**Texto examinado:** [`image-modalities.md`](../modules/image-modalities.md), sección `ct-mri-screenshot`. Solicita modalidad, región, secuencia/ventana, cobertura y lateralidad; limita las conclusiones negativas con cortes incompletos y exige confirmar hallazgos urgentes con estudio completo y valoración experta.

**Contraste externo.** C1 trata la elección de neuroimagen en situaciones clínicas delimitadas de adultos; no estudia el rendimiento de interpretar capturas. C2 describe adquisición, reconstrucciones y visualización adecuadas de TC craneal para la pregunta clínica. Proporciona una referencia técnica más concreta para las necesidades de cobertura y ventanas del texto actual. [C1], [C2].

**Resultado propio.** El contraste respalda la pertinencia de declarar limitaciones de la entrada y de evitar extrapolar una captura al estudio entero. No demuestra sensibilidad para hemorragia, masa o herniación ni valida MRI, otras regiones o las instrucciones completas de revisión anatómica. La ruta a un síndrome clínico conserva la necesidad de fuentes propias de ese síndrome. No se cambia ninguna indicación de imagen o pauta.

**Trabajo documental que falta.** Mantener C1 como referencia de su población/indicación y, al conciliar fuentes, asociar C2 únicamente al alcance técnico craneal que documenta. Obtener acceso suficiente al texto aplicable antes de declarar una renovación íntegra; mapear por separado afirmaciones de MRI y otras regiones. El portal ACR no funciona como respaldo universal.

### 4.3 `ophthalmology-image`

**Texto examinado:** [`image-modalities.md`](../modules/image-modalities.md), sección `ophthalmology-image`. Diferencia fotografía, lámpara de hendidura, fluoresceína, fondo y OCT. La imagen no sustituye exploraciones necesarias; el texto ya condiciona la presión a que sea seguro medirla y la dilatación a que sea apropiada.

**Contraste externo.** O1 utiliza gonioscopia para evaluar cierre angular; UBM/OCT de segmento anterior son complementarios. También advierte que dilatar puede no ser aconsejable en enfermedad no tratada y contempla una valoración individual. Esto coincide con mantener las cautelas del módulo: una fotografía/OCT aislada no permite sustituir la evaluación clínica del cierre angular. [O1].

**Resultado propio.** No se identificó contradicción en esos pasajes focales. No se transforma «exploración apropiada» en una obligación general de dilatar. O1 no acredita por sí sola el manejo completo de globo abierto, oclusiones vasculares, desprendimiento, endoftalmitis, celulitis orbitaria o quemadura química; tampoco mide el rendimiento de Emergency para esas entidades.

**Trabajo documental que falta.** Conservar el componente O1 con alcance limitado y completar fuentes específicas para las demás afirmaciones antes de presentar una renovación integral. El acceso a un catálogo o al resumen de una PPP no demuestra esa revisión. No se propone aquí ninguna modificación clínica de la sección.

## 5. Conciliación de `final-human-review-gate`

### 5.1 Regla ya aceptada y discrepancia concreta

[PR35](https://github.com/JuanCopado/Emergency/pull/35), incorporada mediante `caf59bda7a2e5af5d822e18b210f50c300acb775`, estableció la decisión clínica final de Juan y el papel consultivo de Farmacia. En la base de este expediente, [`AGENTS.md`](../../AGENTS.md), [`documentation-governance.md`](../modules/documentation-governance.md), [`final-human-review-policy.json`](final-human-review-policy.json), esquema 1.1, y [`final_human_review_gate.py`](../scripts/final_human_review_gate.py) ya reflejan esa regla. La cola se construye desde los módulos amarillos actuales y el generador exige una decisión explícita para el módulo y referencia concretos.

La discrepancia está en `modules["final-human-review-gate"]` del registro: autoridad descrita de forma antigua, versión de octubre y cifra histórica de 14 amarillos. La nota mezcla vocabulario de farmacia con controles de liberación, pero **no demuestra por sí sola una exigencia ejecutable de firma farmacéutica**. No se inventa un bloqueo nuevo ni se modifica el generador.

### 5.2 Campos antiguos y sustitución documental preparada

Los valores siguientes fijan el delta documental sobre la base `cdca8e3`. La sustitución aplica PR35, sin nueva decisión clínica ni renovación de la revisión pendiente. Su incorporación al registro y la regeneración del catálogo corresponden a la entrega coordinada, fuera de este archivo.

**`primary_source`**

Antes:

```text
Project governance rule: all yellow modules require appropriate human specialist review plus post-correction Clinical QA before green promotion
```

Después:

```text
Project physician-owner validation directive (PR35, 2026-11-20)
```

**`primary_source_url`**: ausente en la base; enlace preparado a la directriz aceptada:

```text
https://github.com/JuanCopado/Emergency/blob/0d0fd3119bdd9a5cf75407849282d759353402c1/AGENTS.md
```

**`stored_version`**

Antes:

```text
v1.39 final governance gate 2026-10-06
```

Después:

```text
PR35 owner-led governance; final-human-review-policy schema 1.1; clinical review date retained
```

**`note`**

Antes:

```text
Dynamic final-project review queue covers all current yellow entries in this registry. Checked2026-11-14:14yellow modules; do not use historical counts. Prior owner acceptances remain recorded. Automated QA alone does not establish prospective clinical validation; applicable clinical/pharmacy/privacy/operational release gates remain, with CLINICALLY_PENDING global.
```

Después:

```text
Governance metadata reconciled 2026-11-20 to the accepted PR35 directive. Dr. Juan Copado Ceballos is the sole final clinical validator; Pharmacy advice is consultative. The dynamic queue covers the current yellow entries without a fixed historical count. Prior owner acceptances remain valid within scope. Product, privacy, operational and post-correction QA requirements remain applicable. The unchanged last_checked records the prior clinical review, not a new evidence or release approval. CLINICALLY_PENDING. Follow-up: qa/EVIDENCE_FOLLOWUP_20261120.md.
```

**Se conservan:** `priority: high`, `last_checked: 2026-10-06`, `status: yellow` y la ventana de revisión. El catálogo derivado se regenera desde su fuente; no se edita a mano ni se presenta el reemplazo de `src-4a787db0` como división de una fuente clínica o validación de rendimiento. Los controles aplicables de producto, privacidad, operación y QA se mantienen. La revisión final de los módulos amarillos sigue pendiente según su alcance individual.

## 6. Entrega y siguientes pasos sin duplicación

| Frente | Aportación de este expediente | Pendiente que permanece |
|---|---|---|
| Tres módulos de imagen | Identidades concretas, localizadores, tipo de acceso y contraste focal con los textos vigentes | Acceso completo aplicable, conciliación de afirmaciones restantes y evidencia de desempeño cuando se pretenda una afirmación de desempeño |
| Gobernanza | Delta de metadatos conforme a la decisión ya aceptada en PR35 | Integración coordinada y regeneración del catálogo; no requiere repetir la aceptación de la regla |
| Validación de imagen | Reutilización de la política y hoja de ruta existentes | Estudio identificable, referencia independiente y resultados; no se producen en esta entrega |

T05/gasometría, ECG/POCUS y el cierre técnico T05/T06 tienen frentes propios coordinados. Este archivo no encarga de nuevo sus pruebas, pilotos o decisiones. La aceptación previa de `pocus` como marco general no se extiende a `pocus-image`, a integración ECG/POCUS ni a estos tres módulos.

**Dictamen documental:** preparación parcial trazable, sin renovación integral de evidencia, promoción a verde, autorización asistencial o `GO_RELEASE`. Una futura propuesta clínica se presentará con ID, versión, alcance exacto, evidencia y límites para la decisión explícita de Juan, conforme a la [`plantilla vigente`](HUMAN_REVIEW_TEMPLATE.md). La conciliación de PR35 conserva una decisión ya tomada.

[W1]: https://iris.who.int/bitstream/handle/10665/373421/9789240078871-eng.pdf
[M1]: https://www.nature.com/articles/s41591-025-03953-8
[C1]: https://acsearch.acr.org/docs/3102409/Narrative/
[C2]: https://gravitas.acr.org/PPTS/GetDocumentView?docId=76
[O1]: https://www.aaojournal.org/article/S0161-6420(25)00816-4/fulltext
