"""Product-bound reversal calculations and explicit specialist decision pathways.

The public API owns scalar/schema validation. This module owns clinical cross-field
rules and the distinction between a calculation and decision support without a dose.
No workflow fabricates a universal dose for an unidentified product or anticoagulant.
"""
from math import isfinite

from pediatric_numbers import positive


REVIEW_REFERENCE = 'references/acute-reversal-reviewed-2026-11-16.md'
PROTAMINE_LABEL_URL = ('https://www.dailymed.nlm.nih.gov/dailymed/fda/fdaDrugXsl.cfm'
                      '?setid=e1964129-33f4-4e4e-86e3-8e6a4e65bd83&type=display')
PCC_PROFILE = 'octaplex_uk_smpc_2024'
DALTEPARIN_PATHWAY = 'dalteparin_fragmin_protamine'
CONTRACT_IDS = tuple('reversal-' + key for key in (
    'vka-pcc', 'superwarfarin', 'edoxaban', 'betrixaban', 'fondaparinux',
    'other-lmwh', 'enoxaparin-over12', 'argatroban', 'bivalirudin',
    'other-dti', 'danaparoid', 'fibrinolytics', 'antiplatelets', 'unknown',
    'dabigatran-repeat'))

CONTEXTS = ['critical_or_uncontrolled_bleeding', 'major_controlled_bleeding',
            'nonmajor_or_no_bleeding', 'urgent_procedure', 'unknown']
SITES = ['spontaneous_intraparenchymal', 'traumatic_intracranial',
         'other_intracranial', 'extracranial', 'none_or_unknown']
INTRACRANIAL = frozenset(SITES[:3])
ORGAN_FUNCTION = ['preserved', 'impaired', 'unknown']
ACTIVITY = ['present_or_likely', 'not_detected_reliable_assay', 'unknown']


