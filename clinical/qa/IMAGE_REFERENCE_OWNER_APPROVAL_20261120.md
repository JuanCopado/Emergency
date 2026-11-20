# Aceptación médica de nueve referencias de imagen · 20/11/2026

**Registro:** `IMAGE-REF-OWNER-20261120`, versión 1.

**Autor de la decisión clínica:** Dr. Juan Copado Ceballos, médico propietario del proyecto.

**Estado global conservado:** `CLINICALLY_PENDING`. **Sin `GO_RELEASE`.**

## 1. Respuesta y alcance presentado

En la conversación del proyecto se presentaron las nueve fichas **v1, de
20/11/2026**, enumeradas en este recibo, con sus alcances de referencia y
sus límites. La pregunta incluyó expresamente la sustitución textual
**`POCUS-MODE-20261120 v1`**, su aplicación y comprobación. Los expedientes
completos se habían publicado en PR50 y se enlazaron para su revisión.

El propietario respondió literalmente:

> si claro que si

**Decisión registrada: SÍ a las nueve fichas v1 enumeradas, incluida
`POCUS-MODE-20261120 v1`.** Fecha de respuesta: **20/11/2026**, contexto
`Atlantic/Azores`. No se dispone de una marca horaria exacta del mensaje del
propietario; no se le atribuye una. La coordinación registró la respuesta a
las `2026-11-20T20:06:31Z` (`19:06:31-01:00` en Atlantic/Azores); esa es una
hora de registro, no una firma ni la hora demostrada del mensaje.

La aceptación corresponde a las versiones concretas ya presentadas, conforme
a [`AGENTS.md`](../../AGENTS.md) y a la
[plantilla de revisión](HUMAN_REVIEW_TEMPLATE.md). No se solicita de nuevo la
misma decisión. Este recibo transcribe la respuesta; no sustituye esa respuesta
por una aprobación inferida de pruebas técnicas.

## 2. Identidad del material aceptado

- Repositorio: `JuanCopado/Emergency`.
- Commit presentado, posterior a PR50:
  `49bd2dee35c678f9f9184803c1a4e95e588e98a5`.
- Árbol del material presentado:
  `45a9d58186f82a5868e6e084950c76fe3b8c96f4`.
- Rama de integración autorizada:
  `codex/v144-international-scope-20261116`.
- Expediente coordinador:
  [CLINICAL_CLOSURE_DECISIONS_20261120.md](CLINICAL_CLOSURE_DECISIONS_20261120.md),
  especialmente §§2–4.

Las siguientes huellas SHA-256 identifican los bytes revisados en ese commit.
Las anotaciones posteriores de aceptación o ejecución no cambian cuál fue
el material presentado al propietario.

| Documento en `clinical/qa/` | SHA-256 en el commit presentado |
|---|---|
| `CLINICAL_CLOSURE_DECISIONS_20261120.md` | `1b620790d83b1085d0f8a63955cca2425497503bd43c5d378a616b14ada9294a` |
| `IMAGE_REFERENCE_REVIEW_GAS_CT_EYE_20261120.md` | `91f718dd17a9defec98e2c679de7103a9bdc5b0a2412c521f86d830e46346115` |
| `IMAGE_REFERENCE_REVIEW_CXR_SKIN_OTHER_20261120.md` | `f4134ae38adb8b3bb91f015bf62578d6ba4c23666c508696d52f289fbcc40d85` |
| `IMAGE_REFERENCE_REVIEW_ECG_POCUS_20261120.md` | `09e5e208baff73150b168eaf778cf4ba128943ca327dcb5d1183837a78357af8` |

Las matrices de esos tres expedientes contienen el cotejo de las afirmaciones,
las fuentes primarias con versiones y localizadores, las discrepancias y los
límites de acceso. Este recibo registra su decisión y conserva aquellas
delimitaciones; no afirma una nueva revisión íntegra de las fuentes que los
expedientes identificaron como parcialmente accesibles.

## 3. Decisiones individualizadas

La respuesta literal del apartado 1 se aplica a cada fila, todas **versión 1**.

