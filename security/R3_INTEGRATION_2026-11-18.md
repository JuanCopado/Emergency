# R3: composición de seguridad

R2/E1 se reconstruyó sobre `1d0652ebcef9b5990edd9e5745b0c06f8d6b8274` y coincidió con `5a6eb009742673a2a4ecca743c8b0301146dad87` antes de modificarlo.

- PR25 `fc1c0cf87e45ee8d5ecf193b571f6f864955613e` contiene PR27 y aporta lock, dependencias, CI y todos los prehooks auditados. No se reaplica PR27.
- PR24 `e99c62a771e68d35667f56e70a37126dba359001` aporta protección SSRF, errores HTTP redactados, cabeceras y contención de compilación/service worker. Se conservan los cambios R2 en los archivos comunes.
- PR26 `5e37949e7702f33648fa30979a3dd0fd828f1fbd` aporta controlador transaccional, política, inventario de 14 archivos, seis parsers embebidos de Rollup, pruebas y clasificación cerrada de severidades. No se adopta su instalación CI automática ni su eliminación de prehooks. No se cambia su lock revisado.
- El verificador acepta los nombres `postinstall`/`ignore-scripts` de la matriz auditada como alias de `project-hook`/`explicit-apply`, y comprueba todos los comandos de producto antes de aplicar las guardas. Se conservan los comandos nuevos R2 y la inspección del service worker en CI.

Las mitigaciones son restricciones temporales, no una corrección upstream universal. No se altera el baseline, los umbrales de Trivy, sus manifiestos requeridos ni la inclusión de dependencias de desarrollo. Las fechas y resultados de los informes previos pertenecen a sus cortes históricos; el resultado actual figura en `delivery/SECURITY_STATUS.md`, con logs y hashes.

No hay cambios de dosis, fórmulas, contratos, fuentes clínicas ni aprobación asistencial. T02 sigue pendiente de aceptación humana y el estado global permanece `CLINICALLY_PENDING`. Sin commits, push, merge ni despliegue. La auditoría externa y el delta R3 parcial no se consideran conciliados sin recibir sus bytes.
