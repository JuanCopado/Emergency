# RAG clínico — contrato de diseño

## Objetivo
Recuperar únicamente evidencia autorizada y trazable para apoyar módulos de urgencias/UCI.

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
 -> retrieval
 -> reranking
 -> filtros por autoridad/fecha/idioma
 -> top-k con metadatos
 -> respuesta con citas
```

## Metadatos mínimos
Cada documento debe conservar:
- título;
- organización/autores;
- URL o identificador persistente;
- fecha/versión;
- fecha de verificación;
- idioma;
- jurisdicción;
- licencia/uso;
- módulos afectados.

## Seguridad
El RAG no puede modificar automáticamente un módulo clínico. Las discrepancias se envían a la cola de actualización y requieren revisión humana.
