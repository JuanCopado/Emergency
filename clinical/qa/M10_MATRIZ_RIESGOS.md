# M10 · Matriz de riesgos — `skin-wound-image`

20/11/2026 · SHA base `21defd4` · Gravedad: C = crítica (daño al paciente plausible), A = alta, M = media. Probabilidad estimada **cualitativa** (no hay tasas medidas; no se inventan). Estado: Mitigado = control implementado y probado en esta rama; Parcial; Abierto.

| ID | Riesgo | Causa | Grav. | Prob. | Control actual | Estado | Hallazgo / prueba |
|---|---|---|---|---|---|---|---|
| R01 | **Falsa tranquilidad**: la salida llama «benigno / sin infección / descartado» a una lesión, o se interpreta ausencia de hallazgo como normalidad | El proveedor es texto libre; E1/E5 muestran que la IA errónea induce a error | C | Media-alta si se conecta un proveedor | Texto del módulo; marca `reassurance_language`, limitación visible y confianza retirada (regex) | Parcial (regex, sin medición de recall) | F06 · T6 |
| R02 | Infección necrosante o proceso grave no reconocido por foto (dolor desproporcionado, crepitación, profundidad no visibles) | Límite intrínseco de la fotografía (E6) | C | Media | Limitaciones fijas en toda salida `skin_wound`; módulo exige escalar toxicidad, necrosis, ampollas, mucosa | Parcial (depende de que el médico lea) | F06 · T6 |
| R03 | Rendimiento desigual por fototipo/iluminación | E3, E4; sin datos propios | A | Alta (si hay uso) | Aviso de tono/luz en el módulo; sin medición | Abierto | F13 · protocolo §5 |
| R04 | La foto de herida entra por la ruta equivocada y no se aplican las salvaguardas del módulo | Sin tipo `skin_wound` en UI/inferencia | A | Alta (antes) | Tipo añadido en API y UI; inferencia por nombre | Mitigado | F01 · T4 |
| R05 | Imagen corrupta/falsa/hostil llega a un tercero | Sin validación de contenido | A | Media | Guard de firma, estructura, CRC, EOF, píxeles máximos | Mitigado (PNG/JPEG/WebP) | F02 · T1 |
| R06 | Fuga de ubicación o identidad por EXIF/XMP/comentarios/datos añadidos | Se reenviaba el original | A | Alta (móviles escriben GPS) | Detección + eliminación antes del proveedor | Mitigado (PNG/JPEG/WebP); **DICOM/PDF abierto** | F03 · T7 |
| R07 | Rostro, tatuaje, pulsera o pantalla identificables en la foto | Foto clínica de piel suele incluirlos | A | Media | Revisión de identificadores incrustados obligatoria para todo binario | Mitigado (control humano) | F04 · T5 |
| R08 | Interpretación sobre imagen inservible (diminuta, uniforme, desenfocada, sin escala) | Sin puerta de calidad | M | Media | Resolución y PNG uniforme → abstención sin llamada; flags | Parcial (sin desenfoque/exposición/escala/JPEG-WebP uniforme) | F07 · T2/T3 |
| R09 | Abstención del proveedor percibida como fallo y reintentada hasta «obtener algo» | Contrato sin abstención | M | Media | `status:'abstain'` con motivo obligatorio y sin texto clínico; alerta en UI | Parcial (necesita soporte del proveedor; UI sin verificar en navegador) | F05/F12 · T5 |
| R10 | Entrada adversaria: texto incrustado en la imagen que da órdenes al modelo | Diseño del proveedor | A | Desconocida | Salida tratada como dato; barrera de identificadores; aceptación humana | Abierto (no medido) | protocolo §7 |
| R11 | Metadatos MIME/nombre manipulan el tipo o filtran identidad | Cliente no confiable | M | Baja-media | MIME por firma; nombre saneado | Mitigado | F08 · T7 |
| R12 | Mala ruta por nombre de archivo / regex de UI | Heurísticas por subcadena | M | Media | `explicit_kind` manda; UI antepone piel/herida | Parcial | F09/F11 |
| R13 | Se presenta un PASS técnico o un GREEN documental como precisión diagnóstica | Confusión de niveles | A | Media | Política de validación; M10 YELLOW; este expediente declara «no medido» | Mitigado (gobernanza) | Auditoría §2, §6 |
| R14 | Resultados irrazonables por salida sin esquema (calidad, urgencia, no evaluable) | Esquema no impuesto | M | Media | Ninguno en código | Abierto | F10 |
| R15 | Sobreconfianza en usuario por número «confianza» del proveedor | Pasa tal cual | A | Media | Retirada en `skin_wound` (valor original conservado para auditoría) | Mitigado (decisión de producto reversible) | F06 · T6 |
| R16 | Uso fuera de propósito (paciente sin médico delante) | Sin ficha de uso previsto | C | Desconocida | Aceptación del médico antes de persistir; sin ficha regulatoria | Abierto | Auditoría §3 «Indicaciones de producto» |

**Riesgos residuales que impiden pasar a GREEN:** R01-R03, R10, R14, R16 y el hueco de R06 en DICOM/PDF. Ninguno se resuelve con código; requieren el estudio del protocolo y definición de uso previsto.
