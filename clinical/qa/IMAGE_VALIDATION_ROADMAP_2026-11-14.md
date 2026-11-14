# Emergency — Incorporación, evaluación y mejora de imágenes clínicas

Fecha:14/11/2026. Versión2:primer lote docente incorporado; evaluación diagnóstica pendiente. Alcance abierto a todas las modalidades. No cambia estados de validación de imágenes.

## Actualización operativa V2 — 14/11/2026

### Qué ha empezado realmente

Se ha incorporado un primer lote de **5 archivos reales:3 imágenes y2 vídeos**, agrupados en **4 casos de fuente**:dos proyecciones de una radiografía de tórax del mismo caso,una TC estática anotada,un clip ecográfico y una secuencia TC renderizada. No se acredita independencia de pacientes entre fuentes. Licencias y autores constan por archivo. Es material docente/desarrollo, **excluido de métricas de precisión** y pendiente de revisión clínica y privacidad completa de clips.

Se comprobaron descarga,tamaño,SHA-256,decodificación y reproducción preparable mediante visorHTMLoffline. Los vídeos tienen6,0sy24,4s; los originales conservan25 y 10 fotogramas/s,respectivamente. Se extrajeron4fotogramas de navegación por vídeo; no se evaluó movimiento continuo. La inspección visual detectó que la imagen candidata de hidronefrosis eraTC con flechas, no POCUS. Se corrigió su modalidad y quedó marcada como anotada.

El paquete incluye originales,visor,atribuciones,manifest,colaCSVpara revisión,plantilla del siguiente lote y validadoroffline. Las miniaturas sirven para navegar,no para certificar un signo dinámico. No se han configurado servicios externos,transmitido imágenes a un proveedor,ajustado pesos ni producido una nueva cifra de precisión.

### Capacidad actual y enlace de YouTube

En este entorno se dispone de acceso a páginas y de herramientas para inspeccionar imágenes y extraer fotogramas de vídeos autorizados. **Un enlaceYouTube no garantiza acceso a sus píxeles ni visión continua del vídeo.** Título,subtítulos o transcripción permiten estudiar el contenido verbal,no medir reconocimiento visual. Si los fotogramas son accesibles,se puede analizar lo realmente inspeccionado,indicando el alcance. Nunca afirmar que se vio todo el vídeo por haber leído su transcripción.

El adaptador del repositorio `clinical_note_vision_adapter.py` requiere un proveedor HTTPS; en la comprobación de este entorno la configuración está ausente. El flujo binario existente no define un contrato de vídeo validado. Leer un clip con ffmpegno demuestra que el motor clínico lo procese. No se introduceMP4como si fuera una foto. Primero habrá que configurar/verificar el proveedor aprobado y después un contrato temporal específico o una representación de fotogramas validada para cada tarea. Las credenciales permanecen fuera del chat y del repositorio.

### Tres formas distintas de mejorar

| Mecanismo | Qué cambia | Situación |
|---|---|---|
| Instrucciones y reglas de calidad | Cómo se pide/limita la interpretación | Se puede desarrollar y comparar por versión. |
| Recuperación de casos similares | Ejemplos del banco disponibles durante la interpretación | Requiere implementar recuperación visual/contextual y excluir siempre el test. No está implantada por este lote. |
| Entrenamiento/ajuste de pesos | Parámetros de un modelo compatible | Requiere tecnología,derechos,datos y evaluación separados. No se ha ejecutado. |

Leer una web o guardar una imagen no produce por sí solo ninguna de esas mejoras persistentes. Los casos corregidos se registran como propuestas para el siguiente ciclo,con versión y revisión; no se autoaprueban ni actualizan el motor en producción.

### Fuentes web y permisos

Las webs radiológicas pueden aportar ejemplos y referencias; comprobar por caso licencia,uso previsto y derecho a descargar,transformar o entrenar. **Radiopaedia no se trata como un banco libre para extraer masivamente**: su aviso de retirada de2025denuncia extracción automatizada no autorizada; la página actual de términos no pudo leerse directamente en esta revisión. No se ha descargado material de Radiopaedia. Sus casos o textos diagnósticos ya visibles no son un examen ciego limpio.