def reviewed_contracts(contract, field):
    """Replace the fifteen legacy static blocks without changing their identifiers."""
    rows = []

    def base_fields():
        return [
            field('population', 'Población de esta ruta', 'choice',
                  options=['adult', 'pediatric'], expected='adult'),
            field('clinical_context', 'Situación clínica actual', 'choice', options=CONTEXTS),
            field('bleeding_site', 'Localización del sangrado', 'choice', options=SITES),
            field('immediate_resources_available', 'Medios inmediatos de estabilización y escalada disponibles'),
        ]

    def add(key, label, drug, extra, sources, *, numeric=False, fields=None):
        row = contract('reversal-' + key, label, 'reversal', 'Reversión', drug,
                       'procedures-pharmacology.md', 'anticoagulation-reversal',
                       ['Identificar'], [], route='IV' if numeric else 'N/A',
                       model='reviewed_reversal', reviewed_workflow='reversal',
                       review_reference=REVIEW_REFERENCE,
                       source_ids=sources,
                       administration='Seguir la decisión contextual y las condiciones del producto seleccionado.',
                       limitations=[
                           'Ruta adulta. La autorización del propietario corresponde a la implementación; no sustituye la valoración del paciente.',
                           'Un resultado de apoyo de decisión no autoriza una dosis ni una velocidad de administración.',
                           'No confirma existencias, equivalencia entre productos ni revisión de otros módulos.'])
        # Decision support must remain reachable when drug, route or resources are
        # uncertain. Do not inherit the generic administration/local-hospital gates.
        row['fields'] = (base_fields() if fields is None else fields) + extra
        row['available_result_kinds'] = ['calculation', 'decision_support'] if numeric else ['decision_support']
        rows.append(row)

    pcc_if = {'key': 'pcc_profile', 'equals': PCC_PROFILE}
    add('vka-pcc', 'AVK — PCC específico o selección de producto', 'PCC de cuatro factores', [
        field('vka_confirmed', 'Exposición a antagonista de vitamina K confirmada'),
        field('pcc_profile', 'Producto y tabla de dosificación seleccionados', 'choice', options=[
            PCC_PROFILE, 'octaplex_pt_rcm_2020_review', 'other_or_unverified']),
        field('weight_kg', 'Peso medido (kg)', 'number', positive=True, required_if=pcc_if),
        field('pretreatment_inr', 'INR previo a PCC', 'number', minimum=2, required_if=pcc_if),
        field('pcc_presentation', 'Presentación Octaplex de esta ficha', 'choice',
              options=['500_iu_20_ml', '1000_iu_40_ml'], required_if=pcc_if),
        field('product_and_iv_route_verified', 'Producto, ficha aplicable y vía IV verificados', expected=True, required_if=pcc_if),
        field('pcc_contraindication_present', 'Hipersensibilidad, alergia/heparina-HIT o déficit IgA con anti-IgA', expected=False, required_if=pcc_if),
        field('thrombosis_dic_context_reviewed', 'Riesgo trombótico/CID y contexto de coagulopatía revisados', expected=True, required_if=pcc_if),
        field('vitamin_k_plan_confirmed', 'Plan concomitante de vitamina K confirmado para AVK', expected=True, required_if=pcc_if),
        field('pcc_already_given_this_episode', 'Ya se administró PCC en este episodio', expected=False, required_if=pcc_if),
    ], ['OCTAPLEX_UK_2024', 'C05_PRIOR_2026'], numeric=True)

    add('superwarfarin', 'Superwarfarina — toxicología, INR y seguimiento prolongado', 'Vitamina K / hemostasia dirigida', [
        field('exposure_status', 'Exposición a rodenticida anticoagulante', 'choice', options=['confirmed', 'suspected', 'unknown']),
        field('inr_state', 'Resultado del INR', 'choice', options=['elevated', 'within_reference', 'pending']),
        field('toxicology_followup_available', 'Toxicología y seguimiento seriado accesibles'),
    ], ['CDC_BRODIFACOUM_2022', 'CAPQ_VITAMIN_K'])

    for key, label in [('edoxaban', 'Edoxabán'), ('betrixaban', 'Betrixabán')]:
        add(key, label + ' — control hemorrágico y estrategia de reversión', label, [
            field('exact_agent_confirmed', 'Fármaco exacto confirmado'),
            field('residual_activity', 'Actividad anticoagulante residual', 'choice', options=ACTIVITY),
            field('renal_function', 'Función renal', 'choice', options=ORGAN_FUNCTION),
            field('source_control_insufficient', 'Hemorragia persiste pese a medidas de hemostasia/soporte'),
            field('pcc_product_available', 'PCC de cuatro factores disponible para valorar'),
        ], ['EDOXABAN_EMA', 'TRAUMA_2023', 'NCS_2026'] if key == 'edoxaban'
           else ['BETRIXABAN_FDA_2017', 'NCS_2026'])

    add('fondaparinux', 'Fondaparinux — contexto terapéutico y acumulación', 'Fondaparinux', [
        field('exposure_intensity', 'Pauta de fondaparinux', 'choice', options=['therapeutic', 'prophylactic', 'unknown']),
        field('renal_function', 'Función renal', 'choice', options=ORGAN_FUNCTION),
        field('residual_activity', 'Actividad residual/acumulación', 'choice', options=ACTIVITY),
        field('bioaccumulation_evidence', 'Evidencia de bioacumulación por encima del efecto profiláctico esperado'),
    ], ['FONDAPARINUX_LABEL', 'NCS_2016'])

    lmwh_if = {'key': 'lmwh_pathway', 'equals': DALTEPARIN_PATHWAY}
    add('other-lmwh', 'Otras HBPM — dalteparina específica o revisión del agente', 'Protamina / estrategia por HBPM', [
        field('lmwh_pathway', 'Pauta seleccionada', 'choice', options=[DALTEPARIN_PATHWAY, 'other_lmwh_assessment']),
        field('lmwh_agent', 'HBPM identificada', 'choice', options=['dalteparin', 'tinzaparin', 'nadroparin', 'other', 'unknown']),
        field('renal_function', 'Función renal', 'choice', options=ORGAN_FUNCTION),
        field('residual_activity', 'Actividad anticoagulante residual', 'choice', options=ACTIVITY),
        field('dalteparin_dose_to_neutralize_anti_xa_iu', 'Dosis reciente de dalteparina a neutralizar (UI anti-Xa)',
              'number', positive=True, required_if=lmwh_if),
        field('timing_and_anti_xa_units_confirmed', 'Hora, dosis relevante y unidades anti-Xa confirmadas', expected=True, required_if=lmwh_if),
        field('dalteparin_fragmin_product_verified', 'Producto dalteparina/Fragmin y ficha aplicable verificados', expected=True, required_if=lmwh_if),
        field('protamine_product_iv_verified', 'Producto protamina, vía IV y administración lenta de al menos 10 min verificados', expected=True, required_if=lmwh_if),
        field('protamine_contraindication_present', 'Contraindicación o reacción previa relevante a protamina', expected=False, required_if=lmwh_if),
        field('protamine_risk_reviewed', 'Riesgo de anafilaxia/hipotensión y factores de riesgo revisados', expected=True, required_if=lmwh_if),
        field('prior_protamine_this_episode', 'Protamina ya administrada en este episodio', expected=False, required_if=lmwh_if),
    ], ['FRAGMIN_SMPC', 'PROTAMINE_LABEL'], numeric=True)

    add('enoxaparin-over12', 'Enoxaparina >12 h — comprobar actividad antes de protamina', 'Enoxaparina / protamina', [
        field('last_dose_hours', 'Horas desde última dosis de enoxaparina', 'number', exclusive_minimum=12),
        field('renal_function', 'Función renal', 'choice', options=ORGAN_FUNCTION),
        field('residual_activity', 'Actividad residual con ensayo e interpretación adecuados', 'choice', options=ACTIVITY),
        field('ongoing_bleeding', 'Sangrado activo persistente'),
        field('prior_protamine_this_episode', 'Protamina ya administrada en este episodio'),
    ], ['CLEXANE_SMPC'])

    for key, label, source, organ in [
        ('argatroban', 'Argatrobán', 'ARGATROBAN_FDA_2026', 'hepatic_function'),
        ('bivalirudin', 'Bivalirudina', 'BIVALIRUDIN_LABEL', 'renal_function'),
    ]:
        add(key, label + ' — detener perfusión, soporte y reevaluación', label, [
            field('infusion_running', 'Perfusión todavía en curso'),
            field(organ, 'Función hepática' if organ == 'hepatic_function' else 'Función renal', 'choice', options=ORGAN_FUNCTION),
            field('coagulation_test_state', 'Tendencia de coagulación pertinente', 'choice', options=['prolonged', 'normalized', 'pending']),
        ], [source])

    add('other-dti', 'Otros inhibidores directos de trombina — identificar y dirigir', 'Inhibidor directo de trombina', [
        field('agent_status', 'Identificación del inhibidor', 'choice', options=['dabigatran', 'argatroban', 'bivalirudin', 'another_confirmed_dti', 'unknown']),
        field('renal_function', 'Función renal', 'choice', options=ORGAN_FUNCTION),
        field('residual_activity', 'Actividad anticoagulante residual', 'choice', options=ACTIVITY),
    ], ['NCS_2016', 'PRAXBIND_SMPC'])

    add('danaparoid', 'Danaparoide — hemostasia y aclaramiento', 'Danaparoide', [
        field('renal_function', 'Función renal', 'choice', options=ORGAN_FUNCTION),
        field('residual_activity', 'Actividad anti-Xa residual calibrada', 'choice', options=ACTIVITY),
        field('bleeding_controlled', 'Hemorragia controlada con medidas iniciales'),
    ], ['DANAPAROID_SMPC', 'NCS_2016'])

    add('fibrinolytics', 'Fibrinolíticos — hemorragia sintomática y fibrinógeno', 'Hemostasia tras fibrinólisis', [
        field('fibrinolytic_agent', 'Fibrinolítico', 'choice', options=['alteplase', 'tenecteplase', 'other_or_unknown']),
        field('fibrinolysis_indication', 'Indicación de la fibrinólisis', 'choice', options=['acute_ischemic_stroke', 'other_or_unknown']),
        field('fibrinolytic_timing', 'Tiempo desde fibrinólisis', 'choice', options=['within_24_hours', 'over_24_hours', 'unknown']),
        field('symptomatic_intracranial_bleeding', 'Hemorragia intracraneal sintomática atribuida a fibrinólisis'),
        field('cryoprecipitate_available_appropriate', 'Crioprecipitado disponible a tiempo y apropiado'),
        field('fibrinogen_state', 'Fibrinógeno actual', 'choice', options=['below_150_mg_dl', 'at_least_150_mg_dl', 'pending']),
        field('initial_cryoprecipitate_already_given', 'Ya se administró la dosis inicial de crioprecipitado'),
    ], ['AHA_AIS_2026', 'NCS_2016'])

    add('antiplatelets', 'Antiagregantes — decisiones según localización y neurocirugía', 'Antiagregantes / hemostasia', [
        field('antiplatelet_agent', 'Exposición antiagregante', 'choice', options=['aspirin', 'p2y12_inhibitor', 'dual_or_multiple', 'gpiibiiia', 'other_or_unknown']),
        field('urgent_neurosurgery_planned', 'Intervención neuroquirúrgica urgente prevista'),
        field('independent_platelet_transfusion_indication', 'Existe otra indicación transfusional (p. ej., trombocitopenia relevante)'),
    ], ['NCS_2026'])

    add('unknown', 'Agente desconocido — identificar sin retrasar estabilización', 'Agente antitrombótico no identificado', [
        field('medication_records_accessible', 'Envases/receta/registro farmacológico accesibles'),
        field('drug_calibrated_anti_xa_available', 'Ensayo anti-Xa calibrado para el fármaco accesible'),
        field('dabigatran_assay_available', 'dTT/ECT o prueba pertinente de dabigatrán accesible'),
        field('renal_function', 'Función renal', 'choice', options=ORGAN_FUNCTION),
    ], ['NCS_2016', 'TRAUMA_2023'])

    add('dabigatran-repeat', 'Dabigatrán — segunda tanda justificada de idarucizumab', 'Idarucizumab', [
        field('population', 'Población', 'choice', options=['adult', 'pediatric'], expected='adult'),
        field('route', 'Vía de administración', 'choice', options=['IV', 'IM', 'SC', 'PO'], expected='IV'),
        field('dabigatran_confirmed', 'Dabigatrán confirmado como agente a revertir', expected=True),
        field('previous_complete_5g_courses', 'Tandas previas completas de 5 g en este episodio', 'number', minimum=0, integer=True),
        field('repeat_indication', 'Motivo de considerar otra tanda', 'choice', options=[
            'recurrent_clinically_relevant_bleeding', 'life_threatening_rebleeding_risk', 'second_emergency_surgery', 'none']),
        field('coagulation_test', 'Prueba de coagulación prolongada', 'choice', options=['aPTT', 'dTT', 'ECT', 'INR', 'unknown']),
        field('coagulation_prolonged', 'Prolongación pertinente confirmada tras la primera tanda', expected=True),
        field('repeat_indication_reviewed', 'Repetición indicada tras reevaluación clínica', expected=True),
        field('praxbind_product_verified', 'Praxbind 2,5 g/50 mL verificado', expected=True),
        field('hypersensitivity_fructose_risk_reviewed', 'Hipersensibilidad e intolerancia hereditaria a fructosa valoradas', expected=True),
        field('renal_function_and_rebound_reviewed', 'Función renal y posible rebote de dabigatrán revisados', expected=True),
        field('monitoring_rescue_available', 'Monitorización y medios de rescate disponibles', expected=True),
    ], ['PRAXBIND_SMPC'], numeric=True, fields=[])
    return rows


