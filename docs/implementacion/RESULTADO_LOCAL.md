# IMPLEMENTACIÓN · resultado del incremento local

27/11/2026. Referencia permanente: [IMPLEMENTACIÓN](../IMPLEMENTACION.md), PR134. Código aislado: [PR135](https://github.com/JuanCopado/Emergency/pull/135), SHA `8699cdc4f34bff378ae5ef69498bcfd1d944e3bd`. No fusionado ni desplegado. CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE.

## Trabajo ejecutado

Claude Code recibió una consulta real de solo lectura y entregó análisis del repositorio, riesgos y alternativas. Work aceptó IMP-00 exclusivamente para el incremento local. La comparativa y fuentes oficiales separan 10/100/1.000 médicos hipotéticos de cargas, costes o TCO medidos; IMP-01 no está cerrado ni selecciona proveedor. Gemini recibió IMP-02 por la aplicación autenticada y completó un informe; las reservas y fuentes primarias se contrastaron. No se configura una nueva autenticación por el fallo previo de su CLI.

Codex implementó `tools/local-installation/`: paquete determinista con inventario y hashes; recepción ZIP con límites previos al parser; versiones separadas; selección atómica; rollback con revalidación; servidor estático loopback, Host/Origin exactos, CSP con hashes, y API no disponible con 503 JSON. El productor acepta solo un checkout propio limpio y comprueba la revisión embebida; no transforma esa comprobación en firma del editor o atestación independiente del build. No cambia frontend ni motores.

Se corrigieron defectos demostrados: asignación de metadatos ZIP antes del límite, hash CSP de scripts con CRLF, locator ZIP64 capaz de alterar el parser, omisión del worker `.mjs` existente y comparación textual de rutas Windows 8.3. Los FAIL anteriores se conservan en la custodia local; no se resolvieron omitiendo pruebas ni abriendo permisos.

## Evidencia medida

- [Suite local por SHA](evidencias/IMP03_PRUEBAS.json): **23 contadas, 22 PASS y 1 SKIP**. Windows local no permitió crear un symlink nativo (1314); junction NTFS y symlink ZIP se ejecutaron por separado. La regresión 8.3 utiliza `GetShortPathNameW` y Git reales.
- [CI de instalación](https://github.com/JuanCopado/Emergency/actions/runs/46068470440): Windows **23 PASS, 0 SKIP**; Linux **21 PASS, 2 SKIP** de controles específicos de Windows. Fuente del run `8699cdc`; checkout de PR `82d0178` con base documental `8d92844`. No se confunden ambas identidades.
- [Chrome 158.0.8127.37](evidencias/IMP03_NAVEGADOR.json): dos builds reales desde fuentes limpias `81b231c` y `1703435`, sin diferencias `app/clinical` entre esas fuentes; cambia su identidad de build. Tres arranques A→B→A, tres orígenes y workers reales controlando la página; identidad visible correcta, resultado sintético de perfusión **5.3**, API **503**, cero errores CSP/página y cero peticiones externas observadas en ese recorrido.
- Tras detener el servidor y cortar la conexión del navegador, la recarga conservó el cálculo local y la API falló sin devolver HTML. La pestaña A ya abierta no se recargó ni cambió de versión al seleccionar B.
- [Revisión independiente Codex](evidencias/IMP03_REVISION_CODEX.md): hallazgo ZIP reproducido y corregido; revisión final de bytes sin hallazgos abiertos en este alcance. No se presenta como auditoría de Claude o Antigravity.
- [Identidad de los dos paquetes](evidencias/IMP03_PAQUETES.json): 35 archivos por inventario, hashes de ZIP/manifiesto y fuentes. Las copias fueron recibidas físicamente en la instalación de prueba.

La CI general y Sonar de este SHA se recogen por separado al completar sus ejecuciones. Este informe no hereda PASS de PR133, de `be35743` ni de un workflow todavía pendiente.

## Límites y pendientes por tarea

| Tarea | Estado verificable | Pendiente real |
|---|---|---|
| IMP-00 | REVIEWED en alcance local acotado | No aprobación de arquitectura remota o liberación |
| IMP-01 | DELIVERED_PARTIAL | Elección de capacidad/stack remoto, condiciones contractuales y TCO completo |
| IMP-02 | REVIEWED documental acotado | Finalidad, país y obligaciones por flujo antes de activación; no dictamen jurídico |
| IMP-03 | DELIVERED_PARTIAL | Backend local reproducible y alcance de actualización de la PWA instalada no incluidos |
| IMP-04–07 | No despachados | Dependencias y decisiones de arquitectura aplicables aún no satisfechas; sin recursos externos |
| IMP-08–10 | No cerrados | Revisión/auditoría del alcance implementado y aceptación de los entregables pertinentes |
| IMP-11 | BLOCKED_AUTHORIZATION | Sin autorización para provisión, gasto, despliegue o activación clínica |

La prueba de rollback es del lanzador estático en **una raíz conservada**, no garantía global sobre cachés, otras instalaciones, restauraciones antiguas o PWAs instaladas. Cada arranque usa origen nuevo y no migra automáticamente preferencias o marcadores. Se exige comprobar la página efectiva; el ledger no es una raíz de confianza contra el propietario del disco. No se fuerza recarga ni se borra un episodio. Una API 503 nunca acredita soporte offline de funciones que necesitan backend.

C1–C6 se conservan como criterios, sin falsos cierres: C1 está delimitado; C2 requiere CI/seguridad completa y no certifica todo el producto; C3 conserva fuentes clínicas sin modificación, sin repetir aprobaciones; C4 cubre aquí un flujo sintético, no todos los de guardia; C5 tiene evidencia offline parcial y mantiene accesibilidad/migración pendientes; C6 mantiene separadas QA y liberación clínica/regulatoria.

La custodia física está en `C:\Users\juanc\OneDrive\Documentos\ChatGPT\PROYECTO EMERGENCY\ChatGPT_Trabajo\IMPLEMENTACION_20261127`. `D:\ChatGPT_Trabajo` no estuvo disponible en esta ejecución. Los procesos de prueba terminaron; no se dejó servicio público, configuración global modificada, tarea programada ni contratación.
