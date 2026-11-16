"""Two owner-reviewed anaphylaxis workflows; clinical selection stays explicit.

The API validates the same field metadata before calling this module. Validation
here also makes direct use of these high-risk calculation helpers fail closed.
No hospital profile, automatic redosing, pump programming or titration is assumed.
"""
from decimal import Decimal, InvalidOperation
from math import isfinite


REVIEW_REFERENCE = 'references/acute-anaphylaxis-reviewed-2026-11-16.md'
IM_ID = 'anaphylaxis-under6months'
INFUSION_ID = 'anaphylaxis-refractory'
IM_REGIMENS = ['erc_wao_weight_based', 'rcuk_age_banded']
EARLY_REPEAT_CONTEXTS = ['none', 'documented_expert_decision_for_life_threatening_recurrence']


def reviewed_contracts(contract, field):
    """Return only the two existing IDs replaced by this reviewed delivery."""
    repeat = {'key': 'dose_phase', 'equals': 'repeat'}

    def shared(route, population=None):
        population_rules = {'options': ['adult', 'pediatric']}
        if population is not None:
            population_rules['expected'] = population
        return [
            field('population', 'Población; adulto desde 18 años para este formulario', 'choice', **population_rules),
            field('route', 'Vía de esta pauta', 'choice', options=['IM', 'IV'], expected=route),
            field('indication_confirmed', 'Anafilaxia confirmada clínicamente por el profesional', expected=True),
            field('clinical_situation', 'Situación clínica', 'choice',
                  options=['anaphylaxis', 'cardiac_arrest', 'resuscitation_at_birth'], expected='anaphylaxis'),
            field('adrenaline_risk_assessment_completed',
                  'Riesgos, interacciones y producto valorados; no retrasar IM por contraindicaciones relativas', expected=True),
        ]

    im_fields = shared('IM', 'pediatric') + [
        field('age_months', 'Edad cronológica verificada (meses; menos de 6)', 'number', minimum=0, exclusive_maximum=6),
        field('weight_kg', 'Peso actual verificado (kg)', 'number', positive=True),
        field('abc_compromise', 'Compromiso actual de vía aérea, respiración o circulación por anafilaxia', expected=True),
        field('concentration', 'Concentración IM del producto (mg/mL)', 'number', expected=1, positive=True),
        field('undiluted_im', 'Producto de 1 mg/mL SIN DILUIR para vía IM', expected=True),
        field('product_verified', 'Producto, integridad, caducidad y vía IM comprobados', expected=True),
        field('measurement_increment_ml', 'Incremento medible validado del dispositivo (mL)', 'number', positive=True),
        field('minimum_measurable_volume_ml', 'Menor volumen con exactitud de entrega verificada (mL)', 'number', positive=True),
        field('syringe_capacity_ml', 'Capacidad de la jeringa seleccionada (mL)', 'number', positive=True),
        field('device_delivery_accuracy_verified', 'Exactitud del volumen entregado verificada; no basta la graduación', expected=True),
        field('im_needle_and_site_verified', 'Aguja adecuada para llegar al músculo y cara anterolateral del muslo verificadas', expected=True),
        field('monitoring_and_help_plan', 'Reevaluación, monitorización cuanto antes y ayuda de reanimación previstas', expected=True),
        field('dose_phase', 'Primera dosis o repetición', 'choice', options=['initial', 'repeat']),
        field('prior_im_doses', 'Número real de dosis IM previas', 'number', minimum=1, integer=True, required_if=repeat),
        field('last_im_dose_micrograms', 'Última dosis IM realmente administrada (microgramos)', 'number', positive=True, maximum=500, required_if=repeat),
        field('last_im_dose_regimen', 'Pauta de la dosis IM previa', 'choice', options=IM_REGIMENS, required_if=repeat),
        field('elapsed_min', 'Minutos desde la última dosis IM', 'number', positive=True, required_if=repeat),
        field('early_repeat_context', 'Decisión experta documentada; no habilita cálculo antes de 5 min', 'choice', options=EARLY_REPEAT_CONTEXTS, required_if=repeat),
        field('refractory_escalation_active', 'Tras dos dosis: escalada experta por posible anafilaxia refractaria activa', required_if=repeat),
        field('iv_infusion_running', '¿Ya está administrándose la perfusión IV de adrenalina?', expected=False, required_if=repeat),
    ]
    im = contract(
        IM_ID, 'Anafilaxia — menor de 6 meses, adrenalina IM ponderal',
        'anaphylaxis', 'Adrenalina / anafilaxia', 'Adrenalina',
        'infection-respiratory.md', 'anaphylaxis',
        ['0.01 mg/kg', '1 mg/mL', '100--150 micrograms'], [], route='IM', population='pediatric',
        model='reviewed_anaphylaxis_im', dose_unit='micrograms',
        reviewed_workflow='anaphylaxis', review_reference=REVIEW_REFERENCE,
        concentration={'value': 1, 'unit': 'mg/mL', 'role': 'undiluted IM product'},
        maximum={'value': 500, 'unit': 'micrograms', 'scope': 'ERC/WAO single-dose ceiling, not an infant minimum'},
        preparation='Adrenalina 1 mg/mL SIN DILUIR. 0,01 mg/kg = 10 microgramos/kg = 0,01 mL/kg; sin mínimo de 0,1 mg y sin redondeo automático.',
        compatibility='Vía IM exclusivamente en este contrato. No diluir a 0,1 mg/mL ni usar la bolsa IV de 10 microgramos/mL.',
        stability='Producto íntegro y vigente; uso inmediato tras apertura según su ficha. No se asigna vida útil a una dilución.',
        administration='IM en tercio medio anterolateral del muslo. Reevaluar y repetir a los 5 min si persiste compromiso ABC. Antes de 5 min, este contrato ofrece orientación sin dosificación; la actuación urgente sigue la decisión médica individual.',
        limitations=[
            'Pauta seleccionada ERC 2025/WAO 2020; la banda RCUK de 100–150 microgramos para menores de 6 meses es una discrepancia explícita, no un mínimo ni una dosis que se promedie.',
            'El formulario comprueba el cálculo y el dispositivo declarado; no acredita exactitud física, peso plausible ni diagnóstico. Confirmar especialmente neonatos y prematuros, sin retrasar tratamiento necesario.',
            'No cubre reanimación al nacimiento, parada cardíaca, autoinyectores ni otras vías. La valoración de riesgos relativos no equivale a contraindicar adrenalina IM en anafilaxia.',
            'Tras dos dosis adecuadas y compromiso persistente, activar ayuda experta; puede continuar IM mientras se prepara una perfusión segura. No continuar IM automáticamente cuando la perfusión esté en marcha.',
        ])
    im['fields'] = im_fields
    im['available_result_kinds'] = ['calculation', 'decision_support']

    infusion_fields = shared('IV') + [
        field('age_years', 'Edad cronológica verificada (años; puede contener decimales)', 'number', minimum=0),
        field('weight_kg', 'Peso actual verificado (kg)', 'number', positive=True),
        field('persistent_compromise', 'Compromiso persistente tras dosis IM adecuadas', 'choice', options=['respiratory', 'circulatory', 'both']),
        field('prior_im_doses', 'Número real de dosis IM previas', 'number', minimum=2, integer=True),
        field('previous_im_dose_micrograms', 'Penúltima dosis IM administrada (microgramos)', 'number', positive=True, maximum=500),
        field('previous_im_dose_regimen', 'Pauta de la penúltima dosis IM', 'choice', options=IM_REGIMENS),
        field('minutes_since_previous_im', 'Minutos desde la penúltima dosis IM', 'number', minimum=0),
        field('last_im_dose_micrograms', 'Última dosis IM administrada (microgramos)', 'number', positive=True, maximum=500),
        field('last_im_dose_regimen', 'Pauta de la última dosis IM', 'choice', options=IM_REGIMENS),
        field('minutes_since_last_im', 'Minutos desde la última dosis IM', 'number', minimum=0),
        field('early_repeat_context', 'Decisión experta previa documentada; no acredita un intervalo de 5 min', 'choice', options=EARLY_REPEAT_CONTEXTS),
        field('initial_severity', 'Gravedad seleccionada por el experto: moderada 0,5; grave hipotensa/hipóxica 1 mL/kg/h',
              'choice', options=['moderate', 'severe_hypotensive_or_hypoxic']),
        field('expert_present', 'Profesional experimentado en vasopresores presente para iniciar y titular', expected=True),
        field('fluid_resuscitation_assessed', 'Reanimación con fluidos y respuesta evaluadas individualmente', expected=True),
        field('stock_concentration_mg_ml', 'Concentración del producto de partida (mg/mL)', 'number', expected=1),
        field('drug_amount_mg', 'Cantidad total de adrenalina de la preparación (mg)', 'number', expected=1),
        field('final_volume_ml', 'Volumen FINAL verificado de la preparación (mL)', 'number', expected=100),
        field('volume_basis', 'El volumen incluye el fármaco y corrige el sobrellenado', 'choice', options=['verified_final_volume'], expected='verified_final_volume'),
        field('concentration', 'Concentración FINAL de la perfusión (microgramos/mL)', 'number', expected=10),
        field('diluent', 'Diluyente de la pauta seleccionada', 'choice', options=['NaCl_0.9_percent'], expected='NaCl_0.9_percent'),
        field('product_compatibility_stability_verified', 'Producto, diluyente, recipiente, luz y plazo de uso de ESTA mezcla verificados', expected=True),
        field('preparation_age_min', 'Minutos transcurridos desde preparación', 'number', minimum=0),
        field('verified_use_limit_min', 'Límite total de uso verificado para el producto/sistema (min; no valor universal)', 'number', positive=True),
        field('immediate_use_and_asepsis_verified', 'Preparación para uso inmediato y condiciones asépticas verificadas', expected=True),
        field('pump_ready', 'Bomba disponible y capaz de administrar la velocidad calculada', expected=True),
        field('dedicated_primed_line_ready', 'Línea dedicada cebada y permeable, sin conexión compartida', expected=True),
        field('no_bp_cuff_on_infusion_arm', 'Manguito de presión en otro brazo', expected=True),
        field('continuous_ecg_spo2_ready', 'ECG y SpO2 continuos disponibles', expected=True),
        field('bp_interval_min', 'Intervalo real previsto entre mediciones de PA (min)', 'number', positive=True, maximum=5),
        field('extravasation_surveillance_ready', 'Inspección frecuente del acceso y respuesta a extravasación preparadas', expected=True),
        field('suspected_adrenaline_toxicity', 'Sospecha actual de toxicidad por adrenalina: hipertensión, arritmia u otros signos', expected=False),
    ]
    infusion = contract(
        INFUSION_ID, 'Anafilaxia refractaria — inicio experto de perfusión IV',
        'anaphylaxis', 'Adrenalina / anafilaxia', 'Adrenalina',
        'infection-respiratory.md', 'anaphylaxis',
        ['Refractory anaphylaxis', '1 mg made up to a final volume of 100 mL', '0.5--1 mL/kg/h'], [],
        model='reviewed_anaphylaxis_infusion', dose_unit='micrograms/min',
        reviewed_workflow='anaphylaxis', review_reference=REVIEW_REFERENCE,
        concentration={'value': 10, 'unit': 'micrograms/mL', 'role': 'final'},
        preparation='Adrenalina 1 mg (1 mL del producto de 1 mg/mL), hasta volumen FINAL de 100 mL con NaCl 0,9%: 10 microgramos/mL. Contabilizar fármaco y sobrellenado; no sumar 1 mL a un volumen nominal de 100 mL.',
        compatibility='Receta RCUK seleccionada, condicionada al producto y sistema reales. Línea dedicada; no inferir compatibilidad en Y ni sustituir automáticamente por glucosa 5%, 0,1 mg/mL o otra receta.',
        stability='Preparar para uso inmediato; verificar plazo y condiciones de la preparación concreta. No se asignan 24 h universales ni se equipara estabilidad fisicoquímica a seguridad microbiológica.',
        administration='Inicio IV mediante bomba: 0,5 mL/kg/h si moderada; 1 mL/kg/h si grave con hipotensión/hipoxia. Titulación experta al menor efecto necesario; monitorización continua y PA al menos cada 5 min. No es un bolo.',
        limitations=[
            'RCUK 2021, apartado 6.6, aplicable a adultos y niños; población/edad verificadas. La mayoría de edad de 18 años clasifica el formulario y no cambia la fórmula.',
            'Solo calcula el inicio seleccionado; no programa ni titula una bomba. 1 mL/kg/h es el extremo del inicio descrito, no un máximo universal de mantenimiento.',
            'Valora las dos últimas dosis IM, sus pautas y tiempos reales. No declara refractariedad por un contador aislado ni por lesiones cutáneas sin compromiso respiratorio/circulatorio.',
            'No cubre bolos IV, parada cardíaca, reanimación al nacimiento, vía IO ni otras concentraciones. No requiere seleccionar hospital; sí recursos, producto y competencia presentes.',
            'Reducir o detener y reevaluar ante efectos adversos importantes; vigilar extravasación. La selección de glucagón u otro vasopresor y la retirada quedan fuera de este cálculo inicial.',
        ])
    infusion['fields'] = infusion_fields
    infusion['available_result_kinds'] = ['calculation', 'decision_support']
    return [im, infusion]