YouTubetambién establece condiciones de descarga y acceso automatizado; para el banco se prefieren archivos facilitados por el titular o repositorios con licencia explícita. Un vídeo docente que anuncia el diagnóstico pertenece a docencia, no al test. Para películas diagnósticas, conservar duración,orden,fps,resolución y metadatos clínicos necesarios; paraTC/RMpreferir series DICOM autorizadas a una grabación de pantalla.

### Cantidad mínima medible:propuesta de proyecto, no requisito universal

Contar **casos/pacientes por objetivo diagnóstico**, no imágenes,recortes,cortes ni fotogramas. El banco docente es adicional al conjunto de evaluación y no tiene una cuota mínima universal que garantice aprendizaje.

| Etapa | Casuística propuesta por pregunta binaria | Qué se obtiene |
|---|---|---|
| Prueba de incorporación | 20–30 casos diversos | Fallos de archivos,calidad,etiquetado y flujo; no una cifra estable de precisión. |
| Piloto diagnóstico | 50 positivos+50 negativos | Primera señal cuantitativa exploratoria; intervalos amplios. |
| BasalV0práctico | **100 positivos+100 negativos reservados** | Punto de partida medible por tarea; todavía depende del espectro y la referencia. |
| Mayor precisión | 200 positivos+200 negativos o cálculo específico | Intervalos más estrechos; no sustituye validación externa/prospectiva. |

Los negativos deben incluir imitadores difíciles,además de normalidad. Mantener una cohorte local representativa aparte de la enriquecida; la proporción50/50no representa prevalencia real y susVPP/VPNno se trasladan directamente a urgencias. Para tareas multiclase o raras,dimensionar cada clase y no prometer que200 casos totales bastan. Varios objetivos pueden evaluarse en un mismo estudio con referencias independientes,pero no multiplicar artificialmente el número de pacientes.

Ejemplos calculados conWilson95%:
-45/50detectados=90%;ICaproximado78,6–95,7%.
-90/100detectados=90%;ICaproximado82,6–94,5%.
-95/100detectados=95%;ICaproximado88,8–97,8%.
-190/200detectados=95%;ICaproximado91,0–97,3%.

Son ejemplos aritméticos,no resultados de Emergency. Los denominadores positivos se refieren a sensibilidad; para especificidad hacen falta negativos suficientes. Si el sistema se abstiene,se informa cobertura y casos no resueltos conforme al calculador actual; no se eliminan para embellecer resultados. No se fija una precisión basal antes de ejecutar la prueba.

### Flujo rápido para el equipo

1. **Una carpeta por caso**, con identificador seudónimo estable. Nombres neutros para material reservado. No poner el diagnóstico en los archivos de examen.
2. **UnCSVpor lote**, con identificador de agrupación,modalidad,archivos,pregunta clínica,diagnóstico de referencia,método de confirmación,revisor,autorización/desidentificación y destino desarrollo/test. Las referencias del test permanecen separadas del acceso del motor.
3. **Automatización local**:integridad,formato,duración,metadatos,duplicados,miniaturas y preparación de la cola. El reconocimiento de identificadores necesita revisión; no se declara anonimización automática infalible.
4. **Revisión humana concentrada**:aceptar,corregir o indeterminado; priorizar discrepancias,etiquetas dudosas,imitadores y errores graves. Para el test,completar la referencia de todos los casos según protocolo; no validar únicamente las salidas que parecen equivocadas.
5. **Predicción congelada** por versión y tarea con los mismos datos disponibles. Guardar respuesta original,timestamp,modelo,configuración y contexto. Después revelar la referencia y generar resultados.
6. **CicloV1/V2** sobre desarrollo; evaluación pareada y auditoría externa. No ajustar con las respuestas del test ni usar el test como fuente de ejemplos. Revisión periódica y tras cambios relevantes de modelo; no activar una actualización sin autorización.

