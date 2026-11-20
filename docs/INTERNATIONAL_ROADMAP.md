# Emergency — hoja de ruta internacional

Fecha: 16/11/2026. Directriz del propietario: desarrollar una plataforma internacional, amplia y ampliable de apoyo clínico, formación y coordinación en urgencias y cuidados agudos.

Este plan desarrolla [INTERNATIONAL_SCOPE.md](INTERNATIONAL_SCOPE.md). Un hospital o país constituye un perfil de aplicación; no define el alcance completo del producto. Las capacidades nuevas se incorporarán mediante entregas verificables, conservando fuentes, trazabilidad y límites clínicos.

## Situación de partida y estados

La documentación del candidato registra 131 módulos, 196 procedimientos canónicos y cuatro alias, 89 pautas pediátricas, escalas, nota clínica estructurada, exportaciones y circuitos de imagen. Estos antecedentes no equivalen a una nueva ejecución de sus pruebas ni a validación internacional. Los colores se consultan en el registro de evidencia vigente; algunas tablas y cifras de los documentos maestros son históricas.

La interfaz ya registra **español, inglés, portugués y chino simplificado** en `app/src/i18n/index.ts`, con archivos de traducción. `Settings.tsx` permite elegir idioma, tema y representación de microgramos; incorpora el selector opcional de contexto de referencia en la rama internacional. La existencia de cuatro idiomas de interfaz no acredita traducción clínica integral validada.

Estados de este plan:

- **Preparado:** documento o especificación entregados; no implica funcionalidad ejecutable.
- **Propuesta:** ampliación definida, pendiente de implementación.
- **Pendiente:** comprobación o validación aún no acreditada.

P0 identifica fundamentos necesarios para aplicar el nuevo alcance. P1 identifica ampliaciones que pueden avanzar en paralelo cuando sus dependencias estén resueltas. Los responsables indicados son **funciones propuestas**, no personas asignadas ni compromisos confirmados.

## Capacidades, responsabilidades y dependencias

| ID | Capacidad | Prioridad y estado | Responsable por función | Dependencias |
|---|---|---|---|---|
| INT-01 | Alcance, coordinación y perfiles | P0; gobernanza y selector de contexto implementados en la rama internacional | Coordinación de producto y arquitectura | Directriz del propietario |
| INT-02 | Evidencia clínica internacional | P0; política de coherencia internacional INT-02A preparada; diferencias módulo × jurisdicción pendientes de evaluación | Dirección clínica y gestión de evidencia | INT-01 |
| INT-03 | Farmacología y presentaciones | P1; ampliación propuesta | Farmacia clínica e ingeniería clínica | INT-01, INT-02 |
| INT-04 | Procedimientos y recursos | P1; ampliación propuesta | Responsables de procedimientos y experiencia de usuario | INT-01, INT-02 |
| INT-05 | Entornos asistenciales | P1; ampliación propuesta | Responsables clínicos por entorno | INT-01, INT-02; INT-03/04 cuando apliquen |
| INT-06 | Idiomas y accesibilidad | P1; interfaz existente; cobertura clínica pendiente | Localización clínica y accesibilidad | INT-01, INT-02 |
| INT-07 | Imagen, ECG y POCUS | P1; infraestructura parcial; rendimiento pendiente | Imagen, POCUS e ingeniería de evaluación | INT-02, INT-10, INT-12 |
| INT-08 | Documentación e interoperabilidad | P1; exportación existente; conectores propuestos | Interoperabilidad e ingeniería de datos | INT-01, INT-11 |
| INT-09 | Educación y simulación | P1; ampliación propuesta | Formación y simulación clínica | INT-02, INT-04, INT-06 |
| INT-10 | Investigación y validación multicentro | P0/P1; diseño propuesto; validación pendiente | Metodología, calidad y revisores independientes | INT-01, INT-02; capacidad evaluada |
| INT-11 | Despliegue y gestión de datos | P1; ampliación propuesta | Plataforma, seguridad y operación | INT-01 |
| INT-12 | IA independiente del proveedor | P1; ampliación propuesta | Arquitectura de IA y coordinación técnica | INT-01, INT-02, INT-11 |

## Alcance verificable de cada entrega

### INT-01 — Alcance, coordinación y perfiles

**Base:** instrucciones de colaboradores, registros de decisiones y handoffs. Esta entrega establece la orientación internacional y su hoja de ruta.

