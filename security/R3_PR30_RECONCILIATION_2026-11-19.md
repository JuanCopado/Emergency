# Conciliación técnica R3 y PR30

Petición del propietario: conciliar si no existía otro trabajo activo. El responsable de R3 confirmó que no estaba conciliando y conserva su candidato/ZIP. Se trabaja en copia nueva, con objetos Git propios y reconstrucción offline verificada.

| Entrada | Identidad |
|---|---|
| R3 original | árbol79ac7d234010f7d1174bcc64bac5e9e3e1e0ce81;1111archivos |
| ZIP original | SHA2569b41c96c162fac753ccbedd51d11015d340b5d7a4c6371c8bdf417adb0377e68 |
| PR30 | commit1d628f81247d55bcfce9399fcf16875d276107f6; árbolae2ed3f56b003c2791638d04f8271b8e9f69037f |
| Base común de comparación | a1a1ae245d03662fff2508804c7c1112a0e238a9 |

## Resolución

Git merge-tree conserva los cambios propios de R3 y aporta los nueve archivos de PR30. El único conflicto es clinical/CHANGELOG.md: se antepone la entrada técnica PR30 al changelog R3 completo, sin descartar ninguna entrada. En security-and-quality se conserva el workflow R3 y solo se añade la exigencia de TLS; no se cambian thresholds, referencias, baselines, exclusiones o avisos.

clinical_note_api.py, http_transport.py y los tres tests HTTP son idénticos a PR30. Sus16funciones de negocio/dispatch son iguales a R3; solo cambia el arranque y transporte. En esa primera composición, app/src (incluido Q5), módulos, datos, referencias clínicas y QAJSON permanecían idénticos al árbol R3 original. No se concilian las once decisiones clínicas pendientes como si estuvieran aprobadas.

## Ajustes mínimos tras Sonar del compuesto

La primera composición bb6eb05ca18bda4fbec56d6268b24841ec570599 pasó los quality gates de rama y PR, pero Sonar señaló tres avisos de mantenibilidad. Se conservan esas evidencias. En Calculator.tsx se sustituye exclusivamente el valor global NaN por Number.NaN en dos fallbacks de presentación, con el mismo valor IEEE754 y sin cambiar la expresión, el formato ni el cálculo. Es la única diferencia nueva en app/src frente a R3. Los módulos, datos, referencias clínicas, CSS y estados de validación siguen idénticos. El registro de casos compartidos de build-dependency-guard.test.ts pasa por una llamada explícita it(name, run): mismos casos/callbacks/opciones, reconocibles por el analizador; no se añade una prueba vacía ni se elimina cobertura. Se repiten frontend, tipos, lint, construcción y CI/Sonar sobre el nuevo árbol, sin suppressions ni cambios de configuración.

## Verificación y entrega

La entrega identifica el nuevo árbol/commit y contiene matriz de conciliación, manifiesto y replay independiente. Las pruebas de QA, frontend, transporte, PM03, exportaciones y seguridad deben corresponder al compuesto. Sonar se ejecutará sobre una rama aislada con la CI configurada del proyecto: el resultado de PR30 no se traslada a R3. La publicación técnica de una rama/PR de revisión no es incorporación de R3 a la rama internacional ni release.

La impresión nativa Q5 se coordina con el responsable de su tarea separada, sin UI concurrente. Su resultado solo se incorpora como evidencia nueva si identifica exactamente el árbol/código probado; en caso contrario se mantiene como evidencia anterior con su alcance.

## Cierre técnico Q5 en la PR31

El candidato `f3b08fd3008ce8f259e23499edc25a29f8c5f8c6` superó la prueba nativa de dosis y unidad en Edge con tres casos sintéticos, 31 páginas y 449 párrafos. En el caso A, el título «Procedencia» quedó en la página 9 y su campo pasó a la 10. Su evidencia está en `EMERGENCY_Q5_PR31_CIERRE_20261119.zip`, SHA-256 `83020a4895baaa7fd0ce17bcc6fe2c48cb2471591faaf385638c721e020c752d`.

El commit de paginación `7c106cae6c0b331e0521bb600478403f05ca8551` incorpora el CSS de `c3f1ab9851e5fedfb4e0989c67b9ead9fc091f9d` sobre la cabecera `c6b6d909bcddd542a952de6a5ba09e951167cbc6`. La prueba usó la aplicación compilada de ese commit y el diálogo «Imprimir resultado» de Edge 157.0.4341.60 en Windows, con A4 vertical, escala 100 % y márgenes predeterminados. Los resultados de cálculo y los párrafos esperados proceden de las mismas cuatro fichas ejecutadas sobre la cabecera previa al parche.

| Caso sintético | Páginas | Párrafos en orden | Página de dosis y unidad | Página de «Procedencia» y su campo | SHA-256 del PDF nativo |
|---|---:|---:|---:|---:|---|
| A · Solo dosis | 9 | 130 | 1 | 9 | `422cd29909844c0ffc39f70e1a7408c19e67bbd8efb93a4077a7ccd770baa20b` |
| B · Preparación | 10 | 165 | 1 | 10 | `2a62b38bb9362d6c68200667fcfd44ea5a368c44af8f13e673e4834822b24d7d` |
| C · Dosis decimal | 11 | 154 | 2 | 11 | `e627d1d44ce640086f948c3dd125a0a308f1c9aec24fc6a6733b8408b42c68ba` |
| D · Reversión | 17 | 139 | 1 | 17 | `caca1dba225800858d13a7a73e7804e8ca1f2471d2d6a99afeaf891217a5440c` |

**Q5 aprobado para la impresión nativa a PDF.** Se conservaron los 588 párrafos de las 47 páginas. Cada título de sección comparte página con el inicio de su contenido. La dosis y la unidad ocupan líneas consecutivas en los cuatro casos, incluidas las dos últimas líneas de la primera hoja de B y las dos primeras de la segunda hoja de C. El resultado se limita a los casos, el navegador y el destino de impresión probados. El estado clínico sigue siendo `CLINICALLY_PENDING`.

## Estado clínico y límites

CLINICALLY_PENDING y NO_GO_RELEASE clínico permanecen hasta sus procesos de aceptación. Conservar el candidato/ZIP originales y los resultados de fallos, sin presentar auditorías, certificados o revisiones no ejecutados. No se cambian main, líneas cerradas, cálculos o contenido clínico. Las limitaciones de transporte/CLI y PM03 conservadas en PR30 siguen documentadas.