Para acelerar la siguiente fase son útiles:(a)una carpeta/ZIPautorizado o enlaces a repositorios concretos,(b)etiquetas/informes de referencia y un revisor clínico,(c)identificación del proveedor visual aprobado y del entorno donde se ejecutará,para configurarlo de forma segura,(d)prioridad inicial de tareas y población adulta/pediátrica. Se pueden escoger tareas por volumen y daño de omisión; el catálogo seguirá abierto. Ya se avanzó con fuentes públicas explícitamente licenciadas sin esperar esas decisiones.

### Criterio de éxito y tablero

Mostrar por tarea:casos independientes,calidad,referencia,sensibilidad/especificidad cuando sean calculables,cobertura,errores críticos yIC95%,más fecha/modelo/versión. Separar fallos de extracción de texto,percepción,razonamiento y recomendación. Fijar límites de seguridad antes del examen; no cambiar umbrales para aprobar una versión que falla. La conformidad documental del marco no acredita competencia de visión.

### Fuentes adicionales verificadas paraV2

- YouTube: https://www.youtube.com/static?template=terms — permisos/restricciones de acceso y descarga.
- Aviso de Radiopaedia archivado porHugging Face Legal,12/03/2025: https://huggingface.co/datasets/huggingface-legal/takedown-notices/raw/8e921b661f36700c40a6440aca63f85f7d3cbdb8/2025/2025-03-12-Radiopaedia.md — queja sobre copia automatizada,no revisión jurídica completa de las condiciones actuales.
- Licencias de cada archivo:en `manifest.json` del primer lote y su página original deCommons. No se extiende la licencia de un archivo al resto de una web.


## Protocolo metodológico de referencia

## 1. Objetivo y situación de partida

Emergency dará orientación al profesional, identificará hallazgos y limitaciones y solicitará confirmación humana. Una interpretación negativa no debe convertirse automáticamente en exclusión de una enfermedad ni criterio de alta.

El repositorio ya dispone de registro de fuentes, preparación de cohortes, separación de referencias, congelación de predicciones, validación de datos y cálculo de métricas. Esto es infraestructura, no rendimiento clínico demostrado.

La precisión del motor multimodal actual por modalidad y enfermedad está **NO ESTABLECIDA**. El ensayo histórico PTB-XL NATURAL_500 evaluó una regla de ingeniería sobre imágenes de tira de ritmo:500estudios,3positivos de FA,43falsos positivos entre los clasificados,93abstenciones y2no diagnósticos. Cobertura81%; no es81%de exactitud ni precisión de ChatGPT. Las métricas binarias estándar se suprimieron por política. Tres positivos no permiten una estimación sólida de sensibilidad. La plantilla sintética de pruebas tampoco mide visión.

Importación preparada no significa acceso real concedido: revisar las condiciones y autorizaciones de cada fuente antes de descargar. No usar credenciales ni datos clínicos en servicios nuevos sin autorización.

## 2. Unidad de evaluación: una tarea concreta

Crear un catálogo ampliable. Cada entrada define modalidad, población, objetivo, formato requerido, contexto disponible, referencia y consecuencia del error. Evaluar tareas multilabel por hallazgo; una media global no sustituye los resultados de cada tarea.

| Modalidad | Ejemplos, no catálogo cerrado | Entrada y referencia apropiadas |
|---|---|---|
| Ecografía/POCUS | Hidronefrosis, litiasis, ascitis,TVP,neumotórax,derrame,función cardíaca | Vistas y secuencias necesarias; revisión experta y prueba confirmatoria/seguimiento según pregunta. Una imagen fija no demuestra compresibilidad o deslizamiento pulmonar. |
| Radiografía | Tórax, fracturas, luxaciones, dispositivos | Proyecciones completas, lateralidad; lectura experta y confirmación apropiada para lesiones ocultas. |
| TC/RM | Hemorragia, efecto de masa y otras tareas definidas | Series, ventanas y planos necesarios; informe experto sobre estudio completo. Una captura aislada tiene un alcance distinto. |
| ECG | Ritmo, conducción, isquemia y otros patrones | Trazado legible, calibración y contexto definido; referencia independiente. Separar señal original de foto/render. |
| Dermatología/heridas | Lesiones, infección y complicaciones | Imágenes/contexto pertinentes; referencia clínica, histología o seguimiento cuando proceda. |
| Oftalmología | Hallazgos externos/fondo de ojo/otras técnicas | Técnica identificada y referencia oftalmológica apropiada. No atribuir a una foto información de una exploración que no muestra. |
| Informes/gasometría | Lectura de cifras, unidades y posterior interpretación | Transcripción verificada contra original; medir extracción e interpretación por separado, incluidos errores de decimal y unidad. |

