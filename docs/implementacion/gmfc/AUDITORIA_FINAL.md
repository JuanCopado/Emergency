# GMFC-AUDIT — Adenda Final Acotada de Auditoría Documental

**Referencia:** EMERGENCY GMFC-20261128 · Adenda Final
**Carácter:** Evaluación del incremento documental de la Guía Maestra v1.0 PROPUESTA y corrección formal de metadatos.
**Estado:** Los entregables previos (`AG/GMFC_AUDIT_PARTIAL.md` y `AG/GMFC_AUDIT_PARTIAL_RECEIPT.json`) permanecen íntegros e intactos como registro de la auditoría sobre la versión provisional 0.2.
**Dictamen de gobernanza:** `CLINICALLY_PENDING · NOT_FROZEN_NOT_VALIDATED · NO_GO_CLINICAL_RELEASE`.

---

## 1. Corrección Formal de Metadatos y Precisiones Documentales

Conforme al cotejo de coordinación (`COORD/DISPOSICION_AUDITORIA_PARCIAL.md`), se rectifican formalmente las siguientes precisiones métricas e interpretativas:

### 1.1 Corrección de bytes físicos (`(Get-Item).Length`) de los 7 archivos base
Los hashes SHA256 fueron exactamente concordantes (7/7). Los tamaños en bytes reportados en el recibo parcial correspondían a longitud de cadena/caracteres en memoria; los bytes físicos exactos en disco son:
1. `COORD/SINTESIS_PROVISIONAL.md`: **6.861 bytes** (rectifica 4.675).
2. `TECH/GMFC_TECH.md`: **40.577 bytes** (rectifica 31.810).
3. `TECH/GMFC_TECH_REQUIREMENTS.json`: **54.410 bytes** (rectifica 51.520).
4. `CLAUDE/GMFC_UX_ORIGINAL.md`: **24.494 bytes** (rectifica 18.061).
5. `COORD/COTEJO_CLAUDE_UX.md`: **4.053 bytes** (rectifica 2.766).
6. `GEMINI/CONTEXT_ERROR_RECEIPT.json`: **724 bytes** (rectifica 647).
7. `GEMINI/PARTIAL_DELIVERY_RECEIPT.json`: **1.001 bytes** (rectifica 913).

### 1.2 Delimitación estricta de telemetría MCP y alcance
- **`get_owner_decision` (`ABSTAIN`):** No demuestra ausencia de decisiones o autorizaciones previas del propietario; refleja únicamente que la solicitud ad-hoc fue rechazada o que el snapshot no estaba disponible en el servidor MCP local. No se infiere de ello ni revocación ni concesión de permisos.
- **`get_project_state` (`clinical_inference_performed = false`):** Describe exclusivamente el ámbito de ejecución de la herramienta MCP de metadatos en ese momento; no certifica la ausencia de inferencias en toda la aplicación ni supone validación clínica global.

### 1.3 Corrección de atribuciones textuales y normativas
- **Fórmulas y formularios:** La guía 0.1 no utiliza textualmente las expresiones «45 calculadoras FAST» ni «135 calculadoras»; menciona 45 fórmulas. La distinción entre 45 fórmulas de motor, 135 escalas del catálogo y 13 formularios aprobados expuestos en UI se mantiene plenamente válida como delimitación de diseño, sin atribuirla como cita textual errónea de la guía ni como fallo del producto.
- **Origen de restricción de insulina/labetalol:** La decisión `MED-DEC-R46-01/02` corresponde formalmente a procedimientos y al banco de imágenes dermatológicas, no al bloqueo farmacológico de insulina/labetalol. Dicho bloqueo dimana de los expedientes y acuerdos del encargo clínico de agudos, conservándose en su alcance propio sin atribuirlo a R46.
- **Ensayos A/B/A y PR142:** PR142 es una entrega puramente documental. La prueba A/B/A previa (D→E→D) correspondió a la verificación de actualización del paquete PWA/instalador, no a PR142 ni a una prueba de concurrencia de pacientes.
- **Ruta de preferencias:** La persistencia de preferencias de interfaz se localiza en `app/src/state/settings.tsx`, no en `pages/Settings.tsx`.
- **Divergencia entre texto libre y exportación:** Tener modelos distintos con avisos visibles no constituye un fallo técnico reproducido. No se debe imponer un bloqueo global inmediato de exportadores; la propuesta equilibrada consiste en permitir previsualizar y elegir conscientemente la versión revisada que se desea exportar.

---

## 2. Lectura y Verificación del Incremento Documental Final

Se ha leído y verificado físicamente el delta documental fuera de Git:

| Documento del incremento | Bytes (`Get-Item.Length`) | SHA256 verificado bit a bit | Función / Contenido |
|---|---|---|---|
| `COORD/GUIA_V1_PROPUESTA.md` | 17.643 | `5678ef4ea926a9dbe7fdcf116943eede68a28d4f0af0b11e36c4a1447ac8b8e2` | Guía Maestra de Flujo Clínico v1.0 PROPUESTA |
| `COORD/DISPOSICION_AUDITORIA_PARCIAL.md` | 3.576 | `ef715c0869ce875a8607aa8304c0d19254ee580683f4bd0c8c68a2d7499ffb98` | Matices y correcciones de coordinación a la auditoría 0.2 |
| `CLIN_ALTERNATIVE/GMFC_CLIN_GAP_CODEX.md` | 11.451 | `9efe33a0aaf7157e0162a254172aa8b5869296e450aeda916ff0d2aad598f44b` | Cobertura documental alternativa independiente de S04final–S10 |
| `CLIN_ALTERNATIVE/RECEIPT.json` | 3.793 | `ea50e697e82379e6877dde6530c8929ef376438df832e56b04d57752803f2fe1` | Recibo de aislamiento y fuentes de la alternativa Codex |

