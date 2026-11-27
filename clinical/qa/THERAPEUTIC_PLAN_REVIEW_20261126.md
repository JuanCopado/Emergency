# THERAPY-20261126 — Pauta editable y revisión de versión

## Solicitud y alcance

El propietario solicita incorporar los corticoides en adultos y pediatría y que, al seleccionar un diagnóstico o pedir tratamiento, el sistema prepare una pauta sugerida editable: revisión pendiente en rojo, validación médica en verde y salida documental. Una modificación posterior requiere una nueva validación. Esta entrega implementa ese circuito sobre la nota existente y añade la consulta de corticoides.

Base de integración: `228cd21d75d14e1012beb7f5dfe82c2c920c4ccc`, rama `codex/v144-international-scope-20261116`. Rama de trabajo: `codex/corticosteroids-therapeutic-review-20261126`.

**El verde es la revisión del médico sobre una versión concreta del caso y la pauta.** No es una validación prospectiva, una autenticación de identidad profesional ni una promoción del estado clínico general. El registro de 131 módulos y las aceptaciones existentes se conservan.

## Uso

1. Registrar el episodio, edad en años **o** meses y los datos clínicos disponibles. Adulto y pediatría se resuelven por esa edad; una edad desconocida o ambigua no selecciona adulto silenciosamente.
2. Desde un candidato diagnóstico, pulsar **Preparar pauta**; alternativamente, abrir Plan y solicitar una patología. Se selecciona una indicación, sin acumular los tratamientos de diagnósticos alternativos.
3. Revisar la referencia completa y las cinco secciones: medidas iniciales/no farmacológicas, medicación, monitorización, reevaluación/escalada y destino/seguimiento.
4. Editar lo necesario. Completar los apartados ausentes o documentar que no se indica una intervención. Incorporar un texto de plan previo exige una elección explícita.
5. Confirmar revisión del caso y de la pauta individualizada, y revisión de seguridad farmacológica. El botón **Validar pauta**, rojo, solicita el recibo al backend. Una respuesta válida lo cambia a verde y satisface la revisión médica del caso actual para la salida. Los controles de privacidad y de informes pendientes permanecen.
6. Exportar Word, PDF o JSON. Editar el caso o la pauta invalida la revisión. Un cambio de caso, idioma, indicación, peso o contexto exige regenerar la propuesta; editar únicamente las secciones permite volver a validar la versión editada.

## Qué genera y qué requiere individualización

El lector resuelve el ID en el manifiesto canónico y conserva **preámbulo + sección íntegra**. Copia párrafos completos, sin modificar cifras, a las secciones sugeridas. No crea dosis, no realiza una segunda aritmética farmacológica ni combina las cinco primeras hipótesis del motor diagnóstico.

El catálogo conserva los 131 módulos canónicos y añade un acceso focal `ent-emergencies:bell-palsy` a la subsección de Bell, sin crear un nuevo módulo clínico. Una política explícita mantiene 59 módulos de múltiples indicaciones, catálogos, imagen o gobernanza como **consulta de referencia**: entregan la fuente íntegra y un borrador para completar. Así no se copian, por ejemplo, todas las pautas de un catálogo pediátrico a un único niño. Los módulos concretos admitidos, incluidos asma adulta/pediátrica y crisis suprarrenal, conservan la proyección de su contenido.

Incluso cuando las cinco secciones tienen contenido, la asignación de párrafos no prueba que exista una prescripción completa para ese caso. El médico confirma indicación, gravedad, fármaco, dosis, vía, frecuencia, duración, máximos, preparación cuando corresponda, contraindicaciones, monitorización, criterios de reevaluación y destino. Los apartados sin respaldo se muestran vacíos; no se convierten en recomendaciones inventadas. Las calculadoras y contratos farmacológicos actuales siguen siendo las rutas de cálculo.

Las fuentes se identifican como `original`: los módulos incluyen inglés, español y contenido mixto. Las etiquetas del circuito están disponibles en ES/PT/EN/ZH. No se presenta el texto canónico como una traducción clínica revisada.

## Seguridad de versión y salida

