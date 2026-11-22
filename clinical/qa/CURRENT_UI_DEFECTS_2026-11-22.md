# Correcciones de fallos actuales de interfaz · 22/11/2026

## Alcance y base

Base: `0e68e5ee654e7be452cbb7cb5e5fb22b8b1127ed`. Rama de trabajo: `codex/current-ui-20261122`.

Esta entrega corrige cuatro problemas de funciones existentes: pérdida del borrador al navegar, familias de referencia anunciadas como futuras, controles de scores/importación sin localizar e identidad de la aplicación confundida con la versión del catálogo adulto. Mantiene el alcance internacional: el idioma de interfaz no selecciona país ni hospital.

No modifica fórmulas, recomendaciones, fuentes, estados de evidencia o aceptaciones clínicas. No implementa T06 multiplataforma, nuevos proveedores, integraciones hospitalarias ni otros procesos pendientes.

## Cambios y límites

### Borrador de nota

- `ClinicalNoteDraftProvider`, por encima de las rutas de `App`, conserva un único episodio en memoria de la pestaña. Guarda campos, constantes, tarjetas MCDT, revisión y resultados; no usa `localStorage`, `sessionStorage` ni un almacén global de pacientes.
- «Nueva nota» solicita confirmación cuando hay contenido, borra el episodio completo y crea un identificador nuevo. Desmontar la aplicación también descarta el borrador. El aviso visible explica esta duración; `beforeunload` solicita al navegador el aviso nativo al cerrar o recargar con contenido. El navegador controla si presenta ese aviso: no es recuperación tras cierre, caída o recarga.
- Las respuestas de una vista desmontada o de otro episodio no escriben en el borrador. Los estados de operación en curso y errores son locales a la vista; volver a ella permite reintentar una aceptación pendiente. Un resultado de exportación recibido después de salir no inicia una descarga.
- El idioma de la nota forma parte de la sesión. Cambiarlo fuera de la ruta invalida al volver la revisión médica, igual que un cambio de idioma dentro de la ruta.

### Inicio y referencias

- El generador existente produce una proyección pequeña de navegación, con **12 grupos y 131 guías** del catálogo canónico actual. Home presenta sus conteos y enlaces a la biblioteca filtrada por bundle.
- Se elimina de Home la presentación de esas familias como «Próximamente». Se describen como guías de referencia y cada módulo conserva su estado propio; esto no declara una calculadora para cada guía ni promueve estados clínicos.
- La proyección completa `generatedClinicalGuides.json` no cambia. Las pruebas comparan el índice, los estados y el contenido con sus fuentes y comprueban los conteos de navegación.

### Scores e importación

- Los controles, instrucciones operativas, estados y errores de interfaz de `ClinicalScores` y `ScoreDocumentInput` se localizan en ES/PT/EN/ZH.
- Los nombres, etiquetas clínicas, opciones, unidades, texto fuente y resultados canónicos se conservan. Los bloques de fuente se identifican como tales; la interfaz explica que no es una traducción clínica integral. Los detalles de errores del servicio siguen disponibles bajo un mensaje localizado.
- Los metadatos de número de página y bloque permiten actualizar las etiquetas del importador al cambiar de idioma sin volver a extraer el documento ni alterar líneas, valores, unidades o selección de muestra.
- La lógica de candidatos, la aritmética del backend, los límites de PDF y las reglas de selección no cambian.

### Identidad

- Pie, Ajustes y Acerca de distinguen la versión de la aplicación y su revisión Git del **catálogo de perfusión adulta v1.35**.
- Vite lee HEAD y el estado del árbol al iniciar la compilación. Un árbol modificado se identifica con «cambios locales sin confirmar»; una copia sin información Git muestra «Identidad no disponible». No se asigna un SHA inventado ni se presenta HEAD como descripción exacta de cambios sin confirmar.
- Esta identidad describe las fuentes de la compilación; no es una firma de distribución ni una acreditación de despliegue.

## Verificación observada

Entorno: Linux de desarrollo, dependencias exactas del lock y mitigación de dependencias ya preparada. Datos y documentos de pruebas sintéticos.

| Comprobación | Resultado |
| --- | --- |
| RED anterior a cambios: navegación, Home y cuatro idiomas | 7 fallos / 1 éxito; la ida nota → gasometría → nota devolvía vacío el motivo sintético |
| Tanda principal de UI afectada | 94/94, 12 archivos |
| Pruebas del importador de documentos | 3/3 |
| RED de cambio de idioma fuera de la nota | Revisión médica permanecía marcada; fallo reproducido antes del ajuste |
| Repaso final de navegación, exportación e idioma de nota | 17/17, 3 archivos; incluye el nuevo caso de idioma fuera de ruta |
| Casos UI únicos verificados entre esas tandas | 98, 13 archivos; no se ejecutó toda la suite del repositorio |
| `npm run guides:test` | 12/12 |
| `node scripts/build-clinical-guides.mjs --check` | PASS; 131 guías y proyección de navegación vigentes |
| `npm run typecheck` | PASS |
| `npm run lint` | PASS, sin avisos de ESLint |
| `git diff --check` | PASS |
| Detector estático Impeccable sobre las cinco superficies afectadas | `[]`; no equivale a auditoría WCAG o prueba visual de navegador |

