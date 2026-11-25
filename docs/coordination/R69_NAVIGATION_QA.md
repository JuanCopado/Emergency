# R69 · Navegación pediátrica y falsos positivos de QA

Fecha: 24/11/2026. Repositorio JuanCopado/Emergency. Base receptora final:
`bba8827bad22b67d8c38cfd83558920a1bb52cd1`, tras PR103. La reproducción inicial
se hizo en `3b4f58b52fa7e0f1b75d0841cb5cac2b9f15a5a9`, rama
`codex/v144-international-scope-20261116`. Entrega aislada
`codex/r69-pediatric-navigation-20261124`.

## Causa raíz y reproducción

**El módulo pediátrico funciona en su ruta canónica `/pediatrics`.** R55 ensayó
`/pediatric-outpatient`, que no está registrada. También ensayó `/clinical-scores`
en lugar de `/scores`. No son enlaces actuales de la aplicación. Las rutas de API
`/api/pediatric-outpatient` y `/api/clinical-scores` son contratos distintos de las
rutas de interfaz y no deben usarse para deducirlas.

La aplicación usa BrowserRouter y fallback SPA. Vite devuelve index.html con HTTP
200 para una navegación no registrada; React muestra NotFound dentro de Layout.
Por eso título global, main, h1, ausencia de excepción y controles del marco no
demuestran que se haya cargado el módulo solicitado. El wildcard `*` tampoco
convierte un enlace desconocido en válido.

| Ruta ensayada sobre el receptor | HTTP | Encabezado real | Pautas visibles | Resultado semántico |
|---|---:|---|---:|---|
| `/pediatric-outpatient` | 200 | Página no encontrada | 0 | FAIL para pediatría esperada |
| `/clinical-scores` | 200 | Página no encontrada | 0 | FAIL para escalas esperadas |
| `/pediatrics` | 200 | Pediatría ambulatoria | 89 | Módulo correcto |
| `/scores` | 200 | Scores clínicos | N/A | Módulo correcto; el formulario requiere backend |

En las dos páginas no encontradas del receptor se observaron 18 controles genéricos
fuera del catálogo pediátrico; R55 declaraba 17 para escalas. No se equiparan versiones
distintas: el JSON R55 no identifica el SHA ni contiene el código de su generador.
Su incoherencia verificable es `heading=Página no encontrada` y `status=PASS` en
ambos navegadores. El generador externo no fue aportado; no se afirma haber editado
su archivo. Se entrega un verificador reproducible en repositorio y obligatorio en CI,
y se corrige el auditor de UI disponible que tenía la misma debilidad de identidad.

La fixture [R55 original](../../app/scripts/fixtures/r55-browser-accessibility-audit.json)
conserva sus bytes y sus PASS erróneos **solo como evidencia histórica negativa**.
SHA-256: `82e3934cfba7204054edf66854204cd83815aa3d4549e0ef39e98aa0d0ce17f3`.
No es un resultado aprobado de R69 ni una certificación de accesibilidad.

## Corrección concreta

- `route-identity.mjs`: 19 contratos funcionales independientes por patrón de ruta;
  rechaza HTTP no válido, ruta distinta, NotFound, encabezado incorrecto, controles
  específicos ausentes, overlay de framework o errores de navegador. No acepta
  `rendered=true`, `status=PASS` ni recuentos genéricos como evidencia suficiente.
- `check-route-identity.mjs`: observa el DOM real, espera la identidad/controles del
  módulo durante las transiciones de Suspense y devuelve FAIL o lanza ante identidad
  incorrecta. Esperar solo un h1 anterior podría mezclar una URL nueva con la pantalla
  anterior; el verificador espera el estado correcto y vuelve a leer el encabezado.
- `check-route-navigation.mjs`: usa rutas canónicas, compilación real y backend
  canónico, acceso directo, recarga, enlaces internos, vuelta y avance; inspecciona
  enlaces literales y todos los href internos materializados. Excluye el wildcard
  al comparar destinos contra el router y exige contrato para cada ruta registrada.
  Un módulo nuevo sin contrato hace fallar el preflight.
- El catálogo pediátrico compara exactamente los IDs de las 89 pautas y cada una
  de las 52 familias con el catálogo canónico; selecciona una pauta, abre su formulario,
  comprueba interacción y preservación de selección tras recarga. No se cambia pauta,
  concentración, fórmula, filtro clínico ni criterio de alta.
- El auditor `audit-ui-v143.mjs` incorpora el mismo gate para rutas esperadas válidas.
  Los controles negativos están rotulados `expected_valid=false`, nunca como PASS
  de un módulo válido. El nuevo runner escribe FAIL y sale con código 1 ante cualquier
  defecto, elimina resultados antiguos antes del preflight y registra SHA de fuente,
  compilación, commit, estado dirty y versión del navegador.
- CI ejecuta regresiones negativas, navegación real y publica el JSON de la ejecución
  incluso al fallar. No se añaden alias al router para ocultar las rutas erróneas de R55.

## Verificación observada

