# Siguiente incremento propuesto: TREATMENT acotado

Recomiendo E3 TREATMENT como siguiente incremento individual: acceso explícito al panel terapéutico ya existente desde el flujo FAST/NOTE y resumen de alcance/revisión del plan actual. Es una recomendación documental; no se implementa ni autoriza aquí. No genera nuevas pautas, no cambia cálculos y no convierte una sospecha en diagnóstico establecido.

La utilidad esperada es reducir la búsqueda y la lectura de confirmaciones al preparar una nota, aprovechando cinco secciones, procedencia SHA, revisión y exportación ya conectadas. No hay medición de ahorro ni comparación clínica prospectiva. La elección se apoya en menor brecha de integración respecto a las otras dos opciones, no en un puntaje inventado.

| Opción e IDs existentes | Reutilización y utilidad individual | Brecha, riesgo y distribución E | Disposición |
|---|---|---|---|
| TREATMENT, E3.01–E3.04 | Panel de cinco secciones; selección explícita de indicación; edición y revisión; procedencia; rutas therapy/catalog, suggest, validate y medication/preflight presentes en backend individual. Da continuidad a NOTE. | Plan parcial y cobertura limitada; resumen no puede llamarlo prescripción completa. Interacciones no evaluadas no equivalen a ausencia de interacciones. La presencia de ruta no acredita ejecución funcional nueva en E. | Elegir incremento de navegación/resumen, sin reescribir motor. |
| DISCHARGE, E4.01–E4.03 | Catálogo, alertas, calculador y exportador pediátricos existentes; valor al preparar documentación domiciliaria. | No hay contrato integral de informe profesional e instrucciones separados. Ampliar a toda edad/patología añadiría contenido y decisiones; alta, duración, producto y destino no se infieren. E ofrece calculate/export pediátricos, no alta universal. | Aplazar el nuevo flujo universal; conservar acceso al módulo actual. |
| TESTS, E5.01–E5.05 | PDF textual/TXT y candidatos revisables en calculadoras ya disponibles; utilidad para transcripción localizada. | E no empaqueta T05/T06 ni permite inferir OCR/DICOM/interpretación de imágenes. Unificar pruebas abre retención, muestras/unidades, múltiples resultados y capacidades ausentes. E5.01 es posible candidato posterior estrictamente textual, no interpretación global. | Aplazar hub universal; no desactivar las capacidades existentes. |

## Límite concreto del incremento recomendado

Reutilizar E3.01/E3.02: un acceso identificable a tratamiento dentro del flujo existente y un resumen legible que diferencie referencia, plan parcial, pendiente de revisión y revisión válida del contenido actual. El resumen procede del estado existente, no de un nuevo clasificador ni LLM. E3.03 conserva cobertura/STOP actuales; E3.04 conserva los 19 contratos y sus aceptaciones. No exigir otra aceptación clínica general ya otorgada.

Antes de editar, localizar el punto único de acceso existente y evitar duplicarlo; comprobar que la intención diagnóstica explícita puede representarse sin modificar contratos. Si el estado actual no permite afirmar diagnóstico establecido, mantener referencia/plan parcial y no fabricar una bandera clínica nueva silenciosa. La integración requiere revisión del delta y QA focal por SHA; esta recomendación no demuestra compatibilidad instalada ni incluye nuevo E/H o ciclo de instalación.

Quedan fuera: prescripción universal, combinación de hipótesis, cobertura global de interacciones, nuevas dosis o traducciones de contenido clínico, servicios remotos, persistencia, multiepisodio, automatización del alta, órdenes/envíos y requisitos hospitalarios universales. País y hospital sólo se exigen donde cambien el contrato concreto. CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE.

## Criterios sintéticos propuestos, no ejecutados

1. Entrar desde NOTE al panel existente y regresar conserva original/propuesta/final y edición local; no crea plan ni sustituye texto por navegar.
2. Una sospecha o selección de catálogo no aparece como diagnóstico establecido ni plan individual completo; no se combinan tratamientos de dos hipótesis.
3. Cinco secciones incompletas/revisión pendiente conservan ese estado y las guardas existentes; el resumen no habilita exportación que el contrato niega.
4. Editar sección o cambiar contexto/fuente relevante invalida la revisión según contrato existente; no reutiliza sello de contenido anterior.
5. Fuente y alcance son accesibles; falta de cobertura de interacciones aparece no evaluada, sin semáforo global ficticio.
6. Datos/producto/concentración necesarios ausentes conservan bloqueo de cálculo dependiente; no se agregan cifras nuevas para completar el resumen.
7. Caso sintético sin backend/catálogo muestra fallo recuperable y conserva la nota; no inventa resultado ni promete una función T05/T06 ausente.
8. Navegación y revisión con teclado y ancho estrecho se comprueban en el delta, sin declarar WCAG global ni repetir suites ajenas al cambio.

## Fuentes y límites de lectura

- Source de producto leído: GMFC_FAST_NOTE_20261128/candidate, HEAD a4fe1e2c509c188111c6216b31d6b592f8c4baa6; no se infiere que esté integrado. AGENTS.md, STATE.md (corte inicial/historia), CODEX.md y docs/INTERNATIONAL_SCOPE.md fijan alcance individual/internacional y conservación de contratos.
- Guía aceptada recuperada: GMFC_20261128/proposal/docs/implementacion/GUIA_MAESTRA_FLUJO_CLINICO.md:31–33,48–52. La aceptación comunicada por Root se distingue del texto histórico de propuesta.
- Inventario ya revisado, sin regenerarlo: gmfc/REVISION_TECNICA.md:180–275 e INVENTARIO_TECNICO.json IDs E3/E4/E5. Reutilizados estados y localizadores; no se repiten las 37 lecturas ni se actualiza inventario.
- UX previa: gmfc/REVISION_UX_CLAUDE.md:157–158; falta resumen legible y alta propia. Criterios clínicos de alcance: gmfc/REVISION_CLINICA_ALTERNATIVA.md, S05/S07/S08; atribución Codex, no respuesta Gemini completa.
- Cotejo focal source actual: app/src/clinical-note/TherapeuticPlanPanel.tsx:6–17,27–73 (props/estado, selección, cinco secciones, referencia/revisión); tools/local-installation/backend_runtime.py:20–29 (allowlist). Confirma presencia estática, no nueva prueba de E.
- Cotejo focal E5.01: app/src/components/ScoreDocumentInput.tsx:16–43,47–67 (muestras, candidatos, PDF/TXT, fuente y ambigüedad). No prueba precisión clínica ni convierte el componente en hub universal.

Sin pruebas, red clínica, investigación de nuevas recomendaciones, píxeles/PHI, cálculos ni cambios de repositorio/CENTRAL. Herramienta efectiva: exec_command para lecturas locales y git rev-parse; no se atribuye uso de Emergency/GitHub/DevTools MCP ni ahorro medido a esta revisión.
