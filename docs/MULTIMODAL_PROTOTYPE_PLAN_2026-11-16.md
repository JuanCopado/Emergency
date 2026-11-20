# Prototipo multimodal — diseño y ejecución

Origen preservado: base `062d890b4fc92369b83c87664bb4bb0205ccb33f`, rama
`codex/v144-multimodal-prototype-20261116`. Composición técnica del 20/11/2026:
base `9b4f705dcfac0d52c10205f7c46c91f7b5b876df`, rama
`codex/v144-intg-e1-image-20261120`. Se incorporan solo fuentes, pruebas,
esquema y requisitos; no bancos privados, medios ni QA históricos. Encargo del
propietario: ingesta, adaptadores técnicos y banco evaluable; sin entrenamiento
ni autorización clínica. Los resultados históricos no validan esta composición.

Corrección autorizada el 20/11/2026 tras auditoría independiente: candidato local
`codex/v144-intg-e1-auditfix-20261120`, procedente del árbol técnico preservado
`d241f251bb1f766dce24da179b74f6ab0ea7ae6a`. El registro de la corrección y sus
evidencias se entrega por separado; la lista siguiente conserva el plan original,
no certifica que haya datos reales ciegos o una validación clínica completada.

## Diseño

CLI local adicional bajo `clinical/scripts/multimodal/`; no modificar el proveedor
visual ni duplicar el evaluador binario canónico. Catálogo privado con procedencia,
derechos, revisiones y agrupaciones. Proyección estricta de entradas ciegas mediante
lista de campos permitidos, sin referencias, fuentes ni nombres originales.
Validar particiones globales antes de exportar. Medios admitidos: PNG/JPEG y
MP4/WebM; DICOM se bloquea en esta primera entrega y remite al renderizador
existente hasta revisar desidentificación, geometría y series completas.

La ingesta trabaja sobre copias temporales acotadas, verifica firma/extensión,
tamaño/SHA-256 y decodificación con herramientas locales; nunca descarga URLs.
Se conservan solo metadatos técnicos permitidos. Esto no desidentifica píxeles:
material real requiere autorización y revisión humana de metadatos, píxeles y
vídeo completo, asociadas al hash exacto. Los códecs necesitan aislamiento del SO
antes de aceptar cargas hostiles en un servicio. No se habilita ningún endpoint.

Adaptadores ECG, POCUS, radiografía y TC/RM describen representación, contexto
técnico y límites. Fotogramas extraídos conservan origen, orden y tiempo y son
solo navegación; no demuestran compresibilidad, deslizamiento ni otro signo temporal.
No se envían archivos a proveedores externos.

## Ejecución y aceptación — lista original de alcance

- [ ] Tests negativos primero: corrupción, formatos, rutas, límites, privacidad,
  contaminación entre particiones, referencias en entrada y vídeo temporal.
- [ ] Ingesta local y adaptadores con pruebas de decodificación sintética.
- [ ] Banco estructurado: docencia, desarrollo y examen ciego; todos los derivados
  de un paciente/estudio/fuente permanecen en una partición.
- [ ] Evaluación: reutilizar `calculate_blinded_image_metrics.py`; comprobar casos
  reales admisibles, versión/congelación y revisión humana de errores críticos.
  Sintéticos solo prueban software; no producen rendimiento diagnóstico.
- [ ] Demo reproducible con PNG/JPEG/MP4 sintéticos y resultados persistibles;
  WebM se comprueba por separado con material fabricado.
- [ ] Suite Python y validadores pertinentes; auditoría Claude Code o Gemini real.
- [ ] Informe con inventario observado, resultados y revisiones humanas pendientes.

## Decisiones de implementación

El propietario ya autoriza implementar; se ejecuta en esta sesión Codex. Se elige
una CLI local porque el transporte clínico y el contrato de vídeo no están
validados. Interfaz asistencial, nuevas descargas y entrenamiento quedan fuera.
Se conserva la política de suprimir métricas binarias si hay abstenciones.
No cambiar estados de evidencia, fármacos, contratos ni ramas protegidas.

## Riesgos a verificar

1. Archivos corruptos o con extensión falsa no pueden registrarse como válidos.
2. Un recorte o fotograma no puede convertirse en paciente independiente.
3. El export ciego no puede contener referencia, URL diagnóstica ni metadatos libres.
4. Una revisión parcial de vídeo no acredita privacidad completa ni función temporal.
5. Datos sintéticos o referencias incompletas no pueden producir métricas clínicas.
