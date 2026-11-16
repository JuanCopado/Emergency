# Coordinación de guías internacionales y diferencias justificadas

Fecha: 16/11/2026. Entrega: **INT-02A**, ampliación de INT-01.

## Directriz del propietario

Juan solicita distinguir Europa, Reino Unido y los países americanos pertinentes y aplicar las diferencias que correspondan. Precisa después que el proyecto debe seguir guías de amplio reconocimiento internacional para conservar coherencia, evitando fragmentarlo en protocolos excesivamente locales o regionales.

Decisión común: **un núcleo clínico internacional coherente, un mismo módulo canónico y diferencias puntuales solo cuando sean materiales, verificadas y justificadas**. La calidad, vigencia, consenso y aplicabilidad sustentan la selección de guías; no el origen de una fuente ni la ubicación del propietario. Consultar el núcleo no exige elegir hospital o país.

## Base y alcance de la entrega

- Repositorio: `JuanCopado/Emergency`.
- Rama de trabajo: `codex/v144-international-scope-20261116`.
- Base inspeccionada: `285114a56ce2814b54b53d990474bb121876ef84`.
- Árbol de base: `68b2d48017ffad31de8032b5dd93e0e7a78e70ae`.
- Política canónica: [international-guideline-policy.md](../clinical/references/international-guideline-policy.md).
- Marco y hoja de ruta: [INTERNATIONAL_SCOPE.md](INTERNATIONAL_SCOPE.md) e [INTERNATIONAL_ROADMAP.md](INTERNATIONAL_ROADMAP.md).

La entrega anterior conservaba la conciliación focal de ceftriaxona y los antecedentes clínicos. Esta ampliación es documental y de coordinación: no cambia pautas, calculadoras, contratos, interfaz ni catálogos clínicos. La selección opcional de contexto continúa como desarrollo propuesto; no se anuncia un selector implementado.

## Comunicación y participación

| Destino | Acción y estado observado |
|---|---|
| Entradas comunes | Directriz incorporada en AGENTS, CODEX, CLAUDE, GEMINI, README y las entradas clínicas. La referencia canónica también se exige para paquetes clínicos independientes. |
| Equipo de esta entrega | Tres agentes recibieron la precisión final: fuentes y alcance, entradas de colaboradores y revisión independiente. Los dos primeros aplicaron cambios asignados; el tercero emitió un dictamen documental conforme. |
| Actualización clínica | `international-context.md` y `update-policy.md` exigen seleccionar la guía de referencia, resolver diferencias y preparar el cambio concreto en el núcleo o una variante puntual revisable. |
| Vigilancia evidencia semanal | Prompt actualizado y respuesta de guardado comprobada; horario, activación y modo de programación conservados. |
| Revisar guías de emergencias | Prompt actualizado y respuesta de guardado comprobada; horario, activación y modo de programación conservados. |
| Coordinación general | [Issue #18](https://github.com/JuanCopado/Emergency/issues/18) es el registro vivo del aviso y de los enlaces de publicación; su actualización identifica el commit entregado. |
| Colaboradores humanos y sesiones externas | Las instrucciones publicadas permiten incorporar la directriz; no se presume lectura, recepción, instalación local ni integración en otras ramas o chats. |

Las tareas programadas mantienen su función de vigilancia: propondrán la modificación concreta para revisión y conservarán sus condiciones de notificación. El cambio del prompt no ejecuta una revisión clínica ni activa pautas automáticamente. No se ejecutaron las tareas durante esta actualización.

## Contenido operativo acordado

1. Partir del módulo canónico y las guías internacionales más sólidas para la pregunta, población e indicación.
2. Contrastar Europa, Reino Unido, Estados Unidos, Canadá y Latinoamérica/Caribe por país cuando el contexto cambie materialmente la decisión.
3. Mejorar el núcleo cuando el hallazgo tenga aplicación general; añadir una variante puntual del mismo módulo solo cuando exista una diferencia contextual justificada.
4. Conservar pauta completa, procedencia, motivo de selección y revisión real. No combinar dosis, intervalos o umbrales de regímenes incompatibles.
5. Registrar cobertura por recomendación y contexto; una concordancia con el núcleo no obliga a crear otro protocolo.
6. Identificar por separado guía clínica, información de producto y adaptación organizativa. Un hospital aporta circuitos y recursos, sin redefinir por defecto el producto global.

## Fuentes y cobertura

Se identificó un directorio inicial de portales oficiales de OMS/ILCOR, organismos y sociedades europeos/británicos y fuentes americanas. El manual NICE y el portal OPS se identificaron por contenido indexado oficial al devolver 403 la apertura directa; los demás portales enumerados se abrieron. La política registra enlaces, funciones y límites.

Esta revisión identifica **fuentes de búsqueda**, no valida individualmente todas sus recomendaciones. México y Brasil son ejemplos de catálogos nacionales identificados. No consta revisión completa de los 131 módulos frente a todos los países ni se ha medido cobertura clínica internacional nueva.

## Verificación y límites

La revisión independiente de coherencia INT-02A fue conforme: núcleo internacional primero, diferencias materiales justificadas, aplicación mediante decisiones trazables, ausencia de país/hospital obligatorio para referencia, sin fragmentación en protocolos completos por territorio. Su alcance fue documental; no repitió las consultas de portales ni verificó dosis.

Los controles de publicación se limitan al alcance modificado: referencias documentales, preservación de metadatos e historial, estado breve y correspondencia de los archivos editados con el árbol Git. El commit y la comprobación final de publicación se registran en el issue #18. No se ejecuta QA clínico global, build ni validación visual por una modificación documental.

Se mantienen los estados y fechas de evidencia de la base, los 19 contratos agudos bloqueados y `CLINICALLY_PENDING`. La nueva política no constituye aprobación internacional, instalación de la competencia en otro entorno ni integración A/B/C/D. Las ramas protegidas y los cambios ajenos quedan fuera de esta entrega.

## Criterio para las siguientes entregas clínicas

Cada revisión de un módulo debe terminar en una decisión sustentada: conservar el núcleo, mejorarlo, incorporar una variante puntual o documentar un conflicto material pendiente. Añadir país o región a una lista no completa ese trabajo. El alcance clínico aceptado se registra por recomendación y contexto; las capacidades generales que no dependan de una excepción pueden seguir avanzando.