def _decimal(value):
    if type(value) not in (int, float):
        raise ValueError('Se requiere un número, no texto ni booleano.')
    try:
        if not isfinite(value):
            raise ValueError('Se requiere un número finito.')
    except OverflowError as exc:
        raise ValueError('Número fuera del rango calculable.') from exc
    return Decimal(str(value))


def _schema_errors(row, inputs):
    if not isinstance(inputs, dict):
        return [('inputs', 'Los datos deben ser un objeto.')]
    errors = []
    keys = {f['key'] for f in row['fields']}
    if set(inputs) - keys:
        errors.append(('unsupported_inputs', 'Hay campos ajenos a esta pauta.'))
    for spec in row['fields']:
        key = spec['key']
        value = inputs.get(key)
        condition = spec.get('required_if')
        if condition and inputs.get(condition['key']) != condition['equals']:
            if value is not None:
                errors.append((key, 'Campo inactivo: eliminar el dato residual.'))
            continue
        kind = spec['kind']
        invalid = value is None
        if kind == 'number' and not invalid:
            try:
                number = _decimal(value)
                invalid = (spec.get('positive', False) and number <= 0
                           or 'minimum' in spec and number < Decimal(str(spec['minimum']))
                           or 'maximum' in spec and number > Decimal(str(spec['maximum']))
                           or 'exclusive_minimum' in spec and number <= Decimal(str(spec['exclusive_minimum']))
                           or 'exclusive_maximum' in spec and number >= Decimal(str(spec['exclusive_maximum']))
                           or spec.get('integer', False) and number != number.to_integral_value())
            except ValueError:
                invalid = True
        elif kind == 'boolean':
            invalid = type(value) is not bool
        elif kind == 'choice':
            invalid = not isinstance(value, str) or value not in spec['options']
        if 'expected' in spec:
            invalid = invalid or value != spec['expected']
        if invalid:
            errors.append((key, 'Falta o no es válido: ' + spec['label'] + '.'))
    return errors


