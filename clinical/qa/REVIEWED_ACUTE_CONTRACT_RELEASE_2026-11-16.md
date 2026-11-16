# Liberación de contratos revisados — 16/11/2026

## Resultado y alcance

La instrucción expresa del propietario médico reconoce su validación previa y autoriza incorporar el trabajo terminado. Se sustituyen los **19 bloqueos permanentes de GMA-P2-004** por contratos utilizables: **6 permiten cálculo numérico dentro de su pauta verificada y 13 ofrecen apoyo de decisión con acciones concretas**. Las rutas con cálculo también pueden ofrecer orientación sin dosis cuando no se cumplen las condiciones de su pauta numérica revisada. Se conservan los 46 identificadores públicos; no quedan definiciones ejecutables duplicadas de los 19 bloqueos anteriores.

La base verificada es `codex/v144-international-scope-20261116` en `062d890b4fc92369b83c87664bb4bb0205ccb33f`. La implementación está publicada en el commit `04c52c91cb5c07c5cbcaadcf9b2f9e519b1b4e22`, rama `codex/v144-reviewed-contracts-enable-20261116`, y en el [PR #20](https://github.com/JuanCopado/Emergency/pull/20), que registra la integración en la rama internacional. Las comprobaciones locales y remotas han pasado. La publicación no acredita instalación en otro ordenador ni despliegue clínico.

La [aceptación del propietario](../references/acute-contract-owner-acceptance-2026-11-16.json) conserva su declaración y las aceptaciones previas de estatus, anafilaxia y reversión de 13/11/2026. No se vuelve a pedir esa conformidad. No se atribuye una nueva firma independiente a Farmacia ni una validación prospectiva inexistente. Los tres módulos ya estaban GREEN; se conserva su estado y la fecha de su revisión general, añadiendo una revisión de contratos con alcance y fecha propios. El estado global sigue siendo `CLINICALLY_PENDING` por límites ajenos a esta aceptación y al alcance de esta entrega.

## Matriz de los 19 contratos

| Identificador conservado | Capacidad habilitada | Condición que depende del caso |
|---|---|---|
| `status-phenytoin-local` | Carga inicial adulta de fenitoína; dosis/tiempo o preparación verificada y bomba | Edad, peso, ausencia de carga previa, selección clínica, velocidad y monitorización; producto y mezcla exactos solo para mL/bomba |
| `status-refractory` | Escalada, EEG, vía aérea, cuidados críticos y traslado | Tratamiento previo y estado clínico; la ausencia de recursos genera acciones de escalada |
| `anaphylaxis-under6months` | Adrenalina IM ponderal, primera dosis o repetición individual | Edad, peso, 1 mg/mL sin diluir, volumen realmente medible; historia previa solo cuando hay repetición |
| `anaphylaxis-refractory` | Inicio experto de perfusión IV | Dos dosis IM adecuadas, compromiso persistente, preparación final exacta, recursos, vigilancia y plazo de uso verificado |
| `reversal-vka-pcc` | Cálculo con perfil Octaplex UK explícito; selección clínica para otros perfiles | AVK/urgencia, INR, peso, producto, contraindicaciones, vitamina K y dosis previa; no mezclar tablas |
| `reversal-superwarfarin` | Hemostasia urgente, toxicología y seguimiento prolongado | Exposición, INR, sangrado y acceso a seguimiento |
| `reversal-edoxaban` | Selección especializada de hemostasia y pauta íntegra | Actividad residual, gravedad, función renal, producto y contexto de sangrado |
| `reversal-betrixaban` | Identificación y estrategia especializada | Exposición real y fuente aplicable; no extrapolar autorizaciones de otro fármaco |
| `reversal-fondaparinux` | Soporte y opciones contextuales de hemostasia | Dosis terapéutica/profilaxis, bioacumulación, sitio de sangrado y ensayo fiable; sin protamina |
| `reversal-other-lmwh` | Protamina para dalteparina/Fragmin identificada; decisión para otras HBPM | UI anti-Xa correctas, dosis causal, actividad residual, producto y riesgos de protamina |
| `reversal-enoxaparin-over12` | Evaluación de necesidad de reversión tardía | Más de 12 h, sangrado, actividad residual, función renal y tratamiento previo |
| `reversal-argatroban` | Suspensión, soporte, control de foco y reevaluación | Perfusión, coagulación y función hepática |
| `reversal-bivalirudin` | Suspensión, soporte y evaluación de aclaramiento | Perfusión, coagulación y función renal |
| `reversal-other-dti` | Identificación y derivación a la ruta de la molécula | Agente y actividad residual; no extrapolar idarucizumab a toda la clase |
| `reversal-danaparoid` | Soporte y evaluación especializada | Sangrado, actividad y aclaramiento; no reversión fiable con protamina |
| `reversal-fibrinolytics` | Hemostasia según agente, indicación, tiempo y sangrado | Distingue la tabla AHA/ASA 2026 de la pauta contextual NCS 2016 y exige verificar el componente transfusional |
| `reversal-antiplatelets` | Decisión según HIC, cirugía y antiagregante | No transfusión plaquetaria rutinaria; reconoce incertidumbre de DDAVP y del contexto traumático |
| `reversal-unknown` | Estabilización e identificación del agente | Permite datos desconocidos y falta de recursos; no exige una exposición ficticia para abrir el flujo |
| `reversal-dabigatran-repeat` | Segunda tanda de idarucizumab cuando cumple ficha | Primera tanda completa, indicación específica y aPTT/dTT/ECT prolongado; sin repetición automática |

Un flujo de decisión tiene `result_kind=decision_support` y no puede emitir dosis, unidad de dosis, componentes de administración, concentración, volumen, velocidad, duración, cantidad por hora ni máximo como si fueran un tratamiento calculado. Puede explicar opciones respaldadas y sus límites dentro de la orientación clínica. No se presenta la ausencia de un antídoto universal como un contrato pendiente de aceptación administrativa.

## Conciliación clínica y alcance internacional

Las fuentes primarias y las diferencias materiales se detallan en los anexos de [estatus](../references/acute-status-reviewed-2026-11-16.md), [anafilaxia](../references/acute-anaphylaxis-reviewed-2026-11-16.md) y [reversión](../references/acute-reversal-reviewed-2026-11-16.md). El núcleo no exige seleccionar país ni hospital. Un perfil farmacéutico concreto limita solo las conversiones de producto que realmente dependen de él.

- Fenitoína: se conserva la decisión previa del propietario de 20 mg/kg, máximo 2 g, en al menos 40 minutos. El modo de dosis/tiempo funciona sin inventar diluyente, volumen o estabilidad. La preparación opcional exige el producto y procedimiento completos verificados; no se extiende la preparación Galway a otros fabricantes por compartir concentración.
- Anafilaxia en menores de 6 meses: se adopta el cálculo ERC/WAO de 10 microgramos/kg con adrenalina IM 1 mg/mL sin diluir. La banda RCUK de 100–150 microgramos permanece como discrepancia documentada, sin imponerla como mínimo. Se comprueba el volumen exacto y el dispositivo declarado. La adrenalina IM no adquiere una contraindicación absoluta ficticia por un campo genérico de alergia; las cuatro rutas IM ya existentes se armonizan con esta precisión.
- Anafilaxia refractaria: la receta aceptada de 1 mg hasta 100 mL finales produce 10 microgramos/mL. Se calculan los inicios de 0,5 o 1 mL/kg/h según gravedad elegida por el experto. No se declara un máximo universal de mantenimiento ni una estabilidad universal. La vida útil de 60 minutos en un caso sintético es un dato de prueba, no una recomendación clínica.
- Reversión: las tablas de PCC UK y la referencia portuguesa previa no se fusionan. La actualización NCS/SCCM de 24/09/2026 se limita a sus poblaciones y escenarios de hemorragia intracraneal. Se distingue de la indicación regulatoria de andexanet y de otros contextos de sangrado. La tabla AHA/ASA 2026 para HIC sintomática tras trombólisis por ictus conserva agente, tiempo y régimen completos.
- La revisión independiente corrigió la identidad de la fuente de protamina: el enlace Pfizer previamente consignado correspondía a heparina y describía su sobredosis. La referencia de protamina usada para el límite de administración es la etiqueta primaria de Fresenius Kabi en DailyMed, explícitamente identificada en el anexo.

### Correcciones relacionadas que afectan a contratos ya calculables

La ficha Clexane 4.9 distingue administración en las ocho horas previas de administración hace más de ocho horas. Se concilia la frontera: **hasta 8 h inclusive** para la referencia 1 mg/mg; **más de 8 y hasta 12 h** para 0,5 mg/mg. La administración lenta de protamina se limita a **50 mg en al menos 10 min**, respetando cualquier límite más restrictivo del producto. Es un límite de esta administración, no del total acumulado del tratamiento. No se programa una nueva dosis. Se añade un caso independiente a las 8 h exactas.

La discrepancia histórica GMA-P1-003 sobre un perfil de producto con límite estricto menor de 5 mg/min no se declara cerrada por esta entrega. No se genera una velocidad de bomba de protamina que la eluda.

### Aceptaciones anteriores que aún no llegaban a la interfaz

El control de coherencia detectó cuatro etiquetas YELLOW antiguas en la tabla y el catálogo de guías, aunque el registro canónico ya recogía aceptación GREEN del14/11/2026: perfusiones vasoactivas, sedación/analgesia UCI, medicación ambulatoria pediátrica y marco general POCUS. Se sincronizan con esas decisiones documentadas, conservando sus límites y sin modificar los estados del registro ni promover la interpretación de imágenes. También se regeneran las guías desde el texto canónico para incorporar revisiones ya realizadas que no estaban en el archivo derivado. Dos expectativas de UI todavía usaban los textos anteriores al alcance internacional; se concilian con la presentación vigente, manteniendo las comprobaciones de cambio de idioma y del aviso clínico.

## Implementación y comprobaciones de seguridad

La API y la interfaz comparten los campos condicionales. Al cambiar de modo, los datos que dejan de aplicar no se envían; si otro consumidor intenta enviar valores residuales, la API los rechaza. Los modos sin preparación o sin producto no requieren rellenar números ficticios. Faltantes, tipos inválidos, valores no finitos, errores de vía, producto, cronología o límites aplicables producen una parada de ese cálculo.

Los resultados revisados incorporan `OWNER_VALIDATED_2026_11_16`, la aceptación y el anexo de evidencia, visibles también en las exportaciones. La huella de la fuente incluye módulos, metadatos y código de los helpers importados; un cambio de cálculo invalida instantáneas y exportaciones anteriores. JSON, PDF, DOCX e impresión deben conservar el mismo contenido y exigir revisión del resultado actual.

**GMA-P2-001:** se corrigen las multiplicaciones/divisiones intermedias y el resultado redondeado en `doseToRate` y `rateToDose`. Entradas finitas extremas ya no pueden producir una salida `ok` con infinito o cero por desbordamiento/subdesbordamiento. Las fórmulas y unidades clínicas habituales se conservan. Nueve regresiones focales se añadieron al motor existente; su ejecución roja previa y verde posterior se observó durante la tarea.

## Validación observada y límites de entrega

**GMA-P2-004 y GMA-P2-001 quedan resueltos dentro del alcance documentado.** El commit de implementación pasó Clinical QA, App UI QA y Evidence surveillance guardrails, tanto por push como por pull request.

- Local: **812 pruebas Python**, **445 de frontend**, **7/7 controles globales**, 4 pruebas de guías y 9 de procedimientos; typecheck, lint, build, catálogo de fuentes y grafo PASS.
- [Clinical QA remoto](https://github.com/JuanCopado/Emergency/actions/runs/43808946106): **812 pruebas Python y 7/7 controles PASS**.
- [App UI QA remoto](https://github.com/JuanCopado/Emergency/actions/runs/43808946102): **21/21 casos sobre los 19 contratos PASS**, incluidos formularios condicionales, invalidación, controles negativos y fidelidad JSON/PDF/DOCX/impresión. También pasaron las verificaciones de PDF de guías y formulario pediátrico ya presentes.
- La revisión de fuente observada por el navegador coincide exactamente con la revisión clínica/API: `453fbf0208d59704d649838a35a6b26deb41862ae53cc4a001c9a84daae807f9`.
- El informe completo del artefacto remoto se conserva en `REVIEWED_ACUTE_BROWSER_2026-11-16.json`; su SHA-256, run, commit y artefacto están registrados en el JSON de entrega. El intento local previo permanece por separado en `REVIEWED_ACUTE_BROWSER_LOCAL_2026-11-16.json` como `BLOCKED_ENVIRONMENT`, con cero casos.
- La publicación se comunicó en el [hilo común del proyecto](https://github.com/JuanCopado/Emergency/issues/18#issuecomment-6907999527).

La matriz y los resultados finales de las comprobaciones se registran en `REVIEWED_ACUTE_CONTRACT_RELEASE_2026-11-16.json` y `REVIEWED_ACUTE_BROWSER_2026-11-16.json`. Los casos son sintéticos y sus expectativas se especifican manualmente a partir de las fuentes, sin obtenerlas del calculador que se prueba.

Durante la integración se observó una parada esperada de la matriz al cambiar un módulo mientras la prueba conservaba una revisión antigua. Se conserva el mecanismo de invalidación; la matriz se ejecuta de nuevo sobre las fuentes estabilizadas antes de cerrar la entrega. No se oculta ese primer intento ni se lo presenta como resultado final.

Se preservan `main`, RC1 y la línea v1.43. No se cierran otros hallazgos P1/P2 por asociación, no se certifica stock mundial, exactitud física de un dispositivo ni cobertura pediátrica fuera de la población de cada contrato. Las comprobaciones técnicas no equivalen a un ensayo prospectivo ni al despliegue de la aplicación en otro equipo.
