# GUÍA MAESTRA DE FLUJO CLÍNICO — EMERGENCY

**GMFC-20261128 · versión1.0 PROPUESTA PARA ACEPTACIÓN. No aceptada ni implementada.**

Fuente de estudio PR142 `ecacffee5cdd67992e01e3913e8a0682b3b96ca3`; receptor técnico integrado `d3f8a792ca1cd43d022509caa5b43f38856af3ae`. El cambio del instalador entre ambos cortes no modifica las capacidades de interfaz inventariadas. Documento para el médico individual de urgencias, núcleo internacional, web/PWA/local con disponibilidad distinta por función.

**CLINICALLY_PENDING · NOT_FROZEN_NOT_VALIDATED · NO_GO_CLINICAL_RELEASE.** Esta propuesta no permite nueva UI, cambios de fórmulas/dosis, promoción clínica, fusión protegida o despliegue. Requiere aceptación expresa del alcance por el propietario antes de implementación.

## 1. Revisiones realmente recibidas

Claude Code entregó UX independiente completa; Codex entregó inventario técnico independiente completo. Gemini recibió el briefing sin otras respuestas, declaró un fallo de contexto y después entregó S01–S03 completos y S04 truncado. La recuperación compacta no quedó disponible en la conversación. No existe una revisión Gemini10/10 ni se atribuye una respuesta reconstruida al proveedor.

Un revisor Codex independiente, sin leer las otras respuestas, cubrió exclusivamente S04 final y S05–S10 mediante documentos autorizados. Esa alternativa se atribuye a Codex, no a Gemini ni a un médico adjudicador. Antigravity revisó la síntesis parcial0.2; la disposición y revisión del incremento documental final se conservan aparte. Ninguna coincidencia entre agentes constituye validación clínica o aceptación del propietario.

El inventario exacto y sus localizadores permanecen en `gmfc/INVENTARIO_TECNICO.json` y `gmfc/REVISION_TECNICA.md`. Los originales, recibos, hashes y disposiciones se entregan al coordinador único para custodia en Drive. La orquestación de este estudio no crea otra cola: conserva12IDs IMP y26registros clínicos en CENTRAL.

## 2. Objetivo y modelo de trabajo

Acceso directo a una consulta urgente o a la nota durante toda guardia. Una consulta aislada no exige abrir un episodio ni se añade automáticamente a una nota. Cuando el médico trabaja sobre un episodio, su identidad y versión deben ser inequívocas; reutilizar datos requiere origen y destino explícitos. No inferir país, hospital, edad, producto o datos normales a partir del idioma o del contexto del propietario.

Arquitectura local principal, híbrida opcional. No imponer servidores remotos, PostgreSQL, cuentas OIDC, LLM o interoperabilidad hospitalaria al producto individual. No guardar datos identificables de pacientes remotamente por defecto. Preferencias de interfaz y contenido clínico tienen contratos de almacenamiento distintos; el localStorage actual de preferencias no autoriza historias clínicas persistentes.

Preservar los19contratos ya aceptados y45fórmulas deterministas. Hay13formularios aprobados expuestos;45fórmulas no equivale a45formularios ni135calculadoras FAST. No duplicar motor o catálogo. Preparaciones ORIGINALES no identificadas de insulina/labetalol siguen restringidas; no bloquear regímenes genéricos previamente aceptados ni pedir otra votación de las decisiones conservadas.

## 3. Inventario y disponibilidad reales

| Función | Existencia acreditada por lectura estática y evidencia previa | Propuesta pendiente o restricción |
|---|---|---|
| FAST | Rutas, catálogo, buscador, formularios y motores reutilizables | Enrutador universal texto/intención pendiente. Voz no acreditada. No cifras generadas fuera de contrato. |
| NOTE | Original/propuesta/final, copia libre editable, campos canónicos y PDF/DOCX/JSON | Final libre y exportación canónica no son automáticamente el mismo documento. Catálogo completo de plantillas y versión final exportable por consolidar. |
| TREATMENT | Plan parcial de cinco secciones, fuentes SHA y revisión | No prescriptor universal ni motor exhaustivo de interacciones. Propuesta contextual sólo dentro de capacidades/contratos acreditados. |
| DISCHARGE | Módulos y exportadores pediátricos reutilizables | No generador universal de alta. Sin edad/indicación/producto/destino inferidos. Separar informe profesional e instrucciones. |
| TESTS | PDF textual/TXT con candidatos y confirmación; apoyos deterministas acotados | Recepción de archivo no es admisión al banco ni diagnóstico. Voz, OCR, DICOM y otros servicios se clasifican por capacidad, no por extensión aceptada. |
| Mi guardia | Un borrador en memoria y guardas contra pérdida durante ciertas actualizaciones | Gestor multiepisodio PENDIENTE. Persistencia tras cierre no acreditada. A/B/A de versiones PWA no prueba pacientes A/B/A. |
| Offline | UI cacheada y APIs locales si el runtime está activo | PaqueteE no incorpora upload/interpret/T05/T06. Sin WAN no significa sin backend. Indisponibilidad visible y alternativa manual documentada. |
| Identidad/UX | Layout, temas, idioma y ClinicalMinimal opt-in | Portada/logo/iconos1627033 excluidos, sin adopción automática. WCAG2.2AA y rendimiento global no medidos en este estudio. |