def _im_dose_micrograms(weight):
    return min(weight * Decimal('10'), Decimal('500'))


def _previous_dose_valid(dose, regimen, age_months, weight):
    if regimen == 'erc_wao_weight_based':
        return dose == _im_dose_micrograms(weight)
    if age_months < 6:
        return Decimal('100') <= dose <= Decimal('150')
    expected = Decimal('150') if age_months < 72 else Decimal('300') if age_months <= 144 else Decimal('500')
    return dose == expected


def validation_errors(row, inputs):
    """Check individual facts, chronology, source selection and delivery units."""
    if row.get('id') not in (IM_ID, INFUSION_ID):
        return [('unsupported_contract', 'Contrato de anafilaxia no reconocido.')]
    errors = _schema_errors(row, inputs)
    if errors:
        return errors
    weight = _decimal(inputs['weight_kg'])
    if row['id'] == IM_ID:
        age_months = _decimal(inputs['age_months'])
        volume = _im_dose_micrograms(weight) / Decimal('1000')
        increment = _decimal(inputs['measurement_increment_ml'])
        minimum = _decimal(inputs['minimum_measurable_volume_ml'])
        capacity = _decimal(inputs['syringe_capacity_ml'])
        if minimum > capacity or increment > capacity:
            errors.append(('device_parameters', 'Los límites del dispositivo son incoherentes.'))
        if volume < minimum or volume > capacity:
            errors.append(('measurable_volume', 'El volumen calculado está fuera del intervalo de entrega verificado. No redondear ni diluir automáticamente.'))
        try:
            if volume % increment != 0:
                errors.append(('measurement_increment', 'El volumen exacto no es representable con el incremento declarado. Verificar un método de medida adecuado; no redondear automáticamente.'))
        except InvalidOperation:
            errors.append(('measurement_increment', 'La precisión declarada excede el rango calculable; revisar el dispositivo.'))
        if inputs['dose_phase'] == 'repeat':
            if not _previous_dose_valid(_decimal(inputs['last_im_dose_micrograms']), inputs['last_im_dose_regimen'], age_months, weight):
                errors.append(('prior_im_dose', 'La dosis IM previa no coincide con la pauta declarada para esta edad/peso. Reconciliar antes del cálculo de repetición.'))
            if inputs['prior_im_doses'] >= 2 and not inputs['refractory_escalation_active']:
                errors.append(('refractory_escalation', 'Tras dos dosis adecuadas y compromiso persistente, activar evaluación experta de anafilaxia refractaria. Puede mantenerse IM mientras se organiza una perfusión segura.'))
        return errors

    age_years = _decimal(inputs['age_years'])
    if (inputs['population'] == 'adult') != (age_years >= 18):
        errors.append(('population_age', 'Población y edad no coinciden: para este formulario, pediatría <18 años y adultos ≥18 años.'))
    age_months = age_years * 12
    for prefix in ('previous', 'last'):
        if not _previous_dose_valid(_decimal(inputs[prefix + '_im_dose_micrograms']), inputs[prefix + '_im_dose_regimen'], age_months, weight):
            errors.append((prefix + '_im_dose', 'La dosis IM ' + ('penúltima' if prefix == 'previous' else 'última') + ' no coincide con la pauta declarada para esta edad/peso.'))
    interval = _decimal(inputs['minutes_since_previous_im']) - _decimal(inputs['minutes_since_last_im'])
    if interval <= 0:
        errors.append(('im_chronology', 'La penúltima dosis debe preceder realmente a la última; comprobar los tiempos.'))
    computed_concentration = _decimal(inputs['drug_amount_mg']) * 1000 / _decimal(inputs['final_volume_ml'])
    if computed_concentration != _decimal(inputs['concentration']):
        errors.append(('final_concentration', 'Cantidad, volumen FINAL y concentración no concuerdan; riesgo de error entre mg y microgramos.'))
    if inputs['preparation_age_min'] >= inputs['verified_use_limit_min']:
        errors.append(('preparation_expired', 'Se ha alcanzado el límite de uso individual desde la preparación. No reiniciar el reloj al conectar.'))
    rate = Decimal('0.5') if inputs['initial_severity'] == 'moderate' else Decimal('1')
    try:
        for number in (weight * rate, weight * rate * 10 / 60, weight * rate * 10):
            if not isfinite(float(number)):
                raise ValueError
    except (ValueError, OverflowError):
        errors.append(('numeric_range', 'El resultado excede el rango numérico; revisar peso y unidades.'))
    return errors


