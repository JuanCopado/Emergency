# Revisión de referencia del gate clínico · 20/11/2026

**Expediente:** `GATE-REF-20261120`, versión 1. **Módulo:** `final-human-review-gate`. **Tipo de revisión:** norma interna de gobernanza y correspondencia de su implementación. **Base:** `e7c5722045852d654f756d5f3928d4c14daf2dbf`, árbol `b49ea28981e84f234a90aa2095ac5bbebb4ef92d`.

## Dictamen y alcance exacto

**Recomiendo cerrar la revisión de referencia de este módulo reutilizando la aceptación de PR35.** El texto canónico completo, la política 1.1, su generador y sus pruebas siguen siendo los aceptados en esa entrega. No se propone una regla clínica o de gobernanza distinta, por lo que no procede pedir a Juan que vuelva a aprobar la misma autoridad y el mismo circuito.

El cierre recomendado se limita a la vigencia y coherencia de esa norma. **No declara finalizada la revisión clínica de los demás módulos, no autoriza uso asistencial y no concede `GO_RELEASE`.** `CLINICALLY_PENDING` permanece. Este expediente no cambia ningún estado o fecha del registro.

## 1. Evidencia primaria y comprobación

La fuente de este módulo es una directriz del propietario del proyecto, no una guía de tratamiento ni un estudio de rendimiento. No necesita una cohorte diagnóstica para acreditar que su referencia normativa está vigente.