Matriz técnica:37requisitos locales,9EXISTENTE/13PARCIAL/8PENDIENTE/6RESTRINGIDO/1NO_VERIFICADO. Estas categorías describen existencia/evidencia del requisito, no estado médico ni nuevos trabajos IMP.

Los dos módulos YELLOW no se promueven a diagnóstico validado. Se preserva el apoyo determinista limitado y sus guardas cuando ya existe: «YELLOW» no significa que toda función de análisis esté ausente o que haya que borrar código aceptado. Diferenciar extracción, confirmación, referencia, apoyo limitado e inferencia diagnóstica no validada.

## 4. Contratos de las cinco funciones

**FAST.** Intención/entidad confirmadas → contrato canónico disponible → datos verdaderamente imprescindibles → resultado determinista o referencia/bloqueo explicado. Datos ya aportados se muestran editables; preguntar sólo los faltantes pertinentes. Un cálculo puede requerir valor de dosis objetivo, no sólo su unidad, y preparación/concentración si convierte a volumen. Una consulta documental no exige todos los datos de una administración. No elegir indicación, vía o producto por frecuencia. Voz, si se acepta después, requiere confirmación de decimal, unidad y negación antes de uso; entrada manual siempre disponible.

**NOTE.** Conservar original, propuesta y final como versiones identificadas. No rellenar exploración normal, negativos o diagnósticos no aportados. Aceptar cambios por secciones y no sobrescribir silenciosamente. La copia libre actual puede continuar identificada como tal; los PDF/DOCX/JSON actuales corresponden al modelo canónico revisado. Propuesta para implementación posterior: previsualizar el documento exacto elegido y revisar esa versión antes de exportarla. No afirmar ya realizada la integración del final libre; no imponer un bloqueo global por cualquier diferencia entre documentos distintos. Un dato cambiado invalida la revisión de sus dependientes pertinentes, no borra todo el episodio. Copia de borrador inequívoca, sin afirmar firma legal.

**TREATMENT.** Distinguir referencia ante una sospecha de propuesta para diagnóstico explícitamente establecido por el médico. Reutilizar las cinco secciones y fuentes; mostrar si el plan es parcial. Seleccionar una indicación no combina tratamientos de varias hipótesis ni demuestra diagnóstico. Las cifras ejecutables proceden sólo de contrato admitido, con sus datos confirmados. Cobertura de interacciones limitada se muestra «no evaluado», no «sin interacciones».

**DISCHARGE.** La generación de texto no decide el alta. Diferenciar informe profesional de instrucciones comprensibles. Edad/peso, alergias, indicación, producto y concentración se piden según la intención y el contrato; un borrador puede conservar desconocidos explícitos. No inferir antibiótico, duración, receta ni destino. No realizar envíos u órdenes a terceros.

**TESTS.** Mostrar literal/origen/localizador, fecha, unidad y correcciones cuando existan; separar candidato extraído de dato confirmado. No convertir confianza de extracción en certeza diagnóstica. Ante unidad, muestra o duplicado dudosos, no elegir silenciosamente ni calcular lo dependiente. Disponibilidad por función y distribución; una alternativa manual sólo se ofrece si su ruta existe, no como promesa de motor ausente. Ver el original en sesión no obliga a retener el binario. Retención, finalidad y borrado se definen por separado.

## 5. Continuidad, alertas y privacidad

El futuro modelo multiepisodio exige contrato de identidad, ciclo de vida, revisión y respuestas tardías antes de generalizar transferencias. Un resultado de A no rellena B; volver a A no recicla una revisión de otra versión. Diferenciar consulta sin episodio, transferencia selectiva y dato confirmado del episodio. No asumir durabilidad ni recuperación tras cerrar por conservar borrador en una actualización.

