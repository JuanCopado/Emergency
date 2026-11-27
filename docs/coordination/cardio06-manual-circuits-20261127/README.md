# CARDIO-06 — accesos manuales a circuitos existentes

Incremento estructural limitado de MED-RES-CARDIO-06 v1, aprobado por el propietario. Base de trabajo04063b5e0b60047b08041af62a6291231b6cb697, árbol6cf5c2e851a755afe0774fb5d315990d254c849d. No se modifica el candidato de composición congelado ni el receptor.

La guía non-coronary-chest-pain ya indica cinco módulos por causa en clinical/modules/cardiovascular.md:96-99. La biblioteca y la guía imprimible presentan ahora cinco enlaces manuales a esos mismos módulos, con título y estado del catálogo canónico. El panel solo aparece en este módulo; no clasifica pacientes, elige diagnóstico ni prescribe. Mantiene avisoCLINICALLY_PENDING. Se oculta en impresión para preservar el contenido exportable.

No se cambian cuerpos clínicos, dosis, fórmulas, productos, umbrales o estados de evidencia. No se crean módulos nuevos. La interfaz del panel está localizada enES,PT-PT,EN,ZH. Los títulos de destino proceden del catálogo existente y conservan su idioma canónico.

La comparación previa de las seis propuestas originales y sus límites está enCARDIO_STRUCTURE_DELTA.json, conservada como análisis anterior a implementar este incremento. Registro documentalPR122 no implica implementación de todo el alcance. Los restantes deltas se conservan individualizados sin repetir aprobaciones del propietario. Este incremento no cierra CARDIO-06 íntegro: miopericarditis, rotura esofágica y causas musculoesqueléticas/digestivas siguen descritas en el contenido canónico y no reciben destinos inventados.

Validación directa registrada en `QA_RESULTS.json`: 28/28 pruebas PASS (20 nuevas y 8 de reanimación existentes), ESLint PASS y build:security PASS con el indicador de auditoría de mapas existente, controles de contención y de mapas de servicio conservados. Estos ensayos de componentes incluyen los cuatro idiomas; la comprobación real de navegador y dispositivo corresponde a un revisor separado y no se atribuye a esta ejecución. La QA técnica no equivale a adjudicación clínica independiente. CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE.
