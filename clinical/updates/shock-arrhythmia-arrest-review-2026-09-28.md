# Auditoría de shock, arritmias y parada — 28/09/2026

## Resultado del índice real

La versión v1.33 tenía 98 IDs. Ya existían rutas específicas para shock séptico (`sepsis-shock`), cardiogénico, hemorragia mayor/hipovolémico, anafilaxia, adrenal, taponamiento, TEP, neumotórax a tensión y causas obstétricas; el módulo pediátrico `pediatric-dehydration-shock` era acotado a gastroenteritis/deshidratación. Faltaba una puerta de reconocimiento y clasificación para shock no diferenciado y un marco pediátrico que impidiera derivar sin más al algoritmo adulto.

Solo había `arrhythmias-cardiac-arrest`, con reglas de seguridad breves y una remisión genérica a protocolos actuales; no había algoritmo completo de parada ni rutas diferenciadas para niño y adulto.

## Cambios de borrador v1.34

- Añadidos `undifferentiated-shock` y `pediatric-shock`; se conservaron causas etiológicas existentes, sin duplicar sus módulos.
- Añadidos `adult-arrhythmias`, `adult-cardiac-arrest`, `pediatric-arrhythmias` y `pediatric-cardiac-arrest`.
- Conservado `arrhythmias-cardiac-arrest` como selector común por edad/pulso.
- El router separa perfusión presente de parada y marca que la reanimación neonatal al nacimiento pertenece a soporte vital neonatal.
- Cobertura anatómica/etiológica comprobada: hipovolémico/hemorrágico, distributivo (séptico, anafiláctico, adrenal y neurogénico con diagnóstico de exclusión), cardiogénico, obstructivo (TEP, taponamiento y neumotórax a tensión) y mixto. No es una promesa de un algoritmo etiológico autónomo para toda causa rara; debe derivar a la ruta específica y protocolo local.

## Fuentes primarias cotejadas

- Resuscitation Council UK, Adult Advanced Life Support Guidelines 2025: https://www.resus.org.uk/professional-library/2025-resuscitation-guidelines/adult-advanced-life-support-guidelines
- Resuscitation Council UK, Paediatric Life Support 2025: https://www.resus.org.uk/professional-library/2025-resuscitation-guidelines/paediatric-basic-life-support-guidelines
- Adult tachyarrhythmia algorithm 2025: https://www.resus.org.uk/sites/default/files/2025-10/Adult%20tachyarrhythmia%20algorithm%202025.pdf
- Adult bradyarrhythmia algorithm 2025: https://www.resus.org.uk/sites/default/files/2025-10/Adult%20bradyarrhythmia%202025.pdf
- Pediatric arrhythmia algorithm 2025: https://www.resus.org.uk/sites/default/files/2025-10/Paediatric%20arrhythmia%20algorithm%202025.pdf
- Pediatric advanced life support algorithm 2025: https://www.resus.org.uk/sites/default/files/2025-10/Paediatric%20advanced%20life%20support%20algorithm%202025.pdf
- NICE NG254 (2025), suspected sepsis in people under 16: https://www.nice.org.uk/guidance/ng254

## Pendiente antes de uso asistencial

Revisión por especialistas adultos y pediátricos; cotejo del protocolo local de reanimación (energías, dosis, fármacos, desfibriladores, equipos y terminación/traslado), vía neonatal, prácticas de Portugal/Azores y disponibilidad INFARMED/formulario. El texto evita fijar dosis/energías potencialmente dependientes de la tarjeta local. Este cambio del paquete no instala ni publica la competencia.
