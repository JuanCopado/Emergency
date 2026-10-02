# RAG clínico — contrato de diseño

## Objetivo
Recuperar únicamente evidencia autorizada y trazable para apoyar módulos de urgencias/UCI.

## Catálogo de procedencia
El RAG debe resolver primero contra `clinical/references/evidence-sources.json`.
Cada chunk futuro heredará `source_id` y la relación con el módulo de origen.
No se admite un chunk sin fuente trazable.

Los campos de procedencia son: título, organización/autores, tipo de fuente,
URL/identificador persistente, versión, fecha de publicación, última verificación,
idioma, jurisdicción y licencia. Un valor desconocido se representa como `null`;
no se infiere.

Las fuentes históricas compuestas se marcan `compound_identity=true` y no deben
descomponerse automáticamente sin verificación documental.

## Corpus permitido
- guías y consensos oficiales;
- información regulatoria;
- revisiones sistemáticas seleccionadas;
- documentación propia validada;
- protocolos locales expresamente aprobados.

## No permitido
- datos de pacientes identificables;
- notas clínicas sin desidentificar;
- contenido de procedencia/licencia incierta para producción;
- respuestas de LLM tratadas como documentos fuente.

## Pipeline
```
query
 -> normalización clínica
 -> retrieval por source_id/módulo
 -> retrieval semántico
 -> reranking
 -> filtros por autoridad/fecha/idioma/jurisdicción
 -> top-k con metadatos
 -> respuesta con citas
```

## Seguridad
El RAG no puede modificar automáticamente un módulo clínico. Las discrepancias se
envían a la cola de actualización y requieren revisión humana.
