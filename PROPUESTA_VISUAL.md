# Propuesta visual — selector de arritmias/parada

Copia aislada de f61df568945236ba0e8c6bd278c153205a6db0da. Rama local design/arrhythmia-selector-visual-proposal, sin remoto ni publicación. PR #16 y main sin cambios.

Vista previa: http://127.0.0.1:5186/design/arrhythmia-selector

Paleta azul oscuro/verde azulado, grupos Adulto/Pediatría, tarjetas amplias, iconos locales y estados leídos del catálogo canónico. Móvil a una columna; foco visible y respeto a movimiento reducido. Sin dependencias nuevas.

La página de diseño muestra el componente y permite desplegar la guía canónica sin editar su contenido. En las rutas /guides y /clinical se mantiene íntegro el contenido canónico con las excepciones antes del selector; sólo cambia su presentación. El repliegue de la guía pertenece al escaparate de diseño y no se ha aplicado a las páginas clínicas existentes.

Validación: tipos y lint PASS; ocho tests DOM existentes PASS; ocho navegaciones reales con teclado PASS en Chrome 157.0.8103.51 con sandbox habilitado; cero errores de página; anchos móviles 390 y 320 px sin desplazamiento horizontal; compilación PASS. Fuentes clínicas y catálogos idénticos al commit base.

Capturas: preview/desktop.png y preview/mobile-390.png. Resultados: preview/validation.json. Script: app/scripts/preview-selector.mjs. Para iniciar la vista: npm run dev -- --host 127.0.0.1 --port 5186 --strictPort, desde app.

Selector YELLOW, CLINICALLY_PENDING, 4 P1, 19 BLOCKED e I02 NO-GO conservados. Los cuatro GREEN de destinos ya existían. Propuesta para revisión visual, sin integración ni nueva validación clínica.