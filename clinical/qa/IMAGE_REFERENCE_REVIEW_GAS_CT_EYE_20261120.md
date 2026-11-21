# Revisión de referencia: gasometría, capturas TC/RM y ojo

**Fecha:** 20/11/2026 (Atlantic/Azores). **Versión:** 1.
**Expedientes:** `GAS-REF-20261120`, `CT-REF-20261120`, `EYE-REF-20261120`.
**Resultado:** cotejo documental completo de los párrafos actuales; decisiones
médicas de alcance concreto preparadas. No hay respuesta nueva del propietario
registrada en este documento. Se conserva `CLINICALLY_PENDING`.

## 1. Objeto e identidad

Se examinan los ocho párrafos de `blood-gas-image`, los nueve de
`ct-mri-screenshot` y los tres de `ophthalmology-image` en
[`image-modalities.md`](../modules/image-modalities.md). El contenido corresponde
a `21defd4efc4f1b6d15ddb28c655772ca3e4b8a0c` y no cambia en la corrección de
cobertura de PR49. SHA-256 de cada sección, desde su encabezado `##` hasta
el siguiente encabezado:

| ID | SHA-256 del texto examinado |
|---|---|
| `blood-gas-image` | `4f6b62a9e4d4f2b614c9a9d98087bf4d6930db6b09c6e275b4e3e2dd1b372163` |
| `ct-mri-screenshot` | `bd0afe958700dc84512650125a8106d63a617fd448093282fac5acd35637b04c` |
| `ophthalmology-image` | `81c99096193fd15a99ab67b2e16294b3fb4adfc62b04dc4cb7d174a32da948c6` |

Se distingue una recomendación respaldada por una fuente de una medida interna
de seguridad del producto. La segunda puede ser razonable y verificable sin
atribuirle un estudio de eficacia inexistente. Las aprobaciones de los módulos
canónicos relacionados se conservan; no se trasladan automáticamente a estos
tres IDs. El [mapa de imagen](IMAGE_VALIDATION_CLOSURE_20261120.md) recoge la
condición de evaluación independiente que sigue abierta para el módulo padre.

No se modifica aquí el texto, el registro, su fecha de revisión, el semáforo,
el motor ni una fórmula. Las referencias y propuestas de este documento son
revisables antes de cualquier activación.

## 2. Fuentes y acceso comprobado

Consulta focal realizada el 20/11/2026. Una fecha de alojamiento, rastreo o
descarga no se convierte en fecha de edición. «Pasajes indexados» no significa
lectura íntegra de un documento bloqueado.

