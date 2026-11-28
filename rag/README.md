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

Las fuentes históricas compuestas se marcan `compound_identity=true` y no deben descomponerse automáticamente sin verificación documental. Las fuentes ya separadas y verificadas quedan registradas en `clinical/references/evidence-source-overrides.json`.

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

## Primer paso ejecutable de recuperación sintética

El [laboratorio de contenido](CONTENT_LABORATORY.md) añade un índice local y
respuestas extractivas con citas sobre gobernanza propia expresamente autorizada
y fixtures inventados separados. Comprueba permisos, integridad, versiones,
caducidad e inyección documental; no genera decisiones clínicas ni amplía derechos
de originales externos.

La [CLI de procedencia](SYNTHETIC_PROVENANCE_PROTOTYPE.md) recupera metadatos
canónicos por identificadores sintéticos y devuelve citas/versiones exactas con
abstención. Reutiliza el grafo existente; no recupera textos fuente ni genera
respuestas clínicas. El contrato local no concede derechos de producción ni
cierra G05. Se conserva `CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE`.

## Conciliación T01 con v1.44

Cada módulo conserva su identidad completa del registro canónico, incluso cuando comparte URL con otros módulos. Las fuentes de `evidence-source-overrides.json` se importan de una instantánea histórica de main como `historical_component_pending_reconciliation`; se añaden junto a la relación `canonical_registry_identity` y no la sustituyen. No acreditan por sí mismas cobertura actual del módulo, aprobación, licencia de producción ni conciliación clínica. Las identidades compuestas permanecen pendientes. Los IDs derivados de identidades canónicas incluyen título, URL, versión y fecha histórica; no son IDs de aprobación ni un contrato publicado de RAG.
