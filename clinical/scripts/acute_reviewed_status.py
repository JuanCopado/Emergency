"""Reviewed adult status workflows: source-bound loading or specialist decisions.

The caller validates field types, limits, expected values and required_if before
calling validation_errors(). No product-volume inference is made in dose-only
mode. The refractory workflow never returns an anaesthetic prescription.
"""
from math import isclose


REVIEW_REFERENCE = 'references/acute-status-reviewed-2026-11-16.md'
PHENYTOIN_ID = 'status-phenytoin-local'  # Stable compatibility ID, not a location gate.
REFRACTORY_ID = 'status-refractory'
PREPARATION_CONDITION = {'key': 'calculation_scope', 'equals': 'verified_preparation'}
GALWAY_URL = 'https://www.medinfogalway.ie/ivguides/phenytoin-intravenous-adults'
NICE_URL = 'https://www.nice.org.uk/guidance/ng217/chapter/treating-status-epilepticus-repeated-or-cluster-seizures-and-prolonged-seizures'
ICS_URL = 'https://pmc.ncbi.nlm.nih.gov/articles/PMC12062632/'


def reviewed_contracts(contract, field):
    """Keep both public IDs; replace only the two historical status blockers."""
    def preparation_field(key, label, kind='boolean', **rules):
        return field(key, label, kind, required_if=dict(PREPARATION_CONDITION), **rules)

    phenytoin = contract(
        PHENYTOIN_ID, 'Fenitoína IV — carga inicial adulta; dosis o preparación verificada',
        'status', 'Status epiléptico', 'Fenitoína sódica',
        'neurologic.md', 'status-epilepticus', ['second-line'],
        [
            field('age_years', 'Edad (años); este contrato se limita a adultos de 18 años o más', 'number', minimum=18),
            field('weight_kg', 'Peso corporal verificado (kg)', 'number', positive=True),
            field('convulsive_status_confirmed', 'Estatus convulsivo confirmado y persistente tras benzodiazepina adecuada', expected=True),
            field('adequate_benzodiazepine_given', 'Benzodiazepina y dosis previa adecuadas confirmadas', expected=True),
            field('previous_phenytoin_or_fosphenytoin', 'Fenitoína/fosfenitoína previa o tratamiento habitual: requiere evaluación de recarga', expected=False),
            field('cause_specific_pathway_required', 'Se requiere una pauta causal diferente, como eclampsia o crisis tóxicas', expected=False),
            field('cardiac_contraindication_present', 'Bradicardia sinusal, bloqueo sinoauricular/AV de segundo o tercer grado, o Adams–Stokes', expected=False),
            field('standard_loading_appropriate', 'La carga seleccionada de 20 mg/kg (máx. 2 g) es adecuada tras revisión clínica, hepática, cardíaca y de interacciones', expected=True),
            field('elderly_or_cardiac_risk', 'Paciente de edad avanzada o con enfermedad cardíaca; revisión de velocidad reducida'),
            field('max_rate_mg_min', 'Velocidad máxima individual seleccionada (mg/min; nunca superior a 50)', 'number', positive=True, maximum=50),
            field('duration_min', 'Duración elegida para esta carga (min); referencia de proyecto: al menos 40', 'number', minimum=40),
            field('calculation_scope', 'Alcance del resultado', 'choice', options=['dose_only', 'verified_preparation'], option_labels={'dose_only': 'Dosis y tiempo', 'verified_preparation': 'Dosis, preparación verificada y bomba'}),
            preparation_field('preparation_product', 'Producto exacto cubierto por la preparación Galway', 'choice', options=['Epanutin 250 mg/5 mL', 'Phenytoin (Mercury) 250 mg/5 mL']),
            preparation_field('concentration', 'Concentración del producto comprobada (mg/mL)', 'number', expected=50, positive=True),
            preparation_field('product_preparation_matched', 'Producto y procedimiento completo cotejados; no basta una concentración equivalente', expected=True),
            preparation_field('diluent', 'Diluyente de esta preparación', 'choice', options=['NaCl 0.9%'], expected='NaCl 0.9%'),
            preparation_field('diluent_volume_ml', 'Volumen real verificado de NaCl 0,9% antes de añadir el fármaco (mL)', 'number', positive=True),
            preparation_field('final_volume_ml', 'Volumen FINAL real verificado, incluyendo fármaco (mL)', 'number', positive=True),
            preparation_field('actual_volumes_verified', 'Volúmenes reales y manejo de sobrellenado comprobados; no se usa solo el volumen nominal de la bolsa', expected=True),
            preparation_field('elapsed_since_preparation_min', 'Tiempo transcurrido desde la preparación antes del inicio previsto (min)', 'number', minimum=0),
            preparation_field('immediate_start_confirmed', 'Preparación para inicio inmediato; no almacenar ni programar una espera', expected=True),
            preparation_field('drawup_filter_5micron_verified', 'Extracción con filtro de 5 micras conforme a esta preparación', expected=True),
            preparation_field('inline_filter_0_2micron_verified', 'Filtro en línea de 0,2 micras y sistema de infusión verificados', expected=True),
            preparation_field('large_vein_access_verified', 'Acceso venoso de gran calibre y vigilancia del punto de infusión disponibles', expected=True),
            preparation_field('pre_flush_confirmed', 'Lavado previo con NaCl 0,9% confirmado', expected=True),
            preparation_field('post_flush_volume_ml', 'Volumen verificado de lavado final que administra el fármaco residual del sistema (mL)', 'number', positive=True),
            preparation_field('post_flush_plan_verified', 'Lavado final con NaCl 0,9% a la MISMA velocidad de bomba; volumen suficiente del sistema confirmado', expected=True),
            preparation_field('solution_clear', 'Ampolla y mezcla sin turbidez ni precipitado', expected=True),
        ],
        reviewed_workflow='status', review_reference=REVIEW_REFERENCE,
        model='reviewed_phenytoin', dose_unit='mg',
        maximum={'value': 2000, 'unit': 'mg', 'scope': 'carga inicial de esta pauta'},
        administration='Carga IV inicial seleccionada: 20 mg/kg, máximo 2 g. Respetar la velocidad individual y monitorizar ECG, presión arterial y respiración. No convertir mg en mg PE.',
        limitations=[
            'Adultos de 18 años o más con estatus convulsivo; no calcula recarga, mantenimiento, pediatría ni una pauta causal específica.',
            'La dosis clínica seleccionada no hace intercambiables las fichas de producto. Algunas fichas recomiendan otra carga o preparación; verificar su aplicabilidad al caso.',
            'Los 40 min mínimos son la referencia adoptada previamente por el propietario para este contrato, no una exigencia universal de Galway.',
            'En edad avanzada/enfermedad cardíaca este contrato usa un techo conservador de 25 mg/min; puede requerirse una velocidad aún menor u otra pauta individual.',
        ],
        regimen_source={'url': GALWAY_URL, 'checked': '2026-11-16', 'scope': 'adult initial loading; source-specific preparation when requested'},
    )
    for item in phenytoin['fields']:
        if item['key'] == 'monitoring_ready':
            item['label'] = 'ECG, presión arterial y respiración monitorizados, con medios de rescate disponibles'
        elif item['key'] == 'local_protocol_verified':
            item['label'] = 'Pauta clínica seleccionada y contexto de uso verificados'

    refractory = contract(
        REFRACTORY_ID, 'Estatus refractario o falta de recuperación — escalada especializada',
        'status', 'Status epiléptico', 'Valoración y escalada; sin pauta anestésica automática',
        'neurologic.md', 'status-epilepticus', ['Refractory status epilepticus'],
        [
            field('age_years', 'Edad (años); este flujo se limita a adultos de 18 años o más', 'number', minimum=18),
            field('obstetric_context', 'Contexto obstétrico/eclampsia: requiere su circuito específico', expected=False),
            field('adequate_benzodiazepine_given', 'Tratamiento inicial adecuado con benzodiazepina confirmado', expected=True),
            field('adequate_second_line_given', 'Segunda línea adecuada completada; dosis, vía, tiempo y respuesta revisados', expected=True),
            field('second_line_agent', 'Antiepiléptico de segunda línea ya administrado', 'choice', options=['levetiracetam', 'valproate', 'fosphenytoin', 'phenytoin']),
            field('current_state', 'Situación actual tras el tratamiento', 'choice', options=['ongoing_convulsions', 'no_convulsions_impaired_consciousness', 'electrographic_seizures'], option_labels={'ongoing_convulsions': 'Persisten las convulsiones', 'no_convulsions_impaired_consciousness': 'Sin convulsiones visibles, sin recuperación de conciencia', 'electrographic_seizures': 'Crisis documentadas por EEG'}),
            field('eeg_evidence_available', 'Existe EEG que documenta la actividad epiléptica actual'),
            field('expert_team_contacted', 'Equipo experto de UCI/anestesia/neurología ya contactado'),
            field('critical_care_available', 'Cuidados críticos adecuados disponibles para el paciente'),
            field('continuous_eeg_available', 'EEG continuo accesible de inmediato o mediante un circuito establecido'),
            field('airway_support_available', 'Equipo y medios para soporte avanzado de vía aérea/ventilación disponibles'),
            field('cause_specific_pathway_required', 'Se sospecha causa que requiere tratamiento específico, por ejemplo tóxica o metabólica'),
        ],
        route=None, reviewed_workflow='status', review_reference=REVIEW_REFERENCE,
        model='specialist_decision_support',
        administration='Apoyo a la evaluación urgente, monitorización, consulta y traslado; la selección de anestesia y antiepilépticos adicionales corresponde al equipo experto.',
        limitations=[
            'Flujo adulto no obstétrico. No genera dosis, preparación, velocidad de bomba ni autorización para anestesia.',
            'La ausencia de recuperación de conciencia tras cesar las convulsiones no confirma por sí sola estatus no convulsivo: requiere evaluación y EEG.',
            'La falta de recursos activa acciones de escalada/traslado y no impide consultar este flujo.',
        ],
        regimen_source={'urls': [NICE_URL, ICS_URL], 'checked': '2026-11-16', 'scope': 'adult specialist escalation and EEG; no automatic anaesthetic regimen'},
    )
    # A decision-support workflow does not pretend to select a medicine or IV route.
    refractory['fields'] = [item for item in refractory['fields'] if item['key'] not in {
        'route', 'allergy_contraindication_present', 'interaction_reviewed',
    }]
    for item in refractory['fields']:
        if item['key'] == 'monitoring_ready':
            item.pop('expected', None)
            item['label'] = 'Monitorización clínica y fisiológica disponible'
        elif item['key'] == 'local_protocol_verified':
            item['label'] = 'Guía de escalada y contexto clínico revisados'
    return [phenytoin, refractory]


