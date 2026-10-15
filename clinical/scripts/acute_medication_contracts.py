"""Reviewed, source-bound acute medication contracts. No frontend dosing rules."""


def field(key, label, kind='boolean', **rules):
    return {'key': key, 'label': label, 'kind': kind, **rules}


def common(route='IV', population='adult'):
    return [
        field('population', 'Población', 'choice', options=['adult', 'pediatric'], expected=population),
        field('route', 'Vía', 'choice', options=['IV', 'IM', 'SC', 'PO'], expected=route),
        field('indication_confirmed', 'Indicación y fase confirmadas por el profesional', expected=True),
        field('allergy_contraindication_present', 'Alergia o contraindicación para esta opción', expected=False),
        field('interaction_reviewed', 'Interacciones, función renal/hepática y embarazo revisados', expected=True),
        field('monitoring_ready', 'Monitorización y medios de rescate disponibles', expected=True),
        field('local_protocol_verified', 'Protocolo local y contexto de uso verificados', expected=True),
    ]


AMIODARONE = [
    {'id': 'amiodarone-arrest-third', 'label': 'FV/TV sin pulso — después de tres descargas',
     'module': 'adult-cardiac-arrest', 'dose': 300,
     'anchors': ['300 mg IV after a total of three shocks'],
     'fields': [field('shock_count', 'Número de descargas completadas', 'number', expected=3)],
     'administration': '300 mg IV después de un total de tres descargas; seguir ALS y continuar RCP.'},
    {'id': 'amiodarone-arrest-fifth', 'label': 'FV/TV sin pulso — dosis adicional después de cinco descargas',
     'module': 'adult-cardiac-arrest', 'dose': 150,
     'anchors': ['a further 150 mg IV after a total of five shocks'],
     'fields': [field('shock_count', 'Número de descargas completadas', 'number', expected=5),
                field('prior_300mg_given', 'Dosis previa de 300 mg de este algoritmo confirmada', expected=True)],
     'administration': '150 mg IV adicionales después de un total de cinco descargas; continuar ALS.'},
    {'id': 'amiodarone-failed-cardioversion', 'label': 'Con pulso — cardioversión fallida e inestabilidad persistente',
     'module': 'adult-arrhythmias', 'dose': 300,
     'anchors': ['amiodarone 300 mg IV over 10--20 min'],
     'fields': [field('failed_cardioversion_unstable', 'Cardioversión fallida con inestabilidad persistente', expected=True),
                field('duration_min', 'Duración seleccionada (min)', 'number', minimum=10, maximum=20)],
     'administration': '300 mg IV en 10–20 min según protocolo local; volver a intentar cardioversión.'},
    {'id': 'amiodarone-maintenance', 'label': 'Mantenimiento asociado a la carga del circuito de cardioversión',
     'module': 'adult-arrhythmias', 'dose': 900,
     'anchors': ['amiodarone may be followed by 900 mg over 24 h'],
     'fields': [field('loading_pathway_confirmed', 'Carga previa y continuación de este circuito confirmadas', expected=True)],
     'duration_min': 1440,
     'administration': '900 mg durante 24 h en el contexto de continuación descrito; no aplicar a otra indicación.'},
]


def regimens():
    rows = []
    for item in AMIODARONE:
        rows.append({
            **item, 'group': 'amiodarone', 'group_label': 'Amiodarona', 'drug': 'Amiodarona',
            'route': 'IV', 'dose_unit': 'mg', 'model': 'fixed',
            'bundle': 'cardiovascular.md', 'concentration': {'value': 50, 'unit': 'mg/mL', 'role': 'stock'},
            'localization_drug': 'amiodarone',
            'product_anchor': '50 mg/mL; ampoule 3 mL',
            'fields': common() + [field('concentration', 'Concentración del producto (mg/mL; no dilución final)', 'number', expected=50, positive=True),
                                  field('product_verified', 'Presentación exacta y concentración del producto comprobadas', expected=True)] + item['fields'],
            'preparation': None, 'compatibility': None, 'stability': None, 'maximum': None,
            'limitations': ['Diluyente, concentración final, estabilidad y acceso local no especificados en el registro.',
                            'mL extraídos del producto no equivalen a mL de administración ni a mL/h de bomba.',
                            'No hay pauta independiente de FA estable ni de 600 mg/24 h en este contrato.'],
        })
    return rows + insulin_regimens() + sodium_regimens() + status_regimens() + anaphylaxis_regimens() + reversal_regimens()


