# Emergency — cobertura real para SonarQube (17/11/2026)

Alcance: instrumentación técnica sobre la rama `codex/security-sonar-coverage-20261117`, sin cambios a módulos clínicos, dosis, fórmulas, estados de evidencia, main ni ramas protegidas.

## Propósito
La ejecución de SonarQube informaba cobertura 0% por ausencia de LCOV/Cobertura. Se mide cobertura de frontend con Vitest 4.1.12 + V8 4.1.12, y Python con coverage.py 7.17.3. No se simulan porcentajes, no se rebaja el quality gate de 80% en código nuevo y no se excluye código para alterar métricas.

## Ejecución y privacidad
- Los informes se generan antes del escáner en el mismo job de GitHub Actions.
- JS/TS: ejecutar 13 suites y exportar `app/coverage/lcov.info`, incluyendo módulos `app/src` y `app/scripts`. Se excluyen solo pruebas/fixtures de test del cómputo de producción.
- Python: ejecutar suites `clinical/tests` y `security/tests` con instrumentación real para las rutas de scripts, y exportar `coverage/python.xml`.
- Las rutas de LCOV se convierten a rutas relativas a la raíz del repositorio sin cambiar recuentos de líneas.
- Los pasos terminan en fallo si no se obtiene cobertura válida; no se utiliza `continue-on-error`.
- No se publican informes crudos de seguridad ni secretos. Las suites emplean datos sintéticos.
- Se mantiene la configuración previa de acceso restringido al token Sonar y el Quality Gate exigente.

## Verificación requerida
Documentar el resultado de Clinical QA, App UI QA, Semgrep, Trivy y SonarQube en el SHA final. Si Sonar no supera su gate, conservarlo como FAIL, identificar la condición concreta y añadir tests o corregir hallazgos sin suprimirlos.

Estado: `CLINICALLY_PENDING`.
