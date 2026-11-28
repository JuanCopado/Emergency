# GUÍA MAESTRA DE FLUJO CLÍNICO — EMERGENCY

**ID:** GMFC-20261128 · **Versión:** 0.1 — propuesta del propietario y síntesis inicial del coordinador, EN ESTUDIO.
**Fecha:** 28/11/2026 · **Referencia clínica:** uso individual del médico de urgencias, web/PWA/local, núcleo internacional.
**Base observada:** rama internacional, commit `50ef5ee684e85dd769255445e78f2f12c40a266c` (PR140 integrada); PR141 `6a1dcbd971c864f06d5ee66d0989d0709f51379c` sigue siendo propuesta de corrección del instalador, no prerrequisito del estudio. Revalidar base y matriz central al iniciar cada revisión.
**Estado:** `CLINICALLY_PENDING` · `NOT_FROZEN_NOT_VALIDATED` · `NO_GO_CLINICAL_RELEASE`.

Esta guía recoge el planteamiento del médico propietario del 28/11: consulta ultrarrápida por texto/voz, nota profesional desde texto y documentos, plan para diagnóstico establecido, alta ambulatoria y alertas de seguridad/actualización. Añade continuidad de guardia y criterios de diseño como propuestas de estudio, no decisiones clínicas ni funcionalidades autorizadas. No sustituye [IMPLEMENTACIÓN](../IMPLEMENTACION.md), [ORQUESTACIÓN](ORQUESTACION.json), la matriz clínica central ni los contratos canónicos. Las líneas de estudio de [ORQUESTACION_GUIA_MAESTRA.json](ORQUESTACION_GUIA_MAESTRA.json) son asignaciones documentales dentro de la coordinación existente, no una nueva cola de desarrollo.

## 1. Objetivo y principios

Una pantalla de trabajo que ahorre búsqueda, transcripción y burocracia desde el inicio hasta el final de guardia, en patologías leves y críticas, adulto/pediatría y poblaciones especiales. Ofrecer acceso rápido sin episodio para una consulta aislada y trabajo contextual cuando el médico decide abrir un episodio. Introducir cada dato una vez, con origen visible, sin inferir ni arrastrar datos de otro paciente. No exigir integración hospitalaria, cuenta remota ni selección de hospital para el núcleo internacional. El profesional conserva la decisión final; la validación de un documento no es validación clínica del software.

Priorizar rapidez, legibilidad, seguridad, privacidad, accesibilidad y continuidad; una portada moderna sirve a la entrada al trabajo, no añade pasos. Mantener operaciones urgentes accesibles con teclado/táctil, foco visible, colores más texto/iconos, sin depender del color ni de animaciones. Sin imágenes identificables de pacientes ni fuentes restringidas enviadas a servicios externos. Mantener opción manual si voz, OCR o backend no están disponibles.

## 2. Las cinco funciones conectadas

| Función | Entrada | Respuesta esperada | Límite |
|---|---|---|---|
| FAST | Petición breve por texto o dictado; sin episodio obligatorio | Tarjeta inmediata, datos detectados, datos imprescindibles faltantes, cálculo o referencia aplicable | Resolver únicamente intención y entidad confirmadas; no inventar indicación, producto, unidades ni dosis |
| NOTE | Texto libre, antecedentes, medicación, alergias, exploración, evolución, informes y adjuntos | Original conservado, propuesta estructurada, versión final editable y exportable | Separar hechos aportados, extracción, ausencia e inferencias; interpretación YELLOW deshabilitada |
| TREATMENT | Diagnóstico explícitamente establecido por el médico y contexto relevante | Plan por prioridades: estabilización, tratamiento, monitorización/reevaluación, destino | Plantilla documental no equivale a prescripción; bifurcaciones por contexto; solo contratos autorizados para cifras ejecutables |
| DISCHARGE | Diagnóstico establecido, edad/peso cuando corresponda, contexto y decisión de destino | Propuesta editable de tratamiento domiciliario, duración, educación y signos de alarma | No asumir indicación antibiótica ni alta; producto/concentración si hace falta convertir a mL |
| TESTS | Analítica, gasometría, PDF, informe TAC/ECG, imagen | Datos extraídos vinculados al original, unidades/fecha, confianza, corrección y confirmación para cálculos | OCR/extracción no equivalen a interpretación diagnóstica; capacidades no empaquetadas o restringidas se muestran indisponibles |

