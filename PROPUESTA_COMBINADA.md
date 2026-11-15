# Orbit + Noctis — propuesta combinada provisional

Orbit es la estructura común y el tema claro. Noctis aporta la paleta oscura. El selector Claro/Oscuro mantiene la geometría, el contexto y los cuatro destinos; funciona con teclado y recuerda la elección en almacenamiento local exclusivo de esta vista de diseño. Sin modificar el tema global de las páginas clínicas. No requiere nuevos paquetes ni recursos de red.

Vista: http://127.0.0.1:5186/design/arrhythmia-combined
Enlaces directos: ?theme=light y ?theme=dark. Las cuatro propuestas anteriores se conservan en /design/arrhythmia-selector.

Controles: ocho navegaciones reales PASS (cuatro por tema), ocho tests DOM existentes PASS, tipos y lint PASS, compilación PASS. Persistencia y cambio con teclado PASS. Distribución de tarjetas idéntica en escritorio para ambos temas; móvil 390 y 320 px sin desbordamiento. Cero errores de página. Evidencia: preview/combined/validation.json y capturas de escritorio/móvil de ambos temas.

Fuentes clínicas, registro y catálogos idénticos a f61df568945236ba0e8c6bd278c153205a6db0da. PR #16 y main intactos. Selector YELLOW, CLINICALLY_PENDING, 4 P1, 19 BLOCKED e I02 NO-GO conservados. No publicar ni integrar automáticamente.

Esta combinación es una base de diseño para revisión posterior. Próxima iteración: coherencia tipográfica con todas las secciones, escala de espaciado, densidad de información, claridad de los criterios clínicos y revisión de accesibilidad. No se declara el diseño definitivo ni validación clínica por los controles técnicos.