# Diez módulos de imagen: cierres de referencia y validación pendiente

**Fecha:** 20/11/2026. **Expediente:** `IMG-CLOSURE-20261120`, versión 1.
**Estado vigente:** nueve referencias aceptadas por el propietario el 20/11/2026; `CLINICALLY_PENDING`.

**Actualización posterior a PR50:** respuesta «si claro que si», nueve fichas v1 aceptadas y POCUS-MODE v1 aplicado. Registro: **129 GREEN / 2 YELLOW**. El módulo padre de imagen conserva su condición de evaluación y sigue YELLOW, junto al apoyo diagnóstico de nota. Ver [aceptación](IMAGE_REFERENCE_OWNER_APPROVAL_20261120.md). El inventario siguiente se conserva como **mapa previo a la decisión**: sus expresiones de tareas/aceptaciones pendientes describen aquel corte, no el estado vigente.

Contenido clínico examinado: `21defd4efc4f1b6d15ddb28c655772ca3e4b8a0c`,
árbol `d4b2eba6048fe8b8731bb991ad126c8058a9755a`, tras PR47 y PR48.
Este documento se prepara sobre `e7c5722045852d654f756d5f3928d4c14daf2dbf`,
árbol `b49ea28981e84f234a90aa2095ac5bbebb4ef92d`; su cambio respecto a la
base examinada afecta a entrega de cobertura, pruebas de esa entrega y
continuidad, no a los diez módulos ni a sus registros de evidencia.

**Cierre de la entrega coordinada:** los trabajos bibliográficos acotados en
la tabla de §2 ya están completados en las fichas de
[gas/TC/ojo](IMAGE_REFERENCE_REVIEW_GAS_CT_EYE_20261120.md),
[ECG/POCUS](IMAGE_REFERENCE_REVIEW_ECG_POCUS_20261120.md) y
[tórax/piel/otras](IMAGE_REFERENCE_REVIEW_CXR_SKIN_OTHER_20261120.md).
Quedan sus nueve decisiones explícitas y la aplicación del candidato POCUS
si se acepta. El gate de referencia se cierra reutilizando PR35 y el registro
de la entrega pasa a 120 GREEN / 11 YELLOW; los diez IDs de esta tabla
permanecen YELLOW. El [resumen de decisiones](CLINICAL_CLOSURE_DECISIONS_20261120.md)
recoge el estado actual y los límites clínicos que siguen abiertos.

## 1. Resultado y criterio de cierre

Los diez IDs de este expediente siguen YELLOW. El corte base contenía
119 GREEN y 12 YELLOW; `clinical-note-diagnostic-support` y
`final-human-review-gate` tienen revisión separada. Este inventario no cambia
estados, fechas, guías, algoritmos ni la aceptación del propietario.

**La revisión bibliográfica puede completarse sin producir una nueva cohorte
cuando el objeto sea un marco de referencia y seguridad.** Debe contrastar
las afirmaciones realmente contenidas en ese marco, conservar sus límites
y obtener la decisión médica correspondiente. La ausencia de una cohorte
no convierte por sí sola una recomendación bibliográfica en obsoleta.
Tampoco una bibliografía actual demuestra que el producto interprete bien
una imagen.

Las reglas actuales distinguen tres cierres:

| Cierre | Qué exige el contrato vigente | Qué permite afirmar |
|---|---|---|
| Referencia clínica/bibliográfica | [`update-policy.md`, §E](../references/update-policy.md): revisión reciente, actualidad de la recomendación y ausencia de sustitución autoritativa localizada; expediente aplicable, discrepancias resueltas y aceptación expresa conforme a [`AGENTS.md`](../../AGENTS.md) y la [política de revisión final](final-human-review-policy.json). | Actualidad del contenido y alcance aceptado. No una cifra de exactitud del modelo. |
| Exactitud de una tarea de imagen | [IMAGE_VALIDATION_POLICY.md](IMAGE_VALIDATION_POLICY.md): pregunta preespecificada, datos autorizados, referencia independiente, separación por paciente/estudio, cegamiento y congelación antes del revelado, con los denominadores y abstenciones previstos. | Resultados de la tarea, versión y conjunto realmente evaluados. Los casos docentes o sintéticos no se suman a estas métricas. |
| Uso generalizable y despliegue | Evaluación prospectiva representativa para afirmaciones de rendimiento generalizable; controles de datos, privacidad, plataforma, operación y decisión clínica que correspondan al uso propuesto. | Solo el uso concreto autorizado y observado. Un GREEN de referencia no equivale a GO_RELEASE. |

