# C12 · configuración de protección preparada, pendiente de acceso

**Documento histórico.** El ruleset activo `27994721` y sus diferencias se registran en el [cotejo R45](R45_CODEX_C12.md). El comando histórico de creación no corresponde a la regla existente.

Fecha: 22/11/2026. Repositorio: `JuanCopado/Emergency`.

La inspección de GitHub devuelve `protected: false` para `main` y `codex/v144-international-scope-20261116`, comprobaciones requeridas desactivadas y una lista vacía de rulesets. Las instrucciones de no modificar `main`, RC1 y la línea v1.43 siguen vigentes; no constituyen una regla automática del servidor.

La conexión disponible permite publicar código y PR, pero no escribir la configuración administrativa. El CLI no tiene sesión propia. El navegador conectado no estaba disponible y el navegador remoto mostraba GitHub sin sesión al abrir la configuración. No se ha activado ninguna regla y C12 no está OK.

## Configuración concreta para la rama de integración

En un ruleset de ramas activo, aplicar exactamente a `codex/v144-international-scope-20261116`:

| Control | Valor propuesto |
|---|---|
| Require a pull request before merging | Activado |
| Restrict deletions | Activado |
| Block force pushes | Activado |
| Require status checks to pass | Activado, comprobaciones de la tabla inferior |
| Require branches to be up to date | Activado |
| Bypass | Ninguna excepción automática para la integración habitual |

No se exige una nueva firma clínica ni se cambia la autoridad de aceptación del propietario. La protección del código no promueve estados de evidencia ni autoriza un despliegue.

Los siguientes nombres se observaron en el workflow sin filtros de rutas `Security and quality`, run `44950787399`, sobre la base auditada. Seleccionar como origen la aplicación GitHub Actions mostrada por GitHub:

- `semgrep`
- `trivy`
- `real-test-coverage`
- `Native local review with measured Python coverage / t05 native (windows-latest)`
- `Native local review with measured Python coverage / t06 native (ubuntu-24.04)`
- `sonarqube`

El productor `real-test-coverage` ejecuta la QA Python y las pruebas de interfaz; los jobs nativos comprueban T05 y T06 en sus sistemas correspondientes. `Clinical QA` y `App UI QA` adicionales conservan filtros de rutas. No añadir sus nombres `qa`/`ui` como requisitos incondicionales sin ajustar primero esos disparadores: un workflow omitido por rutas puede quedar pendiente y bloquear una entrega documental. En este lote concreto se ejecutarán y verificarán también esos dos workflows porque se modifican las áreas correspondientes.

## Rama reservada main

Preparar un ruleset separado para `main`, con restricción de actualizaciones, borrado y force push. Mantenerla reservada conforme a AGENTS/CODEX; no copiar a esa rama el producto en construcción ni aplicar nombres de comprobaciones de la rama internacional como si describieran su CI histórica. La reserva de RC1 y v1.43 debe conservar sus refs y SHA originales.

## Criterio de cierre

Solo cerrar C12 después de leer de nuevo el ruleset remoto, confirmar que está activo y que apunta a las ramas exactas, y verificar que GitHub exige las comprobaciones de integración. Guardar los IDs de reglas y la lectura posterior. No hacer un force push ni un borrado de prueba.

Documentación primaria: [reglas disponibles](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets), [nombres de comprobaciones de workflows reutilizables](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/troubleshooting-rules), [comprobaciones omitidas por filtros](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks).
