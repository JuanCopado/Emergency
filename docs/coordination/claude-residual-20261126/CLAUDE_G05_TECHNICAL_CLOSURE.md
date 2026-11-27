# G05 · cierre técnico residual · 26/11/2026

**G05 global sigue BLOCKED.** Este expediente cierra solo lo verificable por ingeniería. No habilita consumidor público, RAG ni consultas clínicas externas. Base `87a17301…`, código `5746d3dd…`.

## Correspondencia con los seis requisitos canónicos
Fuente vigente: `docs/coordination/r5-g05-20261126/G05_REQUISITOS.json`, derivado trazable de R88. Sus IDs G05-01 a G05-06 se conservan. Los ejes informativos de R6 no sustituyen esta matriz.

| # | Requisito | Estado | Evidencia observada ahora |
|---|---|---|---|
| G05-01 | Consumidor y despliegue | Laboratorio local conservado; consumidor público no definido | T06 usa 18 escenarios sin búsqueda libre; plataforma por adaptador y alcance público deben conservar su identidad y controles. Resultados de PR119 históricos, no transferibles al nuevo SHA |
| G05-02 | Derechos y procedencia | Permisos por campo/uso y licencia propia pendientes | Documentos consultados no autorizan RAG o redistribución. Se conserva procedencia T06 y evidencia de dependencias |
| G05-03 | Privacidad, autenticidad y seguridad | Controles locales implementados; alcance público pendiente | Privacidad, acceso, retención y aislamiento requieren el consumidor preciso y auditoría del mismo candidato |
| G05-04 | Integridad del contenido externo | RAG público no implementado ni habilitado | Diseño en `rag/README.md`; sin promoción automática de fuentes ni cambio clínico |
| G05-05 | Liberación y trazabilidad | QA y auditoría del SHA final pendientes | El aprobador clínico ya es el Dr. Juan Copado Ceballos; Farmacia es consultiva. Faltan responsables operativos nominales y recibos del candidato que se proponga liberar |
| G05-06 | PTBR-PIX | Contrato literal específico y aceptación pendientes | PTBR-MOD no autoriza acceso a píxeles. No se activa esa función ni se extienden MED-DEC-R46-01/02 |

## Integridad
- 19/19 archivos inmutables de `tools/t06-localhost-lab/SOURCE_PROVENANCE.json` coinciden en SHA-256 con el árbol de `87a17301…`. Los dos adaptadores declarados modificados (`server.py`, `loopback_worker.py`) no cuentan como inmutables.
- `tools/t06-localhost-lab/test_integration.py`: 6/6 PASS (Linux).
- RAG: solo README de diseño. Sin cambios en `rag/`.

## No verificado
Cumplimiento de Europe PMC y NVD por campo; licencia del código propio (NO ASIGNADA); aislamiento exhaustivo del equipo; T05 Windows en esta sesión (no se repitió).

## Preparación operativa pendiente
Designar responsables nominales de ingeniería, seguridad/privacidad y titular de fuentes; documentar finalidad, campos, plataforma, retención y destinatarios del consumidor concreto. Juan ya está designado como autoridad clínica. Este expediente no añade una decisión médica SÍ/NO ni exige firma física; prepara la información que pueda requerir una decisión material posterior. Las aceptaciones de los 19 contratos y MED-DEC-R46-01/02 se conservan en su alcance. Sin consumidores nuevos, estudio ni despliegue.
