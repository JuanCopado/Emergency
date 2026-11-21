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

## Dictamen independiente de Claude Code

**Resultado del 21/11/2026.** Claude Code web autenticado, `claude-sonnet-5-5` (Sonnet 5.5 Alto, modelo configurado y servido según el revisor). Verificó con Git el commit base y el árbol indicados y trabajó sobre una copia desechable extraída con `git archive`. Recomendó integrar el candidato inspeccionado y consideró equivalente la corrección S8786. No encontró P0 ni P1 en su alcance. La respuesta original y su adjunto `R5_AUDITORIA_M10_95c5f25.md` están en la sesión. [Sesión de Claude Code](https://claude.ai/code/session_01VWLTZ9itT8ZY4qGMZQKZ9U)

Claude informó cero diferencias en 600.000 líneas sintéticas, 30.000 fuentes multilínea sintéticas y 5.842 cadenas del catálogo. Pasaron 18/18 pruebas agudas antes y después de aplicar solo la corrección de código en su copia. El revisor observó que `splitlines` ya acota cada llamada a una línea. También pasaron 70 pruebas Python de M10 y procedencia, y siete pruebas de interfaz. En 1.084 rasters sintéticos modificados, observó aceptación o rechazo controlado. Verificó la normalización de metadatos, el control de integridad y la respuesta estática ante entradas de proveedor no válidas.

| ID | Prioridad del revisor | Hallazgo y alcance |
|---|---|---|
| R5-1 | P2 | El filtro de expresiones tranquilizadoras de piel se activa según la categoría. Una foto ambigua o mal categorizada puede quedar fuera del filtro. La documentación previa recoge parte de este riesgo. Una ampliación a otras modalidades requiere revisar su alcance clínico y el impacto en abstenciones. |
| R5-2 | P3 | La detección lingüística tiene cobertura parcial ante variantes Unicode y paráfrasis. |
| R5-3 | P3 | Un raster preparado puede superar el límite de transporte tras normalizarse. Falla cerrado con un mensaje genérico. |
| R5-4 | P3 | Los rechazos por ciertos perfiles de color, profundidades y formatos multimagen corresponden a restricciones publicadas. |
| R5-5 | P3 | El flujo decodifica en preparación y en interpretación. El revisor no midió memoria ni concurrencia. |
| R5-6 | P3 | La API utiliza un mensaje general de abstención para PDF y DICOM, aunque la interfaz los trata por separado. |
| R5-7 | P3 | Pillow puede emitir un aviso de EXIF corrupto en stderr sin contenido del archivo, según el caso observado. |

El revisor usó Pillow 12.3.0. Los resultados de Windows con Pillow 13.0.0 constan en la tabla local. Quedaron fuera de su alcance Sonar del nuevo candidato, CI, Windows, navegador real, proveedor real, pruebas de agotamiento y revisión integral de los demás cambios de PR55–60. El dictamen se refiere al árbol base y a la propuesta de formato aplicada en la copia del revisor.

Los controles M10 se conservan en [el seguimiento técnico](M10_TECHNICAL_FOLLOWUP_20261121.md). La revisión de identificadores visibles y la suficiencia de la imagen corresponden al profesional. Este alcance técnico no mide rendimiento diagnóstico ni autoriza despliegue. El estado global sigue **CLINICALLY_PENDING**.
