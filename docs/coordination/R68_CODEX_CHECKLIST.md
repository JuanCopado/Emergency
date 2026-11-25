# R68 · Conciliación R54/R61 y recepción local

**CLINICALLY_PENDING · YELLOW · NO_GO_CLINICAL_RELEASE · NOT_FROZEN_NOT_VALIDATED.**

| Control | Resultado |
| --- | --- |
| Receptor tras PR101 | `3b4f58b52fa7e0f1b75d0841cb5cac2b9f15a5a9`, PR102 incorporada |
| PR103 | Borrador a `8b3f7ab2aa02b16bf1eb6f6e78d99de16a81dbe9`. La rama de verificación combina ese candidato con el receptor |
| Fichas, manifiesto y bytes | PASS en 30 IDs. S2-09 apunta a [la ficha R61](r54/dossiers/S2-09.r61.json) con SHA‑256 `e55d2d35203147e3f92c95c61e464a80dca4a28f08a7de495dd46648a21fa077` |
| Trazabilidad anterior | PASS. La [ficha R54](r54/dossiers/S2-09.json) y su índice literal preservan `555d6c5717edac86b4b7a30352cca8638e52c3df1ac3c826493144ee8dbe0ce2`. El [índice operativo](r54/INVENTORY.md) enlaza el JPEG anterior por commit |
| Focal local | 60 pruebas PASS, incluidas las regresiones de las fichas, los 24 sellos históricos y ocho pt-BR |
| Conteo | 10/30 archivos, 20/30 pendientes y 0/30 adjudicados. M1=8, M2=4, M3=18 |
| Activos Antigravity y Gemini R65 | BLOCKED. Sin nuevos archivos o informe disponibles para integrar |

## Recepción de archivos

Guardar el paquete recibido fuera del repositorio, con `recepcion.json` junto a sus archivos. Usar una fila por pieza, incluidas las de una galería, con rol `original`, `derivative`, `target` o `distractor`. `kind` admite `synthetic`, `phantom` o `authorized_clinical`. Ejemplo de forma, con valores de muestra que se deben sustituir:

```json
{
  "assets": [
    {
      "stimulus_id": "S1-10",
      "file": "lote/original.jpg",
      "role": "original",
      "kind": "synthetic",
      "source": "<autor, fuente y revisión>",
      "license": "<licencia aplicable al archivo>",
      "permission_ref": "<evidencia de uso, adaptación y redistribución>",
      "privacy_ref": "<referencia a la revisión de privacidad o procedencia sintética documentada>",
      "transformation": "original",
      "bytes": 123,
      "sha256": "<SHA-256 del archivo>"
    }
  ]
}
```

```bash
python clinical/lab/human_factors/intake_r68.py /ruta/al/paquete/recepcion.json
```

`BYTES_VERIFIED_REVIEW_PENDING` acredita coincidencia del archivo con el recibo. La comprobación es local y de solo lectura. Antes de incorporar un derivado, cotejar las referencias de permisos y privacidad, aplicar la especificación por ID, revisar metadatos y píxeles, validar formato, dimensiones y representación a 360×640, y comprobar duplicados y la composición de cada galería. Actualizar el índice y la ficha correspondiente con el hash en la misma entrega que el manifiesto. [Protocolo de adjudicación](../../clinical/qa/R54_IMAGE_ADJUDICATION_PROTOCOL_20261124.md)

## R83 · Cierre de regresiones R84 — 25/11/2026

R84 exige cambios sobre `1a8a14ec2460962b1974bc6cd3af5f8b02d9be38`.
Se reutiliza la corrección estructural de R78 publicada en
`a24a62c2fe3c1a0dcf1cdeb180c6145f6ff92774`, árbol
`93ad4c427df3c0d924e54d0c29f8a9c72610065a`; no se duplica su implementación.

### Contrato de recepción de contenedores
El archivo completo debe contener una única imagen estática JPEG, PNG o WebP.
La coincidencia de tamaño y SHA-256 del recibo es necesaria, pero no suficiente.
Antes de decodificar:
- PNG: firma, límites y CRC de todos los chunks; IHDR inicial; IDAT contiguos;
  IEND vacío obligatorio y exactamente al final. Rechazar truncamientos incluso
  cuando el decodificador pueda recuperar los píxeles.
- JPEG: recorrer segmentos y todos los scans hasta el EOI real. Rechazar cualquier
  byte posterior al EOI, incluidos espacios, otro EOI e imágenes concatenadas.
  Un marcador EOI dentro de metadatos con longitud válida no es el final de imagen.
- WebP: longitud RIFF exacta, límites de todos los chunks, padding par nulo y
  exactamente una imagen; rechazar sobrantes y animación.
Los metadatos internos estructuralmente válidos se aceptan para su revisión
de privacidad posterior. Esta política no certifica privacidad ni adjudicación.

### Evidencia R83 observada
`test_r68_intake.py`: **20 pruebas PASS** localmente, Python 3.14 / Pillow 13.0.0.
Se añaden tres pruebas por `check_receipt` que escriben físicamente cada candidato
y recalculan tamaño y SHA-256 sobre sus bytes:
- 7 negativos PNG/JPEG: sin IEND, truncado dentro de IDAT, CRC IDAT inválido,
  payload/espacio/segundo EOI tras EOI e imágenes JPEG concatenadas.
- 6 negativos WebP: truncado, sobrantes, concatenación, longitud de chunk,
  padding ausente y padding no nulo, ajustando RIFF cuando corresponde.
- 14 variantes válidas: JPEG basal/progresivo/gris/CMYK/EXIF; PNG RGB con texto,
  RGBA, paleta, gris y 16 bits; WebP con pérdida, sin pérdida, RGBA y EXIF.
Se comprueba aceptación con `BYTES_VERIFIED_REVIEW_PENDING`, hash exacto y
manifiesto sin promoción.

Las tres pruebas nuevas se ejecutaron también contra el intake de `1a8a14e`:
9 fallos de subcaso esperados, 0 errores; la prueba de variantes válidas pasa.
En Pillow 13.0.0 el caso PNG `[:-20]` ya se rechaza en el código anterior,
a diferencia de R84/Pillow 12.3.0; se conserva la regresión y se exige CI con
las dependencias fijadas. No se extrapola esa diferencia a una corrección del código.

C12 y Clinical QA deben completarse sobre el nuevo HEAD publicado. Los resultados
de `1a8a14e` y `a24a62c` no se atribuyen a un SHA posterior.
**Dictamen independiente vigente: CHANGES_REQUIRED sobre 1a8a14e; nueva auditoría
Antigravity pendiente sobre el HEAD sucesor. PR106 no se fusiona sin dictamen
favorable y controles completos.** Banco, manifiesto, sellos y adjudicaciones
sin cambios en R83. CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE.