def contract(rid, label, group, group_label, drug, bundle, module, anchors, fields,
             route='IV', population='adult', **values):
    """Absent clinical values remain absent; callers supply all numeric rules."""
    return {'id': rid, 'label': label, 'group': group, 'group_label': group_label,
            'drug': drug, 'bundle': bundle, 'module': module, 'anchors': anchors,
            'route': route, 'fields': common(route, population) + fields,
            'model': 'fixed', 'dose': None, 'dose_unit': None, 'concentration': None,
            'preparation': None, 'compatibility': None, 'stability': None, 'maximum': None,
            'administration': '', 'limitations': ['Revisión clínica y conciliación local pendientes.'], **values}


def insulin_regimens():
    rows = []
    for suffix, label, key, extra in [
        ('dka', 'DKA — fase inicial', 'dka_or_mixed_initial', [field('dka_or_mixed_confirmed', 'DKA confirmada; no HHS aislado', expected=True), field('glucose_mg_dl', 'Glucosa (mg/dL)', 'number', minimum=250)]),
        ('mixed', 'DKA/HHS mixto — fase inicial', 'dka_or_mixed_initial', [field('dka_or_mixed_confirmed', 'DKA/HHS mixto confirmado', expected=True), field('glucose_mg_dl', 'Glucosa (mg/dL)', 'number', minimum=250)]),
        ('dextrose', 'DKA — glucosa inferior a 250 mg/dL / euglucémica', 'dka_after_glucose_below_250', [field('dka_or_mixed_confirmed', 'DKA o DKA/HHS mixto confirmado', expected=True), field('glucose_mg_dl', 'Glucosa (mg/dL)', 'number', positive=True, exclusive_maximum=250), field('dextrose_started', 'Dextrosa 5–10% y plan de continuación hasta resolución establecidos', expected=True)]),
        ('hhs', 'HHS sin cetosis/acidosis significativa', 'hhs_without_significant_ketosis', [field('hhs_without_ketosis_acidosis', 'HHS confirmado sin cetosis/acidosis significativa', expected=True), field('fluid_osmolality_plan', 'Fluidos iniciales y control seriado de osmolalidad establecidos', expected=True), field('glucose_mg_dl', 'Glucosa actual (mg/dL)', 'number', positive=True)]),
    ]:
        rows.append(contract('insulin-' + suffix, label, 'insulin', 'Insulina / DKA', 'Insulina soluble/regular',
            'renal-metabolic.md', 'diabetic-ketoacidosis-hhs',
            ['0.1 units/kg/h', '0.05 units/kg/h', '100 units in a final volume of 100 mL', 'potassium is above 3.5 mmol/L'],
            [field('weight_kg', 'Peso verificado (kg)', 'number', positive=True),
             field('potassium_mmol_l', 'Potasio previo a insulina (mmol/L)', 'number', exclusive_minimum=3.5),
             field('concentration', 'Concentración final verificada (units/mL)', 'number', expected=1),
             field('preparation_verified', '100 unidades en volumen FINAL de 100 mL de NaCl 0,9%; producto y cebado local verificados', expected=True)] + extra,
            model='insulin', insulin_key=key, dose_unit='units/h',
            concentration={'value': 1, 'unit': 'units/mL', 'role': 'final'},
            preparation='Insulina soluble/regular: 100 unidades en volumen FINAL de 100 mL de NaCl 0,9%; 1 unidad/mL. Cebado según protocolo local.',
            administration='Perfusión IV continua mediante bomba. No es un bolo. Vigilar glucosa, potasio, cetonas, pH, fluidos y osmolalidad según el módulo completo.',
            limitations=['K = 3,5 mmol/L se bloquea conservadoramente: la fuente exige superar 3,5 para iniciar/reanudar; requiere revisión profesional.',
                         'No calcula reposición de potasio ni dosis subcutánea de transición. No suspender por normalización aislada de glucosa.',
                         'Diagnóstico y fase requieren confirmación profesional; no se diagnostican automáticamente con estos campos.']))
    return rows


