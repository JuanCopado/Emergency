# Emergency · R12 · registro de decisiones médicas (R8-06A, R8-06B, R8-03)

**22 de noviembre de 2026 · Estado global `CLINICALLY_PENDING` (129 GREEN / 2 YELLOW / 0 RED) · Sin GO_RELEASE**

Registro de tres decisiones metodológicas del médico propietario, Dr. Juan Copado Ceballos, sobre las propuestas de [R8 · contratos propuestos](R8_M10_R5_CONTRATOS_PROPUESTOS_20261121.md) y la [ficha residual R7](R7_M10_R5_RESIDUAL_FICHA_20261121.md). Se registran tal como las comunicó. No se vuelven a solicitar. Este documento solo las registra; no modifica ningún resultado clínico ni las aprobaciones anteriores ([R10 · Fases A y B](R10_DECISION_MEDICA_FASE_A_B_20261122.md)).

## Origen

Constan en la instrucción **«EMERGENCY R12 — NUEVAS DECISIONES DEL MÉDICO PROPIETARIO»**, recibida en la sesión de trabajo del 22 de noviembre de 2026. El texto original no se conserva en el repositorio; la trazabilidad es esta entrada y la fecha de la sesión. No existe firma física ni documento aparte; si el propietario quiere otra forma de constancia, puede añadirla, y no se presupone.

## Decisiones (texto comunicado)

| ID | Decisión | Texto comunicado |
|---|---|---|
| `DEC-CLIN-R8-06A` | **SÍ** | «Política de seguridad en ocho capas, prototipos inactivos y pruebas sintéticas. R5-1 sigue P1 abierto.» |
| `DEC-CLIN-R8-06B` | **SÍ** | «Corpus ciego R5-2 independiente, cuatro estratos, siete clases y adjudicación. Ninguna regex nueva autorizada.» |
| `DEC-CLIN-R8-03` | **SÍ, cinco estados** | «Incorporar "No aplicable" únicamente al contrato inactivo y cuando se confirme ausencia de la premisa clínica del signo. Fase 2 bloqueada.» |

## Alcance y límites

- **06A.** Autoriza una política de seguridad **en ocho capas**, en forma de prototipos **inactivos** y con pruebas **sintéticas**. No activa ningún comportamiento clínico. R5-1 (P1) sigue abierto. **La definición de las ocho capas no consta en el repositorio** (Inferencia: procede de la propuesta científica de Gemini citada en R8, que no es una aprobación médica y no está disponible aquí); no se implementa ningún prototipo de la política hasta disponer de su texto, para no inventarla.
- **06B.** Autoriza el protocolo de un corpus ciego e independiente, con cuatro estratos de idioma (es-ES, pt-PT, pt-BR, en), siete clases y adjudicación. **Ninguna regex nueva autorizada.** No se ha construido corpus ni designado adjudicadores. R5-2 sigue abierto. Implementación: [PR #79](https://github.com/JuanCopado/Emergency/pull/79).
- **03.** Incorpora el quinto estado `not_applicable` («No aplicable») **solo** al contrato inactivo de Fase 1 y **solo** cuando se confirma la ausencia de la premisa clínica del signo. Las premisas concretas de cada signo siguen pendientes de redacción médica. Fase 2 bloqueada. Implementación: [PR #78](https://github.com/JuanCopado/Emergency/pull/78).

## Qué no cambia

- No se activa la Fase B, ni las opciones 2A–2E, ni clasificación visual ni expresiones regulares nuevas.
- No se conecta nada al producto; no cambian dosis, cálculos, filtros ni abstenciones.
- Ninguna de estas decisiones autoriza fusionar sin CI ni auditoría independiente del commit exacto.
- C12, G05 y RAG siguen pendientes o bloqueados.
