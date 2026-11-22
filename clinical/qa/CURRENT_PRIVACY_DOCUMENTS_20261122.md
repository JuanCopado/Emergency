# Correcciones técnicas de privacidad e importación de texto

- Fecha: 2026-11-22.
- Base: `0e68e5ee654e7be452cbb7cb5e5fb22b8b1127ed`.
- Rama de trabajo: `codex/current-privacy-documents-20261122`.
- Alcance: fallos actuales de importación y detección técnica de identificadores, con datos sintéticos.

## Cambios y contrato

### Texto importado completo o rechazo explícito

`clinical_note_api._extract_text` deja de recortar silenciosamente el texto a `MAX_TEXT_CHARS`. Acepta hasta 120.000 caracteres decodificados, conservando el último carácter. Si se supera ese límite, lanza `TextUploadTooLarge` antes de ejecutar el detector de privacidad.

La ruta `/api/clinical-note/upload/prepare` convierte esa excepción en HTTP 422, sin documento parcial ni datos del texto o del nombre de archivo en el error. El contrato incluye `error_code: text_upload_too_large` y `max_text_chars: 120000`, además de un mensaje público fijo. El cliente muestra una explicación en ES/PT/EN/ZH que indica que no se ha importado contenido y pide dividir y revisar cada parte. El manejador HTTP no se modifica en este cambio.

Se preservan la detección de codificación existente, el tratamiento del BOM, la ruta de archivos no textuales y la firma del documento preparado dentro del límite.

### Detección de correo de coste lineal

La regla de correo de la política predeterminada usa `email_shape_linear` en lugar de la búsqueda por expresión regular que podía volver a recorrer sufijos largos. El detector busca cada `@` una vez y examina hacia delante su segmento de dominio. Un `@` termina el segmento anterior, de modo que esos recorridos no vuelven a examinar el mismo dominio por cada prefijo de texto.

Se conserva la forma útil de detección anterior, incluidos sus caracteres y la equivalencia de mayúsculas de Python, mediante casos positivos y negativos representativos. No es un validador RFC de direcciones. Las políticas con reglas `pattern` siguen siendo compatibles; un identificador de detector desconocido produce un error explícito.

La prueba de coste cuenta visitas al texto y longitudes recorridas por `find`, sin umbral de tiempo dependiente del equipo. Verifica cuatro familias de entradas sin coincidencia, con tamaños de referencia 2.000, 4.000, 8.000 y 16.000: texto sin `@`, dominio largo sin sufijo, muchos `@` y sufijos repetidos de una letra. En las 16 combinaciones el trabajo instrumentado es como máximo `6 × longitud + 10`. Esta comprobación focal y la estructura del algoritmo sustentan el coste lineal del detector de correo; no constituyen una medición de rendimiento de toda la aplicación.

### Etiquetas de identificación en los idiomas existentes

La política de servidor y el detector local amplían las etiquetas de nombre, teléfono, dirección e identificador de ES/PT/EN/ZH. Los casos incluyen `Nombre`, `Paciente`, `Nome`, `Doente`, `Name`, `Patient` y `姓名`, junto con variantes actuales razonables. Los nombres requieren una etiqueta delimitada, y las pruebas negativas incluyen frases clínicas corrientes sin etiqueta de identificación.

La interfaz sustituye el estado positivo «Privacidade local OK» por «Sem identificadores detetados localmente», con estilo neutro, y explica que la comprobación automática tiene alcance limitado. La revisión manual y los controles de aceptación/exportación existentes permanecen activos. La detección local de etiquetas no tiene la misma cobertura que la política del servidor y no sustituye su revisión.

## Verificación focal observada

Todos los datos de prueba son sintéticos. No se usa ningún servicio externo ni se guardan documentos clínicos.

| Comprobación | Resultado final |
| --- | --- |
| `python -B -m unittest discover -s clinical/tests -p test_privacy_document_guardrails.py -v` | 11/11 PASS |
| `python -B -m unittest discover -s clinical/tests -p test_skill.py -k privacy -v` | 11/11 PASS |
| `python -B -m unittest discover -s clinical/tests -p test_clinical_note_http_privacy.py -v` | 9/9 PASS |
| Desde `app`: `npm test -- src/test/clinical-note-privacy.test.tsx src/test/image-review.test.ts src/i18n/clinical-ui.test.ts src/test/locale-safety.test.tsx` | 57/57 PASS, 4 archivos |
| Desde `app`: `npm run typecheck` | PASS |
| Desde `app`: `./node_modules/.bin/eslint src/pages/ClinicalNote.tsx src/clinical-note/privacy.ts src/clinical-note/imageReview.ts src/test/clinical-note-privacy.test.tsx` | PASS |

La prueba nueva de Python cubre exactamente 120.000 y 120.001 caracteres, el rechazo previo al escaneo, la respuesta segura 422, Unicode/BOM, texto completo con un correo al final, etiquetas multilingües, controles negativos, compatibilidad del detector de correo y su cota de trabajo. Las 26 pruebas nuevas de interfaz comprueban etiquetas positivas y negativas, el estado local limitado, el bloqueo de exportación y el error traducido en los cuatro idiomas. Los otros 31 casos de interfaz y los 20 casos Python existentes son regresiones focales.

## Límites y alcance preservado

Estas reglas detectan patrones de identificadores y pueden presentar falsos positivos o no detectar otros formatos. No garantizan anonimización universal ni autorizan el envío de datos identificativos. Tampoco cambian diagnósticos, pesos, reglas M10, decisiones de abstención, fuentes clínicas, módulos o estados de aceptación. La revisión del propietario y las decisiones clínicas pendientes conservan su alcance.

Los resultados son pruebas técnicas locales en Linux. No equivalen a validación clínica, QA nativa de Windows, prueba de lectores de pantalla, CI remoto ni certificación de despliegue. No se ejecutó una suite masiva para esta corrección focal.

## Revisión focal: compatibilidad del espacio al pegar texto

Base de esta revisión: `68a8a94f88b26222632fc87df365247a28af90ff`; la verificación inicial anterior corresponde a ese commit. La revisión independiente encontró que cambiar `\s*` por `[ \t]*` había perdido detección con NBSP y saltos de línea antes de `:`. Se restaura `\s*` en las etiquetas locales y en nombre/dirección del servidor, sin añadir etiquetas. En dirección se agrupa el delimitador opcional con su espacio posterior para evitar dos cuantificadores de espacio contiguos cuando no hay delimitador.

RED observado antes de corregir: la prueba Python `-k pasted_whitespace` falla en 12 de sus 16 subcasos; Vitest `-t pasted` falla en los 16 casos nuevos. Cubren nombre y dirección con NBSP y salto de línea en ES/PT/EN/ZH. GREEN después: `python -B -m unittest discover -s clinical/tests -p test_privacy_document_guardrails.py -v`, 12/12 PASS; desde `app`, `./node_modules/.bin/vitest run src/test/clinical-note-privacy.test.tsx`, 42/42 PASS; ESLint de `privacy.ts` y su prueba, PASS. Se mantienen los controles negativos, el límite de texto y la prueba de coste del detector de correo. Solo datos sintéticos.