def _timing_decision(infusion=False):
    return {
        'result_kind': 'decision_support',
        'decision_code': 'anaphylaxis_prior_im_interval_review' if infusion else 'anaphylaxis_early_repeat_review',
        'decision_support': ('Las dos dosis IM se administraron con menos de 5 min de separación; reconciliar su adecuación y evolución antes de usar este cálculo de perfusión.'
                             if infusion else 'Han transcurrido menos de 5 min desde la última dosis IM; este contrato no calcula una repetición anticipada.'),
        'dose': None, 'dose_unit': None, 'route': None, 'concentration': None, 'components': None,
        'withdrawal_ml': None, 'administration_volume_ml': None, 'pump_ml_h': None,
        'duration_min': None, 'amount_per_hour': None, 'amount_per_hour_unit': None,
        'maximum': None, 'preparation': None, 'compatibility': None, 'stability': None,
        'administration': 'Apoyo de decisión urgente, sin pauta numérica ni orden de administración.',
        'next_actions': [
            'Reevaluar ABC, respuesta, dosis y horas reales; el intervalo habitual de las pautas seleccionadas es 5 min.',
            'Mantener reanimación, apoyo experto y decisión médica individual sin esperar al formulario. La declaración de una excepción no sustituye la evidencia de este cálculo.',
            'Documentar cualquier actuación urgente individual y su motivo. No generar otra dosis ni una velocidad de bomba por una casilla de excepción.',
        ],
    }


