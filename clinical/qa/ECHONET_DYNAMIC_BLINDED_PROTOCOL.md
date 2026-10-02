# ECHONET-DYNAMIC — BLINDED LV FUNCTION PROTOCOL v1.0

Fecha de congelación: 02/10/2026.

## Alcance
Solo vídeo apical 4 cámaras de función ventricular izquierda. No extrapolar a POCUS general, eFAST, pulmón, DVT o aorta.

## Licencia
Stanford EchoNet-Dynamic Research Use Agreement: personal/non-commercial research only; no redistribution/publication of dataset copies; no reidentification; research-use only and not for diagnosis/patient care.

## Referencia
Cada vídeo se acompaña de EF, ESV, EDV y trazados. Las mediciones clínicas fueron obtenidas por registered sonographer y verificadas por level-3 echocardiographer.

## Target inicial
`lvef_below_40_percent`: EF < 40.0% vs EF >= 40.0%.
El nombre del target expresa el umbral numérico y no pretende sustituir una categoría clínica completa de insuficiencia cardiaca.

## Cohorte
Usar split TEST oficial. Un vídeo/paciente según la estructura oficial; conservar cualquier identificador de paciente como grupo si aparece.

## Cegamiento
Vídeo y hash model-facing separados de EF sellada. Predicción positive/negative/abstain/nondiagnostic; freeze antes de revelar EF/target.

## Límites
Dataset retrospectivo de un centro y una sola vista A4C. Posible exposición previa del modelo. No equivale a validación prospectiva ni autoriza uso clínico.
