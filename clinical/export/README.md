# Clinical export / printable guides

## Objetivo

Permitir que Emergency transforme contenido clínico canónico ya revisado en una guía visual apta para:

- pantalla completa;
- impresión;
- guardado como PDF desde el navegador;
- uso como algoritmo rápido o guía de 2–4 páginas.

## Regla de seguridad

La exportación NO genera contenido clínico nuevo. El renderer solo debe consumir contenido canónico existente en `clinical/modules/`, calculadoras deterministas y registros de evidencia.

No se permite:

- inventar dosis, energías, concentraciones o parámetros;
- promover YELLOW a GREEN por exportar;
- ocultar fecha, fuente o estado de revisión;
- mezclar módulos sin trazabilidad.

## Formatos

1. **Algoritmo rápido** — objetivo una página.
2. **Guía clínica** — 2–4 páginas cuando el contenido lo requiera.
3. **Guía procedimental** — puede incorporar una ilustración visual ya aprobada.

## UI inicial

Ruta: `/guides`

Acciones:

- **Pantalla completa**
- **Imprimir / guardar PDF**

La primera implementación utiliza CSS de impresión y `window.print()`, evitando añadir una dependencia PDF. El navegador permite seleccionar impresora física o "Guardar como PDF".

## Guías iniciales

- FV / TV sin pulso → `adult-cardiac-arrest`
- Asistolia / AESP → `adult-cardiac-arrest`
- Coma / alteración del nivel de conciencia → `altered-consciousness`

Estas guías son YELLOW y conservan trazabilidad al módulo canónico.
