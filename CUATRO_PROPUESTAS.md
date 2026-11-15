# Cuatro direcciones visuales para Emergency

Exploraciones aisladas del selector. No se añaden funciones IA, decisiones automáticas ni nuevas capacidades clínicas. El lenguaje visual es contemporáneo, con iconos simples, espacios medidos y estados explícitos.

- Horizon: panel claro, azul cobalto y rail lateral de identidad.
- Noctis: grafito y menta, superficies de bajo brillo y sin efectos de neón.
- Atlas: título y contexto a la izquierda, lista de circuitos a la derecha; tonos minerales.
- Orbit: espacio de trabajo compacto con barra de contexto, índigo suave y controles agrupados.

Vista navegable: http://127.0.0.1:5186/design/arrhythmia-selector (alternar propuestas en la franja superior). Se puede añadir ?concept=horizon, ?concept=noctis, ?concept=atlas o ?concept=orbit.

Diseños editables de concepto en Figma: https://www.figma.com/design/s0fnMybStrhN03uVwXJ7df
Cuatro frames y 100 nodos de texto editables con colores vinculados a tokens. Son láminas de dirección visual, no una copia exacta de cada pantalla React. Se exploraron bibliotecas de diseño; tras un error de la API de instancias, se completaron con elementos nativos editables. La versión funcional de navegador es la referencia para comportamiento y adaptación móvil.

Capturas de las cuatro variantes: preview/concepts/*-desktop.png y *-mobile.png. Comparativa: preview/concepts/comparativa.png. Validación: preview/concepts/validation.json. Figma: preview/concepts/figma-noctis.png.

Verificado: cuatro enlaces y estado YELLOW en cada variante; escritorio y anchos móviles 390/320 px sin desplazamiento horizontal; cero pageerrors. Navegaciones reales del componente compartido 8/8 PASS, con teclado; tests DOM existentes 8/8 PASS. Tipos, lint y compilación PASS.

Main, PR #16, registro de evidencias, fuentes clínicas y catálogos sin cambios. No se publica ni fusiona esta copia local. Selector YELLOW, CLINICALLY_PENDING, 4 P1, 19 BLOCKED e I02 NO-GO intactos. Estas propuestas se revisarán después para alinearlas con el conjunto del proyecto.