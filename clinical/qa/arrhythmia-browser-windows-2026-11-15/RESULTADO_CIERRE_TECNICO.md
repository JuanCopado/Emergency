# Evidencia para cierre técnico — ocho navegaciones reales

Resultado: 8/8 PASS con las dependencias exactas del lockfile y la comparación corregida. Preparado para revisión y cierre del ítem técnico en Windows; registro oficial y estado clínico sin cambios.

PC: JUAN-C, Windows. Fuente: commit 761f42d9afc8a7b7202d18bb0fd506d721dd4e50; árbol Git f834c6f8e77c7006082c909bc28f8bfaa8a72d61. Copia nueva aislada en TEMP; no se reutilizó el enlace a dependencias de la ejecución anterior.

## Corrección

Único cambio entre 1001 archivos de fuente comprobados contra el ZIP preservado: app/scripts/check-resuscitation-router.mjs. Se normalizan a minúsculas el texto visible del enlace y el estado esperado antes de compararlos. Mantiene la comprobación del estado y todos los demás criterios; evita el fallo causado por el estilo CSS que muestra GREEN donde el dato contiene green. Se adjuntan original, corregido y parche portable; el parche NO se ha aplicado a ningún repositorio original.

## Dependencias y entorno

Se restauraron 591 paquetes con npm ci --offline --ignore-scripts --no-audit --no-fund, salida 0. Sólo caché local: ninguna descarga de paquetes o navegador, ninguna instalación global, sin scripts de instalación. package.json y package-lock.json permanecen idénticos al commit. npm ls --all --json devuelve salida 0.

Versiones exactas verificadas: Vite 5.4.21; playwright-core 1.63.0; @vitejs/plugin-react 4.7.0; Vitest 2.1.9; esbuild 0.21.5. Node 24.15.0; npm 11.12.1; Chrome/Chromium instalado 157.0.8103.51. Esta ejecución sustituye la limitación de Vite 7.3.7 de la evidencia anterior.

CHROMIUM_PATH apunta al Chrome ya instalado, sólo en los procesos de prueba. BROWSER_PATH no interviene en este localizador. No se cambiaron firewall, antivirus ni permisos.

## Resultados individuales

| Superficie | Destino | Resultado |
|---|---|---|
| /guides | adult-arrhythmias | PASS |
| /guides | adult-cardiac-arrest | PASS |
| /guides | pediatric-arrhythmias | PASS |
| /guides | pediatric-cardiac-arrest | PASS |
| /clinical | adult-arrhythmias | PASS |
| /clinical | adult-cardiac-arrest | PASS |
| /clinical | pediatric-arrhythmias | PASS |
| /clinical | pediatric-cardiac-arrest | PASS |

Script corregido: 15/11/2026 15:28:54 UTC (14:28:54 Atlantic/Azores), salida 0; 8/8 PASS; cero errores de página. Ruta ejecutada: app/scripts/check-resuscitation-router.mjs en la copia temporal indicada en provenance.json.

Ejecución adicional para capturas: 15:29:15 UTC (14:29:15 Atlantic/Azores), salida 0; 8/8 PASS; cero errores de página. Mismas comprobaciones más capturas y sandbox Chromium explícitamente habilitado. Se adjunta capture-router-local.mjs para distinguir la instrumentación del parche mínimo. Dieciséis capturas nuevas: selector y destino para cada caso. Los logs confirman salida 0 del proceso del navegador y limpieza del perfil temporal; servidor y navegador cerrados.

Se verifican cuatro enlaces, excepción de pulso, excepción neonatal, estado del destino, URL tras pulsar el enlace, encabezado y ausencia del selector en destino. Sólo contenido docente/sintético, sin pacientes. Los 8/8 DOM históricos son evidencia distinta.

## Propuesta de cierre y límites

Recomendar aceptación del ítem de ocho navegaciones reales en Windows sobre este commit más el parche del test. No se declara validación clínica ni resolución del EPERM del entorno Linux original. No se ha modificado el registro de evidencias ni aplicado el parche a main u otra referencia.

Permanecen YELLOW, CLINICALLY_PENDING, 4 P1, 19 BLOCKED e I02 NO-GO. Sin cambios en main, v1.42-rc1, v1.43, dosis, fórmulas, contratos o código de producto.

TECHNICAL_CLOSURE_PROPOSAL.json contiene la propuesta revisable, no una actualización oficial. locked-eight-results.json contiene la ejecución principal; captured-eight-results.json, la ejecución con capturas. Se incluyen stdout/stderr completos, códigos de salida, lockfile, inventario de dependencias, fuente oficial previa, parche y comprobación de integridad. hashes-sha256.csv verifica el paquete.