Hay una **condición específica que no debe omitirse**: la nota actual de
`clinical-image-interpretation` exige casos representativos desidentificados,
adjudicación independiente y revisión de métricas de seguridad antes de
promover ese ID. Este expediente conserva esa condición. No la extrapola
automáticamente como requisito de cohorte para toda revisión bibliográfica
de los otros nueve IDs.

Existe un precedente concreto: `musculoskeletal-xray` está GREEN desde el
14/11 para el marco de lectura/seguridad reconciliado bibliográficamente,
con `image_cases_evaluated: 0`, rendimiento diagnóstico no validado y el
módulo padre aún YELLOW. Consta en el [registro](../references/evidence-registry.json)
y en [la revisión aceptada](PSYCHIATRY_IMAGING_CHEST_DISPOSITION_EYE_REVIEW_2026-11-14.json).
Este precedente aclara el significado del estado; no acepta automáticamente
ninguno de los diez módulos siguientes.

## 2. Mapa de los diez IDs

Las referencias de esta tabla son expedientes y decisiones ya existentes.
«Reutilizar» significa conservar su fuente, localizador, población y límite
de acceso; no atribuirles una nueva lectura íntegra ni extender su aceptación.
Las tareas bibliográficas pendientes deben acotarse a las afirmaciones del
módulo, no a una auditoría de toda una especialidad.

