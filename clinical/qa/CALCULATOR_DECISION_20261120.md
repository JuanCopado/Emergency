# Módulo 12 · decisión médica pendiente

**ID SCORE-REF-20261120.** El Dr. Juan Copado Ceballos decide sobre el registro internacional de escalas y fórmulas como ayuda manual. Estado actual YELLOW. Las decisiones terapéuticas corresponden al profesional.

**135 escalas.** Se ensayó cada identificador por el motor canónico con una entrada sintética, incluida la derivación al instrumento oficial cuando procede. Hay 13 formularios interactivos de escalas y 122 entradas sin formulario en esa interfaz. **45 fórmulas.** Cada una tiene un enlace de referencia y una prueba con entradas, resultado esperado y unidad. La matriz documenta la opinión independiente de Gemini y los cotejos posteriores.

| Hallazgo reproducido | Corrección y fuente |
|---|---|
| MELD-Na legado ajustaba por sodio incluso con MELD inicial de 6 | Se aplica a partir de un MELD inicial redondeado mayor de 11. [OPTN histórico, 9.1.D](https://www.hrsa.gov/sites/default/files/hrsa/optn/optn_policy_notice_07-24-2014.pdf) |
| EDACS añadía cuatro puntos por antecedentes coronarios fuera del intervalo de edad | Se aplica el intervalo 18–50. El caso del proyecto con 86 años pasa de 38 a 34. [Than, formulario original](https://www.openclinical.net/wp-content/uploads/2020/05/EDACSDecisionSupportforChestPain.pdf) |
| APACHE II infrapuntuaba sodio y leucocitos | Corregidos los intervalos 150–154 y 155–159 de sodio y 20–39,9 de leucocitos. [Tabla de puntuación](https://www.msdmanuals.com/professional/multimedia/table/acute-physiologic-assessment-and-chronic-health-evaluation-apache-ii-scoring-system) |
| Glasgow pediátrico carecía de la opción verbalizada «retirada al tacto» | En menores de cuatro años se admite como respuesta motora de 5. [RCH, tabla GCS](https://www.rch.org.au/clinicalguide/guideline_index/Altered_conscious_state/) |
| La etiqueta por absorción retardada podía ocultar una concentración de paracetamol en o por encima de la línea del nomograma | La interpretación destaca el cruce de la línea y remite al protocolo aplicable cuando corresponda. [Consenso EE. UU./Canadá, formulación prolongada](https://jamanetwork.com/journals/jamanetworkopen/fullarticle/2808062) |
| Saturaciones en unidades equivocadas, talla negativa y resultados no finitos | Se rechazan entradas y resultados inválidos en el motor. Las pruebas reproducen, entre otros, saturación 970 % y talla −120 cm. |

**Alcance.** Las pruebas miden comportamiento del software. La precisión diagnóstica prospectiva y la calibración local de modelos pronósticos requieren estudios propios. Los enlaces de referencia incluyen publicaciones originales, guías y manuales técnicos. La revisión de extractos no acredita por sí sola cada celda de las tablas originales. Parkland y MELD-Na conservan su identificación histórica. Los instrumentos externos conservan sus condiciones de uso.

**Pregunta.** ¿Aprueba el módulo 12 en verde como referencia y ayuda de cálculo manual, con estos límites, los 13 formularios disponibles y las derivaciones documentadas a instrumentos oficiales? SÍ / NO.