- La generación recibe una firma HMAC de dominio propio. Vincula indicación, población, contexto, referencia, huellas, pendientes iniciales y digest de la propuesta original. Sólo las cinco secciones pueden editarse.
- El contexto cubre episodio, historia, exploración, pruebas, diagnósticos, idioma y privacidad. Excluye únicamente el recibo, la fecha efímera de revisión, el permiso de exportación y las tres salidas antiguas sustituidas por el plan: tratamiento, destino y reevaluación.
- La validación emite un recibo con digest del plan íntegro y del contexto, fecha del servidor, modo `as_suggested`/`edited` y confirmaciones explícitas. La exportación vuelve a cargar las fuentes y comprueba firma, contenido y contexto.
- Un booleano `reviewed=true`, un recibo inventado, un recibo de otro caso o una versión editada no habilitan una salida terapéutica. Omitir el objeto de pauta tampoco habilita las antiguas sugerencias como tratamiento validado.
- JSON, PDF y DOCX usan la pauta revisada. Las antiguas listas de tratamiento, destino y reevaluación no se exportan como una segunda pauta. JSON conserva la procedencia y permite comprobar la misma versión.
- Las respuestas tardías de generación, validación y descarga se descartan si cambió la revisión del episodio o se inició otro episodio.
- No se guardan casos clínicos en almacenamiento del navegador ni se envían a un modelo externo mediante este circuito. Los borradores permanecen en la sesión actual de la aplicación.

El recibo HMAC garantiza integridad y registra la acción recibida por esta API; **no verifica por sí mismo la identidad profesional**. La clave predeterminada es efímera por proceso. Tras reiniciar el backend, un borrador anterior requiere regeneración y revisión, salvo que el operador configure una clave privada estable mediante `CLINICAL_NOTE_THERAPY_HMAC_KEY` en su entorno autorizado. Ninguna clave se escribe en el repositorio ni en las capturas.

## Relación con farmacología

La pauta conserva `medication_safety.status=REVIEW_REQUIRED` y `actionable=false`. La confirmación del médico registra la revisión humana, sin transformar el resultado genérico del preflight en una comprobación automatizada de dosis o interacciones.

Se exige revisar alergias explícitamente; una lista inicialmente vacía no equivale a ausencia confirmada de alergia. Las notaciones reconocidas por kg requieren peso verificado en el contexto. Las expresiones por m² requieren individualización de la dosis absoluta con el cálculo revisado: este circuito no incorpora una calculadora de superficie corporal.

Estos controles de texto son salvaguardas acotadas. No verifican semánticamente toda prescripción libre ni reemplazan las calculadoras o la revisión clínica. Tampoco deben retrasar la asistencia urgente; regulan la emisión de la pauta documentada como revisada.

## Privacidad y referencia pública

Los patrones generales de detección permanecen. Algunos textos canónicos contienen expresiones que esos patrones confunden con identificadores, como `patient-specific` o el verbo `address`.

Sólo se exceptúa una cadena de referencia pública cuando la firma de generación es válida y la cadena coincide exactamente con la fuente canónica actual. Una edición de la sección elimina esa excepción. Las ubicaciones exceptuadas se comparan como tuplas estructurales de claves e índices, nunca como texto JSONPath: una clave literal con puntos o corchetes no puede simular una ubicación de fuente. Etiquetas introducidas, historia, exploración, informes y todo texto modificado siguen pasando por el detector. La interfaz conserva el original recibido para evitar el mismo falso positivo local; el backend vuelve a verificarlo antes de validar o exportar.

## Contrato de API

| Ruta POST | Función |
|---|---|
| `/api/clinical-note/therapy/catalog` | Módulos, población y alcance de referencia |
| `/api/clinical-note/therapy/suggest` | Generación de una propuesta para indicación/población/caso |
| `/api/clinical-note/therapy/validate` | Revisión explícita de esa versión y recibo firmado |
| `/api/clinical-note/export` | Salida comprobada por el gate común |

Los contratos `therapeutic_plan` y `therapeutic_review` están definidos en `qa/clinical-note-schema.json` y en los tipos de la interfaz. No se confía sólo en palabras clave JSON Schema que el validador local no implementa: las firmas, vigencia y condiciones se comprueban en Python.