def _active(field, inputs):
    condition = field.get('required_if')
    return not condition or inputs.get(condition['key']) == condition['equals']


def validation_errors(row, inputs):
    """Clinical restrictions after the API has validated active field types."""
    if not isinstance(inputs, dict):
        return [('inputs', 'Los datos deben ser un objeto estructurado.')]
    missing = [(f['key'], 'Falta un dato requerido para esta decisión: ' + f['label'])
               for f in row['fields'] if _active(f, inputs) and inputs.get(f['key']) is None]
    if missing:
        return missing
    errors = []
    if inputs.get('population') != 'adult':
        errors.append(('population', 'Esta ruta revisada es adulta; no extrapolar dosis a pediatría.'))
    key = row['id']
    if key == 'reversal-vka-pcc' and inputs.get('pcc_profile') == PCC_PROFILE:
        if inputs.get('vka_confirmed') is not True:
            errors.append(('vka_confirmed', 'La tabla por INR corresponde a AVK, no a un DOAC o agente desconocido.'))
        if inputs.get('clinical_context') not in ('critical_or_uncontrolled_bleeding', 'urgent_procedure'):
            errors.append(('pcc_indication', 'Esta pauta exige corrección urgente por sangrado crítico/no controlado o procedimiento que no puede esperar.'))
        for name in ('weight_kg', 'pretreatment_inr'):
            value = inputs.get(name)
            if type(value) not in (int, float) or not isfinite(value) or value <= 0:
                errors.append((name, 'Se requiere un valor positivo finito verificado.'))
        if type(inputs.get('pretreatment_inr')) in (int, float) and inputs['pretreatment_inr'] < 2:
            errors.append(('pcc_inr_below_table', 'INR <2 queda fuera de esta tabla de producto. Valorar la pauta específica de hemorragia intracraneal/otra causa; no extrapolar 25 UI/kg.'))
    elif key == 'reversal-other-lmwh' and inputs.get('lmwh_pathway') == DALTEPARIN_PATHWAY:
        if inputs.get('lmwh_agent') != 'dalteparin':
            errors.append(('lmwh_product_mismatch', 'Esta pauta numérica es de dalteparina/Fragmin, no de otra HBPM.'))
        if inputs.get('clinical_context') != 'critical_or_uncontrolled_bleeding':
            errors.append(('protamine_indication', 'Protamina en esta ruta requiere hemorragia crítica/no controlada; no una reversión profiláctica.'))
        if inputs.get('residual_activity') != 'present_or_likely':
            errors.append(('lmwh_activity', 'Confirmar efecto residual clínicamente relevante antes de administrar protamina.'))
        value = inputs.get('dalteparin_dose_to_neutralize_anti_xa_iu')
        if type(value) not in (int, float) or not isfinite(value) or value <= 0:
            errors.append(('dalteparin_dose_to_neutralize_anti_xa_iu', 'Dosis relevante en UI anti-Xa positiva y finita; no convertir desde mg por suposición.'))
    elif key == 'reversal-fibrinolytics':
        if inputs.get('symptomatic_intracranial_bleeding') is True and inputs.get('bleeding_site') not in INTRACRANIAL:
            errors.append(('bleeding_site_conflict', 'La hemorragia intracraneal sintomática y la localización seleccionada no concuerdan.'))
    elif key == 'reversal-dabigatran-repeat':
        if inputs.get('previous_complete_5g_courses') != 1:
            errors.append(('idarucizumab_course', 'Este contrato calcula exclusivamente la segunda tanda tras una primera de 5 g completa; no una primera ni una tercera tanda.'))
        if inputs.get('repeat_indication') not in ('recurrent_clinically_relevant_bleeding', 'life_threatening_rebleeding_risk', 'second_emergency_surgery'):
            errors.append(('idarucizumab_repeat_indication', 'No existe criterio regulatorio para repetir automáticamente.'))
        if inputs.get('coagulation_test') not in ('aPTT', 'dTT', 'ECT') or inputs.get('coagulation_prolonged') is not True:
            errors.append(('idarucizumab_assay', 'Se requiere prolongación pertinente de aPTT, dTT o ECT; INR aislado no justifica esta segunda tanda.'))
    return errors


