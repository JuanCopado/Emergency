# Seguimiento central de decisiones — 27/11/2026

Este seguimiento suplementario concilia las decisiones ya concedidas y el encargo activo. No sustituye los expedientes históricos ni implementa nuevas reglas clínicas. La [matriz estructurada](TASK_CONTROL.json) conserva estados, dependencias, evidencia y siguiente acción por tarea.

## Base y procedencia

- Receptor internacional comprobado mediante GitHub: `2058e97179ae793914dcd016e4fd033395dbc3e2`; comparación con `codex/v144-international-scope-20261116`: idéntico, cero commits posteriores en la consulta de este corte.
- Árbol receptor: `78e27cb900f7dd901eb5aeb48026276dc48b942c`, idéntico al candidato integrado PR120 `5494b0037dcfe2c2565187985b862ffa8ea1d83b`.
- El trabajo local parte de ese candidato porque el commit de merge no está disponible localmente y `git fetch` falló por resolución DNS. Esta equivalencia de árbol no equivale a identidad de commit ni transfiere resultados de CI a esta entrega.
- [Registro de decisiones del propietario, commit `9018e14`](https://github.com/JuanCopado/Emergency/blob/9018e14bb058c6ebb6f8bf1224924997ba3109a7/docs/coordination/work-closure-20261126/SEGUIMIENTO_DECISIONES_PROPIETARIO_20261127.md), recuperado íntegramente por integración GitHub. Blob: `d4ebe009e41af932e9c041951ed5408643662699`.
- Registro local de coordinación `CONCILIACION_CORTE_CONCURRENTE.json`, observado `2026-11-27T06:53:04.674061+00:00`: el encargo PROT/CARDIO pertenece al chat Codex `6b08ba14-5d8c-83ed-9920-7fcb6372b058`. El intento de recuperar ese chat con Codex App falló; no se afirma recepción de un mensaje nuevo, ejecución terminada ni existencia de un candidato publicado.

## Estado que sustituye únicamente los campos de respuesta pendientes

**MED-RES-PROT-01 v1: SÍ, 27/11/2026 06:14:21 UTC.** Aprobación limitada a clasificar `PROTAMINE_HOSPIRA_10` como `HISTORICAL_REVOKED_ES_NOT_FOR_PRODUCT_SELECTION`, mantener `runtime_enabled=false` y preservar el límite histórico estricto `<5 mg/min`. No modifica rutas activas, no convierte globalmente otros límites en ese límite estricto y no sustituye automáticamente el producto por LEO, Prosulf u otro. El expediente histórico conserva su fuente AEMPS 45777 y la pregunta original; no se le atribuye una nueva verificación regulatoria en este corte.

GMA-P1-003 deja de depender de una respuesta del propietario. Su implementación aislada está asignada al encargo previo de Codex. El SHA, diff y QA de esa implementación no se han recibido: el hallazgo no se declara técnicamente cerrado ni integrado. La conservación observada de `runtime_enabled=false` no demuestra por sí sola la implementación de la clasificación histórica aprobada.

**MED-RES-CARDIO-01..06 v1: SÍ conjunto, 27/11/2026 06:12:33 UTC.** Las seis aceptaciones estructurales se conservan con estos resúmenes de alcance, sin tratarlos como fichas originales ni protocolos nuevos:

| ID | Alcance aprobado resumido | Dependencia para implementar |
|---|---|---|
| MED-RES-CARDIO-01 | Router de monitorización y cuatro circuitos existentes; preservar ARR-SELECTOR y excepciones pediátricas. | Ficha original y delta verificable del encargo activo. |
| MED-RES-CARDIO-02 | Circuitos por lesión valvular y situación hemodinámica; sin pauta universal. | Ficha original y correspondencia con contenido canónico. |
| MED-RES-CARDIO-03 | Circuitos por dispositivo y complicación, con monitorización y especialista aplicables. | Ficha original y correspondencia con contenido canónico. |
| MED-RES-CARDIO-04 | Objetivos de presión arterial por indicación; preservar vías específicas. | Ficha original y fuente exacta de la secuencia general. |
| MED-RES-CARDIO-05 | Selección por indicación, contraindicaciones, producto y jurisdicción. | Ficha original; no habilitar productos o cálculos no verificados. |
| MED-RES-CARDIO-06 | Dolor torácico no coronario por causa; sin antitrombótico genérico ni alta por una sola prueba. | Ficha original y correspondencia con contenido canónico. |

Las fichas originales completas de las seis propuestas no están recuperadas en este expediente. `9018e14` contiene resúmenes y declara esa dependencia. Por tanto, registrar la aprobación está terminado; implementar reglas a partir de esos resúmenes permanece bloqueado por trazabilidad documental. No se pide repetir las decisiones ni se inventan cifras, dosis, umbrales o algoritmos.

## Conservación y límites

Los 19 contratos aceptados el 16/11 y MED-DEC-R46-01/02 mantienen su vigencia y alcance. La revisión del propietario del banco dermatológico conserva 23 casos y 24 archivos, sin heredar permisos de privacidad, redistribución ni condición de validación independiente. Clinical Minimal está aprobado como base visual; este seguimiento no reemplaza la interfaz.

R5-1, R5-2 y SCA conservan sus requisitos humanos e institucionales; su preparación técnica puede continuar. La falta de revisores no bloquea las tareas independientes. Farmacia es consultiva y no constituye una firma obligatoria del proyecto.

Entrega exclusivamente documental. Comprobaciones pertinentes: lectura de JSON, coherencia de los ocho IDs de control, `git diff --check` y revisión del alcance del diff. No se ejecutan suites clínicas o de interfaz sin cambios de código. No se declara CI nueva ni auditoría independiente de este commit.

**CLINICALLY_PENDING · NOT_FROZEN_NOT_VALIDATED · NO_GO_CLINICAL_RELEASE.** Sin cambios de runtime, dosis, fórmulas, catálogos, `last_checked`, ramas protegidas, despliegue o liberación clínica.
