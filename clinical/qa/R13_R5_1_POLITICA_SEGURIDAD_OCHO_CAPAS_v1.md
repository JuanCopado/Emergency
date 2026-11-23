# R5-1 · política de seguridad por modalidad en ocho capas · v1.0

**22 de noviembre de 2026 · Estado global `CLINICALLY_PENDING` (129 GREEN / 2 YELLOW / 0 RED) · Sin GO_RELEASE**

| Campo | Valor |
|---|---|
| Versión | 1.0 (especificación; no es un cambio de producto) |
| Aprobación | `DEC-CLIN-R8-06A` (SÍ), registrada en [R12 · decisiones R8](R12_DECISION_MEDICA_R8_20261122.md), confirmada por el propietario el 22/11/2026. Sin firma física |
| Alcance aprobado | Política de seguridad en ocho capas, **prototipos inactivos** y **pruebas sintéticas**. R5-1 (P1) sigue **abierto** |
| Qué no es | No activa ningún comportamiento clínico, no cambia dosis, cálculos, encaminamiento, filtros ni abstenciones, y no resuelve R5-1 por sí sola |

## Procedencia (exacta y sus límites)

- **Texto operativo:** reproducido por el propietario, Dr. Juan Copado Ceballos, en la instrucción **«EMERGENCY R13 — CLAUDE CODE»** de la sesión del 22/11/2026, como contenido operativo aprobado. Las ocho capas de abajo siguen esa redacción; el orden y los números son los de la instrucción.
- **Referencia científica citada por la instrucción:** `R11_GEMINI_M10_DECISIONES_CLINICAS_RESTANTES`. **Consolidación citada:** `R12_GEMINI_TRES_DECISIONES_P1_FINALES`.
- **Esos dos expedientes no están en el repositorio y no se han recibido en la sesión en que se incorpora esta política.** Su texto íntegro y las fuentes primarias que contienen son **No verificados** aquí: esta especificación recoge solo lo reproducido en la instrucción. La propuesta anterior de Gemini que cita [R8](R8_M10_R5_CONTRATOS_PROPUESTOS_20261121.md) (v1.3) no es una aprobación médica y no se usa como fuente de esta versión.
- Una política aprobada no es una validación clínica: `CLINICALLY_PENDING` sigue vigente.

## Las ocho capas

1. **Puntos de entrada específicos por modalidad.** Separar piel/heridas, ECG, radiografía, POCUS y documentos, evitando un buzón genérico ambiguo.
2. **Selección explícita sin valor predeterminado.** Estado inicial sin categoría; impedir el envío hasta que el usuario elija expresamente una modalidad.
3. **Vista previa antes del envío.** Mostrar la imagen seleccionada junto a la modalidad de destino.
4. **Confirmación contextual.** Botón específico «Confirmar y enviar como ECG», «Confirmar y enviar como POCUS», etc.; ofrecer «Cambiar modalidad». La confirmación humana no equivale a verificación objetiva del contenido.
5. **Contratos independientes por modalidad.** Mantener validadores y formatos específicos. Prohibido aplicar indiscriminadamente el filtro dermatológico a ECG, Rx o POCUS.
6. **Limitaciones fijas específicas.** La interfaz debe explicar claramente el alcance de cada modalidad sin permitir al modelo inventar cláusulas de seguridad. Preservar legibilidad móvil.
7. **Abstención neutral** ante incompatibilidades técnicas demostrables o modalidad no declarada. No utilizar RGB, EXIF, nombres de archivo ni la ausencia de DICOM como prueba clínica de modalidad.
8. **Evaluación independiente.** Pruebas técnicas adversarias y protocolo de usabilidad con profesionales, imágenes sintéticas y medición de errores humanos residuales.

## Estado real de cada capa en el repositorio

| Capa | Estado | Evidencia o límite |
|---|---|---|
| 1 · Entradas por modalidad | **Prototipo inactivo** (PR de R13, bandera apagada) | La interfaz vigente sigue con un buzón genérico y el selector con «Outro» por defecto |
| 2 · Sin valor predeterminado | **Prototipo inactivo** | Vigente: estado inicial «Outro»; el servidor ve «Outro» elegido y «Outro» por defecto como iguales (la interfaz envía `undefined`) |
| 3 · Vista previa | **Prototipo inactivo** | Hoy no hay vista previa antes de enviar |
| 4 · Confirmación contextual | **Prototipo inactivo** | La confirmación humana no verifica el contenido; el texto lo dice |
| 5 · Contratos independientes | **Parcial, ya vigente en el servidor** | El filtro de lenguaje tranquilizador se aplica solo a `skin_wound` (`guard_not_applied_to_other_kinds`); cada categoría tiene su ruta de módulos. Falta una prueba de la propiedad desde la interfaz |
| 6 · Limitaciones fijas | **Mecanismo en prototipo; textos pendientes de redacción médica** | Los textos de cada modalidad los redacta y aprueba el propietario; el modelo no genera cláusulas. La cláusula parcial en inglés de `SKIN_WOUND_FIXED_LIMITATIONS` no se añade hoy en las abstenciones del proveedor |
| 7 · Abstención neutral | **No implementada** | La Fase A registra solo datos (`kind_assessment`, `modality_verification=not_verified`); no abstiene. Con metadatos casi nada es «demostrable» como incompatibilidad. Definir «modalidad no declarada» y la abstención requiere decisión médica (`DEC-CLIN-R7-06`) |
| 8 · Evaluación independiente | **No realizada** | Solo el protocolo de partida; sin pruebas adversarias ni usabilidad con profesionales ejecutadas |

## Relación con las decisiones y el corpus

- Fase A (`DEC-CLIN-R10-FASE-A`): datos, ya fusionada. Fase B (`DEC-CLIN-R10-FASE-B`): avisos visibles **desactivados**; esta política no los activa.
- La capa 7 y el nivel 2 (opciones 2A–2E) siguen pendientes de decisión médica expresa; no se infiere esa decisión de la aprobación de 06A.
- R5-2 (corpus ciego, `DEC-CLIN-R8-06B`) es independiente de esta política; el protocolo está en `qa/corpus/blind/PROTOCOL.md`.

## Riesgos residuales conocidos

- La confirmación humana de la modalidad **no impide** enviar una imagen que no corresponde a la modalidad elegida; reduce el error por omisión de categoría, no el error de juicio.
- Con la bandera apagada (estado actual) **R5-1 sigue abierto**: una foto de piel con categoría errónea sigue sin filtro.
- Legibilidad móvil de la capa 6 sin evaluar; errores humanos residuales sin medir (capa 8).
