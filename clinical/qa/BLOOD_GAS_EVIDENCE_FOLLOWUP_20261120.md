# Gasometría por imagen: seguimiento de evidencia · 20/11/2026

## Identidad, alcance y resultado

Revisión documental focal de `blood-gas-image` sobre el commit internacional
`cdca8e34013bba891a1c49f5ea859f933fcbea63`, árbol
`977ec9cd9443bf0e7a284de13e00f242ea80ef92`. Se cotejan tipo de muestra,
preanalítica, procedencia de FiO₂ y relación entre oxigenación y definición
de SDRA. El módulo canónico es la sección correspondiente de
[image-modalities.md](../modules/image-modalities.md#blood-gas-image), junto
con su preámbulo y [clinical-image-interpretation](../modules/clinical-images.md).

**Resultado:** las fuentes consultadas respaldan las cautelas centrales del
módulo en el alcance comparado. La siguiente entrega útil es completar el
expediente de evaluación previsto en PR #39 con una cohorte identificada,
referencias independientes, denominadores y criterios previos. Esta lectura
de guías no aporta mediciones de rendimiento de Emergency.

En el [registro de evidencia](../references/evidence-registry.json),
`blood-gas-image` permanece **YELLOW**, con `last_checked: 2026-09-27` y fuente
genérica de flujo de imagen sin URL específica. El registro de
`acid-base-emergencies` conserva su GREEN y revisión de referencia manual del
14/11/2026, con el perfil local del analizador pendiente de verificación.
No se traslada ese estado al OCR. Se mantienen `CLINICALLY_PENDING`, las
aceptaciones previas y el intervalo de FiO₂ ya documentado en
[T05](../../docs/BLOOD_GAS_LOCAL.md). Este expediente no modifica fechas de
evidencia, estados, fórmulas, dosis, umbrales ni permisos de uso asistencial.

## Fuentes primarias y acceso comprobado

Consulta realizada el **20/11/2026**. Las fechas siguientes identifican las
publicaciones; la fecha de consulta o la carpeta de descarga no constituyen
una nueva edición. Se conserva el alcance de cada emisor, sin convertir una
guía nacional o de una población concreta en una regla universal.

| ID | Fuente, versión y enlace | Localizador cotejado | Acceso y límite |
|---|---|---|---|
| S1 | AARC, *Blood Gas Analysis and Hemoximetry*, 2013. Respiratory Care 58(10):1694–1703. DOI `10.4187/respcare.02786`. [PDF oficial](https://www.aarc.org/wp-content/uploads/2025/03/davis-et-al-2013-aarc-clinical-practice-guideline-blood-gas-analysis-and-hemoximetry-2013.pdf). | BGA 1.0; 4.6.5–4.6.8; 6.1.1–6.1.3, pp. 1694–1696. | PDF accesible; lectura de los apartados indicados. El [catálogo AARC](https://www.aarc.org/resource/clinical-practice-guidelines/) lo sitúa entre las guías de referencia de panel experto. El documento sigue siendo de 2013 aunque la URL contenga 2025. |
| S2 | AARC, *Capillary Blood Gas Sampling for Neonatal and Pediatric Patients*, 2022. Respiratory Care 67(9):1190–1204. DOI `10.4187/respcare.10151`. [PDF oficial](https://www.aarc.org/wp-content/uploads/2022/10/cpg-capillary-blood-gas-sampling.pdf). | Resumen, p. 1190; apartado de comparación arterial/venosa/capilar, p. 1193; tabla 1, p. 1194. | PDF accesible y apartados cotejados. Población neonatal y pediátrica; no se extrapola una equivalencia a adultos ni a cualquier condición de perfusión. |
| S3 | ANZSRS, posición sobre muestreo arterial, 2024. Seccombe et al., Internal Medicine Journal 54(7):1208–1213; publicación 16/07/2024. DOI `10.1111/imj.16439`. [Texto del editor](https://onlinelibrary.wiley.com/doi/10.1111/imj.16439). | Introducción; métodos; tabla 1; apartado de manejo de muestra y tabla 2. | HTML completo accesible, apartados cotejados. Posición de la sociedad australiana y neozelandesa en medicina respiratoria. La descarga del sitio de la sociedad devolvió 403; el contenido usado procede del editor. |
| S4 | Matthay et al., *A New Global Definition of Acute Respiratory Distress Syndrome*, 2024. AJRCCM 209(1):37–47. DOI `10.1164/rccm.202303-0558WS`. [Editor](https://academic.oup.com/ajrccm/article/209/1/37/8427597). | Resumen, resultados y tabla 1: criterios comunes y categorías específicas. | Texto de esos apartados recuperado mediante el índice público del editor. La apertura directa falló por redirección; [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC10870872/) mostró comprobación de navegador. No se declara lectura íntegra directa. Es una propuesta de consenso internacional, no prueba de adopción universal. |
| S5 | CLSI C46-A2, *Blood Gas and pH Analysis and Related Measurements*, segunda edición, 24/02/2009. [Catálogo oficial](https://clsi.org/shop/standards/c46/). | Ficha, alcance y aviso de archivo. | Solo catálogo público. La ficha declara el estándar archivado, sin revisión continua por el proceso de consenso de CLSI. No se obtuvo el estándar completo ni se atribuyen a él instrucciones no leídas. |

## Comparación con el módulo canónico

| Punto del módulo | Evidencia focal y conclusión | Límite que debe conservarse |
|---|---|---|
| Identificar muestra arterial, venosa o capilar; mantener desconocido lo no rotulado. | S1 exige procedencia de muestra; S2 distingue la utilidad ventilatoria/ácido-base del uso para oxigenación y sus condiciones pediátricas. La identificación explícita es concordante. | Una cifra de PO₂, su apariencia o la plausibilidad del resultado no acreditan procedencia arterial. Esta revisión no establece equivalencias generales de pH/PCO₂ entre tipos de muestra. |
| Confirmar calidad y contexto del resultado. | S3 describe alteraciones por demora, aire, mezcla con anticoagulante y transporte; S1 incluye contaminación y errores de obtención. | Una fotografía legible no permite certificar cómo se obtuvo, transportó o analizó la muestra. Registrar lo conocido y lo no evaluable; el tiempo o la condición de conservación aplicables dependen del procedimiento y del analizador. No se añade un límite numérico universal. |
| Separar medido de calculado y verificar la transcripción. | S1 distingue pH/PCO₂/PO₂ de magnitudes derivadas como bicarbonato y exceso de base. El módulo mantiene la comprobación de coherencia como apoyo. | La concordancia con una fórmula no demuestra que se haya leído correctamente el original ni valida el perfil del analizador. Las guías de muestreo no miden exactitud del OCR de Emergency. |
| Registrar FiO₂, dispositivo, momento y soporte; no deducir una FiO₂ fija del nombre del dispositivo. | S1 recoge FiO₂ o flujo y ajustes ventilatorios entre los datos de solicitud. Esto respalda conservar su procedencia. | El control de literal, unidad y corrección de T05 es un requisito del producto ya aceptado. No se deriva una nueva regla de admisión de estas fuentes ni se presume que flujo y FiO₂ sean intercambiables. |
| P/F como cuantificación, con criterios adicionales para SDRA. | S4 conserva temporalidad, imagen y valoración del origen del edema, y distingue categorías de soporte. El P/F aislado no basta. | La expresión «criterio de PEEP/soporte aplicable» debe seguir condicionada a la categoría: la propuesta incluye una adaptación para recursos limitados sin exigir PEEP o flujo mínimo. Este expediente no incorpora sus nuevos umbrales ni amplía automáticamente el algoritmo. |
| Revisión visual, incertidumbre, peligro y ruta al motor canónico. | Son controles descritos en los módulos y en T05; se conserva la separación entre transcripción y posterior interpretación. | La revisión focal no vuelve a adjudicar tratamientos, puntos de corte de analitos, sensibilidad diagnóstica ni todas las recomendaciones del motor ácido-base. |

La comparación identifica un límite adicional de la evidencia de imagen:
**transcripción correcta, muestra analíticamente válida e interpretación
clínica adecuada son resultados distintos**. El expediente de evaluación
debe poder atribuir un fallo a cada etapa. Esta es una consecuencia del
cotejo; no demuestra que alguno de esos fallos haya ocurrido en una cohorte
de Emergency.

## Qué acreditan las pruebas técnicas existentes

[PR #33](https://github.com/JuanCopado/Emergency/pull/33) integró T05. Su
entrega final fue `982c73c579db70a0c7dac3d648b88a19c0be9e1c`, árbol
`81111edf80771b9f9a3fe5517e2ed6b7ad5aa819`. En el
[job Windows conservado](https://github.com/JuanCopado/Emergency/actions/runs/44543684735/job/135628418213)
se observaron 80 pruebas sin omisiones y siete comprobaciones de navegador,
con extracción sintética real, revisión, FiO₂, revocación y cierre del
launcher. El commit de merge ejecutado fue
`134bcdb32ab2dad5c364028c69f25a2ecf90776c`, con ese mismo árbol. Es evidencia
técnica de aquella identidad, no una cohorte clínica.

Posteriormente, `b0d8eba6dc806731a6cfd05301e22b3a0d177dcf` modificó el
reconocimiento de etiquetas y metadatos en `blood_gas_review.py` y añadió una
regresión. No se atribuyen las cifras históricas de PR #33 a una ejecución
nueva de `cdca8e3` en este expediente. El informe de integración del
19/11/2026 conserva cortes anteriores y debe leerse con esa identidad.

La compatibilidad declarada en [LOCAL_REVIEW.md](../../docs/LOCAL_REVIEW.md)
y [BLOOD_GAS_LOCAL.md](../../docs/BLOOD_GAS_LOCAL.md) sigue siendo:

| Entorno | Capacidad y evidencia necesaria |
|---|---|
| Windows | Extracción mediante worker contenido con Job Objects. Un informe técnico del candidato debe identificar commit/árbol, dependencias/modelo, pruebas nativas sin omisiones, recorrido real y cierre. |
| Linux | Servidor y pruebas portables; la aplicación declara extracción no disponible y bloquea la carga. Ejecutar funciones OCR/PDF directamente no acredita extracción contenida de la aplicación. |

La extracción contenida para Linux requeriría una entrega de producto propia;
queda fuera de este cierre documental. La CSP no demuestra aislamiento de
red del sistema. Esta revisión documental no ejecuta suites, navegador ni
piloto.

## Continuación de PR #39: expediente evaluable pendiente

[PR #39](https://github.com/JuanCopado/Emergency/pull/39), integrado como
`4d2bb3eb0e51325723adc2c86635b7745092e6db`, contiene el protocolo de
[FOUR_YELLOW_REVIEW_20261120.md](FOUR_YELLOW_REVIEW_20261120.md). Se conserva
esa decisión de trabajo; no se vuelve a pedir su aceptación. El
[plan de validación de imagen](IMAGE_VALIDATION_ROADMAP_2026-11-14.md)
aporta la separación por paciente, las referencias y la distinción entre
evaluación reservada y piloto posterior.

El desafío `clinical/tests/blood_gas_photo_challenge.py` genera **tres campos
sintéticos y cinco variantes visuales del mismo ticket**. Ese número no es
un denominador de pacientes independientes. En los documentos inspeccionados
no se identifica una cohorte clínica evaluable de gasometrías con sus
originales, permisos, referencias y resultados. No se inventan tamaño,
dispositivos representados ni rendimiento.

Para hacer ejecutable el protocolo existente, el siguiente expediente debe
completar estos elementos antes de abrir el conjunto reservado:

| Elemento | Contenido concreto pendiente |
|---|---|
| Alcance y corpus | Identificador del conjunto; procedencia y uso autorizado; población y entorno; criterios de inclusión/exclusión; analizadores y formatos; calidad de imagen y campos disponibles. Original del analizador y muestra explícita por ticket, o incertidumbre registrada. |
| Independencia | Identificador disociado que permita agrupar tickets y variantes del mismo paciente, separar desarrollo de evaluación y evitar contar repetidamente una misma observación como independiente. No publicar identificadores clínicos. |
| Referencia | Transcripción fijada contra el original antes de mostrar la salida al evaluador; analito, literal, separador, unidad, tipo de muestra y metadatos. Procedimiento de resolución documentada de discrepancias. |
| Candidato congelado | Commit/árbol, versión del motor/OCR/modelo, configuración y plataforma; predicciones y referencias separadas. Cualquier cambio posterior debe quedar identificable. |
| Criterios previos | Definición de error crítico, abstención y dato no evaluable; reglas de aceptación por objetivo y cómo tratar resultados inciertos. Deben fijarse antes de conocer el rendimiento reservado. Aquí no se añaden umbrales ni tamaños de muestra. |

Los denominadores deben quedar explícitos en la tabla de resultados:

- **Por campo:** total de campos de referencia evaluables; coincidencias
  exactas de analito, cifra, separador y unidad; valores erróneos, omisiones
  y abstenciones. Contar aparte campos adicionales sin correspondencia.
- **Por ticket:** total evaluado y número con error de atribución de muestra;
  conservar también muestras desconocidas o no evaluables, sin reclasificarlas
  como arteriales por omisión.
- **Por paciente y dispositivo:** pacientes independientes, tickets y
  variantes; numerador y denominador de cada subgrupo, con sus limitaciones
  de precisión y representatividad.
- **Por etapa:** interpretación con transcripción de referencia, y después
  interpretación con la salida OCR, conservando ambas mediciones. Registrar
  fallos críticos y abstenciones sin eliminarlos del informe global.

Estas especificaciones desarrollan PR #39; no constituyen resultados
observados ni una autorización para cargar documentos de pacientes en el
entorno sintético actual.

## Siguiente cierre y coordinación

La revisión de fuentes queda preparada con sus localizadores y límites. La
evaluación clínica sigue necesitando el corpus autorizado y el expediente
anterior. Un piloto prospectivo silencioso es una fase posterior diferenciada
en el plan del proyecto; no se considera ejecutado o aprobado por las
pruebas sintéticas, por esta revisión de bibliografía o por un futuro buen
resultado retrospectivo.

La decisión clínica final corresponde al Dr. Juan Copado Ceballos conforme
a [AGENTS.md](../../AGENTS.md), conservando las aceptaciones ya concedidas y
su alcance. Cuando exista evidencia sustantiva adicional se presentará la
decisión concreta correspondiente; este documento no introduce otra firma
obligatoria ni repite la decisión de PR #39.

En STATE, HANDOFF y el [hilo común #18](https://github.com/JuanCopado/Emergency/issues/18)
inspeccionados no se encontró una asignación nominal vigente para completar
esta cohorte. Esa lectura no certifica el estado de chats externos. El
siguiente trabajo acotado es registrar el corpus realmente disponible y
completar referencia, denominadores y criterios previos, reutilizando el
protocolo existente. La coordinación general conserva la actualización de
cola, registro y STATE; este cambio solo añade el presente expediente.

**Límites de la entrega:** cotejo documental y de fuentes primarias en el
alcance indicado; sin imágenes de pacientes, ejecución clínica, cambios de
runtime, nuevas dosis ni promoción de evidencia. La consulta de S4 fue
parcial y la de S5 solo de catálogo. No se afirma una búsqueda exhaustiva de
todas las guías ni validación clínica de Emergency.
