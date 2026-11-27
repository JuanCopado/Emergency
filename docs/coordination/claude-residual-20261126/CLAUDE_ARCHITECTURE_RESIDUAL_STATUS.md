# Arquitectura residual · estado verificado · 26/11/2026

CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE. Sin cambio de dosis, reglas, catálogos ni `last_checked`.

**Identidad.** Base `87a17301c395546536dce12150307a5b1474f844` (árbol `50e1e58f4a830be23dbf5b16ad76aec4597584bb`), rama `claude/residual-architecture-20261126`. Commit de código `5746d3dd103d7d66e9e4fb1ee8d6b35ed4237dd2` (árbol `8dc8cd14abce1074f8d098a39068137b3ba0b3b4`). Este expediente es un commit posterior de solo documentación.

**Coordinación.** PR115 (39 archivos) y PR116 (63 archivos) son de Codex. No se tocó ninguno de sus archivos. Se descartó una corrección propia en `pt.clinical.json` por solapar con PR115 (ver `CLAUDE_INTEROPERABILITY_STATUS.md`).

## Capas de `docs/ARCHITECTURE.md` frente al repositorio

| Capa | Diseño | Implementación observada | Capacidad operativa |
|---|---|---|---|
| Núcleo clínico | sí | 131 módulos; `validate_modules.py` PASS; catálogo derivado `normalize_evidence_sources.py --check`: 254 fuentes / 131 módulos OK | Referencia; sin validación clínica prospectiva |
| Motores deterministas | sí | `app/src/lib/infusion.ts`, calculadoras | Con sus pruebas (app 55 archivos / 1047 pruebas PASS) |
| Grafo | sí | Solo `knowledge-graph/README.md` en Git. El catálogo de procedencia sí existe | Ninguna: el grafo no está construido |
| RAG | sí | Solo `rag/README.md` (contrato). 0 código de recuperación | Ninguna. No declarar implementado |
| Multimodal | sí | Backend M10 y UI de nota; capa 7 solo en laboratorio aislado | Sin rendimiento diagnóstico establecido |
| Agentes | sí | Sin código de agentes (solo `clinical/agents/openai.yaml`) | Ninguna |
| Modelos externos | sí | Solo `models/MODEL_REGISTRY.md` | Ninguna |

## Fronteras frontend, backend y proveedor externo de IA (verificado en código)

- Frontend → backend local: `app/src/clinical-note/api.ts` solo llama a `/api/clinical-note/*` (prepare, interpret, accept, preflight, analyze, export). T06: `fetch('/api/t06-lab/search')` con `credentials:'omit'`, `cache:'no-store'`, `redirect:'error'`.
- Backend → proveedor: `clinical/scripts/clinical_note_vision_adapter.py`. Configuración solo por entorno (`CLINICAL_VISION_PROVIDER_URL/TOKEN/TIMEOUT`, 1..180 s). HTTPS obligatorio, sin redirecciones, solo cargas binarias enrutadas, bloqueo con privacidad STOP. Sin proveedor configurado no hay envío.
- La clave nunca está en el frontend (0 coincidencias de claves en `app/src`).
- Observación (no es un defecto demostrado): `_validate_https` valida solo el esquema, no el destino. Un destino interno es decisión del operador del despliegue.
- PDF y DICOM se excluyen del envío (`imageReview.ts:58`, `ClinicalNote.tsx:408`).

## Pendientes que requieren decisión del propietario
Ver `CLAUDE_G05_TECHNICAL_CLOSURE.md` (consumidor, campos, almacenamiento, responsables) y `CLAUDE_R5_SCA_READINESS.md`.

## Herramientas
Graphify y Ponytail: no instalados en este contenedor (NO DISPONIBLE). Headroom (CLI): no instalado. Se aplicó la política equivalente: búsquedas y lecturas acotadas, sin leer archivos grandes completos.
