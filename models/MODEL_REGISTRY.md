# Registro de modelos externos

Los modelos de Hugging Face u otros proveedores entran primero como **candidatos de evaluación**.

| Modelo/categoría | Uso previsto | Estado | Regla |
|---|---|---|---|
| MedGemma 1.5 4B IT | evaluación multimodal médica texto+imagen | candidate | no usar como diagnóstico autónomo |
| Biomedical embedding model | recuperación semántica | unselected | seleccionar por benchmark propio |
| Biomedical reranker | reranking de evidencia | unselected | seleccionar por benchmark propio |
| General LLM | síntesis/razonamiento | host-dependent | siempre detrás de safety/evidence gates |

## Criterios para promoción
1. licencia compatible;
2. dataset y población entendidos;
3. evaluación en español/portugués/inglés cuando aplique;
4. pruebas de regresión internas;
5. sensibilidad a información crítica;
6. tasa de falsa tranquilidad;
7. abstención apropiada;
8. revisión clínica humana.

Ningún modelo se marca como validado clínicamente por superar benchmarks técnicos.