def sodium_regimens():
    product = [field('concentration', 'Concentración de NaCl (%)', 'number', expected=3),
               field('product_verified', 'Producto NaCl 3% verificado', expected=True)]
    metadata = {'dose_unit': 'mL', 'concentration': {'value': 3, 'unit': '%', 'role': 'ready-to-use'},
                'preparation': 'Producto NaCl 3% verificado; no se calcula preparación desde concentrados.',
                'limitations': ['Bolo con duración finita; no convertir en perfusión continua.',
                                'No predice el cambio de sodio ni autoriza repeticiones automáticas.']}
    return [
        contract('sodium-hyponatremia', 'Hiponatremia con síntomas neurológicos atribuibles',
            'sodium', 'NaCl 3%', 'Cloruro sódico 3%', 'renal-metabolic.md', 'sodium-emergencies',
            ['150 mL sodium chloride 3% IV over 20 min', '10 mmol/L in the first 24 hours', '8 mmol/L in each subsequent 24 hours'],
            product + [field('symptoms_attributable', 'Síntomas neurológicos moderados/graves atribuibles a hiponatremia confirmados', expected=True),
                field('sodium_start_mmol_l', 'Na al inicio de la ventana de corrección (mmol/L)', 'number', positive=True),
                field('sodium_current_mmol_l', 'Na actual (mmol/L)', 'number', positive=True),
                field('correction_window', 'Ventana de corrección', 'choice', options=['first24', 'subsequent24']),
                field('high_ods_risk', 'Riesgo alto de desmielinización osmótica'),
                field('initial_response_reached', 'Ya hubo mejoría clínica o ascenso inicial aproximado de 5 mmol/L', expected=False),
                field('reassessment_ready', 'Reevaluación de síntomas, Na, diuresis y plan de parada/relowering preparados', expected=True)],
            model='volume', dose=150, duration_min=20, sodium_correction=True,
            administration='Bolo de 150 mL IV en 20 min. Reevaluar síntomas y Na; detener bolos rutinarios tras respuesta inicial. Límite acumulado no es objetivo de tratamiento.', **metadata),
        contract('sodium-icp', 'Herniación clínica / crisis de presión intracraneal adulta',
            'sodium', 'NaCl 3%', 'Cloruro sódico 3%', 'neurologic.md', 'traumatic-intracranial-mass-effect',
            ['3% sodium chloride 5 mL/kg IV over 5--20 minutes'],
            product + [field('weight_kg', 'Peso verificado (kg)', 'number', positive=True),
                field('duration_min', 'Duración del bolo (min)', 'number', minimum=5, maximum=20),
                field('herniation_icp_confirmed', 'Herniación clínica / crisis ICP confirmada por el profesional', expected=True),
                field('neurocritical_stop_plan', 'Plan neurocrítico local de límites, reevaluación y repetición verificado', expected=True)],
            model='weight_volume', dose=5,
            administration='Bolo IV 5 mL/kg en 5–20 min; reevaluación neurológica/pupilar inmediata, Na/Cl, función renal y estado hídrico. No pauta continua.', **metadata),
    ]


