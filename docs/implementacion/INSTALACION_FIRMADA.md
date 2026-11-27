# Instalación individual · contrato de entrega

Fuente A del ensayo final: `078dcb866d80e69405814666d9417a76bcc488bc`.
El siguiente commit incorpora este contrato y el arnés reproducible; no modifica
motores clínicos. A y B se compilan por separado con su identidad Git real para
probar actualización y rollback del service worker, no solo cambiar un puntero.
Ambas versiones finales incluyen la corrección de navegación obsoleta, pins
oficiales de seis wheels y staging del verificador. No se atribuye esa protección
retroactivamente a los paquetes preliminares A2/B2, conservados como históricos.
El ensayo A5/B5 incorpora además conservación de la instancia de formularios al
bloquear rutas y al cambiar parámetros de la misma pantalla (seis regresiones
focales de guard). Los contadores del ensayo final son A5=6 y B5=7. La aceptación no equivale a una lista
de revocaciones: el rollback comprueba firma e integridad e intención explícita.

Los paquetes contienen frontend compilado, fuentes canónicas seleccionadas,
fuentes tipográficas y licencias, seis wheels fijados y launcher autenticado.
No contienen un intérprete Python, documentos científicos prestados, casos reales,
claves privadas, tokens ni datos de pacientes. La recepción técnica no autoriza uso
asistencial. Las capacidades ausentes responden con indisponibilidad explícita.

La clave pública de este editor local está en
[PUBLISHER_PUBLIC.json](evidencias/PUBLISHER_PUBLIC.json). Huella observada al
generarla localmente antes de firmar los archivos:
`02a782bd1e8f8ad24548e7535ef7e745188d0c61351c84f2eff710e6c59a56c4`.
Este registro Git es un canal distinto del ZIP que se verifica; el receptor debe
obtener y autenticar su copia de confianza. No equivale a un certificado de una
autoridad pública. La clave privada protegida con DPAPI permanece fuera de Git,
OneDrive y las entregas. No se rota ni sustituye automáticamente.

Instalación y arranque: [bootstrap](../../tools/local-installation/BOOTSTRAP_README.md).
Preferencias y actualización: [PWA](../../tools/local-installation/STABLE_PWA.md).
Capacidades y límites: [backend](../../tools/local-installation/backendREADME.md).

La primera instalación no activa la versión automáticamente. El recibo devuelve
la versión exacta y las órdenes para activarla e iniciar. Las actualizaciones
conservan la raíz de instalación, el editor fijado y el origen. El rollback exige
su acción explícita y una versión firmada, con comprobación de todos sus bytes.
No elimina exportaciones guardadas por el usuario ni modifica episodios abiertos.
Un lock de escritura conservado tras una interrupción no se elimina a ciegas:
comprobar que no haya un instalador activo y revisar su recibo antes de retirarlo.

Ensayo reproducible, únicamente con datos sintéticos y perfil Chrome propio:

```powershell
node tools/local-installation/verify_installed_pwa.mjs 'RUTA_DEL_EXPEDIENTE_CON_EVIDENCIAS'
```

El expediente debe contener `EVIDENCIAS/PAQUETES_FIRMADOS.json` con dos paquetes,
sus firmas, una instalación física verificada y un Python compatible. El arnés
instala una PWA de prueba real, la inicia en modo standalone, prueba A→B→A,
preferencias, pestaña con nota abierta, API obsoleta, corte de WAN y corte completo.
Desinstala exclusivamente su PWA y cierra exclusivamente los procesos y el perfil
que ha creado. Un FAIL conserva la evidencia y no declara PASS por tener SW.

Estado de esta especificación: ensayo integrado todavía pendiente en este commit.
La evidencia resultante identificará paquetes y SHA exactos. Auditoría y CI se
registran aparte; no se heredan de PR133/134/135.

**CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE.**
