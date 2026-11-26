# R98 · Lote candidato de recepción

**CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE**

Este lote aporta bytes físicos para revisión de S1-01. El manifiesto canónico sigue en 10/30 archivos y 0 adjudicados. El lote queda en BYTES_VERIFIED_REVIEW_PENDING.

| Archivo | Papel | Bytes | SHA-256 |
| --- | --- | --- | --- |
| lot-01/S1-01-source.jpg | Copia redimensionada de la fuente | 16840 | 8f91995c4ec6969885b8b2dcd1383ce2d41dc29143d6dd6c751146f55acbfe4c |
| lot-01/S1-01.jpg | Derivado RGB, JPEG 440 × 330 | 43637 | 8bcc20bc199de5ec5d5f645fcb6df3d23c871a3c4271cba8467385949a7e5252 |

## Procedencia y permiso

La página primaria de Commons identifica una fotografía del propio autor y una declaración mundial de dominio público. Commons atribuye el autor a Berteun basándose en la declaración del cargador. La copia obtenida procede de HIVE Doctor, que declara redimensionamiento como única modificación y conserva el título, autor y enlace. Se verificó la licencia en la página primaria. El SHA de esta copia no se presenta como el del original de 2816 × 2112 de Commons.

[Fuente primaria y permiso](https://commons.wikimedia.org/wiki/File:Abrasion_on_hand_20050906.jpg) · [Copia obtenida de GitHub en commit fijo](https://github.com/ReffRizz/hive-apps/blob/f9a2ffd714e18a9c529a0745d988fd59453b4be8/doctor/photos/p385217.jpg) · [Metadatos de procedencia del distribuidor](https://github.com/ReffRizz/hive-apps/blob/f9a2ffd714e18a9c529a0745d988fd59453b4be8/doctor/photos.json)

## Transformación y controles

La copia fuente se conserva. El derivado se convirtió a RGB y se recodificó a JPEG sin EXIF, XMP o comentarios. No se recoloreó la piel ni se editó la morfología. La inspección técnica observa una superficie cutánea abierta sin cierre, sin rostro ni identificadores textuales. El preflight local valida ambos archivos y su recibo. La auditoría de metadatos del derivado devuelve cero hallazgos. dHash 171c3c3031300184, distancia mínima 23 frente a las seis imágenes del banco con dHash disponible. No se hallaron duplicados SHA-256 con los diez archivos históricos.

La revisión de píxeles independiente, MST 2, luz neutra, realismo a 360 × 640 y equivalencia del par permanecen pendientes. El preview es para revisión y no forma parte de los 30 estímulos. No se asigna diagnóstico ni referencia clínica. El médico propietario conserva la adjudicación posterior. La resolución 440 × 330 es la de la copia recuperada; la fuente de mayor resolución sigue pendiente de descarga.

## Reproducción

Desde la raíz del repositorio, ejecutar el procedimiento existente con el recibo local.

```sh
python clinical/lab/human_factors/intake_r68.py clinical/lab/human_factors/intake_batches/r98/lot-01/receipt.json
```

Antes de asignar el derivado al manifiesto canónico, completar las revisiones individuales del protocolo MED-DEC-R46-02. El lote no certifica la privacidad clínica ni el realismo por superar la verificación de bytes.
