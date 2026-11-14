# Insulin UCI RCCC Implementation Plan

**Goal:** cuatro recorridos interactivos de simulación técnica en Emergency.
**Architecture:** reglas declarativas puras con procedencia; cualquier caso ambiguo se bloquea; resultados no clínicos y sin persistencia de datos.
**Tech Stack:** React 18, TypeScript, Vitest ya existentes.
**Spec:** docs/superpowers/specs/2026-11-13-insulin-uci-rccc-design.md

## Global Constraints
- CLINICALLY_PENDING, clinical_use_allowed=false, sin habilitación mediante checkbox.
- Main y referencias protegidas intactas. Sin cambios a contratos clínicos existentes.
- Sólo datos sintéticos; sin llamadas de red con valores introducidos.

## Review Focus
- Vacíos y valores no finitos deben fallar, cero de perfusión debe aceptarse.
- Huecos y solapamientos del original deben bloquearse.
- Tendencia debe usar minutos reales; la lógica histórica sólo admite intervalo de 60 minutos.
- Redondeos SC no deben ocultar diferencias respecto a la dosis total.
- Edición, cambio de recorrido y borrar invalidan el resultado.

## Tasks
- [x] Crear pruebas del motor: límites inicio IV, 144/0.7, 252/260, tiempo 30 min, dosis cero, valores inválidos y SC.
- [x] Ejecutar pruebas en rojo; implementar motor declarativo independiente, sin eval ni DOM.
- [x] Crear y probar UI de cuatro recorridos, estado no clínico, fuentes y borrado.
- [x] Conectar ruta y accesos, ejecutar suite frontend, typecheck, lint y build.
- [x] Registrar evidencia, actualización pendiente y QA real; commit aislado sin merge.

Navegador real bloqueado por entorno; QA global BLOCKED por revisión de evidencia vencida. Ver clinical/qa/INSULIN_UCI_RCCC_2026-11-13.md.
