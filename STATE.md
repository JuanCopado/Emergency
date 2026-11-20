# STATE · integración T05/T06 · 19/11/2026

20/11/2026 · ARR-SELECTOR-20261120. El Dr. Juan Copado Ceballos aprueba el selector manual de cuatro circuitos en las dos vistas. Ocho navegaciones verificadas en Chromium. Registro vigente: 118 GREEN, 13 YELLOW. Estado global CLINICALLY_PENDING.

La validación clínica del proyecto corresponde al Dr. Juan Copado Ceballos. Preparar la evidencia y presentar una pregunta SÍ/NO por decisión según `AGENTS.md`. Farmacia es consultiva.

- T02 · 20/11/2026: el médico propietario aceptó las 11 anotaciones documentales. [Decisiones por ID, alcance y fuentes](clinical/qa/T02_DECISION_MEDICA_20261120.md).
- Entrega: [PR #33](https://github.com/JuanCopado/Emergency/pull/33), destino `codex/v144-international-scope-20261116`.
- Base: PR32 `abdeae442a151ce1b1fe0786725991a7d35bc558`, posterior a PR31 integrado.
- Estado clínico: **CLINICALLY_PENDING**; no GO_RELEASE ni autorización asistencial.
- T05: revisión local de gasometrías, muestras/metadatos, FiO₂ 21–100 % o fracción 0,21–1.
- T05: extracción protegida disponible solo en Windows; bloqueo explícito en Linux.
- T06: consumidor Q4 y circuito R6/B1 con proveedores TLS sintéticos en Linux.
- T06: sin búsquedas libres, API pública, RAG ni cierre global G05.
- Aplicación: accesos comunes y launcher local con procesos independientes.
- Seguridad: JSON estricto y números sin pérdida a cero; transporte, Host y Origin acotados.
- QA: nuevas regresiones y jobs nativos por plataforma; resultados propios en la entrega/CI.
- Aceptaciones clínicas previas, 19 contratos y 46 IDs conservados; no volver a solicitarlas.
- Evidencia: estados y fechas clínicas intactos; ninguna promoción automática.
- Ramas protegidas: `main`, v1.42-rc1 y v1.43 preservadas.
- Uso y límites: `docs/LOCAL_REVIEW.md`.
- Procedencia: `clinical/qa/T05_T06_INTEGRATION_20261119.md`.
- Antecedentes completos: `docs/coordination/STATE_BEFORE_T05_T06_20261119.md`.