Todo dato reutilizado conserva origen disponible, unidad, fecha/localizador y estado: aportado por médico, extraído/confirmado, calculado, referencia o desconocido. Estos nombres son propuesta de diseño, no nuevos enums ya implementados. Desconocido no equivale a negativo, normalidad o estabilidad. Cambiar un dato exige revalidar lo que realmente depende de él.

Alertas con texto y acción, además de color/icono: crítica/bloqueo según contrato, precaución contextual y actualización de fuente pendiente de revisión. Deduplicación no puede ocultar advertencia obligatoria. Una publicación nueva no reemplaza automáticamente pautas ni renueva last_checked. Reglas y cobertura no evaluadas permanecen visibles. Sin nuevos márgenes, umbrales, algoritmos, dosis o adjudicaciones por este estudio.

No audio real, notas o píxeles de pacientes enviados a agentes. Sin originales LOCAL_CUSTODY_ONLY ni reproducción de fuentes restringidas en los anexos. No convertir corpus/validación de eficacia YELLOW en requisito hospitalario universal para funciones de productividad. Las decisiones médicas previas permanecen en su alcance; no se abre un nuevo voto sin cuestión clínica material y evidencia suficiente.

## 6. Diez escenarios sintéticos de aceptación futura

Son criterios propuestos, no ensayos ejecutados ni pautas clínicas. Los mínimos exactos siguen siendo los del contrato autorizado: una brecha de lectura de un revisor no crea nuevos requisitos ni invalida aceptaciones.

| Caso | Falta o ambigüedad | Respuesta/guarda y negativo propuestos | Procedencia de la revisión |
|---|---|---|---|
| S01 adulto80años/80kg, perfusión de noradrenalina | Preparación, valor/unidad objetivo y otros inputs según contrato | Conservar edad/peso separados; referencia o causa de bloqueo sin mL/h no fundamentados. No inferir preparación ni sustituir motor por texto. | Gemini parcialS01; cotejo Work de lista incompleta de dosis objetivo; contrato canónico rige. |
| S02 adrenalina/anafilaxia | Población/vía/contexto o producto según intención | Aclarar lo pertinente antes de cifra individualizada. No elegir vía/población por defecto. Detalles clínicos de vías del texto del agente no se adoptan como nueva recomendación. | Gemini parcialS02, contrato exacto no leído por el proveedor. |
| S03 niño35kg, hidrocortisonaIV | Indicación; edad si la exige el contrato | Retener35kg/IV como aportados, sin indicación por defecto. No calcular una pauta de otra indicación. | Gemini parcialS03; sin nuevo algoritmo ni nueva pauta. |
| S04 niño7kg/fiebre/OMA establecida | Edad, decisión de tratar/destino y producto si procede | Referencia/borrador con lagunas; no antibiótico, duración, alta o mL automáticos. Contrato específico OMA no verificado por esta revisión. | GeminiS04truncado + alternativa CodexS04final, G23/46/88; T13/24–26/46. |
| S05 gasometría | Unidad/muestra/dato pertinente dudosos | Confirmar literal y procedencia; no convertir unidad ni muestra silenciosamente. No exigir FiO2 a todo cálculo por existir en T05. | Alternativa CodexS05; BLOOD_GAS_LOCAL23–46/112–118. Mínimos universales no verificados. |
| S06 pluripatología | Medicación/alergias/función pertinente desconocidas | Plan parcial o referencia sin certificación de seguridad global; listas vacías no significan «ninguna» ni normalidad renal. | Alternativa CodexS06; THERAPEUTIC_PLAN_REVIEW24–26/44–48. |
| S07 diagnóstico establecido/sospecha | Estado diagnóstico o intención ambiguos | Aclarar antes de rotular plan individualizado; varias hipótesis no acumulan pautas. Conservar apoyo limitado y límites YELLOW. | Alternativa CodexS07; G22/44/58, T13–26/92. |
| S08 ambulatorio/domiciliario | Diagnóstico/contexto/destino o inputs de pauta | Documento revisable distinto de receta o aprobación de alta. Cinco secciones no son plan universal completo. | Alternativa CodexS08; G23/44–46, T24–38. |
| S09 polimedicación | Lista o cobertura de reglas incompletas | Mostrar no evaluado/no aplicable/comprobado según evidencia. Cero alertas no certifica compatibilidad. | Alternativa CodexS09; G44/52, T44–48. |
| S10 reevaluación/A-B-A | Episodio y versión del dato/revisión | Respuesta tardía deA no modificaB; cambio relevante revoca revisión dependiente sin borrar otros datos confirmados. No confundir versionesPWA con pacientes. | Alternativa CodexS10; G38/50–51, T18/32–40; TECHE7.01. |