def _dose(weight_kg):
    # Cap first, so a finite but extremely large weight cannot overflow 20 * weight.
    return 20 * min(weight_kg, 100)


def _saline_volume(dose_mg):
    return 50 if dose_mg < 500 else 100 if dose_mg <= 1000 else 250


def validation_errors(row, inputs):
    """Cross-field checks only; the API has validated every active input first."""
    if row['id'] == REFRACTORY_ID:
        if inputs['current_state'] == 'electrographic_seizures' and not inputs['eeg_evidence_available']:
            return [('eeg_evidence', 'No declarar estatus electrográfico sin EEG que lo documente; seleccionar la situación clínica observada y solicitar evaluación urgente.')]
        if inputs['current_state'] == 'no_convulsions_impaired_consciousness' and inputs['eeg_evidence_available']:
            return [('eeg_state', 'Si el EEG ya documenta crisis actuales, seleccionar la situación electrográfica; no registrar el caso solo como falta de recuperación sin confirmar.')]
        return []
    if row['id'] != PHENYTOIN_ID:
        raise ValueError('Unsupported reviewed status contract')

    errors = []
    dose = _dose(inputs['weight_kg'])
    rate = dose / inputs['duration_min']
    if inputs['elderly_or_cardiac_risk'] and inputs['max_rate_mg_min'] > 25:
        errors.append(('individual_rate', 'Edad avanzada/enfermedad cardíaca: esta pauta condicionada exige seleccionar un límite individual de 25 mg/min o menor; no asume que 25 sea adecuado para todos.'))
    if rate > inputs['max_rate_mg_min'] and not isclose(rate, inputs['max_rate_mg_min'], rel_tol=1e-12):
        errors.append(('infusion_rate', 'La duración elegida supera la velocidad máxima individual. Replantear la duración/pauta; nunca acelerar para cumplir la caducidad.'))
    if inputs['calculation_scope'] == 'dose_only':
        return errors

    saline = inputs['diluent_volume_ml']
    final_volume = inputs['final_volume_ml']
    required_saline = _saline_volume(dose)
    if saline != required_saline:
        errors.append(('source_dilution', 'Esta preparación exige ' + str(required_saline) + ' mL reales de NaCl 0,9% según el tramo de dosis. No reducir ni sustituir la bolsa por otra mayor sin otra preparación validada.'))
    expected_final = saline + dose / inputs['concentration']
    if not isclose(final_volume, expected_final, rel_tol=1e-9, abs_tol=1e-9):
        errors.append(('actual_final_volume', 'El volumen final verificado no concuerda con el NaCl real más el volumen de fármaco. Resolver sobrellenado/extracción; no inferir mL/h del volumen nominal.'))
    if dose / final_volume > 10:
        errors.append(('final_concentration', 'Se supera el techo de 10 mg/mL de esta preparación concreta; no producir una velocidad de bomba.'))
    # Include delivery of drug left in the administration set. The actual flush
    # volume is supplied and verified by the clinician; no fixed volume is invented.
    post_flush_duration = inputs['duration_min'] * (inputs['post_flush_volume_ml'] / final_volume)
    completion = inputs['elapsed_since_preparation_min'] + inputs['duration_min'] + post_flush_duration
    if completion > 60 and not isclose(completion, 60, rel_tol=1e-12):
        errors.append(('preparation_window', 'La administración y el lavado que entrega el fármaco residual no terminan dentro de los 60 min desde la preparación. No acelerar ni prolongar la estabilidad: revisar una alternativa específica.'))
    return errors


