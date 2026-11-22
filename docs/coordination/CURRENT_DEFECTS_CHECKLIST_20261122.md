# Emergency · checklist de problemas actuales · 22/11/2026

## Encargo y base

El propietario pidió auditar primero y corregir después los problemas actuales, sin completar ni dar por resueltos los procesos que siguen en construcción. El informe de auditoría se entregó antes de iniciar este lote.

Repositorio: `JuanCopado/Emergency`. Base inspeccionada: `0e68e5ee654e7be452cbb7cb5e5fb22b8b1127ed`, árbol `81a5cc74e41aa70deb6a9a70211fd8ce70c32cb7`, rama `codex/v144-international-scope-20261116`. Rama de correcciones: `codex/current-defects-20261122`.

**OK** exige corrección integrada y comprobación observada; una propuesta, un commit local o un PR abierto no cierran el punto. **EN CURSO** identifica trabajo aún no verificado/integrado. **PENDIENTE DE ACCESO** identifica una acción concreta que la conexión disponible no permite realizar. La prioridad expresa impacto técnico, no validación clínica.

## Lista de resolución

| ID | Prioridad | Problema actual | Criterio de cierre | Estado |
|---|---|---|---|---|
| C01 | P1 | API general sin frontera Host/Origin y credencial de proceso equivalente a la API de gasometría; exposición de red sin identidad | Acceso local autorizado funciona; peticiones ajenas, credencial ausente/errónea y exposición de red no autenticada se rechazan | EN CURSO |
| C02 | P1 | Documentos de texto se recortan silenciosamente a 120.000 caracteres | Rechazo explícito y localizable antes de procesar; documento en el límite conserva todo su texto | EN CURSO |
| C03 | P1 | Detección de correo con coste cuadrático en texto adverso | Recorrido de coste acotado con equivalencia de detección y comprobación de entradas largas | EN CURSO |
| C04 | P1 | Etiquetas identificativas reconocidas en idiomas incompletos | Casos ES/PT/EN/ZH y etiquetas observadas detienen el flujo cuando corresponde; controles negativos preservados | EN CURSO |
| C05 | P2 | Aviso local de privacidad comunica una garantía mayor que el detector real | Mensaje describe alcance limitado y revisión humana necesaria; localizado en cuatro idiomas | EN CURSO |
| C06 | P1 | Se pierde el borrador de nota al visitar gasometría y volver | Borrador en memoria por episodio, descarte explícito y respuestas antiguas aisladas; sin persistencia clínica en localStorage | EN CURSO |
| C07 | P2 | Inicio etiqueta como futuras familias de guías ya disponibles | Disponibilidad y recuentos proceden del catálogo actual; acceso a guías sin prometer herramientas futuras | EN CURSO |
| C08 | P2 | Controles existentes de escalas/importación permanecen en español con otros idiomas seleccionados | Controles localizados ES/PT/EN/ZH; texto clínico canónico identificado y preservado | EN CURSO |
| C09 | P2 | Versión de catálogo adulto presentada como identidad de toda la aplicación | Identidad de aplicación/compilación separada de la versión del catálogo; sin inventar un SHA | EN CURSO |
| C10 | P2 | Documentación vigente contradice funciones y aceptaciones ya existentes | Selector contextual, contratos aceptados, QA de impresión y reserva de ramas descritos con su alcance real; históricos preservados | EN CURSO |
| C11 | P2 | PROC-SP-003 anuncia reimplantación aunque la ficha fuente describe conservación del segmento | Índices y derivados usan el título de la ficha fuente; cuerpo, estados y evidencia conservados | EN CURSO |
| C12 | P1 | GitHub no exige comprobaciones ni protege automáticamente las ramas inspeccionadas | Protección remota activa, exigencia de comprobaciones aplicables y verificación posterior por API | PENDIENTE DE ACCESO |
| C13 | P1 | Una aceptación MCDT tardía puede marcar como aceptado un informe editado o rechazado mientras esperaba | Respuestas de aceptación vinculadas a la revisión enviada; un cambio posterior conserva el estado actual y permite reintento sin instalar datos antiguos | EN CURSO |

## Límite de C12

La API de lectura devuelve `protected: false`, comprobaciones requeridas desactivadas y lista de rulesets vacía para el corte auditado. La conexión GitHub permite trabajo de código, pero no escritura administrativa de protección de ramas. El CLI no tiene una sesión autenticada. El navegador conectado no estaba disponible y el navegador remoto muestra GitHub sin sesión al abrir la configuración. No se ha modificado la protección. La reserva de `main`, RC1 y v1.43 mediante instrucciones continúa vigente.

La [configuración concreta y el criterio de cierre](BRANCH_PROTECTION_PENDING_20261122.md) quedan preparados, con los nombres reales de los seis jobs de seguridad/calidad y el tratamiento de los workflows filtrados por rutas. Preparar ese documento no activa las reglas.

## Fuera de este lote

Permanecen en sus expedientes: decisiones clínicas M10/R7/R8, validación diagnóstica/prospectiva de nota e imagen, G05 y despliegue multiusuario, T05/T06 en otros sistemas/proveedores, ampliación estructurada de procedimientos, traducción clínica integral, revisión literal completa de Narrador, actualización bibliográfica y restauración operativa. Su estado no se contabiliza como fallo corregido ni se cambia por este lote técnico.

Se conservan los 131 módulos, 129 GREEN / 2 YELLOW / 0 RED, las aceptaciones del propietario, los 46 IDs de contratos y el alcance aceptado de los 19 antes bloqueados. El estado global sigue siendo **CLINICALLY_PENDING**. No se modifican fórmulas, dosis, umbrales diagnósticos, contenido clínico de las fichas, fechas de evidencia ni reglas de decisión médica.

## Evidencia de entrega

Las comprobaciones de cada bloque y los SHA de integración se añadirán al cerrar el lote. Este documento todavía no acredita una corrección integrada ni una instalación en un equipo asistencial.

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
