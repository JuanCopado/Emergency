# Emergency · checklist de problemas actuales · 22/11/2026

## Encargo y base

El propietario pidió auditar primero y corregir después los problemas actuales, sin completar ni dar por resueltos los procesos que siguen en construcción. El informe de auditoría se entregó antes de iniciar este lote.

Repositorio: `JuanCopado/Emergency`. Base inspeccionada: `0e68e5ee654e7be452cbb7cb5e5fb22b8b1127ed`, árbol `81a5cc74e41aa70deb6a9a70211fd8ce70c32cb7`, rama `codex/v144-international-scope-20261116`. Rama de correcciones: `codex/current-defects-20261122`.

**OK** exige corrección integrada y comprobación observada; una propuesta, un commit local o un PR abierto no cierran el punto. **EN CURSO** identifica trabajo aún no verificado/integrado. **PENDIENTE DE ACCESO** identifica una acción concreta que la conexión disponible no permite realizar. La prioridad expresa impacto técnico, no validación clínica.

## Lista de resolución

| ID | Prioridad | Problema actual | Criterio de cierre | Estado |
|---|---|---|---|---|
| C01 | P1 | API general sin frontera Host/Origin y credencial de proceso equivalente a la API de gasometría; exposición de red sin identidad | Acceso local autorizado funciona; peticiones ajenas, credencial ausente/errónea y exposición de red no autenticada se rechazan | OK |
| C02 | P1 | Documentos de texto se recortan silenciosamente a 120.000 caracteres | Rechazo explícito y localizable antes de procesar; documento en el límite conserva todo su texto | OK |
| C03 | P1 | Detección de correo con coste cuadrático en texto adverso | Recorrido de coste acotado con equivalencia de detección y comprobación de entradas largas | OK |
| C04 | P1 | Etiquetas identificativas reconocidas en idiomas incompletos | Casos ES/PT/EN/ZH y etiquetas observadas detienen el flujo cuando corresponde; controles negativos preservados | OK |
| C05 | P2 | Aviso local de privacidad comunica una garantía mayor que el detector real | Mensaje describe alcance limitado y revisión humana necesaria; localizado en cuatro idiomas | OK |
| C06 | P1 | Se pierde el borrador de nota al visitar gasometría y volver | Borrador en memoria por episodio, descarte explícito y respuestas antiguas aisladas; sin persistencia clínica en localStorage | OK |
| C07 | P2 | Inicio etiqueta como futuras familias de guías ya disponibles | Disponibilidad y recuentos proceden del catálogo actual; acceso a guías sin prometer herramientas futuras | OK |
| C08 | P2 | Controles existentes de escalas/importación permanecen en español con otros idiomas seleccionados | Controles localizados ES/PT/EN/ZH; texto clínico canónico identificado y preservado | OK |
| C09 | P2 | Versión de catálogo adulto presentada como identidad de toda la aplicación | Identidad de aplicación/compilación separada de la versión del catálogo; sin inventar un SHA | OK |
| C10 | P2 | Documentación vigente contradice funciones y aceptaciones ya existentes | Selector contextual, contratos aceptados, QA de impresión y reserva de ramas descritos con su alcance real; históricos preservados | OK |
| C11 | P2 | PROC-SP-003 anuncia reimplantación aunque la ficha fuente describe conservación del segmento | Índices y derivados usan el título de la ficha fuente; cuerpo, estados y evidencia conservados | OK |
| C12 | P1 | GitHub no exige comprobaciones ni protege automáticamente las ramas inspeccionadas | Protección remota activa, exigencia de comprobaciones aplicables y verificación posterior por API | PENDIENTE DE ACCESO |
| C13 | P1 | Una aceptación MCDT tardía puede marcar como aceptado un informe editado o rechazado mientras esperaba | Respuestas de aceptación vinculadas a la revisión enviada; un cambio posterior conserva el estado actual y permite reintento sin instalar datos antiguos | OK |

## Límite de C12

La API de lectura devuelve `protected: false`, comprobaciones requeridas desactivadas y lista de rulesets vacía para el corte auditado. La conexión GitHub permite trabajo de código, pero no escritura administrativa de protección de ramas. El CLI no tiene una sesión autenticada. El navegador conectado no estaba disponible y el navegador remoto muestra GitHub sin sesión al abrir la configuración. No se ha modificado la protección. La reserva de `main`, RC1 y v1.43 mediante instrucciones continúa vigente.

La [configuración concreta y el criterio de cierre](BRANCH_PROTECTION_PENDING_20261122.md) quedan preparados, con los nombres reales de los seis jobs de seguridad/calidad y el tratamiento de los workflows filtrados por rutas. Preparar ese documento no activa las reglas.

## Fuera de este lote