def calculate(row, inputs):
    """Return a partial result only after the caller has passed all input gates."""
    if row['id'] == REFRACTORY_ID:
        return _refractory_decision(inputs)
    if row['id'] != PHENYTOIN_ID:
        raise ValueError('Unsupported reviewed status contract')
    dose = _dose(inputs['weight_kg'])
    duration = inputs['duration_min']
    result = {
        'result_kind': 'calculation', 'dose': dose, 'dose_unit': 'mg',
        'duration_min': duration, 'infusion_rate_mg_min': dose / duration,
        'amount_per_hour': dose * 60 / duration, 'amount_per_hour_unit': 'mg/h',
        'concentration': None, 'withdrawal_ml': None,
        'administration_volume_ml': None, 'pump_ml_h': None,
        'preparation': None, 'compatibility': None, 'stability': None,
        'calculation_scope': inputs['calculation_scope'],
        'capabilities': {'dose_and_time': True, 'product_withdrawal': False, 'pump_setting': False},
        'limitations': list(row['limitations']),
        'next_actions': ['Reevaluar respuesta, efectos adversos y causa; no repetir automáticamente una carga ni inferir mantenimiento de este resultado.'],
    }
    if inputs['calculation_scope'] == 'dose_only':
        result['limitations'].append('Solo dosis/tiempo en mg de la pauta seleccionada: no se han establecido producto, dilución, volumen, estabilidad ni mL/h. Verificar esos datos antes de preparar o administrar.')
        return result

    final_volume = inputs['final_volume_ml']
    pump = final_volume * 60 / duration
    flush_duration = duration * (inputs['post_flush_volume_ml'] / final_volume)
    result.update({
        'concentration': {'value': dose / final_volume, 'unit': 'mg/mL', 'role': 'final'},
        'stock_concentration': {'value': inputs['concentration'], 'unit': 'mg/mL', 'role': 'stock'},
        'withdrawal_ml': dose / inputs['concentration'],
        'administration_volume_ml': final_volume, 'pump_ml_h': pump,
        'capabilities': {'dose_and_time': True, 'product_withdrawal': True, 'pump_setting': True},
        'preparation': {
            'source': GALWAY_URL, 'product': inputs['preparation_product'],
            'diluent': inputs['diluent'], 'actual_diluent_ml': inputs['diluent_volume_ml'],
            'actual_final_volume_ml': final_volume,
            'drawup_filter_micron': 5, 'inline_filter_micron': 0.2,
            'post_flush': {'diluent': 'NaCl 0.9%', 'verified_volume_ml': inputs['post_flush_volume_ml'], 'pump_ml_h': pump, 'duration_min': flush_duration},
        },
        'compatibility': 'Esta preparación: NaCl 0,9% exclusivamente; comprobar compatibilidad del sistema y evitar mezclas no verificadas.',
        'stability': {
            'scope': 'Solo la preparación Galway comprobada para el producto seleccionado; no generalizar a otros productos.',
            'start': 'Inmediatamente tras preparar; no almacenar la mezcla.',
            'maximum_completion_from_preparation_min': 60,
            'elapsed_before_start_min': inputs['elapsed_since_preparation_min'],
            'completion_including_drug_delivery_flush_min': inputs['elapsed_since_preparation_min'] + duration + flush_duration,
        },
    })
    result['next_actions'].append('Vigilar ECG, presión arterial, respiración y punto de infusión; interrumpir y reevaluar ante deterioro, reacción, extravasación o precipitación. Lavar al mismo ritmo para evitar un bolo del residuo.')
    return result


