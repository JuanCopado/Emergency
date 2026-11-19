import { useClinicalUi } from '../i18n/useClinicalUi';
import { useFormat } from '../lib/useFormat';
import { formatCanonicalNumber } from '../lib/format';
import { MAX_PATIENT_WEIGHT_KG, MIN_PATIENT_WEIGHT_KG, parsePatientWeight } from '../lib/patientWeight';
import PediatricExport from '../pediatrics/PediatricExport';
import { useEffect, useRef, useState, type FormEvent } from 'react';
import { useSearchParams } from 'react-router-dom';
import { calculatePediatric, findRegimen, numericInput, pediatricCatalog, regimensForDrug,
  type Calculation, type Fields, type Gate, type Regimen, type Value } from '../pediatrics/catalog';

const labels: Record<string, string> = {
  age_months: 'Edad (meses)', actual_weight_kg: 'Peso real (kg)', ideal_weight_kg: 'Peso ideal (kg)',
  adjusted_weight_kg: 'Peso ajustado (kg)', egfr_mL_min: 'Filtrado renal (mL/min)',
  dose_mg: 'Dosis por toma (mg)', dose_mg_per_kg: 'Dosis (mg/kg)', dose_mg_per_kg_range: 'Rango de dosis (mg/kg)',
  max_mg_per_dose: 'Máximo por toma (mg)', adult_max_daily_mg: 'Máximo diario adulto (mg)',
  daily_max_mg_per_kg: 'Máximo diario (mg/kg)', frequency: 'Frecuencia', duration_days: 'Duración (días)',
  doses_per_day: 'Tomas por día', total_doses: 'Número total de tomas', route: 'Vía',
  dosing_weight_kg: 'Peso utilizado (kg)', weight_basis: 'Base de peso', administration: 'Administración / alimentos',
  contraindications: 'Contraindicaciones', cautions: 'Precauciones', min_age_months: 'Edad mínima (meses)',
  max_age_months: 'Edad máxima (meses)', verified_concentrations: 'Presentaciones verificadas',
  mg_per_ml: 'mg/mL', label: 'Presentación', product_strength: 'Concentración / presentación',
  volume_per_dose: 'Volumen por toma', exact_ml: 'Volumen exacto (mL)', rounded_0_1_ml: 'Volumen redondeado (mL)',
  concentration_mg_per_ml: 'Concentración (mg/mL)', estimated_total_course_ml: 'Volumen total del curso (mL)',
  renal_adjustment: 'Función renal', hepatic_adjustment: 'Función hepática', source: 'Fuente',
  bands: 'Bandas de edad/peso y pauta', schedule: 'Pauta por fases', topical_instructions: 'Instrucciones tópicas',
  device: 'Dispositivo', matched_band: 'Banda aplicable', dosing_instructions: 'Instrucciones',
  required_patient_flags: 'Criterios clínicos necesarios', excluded_patient_flags: 'Exclusiones clínicas',
  minimum_patient_values: 'Valores mínimos requeridos', maximum_patient_values: 'Valores máximos permitidos',
  known_renal_impairment: 'Insuficiencia renal conocida', known_hepatic_impairment: 'Insuficiencia hepática conocida',
};
const label = (key: string) => labels[key] || key.replaceAll('_', ' ');
const patientWeightFields = new Set(['actual_weight_kg', 'ideal_weight_kg', 'adjusted_weight_kg']);
const omitted = new Set(['id', 'drug_id', 'drug', 'diagnosis', 'dose_model', 'liquid_capable', 'source_url',
  'medication_safety', 'prescription_status', 'status', 'regimen_id']);

function Details({ value }: { value: Value }) {
  const ui = useClinicalUi();
  const f = useFormat();
  if (typeof value === 'number') return <span>{formatCanonicalNumber(value, f.locale)}</span>;
  if (value == null) return <span>{ui("No consta en la fuente")}</span>;
  if (Array.isArray(value)) return <ul className="space-y-1">{value.map((v, i) => <li key={i}><Details value={v} /></li>)}</ul>;
  if (typeof value === 'object') return <dl className="space-y-2">{Object.entries(value).filter(([k]) => !omitted.has(k)).map(([k, v]) =>
    <div key={k}><dt className="font-semibold">{ui(label(k))}</dt><dd className="ml-3"><Details value={v} /></dd></div>)}</dl>;
  return <span>{typeof value === 'boolean' ? (value ? ui("Sí") : ui("No")) : String(value)}</span>;
}

