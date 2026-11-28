# InstalaciÃ³n individual Â· contrato de entrega

Fuente A del ensayo final: `078dcb866d80e69405814666d9417a76bcc488bc`.
El siguiente commit incorpora este contrato y el arnÃ©s reproducible; no modifica
motores clÃ­nicos. A y B se compilan por separado con su identidad Git real para
probar actualizaciÃ³n y rollback del service worker, no solo cambiar un puntero.
Ambas versiones finales incluyen la correcciÃ³n de navegaciÃ³n obsoleta, pins
oficiales de seis wheels y staging del verificador. No se atribuye esa protecciÃ³n
retroactivamente a los paquetes preliminares A2/B2, conservados como histÃ³ricos.
El ensayo A5/B5 incorpora ademÃ¡s conservaciÃ³n de la instancia de formularios al
bloquear rutas y al cambiar parÃ¡metros de la misma pantalla (seis regresiones
focales de guard). Los contadores del ensayo final son A5=6 y B5=7. La aceptaciÃ³n no equivale a una lista
de revocaciones: el rollback comprueba firma e integridad e intenciÃ³n explÃ­cita.

Los paquetes contienen frontend compilado, fuentes canÃ³nicas seleccionadas,
fuentes tipogrÃ¡ficas y licencias, seis wheels fijados y launcher autenticado.
No contienen un intÃ©rprete Python, documentos cientÃ­ficos prestados, casos reales,
claves privadas, tokens ni datos de pacientes. La recepciÃ³n tÃ©cnica no autoriza uso
asistencial. Las capacidades ausentes responden con indisponibilidad explÃ­cita.

La clave pÃºblica de este editor local estÃ¡ en
[PUBLISHER_PUBLIC.json](evidencias/PUBLISHER_PUBLIC.json). Huella observada al
generarla localmente antes de firmar los archivos:
`02a782bd1e8f8ad24548e7535ef7e745188d0c61351c84f2eff710e6c59a56c4`.
Este registro Git es un canal distinto del ZIP que se verifica; el receptor debe
obtener y autenticar su copia de confianza. No equivale a un certificado de una
autoridad pÃºblica. La clave privada protegida con DPAPI permanece fuera de Git,
OneDrive y las entregas. No se rota ni sustituye automÃ¡ticamente.

InstalaciÃ³n y arranque: [bootstrap](../../tools/local-installation/BOOTSTRAP_README.md).
Preferencias y actualizaciÃ³n: [PWA](../../tools/local-installation/STABLE_PWA.md).
Capacidades y lÃ­mites: [backend](../../tools/local-installation/backendREADME.md).

La primera instalaciÃ³n no activa la versiÃ³n automÃ¡ticamente. El recibo devuelve
la versiÃ³n exacta y las Ã³rdenes para activarla e iniciar. Las actualizaciones
conservan la raÃ­z de instalaciÃ³n, el editor fijado y el origen. El rollback exige
su acciÃ³n explÃ­cita y una versiÃ³n firmada, con comprobaciÃ³n de todos sus bytes.
No elimina exportaciones guardadas por el usuario ni modifica episodios abiertos.
Un lock de escritura conservado tras una interrupciÃ³n no se elimina a ciegas:
comprobar que no haya un instalador activo y revisar su recibo antes de retirarlo.

Ensayo reproducible, Ãºnicamente con datos sintÃ©ticos y perfil Chrome propio:

```powershell
node tools/local-installation/verify_installed_pwa.mjs 'RUTA_DEL_EXPEDIENTE_CON_EVIDENCIAS'
```

El expediente debe contener `EVIDENCIAS/PAQUETES_FIRMADOS.json` con dos paquetes,
sus firmas, una instalaciÃ³n fÃ­sica verificada y un Python compatible. El arnÃ©s
instala una PWA de prueba real, la inicia en modo standalone, prueba Aâ†’Bâ†’A,
preferencias, pestaÃ±a con nota abierta, API obsoleta, corte de WAN y corte completo.
Desinstala exclusivamente su PWA y cierra exclusivamente los procesos y el perfil
que ha creado. Un FAIL conserva la evidencia y no declara PASS por tener SW.

Resultado final: apertura nativa y A/B/A manual de documentos verificados por separado. La actualizaciÃ³n instalada y cachÃ© offline NO VERIFICADAS por activaciÃ³n SW pendiente. VÃ©ase RESULTADO_INDIVIDUAL_V05.md y RECTIFICACION_PWA.json del expediente; no usar un PASS de arranque async retractado. AuditorÃ­a y CI se registran por fuente exacta y no se heredan de PR133/134/135.

**CLINICALLY_PENDING Â· NO_GO_CLINICAL_RELEASE.**


Aceptación posterior v0.6: el ciclo nativo y caché del flujo medido sí quedan verificados por VERIFICACION_NATIVA_V06.md, después del comparativo de perfiles y corrección del arnés. El texto de resultado parcial anterior es histórico; no se atribuye un PASS retrospectivo a aquellos ensayos. Usar perfil de prueba propio, corto, estable durante todo el ciclo; no modificar sesiones existentes.
