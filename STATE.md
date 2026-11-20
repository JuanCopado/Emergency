# STATE · continuidad T05/T06 y evidencia · 20/11/2026

Estado global: **CLINICALLY_PENDING**. Registro: 119 GREEN / 12 YELLOW / 0 RED.

- Candidato técnico posterior a PR46: accesibilidad del cálculo y catálogo, más prototipo multimodal aislado. Alcance y procedencia en `docs/coordination/EMERGENCY_V144_CLOSE_20261120.md`.
Validador clínico final: Dr. Juan Copado Ceballos; Farmacia consultiva, conforme a PR35.

20/11/2026 · SCORE-REF-20261120. El Dr. Juan Copado Ceballos aprueba el módulo 12 en los 13 formularios con entrada manual o importación revisada. Registro: 119 GREEN, 12 YELLOW. Estado global CLINICALLY_PENDING.


- T05/T06 integrados en la rama internacional mediante PR33; cinco incidencias Sonar cerradas en PR34.
- Corte técnico comprobado: `cdca8e34013bba891a1c49f5ea859f933fcbea63`; Clinical QA, App UI QA y Security PASS; Sonar 0 nuevas / 0 aceptadas.
- Cierre y evidencias por commit: `clinical/qa/T05_T06_INTEGRATION_20261119.md`.
- Seguimiento de los ocho registros vencidos: `clinical/qa/EVIDENCE_FOLLOWUP_20261120.md`; contraste focal, sin renovar `last_checked` ni promover estados.
- ECG-PT-20261120 v1: errata confirmada y parche de dos consumidores preparado; respuesta médica pendiente, corrección clínica todavía no activada.
- Gobernanza del registro reconciliada con PR35; cola dinámica, sin cifra histórica fija ni segunda firma farmacéutica obligatoria.
- T05: revisión visual y trazabilidad de FiO₂; extracción protegida solo Windows, bloqueo explícito en Linux.
- T06: R6/B1/Q4 TLS sintético local solo Linux/POSIX; sin proveedores públicos, consultas libres, RAG ni cierre G05.
- Aplicación y launcher comunes; procesos y límites de plataforma separados. Uso: `docs/LOCAL_REVIEW.md`.
- JSON estricto, protección no nulo→cero y fronteras HTTP/Host/Origin conservadas.
- ARR-SELECTOR-20261120: cuatro circuitos manuales aceptados, ocho navegaciones Chromium verificadas en dos vistas.
- T02: once anotaciones documentales aceptadas; `clinical/qa/T02_DECISION_MEDICA_20261120.md`.
- Escalas, fórmulas y entrada de PDF/analítica: entregas PR41/44, con alcance en `clinical/qa/CALCULATOR_DECISION_20261120.md`.
- Preservar los 19 contratos agudos aceptados y sus 46 IDs; no reiterar la aceptación ni restablecer bloqueos históricos.
- `main`, RC1 y v1.43 protegidos. Sin GO_RELEASE ni validación diagnóstica prospectiva por estas pruebas.