// Reorder presentation only; every returned value retains its original units and precision.
function ResultDetails({ value }: { value: Fields }) {
  const ui = useClinicalUi();
  const primaryKeys = ['dose_mg', 'volume_per_dose', 'dosing_weight_kg', 'weight_basis',
    'concentration_mg_per_ml', 'frequency', 'max_mg_per_dose', 'adult_max_daily_mg',
    'daily_max_mg_per_kg', 'duration_days', 'estimated_total_course_ml'];
  const primary = primaryKeys.filter(key => Object.hasOwn(value, key));
  const remaining = Object.fromEntries(Object.entries(value).filter(([key]) => !primary.includes(key)));
  return <>
    <dl className="grid gap-3 sm:grid-cols-2" aria-label={ui("Cálculo y pauta")}>
      {primary.map(key => <div className="rounded-xl border border-primary/30 bg-surface-2 p-3" key={key}>
        <dt className="font-bold">{ui(label(key))}</dt><dd className="mt-1 text-lg"><Details value={value[key] ?? null} /></dd>
      </div>)}
    </dl>
    <div className="border-t border-border pt-3"><h3 className="mb-2 font-bold">{ui("Detalle, precauciones y fuente")}</h3><Details value={remaining} /></div>
  </>;
}

function RegimenForm({ regimen }: { regimen: Regimen }) {
  const ui = useClinicalUi();
  const [values, setValues] = useState<Record<string, string>>({});
  const [response, setResponse] = useState<Calculation>();
  const [calculation, setCalculation] = useState<Fields>();
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const resultRef = useRef<HTMLElement>(null);
  useEffect(() => {
    if (response) {
      resultRef.current?.focus({ preventScroll: true });
      resultRef.current?.scrollIntoView?.({ block: 'start' });
    }
  }, [response]);
  const revision = useRef(0);
  const change = (field: string, value: string) => {
    revision.current += 1;
    setValues((old) => ({ ...old, [field]: value }));
    setResponse(undefined); setError(''); setBusy(false);
  };
  const gates: Gate[] = [...(regimen.required_patient_flags || []), ...(regimen.excluded_patient_flags || []),
    ...pediatricCatalog.condition_rules.filter((r) => !r.drug || r.drug === regimen.drug),
    { field: 'known_renal_impairment' }, { field: 'known_hepatic_impairment' }];
  const flags = [...new Map(gates.map((g) => [g.field, g])).values()];
  const numericFields = [...new Set(['age_months', 'actual_weight_kg',
    ...(regimen.weight_basis === 'ideal' ? ['ideal_weight_kg'] : regimen.weight_basis === 'adjusted' ? ['adjusted_weight_kg'] : []),
    'egfr_mL_min', ...(regimen.minimum_patient_values || []).map((g) => g.field),
    ...(regimen.maximum_patient_values || []).map((g) => g.field)])];
  const input = (field: string, title: string, type = 'text') => <label key={field} className="block">{ui(title)}
    <input className="input mt-1" type={type} inputMode={type === 'text' ? 'decimal' : undefined} lang={type === 'text' ? 'en' : undefined} aria-describedby={type === 'text' ? 'pediatric-number-policy' : undefined}
      value={values[field] || ''} onChange={(e) => change(field, e.target.value)} /></label>;
  const submit = async (event: FormEvent) => {
    event.preventDefault();
    const requestedRevision = ++revision.current;
    setResponse(undefined); setError('');
    try {
      const patient: Fields = {};
      for (const field of numericFields) if (values[field]?.trim()) {
        if (patientWeightFields.has(field)) {
          const weight = parsePatientWeight(values[field]);
          if (weight === null) throw new Error(ui("{{label}}: introduce un peso finito entre {{minimum}} y {{maximum}} kg, ambos incluidos.", {
            label: ui(label(field)), minimum: MIN_PATIENT_WEIGHT_KG, maximum: MAX_PATIENT_WEIGHT_KG,
          }));
          patient[field] = weight;
        } else patient[field] = numericInput(values[field], ui(label(field)), !field.includes('weight'));
      }
      for (const gate of flags) if (values[gate.field]) patient[gate.field] = values[gate.field] === 'yes';
      if (values.hepatic_severity) patient.hepatic_severity = values.hepatic_severity;
      for (const field of ['allergies', 'active_medications']) {
        if (values[`${field}_reviewed`] === 'yes') patient[field] = (values[field] || '').split(',').map((s) => s.trim()).filter(Boolean);
      }
      const body: Fields = { regimen_id: regimen.id, patient };
      for (const [field, name] of [['selected_dose_per_kg', ui("Dosis elegida")], ['selected_duration_days', ui("Duración elegida")], ['selected_volume_ml', ui("Volumen elegido")]] as const) {
        if (values[field]?.trim()) body[field] = numericInput(values[field], ui(name));
      }
      if (values.concentration?.trim()) {
        if (values.product_verified !== 'yes') throw new Error(ui("Confirma la presentación exacta antes de calcular mL"));
        body.product = { concentration_mg_per_ml: numericInput(values.concentration, ui("Concentración")),
          external_concentration_verified: values.external_verified === 'yes' };
      }
      setBusy(true);
      const result = await calculatePediatric(body);
      if (revision.current === requestedRevision) { setCalculation(body); setResponse(result); }
    } catch (e) {
      if (revision.current === requestedRevision) setError(e instanceof Error ? e.message : ui("Error de cálculo"));
    } finally {
      if (revision.current === requestedRevision) setBusy(false);
    }
  };
  return <div className="space-y-5">
    <nav aria-label={ui("Secciones pediátricas")} className="flex flex-wrap gap-2">
      <a href="#pediatric-input" className="btn-primary">{ui("Datos y cálculo")}</a>
      <a href="#pediatric-reference" className="btn-ghost">{ui("Ficha y precauciones")}</a>
      {response && <a href="#pediatric-result" className="btn-ghost">{ui("Ver resultado")}</a>}
    </nav>
    <section id="pediatric-reference" className="card p-4 space-y-3" aria-label={ui("Ficha canónica")}>
      <h2 className="text-xl font-bold">{regimen.drug}</h2><p>{regimen.diagnosis}</p>
      <p className="text-sm">{regimen.id}{ui("· YELLOW · pendiente de revisión clínica")}</p>
      <Details value={regimen} />
      {typeof regimen.source_url === 'string' && <a className="underline" href={regimen.source_url} target="_blank" rel="noreferrer">{ui("Consultar fuente canónica")}</a>}
    </section>
    <form id="pediatric-input" onSubmit={submit} className="card p-4 space-y-4" aria-label={ui("Cálculo pediátrico")}>
      <h2 className="text-lg font-bold">{ui("Datos para la pauta seleccionada")}</h2>
      <p id="pediatric-number-policy" className="text-sm text-muted">{ui("Entrada numérica: usa punto decimal (0.1), sin separadores de miles. La salida sigue el idioma seleccionado.")}</p>
      <p className="text-sm text-muted">{ui("Peso introducido: de {{minimum}} a {{maximum}} kg, ambos incluidos; se conservan los límites propios de cada pauta.", {
        minimum: MIN_PATIENT_WEIGHT_KG, maximum: MAX_PATIENT_WEIGHT_KG,
      })}</p>
      <p>{ui("Introduce datos verificados. Una dosis calculable no confirma indicación ni criterios de alta. Los campos vacíos no se interpretan como negativos.")}</p>
      <div className="grid gap-3 sm:grid-cols-2">{numericFields.map((f) => input(f, ui(label(f))))}</div>
      <fieldset className="space-y-3"><legend className="font-bold">{ui("Valoración clínica y contraindicaciones")}</legend>
        {flags.map((gate) => <label className="block" key={gate.field}>{ui(label(gate.field))}
          {gate.message && <span className="block text-sm text-muted">{gate.message}</span>}
          <select className="input mt-1" aria-label={ui(label(gate.field))} value={values[gate.field] || ''} onChange={(e) => change(gate.field, e.target.value)}>
            <option value="">{ui("Sin documentar")}</option><option value="yes">{ui("Sí")}</option><option value="no">{ui("No")}</option>
          </select></label>)}
        <label className="block">{ui("Gravedad de insuficiencia hepática")} <select className="input" value={values.hepatic_severity || ''} onChange={(e) => change('hepatic_severity', e.target.value)}>
            <option value="">{ui("Sin documentar")}</option><option value="mild">{ui("Leve")}</option><option value="moderate">{ui("Moderada")}</option><option value="severe">{ui("Grave")}</option>
          </select></label>
      </fieldset>
      {(['allergies', 'active_medications'] as const).map((f) => <div key={f}>
        {input(f, f === 'allergies' ? ui("Alergias: sustancias o clases, separadas por comas") : ui("Medicamentos actuales, separados por comas"), 'search')}
        <label><input type="checkbox" checked={values[`${f}_reviewed`] === 'yes'} onChange={(e) => change(`${f}_reviewed`, e.target.checked ? 'yes' : '')} />
          {f === 'allergies' ? ui("Estado de alergias revisado") : ui("Medicación actual revisada")}{ui("(vacío significa ninguna conocida solo al confirmar)")}</label>
      </div>)}
      <div className="grid gap-3 sm:grid-cols-2">
        {regimen.dose_mg_per_kg_range && input('selected_dose_per_kg', ui("Dosis elegida dentro del rango (mg/kg)"))}
        {input('selected_duration_days', ui("Duración elegida (días; solo si la fuente exige selección)"))}
        {regimen.dose_model === 'fixed_volume_band' && input('selected_volume_ml', ui("Volumen elegido dentro del rango (mL)"))}
        {regimen.liquid_capable === true && input('concentration', ui("Concentración verificada (mg/mL)"))}
      </div>
      {regimen.liquid_capable === true && <div className="space-y-2">
        <label className="block"><input type="checkbox" checked={values.product_verified === 'yes'} onChange={(e) => change('product_verified', e.target.checked ? 'yes' : '')} />{ui("He verificado la concentración del producto exacto")}</label>
        <label className="block"><input type="checkbox" checked={values.external_verified === 'yes'} onChange={(e) => change('external_verified', e.target.checked ? 'yes' : '')} />{ui("Presentación externa al registro: ficha técnica comprobada")}</label>
      </div>}
      <button className="btn-primary" disabled={busy} type="submit">{busy ? ui("Calculando…") : ui("Comprobar y calcular")}</button>
      {error && <p role="alert" className="rounded-xl border border-danger p-3 font-semibold text-danger">{error}</p>}
    </form>
    <div aria-live="polite" aria-atomic="true" className="sr-only">{response ? (response.blocked ? ui("Cálculo bloqueado. Revisa las alertas.") : ui("Resultado aritmético disponible. Requiere revisión clínica.")) : ''}</div>
    {response && <section ref={resultRef} tabIndex={-1} id="pediatric-result" className={`card p-4 space-y-3 ${response.blocked ? 'border-danger' : 'border-primary'}`} aria-label={ui("Resultado pediátrico")}>
      <h2 className="text-xl font-bold">{response.blocked ? ui("Cálculo bloqueado") : ui("Resultado aritmético — requiere revisión clínica")}</h2>
      <p>{response.safety.prescription_status}</p>
      {response.safety.alerts.map((a, i) => <p key={i} className={`rounded-xl border p-3 ${a.severity === 'STOP' ? 'border-danger bg-surface text-danger' : 'border-warn bg-warn-bg text-warn'}`}><strong>{a.severity === 'STOP' ? '⛔ ' : '⚠ '}{a.severity}: </strong>{a.message} {a.action}</p>)}
      {!response.blocked && response.result && <ResultDetails value={response.result} />}
      {!response.blocked && response.result && response.export_report && calculation && <PediatricExport report={response.export_report} calculation={calculation} result={response.result} />}
    </section>}
  </div>;
}

