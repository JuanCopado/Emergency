# EMERGENCY — Diagnóstico SonarQube tras cobertura real

Fecha: 2026-11-17. Inspección autenticada de solo lectura por GitHub Actions; token restringido a `JuanCopado_Emergency` (nunca impreso).

## Alcance verificado
Candidato inspeccionado: `codex/security-sonar-coverage-20261117` en `44f1f156f15a4511931c0ee1661537cc2d7ae1ee`.

Ejecuciones:
- [Seguridad y SonarQube](https://github.com/JuanCopado/Emergency/actions/runs/44058069846): Semgrep PASS, Trivy PASS, SonarQube Quality Gate FAIL.
- [Clinical QA](https://github.com/JuanCopado/Emergency/actions/runs/44058069909): PASS técnico.
- [Auditoría API de condiciones](https://github.com/JuanCopado/Emergency/actions/runs/44059017166).
- [Auditoría API de incidencias](https://github.com/JuanCopado/Emergency/actions/runs/44059503740).

## Cobertura observada
- Python, ejecución con coverage.py 7.17.3: 76,2% de líneas, 122 clases de código.
- Frontend, Vitest V8 4.1.12: 41,4% sentencias, 43,74% líneas, 55,23% ramas; 85 registros SF en LCOV.
- SonarQube importó Cobertura y LCOV. Avisó de 10 rutas LCOV JSON ajenas a las extensiones de fuente analizadas; no demuestra cobertura para esos archivos.
- SonarQube: cobertura global 72,1%; nueva cobertura 71,6% frente al requisito 80%. No modificar el umbral ni excluir código productivo para aumentar la cifra.

## Quality Gate (API)
- `new_reliability_rating=4` (D), requerido 1 (A): FAIL.
- `new_security_rating=5` (E), requerido 1 (A): FAIL.
- `new_coverage=71.6`, requerido >=80: FAIL.
- `new_maintainability_rating=1`: PASS.
- `new_duplicated_lines_density=0.2`, umbral 3: PASS.
- `new_security_hotspots_reviewed=100`: PASS.

## Incidencias abiertas y valoración
La API `issues/search` comunicó **96 incidencias abiertas** para la rama analizada, sin clasificar todas como fallos explotables. El diagnóstico emitió hasta 80 incidencias de fiabilidad/seguridad para revisión focal. Estas cifras no equivalen a defectos introducidos en esta tarea ni a 96 vulnerabilidades confirmadas.

Priorización por riesgo potencial, sin aceptar ni descartar incidencias automáticamente:
1. Seguridad del API clínico: la respuesta JSON de `clinical_note_api._send` tiene `Content-Type: application/json` y `nosniff`, pero Sonar señala posible XSS y las respuestas de excepción contienen `detail: str(exc)` que merece revisión de privacidad. Verificar explotación real y corregir fuga de detalles cuando proceda.
2. Exportación clínica/pediátrica: Sonar señala rutas derivadas del cuerpo HTTP. En los módulos `acute_medication_api` y `pediatric_result_exporter` el código inspeccionado usa `TemporaryDirectory` y formatos permitidos; no afirmar explotación sin trazar el flujo de datos. Revisar `clinical_note_exporter.export_json` y límites de llamadas directas.
3. `evidence_surveillance.fetch`: URL leída del catálogo y `urlopen`; `assess_source` valida HTTPS y clase de autoridad, pero no fija destinos por hostname. La verificación de redirecciones se hace tras recibir respuesta. Riesgo SSRF que requiere endurecimiento y pruebas sintéticas sin contactar redes internas.
4. Scripts de CLI y herramientas de evaluación de imágenes: múltiples advertencias de recorrido de rutas por argumentos; distinguir herramientas internas con acceso filesystem explícito frente a entradas remotas.
5. GitHub Actions: advertencias de suministro de dependencias / lifecycle scripts, separar herramientas estrictamente fijadas de paquetes transitivos sin hash completo.
6. Fiabilidad: `assert` atrapados por `AssertionError` en QA, ordenación sin comparador y expresiones condicionales redundantes. Revisión de semántica y regresiones antes de cambiar código.

## Decisiones
- Mantener Sonar FAIL hasta resolver los tres criterios, sin suppressions ni rebajar gates.
- No modificar medicamentos, dosis, algoritmos ni fuentes clínicas en esta fase documental.
- Mantener `CLINICALLY_PENDING`, sin merge a main, RC1 ni v1.43.
- Siguiente bloque recomendado: revisión focal de límites de confianza de APIs y vigilancia de evidencia, seguida de tests de cobertura para rutas de alto riesgo.