## 3. Incorporación de cada caso

1. Verificar procedencia, derechos de uso, consentimiento/base de autorización aplicable y condiciones de reutilización. Acceso público no equivale a permiso de entrenamiento.
2. Desidentificar metadatos DICOM, texto incrustado, nombres de archivo y contenido visible; comprobar también fotogramas. Conservar originales autorizados protegidos y derivados evaluables separados.
3. Asignar identificadores seudónimos de paciente/episodio/estudio/caso; conservar vínculos de agrupación sin identificadores directos. Un hash por sí solo no acredita anonimización.
4. Registrar modalidad, anatomía, vistas, calidad, dispositivo, centro, fecha/periodo, edad/grupo y contexto clínico autorizado. No inventar datos ausentes.
5. Registrar diagnóstico/hallazgos, método de referencia, revisores, fecha, certeza y discrepancias en un archivo separado del material que verá el motor. Etiquetas ambiguas deben conservarse y manejarse según protocolo previo.
6. Rechazar duplicados o agruparlos; detectar también recortes, versiones comprimidas y fotogramas del mismo estudio. Varias imágenes del mismo paciente no son varios pacientes independientes.
7. Incluir normales, negativos, variantes, imitadores, coexistencia de patologías, enfermedad precoz/leve, errores técnicos y estudios no diagnósticos. Mantener un conjunto representativo consecutivo/local además de conjuntos enriquecidos con patologías raras.

Campos mínimos del registro:case_id,patient_group_id,study_group_id,modality,target,source,rights_status,deidentification_status,format,views,quality,reference_method,reviewer_ids,reference_label,split,model_version,prompt_version,prediction_timestamp,reference_reveal_timestamp. Añadir checksum de archivos y trazabilidad de transformaciones.

## 4. Cómo validar las etiquetas

La referencia no puede ser la respuesta de Emergency ni un diagnóstico copiado sin verificar de Internet. Como propuesta inicial, dos lectores competentes independientes y un tercero para resolver desacuerdos; adaptar recursos y referencia a cada tarea. No es una regla universal de una guía.

Separar:hallazgo visible, diagnóstico clínico, urgencia y conducta. Los lectores de referencia no conocerán la respuesta del modelo cuando adjudiquen. Si no hay referencia suficiente, el caso puede servir para docencia, pero no para medir exactitud de ese diagnóstico. Las etiquetas automáticas de informes deben identificarse como tales, no tratarse como verdad experta sin contraste.

La evaluación debe ser ciega: eliminar flechas, leyendas diagnósticas y respuestas del contexto. Los ejemplos publicados pueden haber formado parte del entrenamiento de un modelo general; documentar posible contaminación y priorizar un test local/externo no publicado para la confirmación.

## 5. Separar desarrollo, ajuste y examen

- **Banco docente/desarrollo:** ejemplos conocidos, búsqueda de casos, diseño de instrucciones, recuperación de imágenes similares o entrenamiento si la tecnología lo permite.
- **Validación de desarrollo:** ajustar umbrales y seleccionar versión; no constituye examen final.
- **Test reservado:** pacientes/estudios no usados en desarrollo ni recuperables por el motor; referencias ocultas hasta congelar respuestas. Añadir prueba externa por centro/equipo/periodo.

Separar por paciente antes de generar recortes o aumentos. ParaTC, los cortes de un estudio permanecen juntos; para vídeo, todos los fotogramas permanecen juntos. El test no entra en búsquedas de ejemplos. Congelar modelo, instrucciones, herramientas, preprocesado y contexto; registrar versión deAPI y fecha. Un cambio del proveedor obliga a comprobar de nuevo el rendimiento.