| ID y alcance canónico | Evidencia y cierres que ya se pueden reutilizar | Trabajo concreto para cerrar la referencia | Exactitud y despliegue que siguen separados |
|---|---|---|---|
| `clinical-image-interpretation` — especificación común de lectura, incertidumbre y abstención | [Expediente IMG-EVIDENCE](IMAGE_EVIDENCE_FOLLOWUP_20261120.md): consideraciones OMS y STARD-AI, con acceso parcial registrado; contrato interno de entrada/salida y política de evaluación ya existentes. | Consolidar trazabilidad de controles internos y fuentes metodológicas. La etiqueta de «conjunto interno de referencia» no acredita por sí misma un conjunto adjudicado. La condición específica de promoción descrita en §1 sigue abierta. | Evaluación representativa por uso previsto y revisión de errores de seguridad. Ningún resultado aislado de ECG acredita todas las modalidades. La privacidad y el despliegue deben corresponder al procesamiento real propuesto. |
| `blood-gas-image` — transcripción revisada, muestra, metadatos y ruta al motor canónico | [Dossier de gasometría](BLOOD_GAS_EVIDENCE_FOLLOWUP_20261120.md): AARC 2013/2022, ANZSRS 2024 y definición global SDRA 2024, con localizadores/accesos; marcos `acid-base-emergencies` y `diabetic-ketoacidosis-hhs` ya revisados; FiO₂ aceptada y T05 integrado. | Completar la matriz de los ocho párrafos: cautelas de lectura, muestra/preanalítica, unidades/valores derivados, oxigenación y remisión a alertas/síndromes canónicos. Vincular fuentes concretas al registro genérico actual. Para ese cierre de referencia no se necesita demostrar antes una tasa de acierto OCR. | El protocolo de [PR39](FOUR_YELLOW_REVIEW_20261120.md) sigue siendo el plan de evaluación: tickets independientes, referencia por campo, errores/omisiones/abstenciones y tipo de muestra. No hay cohorte de gasometrías identificada en estos expedientes. La extracción contenida T05 sigue siendo Windows; Linux bloquea la carga. |
| `chest-xray` — calidad técnica, revisión sistemática y alertas | Módulos revisados de SCA/EP y [dolor torácico no coronario](PSYCHIATRY_IMAGING_CHEST_DISPOSITION_EYE_REVIEW_2026-11-14.json) para sus límites clínicos; protocolos de entrada visual CXR existentes. | Falta un cotejo propio de sus cinco párrafos: documento/versiones concretos para adquisición AP/PA, proyección/calidad, limitaciones y alertas. La referencia genérica a la colección ACR no demuestra esa comparación. No se exige revisar toda la radiología torácica. | Para rendimiento, fijar una tarea antes de usar un conjunto. CheXpert y MIMIC tienen protocolos; el registro actual no confirma acceso a los archivos. Los ejemplos docentes de tórax no son una cohorte ciega. |
| `ct-mri-screenshot` — límites de capturas/series y signos de peligro | [IMG-EVIDENCE](IMAGE_EVIDENCE_FOLLOWUP_20261120.md): ACR estado mental 2024 y parámetro TC craneal 2025, con pasajes indexados y acceso limitado; protocolo RSNA ICH y render DICOM existentes. | Reconciliar por afirmación qué respalda la referencia craneal y qué es un control interno de cobertura/lateralidad. Completar los puntos aplicables de RM y otras regiones que el expediente focal no revisó. No usar el portal ACR como respaldo universal ni exigir leer guías ajenas al texto. | El registro conserva `actual_access_verified=false` para RSNA; faltan importación elegible y evaluación ciega. Ese objetivo de hemorragia intracraneal no validaría por sí solo RM, otras regiones o exclusión de todo un estudio. |
| `ecg-image` — trazado, calibración, lectura y alertas | [ECG/POCUS](ECG_POCUS_EVIDENCE_FOLLOWUP_20261120.md): fuentes focales ACC/AHA y SBC; [ECG-PT v1](ECG_PT_OWNER_APPROVAL_20261120.md) aceptado y aplicado en PR47; benchmark PTB-XL previo, descrito en §3. | **La corrección del epónimo está cerrada dentro de su alcance.** Completar el cotejo de estandarización, calibración, intervalos/conducción y afirmaciones no cubiertas por el dossier focal. Conservar la aceptación registrada, sin presentar otra vez la misma pregunta. | PTB-XL midió un baseline específico de ingeniería AFIB; no toda la lectura ECG ni ChatGPT. Una futura evaluación del intérprete necesita versión y tarea propias, y separación del conjunto ya revelado. No se reclasifica el benchmark histórico como validación general. |
| `ecg-pocus-integration` — contexto, discordancia y límites de exclusión | Marco `pocus` aceptado el 14/11; referencias ya revisadas de SCA/EP; [dossier focal](ECG_POCUS_EVIDENCE_FOLLOWUP_20261120.md). | Sus tres párrafos permiten un cierre de referencia acotado. Completar el respaldo de las menciones de enfermedad aórtica y taponamiento y documentar cómo se conservan los límites de estudios normales/limitados. No necesita una cohorte combinada para revisar ese consejo de integración. | Una afirmación de mejora diagnóstica por combinación ECG+POCUS sí necesita evaluación de ese uso y referencia independiente. No se deduce de validar cada entrada por separado. |
| `ophthalmology-image` — alcance de fotografía, OCT y exploración; alertas | [Revisión aceptada de oftalmología urgente](PSYCHIATRY_IMAGING_CHEST_DISPOSITION_EYE_REVIEW_2026-11-14.json) y registro GREEN de `ophthalmology-emergencies`: fuentes para quemadura, globo abierto, oclusión arterial, retina, celulitis y endoftalmitis; [IMG-EVIDENCE](IMAGE_EVIDENCE_FOLLOWUP_20261120.md) añade contraste focal de cierre angular. | Mapear sus tres párrafos contra esas referencias ya revisadas, respetando población y acceso. El dossier de cierre angular no cubre todas las alertas, pero tampoco obliga a empezar de cero: las otras fuentes ya constan. Mantener «presión cuando sea seguro» y exploración/dilatación apropiadas al caso. | El reconocimiento desde cada formato es una tarea diferente. No hay en los expedientes una cohorte del producto para esas tareas. Una referencia de exploración urgente no demuestra exactitud desde una foto u OCT. |
| `other-clinical-image` — descripción limitada y derivación fuera del alcance reconocido | Especificación común de imagen y sus reglas de incertidumbre; dos párrafos canónicos sin algoritmo de clasificación de una nueva especialidad. | Es un candidato documental pequeño: definir expresamente la referencia como límite de ámbito y derivación, sin prometer capacidad en anatomía patológica, endoscopia o medicina nuclear. Cotejarlo y someter ese alcance concreto a decisión, sin inventar una guía universal de «otras imágenes». | No existe una única exactitud evaluable de «otras imágenes». Si se pretende habilitar una tarea diagnóstica nueva, primero se define su objetivo, entradas, referencia y evaluación. No hace falta reunir una cohorte indefinida para revisar la regla de abstención. |
| `pocus-image` — formato/adquisición, descripción y límites dinámicos | [Aceptación del marco POCUS](POCUS_FRAMEWORK_OWNER_ACCEPTANCE_2026-11-14.json), sin extensión automática a este ID; [dossier 20/11](ECG_POCUS_EVIDENCE_FOLLOWUP_20261120.md), con Sonoguide pulmonar, cardíaco y venoso y límites de acceso a ACEP 2023. | Precisar una ambigüedad concreta de formato mediante el candidato `POCUS-MODE-20261120 v1`, §5. Después completar el cotejo de los cinco párrafos para un eventual cierre de referencia. No repetir la aprobación del marco `pocus` ya concedida. | Banco y evaluación por tarea previstos, no nuevos resultados. EchoNet carece de acceso real confirmado en el registro; mide un objetivo cardíaco concreto. E1 no ejecuta inferencia ciega ni admite vídeo en `blind_test`; no acredita signos dinámicos. |
| `skin-wound-image` — descripción, límites de la foto y alertas | Protocolo de [PR39](FOUR_YELLOW_REVIEW_20261120.md); marco revisado `dermatology-severe` para sus alertas aplicables. | Completar las referencias concretas para los cuatro párrafos, especialmente infección profunda y límites de lesión pigmentada. El protocolo metodológico de PR39 no es un cotejo de todas esas recomendaciones. Puede cerrarse la referencia descriptiva sin atribuir clasificación diagnóstica validada. | PR39 ya propone separar descripción/abstención de clasificación. Falta un corpus autorizado identificado con referencia y denominadores para el objetivo elegido; conservar variación de tono de piel, iluminación, zona y calidad, sin inventar tamaños o umbrales. |