export default function PediatricOutpatient() {
  const ui = useClinicalUi();
  const [params, setParams] = useSearchParams();
  const selected = findRegimen(params.get('regimen') || '');
  const [drug, setDrug] = useState(selected?.drug_id || '');
  const regimens = drug ? regimensForDrug(drug) : pediatricCatalog.regimens;
  return <div className="space-y-5">
    <header><h1 className="text-2xl font-bold">{ui("Pediatría ambulatoria")}</h1>
      <p className="text-sm text-muted">{ui("Contenido clínico y exportaciones canónicas en el idioma de la fuente; traducción clínica integral pendiente.")}</p>
      <p>{pediatricCatalog.inventory.regimens} {ui("regímenes ·")} {pediatricCatalog.inventory.drug_groups} {ui("fármacos o combinaciones ·")} {pediatricCatalog.inventory.diagnoses} {ui("diagnósticos. YELLOW: revisión pediátrica/farmacéutica pendiente.")}</p>
      <p>{ui("El catálogo general conserva todas las pautas; edad y peso se comprueban al calcular. Datos de referencia en el idioma de la fuente.")}</p>
    </header>
    <label className="block">{ui("Fármaco o combinación")} <select className="input" value={drug} onChange={(e) => { setDrug(e.target.value); setParams({}); }}>
        <option value="">{ui("Todos los fármacos")}</option>{pediatricCatalog.drugs.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
      </select></label>
    <label className="block">{ui("Diagnóstico y régimen")} <select className="input" value={selected?.id || ''} onChange={(e) => setParams({ regimen: e.target.value })}>
        <option value="">{ui("Selecciona una pauta por indicación")}</option>{regimens.map((r) => <option key={r.id} value={r.id}>{r.drug} — {r.diagnosis} ({r.id})</option>)}
      </select></label>
    {selected && <RegimenForm key={selected.id} regimen={selected} />}
  </div>;
}