## Corticoides y trazabilidad

La consulta `/corticosteroids` tiene su [expediente focal](CORTICOSTEROIDS_REVIEW_20261126.md), [catálogo](../pharmacology/corticosteroids.json) y [fuentes](../references/corticosteroids.md). Incluye ocho corticoides, tablas Endotext/ESE diferenciadas, duración biológica, actividad mineralocorticoide y fichas adultas/pediátricas de hidrocortisona. Su generador `--check` se ejecuta en el build.

Se conserva la aceptación de los 19 contratos agudos. No se alteran las 45 fórmulas existentes ni se declara una revisión clínica integral a partir de pruebas de software.

## Verificación de esta entrega

Resultados observados durante la integración (casos sintéticos):

- Flujo y fuentes: **36/36 pruebas Python PASS** en la comprobación final (23 de flujo y 13 de fuentes), incluyendo todos los módulos/poblaciones del catálogo, rechazo de firma/contexto obsoletos, copia de recibos, variantes de dosis, campos de extensión con puntos/corchetes, privacidad, Bell adulto y límite pediátrico, asma adolescente desde un candidato diagnóstico y JSON/PDF/DOCX.
- Regresiones existentes `test_clinical_note_*.py`: **20/20 PASS** (HTTP/privacidad, idioma y procedencia).
- Regresiones focales de `test_skill.py` e idioma adaptadas por el revisor: **59/59 PASS**. Los fixtures terapéuticos obtienen un recibo mediante la API real; las pruebas aisladas del detector conservan su objetivo sin depender del recibo.
- Interfaz de nota y corticoides: **94/94 PASS** en ocho archivos antes de la ampliación focal de Bell; su actualización queda en el expediente CORT.
- TypeScript y build de producción: **PASS**. Las advertencias preexistentes de tamaño de bundles no son una validación clínica.
- El nuevo harness `app/scripts/check-therapeutic-review.mjs` supera comprobación de sintaxis y arranca Python/proxy. **Navegación real no completada**: el lanzador `/usr/bin/chromium` carece de binario y la descarga oficial de Playwright devolvió HTTP 403. No hay capturas ni PASS visual atribuidos a este intento. Se puede ejecutar `npm run therapy:browser-check` cuando exista un Chromium válido (`CHROMIUM_PATH`).

No hay publicación en producción ni prueba en el PC JUAN-C implícita en esta verificación local Linux.

## Aclaración del propietario: pautas cortas

Asma adulta y pediátrica ya disponían de sus pautas en los módulos correspondientes. La consulta nueva mantiene esos enlaces. Se incorpora Bell de forma explícita dentro de ENT y como acceso focal de la pauta: sólo esa subsección se proyecta, preservando el preámbulo y la huella del bundle; no se incorporan los restantes tratamientos ENT. La pauta adulta se ofrece desde los 18 años en este flujo. Para menores de 18, incluidos 16–17, la referencia está disponible con secciones sin rellenar y decisión clínica individual, sin extrapolación automática. Las diferencias entre el umbral de AAO-HNSF y la evidencia pediátrica se documentan en el expediente de corticoides.

La comprobación final añadió la banda explícita de corticoides en asma de 12–17 años, respaldada por GINA 2026, Box 9-2, dentro de `pediatric-acute-asthma`. Las bandas ≤5, 6–11 y 12–17 siguen siendo referencias alternativas para selección e individualización médica, sin presentar la proyección como una elección automática de dosis.

También se corrigió la referencia del candidato diagnóstico de asma según la edad conocida: menor de 18 hacia el módulo pediátrico y desde 18 hacia el adulto, conservando puntuación y evidencia. La prueba recorre el motor diagnóstico real y la generación en 12, 17, 18 años y 204 meses. Si la edad es desconocida no se asigna una población por defecto y la generación continúa requiriéndola. El umbral y la conducta de Bell permanecen independientes; se comprobaron 5, 12, 17, 18 y 45 años. Los candidatos históricos necesitan una nueva ejecución del apoyo diagnóstico para recibir la referencia corregida.
