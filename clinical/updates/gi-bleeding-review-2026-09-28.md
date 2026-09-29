# Revisión de hemorragia digestiva — 28/09/2026

Estado: propuesta de trabajo v1.28; revisión clínica humana y adaptación local pendientes.

## Comprobación del índice real

El manifiesto del paquete enumera 93 IDs y resuelve 93/93 en los bundles. Ya existían `upper-gi-bleeding`, `lower-gi-bleeding` y `anticoagulation-reversal`; se reutilizan esas rutas. No se crea un ID nuevo ni se repite un módulo desarrollado. Los módulos de hemorragia masiva/trauma y seguridad de selección farmacológica aportan reglas transversales.

## Ámbito integrado en `upper-gi-bleeding`

- Reanimación y reevaluación, riesgo Glasgow–Blatchford y límites de la decisión ambulatoria.
- Protección de vía aérea selectiva y no uso rutinario de sonda nasogástrica.
- Procinéticos solo en pacientes seleccionados con hemorragia clínicamente grave/activa: eritromicina IV 250 mg 30–120 min antes; metoclopramida IV como alternativa condicional cuando no hay eritromicina IV, con precauciones por eventos adversos. No sustituyen reanimación ni demoran endoscopia.
- Rama no varicosa: tiempo de endoscopia tras resucitación, estigmas Forrest y hemostasia apropiada, límites de adrenalina sola, PPI poshemostasia y rescate con nueva endoscopia/clip, embolización y cirugía.
- Rama variceal distinta: tratamiento vasoactivo y antibiótico desde la presentación; endoscopia y ligadura; identificación de TIPS preemptivo/rescate; prevención secundaria con hepatología.
- Anemia/ferropenia, H. pylori, AINEs, seguimiento y límites de reversión/reinicio de antitrombóticos.

## Cobertura ya existente en `lower-gi-bleeding`

El módulo existente ya contempla resucitación, posible origen alto ante hematochezia con shock, CTA para sangrado persistente hemodinámicamente significativo, evaluación por radiología intervencionista/embolización, colonoscopia no urgente tras estabilización, reversión selectiva, cautela con antiagregación/stents, disposición y no usar ácido tranexámico de rutina. No se reescribe. Quedan en cola la ruta diagnóstica detallada de intestino delgado tras endoscopias bidireccionales negativas y el cotejo por agente de reversión/reinicio antitrombótico.

## Fuentes revisadas

- ESGE, *Endoscopic diagnosis and management of peptic ulcer bleeding*, actualización 2026 (PDF oficial; incluye corrección del gráfico, 22/05/2026): https://www.esge.com/assets/downloads/pdfs/guidelines/2026_a-2863-8314.pdf
- ESGE, *Endoscopic diagnosis and management of esophagogastric variceal hemorrhage*, 2022: https://www.esge.com/endoscopic-diagnosis-and-management-of-esophagogastric-variceal-hemorrhage
- ACG, *Management of Patients With Acute Lower Gastrointestinal Bleeding*, actualización 2023: https://pubmed.ncbi.nlm.nih.gov/36735555/
- ACG-CAG, manejo de anticoagulantes/antiagregantes durante sangrado GI agudo y periodo periendoscópico, 2022: https://pubmed.ncbi.nlm.nih.gov/35368325/

## Límites pendientes

La actualización ESGE 2026 citada es de úlcera péptica; no se extrapola a cada etiología no varicosa. Tiempos, formulaciones, contraindicaciones y recursos deben cotejarse con el paciente, farmacia y protocolo local. La variación entre guías sobre reversión no se resuelve aquí por una regla universal: usar el módulo agent-específico y balancear gravedad, fármaco/hora de última dosis, riesgo trombótico, control de fuente y consulta especializada. No se verificaron normas DGS, disponibilidad INFARMED ni formulario/stock hospitalario de Azores. Este borrador no constituye protocolo local aprobado ni validación clínica prospectiva.

## Validación técnica

Se conserva el manifiesto de 93 módulos y no se agregan casos sintéticos ni regresiones nuevas. Los validadores y pruebas se deben correr sobre el paquete final y registrar en `VALIDATION.md`.
