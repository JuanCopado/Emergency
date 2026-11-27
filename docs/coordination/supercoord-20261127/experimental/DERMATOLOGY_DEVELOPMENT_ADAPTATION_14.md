# Adaptación explícita de 14 especificaciones a dermatología

**Preparación de desarrollo, sin imágenes nuevas ni reasignación del banco experimental.** Codex ha producido 14 especificaciones técnicas de presentación a partir de metadatos de siete casos SCIN ya revisados por el propietario. Se utiliza un espacio de identificadores nuevo, `DEV-DERM`, con una referencia de trazabilidad a las 14 posiciones históricas. Los IDs S1/S2, mecanismos, archivos canónicos y fichas históricas permanecen intactos.

## Selección reproducible

El filtro sólo admite como **candidatos de metadatos** los ocho activos SCIN del manifiesto de 24 cuyo alcance del propietario es consulta/desarrollo y cuya adenda primaria documenta licencia, consentimiento y curación de desidentificación de la fuente, sin obstáculo identificativo específico observado en los registros disponibles. De ellos se seleccionan siete etiquetas distintas, ordenadas alfabéticamente, con desempate por `case_id` ascendente para los dos casos de eccema. El segundo caso de la etiqueta duplicada queda de reserva.

Se excluyen 16 activos de esta selección, incluidos los dos CDC con rostro/frente y aceptación limitada a representatividad. No se interpreta que esos 16 tengan todos el mismo impedimento ni que toda reutilización esté prohibida: no cumplen el filtro estrecho de esta preparación. No se copian ni procesan sus píxeles.

La adenda primaria no acredita consentimiento incondicional, privacidad de cualquier futuro consumidor ni independencia diagnóstica. Este mapa **no autoriza nuevo uso de píxeles, incorporación al producto o transferencia externa**. Cualquier uso posterior conserva sus salvaguardas y la evaluación de privacidad por finalidad. No se generan derivados de activos con una finalidad de reutilización de píxeles todavía sin resolver.

| Puntero histórico, sin reasignación | Nuevas especificaciones | Etiqueta de la fuente | Finalidad técnica |
|---|---|---|---|
| S1-01 / S2-01 | DEV-DERM-01-1 / -2 | Abscess | Presentación con imagen completa, atribución y limitaciones |
| S1-02 / S2-02 | DEV-DERM-02-1 / -2 | Allergic Contact Dermatitis | Presentación con imagen completa, atribución y limitaciones |
| S1-03 / S2-03 | DEV-DERM-03-1 / -2 | Cellulitis | Presentación con imagen completa, atribución y limitaciones |
| S1-04 / S2-04 | DEV-DERM-04-1 / -2 | Drug Rash | Presentación con imagen completa, sin inferir causalidad |
| S1-05 / S2-05 | DEV-DERM-05-1 / -2 | Eczema | Presentación con imagen completa, atribución y limitaciones |
| S1-06 / S2-06 | DEV-DERM-06-1 / -2 | Folliculitis | Presentación con imagen completa, atribución y limitaciones |
| S1-07 / S2-07 | DEV-DERM-07-1 / -2 | Urticaria | Presentación con imagen completa, sin inferir anafilaxia |

Cada pareja comparte el mismo caso y fuente: **no son dos casos independientes**. Las dos variantes especifican tamaños CSS de 1440×900 y 390×844, `object-fit: contain`, sin recorte ni alteración anatómica. Son requisitos futuros para comprobar presentación adaptable; no imágenes ya renderizadas ni fotografías físicas de una pantalla. La etiqueta de la fuente no se transforma en diagnóstico de referencia. Se mantienen los diferenciales y las limitaciones de historia, exploración y pruebas no disponibles.

## Resultado material

`build_dermatology_development_spec.py` ejecutado correctamente: 24 activos de origen, ocho candidatos SCIN de metadatos, siete casos seleccionados, 14 especificaciones distintas, una reserva por etiqueta duplicada y 16 excluidos. El JSON conserva IDs exactos, SHA-256 de los candidatos tal como constan en los recibos, decisiones, licencia, atribución, limitaciones y hashes de los cuatro documentos de procedencia.

Ninguna imagen fue abierta, copiada, modificada, adquirida, generada o transmitida por esta tarea. Los hashes de los activos proceden de los manifiestos previos; sólo se calcularon ahora los hashes de los documentos fuente y del entregable. No se afirma que existan 14 ni 20 imágenes nuevas terminadas.

El banco conserva **10/30 canónicos, 20 pendientes y cero adjudicaciones**. S2-11 mantiene necesidad de repetición física por moiré. S2-12 mantiene condición experimental, panel y permiso pendientes. R5-1/R5-2/SCA independientes siguen aplazados; este material es desarrollo expuesto y no conjunto independiente de validación.

**CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE.** No se solicitan de nuevo las aprobaciones médicas ya concedidas.