def _support(code, summary, actions, *, information=None, sources=None):
    return {
        'result_kind': 'decision_support', 'decision_code': code,
        'decision_support': summary, 'numerical_dose_authorized': False,
        'dose': None, 'dose_unit': None, 'route': None,
        'concentration': None, 'components': None, 'withdrawal_ml': None,
        'administration_volume_ml': None, 'pump_ml_h': None,
        'next_actions': actions, 'information_needed': information or [],
        'selected_source_ids': sources or [],
        'administration': 'Apoyo de decisión: no se ha calculado ni autorizado una pauta de administración.',
    }


def _initial_actions(inputs):
    actions = []
    context = inputs.get('clinical_context')
    if context == 'critical_or_uncontrolled_bleeding':
        actions.append('Suspender el agente implicado; estabilizar, controlar el foco y activar el circuito de hemorragia crítica y soporte transfusional necesario.')
    elif context == 'urgent_procedure':
        actions.append('Precisar urgencia real, posibilidad de diferir y actividad residual; coordinar hemostasia con el equipo del procedimiento.')
    elif context == 'nonmajor_or_no_bleeding':
        actions.append('No iniciar reversión de alto riesgo de forma rutinaria; revisar la necesidad de interrupción y el riesgo trombótico.')
    elif context == 'major_controlled_bleeding':
        actions.append('Mantener control del foco y vigilancia; reevaluar necesidad de reversión según actividad residual, gravedad y riesgo trombótico.')
    else:
        actions.append('Definir estabilidad, gravedad, localización, fármaco y urgencia; iniciar estabilización si existe compromiso clínico.')
    if inputs.get('bleeding_site') in INTRACRANIAL:
        actions.append('Activar valoración neurocrítica/neuroquirúrgica y neuroimagen urgente según la situación; vigilar expansión y deterioro.')
    if inputs.get('immediate_resources_available') is False:
        actions.append('Activar apoyo urgente y traslado al recurso capaz de monitorizar y tratar; continuar las medidas disponibles sin esperar una casilla de disponibilidad.')
    return actions


def _pcc(inputs):
    actions = _initial_actions(inputs)
    profile = inputs['pcc_profile']
    if profile != PCC_PROFILE:
        if profile == 'octaplex_pt_rcm_2020_review':
            actions.append('El RCM portugués de 2020 utiliza intervalos en mL/kg y máximo 3000 UI; la conciliación C05 identificó diferencias respecto a los intervalos aportados. Elegir y verificar una dosis concreta con la ficha aplicable, sin promediar bandas ni importar la tabla UK.')
        else:
            actions.append('Identificar marca, jurisdicción/ficha aplicable, presentación, unidades de factor IX, tabla por INR, techo y velocidad; aplicar íntegra una pauta respaldada.')
        actions.append('En reversión urgente de AVK, coordinar PCC y vitamina K según el contexto; si PCC no está disponible, valorar plasma y soporte sin retrasar estabilización.')
        return _support('pcc_product_selection', 'Flujo AVK habilitado; este producto aún no tiene un cálculo automático seleccionado.', actions,
                        information=['Agente AVK, INR previo, peso, producto/ficha, contraindicación heparina/HIT/IgA, dosis previa y plan de vitamina K.'],
                        sources=['C05_PRIOR_2026', 'OCTAPLEX_UK_2024'])
    if inputs['immediate_resources_available'] is False:
        return _support('pcc_resources_escalation', 'Se requiere un entorno capaz de administrar y vigilar PCC antes de generar una pauta.', actions, sources=['OCTAPLEX_UK_2024'])
    inr = inputs['pretreatment_inr']
    coefficient = 25 if inr < 4 else 35 if inr <= 6 else 50
    dosing_weight = min(inputs['weight_kg'], 100)
    dose = coefficient * dosing_weight
    volume = dose / 25
    return {
        'result_kind': 'calculation', 'dose': dose, 'dose_unit': 'IU factor IX',
        'route': 'IV', 'drug': 'Octaplex — tabla SmPC UK 16-10-2024',
        'components': {'coefficient_iu_kg': coefficient, 'measured_weight_kg': inputs['weight_kg'],
                       'dosing_weight_kg': dosing_weight, 'weight_cap_kg': 100,
                       'single_dose_cap_iu': coefficient * 100},
        'maximum': {'value': coefficient * 100, 'unit': 'IU factor IX'},
        'concentration': {'value': 25, 'unit': 'IU factor IX/mL', 'role': 'reconstituted_product'},
        'withdrawal_ml': volume, 'administration_volume_ml': volume,
        'pump_ml_h': None,
        'arithmetic': f'{coefficient} UI/kg × {dosing_weight:g} kg = {dose:g} UI; {dose:g} / 25 = {volume:g} mL.',
        'preparation': 'Solo la presentación verificada: 500 UI/20 mL o 1000 UI/40 mL tras reconstitución según el producto; no redondear por viales automáticamente.',
        'administration': 'Vía IV. La ficha seleccionada limita la velocidad a 0,12 mL/kg/min, máximo 8 mL/min; vigilar reacción y ajustar según el producto. No se ha programado una bomba.',
        'next_actions': ['Administrar vitamina K conforme al plan clínico confirmado.',
                         'Controlar INR y respuesta hemostática; no repetir PCC automáticamente.',
                         'Vigilar trombosis, CID e hipersensibilidad y planificar reanudación de anticoagulación cuando proceda.'],
        'selected_source_ids': ['OCTAPLEX_UK_2024'],
    }