Las guías, fármacos, calculadoras, procedimientos y POCUS siguen siendo accesibles desde cualquier flujo. No duplicar el catálogo ni los motores. Separar consulta rápida sin caso de episodio activo explícito; una consulta aislada no se añade automáticamente a una nota.

### 2.1 FAST: respuesta bajo presión

Ejemplos sintéticos: "80 años, 80 kg, perfusión de noradrenalina"; "niño 35 kg, hidrocortisona IV"; "adrenalina en anafilaxia"; "calcular anion gap"; "cardioversión". No contienen una pauta preautorizada. Reconocer ambigüedad de fármaco/indicación/vía y mostrar los datos ya aportados como campos editables; preguntar solamente por los imprescindibles conforme al contrato exacto. En perfusiones: separar dosis objetivo y velocidad, mostrar unidades y preparación confirmada, titulación/monitorización solo si respaldadas. Si faltan datos críticos, mostrar referencia segura sin cifra calculada y el motivo de bloqueo. Nunca inventar concentraciones o equivalencias ni sustituir el cálculo por generación de texto.

Modo crítico: primero resultado o bloqueo, después confirmaciones, advertencias aplicables y acceso a fuente; detalles secundarios desplegables, sin ocultar alertas esenciales. La consulta no debe retrasar una intervención urgente. Medir tiempo a primer resultado útil y clics con casos sintéticos, sin fijar SLA ficticios. Confirmación explícita de números/unidades transcritos por voz (incluidos decimal, negación, mg/µg, kg/edad). Sin capturar audio/identificadores reales en el laboratorio.

### 2.2 NOTE: documentación y reutilización

Reutilizar la pestaña Texto libre y correcciones PR140: original / propuesta / final, evitar duplicados, no sobrescribir silenciosamente y revocar revisión cuando cambia contenido. Preparar formatos de nota inicial, evolución, alta, ingreso/UCI, interconsulta, traslado, procedimiento y pase de guardia. Secciones: motivo; antecedentes; medicación y alergias; historia; exploración; pruebas; evolución; impresión diagnóstica aportada; plan y destino. Diferenciar desconocido/no documentado de negativo confirmado. No completar exploración normal ni datos ausentes.

Previsualizar texto original y cambios; deshacer/restaurar; aceptar secciones por separado; conservar cifras, negaciones, fecha, idioma y unidad. Copiar a historia clínica institucional en texto plano compatible; PDF/DOCX/impresión de la versión exacta revisada conforme a exportadores existentes. Si se modifica dato que afecta al plan, invalidar revisión/cálculo dependiente y solicitar revalidación. No afirmar firma legal del informe por un clic. La nota final es editable; una copia en borrador debe estar inequívocamente identificada y no sustituir exportación canónica revisada.

Adjuntos: conservar original y atribuir página/localizador cuando exista; extracción de analítica/gasometría/informe con unidades y timestamp; mostrar conflictos/duplicados y permitir confirmación o corrección antes de reutilizar. No afirmar que OCR, T05/T06, voz, DICOM o interpretación de ECG funcionan en todas las distribuciones; verificar capacidad exacta, mostrar indisponibilidad y alternativa manual. Sin análisis diagnóstico automático de notas o imágenes YELLOW.

### 2.3 TREATMENT y DISCHARGE

