# Clinical Minimal: brechas HTTP y orden Windows

Base de producto observada: `a606a442c071b3f84c17b43f45704ae62d30d44a` (PR126), árbol `9d7bfd58cca76b968eee1ec3ee7a411c87a3d274`.
Este incremento añade un arnés y recibos; no modifica producto, diseño, dosis ni controles. Work conserva la matriz y documentos centrales. No duplica la auditoría PR126 encargada a Antigravity.

## Evidencia ejecutada

`CLINICAL_MINIMAL_HTTP_QA.json` contiene la ejecución Linux x64 / Chromium 154.0.8037.57 sobre HTTP real y API Python autenticada, sin interceptar respuestas ni imprimir credenciales. Identidad de build comprobada contra el SHA anterior. PASS:

- Ocho estados pendientes del hero: ES/EN oscuro y PT-PT/ZH claro, anchos 360/1366; imagen cargada, H1, foco de teclado visible y ausencia de desbordamiento horizontal.
- 30 enlaces Home abiertos realmente en cada idioma: 120 navegaciones, salida del contenedor opt-in y destino con H1.
- Cuatro flujos móviles Home opt-in → nota → sugerencia real → revisión de esta versión → exportación. Datos exclusivamente sintéticos, marcados NON-PRESCRIBING; medicación no accionable.
- Negativos: exportaciones bloqueadas antes de revisión, validación bloqueada sin confirmación de seguridad y exportaciones bloqueadas tras editar la versión revisada.
- Seis descargas HTTP200: JSON en cuatro idiomas, PDF PT y DOCX ZH. El recorrido inicial comprueba presencia del digest y contenido sintético; PDF/DOCX verifica firma de archivo. El cotejo adicional indicado abajo exige igualdad del digest. No acredita apertura nativa ni impresión.

`ARTIFACT_MANIFEST.json` conserva hashes de ocho capturas y seis descargas locales. No se genera ni sube otro ZIP. La inspección visual focal de ZH claro móvil permite revisar ilustración y foco; la captura completa se tomó tras enfocar búsqueda y refleja la posición de scroll de ese momento.

El recibo conserva el hash exacto del arnés ejecutado. La versión portable posterior acorta únicamente `browserControl` a la tecnología usada: no atribuye el fallo de CUA del entorno de preparación a un futuro equipo Windows. No cambia navegación, aserciones, API ni controles y no justifica repetir el recorrido Linux.

La revisión interna posterior detectó dos defectos del arnés, corregidos: la presencia del digest no prueba su igualdad con la revisión recibida por API, y un preflight fallido podía dejar un PASS previo en la carpeta. `CLINICAL_MINIMAL_DIGEST_QA.json` registra cuatro flujos focales reales adicionales (sin repetir hero/120 enlaces), seis descargas y comparación exacta entre `therapeutic_review.plan_digest` exportado y el digest de la revisión API, además del alcance `physician_review_of_this_version`. `PREFLIGHT_EXPECTED_FAIL.json` es un negativo deliberado: se sembró un PASS antiguo, se exigió Windows en Linux y el arnés lo sustituyó por FAIL. Resultado esperado comprobado, sin iniciar navegador/API. Ahora se registra RUNNING antes del preflight y FAIL al rechazar plataforma/build. Ambos recibos conservan el hash exacto del arnés de su ejecución; no son Windows.

Tres fallos iniciales del arnés quedaron registrados en logs locales: transición React aún pendiente tras cambiar URL; nombre accesible real `Word (.docx)`; envelope de exportación distinto del de validación. Se corrigieron las comprobaciones contra las interfaces existentes, sin tocar las expectativas clínicas ni el producto. Ejecución final útil: PASS. Sintaxis Node y ESLint focal: PASS (ESLint se ejecuta desde `app`). No se repiten las suites previas de PR126.

## Orden operativa a Work — Windows real

Pendiente, sin nueva aprobación médica. Ejecutar en un checkout aislado de esta rama; conservar salidas en una ruta C realmente accesible, por ejemplo `C:\EMERGENCY\FASE_SIGUIENTE\CODEX\minimal-http`. No usar D si no está expuesta. No desactivar políticas de red, seguridad ni autenticación.

```powershell
cd app
npm ci
$env:EMERGENCY_SECURITY_AUDIT='1'
npm run build
$env:CHROMIUM_PATH='C:\Program Files\Google\Chrome\Application\chrome.exe'
# Usar la ruta real de Chrome/Edge instalada; no descargar ni inferirla.
$env:MINIMAL_HTTP_REQUIRE_WINDOWS='1'
Remove-Item Env:\MINIMAL_HTTP_FLOW_ONLY -ErrorAction SilentlyContinue
$env:MINIMAL_HTTP_SOURCE_SHA=(git rev-parse HEAD).Trim()
$env:MINIMAL_HTTP_QA_OUTPUT='C:\EMERGENCY\FASE_SIGUIENTE\CODEX\minimal-http'
node scripts/check-clinical-minimal-http.mjs
```

El script exige `process.platform === win32` cuando se activa el requisito y comprueba el SHA servido. Si la política Windows impide HTTP local, conservar el error y su alcance; no declararlo PASS ni sortear la política. Conservar JSON, capturas y descargas individuales. Añadir observación nativa focal: abrir PDF/DOCX sintéticos, comprobar caracteres y usar diálogo de impresión/vista previa si está disponible; anotar app/versión/resultado. Comprobar navegación con teclado y lector de pantalla disponible, sin llamar a esto certificación completa de accesibilidad. No duplicar auditoría Antigravity ni alterar la matriz desde esta rama.

## Pendientes reales

Windows real, apertura/impresión nativa y lector de pantalla aún no observados desde este entorno Linux. La entrada a gasometría/T06 solo acredita navegación web; sus servicios nativos requieren sus propias evidencias. Browser CUA falló al inicializar (`gaas-browser node_repl sandbox cannot be disabled`); no se infiere de ello el estado del equipo de Work. Ningún cambio productivo fue necesario en la brecha Linux comprobada. Se mantiene opt-in y `CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE`.