Los tres IDs de prioridad estándar (`chest-xray`, `skin-wound-image` y
`other-clinical-image`) tienen fecha 27/09 y ventana de 90 días: a 20/11 no
están vencidos por antigüedad. Siguen YELLOW y requieren su cierre real; no
deben describirse como parte de los ocho avisos vencidos. Los otros siete
IDs de esta tabla son de prioridad alta y conservan sus fechas anteriores.

## 3. Datos reales previos y límite de E1

El repositorio **sí conserva un resultado exploratorio real previo de ECG**.
El [resultado PTB-XL NATURAL_500 v2](results/PTBXL_NATURAL500_V2_AFIB_BASELINE_V1_RESULT.json)
identifica run `37054176049`, artefactos, hashes y congelación en
`aa6649785c6dad3d9daa3838c902d3136774d624` antes del revelado. Registra 500
ECG, tres referencias AFIB, 93 abstenciones y dos no diagnósticos; cobertura
81 %. Las métricas binarias estándar están suprimidas por la política del
estudio. El algoritmo está definido en [PTBXL_AFIB_IMAGE_BASELINE_V1.md](PTBXL_AFIB_IMAGE_BASELINE_V1.md).

Ese resultado se conserva como baseline de ingeniería obtenido del render.
No es una evaluación de ChatGPT, no permite retocar umbrales usando ese mismo
conjunto revelado y no justifica GREEN clínico por sí solo. Aquí se leyó el
registro; no se reejecutó el benchmark ni se descargaron sus datos.