Diagnósticos sintéticos establecidos: IAM con elevación del ST, edema agudo de pulmón, sepsis, asma, cetoacidosis, fibrilación auricular. Estudiar bifurcaciones de gravedad, estabilidad, indicación, edad/peso, alergias, embarazo, función renal/hepática, tiempos y recursos según el caso; no exigir todos los campos siempre. Distinguir referencia general, plan no individualizado, propuesta para revisar y cálculo específico autorizado. Mostrar acciones por secuencia temporal, medicación en líneas claras (fármaco, dosis, unidad, vía, intervalo, preparación, duración/límite según proceda), contraindicaciones, monitorización y reevaluación. Los campos no disponibles no se completan por intuición. Revisar interacción con medicación habitual y tratamientos ya introducidos; si no hay cobertura de interacción, decir no evaluada, no "sin interacciones".

Alta sintética: niño de 7 kg con fiebre y otitis media aguda establecida. Estudiar edad, clínica, gravedad, alergias, indicación de tratamiento/observación, presentación y concentración para volúmenes, pautas y duración si existen contratos y fuentes suficientes, instrucciones comprensibles, signos de alarma y reevaluación. No inferir antibiótico ni criterios de alta. Separar informe profesional de instrucciones al paciente; permitir editar y copiar/imprimir el documento revisado. No enviar recetas, órdenes o acciones a terceros ni activar prescripción autónoma.

## 3. Continuidad de la guardia y alertas

- Episodio activo inequívoco en todas las pantallas; cambiar episodio nunca mezcla medicación, peso, adjuntos o alertas. Proteger borradores y actualización PWA/rollback dentro del comportamiento ya probado, sin prometer recuperación tras cierre ni persistencia de datos clínicos no autorizada.
- Reutilización de valores confirmados con procedencia, hora y unidad; si cambian, revalidación de dependientes. Comparar tendencias y reevaluaciones sin convertir ausencia de datos en estabilidad. Pase de guardia: pendientes explícitos y destino decidido por médico.
- Conciliación de medicación, duplicidades, interacciones, ajustes, alergias: distinguir comprobado, no evaluado y no aplicable; solo alertas con reglas/evidencia admitida. Distinguir bloqueos técnicos no eludibles de precauciones clínicas; revisión con motivo cuando el contrato lo permita. Nada de desactivar globalmente avisos críticos.
- Alerta crítica: bloqueo de cálculo/propuesta ejecutable insegura (unidad incompatible, entrada inválida, contraindicación bloqueante según contrato). Precaución: contextual, acción sugerida dentro del alcance. Actualización científica: fuente, versión incorporada, fecha de publicación y última comprobación, cambio nuevo pendiente de revisión; no actualizar automáticamente recomendaciones o `last_checked` por un aviso. Evitar fatiga mediante deduplicación por episodio, severidad y pertinencia, sin ocultar alertas obligatorias.
- Local-first. Datos sintéticos exclusivamente en desarrollo; privacidad por finalidad antes de habilitar datos reales, persistencia, voz externa o servicios remotos. No usar MCP de desarrollo como motor clínico ni enviar notas a un agente externo. Sin sincronización cloud por defecto.

## 4. Arquitectura y fases de estudio, no implementación

Entrada natural -> extracción/intención y contexto confirmado -> enrutamiento hacia capacidades canónicas -> motor determinista/plantilla/documentación/alerta -> resultado trazable -> revisión/edición -> copia/exportación según estado. El LLM, si se selecciona después, no genera dosis ni sustituye reglas; la interpretación clínica permanece restringida. En caso de capacidad ausente o fuente no apta: abstención explícita y acceso manual cuando sea seguro. Las salidas incluyen fuente/versión, contrato, valores confirmados y alcance cuando proceda.

Orden propuesto de análisis: (1) FAST y NOTE como centro operativo, (2) planes de diagnóstico establecido y alta, (3) importación y alertas transversales, (4) contexto de episodio y continuidad, (5) portada e identidad visual y accesibilidad/rendimiento transversales. Los agentes deben comprobar dependencias y proponer cambios de orden justificados; no crear fases paralelas de infraestructura ni nuevas tareas clínicas. Aprovechar las rutas, componentes, motores, exportadores, i18n, guardas y QA existentes antes de añadir dependencias. Figma/Playwright/DevTools/axe/Lighthouse solo si útiles y autorizados, sin compra ni datos reales. No iniciar código o instalación como parte de este estudio.

