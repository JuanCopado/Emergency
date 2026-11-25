# R92 · Regresión pediátrica combinada

Estado: **PASS** en React y navegador local real sobre el árbol combinado.
La ejecución final del SHA publicado se identifica en el recibo y en el JSON
del artefacto `route-navigation` de su CI; este corte no anticipa resultados.

El flujo comprobado es `/pediatrics` → seleccionar paracetamol y su pauta →
cambiar filtro a fluticasona → Atrás → Adelante → recargar → enlace interno.

| Verificación | Resultado observado |
| --- | --- |
| Acceso directo sin parámetros | PASS; filtro y pauta vacíos, 89 pautas disponibles |
| Selección de paracetamol | PASS; filtro paracetamol, pauta paracetamol-pain-fever-home y formulario |
| Cambiar a fluticasona | PASS; filtro fluticasone-propionate, pauta vacía y sin formulario anterior |
| Atrás | PASS; recupera paracetamol, su pauta y formulario |
| Adelante | PASS; recupera fluticasona sin pauta incorrecta |
| Recarga del filtro | PASS; conserva fluticasona sin pauta |
| Enlace directo a la pauta y recarga | PASS; deriva filtro paracetamol de la pauta |
| Enlace interno desde Inicio | PASS; abre el módulo canónico |
| Catálogo completo | PASS; IDs exactos de 89 pautas y 52 familias, todos los filtros |

Reproducción antes/después: el test React existente de PR104 falla al importar
una copia del componente original de `bba8827` y pasa con PR104. Las copias de
prueba se eliminan; `RegimenForm` nunca se modifica. Logs: `pediatric-before.log`
y `focal.log`.

El arnés `node scripts/check-route-navigation.mjs` ejecuta 106 estados positivos,
incluidos nueve de historial con identidad del módulo y salud del navegador;
513 enlaces registrados y once controles negativos. Conserva los siete
negativos anteriores y añade:

- HTTP 404 real con HTML de la aplicación y módulo renderizado: rechazado.
- Encabezado correcto con controles propios incompletos: rechazado.
- Excepción real de JavaScript en el navegador: rechazada.
- Bloqueo real de la descarga del chunk pediátrico en página nueva: rechazado,
  con solicitud abortada y errores observados.

Los soft-404 con HTTP 200 y «Página no encontrada» siguen rechazados. Ningún
conteo de controles del marco ni un 200 de la SPA acredita identidad clínica.
Los cinco escenarios existentes de formulario con API canónica real pasan.

Entorno local: Chromium/Linux 154.0.8037.57, 127.0.0.1:4180, escritorio
1280×720 y móvil 375×812. Browser app no expone su herramienta JS en esta sesión;
se utiliza el arnés Playwright reproducible del repositorio para la validación
de navegador y CI pedida por el propietario. Sin nuevas dependencias.
Capturas y JSON se entregan fuera del árbol: `navigation-final.json` y
`screenshots/`. No se certifican Edge/Chrome Windows ni accesibilidad clínica.

CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE.