El [registro actual de fuentes de datasets](image-dataset-source-registry.json)
distingue preparación del protocolo de acceso efectivo: RSNA ICH, MIMIC-CXR,
CheXpert y EchoNet mantienen `actual_access_verified=false`. No se inventan
credenciales, DUA, autorizaciones individuales ni importaciones. Los cinco
archivos docentes descritos en la [hoja de ruta](IMAGE_VALIDATION_ROADMAP_2026-11-14.md)
tampoco constituyen un nuevo examen ciego.

[E1 en PR48](../../docs/MULTIMODAL_PROTOTYPE_USAGE.md) añade infraestructura
técnica: contratos, trazabilidad, admisión, congelación y puente de métricas.
Su demo tiene cero casos diagnósticos. No implementa custodia independiente
completa de acceso al examen, no ejecuta inferencia ciega y bloquea vídeo en
`blind_test`. Se reutilizan sus capacidades declaradas; no se repiten bancos
sintéticos para aparentar avance en exactitud clínica ni se exige terminarlos
otra vez para revisar bibliografía.

## 4. Pendientes que pueden reconciliarse sin nueva decisión clínica

1. **ECG-PT-20261120 v1:** la cola ya registra `owner_response: SI` y
   `clinical_content_activated: true`; la guía y ficha están corregidas tras
   PR47. No reaplicar el parche histórico ni repetir la pregunta del epónimo.
   `technical_qa_status` se ha reconciliado en la entrega coordinada como
   `postchange_ci_passed`, con los cuatro runs posteriores a PR47 observados.
   El recibo está en la ficha de aceptación; el estado de liberación global
   pendiente no se elimina por resolver ese metadato técnico.
2. **Continuidad anterior a PR47:** los pasajes de respuesta pendiente en los
   dossieres ya tienen una adenda que los identifica como históricos. La
   frase inicial de `SOURCES.md` y la instrucción de completar integración en
   la ficha de aceptación se han actualizado al cierre real. Se conserva el
   historial, sin convertir un estado antiguo en un nuevo bloqueo.
3. **Fuentes supuestamente ausentes:** enlazar las revisiones aceptadas de
   ácido-base, POCUS, SCA/EP, oftalmología y dermatología a las afirmaciones
   que efectivamente respaldan. La aceptación de esos módulos no se solicita
   de nuevo y tampoco se copia como aprobación de otro ID.
4. **Cierre técnico frente a exactitud:** T05/T06, Fase 5 y E1 tienen
   resultados y límites ya documentados. La continuación útil es completar
   las matrices de referencia o realizar la evaluación realmente pendiente,
   según el objetivo. No presentar más QA sintética como evidencia clínica.

## 5. Candidato concreto: POCUS-MODE-20261120 v1

**Estado:** candidato documental no activado. **Módulo:** `pocus-image`.
**Motivo:** la palabra general «still» puede confundirse con una captura de
un trazado M-mode, que incorpora información temporal. Es una ambigüedad de
formato identificada por lectura; no se declara un error diagnóstico observado
en pacientes o un fallo de rendimiento medido.

