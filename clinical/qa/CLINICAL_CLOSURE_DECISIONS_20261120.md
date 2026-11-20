# Cierre técnico y decisiones clínicas preparadas · 20/11/2026

**Estado global: CLINICALLY_PENDING. Sin GO_RELEASE.**

Este expediente coordina el trabajo solicitado tras resolver la entrega de
cobertura a Sonar. Las matrices enlazadas contienen el cotejo completo de las
afirmaciones almacenadas, sus fuentes/versiones/localizadores, los límites de
acceso y las discrepancias conciliadas. No se presenta una lista de portales
como revisión clínica ni se equipara QA automática con rendimiento diagnóstico.

## 1. Qué queda cerrado en esta entrega

| Pendiente | Resultado y evidencia |
|---|---|
| Entrega de cobertura a Sonar en reintentos | Corrección por ejecución y módulo integrada en PR49, merge `f45b6286fa97ddb03be57005c5a90f916e9042e5`; PR y rama PASS. El reintento real exclusivo de Sonar, job `136511548666`, descargó la cobertura original de los tres productores, comprobó su identidad y pasó el quality gate. [Recibo técnico](../../security/SONAR_COVERAGE_RETRY_2026-11-20.md). |
| Seguimiento de ECG-PT ya aceptado | PR47 integrada; cuatro workflows posteriores al merge PASS. La cola y la [aceptación](ECG_PT_OWNER_APPROVAL_20261120.md) reflejan el resultado. No se vuelve a pedir esa aprobación. |
| Procedencia de la nota clínica | Corregidas 18 referencias de síndrome y una referencia vasoactiva. Los 60 casos conservan todos los resultados ajenos a `source_modules`; 31 cambian solo esas referencias. [Dossier y regresiones](NOTE_PROVENANCE_CLOSURE_20261120.md). |
| Referencia de `final-human-review-gate` | Cotejo completo contra la norma y el código aceptados en PR35, sin cambios materiales. Se reutiliza aquella aceptación y se registra GREEN exclusivamente para esta referencia. [GATE-REF v1](CLINICAL_GATE_REFERENCE_REVIEW_20261120.md). |
| Notas actuales con bloqueos obsoletos | Conciliadas las de ácido-base, ortopedia y apoyo de nota con los 19 contratos ya aceptados el 16/11; sus fechas clínicas no se renuevan. Los documentos históricos siguen identificando sus propios cortes. |

La última acción de referencia lleva el registro de **119 GREEN / 12 YELLOW**
a **120 GREEN / 11 YELLOW / 0 RED**, siempre sobre 131 módulos. Las nueve
fichas de imagen siguientes aún no cambian su estado o fecha; los dos módulos
padre pendientes tampoco. La fuente primaria del gate es la directriz del
propietario ya aceptada, no una firma nueva atribuida a este expediente.

## 2. Nueve decisiones de referencia listas para el propietario

Todas las fichas son **versión 1**, con fecha **20/11/2026**. En las primeras
ocho se conserva el texto clínico actual. La novena incluye una única
aclaración textual, definida y preparada como parche inactivo.

| Ficha | Módulo | Alcance exacto de un SÍ |
|---|---|---|
| `GAS-REF-20261120` | `blood-gas-image` | Marco de transcripción verificada, muestra/metadatos, límites de oxigenación y remisión al motor canónico; ocho párrafos. No exactitud OCR. |
| `CT-REF-20261120` | `ct-mri-screenshot` | Seguridad, límites de capturas/series y derivación; nueve párrafos. No capacidad para excluir patología de un estudio completo. |
| `EYE-REF-20261120` | `ophthalmology-image` | Descripción, exploración segura y alertas; tres párrafos. No reconocimiento validado desde fotografía/OCT. |
| `IMG-REF-CXR-20261120` | `chest-xray` | Descripción, calidad, límites de exclusión y escalada; cinco párrafos. No interpretación visual validada. |
| `IMG-REF-SKIN-20261120` | `skin-wound-image` | Descripción, límites de la fotografía y derivación; cuatro párrafos. No exclusión de melanoma o infección profunda por imagen. |
| `IMG-REF-OTHER-20261120` | `other-clinical-image` | Límites, abstención y derivación; dos párrafos. No habilitación de nuevas modalidades diagnósticas. |
| `ECG-REF-20261120` | `ecg-image` | Referencias del texto actual, incluida la definición ECG-PT ya aplicada. No una nueva aceptación del epónimo ni medición/lectura automática validada. |
| `ECG-POCUS-REF-20261120` | `ecg-pocus-integration` | Integración contextual, discordancia, reevaluación y límites de estudios focales. No rendimiento combinado demostrado. |
| `POCUS-REF-20261120` | `pocus-image` | Marco completo de referencia, incluida expresamente la sustitución `POCUS-MODE-20261120 v1`, su aplicación y verificación. No nuevas capacidades de vídeo ni exactitud diagnóstica. |

Expedientes completos:

- [Gasometría, TC/RM y ojo](IMAGE_REFERENCE_REVIEW_GAS_CT_EYE_20261120.md).
- [Tórax, piel/herida y otras imágenes](IMAGE_REFERENCE_REVIEW_CXR_SKIN_OTHER_20261120.md).
- [ECG, POCUS e integración](IMAGE_REFERENCE_REVIEW_ECG_POCUS_20261120.md).

**Efecto propuesto de cada SÍ:** registrar literal, fecha, ficha, versión y
módulo; enlazar la revisión y sus fuentes; actualizar solo la evidencia de
referencia aceptada a GREEN. Un SÍ a las nueve fichas, con la corrección POCUS
aplicada y comprobada, permitiría **129 GREEN / 2 YELLOW**. Esa cifra es
condicional y no es el estado actual. Un NO mantiene el alcance correspondiente
pendiente sin afectar las aceptaciones anteriores.

La decisión se solicita porque [`AGENTS.md`](../../AGENTS.md) y la
[política de revisión final](final-human-review-policy.json) reservan al
Dr. Juan Copado Ceballos la aceptación clínica explícita del módulo y expediente.
Se puede responder a todos los IDs enumerados o seleccionar IDs concretos; no
se interpreta una instrucción genérica de continuar como una respuesta a una
versión todavía no presentada. No se vuelve a preguntar por PR35, ECG-PT,
el marco POCUS general, los 19 contratos agudos ni las escalas ya aceptadas.

## 3. Único cambio clínico de texto propuesto: POCUS-MODE v1

La palabra general «still» de la guía actual no distingue un único fotograma
B-mode de una captura de un trazado M-mode que sí contiene tiempo. La
aclaración propuesta conserva el alcance focal y evita atribuir la revisión
de una secuencia completa a partir de una sola línea temporal. El contraste
está en ACEP Sonoguide, Lung, 08/03/2021, apartado Lung Sliding, figura 8,
y en las fuentes físicas/documentales del dossier ECG/POCUS.

El [parche inactivo](proposals/POCUS_MODE_20261120_v1.patch) contiene únicamente
el tercer párrafo canónico y su ficha generada. El
[recibo](proposals/POCUS_MODE_20261120_v1.receipt.json) registra los hashes,
el generador, la comprobación y la invariancia de los otros módulos y estados.
Su aplicabilidad se comprobó también sobre la entrega clínica actual. No está
aplicado al producto ni contiene una respuesta del propietario.

La pregunta `POCUS-REF-20261120 v1` incluye este cambio exacto. No se formula
otra pregunta duplicada sobre MODE cuando se decide la ficha completa.

## 4. Validación que sigue realmente pendiente

| Módulo | Qué falta y qué no demuestra esta entrega |
|---|---|
| `clinical-image-interpretation` | Su condición expresa exige casos representativos, desidentificación/autorización, adjudicación independiente y revisión de métricas de seguridad para el uso previsto. El [mapa de imagen](IMAGE_VALIDATION_CLOSURE_20261120.md) conserva los datos reales PTB-XL previos y sus límites; no los extrapola al producto completo ni inventa acceso a otros datasets. E1 es infraestructura técnica, no un examen clínico ciego completado. |
| `clinical-note-diagnostic-support` | Falta validación clínica del apoyo diagnóstico y del uso propuesto. La corrección de procedencia conserva las limitaciones de `evidence_against`, datos discriminantes estáticos y cuatro relaciones `must_not_miss` sin regla resoluble, descritas en el dossier. No se da por solucionado el razonamiento clínico al reparar sus enlaces. |

Los protocolos existentes se reutilizan cuando se disponga de la tarea,
corpus autorizado y referencia independiente correspondientes. No se inventan
nuevos mínimos numéricos, observaciones de pacientes o métricas. Cualquier
despliegue requiere además sus condiciones efectivas de privacidad, producto,
operación y decisión clínica. El estado global permanece `CLINICALLY_PENDING`.

## 5. Identidad y revisión independiente

El árbol base técnico es `b49ea28981e84f234a90aa2095ac5bbebb4ef92d`, publicado
en PR49 como commit `318364bacf00cef22932f1849c79d12eb1e99562`. Los dossieres y
recibos que citan el commit local `e7c5722045852d654f756d5f3928d4c14daf2dbf`
identifican ese mismo árbol; no son revisiones de una versión clínica distinta.
Los textos de imagen examinados conservan hashes por sección y corresponden
al contenido posterior a PR47/PR48.

La revisión independiente del delta de nota comprobó igualdad de las reglas
al excluir solo `source_modules` y recalculó la comparación de las 60 salidas
guardadas. La revisión independiente de las fichas confirmó su delimitación:
ocho textos conservados, una aclaración POCUS candidata y ninguna promoción
de rendimiento diagnóstico. El resultado remoto de la entrega se consulta
en los checks del commit publicado; no se atribuye un PASS a trabajos omitidos.