def _refractory_decision(inputs):
    state = inputs['current_state']
    confirmed = state in ('ongoing_convulsions', 'electrographic_seizures')
    actions = []
    if not inputs['expert_team_contacted']:
        actions.append('Activar ahora UCI/anestesia y neurología; comunicar fármacos, dosis, tiempos y respuesta ya comprobados.')
    else:
        actions.append('Mantener coordinación urgente con UCI/anestesia y neurología y documentar su plan.')
    if not inputs['monitoring_ready']:
        actions.append('Organizar monitorización clínica y fisiológica inmediata durante estabilización y traslado.')
    if not inputs['airway_support_available']:
        actions.append('Solicitar equipo de vía aérea/ventilación y soporte de rescate; no iniciar una infusión anestésica sin capacidad de soporte.')
    else:
        actions.append('Reevaluar vía aérea, ventilación y circulación; el equipo experto decide la necesidad de intubación y soporte.')
    if confirmed:
        actions.append('Persistencia de crisis tras benzodiazepina y segunda línea adecuadas: manejo urgente de estatus refractario con el equipo experto, que decide un antiepiléptico alternativo o anestesia general según el caso.')
    else:
        actions.append('Sin convulsiones visibles pero sin recuperación: evaluar causas posictales/farmacológicas/metabólicas y solicitar EEG urgente; no diagnosticar estatus no convulsivo solo por la conciencia alterada.')
    if inputs['continuous_eeg_available']:
        actions.append('Coordinar EEG continuo para valorar actividad persistente y la respuesta al tratamiento especializado.')
    else:
        actions.append('Solicitar asesoramiento a un centro con neurofisiología/neurocríticos y acordar acceso a EEG y traslado cuando corresponda; su ausencia no debe retrasar la estabilización.')
    if not inputs['critical_care_available']:
        actions.append('Organizar consulta y traslado seguro a cuidados críticos con las capacidades requeridas mientras continúa la estabilización.')
    if inputs['cause_specific_pathway_required']:
        actions.append('Activar en paralelo el circuito de la causa identificada o sospechada; este flujo no calcula tratamiento toxicológico o metabólico específico.')
    actions.append('Revisar causas reversibles y tratamiento antiepiléptico previo; acordar continuación, investigación y vigilancia con el equipo experto.')
    return {
        'result_kind': 'decision_support', 'treatment_calculated': False,
        'dose': None, 'dose_unit': None, 'concentration': None,
        'withdrawal_ml': None, 'administration_volume_ml': None, 'pump_ml_h': None,
        'duration_min': None, 'amount_per_hour': None, 'amount_per_hour_unit': None,
        'preparation': None, 'compatibility': None, 'stability': None,
        'capabilities': {'specialist_escalation': True, 'anaesthetic_regimen': False, 'pump_setting': False},
        'decision_support': {
            'stage': 'refractory_status' if confirmed else 'persistent_impaired_consciousness_requires_eeg',
            'refractory_status_supported_by_entered_state': confirmed,
            'priority': 'urgent', 'current_state': state,
            'previous_second_line_agent': inputs['second_line_agent'],
            'resource_gaps': [key for key in ('monitoring_ready', 'expert_team_contacted', 'critical_care_available', 'continuous_eeg_available', 'airway_support_available') if not inputs[key]],
            'anaesthetic_treatment_authorized': False,
        },
        'next_actions': actions,
    }