**Texto actual**, tercer párrafo de
[`image-modalities.md`](../modules/image-modalities.md#pocus-image):

> A still cannot prove lung sliding, compressibility, respiratory variation,
> valve motion, ejection fraction or dynamic response. One color-Doppler frame
> cannot establish absent flow.

**Texto propuesto v1**, para sustituir exclusivamente ese párrafo:

> A single static B-mode frame cannot establish lung sliding, compressibility,
> respiratory variation, valve motion, ejection fraction or dynamic response.
> An M-mode tracing of the pleural line contains temporal information along
> the sampled line; assess only the acquisition, location and recorded interval
> actually shown, with an identifiable time axis. It does not establish that
> a complete cine or compression sequence has been reviewed. One color-Doppler
> frame cannot establish absent flow.

### Fuente, alcance e impacto

- **Fuente consultada directamente el 20/11/2026:** ACEP Sonoguide,
  [Lung](https://www.acep.org/sonoguide/basic/lung), versión de página
  **08/03/2021**, sección II, apartado **Lung Sliding** y figura **8**;
  también identifica trazados M-mode en las figuras 9, 16 y 17. El HTML
  oficial fue accesible. Es material docente de la sociedad, no una nueva
  guía de 2026 ni un estudio de rendimiento de Emergency.
- El apartado distingue visualización B-mode de M-mode. El
  [dossier ECG/POCUS del 20/11](ECG_POCUS_EVIDENCE_FOLLOWUP_20261120.md) ya
  advertía que un trazado con eje temporal no equivale a un único fotograma
  B-mode. La propuesta lleva esa distinción al párrafo canónico con un límite
  explícito de lo realmente visible.
- El cambio conserva incertidumbre, adquisición identificable y confirmación
  humana. No habilita vídeo ciego ni el cálculo de función cardíaca; tampoco
  incorpora umbrales ni atribuye al modelo sensibilidad/especificidad. No permite
  declarar que se haya revisado un clip completo por ver una captura.
- Consumidores del cambio, si se acepta: sección `pocus-image` de
  `clinical/modules/image-modalities.md` y su proyección exacta en
  `app/src/data/generatedClinicalGuides.json`. El marco general `pocus`
  previamente aceptado conserva su alcance.

**Pregunta para decisión médica:** ¿Aprueba sustituir exclusivamente ese
párrafo de `pocus-image` por el texto **POCUS-MODE-20261120 v1** y regenerar
su ficha en la aplicación, manteniendo YELLOW, la fecha de revisión integral
y `CLINICALLY_PENDING`, sin habilitar nuevas capacidades de vídeo ni afirmar
rendimiento diagnóstico? **SÍ / NO**.

**Respuesta del propietario:** no registrada para esta propuesta. No se
interpreta la aprobación de ECG-PT, el marco POCUS general o PR48 como una
respuesta a esta pregunta. Este archivo no aplica el cambio ni modifica la
cola canónica. Si se acepta, corresponde conservar respuesta literal, fecha,
ID y versión y comprobar la proyección afectada; no se necesita ejecutar una
cohorte para demostrar la fidelidad de esa modificación textual.

## 6. Secuencia de trabajo acotada

El seguimiento de ECG ya aceptado está reconciliado y los nueve expedientes
completos están enlazados arriba. La continuación es la decisión explícita
sobre cada ficha y alcance; puede registrarse una respuesta que enumere los
IDs aceptados. No se agrupan diez estados en una aceptación genérica ni se
incluye implícitamente al padre de imagen en las fichas de referencia.

El candidato POCUS de §5 está definido para una decisión puntual. El resto
del cotejo de ECG, POCUS, tórax, TC/RM y piel conserva sus límites de fuente;
una comparación focal no se rotula como revisión integral. Solo cuando el
objetivo sea medir rendimiento se prepara el corpus y el protocolo específico
ya previsto, sin inventar nuevos mínimos, umbrales o métricas.

**Comprobaciones de esta entrega:** lectura de módulos, registro, cola,
políticas, decisiones y expedientes citados; consulta primaria focal de
ACEP para el candidato. Sin suites, benchmark adicional, inferencia clínica,
datos nuevos de pacientes ni cambios de producto. La mera incorporación de
este documento no cierra la validación de los diez IDs.

## 7. Ampliación documental de esta entrega

Tras este inventario se completó la matriz de todo el texto almacenado de
`ecg-image`, `pocus-image` y `ecg-pocus-integration` en
[IMAGE_REFERENCE_REVIEW_ECG_POCUS_20261120.md](IMAGE_REFERENCE_REVIEW_ECG_POCUS_20261120.md).
Sus fichas identifican el alcance de referencia ahora preparado y los
localizadores adicionales que resuelven los huecos bibliográficos señalados
arriba; no cambian la situación de rendimiento o despliegue.

La pregunta puntual de §5 conserva el alcance de un cambio de contenido sin
promoción de estado. La ficha ampliada **POCUS-REF-20261120 v1** incluye
expresamente el mismo texto **POCUS-MODE-20261120 v1** y añade la decisión
sobre el cierre bibliográfico tras su aplicación comprobada. Si se presenta
esa ficha ampliada al propietario, no hace falta repetir la pregunta puntual;
una aprobación limitada a esta última no se interpreta como aprobación del
alcance más amplio. Ambas siguen sin respuesta registrada en estos documentos.