---

## 3. Disposición Precisa de la Brecha Clínica y Alternativa Atribuida

1. **Estado definitivo de Gemini:**
   La recuperación de contexto en Gemini concluyó sin persistencia de texto compacto en el hilo; no se realizarán más reenvíos. Se confirma documentalmente que la revisión clínica directa de Gemini abarca únicamente los casos **S01–S03 completos y S04 truncado**. No existe revisión clínica tripartita ni adjudicación médica formal sobre S04–S10.
2. **Atribución de la alternativa Codex:**
   La cobertura de los escenarios S04 final y S05 a S10 ha sido elaborada de forma independiente por Codex (`CLIN_ALTERNATIVE/GMFC_CLIN_GAP_CODEX.md`) a partir de la documentación y contratos autorizados (`GUIA_MAESTRA_FLUJO_CLINICO.md`, `THERAPEUTIC_PLAN_REVIEW_20261126.md`, `BLOOD_GAS_LOCAL.md`, `REVIEWED_ACUTE_CONTRACT_RELEASE_2026-11-16.md`, `CURRENT_STATE.md`).
   - Se atribuye estrictamente a **Codex como propuesta de diseño documental**.
   - **No es respuesta de Gemini**, ni constituye adjudicación médica o validación clínica prospectiva.
3. **Criterios de diseño consolidados para los 10 escenarios sintéticos:**
   - **S01 (Noradrenalina):** Retener edad/peso; bloqueo ante dosis objetivo o preparación ausente; rige el contrato canónico.
   - **S02 (Adrenalina / Anafilaxia):** Sin selección automática de vía ni dosis sin confirmar contexto e indicación.
   - **S03 (Hidrocortisona IV pediátrica):** Mantener 35 kg / IV; no inferir indicación ni aplicar algoritmos no contrastados.
   - **S04 (Fiebre / OMA 7 kg):** La tríada «7 kg + fiebre + OMA» no selecciona antibiótico, duración ni alta automática; concentración ausente no calcula mL; contrato OMA exacto clasificado como no verificado.
   - **S05 (Gasometría):** Duda de unidad o muestra no se convierte en dato confirmado; cambio de valor invalida dependientes; no forzar $\text{FiO}_2$ si la consulta no lo exige.
   - **S06 (Pluripatología):** Listas vacías no equivalen a «sin alergias» o «función renal normal»; estado de interacciones rotulado como «no evaluado / revisión requerida».
   - **S07 (Sospecha vs Diagnóstico establecido):** Sospecha genera referencia o borrador; el plan individualizado exige confirmación médica diagnóstica expresa; se preserva el apoyo determinista limitado sin promover YELLOW.
   - **S08 (Ambulatorio / Domiciliario):** Separar informe profesional de instrucciones legibles; el borrador no es receta ni alta autónoma.
   - **S09 (Polimedicación):** Cero alertas no certifica compatibilidad; cobertura limitada se explicita documentalmente.
   - **S10 (Reevaluación / Continuidad):** Aislamiento de versión por episodio; respuesta tardía de un caso no contamina otro; cambio de contexto revoca revisión dependiente sin borrar datos confirmados ajenos.

---

## 4. Dictamen Documental sobre la Guía Maestra v1.0 PROPUESTA

Tras contrastar `COORD/GUIA_V1_PROPUESTA.md` (SHA256 `5678ef4ea926a9dbe7fdcf116943eede68a28d4f0af0b11e36c4a1447ac8b8e2`):

1. **Integración de correcciones:**
   La guía v1.0 propuesta recoge puntualmente las observaciones y deslindes formulados:
   - Preserva los **19 contratos de genéricos previamente aceptados** y las **45 fórmulas deterministas**, delimitando los **13 formularios interactivos**.
   - Limita la restricción estrictamente a **preparaciones comerciales originales no identificadas** (insulina/labetalol), sin bloquear genéricos autorizados.
   - Conserva el **apoyo determinista limitado con guardas** en el backend sin deshabilitarlo, manteniendo los **2 módulos YELLOW sin promoción clínica**.
   - Mantiene el gestor multiepisodio como **PENDIENTE**, sin atribuir a la PWA capacidades de persistencia durable o aislamiento clínico que no posee.
   - Establece la necesidad de previsualizar y elegir la versión revisada antes de la exportación formal, sin imponer bloqueos prematuros.
   - Conserva la arquitectura local/híbrida sin exigir infraestructura hospitalaria o servidores remotos por defecto.
   - Mantiene la disciplina de proyecto: conserva los 12 IDs IMP existentes en CENTRAL, sin añadir colas paralelas ni fases inventadas.
2. **Evaluación de completitud material:**
   No se detectan omisiones documentales o contradicciones técnicas insalvables en el texto de la propuesta. La laguna clínica de Gemini queda expresamente declarada y transparentada en la propia guía mediante la atribución precisa a la alternativa documental Codex.
3. **Dictamen de suficiencia de alcance:**
   La Guía Maestra de Flujo Clínico v1.0 PROPUESTA se declara **DOCUMENTALMENTE APTA PARA SER PRESENTADA AL PROPIETARIO PARA LA DELIBERACIÓN Y DECISIÓN DE ALCANCE**.
   - Dicha aptitud se limita a la presentación de la propuesta de alcance.
   - **No constituye aceptación del propietario**.
   - **No habilita `MERGE_READY`**.
   - **No autoriza implementación de código, modificación de fuentes ni despliegue clínico**.

**Dictamen oficial ratificado:**
`CLINICALLY_PENDING · NOT_FROZEN_NOT_VALIDATED · NO_GO_CLINICAL_RELEASE`