Permanecen en sus expedientes: decisiones clínicas M10/R7/R8, validación diagnóstica/prospectiva de nota e imagen, G05 y despliegue multiusuario, T05/T06 en otros sistemas/proveedores, ampliación estructurada de procedimientos, traducción clínica integral, revisión literal completa de Narrador, actualización bibliográfica y restauración operativa. Su estado no se contabiliza como fallo corregido ni se cambia por este lote técnico.

Se conservan los 131 módulos, 129 GREEN / 2 YELLOW / 0 RED, las aceptaciones del propietario, los 46 IDs de contratos y el alcance aceptado de los 19 antes bloqueados. El estado global sigue siendo **CLINICALLY_PENDING**. No se modifican fórmulas, dosis, umbrales diagnósticos, contenido clínico de las fichas, fechas de evidencia ni reglas de decisión médica.

## Evidencia de entrega

**Doce puntos OK y C12 pendiente de acceso.** [PR70](https://github.com/JuanCopado/Emergency/pull/70) integrada en `e8de202d874c6db588d3561ff13859e5ee53c96d` sobre la rama internacional. El árbol `4f3331e48474816d4487635bae2c05d24849acee` coincide exactamente con el head comprobado `e6a4e00cfd89d1aa7a625f9ef3d3ed9efe0ac1a1`. Los seis workflows de push y PR finalizaron SUCCESS antes de integrar. El [recibo de integración](PR70_INTEGRACION_20261122.md) conserva las pruebas, el alcance, las incidencias iniciales y la verificación remota. Esta entrega no acredita una instalación en un equipo asistencial.

### C10/C11 · comprobaciones locales

- `python3 -m unittest clinical.tests.test_procedure_migration_v142 clinical.tests.test_procedure_schema_v141 clinical.tests.test_procedures_v141`: **19/19 PASS**.
- `npm test -- src/test/procedure-catalog.test.ts src/test/reference-context.test.tsx src/context/reference-context.test.ts`: **23/23 PASS**, tres archivos.
- Catálogo regenerado: **196 procedimientos, cuatro alias, 16 familias**. El único campo cambiado en el JSON de PROC-SP-003 es `name`; la ficha fuente completa, el registro de evidencia y la aceptación de contratos permanecen idénticos byte a byte a la base.
- La concordancia transversal deja de permitir la antigua diferencia de título de PROC-SP-003. El informe de migración se genera desde el estado actual; los informes de auditoría históricos y sus huellas permanecen intactos.

### Revisión cruzada y composición

La revisión independiente de la frontera HTTP no encontró una elusión concreta en el circuito navegador → Vite → Python ni consumidores actuales incompatibles. Se mantiene el límite de autenticación entre procesos locales; no identifica al médico.

La revisión de privacidad detectó una regresión introducida al ampliar etiquetas: ciertos separadores con espacio no separable o salto de línea dejaban de reconocerse. Se reprodujo y corrigió antes de publicar, con regresiones RED → GREEN en servidor e interfaz, preservando la forma previa de espacios. Esta corrección forma parte de C04.

C13 se identificó durante la revisión cruzada del borrador y ya existía en la base auditada. Es un problema de integridad de una función actual, por lo que se incorpora a este lote. No modifica el contenido médico del informe ni completa un proceso futuro.

La primera comprobación conjunta de los cambios de backend y nomenclatura superó **140/140 pruebas**. Las comprobaciones definitivas del lote compuesto y sus resultados remotos se registrarán al completar la entrega.

La composición de interfaz previa al delta C13 superó **927/927 pruebas en 44 archivos**, lint, TypeScript y build de distribución. El build conserva el aviso de tamaño de chunks superior a 500 kB. C13 añadió cuatro casos focales; sus comprobaciones posteriores y la CI del commit definitivo se registran aparte para no atribuirles una ejecución anterior.

Al componer se preservaron ambos lados de los dos conflictos esperados: aviso de privacidad + ID/estado de borrador en `ClinicalNote.tsx`, y frontera HTTP + identidad de código en `vite.config.ts`. Dos harnesses existentes de navegador se adaptaron al nombre accesible localizado de la región de resultados de escalas; se conservan sus aserciones clínicas y negativas.

Expedientes: [HTTP y launcher](../../clinical/qa/HTTP_LOCAL_BOUNDARY_20261122.md), [privacidad/documentos](../../clinical/qa/CURRENT_PRIVACY_DOCUMENTS_20261122.md), [interfaz y C13](../../clinical/qa/CURRENT_UI_DEFECTS_2026-11-22.md).

Composición final con C13 y los espacios de documentos: **58/58 Vitest** en aceptación MCDT, navegación de nota, privacidad y frontera Vite/Python; **12/12 Python** de privacidad/importación. Comparación con la base: sin cambios en `clinical/calculators`, `clinical/references` ni `app/src/data/drugs.json`; los únicos módulos modificados son las dos etiquetas de los índices de procedimientos. Los cuerpos clínicos y las aceptaciones permanecen intactos.

### Primer ciclo remoto y ajuste del cliente de pruebas

Los primeros runs de Clinical QA de PR70 (`44991697629` y `44991732296`, head `bdb0dfc2`) ejecutaron 1.202 pruebas con 14 omitidas y fallaron en 67 subcasos de cinco métodos de `test_patient_weight_http.py`. Su helper aún enviaba peticiones sin Origin ni credencial, por lo que la nueva frontera las rechazaba antes de probar la validación numérica. Se corrigió únicamente ese cliente de prueba reutilizando `request_metadata(server)`. Se mantienen todas sus entradas, expectativas 200/422, comprobaciones de JSON exacto, cálculo y exportación. La ejecución focal posterior supera **6/6 métodos**. El siguiente ciclo remoto verifica el commit actualizado; el fallo inicial no se presenta como PASS.

### Segundo ciclo remoto y control de calidad

En `c5d329bcf120da705d877c7b9ac8532b03416888`, Clinical QA pasa en push (`44992153086`) y PR (`44992157865`): 1.202 pruebas contabilizadas, 14 omitidas, 1.188 ejecutadas sin fallos. App UI QA (`44992157844`) pasa 931 pruebas en 45 archivos y sus recorridos Chromium: 13 formularios de escalas, ocho enlaces de reanimación, 21 casos agudos, cuatro PDF reales y cinco escenarios pediátricos.

Security and quality (`44992153182` y `44992157837`) supera Trivy, Semgrep, cobertura medida y T05/T06 nativos, pero Sonar bloquea el PR por cobertura nueva del 77,0 % frente al 80 % requerido y calificación de seguridad B frente a A. La anotación de seguridad señala la construcción de orígenes HTTP mediante una variable que solo puede contener loopback. Las otras anotaciones requieren revisar la lista de direcciones locales y la búsqueda de Git en PATH. La lectura de la cobertura muestra que los recorridos Vite cargan una copia del middleware distinta de la importada por el instrumento de cobertura. El siguiente delta explicita los orígenes locales, comprueba configuraciones rechazadas y ejercita funcionalmente el plugin importado con peticiones reales; conserva los siete recorridos anteriores. La identidad de compilación se revisa con pruebas de repositorios reales y selección de ejecutable independiente de PATH. No se alteran umbrales, exclusiones ni resultados para eludir el gate. Este ciclo permanece registrado como fallido hasta observar el siguiente resultado.

La conciliación final de C10 incluye la frase vigente de `docs/INTERNATIONAL_SCOPE.md` sobre el selector ya existente y precisa los comandos por plataforma y el motor local de perfusiones en `app/README.md`.

El delta local compuesto de cierre supera **26/26 Vitest en cuatro archivos**, los nueve métodos Python de frontera y los seis de integridad numérica HTTP, lint, TypeScript y build. La ejecución de los seis métodos HTTP utiliza el modo discovery esperado por sus imports de pruebas; una invocación conjunta anterior sin esa ruta de importación falló al cargar el módulo y no se contabiliza como prueba aprobada. La medición focal acredita las 34 líneas y nueve funciones del middleware, con 43/45 ramas; no se atribuye ese porcentaje al proyecto completo. La identidad de compilación usa Git nativo desde rutas absolutas fijas, entorno aislado y fsmonitor desactivado; doce casos con repositorios reales conservan SHA/dirty/unknown y verifican las redirecciones rechazadas. El import de ese helper y la frontera HTTP se conservaron juntos al resolver el conflicto de Vite. El siguiente head remoto debe superar el gate completo antes de integrar.

Detalle de análisis de la frontera local y del hotspot de IP: [revisión Sonar de HTTP](../../clinical/qa/HTTP_LOCAL_BOUNDARY_SONAR_20261122.md). La dirección IPv4-mapped de loopback permanece literal en la lista de conexiones admitidas; no se ha ocultado ni cerrado administrativamente el hotspot para conseguir un PASS.

### Cierre observado

Clinical QA del head definitivo: **1.205 pruebas contabilizadas, 14 omitidas y 1.191 ejecutadas sin fallo**; App UI QA: **947/947 en 47 archivos**, con 13 formularios de escalas, ocho enlaces de reanimación, 21 casos agudos, cuatro PDF y cinco escenarios pediátricos. Los seis jobs de seguridad/calidad aprobaron en push y PR. Sonar del PR: **88,7 % de cobertura nueva, gate PASS**; rama: **84,1 %, gate PASS**. Son ámbitos de comparación distintos. Se conserva la anotación S1313 de loopback y la incidencia interna Protobuf/UTF-8 con sus límites, sin waivers ni cambios de umbral. El estado OK acredita estos defectos técnicos integrados, no una liberación clínica.