La prueba de navegación usa las rutas reales de `App` y el enlace real de la nota. Sustituye el cuerpo de Gasometría por un enlace de retorno sintético: acredita el ciclo de vida del borrador, no la extracción de gases. Comprueba persistencia del mismo episodio, ausencia de texto clínico en almacenamiento del navegador, borrado deliberado, nuevo ID, respuestas tardías, rearme de aceptación y cambio de idioma.

No se ejecutaron en este lote un build de distribución, capturas de navegador, el backend completo, pruebas con pacientes, Windows ni una validación clínica prospectiva. El build y la integración entre lotes pertenecen a la entrega compuesta. Se mantiene `CLINICALLY_PENDING` donde corresponde.

## Integración

`ClinicalNote.tsx` coincide con el lote paralelo de privacidad en el mismo archivo, pero esta entrega no modifica su regex ni los mensajes del detector. `vite.config.ts` coincide con el lote de HTTP: conservar tanto el cálculo de identidad como sus controles de servidor. No se modifican los archivos comunes de estado en esta rama de lote.

## Delta C13 · aceptación de MCDT y respuestas obsoletas

Base del delta: `96bb58ee06a4426fd01cff9646ee0397a86663d9`.

Una revisión independiente identificó un fallo previo de integridad: mientras `/upload/accept` esperaba, era posible editar o rechazar la tarjeta enviada, o editar otra tarjeta ya aceptada. La respuesta instalaba las colecciones completas de informes y timeline de la nota antigua y marcaba la tarjeta actual como aceptada. Podían quedar un texto visible nuevo y un informe aceptado antiguo, o reaparecer un informe retirado de otra tarjeta.

El delta captura la revisión de la nota antes de enviar la aceptación y comprueba, antes de aplicar la respuesta, que la vista continúa activa y que la revisión no ha cambiado. La revisión global cubre también las demás tarjetas porque el endpoint devuelve colecciones completas de la nota enviada. Una respuesta obsoleta se descarta; se conservan los cambios/rechazos actuales y el botón vuelve a permitir una aceptación explícita. Los errores de una solicitud obsoleta tampoco sustituyen el estado actual. No se cambia el contenido clínico ni el contrato del backend.

Pruebas nuevas en `clinical-note-acceptance-integrity.test.tsx`: edición de la tarjeta enviada, rechazo de esa tarjeta, edición de otra tarjeta aceptada y control positivo sin cambios. Además del estado visible y timeline, comprueban los informes que recibe una operación posterior de la nota, para detectar restauraciones silenciosas de las colecciones antiguas.

- **RED:** 3 fallos y 1 éxito antes de la guardia; los tres casos de cambio terminaban indebidamente aceptados.
- **GREEN:** 16/16 en aceptación, navegación y exportación (3 archivos).
- `npm run typecheck`, `npm run lint` y `git diff --check`: PASS.
- Datos sintéticos y APIs simuladas. No se amplió la suite general ni se repitió el build de distribución.

## Delta de seguridad C09 · identidad de compilación

Base del delta: `a574ed4787b53b0c98d67c97d06be4f151ffbc9c`.

La consulta de Git de `vite.config.ts` buscaba el ejecutable en `PATH`. Las pruebas previas a la corrección reprodujeron la ejecución de un homónimo sintético colocado al principio de esa variable. También reprodujeron la ejecución de un monitor de archivos configurado en el repositorio y dos identidades incorrectas: una copia sin metadatos que heredaba el SHA de su repositorio contenedor y variables `GIT_DIR`/`GIT_WORK_TREE` que dirigían la consulta a otro repositorio.

La consulta se extrae a `scripts/build-identity.mjs`, con ejecutables de rutas absolutas fijas (`/usr/bin/git` o `C:\Program Files\Git\cmd\git.exe`), `shell: false`, tiempo y salida acotados y un entorno explícito sin `PATH` ni redirecciones Git heredados. Se desactiva `core.fsmonitor` y la caché de archivos sin seguimiento para consultar el árbol actual. Se exige `.git` en la raíz solicitada y se conserva Git nativo para resolver referencias empaquetadas y worktrees. Una instalación de Git en otra ubicación, metadatos inválidos o el fallo de cualquier consulta producen «Identidad no disponible», sin inventar una revisión ni afirmar que el árbol está limpio.

La identidad continúa distinguiendo revisión de fuentes y cambios locales. Esto no es aislamiento de la compilación, firma de distribución ni certificación de un repositorio ajeno.

- **RED:** 4 fallos / 8 éxitos en 12 casos con repositorios temporales reales, antes de aplicar la corrección.
- **GREEN:** 15/15 en 2 archivos: 12 casos del helper y 3 de la etiqueta visible de identidad.
- Los casos verifican árbol limpio, modificación, staging, archivo nuevo, archivo ignorado, refs empaquetadas, worktree, copia sin `.git`, metadatos inválidos, redirección heredada, homónimo de `PATH`, índice corrupto y monitor configurado. Algunos casos comprueban más de una condición.
- `npm run typecheck`, `npm run lint` y `git diff --check`: PASS.
- Observado en Linux con Git nativo. No se ejecutó la rama Windows ni una instalación macOS; sus rutas no estándar conservan el fallback explícito. No se amplió la suite ni se repitió el build. La revisión de Sonar corresponde al siguiente SHA publicado de la entrega compuesta.
