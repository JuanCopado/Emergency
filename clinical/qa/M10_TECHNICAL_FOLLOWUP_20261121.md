# M10 · revisión técnica de PR51 · 21/11/2026

La referencia documental de piel y heridas está aceptada en PR52. Los módulos padre de imagen y apoyo diagnóstico continúan YELLOW. Estado global CLINICALLY_PENDING.

La PR51 original (c040a172) divergía de la integración (4aa2d397) con ancestro 21defd4. Su composición local sin conflictos produjo el árbol 289a2bc413bf66b92685f444e6a36776df0dca99 y pasó las 48 pruebas M10 existentes. La auditoría adicional observó transporte de PDF y DICOM, tolerancia de tipos erróneos durante la abstención, aceptación literal de una frase de alta tranquilizadora, rechazo de un PNG bicolor y aceptación de JPEG y WebP blancos. El precedente de Sonar fue 79,0 % y C. El resultado del nuevo análisis corresponde al check remoto de cada commit.

## Alcance del cambio

- La entrada binaria externa admite imágenes PNG, JPEG y WebP fijas. La ruta de salida genera un PNG nuevo a partir de los píxeles decodificados y orientados. Comprueba dimensiones, presupuesto de memoria y tamaño de transporte. Se excluyen del proveedor los contenedores PDF o DICOM, las animaciones, la transparencia no opaca y los perfiles ICC que exigirían una conversión de color. La revisión de identificadores visibles sigue siendo obligatoria.
- La ausencia de variación se evalúa en los canales visibles. Una imagen técnicamente legible sigue necesitando revisión de iluminación, enfoque, escala y suficiencia clínica.
- El tipo de cada campo del proveedor se valida también en la abstención. Las frases reconocidas de tranquilidad indebida en piel provocan abstención con texto clínico retirado. La detección lingüística es parcial y depende del idioma y la formulación.
- La selección manual de categoría prevalece y la tarjeta muestra la categoría devuelta por el servidor. Las imágenes de ensayo son sintéticas. La respuesta de proveedor se ensaya con transporte simulado sin red.

## Revisión residual R4 sobre la integración ca308af6

Una respuesta simulada de fotografía de piel podía incluir una frase de tranquilidad en las limitaciones. En la vía «ok» el adaptador mantenía la interpretación. En la abstención también se mostraba la frase. El filtro ahora revisa cada limitación del proveedor en ambos estados, elimina los elementos reconocidos y presenta el aviso local de abstención. Los motivos seguros independientes se conservan. Una abstención con todos sus motivos seguros conserva exactamente los motivos y las banderas originales. Las pruebas cubren también el intento de aceptar la propuesta sin revisión. La regla lingüística mantiene su cobertura parcial y puede marcar expresiones de precaución. La prueba utiliza un PNG sintético y un proveedor simulado. Estado global `CLINICALLY_PENDING`.

La primera revisión pasó 59 pruebas focales en Windows. Claude Code observó que las etiquetas de procedencia y las frases que ocupan varios motivos también llegan a la tarjeta de revisión. El adaptador sustituye una etiqueta reconocida por su valor técnico genérico, se abstiene y conserva la otra etiqueta cuando es válida. Revisa asimismo el texto conjunto de los motivos y retira sólo los elementos afectados. Las 62 pruebas focales de la segunda revisión pasaron en Windows. Se conservan el límite de 128 caracteres y el requisito de etiquetas imprimibles.

## Verificación anterior

En Windows, 52 pruebas del módulo aprobaron con Pillow 13.0.0. El auditor independiente ejecutó además nueve contratos del flujo y seis casos raster estándar, con píxeles uniformes y bicolores y marcas sintéticas de metadatos. La revisión final se vincula a la identidad del candidato en la matriz de integración. Los resultados de estas pruebas no estiman sensibilidad ni especificidad clínica. No hay cohorte prospectiva ni aprobación para despliegue.

## Reverificación de Claude Code sobre 24353afb

El gate Sonar de ese commit pasó con 86,0 % de cobertura nueva y ninguna incidencia nueva. En revisión independiente posterior, Claude encontró límites adicionales en metadatos EXIF, nombres declarados, identificadores del proveedor y presentación de resultados. El backend convierte errores de decodificación en una respuesta pública 422 y las respuestas de proveedor malformadas en un fallo explícito 502 sin datos de la propuesta. Se comprueba la extensión cuando existe y se rechazan caracteres de control en nombres o etiquetas de proveedor/modelo. Estas etiquetas admiten hasta 128 caracteres imprimibles. Las omisiones de anotaciones y la selección de categoría en pantalla se verifican por separado. El límite de 12 MiB se comprueba también al normalizar y la comprobación de color y transparencia ocurre antes del envío. La aplicación conserva la revisión manual para los formatos fuera del alcance.