| Evidencia | Identidad/localizador | Comprobación del 20/11/2026 |
|---|---|---|
| Directriz del propietario | [`AGENTS.md`](../../AGENTS.md), sección «Decisión clínica del propietario · 20/11/2026»; [versión aceptada](https://github.com/JuanCopado/Emergency/blob/0d0fd3119bdd9a5cf75407849282d759353402c1/AGENTS.md) | Juan es el único validador clínico final; Farmacia es consultiva; se conservan aceptaciones anteriores en su alcance y controles aplicables. |
| Integración de esa decisión | [PR35](https://github.com/JuanCopado/Emergency/pull/35), commit de entrega `0d0fd3119bdd9a5cf75407849282d759353402c1`, merge `caf59bda7a2e5af5d822e18b210f50c300acb775` | El objeto Git y su relación de integración se han leído. La aceptación de esta directriz ya consta en la continuidad del proyecto. No se fabrica una respuesta nueva de Juan. |
| Texto canónico completo | [`documentation-governance.md`](../modules/documentation-governance.md), sección `final-human-review-gate` | Igualdad textual con la sección de PR35. Incluye propósito, diez pasos, resultados y límite de la revisión automática. |
| Política ejecutable | [`final-human-review-policy.json`](final-human-review-policy.json), `schema_version: 1.1` | Archivo idéntico al de PR35; mantiene decisión por módulo/expediente, privacidad cuando corresponda, correcciones y QA. |
| Generador y criterio de elegibilidad | [`final_human_review_gate.py`](../scripts/final_human_review_gate.py), `build_review_queue` y `can_promote` | Archivo idéntico al de PR35; lectura completa, sin edición. |
| Regresiones de la decisión | [`test_final_human_review_gate.py`](../tests/test_final_human_review_gate.py) | Archivo idéntico al de PR35; **2 pruebas PASS** en esta revisión. |
| Criterio general de estado | [`update-policy.md`](../references/update-policy.md), apartado E | GREEN identifica una referencia revisada y considerada vigente; no es por sí mismo aprobación de producción clínica. |

La comparación se realizó contra los objetos Git aceptados y los archivos actuales, no contra una descripción de terceros. No se reabrieron revisiones de fuentes clínicas de imagen o de nota para resolver una norma de gobernanza que ya estaba aceptada.

## 2. Qué exige la norma y qué hace el código

El texto exige un expediente versionado por módulo, decisión explícita de Juan para ese alcance, comprobaciones aplicables de producto, privacidad u operación, corrección de hallazgos críticos, QA posterior y trazabilidad de revisión. Solo permite promover individualmente el módulo revisado. La aprobación de la norma no significa que esas condiciones estén cumplidas para otros módulos.

`build_review_queue` examina dinámicamente los registros amarillos. No usa una cifra histórica fija ni exige una segunda firma farmacéutica. Marca la revisión final de cada módulo como `NOT_REVIEWED` y añade privacidad/información-gobernanza a las clases de módulo que identifica. Una aceptación puntual previa dentro de un módulo amarillo no se convierte por ello en aprobación de todo ese módulo.

`can_promote` exige que el dato recibido declare aprobación booleana explícita, el mismo módulo, la misma referencia de expediente, Juan como revisor, fecha, resultado PASS o PASS_WITH_NONCRITICAL_NOTE y QA posterior PASS. **No escribe en el registro.** La búsqueda de consumidores no encontró un flujo que lo utilice para promover automáticamente módulos; lo emplean sus pruebas.

Su alcance técnico es limitado: no autentica una firma, no obtiene pruebas de QA por sí mismo ni verifica los resultados desglosados de privacidad u operación. Esas revisiones siguen siendo condiciones de la norma y deben constar en el expediente aplicable. No se presenta el helper como un autorizador autónomo de despliegue. Esta limitación ya pertenece al código aceptado en PR35 y no impide verificar la vigencia de su referencia.

Por lectura del generador, cerrar la referencia del propio gate no desactiva la revisión de los demás amarillos: la condición se aplica por registro y no hay un interruptor global dependiente del estado de `final-human-review-gate`.

## 3. Por qué seguía amarillo y qué puede cerrarse

En el corte examinado, [`evidence-registry.json`](../references/evidence-registry.json) conserva:

```text
priority: high
status: yellow
last_checked: 2026-10-06
primary_source: Project physician-owner validation directive (PR35, 2026-11-20)
stored_version: PR35 owner-led governance; final-human-review-policy schema 1.1; clinical review date retained
```

La antigüedad de 45 días supera la ventana de 30. La conciliación del 20/11 había corregido los metadatos de autoridad, pero había conservado deliberadamente fecha y estado porque aquel trabajo no era una revisión completa del gate. Eso explica el aviso; no demuestra que falte una nueva firma de Farmacia o una nueva aceptación de PR35.

La entrada del 13/11 en [`pending-updates.json`](../updates/pending-updates.json), `expired_green_reclassified_yellow_source_renewal_pending`, conserva un corte histórico de caducidad. No es una instrucción para mantener indefinidamente el amarillo después de revisar la referencia vigente. El seguimiento focal del 20/11 tampoco declaró entonces un cierre integral; ese antecedente se preserva.

Esta revisión sí coteja íntegramente la norma del módulo, su política y su implementación con la decisión aceptada. No se ha identificado una norma posterior discrepante en las instrucciones vigentes examinadas ni un cambio de esos archivos respecto de PR35. La fuente interna está disponible y tiene identidad exacta.

## 4. Acción documental recomendada al coordinador

Cuando incorpore este expediente y compruebe la QA de la entrega, el coordinador puede registrar el cierre **de referencia de gobernanza**. La aplicación debe conservar explícitamente la procedencia de la aceptación anterior; no atribuir a Juan una firma de este documento nuevo.

| Campo/registro | Propuesta concreta, todavía no aplicada aquí |
|---|---|
| `status` de `final-human-review-gate` | `green`, exclusivamente para la referencia de gobernanza revisada. |
| `last_checked` | `2026-11-20`, fecha del cotejo completo de la referencia, no de una validación clínica general. |
| `primary_source` y `primary_source_url` | Conservar la directriz PR35 y su enlace inmutable. |
| `stored_version` | `PR35 owner-led governance; final-human-review-policy schema 1.1; governance reference reverified 2026-11-20`. |
| Nota y revisión focal | Referenciar este expediente, describir la aceptación PR35 reutilizada, las dos regresiones observadas y el límite de `can_promote`; declarar `CLINICALLY_PENDING` y ausencia de autorización asistencial. |
| Fuente derivada y cola | Regenerar con las herramientas existentes y anotar resolución del pendiente de referencia, preservando el historial de caducidad. No reescribir otras aceptaciones ni reclasificar módulos ajenos. |

Aplicar únicamente este cierre al corte de 119 GREEN / 12 YELLOW daría **120 GREEN / 11 YELLOW**. Es una consecuencia propuesta, no un estado observado en esta tarea. Los módulos padres de imagen y de apoyo diagnóstico de nota continúan pendientes en su alcance; ninguna aceptación del gate los valida.

**No se formula una nueva pregunta SÍ/NO sobre PR35.** Una modificación material futura de la norma o un alcance clínico nuevo sí exigiría su propia decisión, pero no se propone aquí.

## 5. Verificación y límites de la entrega

Comando ejecutado:

```bash
python -B -m unittest discover -s clinical/tests -p test_final_human_review_gate.py
```

Resultado observado: **2/2 PASS**. Las comprobaciones de igualdad contra `0d0fd3119bdd9a5cf75407849282d759353402c1` fueron verdaderas para la sección canónica completa, la política 1.1, el script y su archivo de pruebas.

No se ejecuta una nueva suite global por esta revisión documental ni se afirma haber completado QA de una futura publicación. Tampoco se cambia el estado de un módulo, se modifica el helper, se registra una aprobación médica nueva, se utiliza información de pacientes o se completa una evaluación de despliegue. El cierre recomendado permite retirar un pendiente de referencia ya comprobado sin convertirlo en un cierre clínico global.

## 6. Aplicación por el coordinador

La entrega coordinada aplica la propuesta de §4: referencia del gate GREEN,
`last_checked: 2026-11-20`, revisión focal enlazada y resolución del antecedente
de caducidad en la cola. Se sincronizan tabla, catálogo derivado y proyección.
El registro resultante es **120 GREEN / 11 YELLOW / 0 RED**. No se añade una
respuesta nueva del propietario ni se cambia la norma o el helper. El cierre
y su QA de conjunto se recogen en
[CLINICAL_CLOSURE_DECISIONS_20261120.md](CLINICAL_CLOSURE_DECISIONS_20261120.md).