**Implementado y probado en la rama internacional:** esquema explícito de contexto y controles opcionales para jurisdicción, organización y entorno; acceso al núcleo de referencia sin país ni centro elegidos; dos contextos sintéticos que reutilicen los mismos módulos canónicos. Idioma, país y disponibilidad de recursos no se infieren unos de otros. El contexto solo condiciona la función o diferencia que dependa de él. Cada entrega registra versión base, alcance, responsable y recepción de directrices. El esquema y el selector de Ajustes se verifican con las [pruebas de contexto](../app/src/context/reference-context.test.ts) y las [pruebas de interfaz](../app/src/test/reference-context.test.tsx). Los perfiles describen recursos declarados.

### INT-02 — Evidencia clínica internacional

**Base:** módulos, fuentes, registro de evidencia y cola de actualizaciones.

**Entrega INT-02A — política de coherencia internacional preparada:** [international-guideline-policy.md](../clinical/references/international-guideline-policy.md) establece un núcleo basado en guías internacionalmente reconocidas por calidad metodológica, vigencia, consenso y aplicabilidad. El catálogo de Europa por país, Reino Unido y su nación cuando proceda, Estados Unidos, Canadá y Latinoamérica/Caribe por país sirve para comprobar diferencias; no define una plataforma separada por territorio.

**Aceptación siguiente:** documentar la selección de guía o algoritmo canónico por módulo y evaluar las diferencias materialmente relevantes. La matriz módulo × jurisdicción registra cobertura de revisión, no protocolos nuevos. Cada recomendación declara fuente, versión, población y ámbito de aplicación; cada diferencia justificada identifica un anexo o variante puntual, completo en el tramo que modifica, y sus limitaciones pendientes. Las discrepancias permanecen visibles, con decisión trazable; no se mezclan secuencias ni se promedian pautas. Se conserva un mismo módulo clínico y una aprobación organizativa no se convierte en aprobación mundial.

**Límite de esta entrega:** la política está preparada; no se ha completado la evaluación de diferencias de todos los módulos. No se ha implementado un selector de jurisdicción ni se ha acreditado conformidad regional por publicar la política. Consultar el núcleo no exige un selector, país o centro. Los ámbitos aún no revisados se identifican como pendientes sin bloquear capacidades generales que no dependan de esa revisión, y sin crear protocolos superlocales.

### INT-03 — Farmacología y presentaciones

**Base:** regímenes pediátricos, calculadoras y contratos agudos; 19 bloqueos conservados.

**Aceptación:** separar principio activo, pauta, producto, preparación, disponibilidad y protocolo del perfil. Cambiar un perfil no altera dosis canónicas; la ausencia de stock en un centro no se interpreta como inexistencia global. Preparaciones no verificadas conservan su limitación específica. Este plan no modifica fórmulas ni desbloquea contratos.

### INT-04 — Procedimientos y recursos

**Base:** catálogo canónico, alias y navegación por familias.

**Aceptación:** conservar un ID y una guía por técnica, con variantes de contexto identificadas. Mostrar requisitos de material, capacitación y rescate según recursos declarados, sin asumir disponibilidad de especialistas. Ampliar ayudas visuales y listas de comprobación sin duplicar contenido clínico.

### INT-05 — Entornos asistenciales

**Base:** contenidos de urgencias, críticos, pediatría y otras poblaciones especiales.

**Aceptación:** escenarios sintéticos hospitalarios, prehospitalarios, de transporte, rurales y de recursos limitados muestran aplicabilidad y necesidades de escalada. No se presuponen UCI, laboratorio, imagen o traslado. La ampliación de entornos exige revisión del contenido afectado; no crea recomendaciones prescriptivas por analogía.

### INT-06 — Idiomas y accesibilidad

**Base:** cuatro idiomas de interfaz, preferencias y exportaciones con trabajo previo de Unicode.

**Aceptación:** inventario de cobertura por idioma; revisión de textos clínicos y pruebas de números, unidades, negaciones y umbrales. Navegación por teclado y lectura asistida verificadas en recorridos representativos. Cambiar idioma no cambia jurisdicción ni pauta; el contenido pendiente de traducción se identifica.

### INT-07 — Imagen, ECG y POCUS

**Base:** rutas multimodales, controles de privacidad, metodología ciega y material docente inicial. No consta precisión multimodal general establecida.

