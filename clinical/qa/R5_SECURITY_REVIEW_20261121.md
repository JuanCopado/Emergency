# R5 · Revisión de seguridad de presentación e imagen · 21/11/2026

Estado global **CLINICALLY_PENDING**. Base internacional `95c5f25f755e27628baf8e5f69f60df2b308ea92`, árbol `8dae69dad71b0b917a2caa35b81a286e4bbf5c74`, tras PR60. El cambio afecta al formato de prosa de fuentes en informes agudos. Los datos de fuente, cálculos, controles clínicos y revisión de imagen quedan en su alcance previo.

## Hallazgo y corrección

SonarQube Cloud registró `AaH-diiRI9bv3GTIgPaA`, `python:S8786`, MAJOR, abierto en `clinical/scripts/acute_medication_api.py:238` de la rama internacional. Los datos de PR60 mostraban cero incidencias en su alcance de análisis. La incidencia abierta corresponde al análisis de rama. [Incidencia en SonarQube Cloud](https://sonarcloud.io/project/issues?id=JuanCopado_Emergency&issues=AaH-diiRI9bv3GTIgPaA&open=AaH-diiRI9bv3GTIgPaA)

`_report_prose` reconoce el prefijo de apertura o cierre de bloque y comprueba por separado el texto tras el marcador. Al eliminar la captura del resto de la línea y el anclaje final, el motor de expresiones regulares deja de encontrar distintas particiones entre el marcador y el resto. Se conservan el carácter del delimitador, su longitud mínima y la presencia de texto en un posible cierre. La regresión permanente comprueba líneas CRLF, cierres de longitud mayor, espacios y tabulación finales, y delimitadores cortos, mixtos o seguidos de texto dentro del bloque.

El hallazgo es técnico y afecta a la fiabilidad de presentación. La verificación del cierre requiere un nuevo análisis Sonar sobre el candidato publicado. No se ejecutaron pruebas de agotamiento de recursos.

## Comprobaciones locales en Windows

| Verificación | Resultado |
|---|---|
| Suite `test_acute_medication_v144.py` | 19/19, con exportación fiel, condiciones de fallo cerrado, casos nominales y regresión de bloques literales. |
| Comparación con la función del commit base | 230 fragmentos sintéticos ordinarios, cero diferencias de texto. Incluye delimitadores válidos y no válidos, enlaces y distintos saltos de línea. |
| M10, clases focales T2–T6, T8 y cinco casos de T7 | 43/43 con Python 3.12.14 y Pillow 13.0.0. Incluye proveedor simulado, abstención, error de respuesta sin reflejar datos, términos reconocidos de falsa tranquilidad, exclusión de contenedores, orientación, metadatos y nombre de archivo. |
| `git diff --check` | Sin errores. |

Recibos externos al repositorio: `B-acute-tests-completed.log`, `B-prose-equivalence.log`, `B-m10-media-tests.log` y `B-open-issue.json`. La ejecución M10 usó el entorno local que ya tenía Pillow. No hubo proveedor real ni datos de pacientes.

## Revisión independiente

Claude Code web, modelo Sonnet 5.5 Alto, en sesión autenticada de R5. Progreso observado al preparar este commit: «Estado: verificado SHA/árbol, S8786 evaluado (equivalencia 0 diferencias). Ahora reviso M10: guarda, adaptador y API en el candidato». Revisión M10 y dictamen final pendientes en este corte. [Sesión de Claude Code](https://claude.ai/code/session_01VWLTZ9itT8ZY4qGMZQKZ9U)

Los controles M10 se conservan en [el seguimiento técnico](M10_TECHNICAL_FOLLOWUP_20261121.md). El filtro lingüístico cubre expresiones reconocidas. La revisión de identificadores visibles y la suficiencia de la imagen corresponden al profesional. Este alcance técnico no mide rendimiento diagnóstico ni autoriza despliegue.
