# Orbit / Noctis — base visual provisional para revisión

Esta propuesta conserva la preferencia del propietario: Orbit como tema claro y Noctis como tema oscuro. El propietario considera que todavía falta atractivo y modernidad; no se registra aceptación estética definitiva. La PR sirve para revisar la base funcional y orientar otra iteración de dirección artística.

## Alcance

Selector claro/oscuro con preferencia persistente y misma distribución; tipografía DM Sans alojada localmente con licencia OFL; escala de espaciado y jerarquía refinadas; versiones de escritorio y móvil. Cuatro accesos existentes con estados canónicos leídos del catálogo. La ruta /design/arrhythmia-combined es una vista de propuesta; /design/arrhythmia-selector conserva las exploraciones previas como referencia. El componente compartido cambia también su presentación en /guides y /clinical, conservando allí íntegros los criterios y excepciones previos.

No se añaden funciones clínicas IA, decisiones automáticas, dosis, fórmulas, contratos ni promociones clínicas. No se integra el parche del test original: las comprobaciones visuales tienen su propio script de navegador con la comparación normalizada.

## Independencia

Base de revisión fijada a f61df568945236ba0e8c6bd278c153205a6db0da en una rama nueva review/orbit-noctis-base-20261115. La rama design/orbit-noctis-visual-base se revisa contra ese snapshot. No se añaden commits a la rama de la PR #16 ni se modifica main. No fusionar ni activar auto-merge.

## Evidencia

- preview/combined/light-desktop.png y dark-desktop.png.
- preview/combined/light-mobile.png y dark-mobile.png.
- preview/combined/validation.json: ocho navegaciones reales, cuatro por tema, con teclado; cero errores de página. Misma geometría entre temas, persistencia y fuente local cargada.
- preview/pr-review/: resultados de lint, tipos, tests, compilación y navegador repetidos antes de publicar.
- Scripts reproducibles: app/scripts/capture-selector-combined.mjs; ocho tests DOM existentes en app/src/test/resuscitation-circuits.test.tsx.

Para abrir la propuesta local: npm run dev -- --host 127.0.0.1 --port 5186 --strictPort desde app; visitar /design/arrhythmia-combined?theme=light o ?theme=dark. No requiere fuentes remotas durante el uso.

## Revisión solicitada

Revisar jerarquía, composición, contraste, densidad, navegación y adaptación móvil como base provisional. Pendiente: una dirección visual más distintiva, armonización con el conjunto del proyecto y evaluación humana de usabilidad. La petición actual de PR no implica que el diseño se considere terminado.

Permanecen YELLOW, CLINICALLY_PENDING, 4 P1, 19 BLOCKED e I02 NO-GO; 117 GREEN/14 YELLOW/0 RED. El cierre técnico de la PR #16 no se reabre ni se modifica, y el prototipo visual no constituye validación clínica.