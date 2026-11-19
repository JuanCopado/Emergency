# Integración T05/gasometría y T06 · 19/11/2026

Autorización: petición del propietario «integrar T05/gasometría y T06». Rama de trabajo: `codex/integrate-t05-t06-20261119`. Estado clínico: **CLINICALLY_PENDING**. No constituye `GO_RELEASE` ni aceptación asistencial.

## Base y material recuperado

- Base de composición: PR32, commit `abdeae442a151ce1b1fe0786725991a7d35bc558`, árbol `feabbe55ecceea886ccde20aec526ff920dcb473`. Incluye las correcciones P1 de JSON/precisión sobre la integración PR31 `2eeedfd36880e8b971c63f13f7736922cf87de1e`.
- T05: replay desde commit `1d0652ebcef9b5990edd9e5745b0c06f8d6b8274`, con árboles originales verificados `9e6ad2d55b38a3d3130a44bb574c4cdbec6694c1` → `eb9e263f36856addac2de42835c7b191c4856d41` → `0b9a2ecaab038b7624e8a0855c54f220a71882da` (R3, PAR01, FiO₂). Paquetes y manifiestos recuperados; no se reconstruyó código a partir de resúmenes.
- T06: paquete PAR02 SHA-256 `bc5dda63770a5240695bfd7bef98bc9ad86bf1cdef13c445f73ee8eff04083f1`, manifiesto 431/431. Q4 procedente del árbol `c22b755a93fbb1b4dd28dbb88a59dcc67818f9be`; este identificador es un árbol, no un commit. R6/B1 y los cinco archivos Q4 conservan bytes; detalle en `tools/t06-localhost-lab/SOURCE_PROVENANCE.json`.

Los logs y capturas históricos permanecen en sus entregas de origen. La integración incorpora código, pruebas, contratos y procedencia necesarios; no presenta esos logs como pruebas del árbol nuevo.

## Resultado de la composición

Rutas `/blood-gas` y `/t06-lab` incorporadas a la misma aplicación, con acceso desde Inicio y enlace desde la nota clínica a T05. Launcher común, dependencias reproducibles, modelo OCR con hash y licencia y límites de plataforma explícitos.

T05 conserva la revisión visual, separación de muestras, confirmación humana, revocación de resultados y trazabilidad de FiO₂. Se corrigen dos fronteras técnicas encontradas al componer: JSON con miembros duplicados y pérdida no nulo→cero, tanto en números JSON como en analitos textuales. Se reutiliza el transporte HTTP acotado; no se alteran fórmulas ni se introducen nuevos umbrales médicos.

T06 conserva el circuito real R6/B1 con TLS sintético y Q4. Su adaptador limita conexiones, tiempo, Host, Origin, framing y plataforma. Los errores son estáticos. No recibe consultas libres ni datos de pacientes; el acceso a proveedores públicos sigue fuera de este circuito.

El launcher conserva procesos separados: el audit hook de T06 nunca se instala en el servidor clínico. Vite habilita las proxies nuevas solo en modo local, comprueba la conexión y el Host de entrada, conserva Origin y añade CSP y la marca de sesión sin nuevo service worker.

## Revisión del lock de desarrollo

El nuevo middleware Vite necesita tipos Node: se añaden únicamente `@types/node` 22.20.5 y `undici-types` 6.21.0, ambos de desarrollo. Se comparó cada entrada del lock: ninguna dependencia existente ni paquete objetivo de la mitigación cambia. Los scripts, incluido el postinstall previo, se conservan. Una revisión técnica independiente confirmó este delta; se actualiza solo `lock_sha256` en la política de picomatch a `902f89eb70b96e535fb2e2870aa74c2e426ce983c8ce856f59a106a1d5c39af7`. No se cambia `policy_sha256`, targets, guardas, reglas, baseline ni severidades de seguridad. La instalación y las pruebas de la mitigación siguen siendo obligatorias.

## Verificación y límites

Las pruebas nuevas se ejecutan sobre la composición, conservando las regresiones de PR32. Los resultados locales y los enlaces a CI se registran en el informe de entrega de este encargo. El workflow `Local review integration` exige extracción real T05 en Windows y circuito real T06 en Linux, con navegador y recibos propios; no se atribuye aquí un PASS futuro.

El worker T05 requiere Windows Job Objects. El transporte B1 T06 requiere Linux/POSIX. No se ha portado ninguno ni eliminado su contención; no existe una plataforma única que ejecute ambos adaptadores nativos entregados. Un HTTP200 de sesión no se considera prueba de extracción. Una ejecución de navegador no acredita aislamiento de red del SO ni validación clínica.

El registro de evidencia y sus fechas clínicas se conservan sin promoción. Los 19 contratos aceptados y 46 IDs se mantienen; no se restablecen bloqueos históricos. No se modifica `main`, las referencias congeladas ni v1.43. Uso y comandos: `docs/LOCAL_REVIEW.md`.