No fijar70/15/15 como ley: reservar suficientes positivos y negativos por tarea y planificar el tamaño según incertidumbre aceptable. Un test consultado reiteradamente puede contaminar la selección; mantener un conjunto de auditoría adicional y renovarlo con casos nuevos bajo protocolo.

## 6. Medición inicial V0

1. Elegir primeras tareas y formato de respuesta sin convertirlas en límite del catálogo.
2. Reunir un piloto de30–50estudios independientes por tarea como propuesta logística para detectar fallos, no como validación concluyente.
3. Definir antes de evaluar:inclusión,exclusión,referencia,objetivos de seguridad y tratamiento de abstenciones/no diagnósticos.
4. CongelarV0 y predecir una vez por caso en condiciones predefinidas. Evaluar imagen sola y con contexto como experimentos distintos si interesan ambos.
5. Guardar respuesta original, hallazgos, localización/lateralidad, incertidumbre, calidad, urgencia y recomendación. No imponer diagnósticos a imágenes insuficientes.
6. Revelar referencias después y calcular resultados por tarea, no por número total de archivos.

Como aproximación binomial independiente para planificar: n≈1,96²×p×(1−p)/d². Para sensibilidad esperada0,95 y margen±0,05 se obtienen≈73casos **positivos**; para especificidad0,90 y±0,05,≈139**negativos**. Son aproximaciones, no tamaños garantizados ni mínimos universales: comprobar intervalos exactos/Wilson, agrupación, prevalencia, pérdidas y diseño con apoyo estadístico. Para precisión mayor se requieren más casos. Los tamaños anteriores son por objetivo, no por modalidad entera.

## 7. Qué mostrar en el tablero

| Métrica | Interpretación |
|---|---|
| Casos/pacientes positivos y negativos | Denominadores y representatividad; no contar100fotogramas como100pacientes. |
| Sensibilidad y falsos negativos | Patología detectada y omitida; revisar omisiones críticas individualmente. |
| Especificidad y falsos positivos | Evitar falsas alarmas y derivaciones innecesarias. |
| VPP/VPN | Dependen de prevalencia; no trasladar valores de un banco enriquecido a urgencias reales. |
| Cobertura, abstención y no diagnósticos | Qué proporción interpreta y qué deja sin resolver. Informar siempre. |
| Intervalos de confianza95% | Mostrar incertidumbre; bootstrap por paciente si hay dependencia. |
| Errores de localización,lateralidad,medición y extracción | Un diagnóstico acertado puede acompañarse de un error peligroso. |
| Error crítico y orientación insegura | Falsa tranquilidad, omisión urgente, invención de hallazgos o conducta peligrosa. Rúbrica previa y adjudicación humana. |
| Tiempo,repetibilidad y subgrupos | Robustez entre equipos,centros,edades,calidad y cambios de versión. No afirmar equivalencia con muestras pequeñas. |

El calculador actual de Emergency suprime sensibilidad/especificidad/VPP/VPN/exactitud estándar si existe alguna abstención o no diagnóstico; muestra cobertura y recuentos no resueltos. Mantener esta protección. Para una futura ampliación, presentar métricas condicionales claramente etiquetadas junto a cobertura y resultados globales de seguridad según un plan preespecificado; no excluir casos difíciles para mejorar cifras. No se modifica el calculador en este encargo.

Una confianza verbal de90%no es una probabilidad calibrada. Solo medir calibración/Brier cuando exista una probabilidad definida y evaluable. Para segmentación, añadirDice/IoU; para medidas, error absoluto y análisis de concordancia; no imponer estas métricas a tareas que no segmentan ni miden.

## 8. Mejora controlada V1,V2…

Revisar fallos del conjunto de desarrollo y clasificarlos:adquisición,calidad,referencia,percepción,razonamiento o salida/seguridad. Elegir una intervención identificable:mejor adquisición,preprocesado,instrucciones,recuperación de ejemplos,modelo o ajuste de pesos cuando esté disponible y autorizado.

