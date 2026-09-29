# Copia completa — emergency-medicine v1.26

Exportación fiel de la competencia instalada el 27/09/2026, con 93 módulos y
archivos de continuidad añadidos. Los archivos originales se conservan sin cambios.

## Contenido
- SKILL.md y configuración de la competencia.
- modules/: contenido de los 93 módulos, agrupados en archivos temáticos.
- references/: índice, enrutador, registro de evidencia y políticas.
- scripts/: código Python de calculadoras, carga de módulos y validadores.
- tests/: pruebas y casos documentados.
- updates/: cola y plantilla para actualizaciones de evidencia.
- CURRENT_STATE.md, MODULES.md, AGENTS.md y HANDOFF_PROMPT.md: continuidad.
- SOURCE_SHA256.json: huellas de integridad de los archivos exportados.

## Cómo continuar
1. Guarda este ZIP como copia maestra y descomprímelo cuando necesites trabajar.
2. En un nuevo hilo, adjunta el ZIP y pide: «Descomprime la competencia y lee
   AGENTS.md, CURRENT_STATE.md, SKILL.md y references/module-index.md. Comprueba
   el estado actual y continúa desde los pendientes sin repetir módulos».
3. También puedes subir el contenido de emergency-medicine a un repositorio Git
   privado para conservar historial de cambios. Cada avance debe actualizar
   código, módulos, evidencia, changelog y estado; después guardar una nueva versión.
4. Importar los archivos en otra herramienta no instala automáticamente una skill:
   sigue el mecanismo de instalación que admita esa herramienta. El contenido
   puede leerse como contexto; la interpretación clínica necesita un modelo anfitrión.

## Comprobación técnica local
Desde la carpeta emergency-medicine, con Python 3:

```sh
python3 scripts/validate_modules.py
python3 scripts/audit_evidence_coverage.py
python3 scripts/validate_clinical_cases.py
python3 -B -m unittest discover -s tests -p 'test_*.py' -q
```

En esta sesión: 93/93 módulos resolubles, 93/93 registros de evidencia,
58 pruebas técnicas superadas y 27 comprobaciones de regresiones con fuentes.
Esto no acredita precisión diagnóstica ni validación clínica prospectiva.

El paquete contiene todos los archivos de la competencia instalada, incluido su
código Python. No contiene un modelo de IA propio ni el historial completo del chat.
La actualización de evidencia requiere ejecución y revisión; el ZIP no programa
por sí solo tareas periódicas.
