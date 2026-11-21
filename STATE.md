# STATE · referencias de imagen aceptadas · 20/11/2026

Estado global: **CLINICALLY_PENDING**. Registro: **129 GREEN / 2 YELLOW / 0 RED**, 131 módulos.
Validador clínico final: Dr. Juan Copado Ceballos; Farmacia consultiva, según PR35.

- Cobertura Sonar cerrada: postmerge PR50 PASS en reintento 2, run 44805197675/job 136538151239, cobertura original y quality gate PASSED.
- T05/T06 integrados mediante PR33; correcciones previas Sonar en PR34. Alcance: `clinical/qa/T05_T06_INTEGRATION_20261119.md`.
- PR48: accesibilidad y prototipo multimodal sintético E1; sin inferencia ciega ni validación diagnóstica.
- Gate de referencia revisado íntegramente y GREEN con la aceptación PR35 ya existente; no es autorización asistencial.
- Nota: corregidas fuentes de 18 síndromes y una referencia vasoactiva; 60 casos sin cambios fuera de procedencia.
- Nota: 60 casos conservados; negaciones, discriminantes y relaciones visibles. P1 de puntuación en notas mixtas y rendimiento clínico pendientes. Alcance: `clinical/qa/NOTE_OBSERVATIONS_20261121.md`.
- PR51/M10: normalización técnica de rasters, abstención y exclusión externa de PDF/DICOM. Alcance y controles en `clinical/qa/M10_TECHNICAL_FOLLOWUP_20261121.md`.
- Nueve fichas de imagen v1 aceptadas: «si claro que si», 20/11; GREEN de referencia con alcance y fuentes registrados.
- POCUS-MODE v1 aplicado exactamente; 12 pruebas de proyección, 4 de normalización y 2 del gate PASS; QA remota: checks del commit entregado.
- Aceptación: `clinical/qa/IMAGE_REFERENCE_OWNER_APPROVAL_20261120.md`; padres de imagen y nota YELLOW, rendimiento pendiente.
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