| Clave | Fuente y versión | Localizador pertinente, acceso y límite |
|---|---|---|
| G1 | [AARC, Blood Gas Analysis and Hemoximetry, 2013](https://www.aarc.org/wp-content/uploads/2025/03/davis-et-al-2013-aarc-clinical-practice-guideline-blood-gas-analysis-and-hemoximetry-2013.pdf), DOI `10.4187/respcare.02786` | PDF accesible; apartados BGA 1.0, 3.1, 4.6.5–8 y 6.1, pp. 1694–1696. El [catálogo oficial](https://www.aarc.org/resource/clinical-practice-guidelines/) mantiene la referencia de 2013; el segmento 2025 de la URL no es otra edición. |
| G2 | [AARC, Capillary Blood Gas Sampling for Neonatal and Pediatric Patients, 2022](https://www.aarc.org/wp-content/uploads/2022/10/cpg-capillary-blood-gas-sampling.pdf), DOI `10.4187/respcare.10151` | PDF accesible; resumen/recomendaciones, p. 1190. Población neonatal y pediátrica: no se extrapolan al adulto equivalencias ni plazos de transporte. |
| G3 | [ANZSRS, posición sobre extracción de gasometría arterial, 2024](https://onlinelibrary.wiley.com/doi/10.1111/imj.16439), DOI `10.1111/imj.16439` | HTML completo accesible; preparación, muestreo y tabla 2 sobre interferencias de manejo. Respalda cautelas preanalíticas; no mide OCR ni el producto. |
| G4 | [ATS, Interpretation of ABGs](https://site.thoracic.org/assemblies/cc/clinical-education/interpretation-of-abgs), recurso educativo de David A. Kaufman | HTML oficial accesible; pasos 1–4, consistencia interna, pH normal y compensación. Sin atribuir una fecha editorial no indicada. |
| G5 | [A New Global Definition of ARDS, 2024](https://academic.oup.com/ajrccm/article/209/1/37/8427597), DOI `10.1164/rccm.202303-0558WS` | Tabla 1 y pasajes del texto primario recuperados por índice. El acceso directo a OUP y PMC no permitió lectura íntegra; no se declara. Se distinguen las categorías intubada, no intubada y de recursos limitados. |
| C1 | [ACR–ASNR–SPR, parámetro de TC de cabeza](https://gravitas.acr.org/PPTS/GetDocumentView?docId=76), revisión 2025, resolución 20 | Encabezado/versionado oficial y §IV.A–B recuperados por índice; descarga directa 403. Pasajes técnicos también indexados en el [PDF oficial](https://www.acr.org/-/media/ACR/Files/Practice-Parameters/CT-Head.pdf). No se certifica lectura completa ni edición independiente del enlace alternativo. |
| C2 | [ACS, Best Practices Guidelines: Management of Traumatic Brain Injury, 2024](https://www.facs.org/media/vgfgjpfk/best-practices-guidelines-traumatic-brain-injury.pdf) | PDF de 99 páginas accesible; lectura focal de Imaging, pp. impresas 12–14. Respalda planos/series pertinentes y signos intracraneales; no constituye revisión de todas las indicaciones de RM o TC corporal. |
| C3 | [DICOM PS3.3 2026d, §C.7.6.2](https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_C.7.6.2.html) | HTML oficial accesible; tabla C.7-10 y §C.7.6.2.1.1: orientación, posición y espaciado del paciente/imagen. Es una referencia de metadatos, no evidencia de exactitud clínica del visor. |
| E1 | [College of Optometrists, tabla de urgencia de derivación, anexo 4](https://www.college-optometrists.org/clinical-guidance/guidance/guidance-annexes/annex-4-urgency-of-referrals-table) | HTML público completo accesible; apartados anterior, posterior y órbita. Referencia profesional británica para alertas; no se importa un nuevo plazo universal ni una vía local de traslado. |
| E2 | [College of Optometrists, lesión química](https://www.college-optometrists.org/clinical-guidance/clinical-management-guidelines/trauma_chemical), 13/03/2026, versión 14 | Resumen público y notas de actualización accesibles/indexados. Detalle reservado a miembros no declarado leído. Cotejo limitado a irrigación inmediata y derivación. |
| E3 | [AAO, Open Globe Injury](https://www.aao.org/education/disease-review/open-globe-injury), 01/08/2020 | Texto educativo primario indexado: exploración y precauciones ante globo abierto. No se presenta como PPP nueva de 2026. |
| E4 | [AHA, CRAO: Top Things to Know](https://professional.heart.org/en/science-news/management-of-central-retinal-artery-occlusion/top-things-to-know), 08/03/2021; declaración DOI `10.1161/STR.0000000000000366` | Resumen oficial completo accesible; puntos 4, 5.1 y 10. Se utiliza exploración y urgencia; no se incorpora aquí una indicación de trombólisis. |
| E5 | [College of Optometrists, cierre angular](https://www.college-optometrists.org/clinical-guidance/clinical-management-guidelines/primaryangleclosure_primaryangleclosureglaucoma_pa), 01/09/2026, versión 18 | Resumen público/actualizaciones accesibles; carácter urgente del ataque agudo. No se añaden fármacos ni se ignoran mecanismos secundarios. |
| E6 | [College of Optometrists, celulitis preseptal/orbitaria](https://www.college-optometrists.org/clinical-guidance/clinical-management-guidelines/cellulitis_preseptalandorbital), 14/10/2025, versión 15 | Resumen público indexado; riesgo visual/sistémico y derivación urgente ante sospecha orbitaria. No se prescribe un régimen antibiótico nuevo. |

Se reutilizan, con su alcance y límites de acceso originales, las revisiones
aceptadas del registro: `acid-base-emergencies` y
`traumatic-intracranial-mass-effect` (14/11),
`diabetic-ketoacidosis-hhs` y `pulmonary-embolism` (13/11), y
`ophthalmology-emergencies` (14/11). Esta última contiene también la PPP
retiniana AAO 2025 y la fuente del College sobre endoftalmitis. Sus alertas
se contrastan ahora con E1; no se afirma haber releído íntegramente esas PPP.
Expedientes: [fisiología](NINE_SELECTED_MODULES_REVIEW_2026-11-14.json),
[DKA/HHS](SIX_EVIDENCE_RECONCILIATIONS_2026-11-13.json),
[TCE](TBI_AND_EIGHT_PEDIATRIC_REVIEW_2026-11-14.json),
[EP](PE_OWNER_CONCORDANCE_GREEN_2026-11-13.json) y
[oftalmología](PSYCHIATRY_IMAGING_CHEST_DISPOSITION_EYE_REVIEW_2026-11-14.json).

## 3. GAS-REF-20261120 v1: ocho párrafos

| Párrafo actual | Cotejo y decisión propuesta |
|---|---|
| 1. Tipo de informe y valores realmente visibles | G1 distingue resultados y variables analíticas. Exigir visibilidad, unidades y banderas es control interno de entrada: conservarlo, sin atribuir precisión OCR. |
| 2. Muestra, hora y oxígeno | G1 identifica muestra/oxígeno/metadatos; G2 acota el uso capilar y venoso. Conservar la prohibición de asumir muestra arterial o interpretar PO₂ venosa como PaO₂. |
| 3. Dígitos, decimales, desigualdades y calidad | G3 describe errores preanalíticos; el cotejo visual y la prohibición de reparar dígitos son controles internos adicionales. Ninguna fuente prueba que el programa detecte todos esos errores. Conservar. |
| 4. Medido frente a calculado y consistencia | G1 y G4 respaldan esa distinción y el contraste fisiológico. La coherencia matemática no acredita fidelidad de transcripción, porque los valores derivados pueden compartir el error. Conservar esa limitación. |
| 5. Oxigenación | La conversión de FiO₂ y las condiciones de cálculo remiten al marco fisiológico canónico ya aceptado. G5 exige más que un cociente P/F para SDRA. «Applicable» es necesario: la categoría de recursos limitados no exige el mismo soporte/PEEP que las demás. Conservar sin imponer un criterio único ni añadir umbrales. |
| 6. Segunda pasada de peligro | G4 advierte que pH próximo a normal no descarta trastorno; G3 respalda considerar problemas de muestra. La selección de analitos y la urgencia se remiten a los módulos canónicos ácido-base/electrolitos/DKA. Conservar repetición de un valor inesperado sin retrasar atención si existe peligro clínico. No añadir límites analíticos universales. |
| 7. Ruta a ácido-base y DKA/HHS | Es trazabilidad interna hacia módulos aceptados, con valores verificados. El motor T05 no se revalida clínicamente por revisar este enlace. Conservar. |
| 8. Prioridad del peligro y contexto seriado | G1 contempla evaluación y respuesta a tratamiento; G4 limita inferencias de un equilibrio aislado. Conservar el contexto clínico/temporal y evitar inferir etiología o cronicidad definitiva de una sola gasometría. |

**Resultado:** no se identifica en este cotejo una corrección de fórmula,
umbral o conducta necesaria en los ocho párrafos. La fuente antigua AARC
2013 se contextualiza con 2022/2024 y el marco canónico vigente; no se
etiqueta como reemplazada solo por su edad. Los controles de OCR siguen
siendo requisitos de proceso cuya eficacia debe medirse aparte.

**Pregunta concreta:** ¿Aprueba `GAS-REF-20261120 v1` para registrar como
actual el marco de referencia de los ocho párrafos de `blood-gas-image`,
vincular estas fuentes y pasar únicamente su evidencia de referencia a GREEN,
sin atribuir exactitud OCR, validación del analizador local ni GO_RELEASE?
**SÍ / NO. Respuesta: pendiente.**

## 4. CT-REF-20261120 v1: nueve párrafos

| Párrafo actual | Cotejo y decisión propuesta |
|---|---|
| 1. Identificación de técnica/serie | C1–C2 distinguen protocolos, ventanas y secuencias. Registrar lo mostrado es control de alcance, no inferir la serie ausente. Conservar. |
| 2. Revisión intracraneal sistemática | C2 identifica compartimentos y signos de efecto de masa; C1 requiere presentación adecuada. La lista anatómica ordena la inspección interna, sin demostrar sensibilidad ni sustituir revisión completa. Conservar. |
| 3. Navegación y planos | C1–C2 apoyan información contigua y planos pertinentes. «Inicio, mitad y final» es una heurística interna de navegación, no una pauta validada para declarar negativo un examen. Los párrafos 5–6 siguen exigiendo cobertura adecuada y prohíben extrapolar a cortes ausentes. Conservar con esa lectura explícita. |
| 4. Lateralidad | C3 define orientación/posición del paciente. La cautela ante captura sin marcador es una inferencia de seguridad: no asumir que el lado de pantalla identifica al paciente. Conservar. |
| 5. Negativos intracraneales | C1–C2 requieren imágenes y presentación apropiadas. La condición de cobertura es interna y más limitada que una lectura radiológica completa; su cumplimiento no mide rendimiento. Conservar abstención cuando faltan regiones/ventanas. |
| 6. Captura frente a estudio | Control explícito de ámbito: los píxeles recibidos no contienen las regiones/series ausentes. No es una promesa de excluir enfermedad aunque la captura parezca normal. Conservar. |
| 7. Mediciones, realce y difusión | C3 muestra la dependencia de datos espaciales; C2 distingue las secuencias DWI/ADC de otras imágenes. Exigir los datos pertinentes es un límite, no un algoritmo para cuantificar HU o diagnosticar restricción desde cualquier captura. Conservar. |
| 8. Sospecha de proceso crítico | Se trata de escalar una sospecha y obtener estudio completo/experto, sin activar diagnóstico definitivo o tratamiento por una captura. C2 y los marcos canónicos urgentes respaldan la prioridad; no se traslada evidencia de TC craneal a exactitud para LVO, EP o disección. Conservar. |
| 9. Compartimento y peligro por efecto de masa | C2 y el marco TCE ya aceptado respaldan separar la colección de sus signos de compromiso. La ruta canónica conserva sus criterios y decisiones. Conservar; no añadir umbrales neuroquirúrgicos. |

**Resultado:** cotejo suficiente para el marco limitado de seguridad y
derivación, con acceso parcial ACR declarado. No se ha revisado toda la
radiología ni se afirma exactitud en TC/RM, exclusión de un estudio completo
o eficacia de la heurística de navegación. La parte no craneal del texto es
un límite de uso y una indicación de confirmación, no un nuevo algoritmo
clínico de otra región. Si se pretendiera convertirla en uno, requeriría su
propio alcance y evaluación.

**Pregunta concreta:** ¿Aprueba `CT-REF-20261120 v1` para el marco de seguridad
y derivación de los nueve párrafos de `ct-mri-screenshot`, enlazar las fuentes
y pasar únicamente su evidencia de referencia a GREEN, conservando la
restricción de capturas/series incompletas y sin validar capacidad diagnóstica
ni autorizar GO_RELEASE? **SÍ / NO. Respuesta: pendiente.**

## 5. EYE-REF-20261120 v1: tres párrafos

| Párrafo actual | Cotejo y decisión propuesta |
|---|---|
| 1. Formato, lateralidad y estructura visible | Identificar la adquisición y limitarse al contenido visible es control de entrada. No se afirma que fotografía externa, fondo y OCT sean intercambiables ni que una imagen permita evaluar estructuras ausentes. Conservar. |
| 2. Exploración presencial y seguridad | E3–E4 y la revisión de oftalmología aceptada respaldan exploración pertinente al problema. «Pressure (when safe)» preserva la cautela ante globo abierto; «appropriate» no ordena dilatación universal en cualquier ojo. Conservar ambas condiciones. |
| 3. Alertas y quemadura | E1 cubre las alertas enumeradas; E2–E6 corroboran quemadura, globo abierto, CRAO, cierre angular y celulitis. La retina/endoftalmitis se vincula también a las fuentes ya revisadas. Conservar irrigación antes de obtener fotografías en exposición química. No incorporar aquí dosis, nuevos tiempos de derivación ni recetas de especialidad. |

**Resultado:** los tres párrafos son coherentes como marco descriptivo y
de alerta, apoyado en fuentes profesionales y en el módulo canónico ya
aceptado. Los límites de acceso a guías completas no impiden cotejar estas
afirmaciones públicas concretas, pero impiden atribuir una revisión de todo
el contenido de esas guías. No existe aquí una validación del reconocimiento
desde fotos, OCT, fondo o lámpara de hendidura.

**Pregunta concreta:** ¿Aprueba `EYE-REF-20261120 v1` para el alcance
descriptivo, exploración segura y alertas de los tres párrafos de
`ophthalmology-image`, enlazar estas fuentes y pasar únicamente su evidencia
de referencia a GREEN, conservando el módulo padre pendiente y sin atribuir
rendimiento diagnóstico ni GO_RELEASE? **SÍ / NO. Respuesta: pendiente.**

## 6. Aplicación posterior y comprobaciones

Una respuesta afirmativa se registra con literal, fecha, expediente, versión
y alcance; el registro solo cambia para los IDs aceptados y con el alcance
documentado. No se vuelve a solicitar la aceptación de ácido-base, TCE,
DKA/HHS, EP u oftalmología urgente ya registrada. Una respuesta negativa
mantiene el candidato pendiente y permite señalar la discrepancia concreta.

Este expediente completa el cotejo de referencia que faltaba, sin ejecutar
un conjunto de pacientes. El plan de evaluación permanece en la
[política de imagen](IMAGE_VALIDATION_POLICY.md) y en los protocolos ya
existentes. No se inventan tamaño de muestra, acceso a datasets, adjudicadores,
métricas de OCR/visión o validación del entorno asistencial.
