# Conciliación focal PR138 y PR139

28/11/2026 · IMPLEMENTACIÓN v0.7 · mismos doce IDs. Preparación aislada; no fusión de PR ni despliegue.

## Identidades y alcance

- Base auditada y distribuida: PR137 `9c64cf1ece251a24f2c2bb8cf7982822991f8403`, distribución D y kit firmados. Sus pruebas de instalación, actualización, rollback y auditoría se reutilizan exclusivamente en ese alcance.
- PR138 `28aff2f6f56ab26373bea0fd2eb0f39196ffc215`: una línea del lock MCP limita pywin32 a win32. Los 496 hashes permanecen idénticos. CI fuente observada: nueve controles SUCCESS; el job MCP Windows instala el lock con hashes y verifica stdio. El recibo de instalación Linux indicado en el cuerpo de la PR no se presenta aquí como observado directamente.
- PR139 `49a417bad01a35aa46ce909d3c948d0093c8554e`: espacio local de texto, propuesta por encabezados y copia editable. Su base internacional es anterior a PR137. En la copia de revisión se conservaron ambas entradas de STATE.md al resolver el único conflicto; Layout se concilió sin conflicto textual. No se modificaron las ramas fuente.

## Defectos confirmados y corrección acotada

1. P1: la comparación por subcadena podía omitir «asma» porque el campo ya contenía «Sin asma», o «4 horas» dentro de «24 horas». Ahora sólo un bloque de líneas completas consecutivas idénticas cuenta como presente; las regresiones preservan negaciones, cifras e idempotencia.
2. P2: «Aplicar» estaba junto al documento final editable aunque aplicaba la propuesta anterior. La acción pasa a la tarjeta de propuesta, con nombre explícito. La copia libre sólo se copia; las cuatro traducciones explican que PDF/Word utilizan los campos de la nota y no sus ediciones. No se ha añadido un exportador de texto libre.
3. P2: el indicador aplicado persistía al editar la sección. Se invalida cuando cambia su cuerpo, destino o inclusión.

Verificación focal recibida: 21/21 pruebas de los dos archivos afectados, TypeScript y ESLint focal favorables. Auditoría original y fallos de prueba metodológicos se conservan fuera de Git. Revisión independiente posterior y recorrido/exportación del nuevo flujo se registran por identidad en los recibos de coordinación; no se anticipa su dictamen ni CI en este documento.

## Control pendiente que se ejecuta

El workflow MCP existente pasa a comprobar Windows y Ubuntu con Python 3.12 y el mismo lock `--require-hashes --only-binary=:all:`; los artefactos se identifican por sistema operativo. Cubre la ausencia de instalación Linux en la CI previa. No cambia exclusiones, umbrales ni reglas de Sonar, Semgrep o Trivy. La CI final del nuevo SHA se recoge externamente, sin trasladar el PASS de las PR fuente a otra composición.

No se repiten firma, instalación, PWA instalada ni rollback de D. El código conciliado no se declara incluido en el paquete D existente; si se selecciona posteriormente para distribuirlo, requerirá sus propios bytes y aceptación aplicable. No se empaqueta ahora otro instalador.

## Límites de producto y ciencia

Sin cambios en motores, dosis, fórmulas, fuentes clínicas, decisiones aprobadas o last_checked. El espacio nuevo no interpreta ni genera diagnósticos, no almacena su contenido en navegador/servidor y no habilita IA operativa. Las secciones sin campo de destino se señalan y permanecen en la copia libre; no se promete exportarlas mediante la nota canónica. La revisión visual focal no acredita WCAG completa ni validación clínica.

Se conservan 15/18 lecturas documentales y cero lecturas íntegras nuevas: ACEP/AAD siguen sujetos al flujo autorizado y la tabla IFEM conserva 25 símbolos pendientes. Dos módulos YELLOW, corpus independiente, adjudicación humana, privacidad por activo y preparaciones originales no identificadas mantienen sus límites documentados. No se repiten aprobaciones ni se crea una pregunta médica sin evidencia madura.

PR137 sigue siendo el candidato técnico distribuido y auditado; la incorporación de estos deltas y cualquier fusión protegida requieren autorización aplicable y controles exactos favorables. Portada, nuevas fases visuales e interoperabilidad institucional no se activan por esta conciliación.

**CLINICALLY_PENDING · NOT_FROZEN_NOT_VALIDATED · NO_GO_CLINICAL_RELEASE.**
