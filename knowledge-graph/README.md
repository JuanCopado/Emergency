# Knowledge graph

Esta capa representa **metadatos y trazabilidad**, no conocimiento clínico inferido automáticamente.

## Fuentes normalizadas
`clinical/references/evidence-sources.json` es el catálogo normalizado derivado de
`evidence-registry.json`. Separa la identidad de la fuente de la relación
módulo→fuente y admite múltiples fuentes por módulo.

Cada fuente conserva estos campos, aunque el valor sea `null` si no está
verificado: organización, tipo, URL, identificador persistente, versión, fecha de
publicación, última verificación, idioma, jurisdicción y licencia.

Regla importante: una cita histórica que combina varias fuentes en un único texto no se divide automáticamente. Se marca `compound_identity=true` hasta que sus componentes se verifiquen individualmente. Las separaciones verificadas se guardan en `clinical/references/evidence-source-overrides.json`; el normalizador aplica esas excepciones de forma determinista. Es preferible conservar incertidumbre estructurada a inventar metadatos.

Regenerar/comprobar:
```bash
python3 clinical/scripts/normalize_evidence_sources.py
python3 clinical/scripts/normalize_evidence_sources.py --check
```

## Grafo determinista
`clinical/scripts/build_project_graph.py` genera relaciones verificables desde:
- `clinical/references/module-index.md`
- `clinical/references/evidence-registry.json`
- `clinical/references/evidence-sources.json`

Tipos:
- `clinical_module`
- `module_bundle`
- `evidence_source`

Relaciones:
- `LOCATED_IN`
- `SUPPORTED_BY`, con `role` y `claim_scope`.

El generador falla si manifiesto, registro de evidencia y mapa de fuentes no
contienen exactamente los mismos módulos o si una relación apunta a una fuente
inexistente.

## Siguiente fase
Separar progresivamente las fuentes compuestas verificando cada guía/consenso
individual y después añadir una ontología clínica controlada para síndrome,
fármaco, dosis, prueba, hallazgo, procedimiento, contraindicación y recomendación.
Las relaciones clínicas nuevas requieren revisión humana antes de incorporarse.

## Conciliación T01 con v1.44

Cada módulo conserva su identidad completa del registro canónico, incluso cuando comparte URL con otros módulos. Las fuentes de `evidence-source-overrides.json` se importan de una instantánea histórica de main como `historical_component_pending_reconciliation`; se añaden junto a la relación `canonical_registry_identity` y no la sustituyen. No acreditan por sí mismas cobertura actual del módulo, aprobación, licencia de producción ni conciliación clínica. Las identidades compuestas permanecen pendientes. Los IDs derivados de identidades canónicas incluyen título, URL, versión y fecha histórica; no son IDs de aprobación ni un contrato publicado de RAG.
