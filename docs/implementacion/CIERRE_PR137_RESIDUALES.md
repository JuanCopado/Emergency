# PR137 — cierre focal del candidato individual

28/11/2026 · IMPLEMENTACIÓN v0.7, mismos doce IDs. Este documento es una adenda de ejecución, no otra fase de desarrollo.

## Identidad y evidencia reutilizada

Base PR137: `00bf559d99f6990e73f5b0f77abd9a1d870032f6`, composición `b54301e891110715ed9a388723155f8c354b07b6`. PR129–136 ya son ancestros de esa composición: no se integran otra vez. Receptor internacional conservado: `fa2381dcfe77253f575ac843860b3167125f1e1e`.

Se reutilizan los 21 checks (20 jobs de Actions y control externo), ocho workflows y Sonar favorables de la base. Se conserva el paquete firmado C y su ensayo nativo B5→C→B5, notas, preferencias, 409 y frontend offline; ese ensayo corresponde a sus bytes originales. No es una prueba de otro instalador. Sonar no incluye `tools/local-installation` entre sus fuentes: las revisiones focales y pruebas del instalador son independientes de ese gate.

## IMP-03 — dos defectos operativos confirmados

Código final focal: `15fbec878ca45170fd27e4d0178ff420587792b4`, árbol `c757e12147200616dc905bc1804d0143b08c4d60`. Cuatro archivos respecto a la base: escritor/selección del instalador, dos archivos de pruebas y descubrimiento de pruebas en Linux.

- El escritor obtiene un bloqueo del SO en `writer.guard`, persistente, y mantiene un `writer.lock` temporal O_EXCL con identificador propio. Tras una caída sólo se recupera un marcador v2 completo bajo el bloqueo del SO. Un lock legado, vacío, parcial o desconocido sigue cerrado; no se deduce su seguridad por PID o antigüedad.
- Al terminar normalmente se retira sólo el lock cuya identidad y contenido siguen siendo propios. Si un escritor antiguo gana O_EXCL durante la recuperación, el nuevo falla sin borrar el marcador ajeno. Esto conserva el protocolo antiguo después de una salida limpia, sin cambiar firmas, confianza del launcher ni paquetes previos.
- La CLI estática actualizada rechaza paquetes individuales antes de cambiar selección o contador: su activación/reversión debe usar la ruta individual autenticada. Esto evita un error de uso de la CLI; no pretende impedir que el propietario del disco ejecute herramientas antiguas o modifique sus archivos.

La propuesta intermedia `98ff51b` se conserva como evidencia, pero no se adopta sola: su marcador persistente en `writer.lock` impedía arrancar el escritor empaquetado antiguo. Las revisiones favorables iniciales se limitaron después por esa incompatibilidad. El delta final usa el guard separado; no introduce un host de confianza nuevo.

Regresión integrada final: 30 pruebas contadas, **29 PASS / 1 SKIP** (symlink nativo Windows, privilegio1314), salida0, 7,111s en Windows ARM64/Python3.13.17. Incluye procesos reales, caída/reintento, exclusión, escritor antiguo ganador, retorno limpio al protocolo anterior y rechazo de selección individual por la CLI estática. No equivale a una nueva prueba de firma real, PWA A/B/A o paquete actualizado. El destino del producto sigue siendo Python3.12x64; su CI se verifica por el HEAD publicado, sin heredar la de la base. Los recibos finales de auditoría y CI se conservan fuera de Git para no generar commits circulares por registrar el propio SHA.

Límites: un corte durante la inicialización parcial requiere recuperación revisada. No se acredita soporte de locks en sistemas de archivos remotos. Los ZIP anteriores quedan intactos; no se declara que el parche esté instalado en el paquete C ni se distribuye un paquete nuevo firmado en este cierre.

## Evaluación práctica de la instalación C

Tres recorridos nuevos y acotados, con datos sintéticos, mediante Chrome DevTools MCP en un contexto limpio y origen loopback, sin modificar cabeceras ni protecciones:

| Recorrido | Resultado observado |
|---|---|
| Pantalla360 EN/oscuro, búsqueda, ficha y retorno | PASS acotado. El recorte de la captura anterior no se reproduce; no se parchea la interfaz basándose en aquel artefacto. |
| Borrador personalizado, consulta, revisión humana final y retorno | PASS acotado. Identificador, texto y estado pendiente de revisión se conservan. |
| Laboratorio opcional T06 y retorno | PARCIAL de claridad. Respuesta400 controlada y sin resultado falso; falta explicar en esa pantalla que el circuito no está empaquetado. El retorno conserva el borrador. |

El contexto habitual de Chrome controlado por la extensión mostró `origin_rejected`; no se identificó cuál de las cabeceras difería. El contexto limpio admitió Host/origen y Sec-Fetch-Site:none con200. No se eludieron controles ni se atribuye ese éxito al perfil habitual o a una PWA instalada. Las capturas nuevas se observaron inline; el recibo contiene DOM y medidas, no archivos PNG físicos. Servidor y página de prueba propios cerrados.

T06 es un laboratorio opcional, no una función clínica operativa incluida ni un bloqueo de toda la instalación individual. Su mensaje genérico queda como defecto menor de claridad; no habilita conexión institucional ni justifica ampliar el backend. La comprobación visual no demuestra conformidad WCAG completa. Se conservan límites de PDF sin etiquetas, voz multilingüe e impresión física no acreditadas.

## IMP-09/10 y residuales clínicos

Antigravity recibió realmente el encargo en la conversación `dcadad6d-21af-4183-930d-15f975c260d1`, leyó el código y entregó un informe físico del SHA intermedio. La adenda final y la revisión independiente alternativa se vinculan al SHA final y se registran en la matriz central; no se heredan dictámenes anteriores a un árbol distinto.

Gemini recibió contexto propio permitido y respondió en `https://gemini.google.com/app/d506b1e741021b2d`. No recibió originales restringidos, PHI, fotografías ni claves ciegas. Conserva15/18 lecturas íntegras y cero nuevas preguntas médicas maduras. Work verificó la pista bibliográfica ESPGHAN PMID42383497/DOI10.1002/jpn3.70485 y su enlace PMC; el cuerpo quedó bloqueado por comprobación de navegador, sin eludirla. La licencia declarada por Gemini no se adopta sin verificarla. BSH PMID40903841 confirma identidad bibliográfica, no lectura íntegra ni atribución de recomendación.

Insulina original y preparación original de labetalol siguen SIN IDENTIFICAR. No se reabren protamina,37módulos, seisCARDIO,23aprobaciones dermatológicas ni MED-DEC-R46-01/02. Privacidad/admisión de imágenes, condiciones S2-11/S2-12 y corpus/revisores de los dos YELLOW mantienen sus dependencias exactas. Los huecos antiguos de simulación no reactivan fabricación o presupuestos sustituidos. La mención histórica de PR127 sin integrar se corrige documentalmente; sus limitaciones técnicas siguen visibles. No se renueva `last_checked`.

## Decisión de integración preparada

La integración sólo puede proponerse sobre el HEAD final revisado y su CI exacta favorable, conservando el receptor protegido y la pila ya conciliada. No se ha autorizado aquí un merge, despliegue o uso asistencial. La aceptación del protocolo de locks no acredita una nueva distribución firmada instalada. Las evidencias y acuses se depositan en la [carpeta común](https://drive.google.com/drive/folders/1p07cOR8RcFLg3Y7zoa9UqaRAWOYhO1hs) con lectura de retorno y SHA-256.

**CLINICALLY_PENDING · NOT_FROZEN_NOT_VALIDATED · NO_GO_CLINICAL_RELEASE.**
