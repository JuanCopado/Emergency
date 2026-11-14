# Selector arritmias/parada — revisión operativa, 13/11/2026

**YELLOW retenido; CLINICALLY_PENDING.** El motivo deja de ser genérico: faltan comprobación en navegador real y validación operativa del equipo/local. Los cuatro circuitos destino mantienen sus propios pendientes clínicos.

## Correcciones y comprobaciones

El selector previo era documental: los IDs se mostraban como texto. Ahora ambas vistas, `/guides/arrhythmias-cardiac-arrest` y `/clinical/arrhythmias-cardiac-arrest`, ofrecen cuatro enlaces manuales a los módulos existentes. Cada enlace conserva el estado del destino. No se añade clasificación automática por edad, pulso o ritmo ni se calculan tratamientos.

| Selección manual | Destino |
|---|---|
| Adulto, arritmia con pulso | adult-arrhythmias |
| Adulto, parada | adult-cardiac-arrest |
| Pediatría, arritmia con circulación | pediatric-arrhythmias |
| Pediatría, parada o indicación de RCP | pediatric-cardiac-arrest |

Se corrige una omisión del texto fuente: el niño con FC<60/min y mala perfusión pese a soporte respiratorio adecuado necesita compresiones incluso si conserva pulso; no debe esperar a estar sin pulso. El circuito pediátrico destino ya contenía esta excepción. Se mantiene la exclusión de transición neonatal al nacimiento y la selección clínica/local del marco adulto/pediátrico, sin imponer un límite automático de edad.

Fuentes: [RCUK2025 PLS](https://www.resus.org.uk/professional-library/2025-resuscitation-guidelines/paediatric-basic-life-support-guidelines), [algoritmo PALS noviembre2025V2](https://www.resus.org.uk/sites/default/files/2025-12/Paediatric%20advanced%20life%20support%20algorithm%20Nov%202025%20V2.pdf), [RCUK2025 ALS](https://www.resus.org.uk/professional-library/2025-resuscitation-guidelines/adult-advanced-life-support-guidelines). Alcance: enrutamiento, no revisión completa de dosis/energías de los circuitos destino.

## Verificación y límites

Ocho pruebas DOM de navegación PASS: cuatro destinos en dos superficies, fidelidad del contenido destino/estado y visibilidad de excepciones antes de navegar. Esto es una prueba de integración funcional, no simulación clínica ni entrenamiento local de un equipo. El navegador real continúa bloqueado por el entorno previamente documentado; no se declara su comprobación. No hay firma clínica/farmacéutica nueva. No se cambian los cuerpos clínicos de los cuatro destinos, contratos de medicamentos ni simulador de insulina.

Resultados completos: `RESUSCITATION_ROUTER_OPERATIONAL_QA_2026-11-13.json`. Registro global sin promociones:33 GREEN/98 YELLOW. Sin publicación remota.

QA final:434 pruebas frontend,603 Python,7/7 controles y4 pruebas de generación PASS; compilación/TypeScript y lint PASS. Sin cambios en130 registros/guías fuera del selector ni en los cuatro cuerpos destino.
