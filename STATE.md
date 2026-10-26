# STATE — T01, 26/10/2026

- Base v1.44: `ada519ac2f8e31ce807f397319ce260724642756`.
- Rama aislada de trabajo: `codex/v144-t01-architecture-ci`; sin merge ni publicación.
- 131 módulos; estados preservados: 29 GREEN / 102 YELLOW. CLINICALLY_PENDING.
- Catálogo derivado: 220 fuentes; 131 módulos con procedencia; 77 identidades compuestas pendientes.
- Grafo determinista de procedencia: no produce recomendaciones ni aprobación clínica.
- RAG: contrato documental; recuperación semántica y modelos no implementados por T01.
- Cuatro P1 originales abiertos: GMA-P1-001, GMA-P1-002, GMA-P1-003, GMA-C-P1-001.
- Los 19 contratos agudos bloqueados conservan su estado y código.
- CI propuesta en esta rama: push `main`, `v1.*`, `codex/**`, sujeto a rutas; sin ejecución remota acreditada.
- Auditoría reforzada bloquea tres GREEN con revisión vencida: ictus isquémico, SCA y sepsis/shock.
- No se alteran fechas, fuentes canónicas, dosis, fórmulas ni protocolos para pasar QA.
- Los resultados técnicos y límites de T01 se documentan en `docs/T01_IMPLEMENTATION_REPORT.md`.
- C01 permanece separado y sin modificar. MVP pendiente de resolver los gates de QA y revisión humana.
