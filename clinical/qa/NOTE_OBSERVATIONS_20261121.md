# Nota clínica · observaciones y límites del motor

Base internacional `4aa2d3971f00ebe4e5df051bfddf08805387fb55`, árbol `14c41f320b95bbd647ed599d203ac000e67226a6`. El padre diagnóstico permanece YELLOW. Estado global CLINICALLY_PENDING.

## Reproducción y cambio técnico

En la base pasaron los bancos congelados de 47, 8 y 5 casos. Las primeras cuatro regresiones específicas fallaron en once comprobaciones. Se observaron una negación explícita omitida del resultado, SpO₂ documentada solicitada de nuevo, una relación urgente omitida y activaciones por menciones especulativas o atribuidas a un familiar. Se probaron los mismos campos y notas tras el cambio. Los cinco bancos y el catálogo de 92 reglas conservan sus bytes, incluidos pesos, umbrales, recomendaciones, relaciones y referencias de PR50.

| Área | Cambio verificable | Límite |
|---|---|---|
| Evidencia contraria | El candidato, la interfaz y la exportación muestran negaciones directas actuales de términos de la regla. | Un signo no documentado, remoto o hipotético no constituye un resultado negativo. La lista es observacional y no excluye enfermedad. |
| Datos discriminantes | Se cotejan edad, SpO₂, frecuencia respiratoria, GCS total y existencia de un informe oficial ECG. El ECG sigue pidiendo verificar su contenido y adecuación. | Son cinco de 234 etiquetas distintas. Las combinaciones, condiciones, pruebas seriadas y los otros campos siguen pendientes de revisión médica. |
| Relaciones urgentes | Se identifican en las limitaciones las referencias sin regla ejecutable vinculadas a los cinco primeros síndromes, también cuando exceden el límite de cinco tarjetas. | No se crea un diagnóstico para un identificador sin regla. Las cuatro referencias conocidas son `acute-chest-syndrome`, `arrhythmias-cardiac-arrest`, `pediatric-electrolyte-emergencies` y `traumatic-intracranial-mass-effect`. La lista visible no es exhaustiva. |
| Contexto | Se distinguen patrones acotados de negación, sujeto, temporalidad e incertidumbre. Las cláusulas independientes comprobadas recuperan su sujeto y contexto. | El sistema no implementa un analizador general. Parentescos, idiomas, expresiones y anáforas no contemplados pueden interpretarse incorrectamente. |
| Abstención | Una regla sin evidencia afirmada independiente devuelve puntuación efectiva cero, aunque mencione un hallazgo posible. Las alertas objetivas conservan su circuito. | En notas mixtas se mantiene la puntuación previa y se explicita cualquier mención no confirmada que haya sumado peso en la tarjeta y en la exportación. |

El campo opcional `weighted_uncertainty` distingue la contribución a la categoría de cada candidato. Una mención incierta no se presenta como evidencia favorable ni se marca como peso adicional cuando el mismo disparador ya tiene un término afirmado. La advertencia acompaña también a las relaciones prioritarias. Las notas históricas sin el campo siguen siendo válidas.

## Riesgo P1 pendiente

«Possible ST elevation. Nausea.» todavía produce la categoría reglada HIGH para síndrome coronario agudo. Solo los síntomas autonómicos figuran como evidencia afirmada. La tarjeta y la línea exportada advierten que «st elevation» contribuye sin confirmación. El aviso permite identificar el problema al revisar cada candidato. Su rendimiento clínico y la seguridad de esa categoría permanecen pendientes.

Se ensayó por separado suprimir todo el peso de términos especulativos. El experimento local `9885e3cf468dfe52d8da9bc578325e7cb6ae4eee`, árbol `e3f2577108883c116089bb8f57f0e006e40e226e`, obtuvo 46/47, 7/8 y 5/5. El caso de taponamiento combina derrame pericárdico, hipotensión, JVP elevada y sospecha explícita de taponamiento. El de endocarditis combina fiebre persistente, prótesis valvular, nuevo soplo y sospecha explícita de endocarditis. Sus signos afirmados aportan 3 y 2 puntos con las reglas actuales, frente a 9 y 7 cuando también se puntúa la sospecha. Con la supresión completa, el primero queda fuera de las cuatro hipótesis mostradas y el segundo por debajo del umbral moderado de 3. Cambiar pesos, expectativas o límites de presentación requiere adjudicación. El experimento queda fuera del candidato técnico.

## Comprobación

En las mismas 60 notas, la comparación base/candidato de las salidas reales mostró idéntico orden de probables y las mismas pruebas y tratamientos sugeridos. Cinco notas cambiaron en otras salidas. La tabla registra todos los cambios de pertenencia a las listas observados.

| Caso congelado | Efecto en el candidato respecto a la base | Motivo y visibilidad |
|---|---|---|
| Isquemia mesentérica | Añade neumotórax hipertensivo a las tarjetas prioritarias. | La relación sin regla de arritmias ya no consume tarjeta. La embolia pulmonar supera las cinco y figura por ID en las limitaciones. |
| Trauma mayor | Añade shock indiferenciado a las tarjetas prioritarias. | La relación de efecto masa traumático sin regla se comunica por ID y deja libre una tarjeta. |
| Abdomen agudo pediátrico | Añade parada cardiorrespiratoria pediátrica a las tarjetas prioritarias. | La relación de electrolitos pediátricos sin regla se comunica por ID y deja libre una tarjeta. |
| Ahogamiento pediátrico | Retira de las tarjetas la parada cardíaca adulta y las arritmias adultas. | Se aplican los límites de edad ya configurados. Ambos ID siguen visibles con el motivo de exclusión. Se conserva la parada pediátrica. |
| Taponamiento | Deja de mostrar shock cardiogénico como diferencial bajo (1 punto en la base). | El único término de esa regla era «JVP elevada» después de «suspeita de taponamento cardíaco e». La coordinación resulta ambigua para el analizador. Esta pérdida de un diferencial previo requiere adjudicación y revisión médica. |

No se observó pérdida de una tarjeta prioritaria por el cupo en estos 60 casos. La comprobación de desbordamiento usa el caso de isquemia mesentérica y comprueba la presencia del ID en las limitaciones. La interpretación clínica de las diferencias sigue pendiente.

Se conservan las 60 expectativas y casos sin edición. Pasaron los tres runners, las nueve pruebas nuevas, las siete de procedencia de PR50, las diez pruebas existentes de contexto y el auditor de cobertura de fuentes. Se comparó el delta con el borrador histórico PR15, `1fd4e5c7733e752a780a69f0a603c8466bd23a3a`. Se recuperó la presentación de observaciones y limitaciones para la interfaz internacional vigente. Los cambios de exportación, seguridad y autorización ajenos de PR15 quedan fuera de esta rama.

```sh
python -B -m unittest discover -s clinical/tests -p test_diagnostic_observations.py
python -B -m unittest discover -s clinical/tests -p test_clinical_note_provenance.py
python -B -m unittest discover -s clinical/tests -p test_skill.py -k v142_diagnostic
python -B clinical/scripts/run_clinical_note_diagnostic_cases.py
python -B clinical/scripts/run_clinical_note_diagnostic_closure_cases.py
python -B clinical/scripts/run_clinical_note_pediatric_routing_cases.py
python -B clinical/scripts/audit_clinical_note_diagnostic_coverage.py
```