## 5. Encargo multiagente

### Work — coordinador
Leer AGENTS.md, IMPLEMENTACION.md, ORQUESTACION.json, matriz vigente, PR140/141, QA y alcance de uso individual. Fijar versión y hash de esta guía, receptor y candidato; recuperar entregas anteriores. Usar MCP Emergency en metadata con snapshots vigentes cuando aporte valor. Enviar a Claude, Gemini y Codex el mismo briefing de referencia; cada agente revisa su dimensión en paralelo, sin contaminarse con las otras conclusiones iniciales. Registrar transmisión, acuse y respuesta real. No afirmar despacho si no existe evidencia. Antigravity recibe la síntesis después de los tres estudios; si no está disponible, documentar límite y utilizar revisión independiente acotada por otro colaborador con atribución real. No suplir una respuesta inventada.

### Claude Code — experiencia de guardia y diseño
Estudiar tareas de alta y baja gravedad, entrada natural, interacción bajo interrupciones, atajos, jerarquía de tarjetas, original/propuesta/final, edición y exportación, modo claro/oscuro y responsive, alertas no intrusivas, portada. Revisar PR139/140 y el diseño ClinicalMinimal previo; no duplicarlos. Entregar recorrido desde inicio de guardia, mapa de pantallas, estados vacío/error/carga/no disponible, propuesta de layout y microcopy, y criterios medibles de UX. Comparar diseño existente versus cambios propuestos; prototipos solo conceptuales y sintéticos, no implementación ni Figma de datos reales.

### Gemini — seguridad clínica y evidencia
Estudiar ejemplos sintéticos de consulta inmediata, adulto crítico, pediatría ambulatoria, paciente complejo, diagnóstico establecido vs sospecha y documentación. Identificar datos imprescindibles por intención, bifurcaciones, contraindicaciones/ajustes, alertas, cuándo abstenerse y límites del motor de interacción. Cotejar referencias primarias y localizadores si aporta cambios clínicos; no repetir 15/18 lecturas previas ni inferir insulina/labetalol originales. Mantener cuarentenas y decisiones aceptadas. Entregar matriz por escenario: condición, dato mínimo, salida permitida, dato no conocido, riesgo, guarda, fuente o brecha, y decisión médica residual solo si madura. No introducir dosis, cambios de algoritmo, prescripción ni nuevos votos.

### Codex — viabilidad y aprovechamiento del código
Inventariar en base vigente componentes/rutas de nota, texto libre, importación, QA, motores deterministas, selección de país, catálogos, exportadores, privacidad/episodios y disponibilidad web/local/PWA. Cruzar cada requisito con existencia acreditada, parcial, ausente, restringido o no verificado; ruta y SHA, guardas/dependencias y pruebas ya existentes. Proponer integración incremental y criterios negativos, sin escribir código. Identificar cómo medir acciones, latencia extremo a extremo y exactitud sin campañas innecesarias. Preservar contratos y fórmulas; no extender RAG, MCP ni backend remoto sin beneficio demostrado. Confirmar qué está realmente empaquetado en cada distribución.

### Antigravity — revisión independiente de la síntesis
Revisar versión exacta de la síntesis tras las tres entregas. Detectar contradicciones, omisiones, riesgos de confusión entre pacientes, pérdida de texto, unidades, atribución, alertas, capacidades no validadas, exportación y privacidad. Distinguir defecto probado, riesgo condicionado y mejora opcional. Dar dictamen sobre guía de diseño (no MERGE_READY clínico ni autorización). No repetir auditorías técnicas del mismo árbol. Entregar hallazgos focales con impacto y corrección propuesta.

## 6. Aceptación del estudio y métricas propuestas

