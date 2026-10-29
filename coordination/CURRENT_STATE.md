# Estado de coordinación

PLAN_ID: `1a10fda3a5b8295125a4b82088710a9ac31cc7361a32272f4e948d86eb3e0597`. Plan Maestro: **v1.1.1-reconstruction-draft**. Registro vigente: **PUBLISHED_DOCUMENTARY**. Estado global: **CLINICALLY_PENDING**.

## Hechos y cortes diferenciados

- Preparación D-001C: 2026-10-29T13:50:48-05:00, completada localmente sin commit/publicación.
- Preparación de revisión D-001C/R1: 2026-10-29T13:57:58-05:00; informe emitido 2026-10-29T13:59:52-05:00, también sin commit/publicación.
- Publicación D-001D: rama `coordination/v144-control`, commit `37c9c7c003d43fc1992ae353ee45190483651ca3`, PUBLISHED_PASS. Fecha 2026-10-29; commit 2026-10-29T19:08:06Z; publicación ya verificada según informe D-001D de 2026-10-29T14:10:28-05:00. Hora exacta del push no disponible.
- Corte operativo de corrección D-001E: 2026-10-29T14:24:40-05:00. Esta revisión y SHA256SUMS.txt son locales, **no publicados**. El SHA de entrada permanece en el commit D-001D, no hay commit nuevo.

## Autoridad y restricciones conservadas

D-000: autoridad del propietario. D-001A: copia temporal de Codex únicamente. D-001C: preparación documental. D-001D: autorización histórica de un commit/push documental; no se amplía. D-001E: correcciones locales sin commit/push/PR/merge/rebase. La fuente permanente de autorización sigue PENDING_EVIDENCE_LINK; hashes locales no son firmas.

PT-1 GLOBAL: **NOT_VERIFIED**. D-006A/D-006B: **NOT_AUTHORIZED**. I02: **NO-GO**. Agentes reales no autorizados; inventario de worktrees pendiente de G0; no iniciar G0-B. Cuatro P1 históricos abiertos y 19 contratos farmacológicos bloqueados según inventario documental, sin nueva auditoría clínica. No promover YELLOW a GREEN ni modificar main, RC1, v1.43, dosis, algoritmos, contratos o pruebas.

## PT-1: significado de cada resultado

PT-1B Codex Cloud: FAIL declarado. PT-1C lectura pública: PASS declarado. Paso 2: CONDITIONALLY_CLOSED. Esos estados no se cambian retrospectivamente.

| Tarea | Alcance | Estado |
|---|---|---|
| PT-1D/T0 | Pruebas sintéticas del laboratorio restringido | PASS limitado declarado; no ejecutadas por Codex |
| PT-1D/T1 | Pruebas negativas limitadas de exposición de herramientas | PASS limitado declarado; no ejecutadas por Codex |
| PT-1D/H | Intento original de registrar evidencias cuando no existía el ledger | BLOCKED histórico, según instrucción del propietario D-001E |

El registro posterior de evidencias en D-001C/R1 y su publicación en D-001D son hechos distintos; no reescriben H como PASS. El alias antiguo PT1D_H se conserva en la trazabilidad, sin duplicar tarea.

Fuentes originales PT-1D/F (sanitización) y G (exportación): no disponibles. El ZIP PT1D_T0_T1_SANITIZED_EVIDENCE.zip tiene hash **declarado**, no recomputado por Codex: `8aa7ac89e8d26088937cfee9a5edfd63ac4a4f1030a7131881652fedb6746f70`. No se aporta informe identificable de un auditor tercero; esa verificación sigue NOT_VERIFIED. El informe histórico de H y los informes R1/D-001D disponibles tienen hashes de sus bytes comprobados; eso no valida el ZIP ni las pruebas originales.

Ver MASTER_LEDGER, DECISIONS y PLAN_MANIFEST para procedencia y cronología; reports/TASK_REPORT_PT1D_H.md conserva el registro histórico y añade una corrección explícita.
