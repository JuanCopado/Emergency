# R84 · REAUDITORÍA INDEPENDIENTE DE REGRESIONES — PR106 (CODEX R83)

**Repositorio:** `JuanCopado/Emergency`  
**Pull Request:** `#106` (`codex/r68-recepcion-20261124` → `codex/v144-international-scope-20261116`)  
**HEAD exacto auditado (Codex R83):** `a24a62c2fe3c1a0dcf1cdeb180c6145f6ff92774` (*Validate complete image containers before stimulus intake*)  
**Árbol exacto (`tree`):** `93ad4c427df3c0d924e54d0c29f8a9c72610065a`  
**Commit padre (`1a8a14e`):** `1a8a14ec2460962b1974bc6cd3af5f8b02d9be38`  
**Modalidad:** Solo lectura · **Gobernanza:** `CLINICALLY_PENDING` · `NO_GO_CLINICAL_RELEASE`  
**Dictamen para `a24a62c2fe3c1a0dcf1cdeb180c6145f6ff92774`:** **`BLOCKED`** *(código y regresiones 100% resueltos; bloqueado únicamente a la espera de que finalicen `real-test-coverage` [`in_progress`] y `sonarqube` [pendiente] en GitHub)*

---

## 1. Auditoría de la corrección Codex R83 (`a24a62c2`)

El commit `a24a62c2fe3c1a0dcf1cdeb180c6145f6ff92774` añade `clinical/lab/human_factors/image_structure.py` (128 líneas), integra `VALIDATORS` en `intake_r68.py` (+8 líneas) y amplía `test_r68_intake.py` (+120 líneas).

Controles estructurales verificados en `image_structure.py` antes de invocar a Pillow:
- **PNG (`png`):** Firma `\x89PNG\r\n\x1a\n`, `IHDR` primero con `size == 13`, verificación `zlib.crc32` en cada chunk, `IDAT` contiguos, `IEND` con `size == 0`, `seen_data == True` y `end == len(data)` (cero bytes posteriores).
- **JPEG (`jpeg`):** Firma `FF D8`, recorrido completo de segmentos y scans (`0xDA` SOS con manejo de byte-stuffing `FF 00` y marcadores `D0..D7`), y exigencia de `EOI` (`FF D9`) con `scans > 0` y `offset == len(data)` (cero bytes posteriores o imágenes concatenadas).
- **WebP (`webp`):** Firma `RIFF....WEBP`, longitud RIFF exacta (`size + 8 == len(data)`), padding par de byte `0`, rechazo de `ANIM`/`ANMF` y bit animado en `VP8X`, y exactamente 1 frame `VP8 `/`VP8L`.
- **Presupuesto de trabajo:** `MAX_PARTS = 65536`, `MAX_ASSET_BYTES = 64 MiB`, `MAX_IMAGE_PIXELS = 16.000.000`.

---

## 2. Repetición independiente de las tres regresiones y matriz ampliada sobre `a24a62c2`

Reproducción independiente ejecutada sobre `a24a62c2fe3c1a0dcf1cdeb180c6145f6ff92774` con `uv run --with pillow python`:

| Caso reproducido | Resultado en `1a8a14e` | Resultado en `a24a62c2` | Estado |
|---|---|---|---|
| **PNG sin `IEND`** (bytes y SHA-256 coincidentes) | ACEPTADO (fallo) | **RECHAZADO** (`unreadable image container`) | **RESUELTO** |
| **PNG truncado en `IDAT`** (bytes y SHA-256 coincidentes) | ACEPTADO (fallo) | **RECHAZADO** (`unreadable image container`) | **RESUELTO** |
| **JPEG con datos tras `EOI` (`FF D9`)** (bytes y SHA-256 coincidentes) | ACEPTADO (fallo) | **RECHAZADO** (`unreadable image container`) | **RESUELTO** |
| **PNG con CRC de `IHDR` corrupto** (1 bit invertido) | — | **RECHAZADO** (`unreadable image container`) | **PASS** |
| **PNG con byte posterior a `IEND`** | — | **RECHAZADO** (`unreadable image container`) | **PASS** |
| **WebP con byte fuera de `RIFF` / longitud RIFF errónea** | — | **RECHAZADO** (`unreadable image container`) | **PASS** |
| **WebP animado** | RECHAZADO | **RECHAZADO** (`unreadable image container`) | **PASS** |
| **JPEG, PNG y WebP estáticos válidos** | ACEPTADO | **ACEPTADO** (`BYTES_VERIFIED_REVIEW_PENDING`) | **PASS** |
| **Imagen > 16 Mpx (`4001x4001`)** | RECHAZADO | **RECHAZADO** (`expected a bounded still image`) | **PASS** |

- **Pruebas focales locales (`test_r68_intake.py` en `a24a62c2`):** **`Ran 17 tests in 0.119s — OK`**.
- **Preservación del banco (reutilizando R79):** `a24a62c2` solo modifica 3 archivos de código/pruebas; los 10 estímulos históricos, `S2-09.r61.json`, `S2-09.json` y el estado `0/30` adjudicaciones permanecen inalterados.

---

## 3. Estado de los seis checks C12 y Clinical QA sobre `a24a62c2fe3c1a0dcf1cdeb180c6145f6ff92774`

| Check requerido | Estado observado en GitHub |
|---|---|
| `semgrep` | `completed` / **`success`** |
| `trivy` | `completed` / **`success`** |
| `Native local review ... / t05 native (windows-latest)` | `completed` / **`success`** |
| `Native local review ... / t06 native (ubuntu-24.04)` | `completed` / **`success`** |
| `qa` (Clinical QA) | `completed` / **`success`** |
| `real-test-coverage` | **`in_progress`** (`conclusion: null`) |
| `sonarqube` | **Pendiente / no iniciado aún** |

---

## 4. Dictamen final para `a24a62c2fe3c1a0dcf1cdeb180c6145f6ff92774`

- **Dictamen:** **`BLOCKED`** (bloqueo exclusivamente temporal de CI).
- **Criterio:** La corrección técnica de Codex R83 supera todas las regresiones y validaciones estructurales. Sin embargo, dado que `real-test-coverage` sigue en ejecución y `sonarqube` aún no ha concluido, no se certifican checks no finalizados. Una vez que ambos finalicen en `success` sobre `a24a62c2fe3c1a0dcf1cdeb180c6145f6ff92774` (y se retire `Draft`), el SHA quedará habilitado para `MERGE_READY`.