Guardar un caso **no modifica automáticamente los pesos del motor**. Recuperación de ejemplos, mejora de instrucciones y entrenamiento son mecanismos distintos y deben registrarse por separado. No activar entrenamiento ni transmisión de datos por el mero hecho de incorporarlos al banco.

Comparar versiones de forma pareada en los mismos casos reservados, con intervalos de las diferencias y pruebas apropiadas al diseño. Una ganancia en media no compensa un deterioro en omisiones críticas. Analizar errores nuevos y resultados por subgrupo. Si falla el criterio de seguridad previamente acordado, conservar versión anterior y corregir en desarrollo; nunca retocar la respuesta congelada.

Antes de uso asistencial ampliado:prueba externa y después evaluación prospectiva silenciosa, sin que la salida determine la atención. Posteriormente, evaluación del clínico con y sin ayuda para medir beneficio real y sesgo de automatización. Cada ampliación de patología/modalidad vuelve a pasar por evaluación propia.

## 9. Niveles de madurez propuestos para el proyecto

| Nivel | Evidencia necesaria | Qué permite afirmar |
|---|---|---|
| N0 | Flujo técnico y ejemplos conocidos | Funciona la entrada/salida; precisión no establecida. |
| N1 | Piloto ciego con referencia independiente | Estimación exploratoria por tarea, con incertidumbre. |
| N2 | Test reservado suficiente y evaluación externa | Rendimiento retrospectivo definido en esas poblaciones/condiciones. |
| N3 | Evaluación prospectiva local silenciosa | Rendimiento observado en el circuito real estudiado. |
| N4 | Evaluación de ayuda al clínico y vigilancia | Utilidad/seguridad del uso supervisado en el alcance evaluado. |

Son niveles internos propuestos, no certificación externa. El marco documentalGREEN no cambia estos niveles ni autoriza diagnóstico autónomo. No existe un umbral único de95%que valide todas las tareas. Acordar por tarea un límite inferior de sensibilidad/especificidad, cobertura mínima y tolerancia a errores críticos según uso y daño; fijarlos antes del test.

## 10. Primera entrega ejecutable

1. Reutilizar el registro de fuentes y manifiestos existentes; ampliar modalidades sin duplicar el sistema.
2. Crear el catálogo abierto de tareas y ficha de anotación correspondiente.
3. Incorporar el primer lote autorizado y etiquetado; informe de calidad y duplicados.
4. CongelarV0,cohorte e instrucciones; emitir predicciones ciegas.
5. Publicar tablero basal por tarea con intervalos y ejemplos de errores revisados.
6. Crear lote de desarrolloV1 y plan de comparación, conservando test separado.

Responsabilidades:coordinador clínico define uso/daño;especialistas adjudican referencias;responsable de datos verifica derechos/desidentificación/separación;ingeniería mantiene versiones y predicciones;analista revisa tamaño,métricas e incertidumbre. Pueden combinarse funciones, pero se conserva independencia entre respuesta del motor y referencia.

ActualizaciónV2:se han materializado5 archivos para docencia/desarrollo, no para precisión ciega. No se han entrenado modelos ni ejecutado una nueva medición clínica. No se asignan porcentajes basales nuevos ni se promueven módulos de interpretación aGREEN.

## Referencias metodológicas

- STARD-AI 2025: https://www.nature.com/articles/s41591-025-03953-8 . Marco de comunicación de estudios de exactitud; no certifica un sistema ni fija umbrales universales.
- FUTURE-AI 2025: https://www.bmj.com/content/388/bmj-2024-081554 . Evaluación externa/local, trazabilidad y vigilancia.
- TRIPOD-LLM 2025: https://www.nature.com/articles/s41591-024-03425-5 . Versiones,instrucciones y evaluación deLLM; aplicar con cautela a sistemas multimodales.
- Emergency: `clinical/qa/IMAGE_VALIDATION_POLICY.md`, `clinical/qa/PHASE5_IMAGE_CLOSURE.md`, `clinical/qa/PTBXL_AFIB_IMAGE_BASELINE_V1.md`, `clinical/qa/image-dataset-source-registry.json`, `clinical/scripts/calculate_blinded_image_metrics.py`.