Las referencias G/T/B anteriores se desarrollan con rutas y líneas en `gmfc/REVISION_CLINICA_ALTERNATIVA.md`; las de los tres primeros casos proceden del briefing y respuesta parcial, no de una nueva lectura científica del proveedor. No se inventa una validación10/10 de Gemini.

## 7. Disposición de las propuestas

**ADOPTAR como alcance propuesto:** reutilizar catálogo/motores/exportadores/guardas; acceso manual rápido; origen del dato; desconocido explícito; revisión granular; versión copiada/exportada identificada; transferencias deliberadas; alertas pertinentes no ocultables; layout y preferencias existentes. El cotejo UX01–27 y la matriz técnica37 contienen trazabilidad individual.

**REFORMULAR:** final libre versus modelo canónico; continuidad versus persistencia; YELLOW versus apoyo limitado; formulario frente a fórmula; extracción frente a interpretación; archivo recibido versus admitido; offline por capacidad; genérico aceptado frente a original desconocido. No declarar defecto del producto por un riesgo futuro ni por lenguaje de una propuesta ya corregida.

**APLAZAR:** elección de voz/OCR/LLM, almacenamiento durable, infraestructura remota, portada definitiva y automatizaciones no demostradas hasta aceptar alcance y justificar utilidad. No equivale a exigir proveedores nuevos ni nuevas fases clínicas.

**DESCARTAR:** motores duplicados, dosis generadas, datos clínicos normales inventados, proveedor remoto obligatorio, mezcla de pacientes, nuevas votaciones de decisiones vigentes, permiso inferido de un ABSTAIN y métricas de ahorro/velocidad/seguridad no medidas.

## 8. Orden propuesto y verificación proporcional

1. IMP00/02/10: aceptar contrato de versión de documento, capacidad visible e identidad de episodio. Esta guía no implementa esas decisiones.
2. Tras aceptación: menor flujo FAST manual y NOTE reutilizando lo existente. No router universal generativo ni reescritura de motores.
3. Antes de transferencias generalizadas: contrato explícito de episodios y negativos de aislamiento. Persistencia durable se decide por separado.
4. Extender el mismo modelo a planes, alta y pruebas según capacidades disponibles y contratos; sin convertir servicios ausentes en requisitos del núcleo.
5. IMP09 comprueba sólo el incremento implementado: texto/cifras/negación/Unicode, versión exportada, obsolescencia, unidad/procedencia, interrupción/episodio, capacidades ausentes y accesibilidad del flujo cambiado. IMP03 sólo si cambian bytes de paquete; IMP04–08 remotos condicionales, IMP11 separado.

Tiempo hasta primer resultado útil, acciones, correcciones, errores, carga percibida, teclado/foco/lector/contraste, móvil/tablet y temas son mediciones futuras comparables, no PASS de este estudio. Reutilizar QA vigente para componentes idénticos. No repetir D→E→D por documentación, no ejecutar campañas preventivas ni instalar herramientas innecesarias.

## 9. Evidencia, coordinación y aceptación

Emergency MCP se usó realmente para metadatos del snapshot, no para CI viva ni validación clínica. GitHub MCP verificó PR/fuentes y la integración técnica separada; Claude Code fue CLI sólo lectura y Gemini/Antigravity se coordinaron mediante Computer Use al no existir un conector de chat suficiente en el inventario habilitado. Registro útil en `gmfc/MCP_USO_REAL.json`; instalado no equivale usado y no se afirma ahorro medido.

PR142 y sus originales quedan intactos porque su lease de autor no está confirmado. La propuesta se mantiene en rama documental propia; la referencia permanente y CENTRAL sólo las actualiza el coordinador único. No se sustituye la matriz clínica ni se añaden IDs de implementación.

Estado de esta guía: propuesta de alcance con revisión Gemini incompleta explícita y alternativa documental atribuida. La aceptación pendiente es del propietario sobre el alcance, no una nueva aprobación médica general. No hay preguntas clínicas materiales nuevas acreditadas ni cambios de last_checked, dosis, algoritmos o estadosYELLOW. Ningún informe de agente permite uso asistencial o despliegue.