| Control | Resultado |
|---|---|
| R55 Edge y Chrome, fixture original | Sus falsos PASS son rechazados por las regresiones |
| Acceso directo, recarga, enlace, vuelta, avance | PASS en 19 patrones de ruta; incluye módulo y fichas dinámicas representativas |
| Estados positivos de navegador | 97 PASS, incluyendo catálogo y formulario móvil |
| Controles negativos | 7 `REJECTED_INVALID_ROUTE`: dos rutas R55, ruta inexistente y IDs desconocidos de fármaco, guía, módulo y procedimiento |
| Destinos de navegación | 510 enlaces internos únicos, todos registrados sin usar `*` |
| Catálogo pediátrico | 89 pautas / 52 familias; IDs y agrupaciones exactos; selección, formulario y recarga PASS |
| Regresiones negativas | 6 casos compartidos por node:test y Vitest; cubren también HTTP 404 con h1 correcto, datos ausentes, controles del marco, errores y overlays |
| Cobertura focal del helper de identidad | 100 % líneas, funciones y ramas; no es una cifra de cobertura global |
| Frontend | 1.042 pruebas PASS; lint, tipos y build PASS |
| Formulario pediátrico contra backend real | Cinco escenarios existentes PASS; sin modificar sus expectativas clínicas |
| Clinical QA del corte inicial 3b4f58b | PASS, 1.674 pruebas, 16 omitidas; todos los gates PASS; repetición post-PR103 y checks finales en recibo de la PR |
| CI y Sonar del SHA final | Consultar checks y recibo de la PR, sin heredar resultados de PR102/103 |

Flujo principal: Inicio → Pediatría → familia/pauta → formulario → recarga → regreso
y avance. Prueba de escritorio 1280×720 y formulario a 375×812; Chromium Linux
154.0.8037.57. El Browser skill estaba disponible, pero su herramienta de control
`js` no estaba expuesta: se emplea el arnés Playwright del repositorio para las
regresiones de navegador/CI autorizadas en R69. No se atribuye una nueva ejecución
nativa de Edge o Chrome Windows a estos resultados. El runner permite el ejecutable
instalado mediante `CHROMIUM_PATH`, sin descargar navegadores ni cambiar dependencias.

Gasometría usa su servicio local real para obtener la capacidad de sesión, evitando
confundir una composición incompleta del arnés con un defecto de navegación. La
extracción Windows y el transporte T06 se verifican en los gates nativos existentes;
no se simulan ni se certifican por mostrar sus pantallas. Sin certificación WCAG,
lector de pantalla ni extracción clínica nueva.

## PR102, PR103 y separación de R68/R64

PR102 está fusionada como `18de1f093b87ca41a939d1179b83929e7e9e3b14`.
En el receptor inicial 3b4f58b, las 30 fichas R54 coincidían con sus IDs y SHA del manifiesto.
PR103 se comprobó inicialmente abierta en `3db2867e1541260da942ff48445e6b91566c3209`
y se fusionó durante R69 como `bba8827bad22b67d8c38cfd83558920a1bb52cd1`:
su único estímulo cambiado es S2-09, de
`555d6c5717edac86b4b7a30352cca8638e52c3df1ac3c826493144ee8dbe0ce2`
a `e55d2d35203147e3f92c95c61e464a80dca4a28f08a7de495dd46648a21fa077`.
Los bytes físicos de PR103 verifican ese nuevo SHA. La ficha sucesora
`S2-09.r61.json` de R68, rama `codex/r68-recepcion-20261124` en
`8e917c4694a7b2fd9ea06b75e87f68c08f62ca59`, ya coincide con ese hash.

En el receptor post-PR103, los bytes y manifiesto nuevos coinciden, pero la ficha
histórica R54 de S2-09 conserva el hash anterior. No debe presentarse como ficha
del estímulo actual. La incorporación de la sucesora ya preparada queda en R68,
que no estaba fusionada en la base BBA. R69 señala esa dependencia explícita y
no reescribe la ficha histórica ni duplica la conciliación de R68. Tampoco
incorpora estímulos, modifica C12 o reimplementa entregas externas R64. No se encontró
un artefacto o rama R64 publicado en las fuentes consultadas; esta entrega se limita
a navegación e identidad funcional del QA, sin asumir el cierre de esa otra tarea.

## Checklist de entrega

| Requisito R69 | Evidencia |
|---|---|
| HEAD / PR102 / PR103 / receptor | Base y estados identificados arriba |
| Causa raíz / reproducción antes de corregir | Dos rutas erróneas y soft-404 reproducidos; fixture literal conservada |
| Router, enlaces, compilación frente a prueba | Router/enlaces canónicos correctos; corregidos datos y criterio del QA |
| Identidad funcional / negativos | Contratos de 19 patrones, siete controles negativos y seis regresiones |
| Acceso directo / recarga / interna / retorno | 97 estados observados, sin errores |
| Catálogo y otros módulos | 89/52 e inventario de 510 enlaces; controles propios por módulo |
| Manifiesto y fichas / no duplicar R68 | Cotejo de receptor, bytes PR103 y ficha sucesora R68; sin editar banco |
| Regresiones / frontend / Clinical QA / CI | Resultados locales arriba; checks remotos vinculados en PR |
| PR aislada / SHA / revisión Antigravity | Recibo final de la PR; sin fusión ni atribuir dictamen independiente |
| Restricciones | CLINICALLY_PENDING y NO_GO_CLINICAL_RELEASE; main/producción y contenido clínico intactos |

Reproducir tras `npm ci` y el postinstall habitual: `npm run build`,
`node --test scripts/route-identity.node-test.mjs`,
`ROUTE_QA_OUTPUT=/ruta/fuera/del/repositorio/navigation.json node scripts/check-route-navigation.mjs`.
En Windows, usar las variables de entorno equivalentes y la ruta del navegador
instalado. El arnés requiere Python y los requisitos clínicos fijados del proyecto.
