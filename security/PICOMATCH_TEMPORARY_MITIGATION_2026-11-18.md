# Mitigación temporal local de picomatch — 18/11/2026

Estado: defensa local evaluada; **no es una corrección oficial ni cierra el aviso de Trivy**.
Base exacta: `af87ff815665884103689c771ac0807b751a5883`, árbol `469746c26b2495aaa36391eb3b0be83254c8f179`.
Alcance: herramientas de desarrollo de la copia aislada; núcleo internacional y perfiles clínicos sin cambios. Estado clínico conservado: `CLINICALLY_PENDING`.

## Decisión y funcionamiento

La [alerta oficial GHSA-fc5q-39xc-vjpf](https://github.com/advisories/GHSA-fc5q-39xc-vjpf), consultada el 18/11/2026, mantiene afectadas las versiones hasta 4.0.7 y no identifica versión corregida. Se conserva esa clasificación.

Se añade una comprobación mínima dentro de `extglobOpen` de `lib/parse.js`: si el propio analizador reconoce un extglob repetido `+(...)` o `*(...)`, lanza `SyntaxError` con código `ERR_PICOMATCH_REPEATED_EXTGLOB` antes de construir su expresión regular. No se devuelve un resultado falso que pudiera omitir recursos silenciosamente. La comprobación se aplica a las cinco copias instaladas de 2.3.2 y 4.0.7.

El instalador local valida inventario contra el lock, versión, rutas ordinarias dentro de `app/node_modules` y hashes SHA-256 de todos los archivos antes de escribir. Solo acepta bytes originales conocidos o los bytes exactos de la mitigación. No descarga código, no cambia versiones, no cambia integridades del lock ni crea excepciones de escaneo. La operación es idempotente, comprueba cada escritura y revierte las escrituras realizadas si falla una de ellas.

Se descartaron para esta evaluación: una excepción de Trivy (ocultaría el pendiente), una reescritura comunitaria no integrada oficialmente (mayor cambio semántico) y confiar solo en límites de tiempo (dejaría producirse el bloqueo). La restricción de sintaxis elegida es conservadora y verificable, con incompatibilidad explícita.

## Instalación reproducible y controles

Desde `app`, con Node y npm disponibles:

```text
npm ci --ignore-scripts --no-audit --no-fund
npm run security:picomatch:apply
npm run security:picomatch:check
npm run security:picomatch:test
npm test -- --maxWorkers=2
npm run lint
npm run build
```

Un `npm ci` normal ejecuta la aplicación por `postinstall`; el flujo con `--ignore-scripts` exige la aplicación explícita, incorporada en la copia local del workflow de seguridad. El workflow de App UI verifica y prueba la defensa. Los comandos habituales de desarrollo, compilación, pruebas, cobertura, lint y tipos tienen comprobaciones previas que fallan si la defensa falta. Esta integración se preparó y probó localmente; no se publicó ni ejecutó una nueva CI remota.

## Resultados locales observados

| Comprobación | Resultado |
| --- | --- |
| Controles originales 2.3.2 y 4.0.7, tres patrones por versión | 6 procesos llegaron al límite de 1.500 ms tras compilar; se terminaron de forma controlada |
| Pruebas específicas de mitigación | 6/6 PASS; cero omitidas |
| Compilaciones restringidas: cinco copias, APIs y opciones | 1.800 rechazos con el error esperado |
| Comparaciones de patrones habituales contra originales | 18.000 coincidencias de comportamiento |
| Reinstalación limpia sin scripts | PASS; comprobación y prebuild bloqueados hasta aplicar la defensa |
| Idempotencia y reversión | PASS; reversión restaura exactamente los hashes originales |
| Bytes/versiones desconocidos y enlace fuera de node_modules | Rechazo comprobado sin sobrescritura del contenido inesperado |
| Pruebas de la aplicación | 445/445 PASS |
| Lint y compilación, incluido TypeScript | PASS |
| Comparación de compilaciones antes/después | 26/26 archivos idénticos byte por byte |

Los resultados y metadatos finales de Trivy se conservan en el informe externo de esta evaluación; su política, clasificación y bloqueo no se relajan por esta defensa local.

## Limitaciones y retirada

- Se rechazan también extglobs repetidos válidos, por ejemplo `+(a|b)`. Una dependencia futura que necesite esa sintaxis fallará de forma visible. No se asegura compatibilidad universal.
- Se evalúa la ruta de análisis de globs de las dos versiones y cinco copias inventariadas. No se afirma protección general frente a todos los ReDoS, expresiones regulares recibidas directamente, estados de analizador fabricados u otras bibliotecas.
- Una instalación con scripts desactivados queda sin defensa hasta ejecutar `security:picomatch:apply`. Las invocaciones directas ajenas a los comandos npm protegidos pueden saltarse las comprobaciones previas. Los archivos instalados actualmente sí están comprobados.
- Se requiere una instalación completa de desarrollo acorde al lock; una instalación parcial o versión distinta se rechaza en vez de parcharse automáticamente. Un cambio de hashes requiere revisión explícita. No se protege frente a un escritor hostil concurrente con acceso al mismo directorio.
- El reconocimiento de Trivy sigue siendo por versiones/manifiestos. Un parche local no convierte estas versiones en oficialmente corregidas y **no autoriza a quitar su bloqueo**.
- `npm run security:picomatch:revert` restaura los bytes originales para diagnóstico; después las comprobaciones previas deben fallar. Para volver al estado completo anterior se utiliza otra copia de la base conservada, no se sobrescribe el candidato original.
- Cuando exista una versión oficial corregida: verificar publicación y aviso, actualizar la resolución del lock, retirar conjuntamente la defensa y sus hooks, repetir las pruebas y Trivy. No mantener esta mitigación indefinidamente ni declarar el CVE cerrado solo por los ensayos presentes.
- No se repitieron pruebas clínicas Python ni la revisión visual de PDF porque no cambian sus fuentes, cálculos, contenido ni resultados compilados. No se ha ejecutado Sonar sobre este nuevo árbol: su aprobación anterior pertenece a la base, no a esta propuesta.

La validación técnica local no constituye validación clínica ni despliegue. El informe externo identifica las limitaciones y el estado real de Trivy, sin atribuir aprobación remota a esta copia.
