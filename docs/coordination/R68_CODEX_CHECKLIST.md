# R68 · Conciliación R54/R61 y recepción local

**CLINICALLY_PENDING · YELLOW · NO_GO_CLINICAL_RELEASE · NOT_FROZEN_NOT_VALIDATED.**

| Control | Resultado |
| --- | --- |
| Receptor tras PR101 | `3b4f58b52fa7e0f1b75d0841cb5cac2b9f15a5a9`, PR102 incorporada |
| PR103 | Borrador a `8b3f7ab2aa02b16bf1eb6f6e78d99de16a81dbe9`. La rama de verificación combina ese candidato con el receptor |
| Fichas, manifiesto y bytes | PASS en 30 IDs. S2-09 apunta a [la ficha R61](r54/dossiers/S2-09.r61.json) con SHA‑256 `e55d2d35203147e3f92c95c61e464a80dca4a28f08a7de495dd46648a21fa077` |
| Trazabilidad anterior | PASS. La [ficha R54](r54/dossiers/S2-09.json) y su índice literal preservan `555d6c5717edac86b4b7a30352cca8638e52c3df1ac3c826493144ee8dbe0ce2`. El [índice operativo](r54/INVENTORY.md) enlaza el JPEG anterior por commit |
| Focal local | 59 pruebas PASS, incluidas las regresiones de las fichas, los 24 sellos históricos y ocho pt-BR |
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
