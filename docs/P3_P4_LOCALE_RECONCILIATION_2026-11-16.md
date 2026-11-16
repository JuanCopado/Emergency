# P3 / P4 — entrada numérica y mensajes de interfaz

Fecha: 16/11/2026. Base: `062d890b4fc92369b83c87664bb4bb0205ccb33f` (`codex/v144-international-scope-20261116`). Rama aislada: `codex/v144-p3-p4-locale-20261116`.

## Resultado y alcance de revisión

- **P3: IMPLEMENTADO, pendiente de aceptación/integración.** La decisión del propietario sustituye la propuesta histórica de convertir todos los separadores en coma. La entrada numérica usa punto, sin agrupación; la salida usa el idioma de interfaz. Cambiar idioma no selecciona país, hospital ni pauta.
- **P4 de interfaz: IMPLEMENTADO, pendiente de aceptación/integración y revisión lingüística.** 278 entradas estáticas en español, inglés, portugués y chino, integradas en `clinicalUi` para agudos, pediatría ambulatoria, exportación pediátrica, nota clínica y el visor de valores. Se resuelven localmente al mostrar la interfaz; no hay traducción remota de casos.
- **Traducción clínica integral: NO COMPLETADA.** Guías, etiquetas y mensajes arbitrarios del backend, alertas canónicas, contenido aportado por el clínico y documentos JSON/PDF/DOCX conservan su idioma y sus valores originales. La interfaz lo indica expresamente. La traducción de la interfaz no acredita equivalencia clínica de esos documentos ni sustituye una revisión profesional.
- **Navegador real: NO VERIFICADO.** Chromium abortó antes de ejecutar casos: `socket() failed: Operation not permitted`. Se entrega `npm run i18n:browser-check` para reproducir las comprobaciones con datos sintéticos en un entorno que permita arrancarlo.
- No se ha hecho merge ni desbloqueo clínico. No se modifican dosis, fórmulas, contratos farmacológicos, fuentes o fechas de evidencia. Permanecen 19 contratos bloqueados, 117 módulos GREEN / 14 YELLOW y `CLINICALLY_PENDING`.

## Contrato de números

| Idioma de interfaz | Entrada | Valor numérico para cálculo/API | Salida |
|---|---|---:|---|
| Español | `0.1` | `0.1` | `0,1` |
| Portugués | `0.1` | `0.1` | `0,1` |
| Inglés | `0.1` | `0.1` | `0.1` |
| Chino simplificado | `0.1` | `0.1` | `0.1` |

China utiliza punto decimal en el formato estándar `zh-CN`; fuente primaria: [Unicode CLDR 48 — Chinese, Numbers/Symbols/decimal](https://www.unicode.org/cldr/charts/48/summary/zh.html). Se mantiene la convención del idioma en lugar de atribuirle erróneamente una coma.

- `1000.5` se presenta como `1000,5` o `1000.5`; no se añaden separadores de miles.
- `1,000`, `0,1`, `1 000`, formatos mixtos, hexadecimales y valores no finitos no se reinterpretan como otro número. Se rechazan donde se introducen datos numéricos.
- `1.000` significa uno según el contrato de entrada; para mil se escribe `1000`. La ayuda visible explica punto decimal y ausencia de agrupación.
- Las cadenas de salida localizadas nunca se vuelven a usar como entrada de cálculo ni se envían en lugar de números JSON.
- `formatCanonicalNumber` conserva la representación numérica de JavaScript sin añadir redondeo a resultados canónicos, incluidas estructuras anidadas; no se recuperan cifras que ya se hayan perdido antes de recibir el número.
- Los redondeos de presentación ya existentes (p. ej. bomba a una decimal) conservan su alcance. Las fórmulas y la precisión interna no cambian.
- Infusiones, agudos, pediatría, nota clínica e insulinoterapia de simulación usan entradas con punto. Los formularios de scores ya lo exigían; el visor común ahora localiza sus valores numéricos.
- La edad inválida impide construir/enviar la nota, analizar, aceptar una prueba o exportar; los signos vitales inválidos no se guardan como `null` silenciosamente.

## Traducción y seguridad

Las claves de lenguaje natural están en un namespace específico; `keySeparator:false` y `nsSeparator:false` evitan que puntos o dos puntos alteren su resolución. Los valores son recursos versionados, con cambio automático al seleccionar idioma. Se comprueban igualdad de claves, ausencia de vacíos, variables y preservación de `STOP`, `YELLOW` y `CLINICALLY_PENDING`.

Las validaciones no toman decisiones por la traducción. Booleanos siguen siendo booleanos; IDs, enumeraciones, selección de pauta, revisión de fuente, rechazo de resultados antiguos, confirmación y controles de exportación conservan sus contratos. Textos clínicos desconocidos no se traducen por sustitución o inferencia.

Las traducciones se han preparado con asistencia de IA. No se atribuye revisión humana profesional ni validación clínica del chino, inglés, español o portugués. Las pruebas de igualdad estructural no prueban equivalencia semántica.

## Verificación observada

| Comprobación | Resultado |
|---|---|
| Regresiones iniciales antes de corregir | 17 FAIL / 16 PASS: reproducen ambigüedad numérica y ausencia de traducción/recorridos |
| Suite frontend final | **488/488 PASS** en 16 archivos; después de reforzar la aserción de no-envío se repitieron las 14 regresiones de idioma/seguridad, **14/14 PASS** |
| Lint / TypeScript / build | **PASS / PASS / PASS** tras la última corrección; build mantiene aviso no bloqueante de tamaño de chunk |
| Clinical QA ejecutado sobre esta base sin cambios de backend | **7/7 PASS; 740 pruebas Python PASS** |
| Revisión técnica independiente | Agente revisor con contexto separado: hallazgo de edad inválida corregido y revisado; **sin hallazgos importantes pendientes en este alcance**. No se ejecutó Claude Code ni Gemini |
| Chromium | **NO EJECUTADO**: fallo de arranque antes del primer caso |
| Revisión lingüística clínica profesional | No realizada |
| CI remoto | No verificado en esta entrega |

La base ya tenía cinco fallos frontend: tres de fidelidad de guías generadas desactualizadas y dos expectativas de Home/About anteriores a la internacionalización. Se reprodujeron sin cambios en una copia de la base. Se regeneró `generatedClinicalGuides.json` a partir de las fuentes canónicas vigentes y se actualizaron esas expectativas. Esta regeneración no es una nueva traducción ni una modificación de las guías originales.

Comandos: `npm ci --no-audit --no-fund`, `npm test -- --reporter=dot`, `npm run lint`, `npm run typecheck`, `npm run build`, `python3 clinical/qa/qa_runner.py` (desde `clinical`, `python3 qa/qa_runner.py`). El browser-check debe ejecutarse después de build.

## Decisión del propietario

Revisar este candidato y las traducciones, aceptar la política de entrada/salida y decidir su integración en la línea de internacionalización. La aceptación técnica de P3/P4 de interfaz no libera contratos farmacológicos, no promueve evidencia y no constituye autorización global de uso clínico. El antiguo NO-GO de traducción clínica completa no se presenta como resuelto por añadir recursos de interfaz.
