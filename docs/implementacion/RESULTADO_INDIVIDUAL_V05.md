# Resultado individual v0.5 · entrega parcial verificable

**IMP-01: decisión técnica local aceptada. IMP-03/09/10: PARCIAL.**
No cierre completo de instalación ni autorización asistencial.

Paquete B5: `ff8f9090e85d48a684e5f9911a2dce0f0c5eddec`, 138 archivos,
28.707.820 bytes, SHA-256 `888da94ac5355b64c4b26b4a914391a9f70c6865a9ca579b832e73207bf07ee2`.
A5 de rollback: `078dcb866d80e69405814666d9417a76bcc488bc`.
HEAD de pruebas/documentación se distingue de la fuente empaquetada; los seis
módulos de ejecución y el frontend conservan sus bytes Git. [PR136](https://github.com/JuanCopado/Emergency/pull/136)
continúa en borrador sobre PR135. PR129–135 permanecen abiertas y sin fusionar.

| Control | Resultado medido |
|---|---|
| Firma Ed25519, pin independiente, ZIP/hashes e intake reanudable | PASS sintético y físico; clave privada DPAPI fuera de OneDrive/Git |
| Seis wheels | Versiones/ABI/SHA oficiales del mismo objeto Git exigidos antes de firmar; manipulación/ausencias/extras rechazados |
| Instalación limpia B5 | PASS 23,297s; verificador en staging, rename, runtime offline separado; sin pip global |
| Suite local final | 94 ejecutadas, 93 PASS/1 SKIP por permiso symlink1314 |
| CI de `90ba359bf5b0595f5d62d5ca195039ab90d29d3c` | 4 workflows/10 jobs SUCCESS; Windows individual94/94; React1186/67 archivos; clínica1779 con21 SKIP |
| Sonar del mismo SHA | QUALITY GATE PASSED; tools/local-installation está fuera de sonar.sources, sin atribuirle cobertura |
| PWA nativa abierta | PASS independiente: mismo target, nueva ventana OS, standalone y SHA A5 exacto mediante PWA.openCurrentPageInApp |
| A/B/A de documentos nuevos | PASS en Chrome158; mismo origen/preferencias, nota/documento/encuentro antiguo intactos, API409, rutas nuevas bloqueadas; sin requests externos de la app |
| Actualización de PWA instalada/caché sin servidor | NO VERIFICADO; bloquea la aceptación final |

**Bloqueo IMP03-SW-ACTIVATION:** en el paquete individual no se observó registro
activo/controlador dentro de35s, con316 sondeos resueltos. sw.js y Workbox
respondieron200; causa **NO DETERMINADA**. No atribuirlo a dependencia externa,
permisos o tamaño sin evidencia. La ausencia de error de página no es PASS.

Se retractan los PASS de arranque deducidos de predicados async de waitForFunction:
la versión instalada trataba la Promise como truthy antes de adoptar false.
El sondeo final comprueba el resultado resuelto en Node. Los fallos originales
se conservan, junto con errores de selección de target/perfil y Git128.
Git128 quedó identificado como contaminación GIT_CONFIG heredada en la fixture;
su entorno se aisló sin modificar la configuración del equipo. PWA.launch no
produjo un target de página enlazable por aquel arnés; la apertura nativa alternativa
es una prueba distinta, no un PASS retroactivo de ese comando.

La auditoría alternativa independiente corrigió pins, staging y remount de formularios.
No se atribuye a Antigravity: no pudo activar la ventana y no emitió dictamen nuevo.
Claude decidió local primero/híbrida opcional; no eligió proveedor ni autorizó gasto.
Los remotos, OIDC y PostgreSQL no son requisitos de esta preparación local.

Requisitos/límites: Python3.12x64 previamente instalado, intérprete no incluido;
OCR/T05/T06 e inferencia remota ausentes con503 explícito. Sin WAN, el proceso local
sirve UI/API verificadas; no equivale a API disponible sin proceso ni a caché PWA
validada. No se modifican fórmulas, dosis, motores, aceptaciones ni estados clínicos.
No merge protegido, contratación, despliegue o GO_RELEASE. C12 de una futura fusión
deberá verificarse sobre el receptor y commit correspondientes, no deducirse aquí.

Plan y cola conservan los doce IDs. CI del HEAD posterior, evidencias, guía y
comprobantes privados: [carpeta de entrega](https://drive.google.com/drive/folders/1DUeujW5m2tVRiJxzg4mk1I4mOyAy86ah)
y [checks vigentes PR136](https://github.com/JuanCopado/Emergency/pull/136/checks).
**CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE.**
