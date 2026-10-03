# ECHONET-DYNAMIC VISUAL INPUT PROTOCOL v1.0 — FROZEN

Fecha de congelación: 03/10/2026.

## Alcance
Solo vídeos A4C del split TEST oficial para target `lvef_below_40_percent`.

## Entrada
Usar el vídeo completo autorizado. No seleccionar manualmente ciclos o frames por la EF conocida.

## Representación model-facing
Cuando el consumidor no acepte vídeo nativo:
- extraer **32 frames** equiespaciados en el índice temporal completo;
- incluir primer y último frame;
- preservar orden temporal;
- no hacer selección por calidad después de ver el resultado;
- no usar EF, EDV/ESV ni trazados para elegir frames.

Si el consumidor acepta vídeo, usar el archivo completo sin re-codificación diagnóstica.

## Preprocesado
- mantener aspect ratio;
- conversión de color/grayscale solo si la interfaz lo exige;
- no cropping dependiente del contenido;
- no overlay con EF, contours o labels;
- cualquier texto/overlay diagnóstico visible debe provocar revisión de leakage antes de evaluación.

## Fallo cerrado
Vídeo corrupto, <32 frames para el modo de 32 frames, o incapacidad de decodificación ->
`nondiagnostic`; no eliminar post hoc.

## Límites
EchoNet-Dynamic es single-center, A4C y no representa POCUS de urgencias general.