def status_regimens():
    rows = []
    for key, drug, coefficient, cap, unit, route, anchor, extra in [
        ('lorazepam', 'Lorazepam', .1, 4, 'mg', 'IV', '0.1 mg/kg IV (max 4 mg)', []),
        ('diazepam', 'Diazepam', None, 10, 'mg', 'IV', '0.15--0.2 mg/kg IV (max 10 mg)', [field('dose_mg_kg', 'Dosis elegida según protocolo (mg/kg)', 'number', minimum=.15, maximum=.2)]),
        ('midazolam', 'Midazolam', .2, 10, 'mg', 'IM', '0.2 mg/kg (max 10 mg when >40 kg)', [field('no_iv_access', 'No hay acceso IV; opción IM seleccionada', expected=True)]),
        ('levetiracetam', 'Levetiracetam', 60, 4500, 'mg', 'IV', '60 mg/kg IV, max 4,500 mg', []),
        ('fosphenytoin', 'Fosfenitoína', 20, 1500, 'mg PE', 'IV', '20 mg PE/kg IV, max 1,500 mg PE', [field('conduction_disease', 'Enfermedad de conducción/bloqueo AV u otra contraindicación cardíaca', expected=False)]),
        ('valproate', 'Valproato sódico', 40, 3000, 'mg', 'IV', '40 mg/kg IV, max 3,000 mg', [field('hepatic_disease', 'Enfermedad hepática significativa', expected=False), field('pregnancy_childbearing_risk', 'Embarazo o potencial gestacional que requiere decisión especializada', expected=False)]),
    ]:
        first = key in ('lorazepam', 'diazepam', 'midazolam')
        stage = [field('prior_bzd_doses', 'Dosis previas de benzodiacepina documentadas (0 o 1)', 'number', minimum=0, maximum=1, integer=True)] if first else [field('adequate_bzd_failed', 'Persistencia tras benzodiacepina adecuada confirmada', expected=True)]
        rows.append(contract('status-' + key, ('Primera línea — ' if first else 'Segunda línea — ') + drug,
            'status', 'Status epiléptico', drug, 'neurologic.md', 'status-epilepticus', [anchor],
            [field('weight_kg', 'Peso verificado (kg)', 'number', positive=True, **({'exclusive_minimum': 40} if key == 'midazolam' else {})),
             field('convulsive_status_confirmed', 'Status convulsivo confirmado; causas específicas evaluadas', expected=True),
             field('airway_rescue_ready', 'Soporte respiratorio/rescate preparado', expected=True),
             field('one_option_selected', 'Una sola alternativa elegida para esta fase', expected=True)] + stage + extra,
            route=route, model='weight', dose=coefficient, coefficient_field='dose_mg_kg' if coefficient is None else None,
            maximum={'value': cap, 'unit': unit}, dose_unit=unit,
            administration='Dosis de esta alternativa y fase; no sumar alternativas automáticamente. Ver secuencia, reevaluación y escalada en la fuente completa.',
            limitations=['Presentación, dilución, velocidad, compatibilidad y estabilidad no especificadas: no se generan mL ni mL/h.',
                         'PE significa equivalentes de fenitoína; no convertir a mg de otra formulación.',
                         'Repetición/escalada requieren reevaluación clínica; no hay programación automática.']))
    for key, label, reason in [
        ('refractory', 'Refractario tras segunda línea — UCI/EEG', 'Escalar a UCI/neurología, vía aérea y EEG continuo; pauta anestésica requiere protocolo especializado.'),
        ('phenytoin-local', 'Fenitoína cuando no hay fosfenitoína', 'La fuente exige carga local monitorizada; no hay pauta de producto/velocidad local verificada. No sustituir mg PE automáticamente.'),
    ]:
        rows.append(contract('status-' + key, label, 'status', 'Status epiléptico', label,
            'neurologic.md', 'status-epilepticus', ['second-line'], [], block_reason=reason,
            limitations=[reason], administration=reason))
    return rows


def anaphylaxis_regimens():
    rows = []
    for key, label, dose, age in [
        ('adult', 'Adulto', 500, []),
        ('over12', 'Pediatría mayor de 12 años', 500, [field('age_months', 'Edad verificada (meses)', 'number', exclusive_minimum=144), field('small_prepubertal', 'Paciente pequeño o prepuberal', expected=False)]),
        ('6to12', 'Pediatría de 6 a 12 años', 300, [field('age_months', 'Edad verificada (meses)', 'number', minimum=72, maximum=144)]),
        ('6monthsto6', 'Pediatría de 6 meses a menos de 6 años', 150, [field('age_months', 'Edad verificada (meses)', 'number', minimum=6, exclusive_maximum=72)]),
    ]:
        rows.append(contract('anaphylaxis-' + key, label + ' — adrenalina IM', 'anaphylaxis', 'Anafilaxia',
            'Adrenalina', 'infection-respiratory.md', 'anaphylaxis', ['1 mg/mL (1:1000)', '500 micrograms IM (0.5 mL)', '5 min'],
            [field('concentration', 'Concentración del producto (mg/mL)', 'number', expected=1),
             field('product_verified', 'Producto adrenalina IM 1 mg/mL verificado', expected=True),
             field('abc_compromise', 'Problemas de vía aérea, respiración o circulación por anafilaxia persistentes', expected=True),
             field('prior_im_doses', 'Dosis IM adecuadas ya administradas', 'number', minimum=0, maximum=1, integer=True),
             field('elapsed_min', 'Minutos desde la dosis IM previa (0 si ninguna)', 'number', minimum=0),
             field('small_volume_checked', 'Volumen, vía IM y técnica comprobados independientemente', expected=True)] + age,
            route='IM', population='adult' if key == 'adult' else 'pediatric', model='adrenaline_im', dose=dose, dose_unit='micrograms',
            concentration={'value': 1, 'unit': 'mg/mL', 'role': 'IM product'},
            preparation='Adrenalina 1 mg/mL (1:1000) para inyección IM; no es preparación IV.',
            administration='IM; reevaluar ABC y constantes. Repetir después de 5 min si persiste compromiso. Tras dos dosis adecuadas, activar vía refractaria experta.',
            limitations=['No sustituye la activación urgente ni la evaluación de respuesta.',
                         'Mayores de 12 años pequeños/prepuberales: fuente primaria incluye excepción no transcrita en el módulo; bloquear y revisar, sin introducir una pauta nueva.',
                         'Menores de 6 meses: la fuente ofrece un intervalo sin regla individual de selección; usar rama de revisión.']))
    for key, label, reason in [
        ('under6months', 'Menor de 6 meses — revisión de selección', 'La fuente almacena 100–150 microgramos; falta regla individual verificada. Requiere decisión pediátrica, sin dosis automática.'),
        ('refractory', 'Refractaria tras dos dosis IM adecuadas', 'Activar soporte experto, monitorización y protocolo de perfusión IV. No hay preparación/velocidad IV local verificada; evitar bolos IV no monitorizados.'),
    ]:
        rows.append(contract('anaphylaxis-' + key, label, 'anaphylaxis', 'Anafilaxia', 'Adrenalina',
            'infection-respiratory.md', 'anaphylaxis', ['Refractory anaphylaxis'], [],
            block_reason=reason, limitations=[reason], administration=reason))
    return rows