| Ficha | Módulo canónico | Decisión y alcance aceptado | Límite conservado |
|---|---|---|---|
| `GAS-REF-20261120` | `blood-gas-image` | **SÍ.** Ocho párrafos: transcripción verificada, muestra y metadatos, límites de oxigenación y remisión al motor canónico. | No acredita exactitud de OCR ni interpretación clínica autónoma. |
| `CT-REF-20261120` | `ct-mri-screenshot` | **SÍ.** Nueve párrafos: seguridad, límites de capturas y series, y derivación. | No permite excluir patología de un estudio completo a partir de capturas. |
| `EYE-REF-20261120` | `ophthalmology-image` | **SÍ.** Tres párrafos: descripción, exploración segura y alertas. | No acredita reconocimiento diagnóstico desde fotografía u OCT. |
| `IMG-REF-CXR-20261120` | `chest-xray` | **SÍ.** Cinco viñetas: descripción, calidad, límites de exclusión y escalada. | No acredita exactitud de interpretación visual. |
| `IMG-REF-SKIN-20261120` | `skin-wound-image` | **SÍ.** Cuatro viñetas: descripción, límites de fotografía y derivación o escalada. | No acredita exclusión de melanoma o infección profunda por imagen. |
| `IMG-REF-OTHER-20261120` | `other-clinical-image` | **SÍ.** Dos viñetas: límites, abstención y derivación especializada. | No habilita interpretación diagnóstica de nuevas modalidades. |
| `ECG-REF-20261120` | `ecg-image` | **SÍ.** Referencias del texto actual, incluida la definición ECG-PT ya aplicada, con abstención ante calidad insuficiente y descripción contextual. | No reabre la aceptación de ECG-PT ni acredita lectura o medición automática. |
| `ECG-POCUS-REF-20261120` | `ecg-pocus-integration` | **SÍ.** Integración contextual, discordancias, reevaluación y límites de estudios focales. | No acredita rendimiento diagnóstico combinado. |
| `POCUS-REF-20261120` | `pocus-image` | **SÍ.** Marco completo de referencia, incluida la sustitución exacta `POCUS-MODE-20261120 v1` del apartado 4 y su aplicación comprobada. | No añade capacidades de vídeo ni acredita exactitud diagnóstica o revisión de secuencias completas. |

Expedientes de evidencia aplicables:

- [Gasometría, TC/RM y ojo](IMAGE_REFERENCE_REVIEW_GAS_CT_EYE_20261120.md).
- [Tórax, piel/herida y otras imágenes](IMAGE_REFERENCE_REVIEW_CXR_SKIN_OTHER_20261120.md).
- [ECG, POCUS e integración](IMAGE_REFERENCE_REVIEW_ECG_POCUS_20261120.md).

En las primeras ocho fichas se acepta conservar el texto clínico revisado.
La novena acepta una única aclaración clínica textual, definida a continuación.
La aceptación conserva el núcleo internacional y las poblaciones, formatos
y límites definidos en cada expediente; no selecciona un país u hospital.

## 4. POCUS-MODE-20261120 v1: sustitución aceptada

Se acepta reemplazar exclusivamente el tercer párrafo de `pocus-image` en
`clinical/modules/image-modalities.md` y actualizar su proyección generada en
`app/src/data/generatedClinicalGuides.json`.

**Texto anterior**, normalizado como una línea sin marcador de viñeta:

> A still cannot prove lung sliding, compressibility, respiratory variation, valve motion, ejection fraction or dynamic response. One color-Doppler frame cannot establish absent flow.

**Texto aceptado**, normalizado del mismo modo:

> A single static B-mode frame cannot establish lung sliding, compressibility, respiratory variation, valve motion, ejection fraction or dynamic response. An M-mode tracing of the pleural line contains temporal information along the sampled line; assess only the acquisition, location and recorded interval actually shown, with an identifiable time axis. It does not establish that a complete cine or compression sequence has been reviewed. One color-Doppler frame cannot establish absent flow.

La evidencia y su conciliación están en el dossier ECG/POCUS, §3.2 U1–U6 y
§5, con el contraste focal de **ACEP Sonoguide, Lung, 08/03/2021, §II
«Lung Sliding», figura 8**. La aceptación no convierte ese material docente
en una guía nueva de 2026 ni en resultados de rendimiento de Emergency.

Identidad exacta de la propuesta aprobada:

| Elemento | Identidad |
|---|---|
| [Parche presentado](proposals/POCUS_MODE_20261120_v1.patch) | SHA-256 `f7c01481303505274fb4af89837efb9de1d7f82894645a8712a367c31b9a4fc1`; 4.311 bytes |
| Párrafo anterior | SHA-256 `84efaed0576614507a5866d6bf06133841852108d8842c265ad0e505b03932d6` |
| Párrafo aceptado | SHA-256 `8cc70c79846ab441671acdd783dedbad008f33986da9fd6a7b2488701a1ef70c` |
| Recibo de preparación | [POCUS_MODE_20261120_v1.receipt.json](proposals/POCUS_MODE_20261120_v1.receipt.json) |

Las huellas de párrafo usan UTF-8, una línea exacta, sin marcador de cita o
viñeta y sin salto final. El recibo de preparación documenta el estado
**INACTIVE anterior a la decisión** y sus comprobaciones de candidato. Esas
comprobaciones previas no acreditan por sí solas su aplicación posterior.
La aceptación de `POCUS-REF-20261120 v1` ya incluye esta sustitución; no hace
falta otra pregunta médica sobre el mismo texto.