def calculate(row, inputs):
    """Return an initial/repeat IM dose or an expert-selected initial IV rate."""
    errors = validation_errors(row, inputs)
    if errors:
        raise ValueError('Datos de anafilaxia inválidos: ' + '; '.join(code for code, _ in errors))
    if row['id'] == IM_ID and inputs['dose_phase'] == 'repeat' and inputs['elapsed_min'] < 5:
        return _timing_decision()
    if row['id'] == INFUSION_ID and _decimal(inputs['minutes_since_previous_im']) - _decimal(inputs['minutes_since_last_im']) < 5:
        return _timing_decision(infusion=True)
    weight = _decimal(inputs['weight_kg'])
    if row['id'] == IM_ID:
        micrograms = _im_dose_micrograms(weight)
        volume = micrograms / 1000
        actions = ['Reevaluar ABC y respuesta; registrar dosis y hora reales. No generar repeticiones automáticas.']
        if inputs.get('prior_im_doses', 0) >= 2:
            actions.append('Escalada por posible anafilaxia refractaria activa; continuar IM solo mientras persista la indicación y la perfusión aún no esté en marcha.')
        if inputs['age_months'] < 1:
            actions.append('Neonato: confirmar diagnóstico y evaluación individual; solicitar ayuda pediátrica/neonatal sin retrasar el tratamiento necesario.')
        return {
            'dose': float(micrograms), 'dose_unit': 'micrograms',
            'concentration': {'value': 1, 'unit': 'mg/mL', 'role': 'undiluted IM product'},
            'withdrawal_ml': float(volume), 'administration_volume_ml': float(volume),
            'pump_ml_h': None, 'duration_min': None,
            'components': {'weight_kg': float(weight), 'coefficient_micrograms_kg': 10,
                           'dose_mg': float(micrograms / 1000), 'dose_micrograms': float(micrograms),
                           'volume_ml': float(volume), 'minimum_dose_applied': False, 'automatic_rounding_applied': False},
            'next_actions': actions,
        }

    rate = Decimal('0.5') if inputs['initial_severity'] == 'moderate' else Decimal('1')
    pump = weight * rate
    per_hour = pump * 10
    per_min = per_hour / 60
    return {
        'dose': float(per_min), 'dose_unit': 'micrograms/min',
        'concentration': {'value': 10, 'unit': 'micrograms/mL', 'role': 'final'},
        'withdrawal_ml': 1, 'administration_volume_ml': None, 'pump_ml_h': float(pump),
        'duration_min': None, 'amount_per_hour': float(per_hour), 'amount_per_hour_unit': 'micrograms/h',
        'components': {'weight_kg': float(weight), 'initial_rate_ml_kg_h': float(rate),
                       'dose_micrograms_kg_min': float(rate * 10 / 60), 'dose_micrograms_min': float(per_min),
                       'dose_micrograms_h': float(per_hour), 'drug_amount_mg': 1, 'final_volume_ml': 100,
                       'stock_withdrawal_ml': 1, 'diluent': 'NaCl 0.9%',
                       'remaining_verified_use_min': float(_decimal(inputs['verified_use_limit_min']) - _decimal(inputs['preparation_age_min']))},
        'next_actions': [
            'Verificar que la bomba y el acceso entregan esta velocidad; iniciar bajo supervisión experta con ECG/SpO2 continuos y PA al menos cada 5 min.',
            'Titular individualmente al menor efecto necesario. El equilibrio tras un cambio puede tardar 5–10 min; este cálculo no propone escalones ni un máximo universal.',
            'Vigilar hipertensión, arritmia y extravasación; reducir o detener y reevaluar si aparecen efectos adversos importantes.',
            'No seguir administrando IM automáticamente cuando la perfusión funcione. Si aún no es posible una perfusión segura, mantener la atención y la pauta IM indicadas con ayuda experta.',
        ],
    }