def _lmwh(inputs):
    actions = _initial_actions(inputs)
    if inputs['lmwh_pathway'] != DALTEPARIN_PATHWAY:
        actions += ['Identificar HBPM exacta, dosis/unidad, última administración, pauta terapéutica o profiláctica, función renal y actividad anti-Xa pertinente.',
                    'Protamina tiene neutralización incompleta y dependiente de la HBPM. Seleccionar la ficha del agente; no convertir mg a UI anti-Xa por analogía ni usar esta fórmula para danaparoide.',
                    'Si se confirma dalteparina/Fragmin con actividad relevante y hemorragia crítica, puede seleccionarse la pauta específica de este contrato.']
        return _support('lmwh_agent_specific_review', 'Decisión para HBPM habilitada; se requiere identificar la pauta propia del agente.', actions,
                        information=['Agente, dosis relevante y unidad anti-Xa, tiempo, función renal, pruebas pertinentes, protamina previa y riesgos.'], sources=['FRAGMIN_SMPC', 'PROTAMINE_LABEL'])
    if inputs['immediate_resources_available'] is False:
        return _support('protamine_resources_escalation', 'Protamina requiere monitorización y capacidad de tratar anafilaxia/hipotensión.', actions, sources=['PROTAMINE_LABEL'])
    units = inputs['dalteparin_dose_to_neutralize_anti_xa_iu']
    uncapped_dose = positive('protamine_dose_mg', units / 100)
    dose = min(uncapped_dose, 50)
    return {
        'result_kind': 'calculation', 'drug': 'Protamina para dalteparina/Fragmin',
        'dose': dose, 'dose_unit': 'mg', 'route': 'IV', 'pump_ml_h': None,
        'components': {'dalteparin_anti_xa_iu': units, 'protamine_mg_per_100_anti_xa_iu': 1,
                       'single_dose_cap_mg': 50},
        'maximum': {'value': 50, 'unit': 'mg por administración inicial lenta de al menos 10 minutos'},
        'arithmetic': f'{units:g} UI anti-Xa / 100 = {uncapped_dose:g} mg; límite de esta dosis = 50 mg; resultado = {dose:g} mg.',
        'administration': 'Protamina IV lenta durante al menos 10 minutos; no más de 50 mg en 10 minutos. Respetar un límite más lento si lo exige la ficha real. Este techo no es la dosis acumulada máxima de todo el tratamiento. La concentración, volumen y preparación dependen del producto verificado; no se inventan mL.',
        'next_actions': ['Neutralización de anti-Xa de dalteparina incompleta (aproximadamente 25–50%); vigilar sangrado y coagulación.',
                         'No repetir ni superar el techo automáticamente; reevaluar actividad, función renal y dosis previa con experiencia en hemostasia.',
                         'Disponer de rescate inmediato por hipotensión, anafilaxia y reacciones pulmonares.'],
        'selected_source_ids': ['FRAGMIN_SMPC', 'PROTAMINE_LABEL'],
        'product_safety_reference': PROTAMINE_LABEL_URL,
    }