Todos los agentes entregan una síntesis breve y una matriz de hallazgos con ID local, requisito, situación actual, evidencia (SHA/ruta/localizador), cambio propuesto, prioridad, riesgo evitado, dependencia, coste/beneficio cualitativo o medido, recomendación y límite. Un único coordinador decide ADOPTAR / REFORMULAR / APLAZAR / DESCARTAR con motivo; no acumular propuestas. Distinguir requisitos directos del propietario de mejoras sugeridas por agentes. Reutilizar criterios C1–C6 y los doce IDs IMP existentes: IMP-00 alcance/inventario; IMP-02 aplicabilidad clínica/regulatoria; IMP-09 QA; IMP-10 consolidación; IMP-11 autorización solo cuando corresponda. Las tareas clínicas conservan sus IDs en la matriz central.

Casos sintéticos de aceptación para la futura implementación:
1. FAST: petición suficiente y petición incompleta/ambigua (adulto/pediatría); no confundir mg/µg, edad/peso, vía, concentración o separador decimal; sin cifra si falta requisito crítico.
2. NOTE: pegado largo, texto sin encabezados, negación, caracteres Unicode, valores y unidades, reaplicar/editar sin pérdida ni duplicación; exportar versión revisada; conservar original.
3. TESTS: documento con valor dudoso, unidades incompatibles o repetidas; corrección y trazabilidad; OCR/voz indisponibles con alternativa manual.
4. TREATMENT: diagnóstico establecido con rama hemodinámica/contraindicación variable; plan parcial marcado como tal, cambio de dato invalida revisión; no habilitar pauta restringida.
5. DISCHARGE: pediatría de 7 kg con edad/presentación faltante, alergia y ausencia de indicación antibiótica; no pauta inventada, separar instrucciones del informe.
6. Continuidad: cambiar A/B/A, interrupción, actualización, offline, conflicto de datos y sesión; cero mezcla en casos ensayados, no inferir persistencia clínica universal.
7. Alertas: crítica vs precaución vs nueva versión, aviso no evaluado, duplicado y actualización de guía; no ocultar advertencias obligatorias ni cambiar fuentes sin revisión.
8. UX: teclado, táctil, escritorio/tablet/móvil, idiomas vigentes, modo claro/oscuro, sin dependencia exclusiva del color. Medir pasos y tiempo hasta respuesta útil, edición necesaria, errores y carga percibida; comparativa solo cuando exista medición comparable y costes netos (incluida preparación/llamadas/salida). No fijar porcentajes, tiempos o cobertura universal sin datos.

El resultado final debe ser una guía v1.0 con matriz de trazabilidad, mapa de capacidades existentes, orden de incrementos, escenarios y límites. Si una revisión no llega, conservar estado parcial y explicar qué falta; no declarar revisión multiagente completa. Presentar al propietario solo decisiones materiales nuevas con evidencia suficiente. No iniciar implementación de la guía hasta que el coordinador consolide el estudio y el propietario acepte el alcance; la reparación técnica ya autorizada se mantiene separada.

## 7. Referencias de proyecto y límites

- [AGENTS.md](../../AGENTS.md), [IMPLEMENTACIÓN](../IMPLEMENTACION.md), [ORQUESTACIÓN](ORQUESTACION.json), [alcance internacional](../INTERNATIONAL_SCOPE.md), [puertas clínicas](../../clinical/qa/RELEASE_GATES.md).
- [PR139](https://github.com/JuanCopado/Emergency/pull/139), [PR140](https://github.com/JuanCopado/Emergency/pull/140), [PR141](https://github.com/JuanCopado/Emergency/pull/141), [MCP](../../tools/emergency-mcp/README.md).
- El propietario solicita estudiar esta guía antes de continuar; la versión 0.1 es documentación preparatoria. No hay acuses de nuevos agentes, estudio clínico prospectivo ni cambio de código. Conservar 19 contratos, 45 fórmulas, MED-DEC-R46-01/02, las 23 decisiones dermatológicas, dos módulos YELLOW y `CLINICALLY_PENDING`. Sin fusionar ramas protegidas, sin despliegue, compra, datos reales, nuevas dosis ni cambios de `last_checked`.
