# CHEST X-RAY VISUAL INPUT PROTOCOL v1.0 — FROZEN

Fecha de congelación: 03/10/2026.

Aplica a CheXpert expert-test y MIMIC-CXR-JPG curated test.

## Principio
Usar **los píxeles proporcionados por el dataset**, sin ajuste post hoc dependiente del
resultado. No aplicar CLAHE, equalización, recorte pulmonar, eliminación de dispositivos,
inpainting, OCR-based masking ni ventanas distintas por sospecha clínica.

## Entrada
- CheXpert: imagen distribuida por el dataset para el estudio/vista.
- MIMIC-CXR-JPG: JPG oficial correspondiente al dicom_id del estudio.
- Conservar todas las vistas del estudio juntas.
- La predicción primaria es a nivel de estudio.

## Normalización permitida
Solo para compatibilidad de visualización/modelo:
1. decodificar a escala de grises;
2. respetar orientación ya codificada por el dataset;
3. reescalar isotrópicamente manteniendo aspect ratio si el consumidor exige un tamaño máximo;
4. padding neutro si se necesita canvas cuadrado.

No recortar anatomía. No modificar contraste en función del contenido.

## Leakage
El paquete model-facing no contiene:
- patient/study IDs fuente;
- labels;
- reportes;
- nombres de archivo originales que codifiquen IDs;
- referencia experta/manual.

## Fallo cerrado
Imagen ausente/corrupta, dimensions no válidas o estudio sin ninguna vista usable ->
`nondiagnostic`; no excluir post hoc.

## Límites
Este protocolo estandariza el input visual, no valida diagnóstico ni licencia de acceso.
