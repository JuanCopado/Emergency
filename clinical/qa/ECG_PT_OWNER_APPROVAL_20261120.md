# ECG-PT-20261120 v1 — aceptación médica documentada

**Fecha:** 20 de noviembre de 2026, 17:16:52 UTC. **Validador médico final:** Dr. Juan Copado Ceballos. **Respuesta literal:** «Si acepto el cambio»; aceptación afirmativa explícita de la propuesta ECG-PT-20261120 v1 inmediatamente anterior.

## Cambio autorizado, sin ampliaciones

Sustituir exclusivamente la definición errónea del signo Peñaloza–Tranchesi en `clinical/modules/image-modalities.md`, sección `ecg-image`, y actualizar la proyección exacta en `app/src/data/generatedClinicalGuides.json`:

> **Peñaloza–Tranchesi sign (historical, indirect finding):** low-amplitude QRS in V1 with a marked amplitude increase in V2, described as an indirect sign of right atrial enlargement. It is nonspecific and does not establish chamber enlargement alone; correlate with lead placement, the full ECG and echocardiography.

Se elimina la atribución anterior a S profundas en V5–V6 y sobrecarga ventricular derecha **solo en ese epónimo**. Sin cambios en patrones de Winter/Wellens, cálculos, dosis, productos, protocolos de países o los otros 130 módulos.

## Fuentes y alcance de contraste

- Samesima et al., directrices SBC sobre informes ECG (2022), DOI [10.36660/abc.20220623](https://doi.org/10.36660/abc.20220623), §§6.1.2 y 6.1.5.2; definición específica y comparación con criterios ventriculares.
- Santos et al., *J Electrocardiol* (2017), DOI [10.1016/j.jelectrocard.2017.07.009](https://doi.org/10.1016/j.jelectrocard.2017.07.009), resumen; ejemplo de inespecificidad del signo.
- Informe de investigación previa: [ECG_POCUS_EVIDENCE_FOLLOWUP_20261120.md](ECG_POCUS_EVIDENCE_FOLLOWUP_20261120.md). No se extrapola rendimiento diagnóstico.

## Resultado y límites

- Decisión puntual: **SÍ**, con fecha e ID registrados en `clinical/updates/pending-updates.json`.
- Implementación integrada mediante [PR47](https://github.com/JuanCopado/Emergency/pull/47), merge `e1d05196dc85b1e112a5e7f90dd92cf68ab7bec5`, árbol `1d65939220de33161f4c06e9a5e013359995c757`, en la rama internacional. Verificación posterior al merge observada el 20/11: Evidence `44784529250`, Clinical QA `44784529339`, UI `44784529236` y Security `44784529314`, los cuatro PASS. La cola canónica queda conciliada con ese cierre técnico.
- El módulo `ecg-image` continúa **YELLOW**, con `last_checked=2026-09-27`; sin promoción ni renovación general.
- **CLINICALLY_PENDING**; ni este cambio ni las pruebas técnicas conceden GO_RELEASE o validación de diagnóstico automático desde imágenes.
- No se han aceptado modificaciones adicionales ni dado por finalizadas las revisiones integrales de evidencia de imagen.
