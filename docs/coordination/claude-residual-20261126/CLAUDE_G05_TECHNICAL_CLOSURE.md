# G05 · cierre técnico residual · 26/11/2026

**G05 global sigue BLOCKED.** Este expediente cierra solo lo verificable por ingeniería. No habilita consumidor público, RAG ni consultas clínicas externas. Base `87a17301…`, código `5746d3dd…`.

## Los seis requisitos vigentes
Fuente: `docs/coordination/R6_G05_20261121.md` («Pendiente congelar consumidor, campos, almacenamiento, plataforma, privacidad y responsables»). La enumeración como seis requisitos es **inferencia** de esa frase; no hay un documento que los numere.

| # | Requisito | Estado | Evidencia observada ahora |
|---|---|---|---|
| 1 | Consumidor | Implementado y verificado en el alcance del laboratorio | Ruta `T06Lab → buildT06ViewModel → T06Metadata`, catálogo local de 18 escenarios, sin búsqueda libre. Pruebas T06 dentro de la app: PASS (55 archivos / 1047). El resultado 18/18 de Q4 se reutiliza de R5, no se repitió |
| 2 | Campos | Parcial | `T06ViewModel` es un tipo cerrado y `buildT06ViewModel` valida entradas. Derechos por campo NO VERIFICADOS (PubMed, Europe PMC, NVD) |
| 3 | Almacenamiento | Cliente sin persistencia; servidor sin política | 0 uso de `localStorage`, `sessionStorage` o IndexedDB en `app/src/t06`. La app guarda solo preferencias (idioma, tema, µg/mcg, contexto de referencia). Retención del servidor: no definida |
| 4 | Plataforma | Implementado con límite | Lanzador T06 solo Linux (`run_local.py:22`); T05 usa Job Objects de Windows. Una interfaz común no valida ambas plataformas |
| 5 | Privacidad | Parcial | Catálogo sintético sin PHI. Revisión de privacidad de un consumidor público: inexistente |
| 6 | Responsables | BLOQUEADO por decisión del propietario | Sin designación nominal de ingeniería, seguridad, titular de fuentes ni aprobador clínico (R5) |

## Integridad
- 19/19 archivos inmutables de `tools/t06-localhost-lab/SOURCE_PROVENANCE.json` coinciden en SHA-256 con el árbol de `87a17301…`. Los dos adaptadores declarados modificados (`server.py`, `loopback_worker.py`) no cuentan como inmutables.
- `tools/t06-localhost-lab/test_integration.py`: 6/6 PASS (Linux).
- RAG: solo README de diseño. Sin cambios en `rag/`.

## No verificado
Cumplimiento de Europe PMC y NVD por campo; licencia del código propio (NO ASIGNADA); aislamiento exhaustivo del equipo; T05 Windows en esta sesión (no se repitió).

## Decisión pendiente (SÍ/NO)
**¿Designas responsables nominales de ingeniería, seguridad y titular de fuentes, y congelas el consumidor T06 de 18 escenarios como único consumidor del alcance G05, sin proveedores públicos ni RAG?**
Un SÍ permite abrir el expediente de derechos por campo y la auditoría de privacidad. Un NO mantiene G05 bloqueado sin cambios.
