# Laboratorio de factores humanos · Etapa 1 · estructura (sin estudio ejecutado)

**`CLINICALLY_PENDING` · `NOT_EXECUTED`.** Estructura técnica para el banco de estímulos y la captura de la Etapa 1 ([`DEC-CLIN-R19-01`](../../R20_DECISION_MEDICA_R19_01_20261123.md); [protocolo integrado](../../R20_PROTOCOLO_ETAPA1_INTEGRADO.md)). No hay participantes, estímulos reales ni datos en este directorio.

- `manifest.example.json`: **ejemplo sintético** del manifiesto versionado de escenarios (códigos opacos, sin imágenes). El manifiesto real lo prepara una persona distinta de quien implementa la interfaz, lo revisa el médico propietario y se congela con SHA-256 (`stimulus_sha256` por escenario y hash del manifiesto).
- Reglas que valida `clinical/scripts/human_factors_tools.py manifest`: escenarios sintéticos, códigos opacos sin texto libre, identidad única de escenario, bancos `set1`/`set2` disjuntos (ningún `case_code` en ambos), huellas `stimulus_sha256` únicas y bien formadas; `stimuli_frozen` solo es verdadero si todos los escenarios tienen huella.
- Flujo: `manifest` → `assign` (AB/BA equilibrado por códigos seudónimos) → captura de registros cerrados (`validate`) → `export` (JSON reproducible con huellas, validado por `clinical/references/human-factors-export.schema.json`).
- Brazos A (interfaz vigente) y B (prototipo inactivo): `npm run hf:lab-preflight` en `app/`.
- **Prohibido en este directorio:** imágenes, datos de pacientes, nombres, correos, teléfonos, identificadores personales. Una prueba escanea el directorio.