def reversal_regimens():
    rows = []
    agents = ['dabigatran', 'apixaban', 'rivaroxaban', 'ufh', 'enoxaparin', 'edoxaban', 'fondaparinux', 'other', 'unknown']
    def add(key, label, drug, agent, anchors, extra, **values):
        rows.append(contract('reversal-' + key, label, 'reversal', 'Reversión / antídotos', drug,
            'procedures-pharmacology.md', 'anticoagulation-reversal', anchors,
            [field('anticoagulant', 'Anticoagulante causal exacto', 'choice', options=agents, expected=agent),
             field('exact_agent_confirmed', 'Agente, indicación y dosis previas confirmados', expected=True),
             field('last_dose_hours', 'Horas desde última dosis conocida', 'number', minimum=0),
             field('life_threatening_uncontrolled_bleeding', 'Hemorragia vital/no controlada confirmada', expected=True),
             field('renal_hepatic_tests_reviewed', 'Función renal/hepática y pruebas específicas revisadas', expected=True),
             field('product_verified', 'Producto exacto y disponibilidad verificados; riesgo trombótico revisado', expected=True)] + extra,
            limitations=['No extrapolar a otro anticoagulante ni a hemorragia menor.',
                         'Preparación, volumen, velocidad de bomba y conciliación de producto local no documentados en este contrato.',
                         'Control de foco, reevaluación y reinicio antitrombótico requieren decisión profesional.'], **values))
    add('dabigatran', 'Dabigatrán — idarucizumab', 'Idarucizumab', 'dabigatran', ['idarucizumab 5 g IV', '2 × 2.5 g consecutivos'],
        [field('reversal_indication', 'Indicación de reversión', 'choice', options=['major_bleeding', 'urgent_surgery'])],
        dose=5, dose_unit='g', administration='5 g IV como dos dosis consecutivas de 2,5 g. Reevaluar por rebote; segunda dosis no rutinaria.',
        components={'consecutive_doses': 2, 'each_g': 2.5})
    # Urgent surgery is an independent labelled indication; no false bleeding requirement.
    rows[-1]['fields'] = [f for f in rows[-1]['fields'] if f['key'] != 'life_threatening_uncontrolled_bleeding']
    for agent, threshold in [('apixaban', 5), ('rivaroxaban', 10)]:
        add(agent, agent.capitalize() + ' — andexanet alfa', 'Andexanet alfa', agent,
            ['400 mg IV', '800 mg IV', '4 mg/min durante 120 min', '8 mg/min durante 120 min', 'Si dosis o intervalo son desconocidos'],
            [field('last_dose_mg', 'Última dosis del anticoagulante (mg)', 'number', positive=True)],
            model='andexanet', threshold_mg=threshold, dose_unit='mg',
            administration='Dosis mostrada = bolo IV; después perfusión de 120 min según los componentes. No convertir a mL sin producto/concentración verificados. Dosis/hora desconocidas: consultar hematología/farmacia.')
    add('ufh', 'UFH reciente — referencia de protamina', 'Protamina', 'ufh',
        ['1 mg de protamina por cada 100 U de UFH', '50 mg', '≤5 mg/min'],
        [field('recent_ufh_units', 'UFH administrada en la ventana reciente (U)', 'number', positive=True),
         field('recent_window_hours', 'Ventana reciente documentada (horas)', 'number', minimum=2, maximum=3),
         field('time_adjustment_reviewed', 'Ajuste por tiempo y pauta final revisados según protocolo local', expected=True)],
        model='ufh', dose_unit='mg', maximum={'value': 50, 'unit': 'mg'},
        administration='Referencia aritmética de 1 mg por 100 U recientes, máximo habitual 50 mg; ajustar por tiempo transcurrido. IV lenta ≤5 mg/min; vigilar hipotensión/anafilaxia y aPTT/ACT.')
    next(f for f in rows[-1]['fields'] if f['key'] == 'last_dose_hours')['maximum'] = 3
    for suffix, label, coefficient, time_rules, extra in [
        ('early', 'Menos de 8 horas', 1, {'exclusive_maximum': 8}, []),
        ('late', 'De 8 a 12 horas', .5, {'minimum': 8, 'maximum': 12}, []),
        ('repeat', 'Segunda dosis condicionada', .5, {}, [field('prior_protamine_given', 'Primera dosis de protamina documentada', expected=True), field('persistent_activity', 'Persisten sangrado/actividad y se confirmó indicación especializada', expected=True)]),
    ]:
        add('enoxaparin-' + suffix, 'Enoxaparina — ' + label, 'Protamina', 'enoxaparin',
            ['1 mg protamina por 1 mg enoxaparina', '0.5 mg protamina por 1 mg enoxaparina'],
            [field('enoxaparin_mg', 'Dosis causal de enoxaparina (mg; no unidades anti-Xa)', 'number', positive=True)] + extra,
            model='enoxaparin', dose=coefficient, dose_unit='mg',
            administration='Reversión parcial, no neutralización completa. Reevaluar sangrado, función renal y actividad anti-Xa; producto, máximo y velocidad según protocolo verificado.')
        next(f for f in rows[-1]['fields'] if f['key'] == 'last_dose_hours').update(time_rules)
    blocked = [
        ('vka-pcc', 'VKA — vitamina K / 4F-PCC', 'Requiere INR, peso y tabla exacta del PCC local. No aplicar automáticamente a sangrado menor o INR aislado; no se ha verificado tabla de producto.'),
        ('superwarfarin', 'Superwarfarinas', 'Vitamina K prolongada y seguimiento INR requieren toxicología/hematología; no hay pauta individual verificada.'),
        ('edoxaban', 'Edoxabán', 'No extrapolar indicación EMA de andexanet; PCC inespecífico exige selección/dosis de protocolo experto.'),
        ('betrixaban', 'Betrixabán', 'Verificar regulación y protocolo experto; no extrapolar andexanet.'),
        ('fondaparinux', 'Fondaparinux', 'Sin antídoto específico aprobado en la fuente; protamina no neutraliza. Soporte/control de foco y consulta experta.'),
        ('other-lmwh', 'Otras HBPM', 'Reversión parcial según ficha exacta; no convertir unidades entre HBPM.'),
        ('enoxaparin-over12', 'Enoxaparina después de 12 horas', 'Necesidad individual según actividad persistente/función renal; no hay dosis universal.'),
        ('argatroban', 'Argatrobán', 'Sin antídoto específico; suspender, soporte, control de foco y valoración de función hepática.'),
        ('bivalirudin', 'Bivalirudina', 'Sin antídoto específico; suspender, soporte, control de foco y valoración renal.'),
        ('other-dti', 'Otras trombinas directas parenterales', 'Sin pauta universal de antídoto; manejo experto por producto y función renal.'),
        ('danaparoid', 'Danaparoide / heparinoides', 'No reversión fiable con protamina; soporte y hematología, sin pauta universal.'),
        ('fibrinolytics', 'Trombolíticos / fibrinolíticos', 'Suspender; control urgente de fibrinógeno y coagulación, neuroimagen si ICH; crioprecipitado/fibrinógeno según protocolo.'),
        ('antiplatelets', 'Antiagregantes', 'No hay antídoto universal; decisiones según sangrado/procedimiento. No transfusión plaquetaria automática.'),
        ('unknown', 'Agente, dosis o tiempo desconocidos', 'Identificar agente, última dosis, pruebas y función orgánica. No elegir antídoto a ciegas.'),
        ('dabigatran-repeat', 'Repetición de idarucizumab', 'No rutinaria: requiere criterios específicos del producto y hematología; no se automatiza.'),
    ]
    for key, label, reason in blocked:
        rows.append(contract('reversal-' + key, label, 'reversal', 'Reversión / antídotos', label,
            'procedures-pharmacology.md', 'anticoagulation-reversal', ['Identificar'], [],
            block_reason=reason, limitations=[reason], administration=reason))
    return rows
