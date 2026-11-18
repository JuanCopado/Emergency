# SonarQube PR #24 — finding de seguridad, 18/11/2026

Consulta autenticada de metadatos con token cifrado de Actions, restringido al proyecto; no se extrajo código clínico ni datos de pacientes.

- PR auditada: https://github.com/JuanCopado/Emergency/pull/24
- Resultado inicial (commit b86ba5e0a116ee0abc6c94d4de680dc007e86d9e): Quality Gate FAIL, nueva calificación de seguridad C.
- API issues/search con organization=juancopado: 1 incidencia de tipo VULNERABILITY, regla pythonsecurity:S5144, archivo clinical/scripts/evidence_surveillance.py línea 72, mensaje "Server-Side Request Forgery via file content in evidence_surveillance.fetch()". No se marcaron hallazgos falsos ni aceptados automáticamente.
- Remediación candidata posterior: ce808a63f3f68c8750fd48c425d4d95bbe3f4de3. Destinos de red derivados exclusivamente de URLs literales asociadas a identificadores de fuente. Verificación de la nueva revisión todavía pendiente en el momento de este registro.
- No modificar las condiciones de SonarQube. CLINICALLY_PENDING permanece.

La acción temporal de consulta se elimina en este commit; los secretos nunca estuvieron en código ni en logs publicados.
