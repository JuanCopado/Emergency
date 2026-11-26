# Seguridad y rendimiento · resultados observados · 26/11/2026

Base `87a17301…`. Solo hallazgos vigentes; no se repitieron auditorías previas sobre objetos sin cambios.

## Dependencias
| Comprobación | Resultado |
|---|---|
| `npm audit` (app, lockfile actual) | 0 vulnerabilidades (info/low/moderate/high/critical = 0) |
| `pip-audit` sobre `clinical/requirements.txt`, `-test`, `-multimodal`, `-blood-gas` | 0 vulnerabilidades conocidas. Límite: solo pins directos (`--no-deps`); dependencias transitivas no auditadas |
| Dependencias de `package.json` sin referencia directa | 0 reales. `@vitest/coverage-v8` y `postcss` los consumen la CI y la configuración (falsos positivos del buscador) |
| depcheck | No ejecutado: `npx --yes` (descarga de un paquete no vetado) fue denegado; se sustituyó por búsqueda local |

## Exposición de información clínica
- `localStorage`: solo preferencias (idioma, tema, símbolo µg/mcg, contexto de referencia con esquema estricto sin campos de paciente). Único punto de escritura: `app/src/lib/storage.ts`.
- 0 `console.log/debug/info` fuera de pruebas en `app/src`. 0 uso de `sessionStorage` o IndexedDB.
- 0 claves de proveedor en el frontend. El backend las toma del entorno.

## Tamaño de bundles (build de producción)
| Chunk | Tamaño | gzip |
|---|---|---|
| `index` | 601,78 kB | 178,66 kB |
| `ResuscitationCircuits` | 583,84 kB | 186,81 kB |
| `score-pdf` | 501,31 kB | 150,34 kB |
| `Procedures` | 472,29 kB | 106,84 kB |
| `pdf.worker.min` | 1.271,92 kB | no informado |
Precaché PWA: 36 entradas, 2.543,66 KiB. Vite avisa de chunks > 500 kB.

**Oportunidades sin tocar comportamiento clínico (no aplicadas):** partición manual de `index` y `ResuscitationCircuits` (`manualChunks`); revisar qué entra en el precaché. Quitar PDF o el worker del precaché cambia el comportamiento sin conexión: decisión del propietario, no se aplicó.

## Otros
- Código duplicado y componentes obsoletos: NO VERIFICADO (sin herramienta local aprobada).
- Auditoría de evidencia: `clinical-image-interpretation: evidence review overdue (70 days; limit 30; status yellow)`. Se informa, no se renovó la fecha (política AGENTS).
- Pruebas: app 55 archivos / 1047 PASS; typecheck y build correctos; clínica 1697 pruebas con 19 errores, **todos de entorno** (modelo OCR local verificado y fuente `arial.ttf` ausentes en este contenedor; los 19 son `test_blood_gas_*`). Estos 19 se confirman solo en CI: NO VERIFICADO localmente.