**Aceptación:** evaluación por tarea, modalidad y población con referencia independiente, separación entre desarrollo y evaluación, abstención y resultados trazables. Cada adaptador declara versión y limitaciones. Incorporar imágenes docentes o un proveedor visual no acredita rendimiento diagnóstico.

### INT-08 — Documentación e interoperabilidad

**Base:** nota estructurada, revisión de resultados y exportaciones JSON/PDF/DOCX e impresión.

**Aceptación:** contratos de intercambio y conectores a sistemas clínicos, incluyendo FHIR/HL7/DICOM cuando corresponda, con versiones elegidas y pruebas sintéticas. Conservar procedencia y distinguir informe original de interpretación. No se anuncia conexión operativa antes de comprobarla con el sistema autorizado.

### INT-09 — Educación y simulación

**Base:** casos sintéticos, materiales docentes y laboratorio no prescriptivo de insulinoterapia.

**Aceptación:** itinerarios por competencias y roles, casos versionados y evaluación formativa. Modo docente reconocible; resultados separados de órdenes asistenciales y de validación clínica. Las variantes lingüísticas y de recursos conservan objetivos, fuentes y límites del caso.

### INT-10 — Investigación y validación multicentro

**Base:** QA técnico, revisiones documentales y aceptaciones de alcance limitado.

**Aceptación:** protocolo de evaluación por país, población y entorno, con criterios previos, referencias independientes, control de versiones y análisis de resultados. Separar pruebas técnicas, revisión del contenido, aceptación operativa y evaluación prospectiva. Una aceptación no se hereda automáticamente entre centros. El acceso o transferencia de datos requiere su autorización concreta.

### INT-11 — Despliegue y gestión de datos

**Base:** backend de confianza, controles de privacidad y revisión humana.

**Aceptación:** opciones de despliegue documentadas, aislamiento por organización, roles y auditoría. Dos perfiles no comparten datos por defecto. Un modo sin conexión debe informar versión y vigencia del contenido. Ubicación, proveedor y condiciones de tratamiento se seleccionan explícitamente; no se presume conformidad normativa universal.

### INT-12 — IA independiente del proveedor

**Base:** circuitos de colaboración, handoffs y separación entre resultados propuestos y revisión humana.

**Aceptación:** contrato común de adaptadores y capacidades, configuración explícita del proveedor, procedencia del resultado y evaluación por tarea. Cambiar modelo exige comprobar regresiones y límites; una marca no define el producto. Comparar calidad, latencia y consumo con métricas de ejecuciones autorizadas. La coordinación distingue instrucción publicada, recepción confirmada y trabajo entregado.

## Secuencia de ejecución

1. **Fase 1 — esta entrega:** alcance internacional, instrucciones comunes, hoja de ruta y clasificación de referencias locales como perfiles o antecedentes.
2. **Fase 2 — controles de contexto implementados:** esquema, resolución y controles opcionales de contexto; núcleo accesible sin país o centro elegidos y pruebas sintéticas de dos contextos independientes. El selector conserva los módulos clínicos comunes.
3. **Fase 3 — propuesta:** paquetes paralelos de idiomas, entornos, documentación, educación, imagen y adaptadores de IA, cada uno con aceptación propia.
4. **Fase 4 — pendiente:** evaluación multicentro y liberaciones con alcance declarado por capacidad, población y entorno.

**Ampliación INT-02A:** la fase documental incluye ahora la política de coherencia internacional y diferencias justificadas. Su siguiente trabajo es registrar la selección canónica y comprobar diferencias materiales módulo × jurisdicción; la fase 2 ya incorpora los controles opcionales de contexto. Las excepciones clínicas requieren su propia evidencia y decisión médica.

La amplitud del producto no elimina los controles clínicos. Se mantienen `CLINICALLY_PENDING`, trazabilidad y bloqueos aplicables hasta que cada criterio correspondiente esté acreditado.

## Base interna consultada

- [Estado actual](../clinical/CURRENT_STATE.md), [módulos](../clinical/MODULES.md), [validación](../clinical/VALIDATION.md) e [índice canónico](../clinical/references/module-index.md).
- [Configuración de idiomas](../app/src/i18n/index.ts) y [preferencias de interfaz](../app/src/pages/Settings.tsx).

Revisión documental y de código estático; esta hoja de ruta no registra nuevas ejecuciones de QA ni nuevas aprobaciones clínicas.