def calculate(row, inputs):
    """Return a dose only for an explicitly reviewed, fully specified regimen."""
    errors = validation_errors(row, inputs)
    if errors:
        raise ValueError('; '.join(message for _, message in errors))
    key = row['id']
    if key == 'reversal-vka-pcc':
        return _pcc(inputs)
    if key == 'reversal-other-lmwh':
        return _lmwh(inputs)
    if key == 'reversal-dabigatran-repeat':
        return {
            'result_kind': 'calculation', 'dose': 5, 'dose_unit': 'g', 'route': 'IV',
            'drug': 'Idarucizumab — segunda tanda',
            'components': {'consecutive_doses': 2, 'dose_each_g': 2.5, 'volume_each_ml': 50,
                           'course_number': 2},
            'concentration': {'value': 0.05, 'unit': 'g/mL', 'role': 'ready_to_use'},
            'administration_volume_ml': 100, 'pump_ml_h': None,
            'administration': 'Dos administraciones consecutivas de 2,5 g/50 mL: cada perfusión durante 5–10 minutos, o bolos consecutivos según la ficha de Praxbind. No es una perfusión continua.',
            'next_actions': ['Reevaluar hemostasia y aPTT/dTT/ECT; vigilar posible rebote, especialmente con insuficiencia renal.',
                             'No programar una tercera tanda: no se ha establecido una dosis diaria máxima.',
                             'Planificar reanudación antitrombótica cuando esté clínicamente indicada y exista hemostasia.'],
            'selected_source_ids': ['PRAXBIND_SMPC'],
        }

    actions = _initial_actions(inputs)
    site = inputs['bleeding_site']
    context = inputs['clinical_context']
    critical = context == 'critical_or_uncontrolled_bleeding'
    source_ids = row['source_ids']
    if key == 'reversal-superwarfarin':
        if critical:
            code, summary = 'superwarfarin_urgent_hemostasis', 'Hemorragia crítica: reversión urgente y toxicología en paralelo.'
            actions += ['Confirmar coagulopatía por antagonismo de vitamina K; valorar PCC de cuatro factores y vitamina K1 parenteral con pauta de urgencia y producto identificados.',
                        'No trasladar automáticamente una dosis de mantenimiento de warfarina a intoxicación por brodifacoum u otro rodenticida.']
        elif inputs['inr_state'] == 'within_reference':
            code, summary = 'superwarfarin_surveillance', 'INR inicialmente normal: vigilancia de coagulopatía tardía, sin vitamina K profiláctica automática.'
            actions.append('Acordar con toxicología cuándo repetir INR según agente, dosis y tiempo de exposición; un resultado normal inicial no excluye toxicidad posterior.')
        else:
            code, summary = 'superwarfarin_individualized_vitamin_k', 'Coagulopatía/exposición requiere vitamina K individualizada y seguimiento toxicológico.'
            actions.append('Obtener INR y evaluación de sangrado; seleccionar dosis, vía y controles de vitamina K1 con toxicología según respuesta.')
        actions.append('El tratamiento puede prolongarse semanas o meses; documentar acceso a vitamina K, INR seriado y criterio supervisado de retirada para evitar rebote.')
        if not inputs['toxicology_followup_available']:
            actions.append('Contactar centro de toxicología y organizar seguimiento/derivación antes de un alta que dependa de controles prolongados.')
        return _support(code, summary, actions, information=['Rodenticida exacto, exposición, INR seriado, sangrado, tratamientos previos y posibilidad de seguimiento.'], sources=source_ids)

    if key in ('reversal-edoxaban', 'reversal-betrixaban'):
        agent = 'edoxabán' if key.endswith('edoxaban') else 'betrixabán'
        if not inputs['exact_agent_confirmed']:
            actions.append('Confirmar el agente mediante envase/registro/prescriptor y dirigir a la ruta de agente desconocido si persiste la incertidumbre.')
            return _support('factor_xa_identification', 'Identificar el anti-Xa antes de seleccionar una pauta específica.', actions, sources=source_ids)
        actions.append('Precisar última dosis y función renal, hemograma y actividad anti-Xa calibrada cuando esté disponible; INR normal no excluye efecto ni selecciona dosis de PCC.')
        if inputs['residual_activity'] == 'not_detected_reliable_assay':
            actions.append('Si un ensayo apropiado excluye actividad relevante, buscar otra causa de hemorragia; no administrar PCC solo por el antecedente farmacológico.')
            return _support('factor_xa_no_relevant_activity', 'El antecedente de ' + agent + ' no demuestra actividad actual.', actions, sources=source_ids)
        if not critical:
            actions.append('Individualizar interrupción y procedimiento; esta salida no convierte sangrado menor o cirugía diferible en indicación de PCC.')
            return _support('factor_xa_context_review', 'Selección de hemostasia según gravedad y efecto residual.', actions, sources=source_ids)
        if key == 'reversal-edoxaban' and inputs['source_control_insufficient']:
            actions.append('La ficha de Lixiana contempla PCC de cuatro factores 50 UI/kg para sangrado vital no controlado con hemostasia/transfusión. Verificar producto, dosis/techo justificables y riesgo trombótico; este flujo no inventa un máximo universal ni una orden numérica.')
            actions.append('En trauma la guía europea 2023 permite 25–50 UI/kg y propone inicialmente 25 UI/kg: elegir el régimen íntegro que corresponda al contexto y registrar la razón, sin combinarlo con bandas de INR de AVK.')
        elif key == 'reversal-edoxaban':
            actions.append('Mantener control inmediato del foco y soporte; decidir reversión urgente en paralelo según el contexto, sin exigir esperar al fracaso secuencial si la situación es crítica.')
        else:
            actions.append('La ficha histórica FDA de betrixabán no establece antídoto específico. Valorar una estrategia hemostática especializada y una fuente actual aplicable antes de usar PCC fuera de indicación; no extrapolar automáticamente andexanet.')
        if site in INTRACRANIAL:
            actions.append('NCS/SCCM 2026 favorece condicionalmente PCC de cuatro factores sobre andexanet en HIC por anti-Xa oral; no combinar ambos de rutina ni extrapolar eficacia específica a agentes sin datos suficientes.')
        if not inputs['pcc_product_available']:
            actions.append('Coordinar disponibilidad de un producto y traslado/soporte hemostático urgente; no sustituirlo por vitamina K o protamina como antídotos del anti-Xa.')
        return _support('factor_xa_specialist_hemostasis', 'Hemostasia urgente con selección documentada de una estrategia específica para ' + agent + '.', actions,
                        information=['Fármaco/dosis/hora, actividad residual, función renal, producto hemostático, pauta íntegra, techo y tratamiento previo.'], sources=source_ids)

    if key == 'reversal-fondaparinux':
        actions.append('No usar protamina como reversor de fondaparinux. Comprobar dosis, última toma/inyección, función renal y ensayo anti-Xa calibrado si es accesible.')
        if inputs['residual_activity'] == 'not_detected_reliable_assay':
            actions.append('Un ensayo apropiado excluye efecto residual relevante: buscar otra causa del sangrado y tratarla; no indicar aPCC/rFVIIa empíricamente solo por el antecedente de fondaparinux.')
            return _support('fondaparinux_no_relevant_activity', 'Actividad de fondaparinux excluida con una prueba fiable; no generar reversión empírica.', actions, sources=source_ids)
        if site in INTRACRANIAL and inputs['exposure_intensity'] == 'prophylactic' and inputs['renal_function'] == 'preserved' and not inputs['bioaccumulation_evidence']:
            return _support('fondaparinux_prophylaxis_no_accumulation', 'No hay indicación automática de reversión de una pauta profiláctica sin evidencia de acumulación.', actions, sources=source_ids)
        if site in INTRACRANIAL:
            actions.append('En HIC con exposición terapéutica o acumulación, NCS/SCCM 2016 describe aPCC 20 UI/kg; si no puede emplearse, rFVIIa 90 microgramos/kg. Son opciones de baja evidencia para decisión especializada, no una pauta universal ni equivalentes a PCC no activado.')
        else:
            actions.append('La ficha no establece antídoto; priorizar foco y soporte. No extrapolar las opciones de HIC a todo sangrado extracraneal o procedimiento.')
        return _support('fondaparinux_contextual_hemostasis', 'Estrategia específica según exposición, acumulación y localización.', actions, sources=source_ids)

    if key == 'reversal-enoxaparin-over12':
        if inputs['residual_activity'] == 'not_detected_reliable_assay' and not inputs['ongoing_bleeding']:
            code, summary = 'enoxaparin_late_no_routine_protamine', 'Después de 12 h, sin efecto relevante ni sangrado persistente, protamina habitualmente no es necesaria.'
            actions.append('Vigilar evolución y reconsiderar si aparece sangrado o cambia la interpretación de la exposición; no administrar protamina por el reloj solamente.')
        else:
            code, summary = 'enoxaparin_late_residual_review', 'Más de 12 h no descarta efecto en acumulación renal o sangrado persistente.'
            actions += ['Revisar última dosis real, dosis repetidas, función renal, actividad anti-Xa pertinente y protamina previa.',
                        'Si existe actividad clínicamente relevante, decidir protamina de forma individual; este contrato no prolonga automáticamente las fórmulas de ≤12 h.',
                        'La neutralización anti-Xa es incompleta (hasta aproximadamente 60%); controlar sangrado y no repetir protamina automáticamente.']
        return _support(code, summary, actions, sources=source_ids)

    if key in ('reversal-argatroban', 'reversal-bivalirudin'):
        argatroban = key == 'reversal-argatroban'
        agent = 'argatrobán' if argatroban else 'bivalirudina'
        if inputs['infusion_running']:
            actions.append('Detener la perfusión de ' + agent + ' en el contexto de hemorragia/sobredosis que requiere reversión y comprobar bomba, velocidad y dosis realmente administrada.')
        actions.append('No existe un antídoto específico establecido en la ficha consultada; controlar el foco, hemodinámica, hemoglobina y coagulación pertinente de forma seriada.')
        if argatroban:
            actions.append('Seguir aPTT y función hepática; tras suspender, el efecto suele reducirse en 2–4 h y puede prolongarse con insuficiencia hepática. Ese intervalo no autoriza esperar ante sangrado crítico.')
        else:
            actions.append('Revisar función renal y ajustar la interpretación del aclaramiento; bivalirudina es hemodializable, pero la selección de depuración requiere decisión clínica/nefrólogica y no sustituye la hemostasia inmediata.')
        if inputs['coagulation_test_state'] == 'normalized':
            actions.append('Si coagulación pertinente se normaliza y persiste sangrado, buscar lesión/fuente u otra coagulopatía; no añadir un antídoto ficticio.')
        return _support('dti_stop_support_reassess', 'Suspensión y soporte dirigidos a ' + agent + ', con reevaluación de aclaramiento.', actions, sources=source_ids)

    if key == 'reversal-other-dti':
        named = inputs['agent_status']
        if named in ('dabigatran', 'argatroban', 'bivalirudin'):
            actions.append('Dirigir a la ruta específica de ' + named + '; idarucizumab solo corresponde a dabigatrán.')
        elif named == 'unknown':
            actions.append('Verificar agente con registros, administración y laboratorio; utilizar la ruta de agente desconocido mientras se identifica.')
        else:
            actions.append('Suspender el inhibidor confirmado y revisar ficha exacta, última dosis, duración de perfusión, aclaramiento y pruebas pertinentes.')
            if site in INTRACRANIAL:
                actions.append('Las opciones no específicas de NCS/SCCM 2016 para HIC por otros DTI tienen evidencia limitada: decidir producto y pauta con experiencia en hemostasia; no sustituir una elección clínica por una dosis universal de PCC.')
        return _support('other_dti_identify_route', 'Identificar el inhibidor y aplicar una estrategia específica.', actions, sources=source_ids)

    if key == 'reversal-danaparoid':
        actions += ['Suspender danaparoide en hemorragia grave, controlar el foco y revisar función renal y actividad anti-Xa calibrada.',
                    'La ficha no recomienda protamina como reversor: la neutralización parcial no demuestra beneficio hemostático.',
                    'Si no se controla, valorar soporte transfusional y, en casos seleccionados, plasmaféresis con el equipo experto según la ficha; no convertir esta posibilidad en un tratamiento rutinario.']
        if site in INTRACRANIAL and not inputs['bleeding_controlled']:
            actions.append('La opción rFVIIa de NCS/SCCM 2016 para HIC es de evidencia muy baja y exige valoración trombótica y producto específico; no se emite una dosis automática.')
        return _support('danaparoid_support_clearance', 'Hemostasia y aclaramiento individualizados; sin cálculo de protamina.', actions, sources=source_ids)

    if key == 'reversal-fibrinolytics':
        actions += ['Si persiste una perfusión de fibrinolítico y se sospecha hemorragia relevante, detenerla; obtener hemograma, PT/INR, aPTT, fibrinógeno y pruebas pretransfusionales.',
                    'La sospecha de hemorragia intracraneal sintomática requiere TC urgente y coordinación neurocrítica/neuroquirúrgica.']
        in_window = inputs['fibrinolytic_timing'] == 'within_24_hours'
        if not inputs['symptomatic_intracranial_bleeding'] or not in_window:
            actions.append('La pauta aquí revisada de crioprecipitado corresponde a HIC sintomática en las primeras 24 h. Fuera de ese contexto, dirigir hemostasia a la causa, el fibrinógeno y la valoración clínica sin aplicar automáticamente esa dosis.')
            return _support('fibrinolytic_context_review', 'Definir localización, síntomas y tiempo antes de seleccionar la pauta.', actions, sources=source_ids)
        aha = (inputs['fibrinolytic_agent'] in ('alteplase', 'tenecteplase')
               and inputs['fibrinolysis_indication'] == 'acute_ischemic_stroke')
        if inputs['cryoprecipitate_available_appropriate']:
            if not inputs['initial_cryoprecipitate_already_given']:
                timing = ' En la pauta AHA/ASA 2026 seleccionada, administrar en 10–30 min.' if aha else ''
                actions.append('Para este contexto, la pauta inicial de referencia es crioprecipitado 10 unidades; confirmar con transfusión la equivalencia del componente disponible y administrar conforme al régimen seleccionado.' + timing)
            elif inputs['fibrinogen_state'] == 'below_150_mg_dl':
                actions.append('Fibrinógeno <150 mg/dL después de la dosis inicial: valorar crioprecipitado adicional guiado por fibrinógeno y evolución, sin repetir 10 unidades automáticamente.')
            else:
                actions.append('Revisar el fibrinógeno posterior y la respuesta clínica antes de administrar más componente; no repetir por programación.')
        elif aha:
            actions.append('AHA/ASA 2026, tabla 5: si los hemoderivados no pueden utilizarse o el crioprecipitado se demora, valorar ácido tranexámico 1000 mg IV durante 10 min. Verificar riesgos y producto antes de emitir una orden; no mezclarlo con la pauta ponderal NCS 2016.')
        else:
            actions.append('NCS/SCCM 2016 contempla ácido tranexámico 10–15 mg/kg IV durante 20 min como alternativa si crioprecipitado no puede emplearse a tiempo. Pauta contextual de baja evidencia; requiere selección clínica y producto confirmado.')
        actions.append('Repetir fibrinógeno y mantener objetivo ≥150 mg/dL en esta pauta; vigilar estado neurológico, hemostasia, presión arterial y necesidad de intervención.')
        return _support('fibrinolytic_sich_hemostasis', 'Ruta de HIC sintomática tras fibrinólisis, con régimen de referencia explícito.', actions,
                        information=['Componente transfusional real y equivalencia de unidades, fibrinógeno seriado y tratamientos ya administrados.'],
                        sources=['AHA_AIS_2026'] if aha else ['NCS_2016'])

    if key == 'reversal-antiplatelets':
        actions.append('Confirmar antiagregante, última dosis, plaquetas y posibles coexposiciones; suspenderlo en HIC y coordinar cualquier interrupción con su indicación trombótica.')
        if inputs['independent_platelet_transfusion_indication']:
            actions.append('Evaluar la indicación transfusional independiente por su propio protocolo; la regla de reversión farmacológica no prohíbe tratar trombocitopenia u otra indicación demostrada.')
        if site == 'spontaneous_intraparenchymal' and not inputs['urgent_neurosurgery_planned']:
            code, summary = 'antiplatelet_avoid_routine_platelets', 'Evitar transfusión de plaquetas para revertir antiagregación en hemorragia intraparenquimatosa espontánea sin neurocirugía.'
        elif site == 'spontaneous_intraparenchymal' and inputs['antiplatelet_agent'] == 'aspirin' and inputs['urgent_neurosurgery_planned']:
            code, summary = 'aspirin_neurosurgery_platelet_consideration', 'NCS/SCCM 2026 sugiere plaquetas en hemorragia intraparenquimatosa espontánea bajo aspirina que requiere cirugía.'
            actions.append('Coordinar componente, momento y reevaluación con neurocirugía/transfusión; esta recomendación condicional no fija una dosis universal para cualquier antiagregante.')
        elif site == 'traumatic_intracranial':
            code, summary = 'antiplatelet_traumatic_ich_uncertainty', 'NCS/SCCM 2026 no pudo recomendar a favor ni en contra de plaquetas para HIC traumática asociada a antiagregantes.'
            actions.append('Decidir según sangrado, cirugía, coagulopatía y pruebas pertinentes; si está disponible, considerar evaluación viscoelástica para coagulopatía traumática.')
        else:
            code, summary = 'antiplatelet_contextual_hemostasis', 'Decisión especializada según agente, localización y procedimiento; sin transfusión automática.'
        actions.append('La actualización NCS/SCCM 2026 tampoco establece una recomendación de desmopresina para este fin; no automatizar una dosis universal ni copiar la recomendación antigua como vigente.')
        return _support(code, summary, actions, sources=source_ids)

    if key == 'reversal-unknown':
        actions += ['Reconstruir fármaco, dosis, vía, última administración y coexposiciones usando envases, receta, registro de administración, prescriptor y farmacia.',
                    'Obtener hemograma, PT/INR, aPTT, fibrinógeno, función renal/hepática y muestra previa a reversión cuando sea posible sin retrasar la atención.',
                    'PT/INR o aPTT normales no excluyen todos los DOAC; seleccionar pruebas con calibración y sensibilidad apropiadas.']
        if not inputs['medication_records_accessible']:
            actions.append('Solicitar ayuda de acompañantes, prescriptor/farmacia y registro de administración para recuperar la exposición; mantener explícito que el agente sigue sin identificar.')
        if inputs['drug_calibrated_anti_xa_available']:
            actions.append('Solicitar anti-Xa con calibrador del fármaco sospechado y comprobar interferencias de heparina/otros anti-Xa; no convertir un resultado genérico en identidad del agente.')
        else:
            actions.append('Si anti-Xa específico no es accesible, integrar hora, registros y pruebas disponibles con el laboratorio; no interpretar ausencia de prueba como ausencia de efecto.')
        if inputs['dabigatran_assay_available']:
            actions.append('Usar dTT/ECT o prueba validada pertinente para apoyar/excluir actividad de dabigatrán según sensibilidad y contexto.')
        actions.append('En sangrado crítico, decidir rescate con el equipo experto según exposición más probable y balance riesgo/beneficio, sin esperar confirmación perfecta ni emitir un cóctel automático de antídotos.')
        return _support('unknown_agent_identification', 'Flujo operativo de estabilización e identificación, sin dosis empírica universal.', actions,
                        information=['Agente, dosis/hora, indicación, sitio/severidad, función renal/hepática, pruebas pertinentes y reversores ya usados.'], sources=source_ids)
    raise ValueError('Contrato de reversión no reconocido: ' + key)
