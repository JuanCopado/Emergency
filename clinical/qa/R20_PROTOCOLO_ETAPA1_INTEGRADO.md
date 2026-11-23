# Etapa 1 de factores humanos · protocolo integrado (Gemini R20 v1.0) y correspondencia con la herramienta

**23 de noviembre de 2026 · `CLINICALLY_PENDING` · estudio `NOT_EXECUTED` (sin reclutamiento ni datos) · R5-1 (P1) abierto**

Integra por referencia el protocolo científico `R20_GEMINI_PROTOCOLO_ETAPA1`, el plan `R20_GEMINI_PLAN_ESTADISTICO` y la conciliación `R20_GEMINI_CONCILIACION_FINAL` (informe consolidado `R20-CONSOLIDADO v1.0`, aportado por el coordinador; los originales no se copian al repositorio). Base: `DEC-CLIN-R19-01` ([registro](R20_DECISION_MEDICA_R19_01_20261123.md)). Complementa el [protocolo base](R14_PROTOCOLO_FACTORES_HUMANOS_R5_1.md). Gemini clasifica el ensamblaje del banco, el reclutamiento y la ética como `BLOCKED`; esta integración no los desbloquea.

## Qué fija el protocolo R20 (resumen fiel)

- **Participantes (Etapa 1):** Grupo 1 médicos de urgencias/familia; Grupo 2 enfermería de urgencias/curas/triaje; exclusión de quien diseñó o revisó PR82/PR83; consentimiento informado. Tamaño: **sin tamaño confirmatorio**; referencia formativa 5–8 por iteración/grupo o al menos 15 por grupo distinto (FDA HFE/IEC 62366-1) para caracterización preliminar; **reclutamiento no iniciado**.
- **Diseño:** cruzado AB/BA 1:1, bloques permutados estratificados por grupo profesional, lengua (ES/PT/EN) y dispositivo inicial; dos bancos de estímulos disjuntos e isomórficos (Set 1/Set 2) contrabalanceados; *washout* de al menos 10 minutos; sin entrenamiento sobre los escenarios adversariales.
- **Escenarios:** A (herida bien elegida), B/C/D (herida inyectada en ECG/Rx/POCUS), E1 (T7-01), E2 (T7-03/T7-04), F (fotos móviles RGB legítimas de ECG/Rx/POCUS y documento, con 0 % de falsos bloqueos técnicos).
- **Dispositivos:** móvil estrecho 360×640 y 390×844 (más +15 % de escala de accesibilidad) y escritorio; intra-participante balanceado de preferencia.
- **Registro:** identificadores opacos (`participant_opaque_id`), consentimientos custodiados aparte, telemetría sin PII; adjudicación independiente (dos adjudicadores y un tercero; κ de Cohen y AC₁ de Gwet antes del análisis); parada inmediata ante fuga de PII/PHI o exposición asistencial; dictamen o exención ética previa.
- **Variables:** error de selección, detección antes del envío, confirmación errónea, bypass residual (primaria), falsas cancelaciones, riesgo por participante, *close calls*, tiempo y Δt, comprensión (3 ítems) y entrevista de causa raíz.

## Correspondencia con `human_factors_tools.py` (hf-tools-0.3)

| Requisito del plan estadístico R20 | Estado en la herramienta |
|---|---|
| Remuestreo de participantes completos, estratificado AB/BA, ≥ 5.000 réplicas, semilla registrada | **Implementado** |
| Intervalo BCa principal; percentil secundario | **Implementado** (`cluster_bootstrap_bca_95`, `primary_interval`) |
| `small_cluster_warning` con P < 30 | **Implementado** (30 = referencia de la literatura, no umbral del estudio) |
| Bloques `trial_level_metrics` y `participant_level_metrics` separados | **Implementado** |
| Nivel participante: Clopper-Pearson exacto sobre P y McNemar exacto | **Implementado** (exploratorio; sin veredicto) |
| Cero eventos: `zero_event_degeneracy_flag`, recuentos `0/N` y `0/P`, cota exacta sobre P etiquetada, sin Clopper-Pearson sobre `0/N` | **Implementado** |
| ρ̂ (ANOVA) y DEFF descriptivo; `stage2_planning_inputs` | **Implementado** |
| Sensibilidad del periodo 1 (descriptiva, sin conmutación condicional) y prohibición del pretest de *carryover* | **Implementado** (`carryover_pretest = PROHIBITED_NEVER_PERFORMED`) |
| Modelo primario GLMM / alternativa GEE con varianza robusta de muestras pequeñas | **No implementado** (solo biblioteca estándar): `crossover_and_device_models.status = NOT_IMPLEMENTED_STDLIB_ONLY`; requiere un paquete estadístico en el entorno del estudio |
| Efecto de dispositivo (interacción β₅; contraste móvil−web pareado) | **Parcial:** resultados por plataforma; contraste y modelo con interacción pendientes |
| `acceptance_decision = PENDING_PHYSICIAN_OWNER_REVIEW`, sin umbrales ni tamaño | **Implementado** |
| Salida sellada con `git_commit_sha`, hashes del manifiesto y de los datos | **Implementado** (`export`) |
| Etiqueta `NOT_EXECUTED_PROTOCOL_ONLY` | La herramienta emite `NOT_EXECUTED_TOOLING_ONLY` (equivalente: ningún estudio ejecutado) |

## Bloqueos de la Etapa 1 (sin cambios)

Banco sintético sin ensamblar ni congelar (`HF_ETAPA1_STIMULI_SHA256.txt`); sin dictamen o exención ética; sin auditoría independiente local de PR82/PR83; sin *dry-run* de captura anonimizada; interfaz de captura del estudio no implementada; medición móvil real pendiente (el diseño es `PASS`; la medición sigue `NO VERIFICADO`). Etapa 2: sin `N`, márgenes ni umbrales; requiere nueva decisión médica explícita.

## Capa 7 · denominaciones de Gemini (conciliación R20, sección 2.1)

| Mensaje Gemini | Identificador canónico (contrato) | Disparador(es) | Subcódigo Gemini |
|---|---|---|---|
| `MSG_T7_NO_MODALITY` (Texto 1) | `MSG_T7_A` | T7-01, T7-02 | `explicit_flow_missing_selection`, `unknown_or_unsupported_contract_id` |
| `MSG_T7_INCOMPATIBLE_MODALITY` (Texto 2) | `MSG_T7_B` | T7-04 | `modality_container_incompatible` |
| `MSG_T7_CORRUPT_FILE` (Texto 3) | `MSG_T7_C` | T7-03 | `zero_bytes_or_decode_or_pr66_limit` |
| `MSG_T7_UNSUPPORTED_FORMAT` (Texto 4) | `MSG_T7_D` | T7-04 | `global_unsupported_format` |

Los doce textos coinciden con los del informe Gemini (es, pt AO90 y en). El informe añade una variante `pt-BR` («arquivo» en lugar de «ficheiro»): **no se aplica** porque la aplicación no tiene configuración regional pt-BR (locales `pt`, `es`, `en`, `zh`) y la variante no figura en los textos aprobados comunicados por el propietario; el núcleo portugués común AO90 se conserva.