## 5. Efecto autorizado y verificación de aplicación

La aceptación permite registrar el literal, la fecha, las nueve fichas y sus
módulos en la trazabilidad, cerrar sus revisiones de referencia y actualizar
sus estados a GREEN cuando quede aplicada y comprobada la versión aceptada.
Para POCUS, esa condición incluye el párrafo exacto y su proyección generada.

El registro presentado tenía **120 GREEN / 11 YELLOW / 0 RED** sobre 131
módulos. El efecto de aplicar y verificar estas nueve decisiones es
**129 GREEN / 2 YELLOW / 0 RED**. Es el resultado autorizado de la aplicación,
no una medición de sensibilidad, especificidad, calibración o seguridad
prospectiva. Este recibo acredita la aceptación; la ejecución efectiva y
sus comprobaciones deben quedar reflejadas en el registro de evidencia,
la cola, el estado vigente y los checks de la entrega correspondiente.

La verificación del delta debe confirmar el texto aceptado de POCUS, su
proyección, los nueve módulos afectados y la preservación del resto de
aceptaciones. Los expedientes de revisión y sus límites se conservan como
procedencia. No se renuevan otras fechas de evidencia por esta decisión.

## 6. Alcances que permanecen pendientes

| Módulo | Estado conservado y evidencia que sigue faltando |
|---|---|
| `clinical-image-interpretation` | **YELLOW.** Casos representativos para el uso previsto, desidentificación y autorización, adjudicación independiente y revisión de métricas de seguridad. El trabajo previo PTB-XL y la infraestructura E1 conservan sus alcances; esta aceptación no los extrapola a la interpretación general del producto. |
| `clinical-note-diagnostic-support` | **YELLOW.** Validación clínica del apoyo diagnóstico y del uso propuesto. La reparación de procedencia no resuelve por sí sola `evidence_against` vacío, los datos discriminantes estáticos ni las cuatro relaciones `must_not_miss` sin regla resoluble documentadas. |

Se mantienen las condiciones aplicables de producto, privacidad, operación
y despliegue, así como `CLINICALLY_PENDING` y la ausencia de `GO_RELEASE`.
Los detalles están en el [mapa de imagen](IMAGE_VALIDATION_CLOSURE_20261120.md)
y en el [dossier de procedencia de nota](NOTE_PROVENANCE_CLOSURE_20261120.md).

La respuesta médica no demuestra que se haya cambiado la configuración
**Automatic Analysis** de Sonar ni que haya finalizado su comprobación
posterior al merge. Ese ajuste y el resultado técnico se verifican y
registran por separado; este recibo no los declara completados.

## 7. Aceptaciones previas preservadas

Se conservan en sus alcances PR35 y la política del revisor médico final,
ECG-PT, el marco POCUS general ya aceptado, los 19 contratos agudos y sus
46 IDs, los 13 formularios de escalas, los circuitos del selector y las
decisiones T02. No se exige otra firma de Farmacia ni se restablecen
bloqueos administrativos históricos. `main`, RC1 y v1.43 permanecen fuera
de la entrega autorizada.

## 8. Aplicación y comprobación observadas

Se aplicó el parche exacto sobre `49bd2dee35c678f9f9184803c1a4e95e588e98a5`. La huella del tercer párrafo coincide con la propuesta aceptada; la proyección conserva los otros 130 textos de guía y cambia únicamente los nueve estados aceptados. Registro resultante: **129 GREEN / 2 YELLOW / 0 RED**. Los dos registros padre y las restantes fechas/aceptaciones permanecen intactos. Las tres matrices de fuentes mantienen sus bytes y hashes.

Validación focal ejecutada: 131 módulos resueltos, catálogo de 254 fuentes coherente, auditor de evidencia con 0 errores y 1 aviso de antigüedad del padre de imagen; 12 pruebas de proyección, 4 de normalización y 2 del gate PASS. La cola final contiene exactamente los dos módulos pendientes. El [recibo JSON](IMAGE_REFERENCE_OWNER_APPROVAL_20261120.json) registra estos resultados. Los checks remotos de publicación/integración se consultan por el commit de entrega; no se atribuyen anticipadamente.

Sonar de la base PR50: reintento 2 del run 44805197675, job 136538151239, **QUALITY GATE STATUS: PASSED** a las 20:09:13Z del 20/11/2026. Se recuperaron los artefactos originales 14662802790, 14662283369 y 14662811742 y se analizaron `coverage.xml` y `app/coverage/lcov.info`. Artefacto combinado 14664890392. Este resultado supera el bloqueo previo en esa ejecución; no se afirma haber visto el ajuste de Automatic Analysis ni que esta aceptación médica lo haya cambiado.
