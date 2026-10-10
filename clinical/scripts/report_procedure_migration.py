"""Render migration coverage from committed/source artifacts; never promote evidence."""
from procedure_structured import ROOT, DATA, REVIEW, canonical, load, project, validate


def report():
    cards, aliases = canonical()
    baseline = load(ROOT / 'qa/procedure-migration-baseline-v1.42.json')
    reviews = load(REVIEW)
    migrated = {}; valid = 0
    for pid in cards:
        path = DATA / (pid + '.json')
        if path.exists():
            data = load(path)
            if data.get('schema_version') == '1.42':
                migrated[pid] = data
                valid += not validate(data) and data == project(cards[pid], reviews)
    rescue = sum(d['rescue'] is not None for d in migrated.values())
    escalation = sum(d['escalation'] is not None for d in migrated.values())
    families = sorted({pid.split('-')[1] for pid in cards})
    complete = [f for f in families if all(pid in migrated for pid in cards if pid.split('-')[1] == f)]
    lines = [
        '# v1.42 — migración estructurada de procedimientos', '',
        'Baseline local limpio: `a896ad67e14f33048f006574bffd273f04751b0b`.',
        'Ref remoto observado: `0d2fcec1baba7dd50e352890777f4873d8a4dd0d`; local 13 por delante, 0 por detrás al iniciar. Sin reset, pull, rebase, merge ni push.', '',
        '## Contrato y alcance', '',
        'Fuente clínica: índice textual y 16 archivos de familia. El texto no se modifica. Los campos conservan los nombres existentes; `schema_version: 1.42` identifica el contrato nuevo y el schema v1.41 se conserva como histórico.',
        'El schema anterior forzaba rescue no vacío, subclasificaciones (absoluta/relativa, temporalidad de complicaciones, material esencial/opcional), población y metadatos no sustentados por las fichas. v1.42 conserva párrafos en `unclassified`, omite población/setting no explícitos y usa null para metadatos bibliográficos/fecha no desglosados. El texto íntegro de Fuentes permanece en sources.title; no se inventan organización, URL ni año.',
        'STOP = condición para detener/no continuar. RESCUE = acción explícita ante fallo/complicación. ESCALATION = transición explícita a otro recurso/equipo/técnica. No son intercambiables: solo se comparte un pasaje si contiene realmente ambas funciones.',
        'Las cuatro secciones tituladas Rescate se extraen literalmente. Otros pasajes se seleccionan individualmente en `references/procedure-safety-extractions-v1.42.json`, con sección y cita exactas. El generador solo comprueba/proyecta esas selecciones: no clasifica mediante palabras clave ni crea acciones. Null + pending_review indica falta de extracción inequívoca; no prueba que no exista ninguna instrucción relacionada en la prosa.',
        'Cada JSON conserva todas las secciones, preámbulo de familia, heading y hash del cuerpo. Pasos numerados se separan solo si la fuente enumera 1), 2), etc.; el resto conserva el párrafo completo, sin inventar una secuencia. Nombre/familia/nivel proceden del índice, y el heading de la ficha se conserva sin corregirlo.',
        'El frontend sigue consumiendo su catálogo derivado del texto, no estos JSON. No se cambia la capa visual ni la farmacología. Los 196 canónicos permanecen YELLOW; clinical_qa pending, revisión humana obligatoria. QA automatizado no es validación prospectiva.', '',
        '## Inventario y progreso', '',
        '| Métrica | Antes | Después actual |', '| --- | ---: | ---: |',
        '| Canónicos | 196 | 196 |', '| Alias | 4 | 4 |', '| Familias | 16 | 16 |',
        f'| JSON existentes | 26 | {len(list(DATA.glob("*.json")))} |',
        f'| JSON válidos | 26 (schema v1.41) | {valid} migrados (schema v1.42 + fidelidad) |',
        f'| JSON migrados | 0 | {len(migrated)} |',
        f'| Rescue extraído con soporte explícito | 4 secciones dedicadas; 26 JSON previos con rescue por revisar | {rescue} |',
        f'| Rescue pendiente en migrados | No cuantificado semánticamente | {len(migrated)-rescue} |',
        f'| Escalation extraída con soporte explícito | 0 campos separados | {escalation} |',
        f'| Escalation pendiente en migrados | No cuantificado semánticamente | {len(migrated)-escalation} |',
        '| JSON previos con diferencias respecto a la fuente | 26 | Valores previos preservados en auditoría; migrados cotejados |',
        '| YELLOW canónicos | 196 | 196 |', '',
        'Familias completadas estructuralmente: ' + (', '.join(complete) or 'ninguna') + '.',
        'El detector antiguo reproduce 27 “preparados” / 169 sin palabra de rescate; no constituye inventario semántico. Existen 170 JSON inicialmente ausentes, no 169.', '',
        '## Discrepancias y prioridades', '',
        '- P0: ninguno identificado en esta migración estructural.',
        '- P1: el JSON previo podía añadir/simplificar instrucciones de seguridad no trazadas al texto. Se retiran enriquecimientos no sustentados de la salida activa, conservando el original en Git y los valores auditados. No se decide que una recomendación clínica sea falsa: queda pendiente revisión humana.',
        '- P2: schema antiguo y tests comprobaban presencia de rescue, no soporte textual; se sustituye por contrato de ausencia explícita y pruebas de fidelidad/schema real. Los 26 JSON antiguos validaban el schema, lo cual no garantizaba equivalencia clínica.',
        '- P2: 74 variantes de título índice/ficha y 10 niveles que omiten el modificador POCUS en la ficha (US-001..006, US-008..010 y WND-006). Se usa el índice y se retiene el heading original; no se modifica ninguna fuente.',
        '- P2: los rescue/escalation pendientes requieren revisión clínica; no se rellenan ni bloquean la conservación estructural del resto de la ficha.',
        '- P3: completar metadatos bibliográficos desglosados requiere trabajo posterior; la fuente literal se conserva. Actions remoto no ejecutado.', '',
        'Valores textuales/JSON previos, campos y acciones: `procedure-migration-baseline-v1.42.json`. No todas las diferencias de redacción son contradicciones clínicas. Las diferencias se revisan contra la fuente, que prevalece para esta migración.', '',
        '## Validación y determinismo', '',
        'Comandos por familia: `procedure_structured.py --family CODE`; unittest de migración con `PROCEDURE_MIGRATION_FAMILY=CODE`; suites de procedimientos/schema/alias; segunda generación y comparación de bytes; diff-check y commit antes de continuar. El modo por familia no limita las comprobaciones de proyección de los 196 ni las de alias.',
        'Estado de ejecuciones finales: se registra en `VALIDATION.md` y en el cierre de sesión. Este informe calcula cobertura, no infiere que los tests hayan sido ejecutados. Generación sin timestamps, orden lexicográfico e IDs estables; JSON rechaza no finitos, claves/listas duplicadas, tipos incorrectos y promociones.', '',
        '## Alias (sin ficha JSON ni evidencia duplicada)', '',
    ]
    lines += [f'- `{a}` → `{t}`' for a, t in sorted(aliases.items())]
    lines += ['', '## Auditoría por procedimiento', '',
              '“Pendiente” significa sin extracción independiente inequívoca; el contenido original se conserva en sus secciones.', '',
              '| PROC-ID | Familia | JSON existe | Schema válido | STOP | Rescue explícito | Escalation explícita | Discrepancia texto/JSON | Acción |',
              '| --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    old = {r['procedure_id']: r for r in baseline['procedures']}
    for pid, card in cards.items():
        d = migrated.get(pid); exists = (DATA / (pid+'.json')).exists()
        fidelity = d == project(card, reviews) if d else False
        lines.append(f'| {pid} | {pid.split("-")[1]} | {"Sí" if exists else "No"} | {"v1.42" if d and not validate(d) else "v1.41" if exists else "—"} | Sí | {"Sí" if d and d["rescue"] else "Pendiente"} | {"Sí" if d and d["escalation"] else "Pendiente"} | {"Conforme" if fidelity else "Previa registrada" if old[pid]["json_exists"] else "Sin JSON"} | {"Migrado; revisión humana" if d else "Migrar"} |')
    lines += ['', '## Familias y PROC-IDs', '']
    for family in families:
        lines.append(f'- {family}: ' + ', '.join(pid for pid in migrated if pid.split('-')[1] == family) + '.')
    lines += ['', '## Archivos de la migración', '',
              'Datos: un archivo `clinical/data/procedures/PROC-ID.json` por cada ID migrado listado arriba. Los 26 existentes se regeneran; los otros 170 se crean al completar las familias.',
              'Infraestructura/documentación: `clinical/scripts/procedure_structured.py`, `clinical/scripts/report_procedure_migration.py`, `clinical/schemas/procedure-v1.42.schema.json`, `clinical/references/procedure-safety-extractions-v1.42.json`, `clinical/qa/procedure-migration-baseline-v1.42.json`, `clinical/qa/V1.42_PROCEDURE_STRUCTURED_MIGRATION.md`, `clinical/tests/test_procedure_migration_v142.py`, tests de schema AIR/NEURO, `clinical/requirements-test.txt`, `clinical/CURRENT_STATE.md`, `clinical/VALIDATION.md`, `clinical/CHANGELOG.md`, `clinical/references/module-index.md` y `clinical/references/evidence-registry.json`.', '']
    return '\n'.join(lines)


if __name__ == '__main__':
    path = ROOT / 'qa/V1.42_PROCEDURE_STRUCTURED_MIGRATION.md'
    path.write_text(report(), encoding='utf-8', newline='\n')
    print(path.name)
