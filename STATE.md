# STATE · cobertura y cierre de referencias · 20/11/2026

Estado global: **CLINICALLY_PENDING**. Registro: **120 GREEN / 11 YELLOW / 0 RED**, 131 módulos.
Validador clínico final: Dr. Juan Copado Ceballos; Farmacia consultiva, según PR35.

- PR49 integrada en `f45b628`: Sonar PASS inicial, reintento exclusivo y rama. Recibo: `security/SONAR_COVERAGE_RETRY_2026-11-20.md`.
- T05/T06 integrados mediante PR33; correcciones previas Sonar en PR34. Alcance: `clinical/qa/T05_T06_INTEGRATION_20261119.md`.
- PR48: accesibilidad y prototipo multimodal sintético E1; sin inferencia ciega ni validación diagnóstica.
- Gate de referencia revisado íntegramente y GREEN con la aceptación PR35 ya existente; no es autorización asistencial.
- Nota: corregidas fuentes de 18 síndromes y una referencia vasoactiva; 60 casos sin cambios fuera de procedencia.
- Nota: siguen pendientes rendimiento clínico y límites del razonamiento descritos en `clinical/qa/NOTE_PROVENANCE_CLOSURE_20261120.md`.
- Nueve fichas completas de referencia de imagen listas para decisión explícita, todas v1; no se han promovido.
- POCUS-MODE v1: aclaración de B-mode/M-mode en parche inactivo, con proyección comprobada; incluida en POCUS-REF v1.
- Decisiones y cierre: `clinical/qa/CLINICAL_CLOSURE_DECISIONS_20261120.md`; los padres de imagen y nota siguen YELLOW.
- ECG-PT v1 ya aceptado e integrado en PR47; cuatro flujos posteriores al merge PASS. Cola técnica conciliada.
- T05: revisión visual y trazabilidad FiO₂; extracción protegida solo Windows, bloqueo explícito en Linux.
- T06: R6/B1/Q4 TLS sintético local solo Linux/POSIX; sin cierre G05, proveedores públicos, consultas libres ni RAG.
- Aplicación/launcher comunes; procesos y límites separados. Uso: `docs/LOCAL_REVIEW.md`.
- JSON estricto, protección no nulo→cero y fronteras HTTP/Host/Origin conservadas.
- SCORE-REF-20261120: 13 formularios aceptados, entrada manual o importación revisada y cálculo a petición médica.
- ARR-SELECTOR-20261120: cuatro circuitos manuales aceptados; ocho recorridos Chromium verificados en dos vistas.
- T02: once anotaciones aceptadas; escalas/fórmulas/PDF en PR41/44. Se conservan sus alcances y decisiones.
- Preservar los 19 contratos agudos aceptados y sus 46 IDs; no restablecer bloqueos históricos ni repetir aceptación.
- `main`, RC1 y v1.43 protegidos. Sin GO_RELEASE ni exactitud prospectiva inferida de pruebas técnicas.
