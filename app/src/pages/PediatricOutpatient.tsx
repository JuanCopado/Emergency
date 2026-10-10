import { useRef, useState, type FormEvent } from 'react';
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
const omitted = new Set(['id', 'drug_id', 'drug', 'diagnosis', 'dose_model', 'liquid_capable', 'source_url',
  'medication_safety', 'prescription_status', 'status', 'regimen_id']);

function Details({ value }: { value: Value }) {
  if (value == null) return <span>No consta en la fuente</span>;
  if (Array.isArray(value)) return <ul className="space-y-1">{value.map((v, i) => <li key={i}><Details value={v} /></li>)}</ul>;
  if (typeof value === 'object') return <dl className="space-y-2">{Object.entries(value).filter(([k]) => !omitted.has(k)).map(([k, v]) =>
    <div key={k}><dt className="font-semibold">{label(k)}</dt><dd className="ml-3"><Details value={v} /></dd></div>)}</dl>;
  return <span>{typeof value === 'boolean' ? (value ? 'Sí' : 'No') : String(value)}</span>;
}

function RegimenForm({ regimen }: { regimen: Regimen }) {
  const [values, setValues] = useState<Record<string, string>>({});
  const [response, setResponse] = useState<Calculation>();
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
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
  const input = (field: string, title: string, type = 'text') => <label key={field} className="block">{title}
    <input className="input mt-1" type={type} inputMode={type === 'text' ? 'decimal' : undefined}
      value={values[field] || ''} onChange={(e) => change(field, e.target.value)} /></label>;
  const submit = async (event: FormEvent) => {
    event.preventDefault();
    const requestedRevision = ++revision.current;
    setResponse(undefined); setError('');
    try {
      const patient: Fields = {};
      for (const field of numericFields) if (values[field]?.trim()) patient[field] = numericInput(values[field], label(field), !field.includes('weight'));
      for (const gate of flags) if (values[gate.field]) patient[gate.field] = values[gate.field] === 'yes';
      if (values.hepatic_severity) patient.hepatic_severity = values.hepatic_severity;
      for (const field of ['allergies', 'active_medications']) {
        if (values[`${field}_reviewed`] === 'yes') patient[field] = (values[field] || '').split(',').map((s) => s.trim()).filter(Boolean);
      }
      const body: Fields = { regimen_id: regimen.id, patient };
      for (const [field, name] of [['selected_dose_per_kg', 'Dosis elegida'], ['selected_duration_days', 'Duración elegida'], ['selected_volume_ml', 'Volumen elegido']] as const) {
        if (values[field]?.trim()) body[field] = numericInput(values[field], name);
      }
      if (values.concentration?.trim()) {
        if (values.product_verified !== 'yes') throw new Error('Confirma la presentación exacta antes de calcular mL');
        body.product = { concentration_mg_per_ml: numericInput(values.concentration, 'Concentración'),
          external_concentration_verified: values.external_verified === 'yes' };
      }
      setBusy(true);
      const result = await calculatePediatric(body);
      if (revision.current === requestedRevision) setResponse(result);
    } catch (e) {
      if (revision.current === requestedRevision) setError(e instanceof Error ? e.message : 'Error de cálculo');
    } finally {
      if (revision.current === requestedRevision) setBusy(false);
    }
  };
  return <div className="space-y-5">
    <section className="card p-4 space-y-3" aria-label="Ficha canónica">
      <h2 className="text-xl font-bold">{regimen.drug}</h2><p>{regimen.diagnosis}</p>
      <p className="text-sm">{regimen.id} · YELLOW · pendiente de revisión clínica</p>
      <Details value={regimen} />
      {typeof regimen.source_url === 'string' && <a className="underline" href={regimen.source_url} target="_blank" rel="noreferrer">Consultar fuente canónica</a>}
    </section>
    <form onSubmit={submit} className="card p-4 space-y-4" aria-label="Cálculo pediátrico">
      <h2 className="text-lg font-bold">Datos para la pauta seleccionada</h2>
      <p>Introduce datos verificados. Una dosis calculable no confirma indicación ni criterios de alta. Los campos vacíos no se interpretan como negativos.</p>
      <div className="grid gap-3 sm:grid-cols-2">{numericFields.map((f) => input(f, label(f)))}</div>
      <fieldset className="space-y-3"><legend className="font-bold">Valoración clínica y contraindicaciones</legend>
        {flags.map((gate) => <label className="block" key={gate.field}>{label(gate.field)}
          {gate.message && <span className="block text-sm text-muted">{gate.message}</span>}
          <select className="input mt-1" aria-label={label(gate.field)} value={values[gate.field] || ''} onChange={(e) => change(gate.field, e.target.value)}>
            <option value="">Sin documentar</option><option value="yes">Sí</option><option value="no">No</option>
          </select></label>)}
        <label className="block">Gravedad de insuficiencia hepática
          <select className="input" value={values.hepatic_severity || ''} onChange={(e) => change('hepatic_severity', e.target.value)}>
            <option value="">Sin documentar</option><option value="mild">Leve</option><option value="moderate">Moderada</option><option value="severe">Grave</option>
          </select></label>
      </fieldset>
      {(['allergies', 'active_medications'] as const).map((f) => <div key={f}>
        {input(f, f === 'allergies' ? 'Alergias: sustancias o clases, separadas por comas' : 'Medicamentos actuales, separados por comas', 'search')}
        <label><input type="checkbox" checked={values[`${f}_reviewed`] === 'yes'} onChange={(e) => change(`${f}_reviewed`, e.target.checked ? 'yes' : '')} />
          {f === 'allergies' ? 'Estado de alergias revisado' : 'Medicación actual revisada'} (vacío significa ninguna conocida solo al confirmar)</label>
      </div>)}
      <div className="grid gap-3 sm:grid-cols-2">
        {regimen.dose_mg_per_kg_range && input('selected_dose_per_kg', 'Dosis elegida dentro del rango (mg/kg)')}
        {input('selected_duration_days', 'Duración elegida (días; solo si la fuente exige selección)')}
        {regimen.dose_model === 'fixed_volume_band' && input('selected_volume_ml', 'Volumen elegido dentro del rango (mL)')}
        {regimen.liquid_capable === true && input('concentration', 'Concentración verificada (mg/mL)')}
      </div>
      {regimen.liquid_capable === true && <div className="space-y-2">
        <label className="block"><input type="checkbox" checked={values.product_verified === 'yes'} onChange={(e) => change('product_verified', e.target.checked ? 'yes' : '')} /> He verificado la concentración del producto exacto</label>
        <label className="block"><input type="checkbox" checked={values.external_verified === 'yes'} onChange={(e) => change('external_verified', e.target.checked ? 'yes' : '')} /> Presentación externa al registro: ficha técnica comprobada</label>
      </div>}
      <button className="btn-primary" disabled={busy} type="submit">{busy ? 'Calculando…' : 'Comprobar y calcular'}</button>
      {error && <p role="alert">{error}</p>}
    </form>
    {response && <section className="card p-4 space-y-3" aria-label="Resultado pediátrico">
      <h2 className="text-xl font-bold">{response.blocked ? 'Cálculo bloqueado' : 'Resultado aritmético — requiere revisión clínica'}</h2>
      <p>{response.safety.prescription_status}</p>
      {response.safety.alerts.map((a, i) => <p key={i}><strong>{a.severity}: </strong>{a.message} {a.action}</p>)}
      {!response.blocked && response.result && <Details value={response.result} />}
    </section>}
  </div>;
}

export default function PediatricOutpatient() {
  const [params, setParams] = useSearchParams();
  const selected = findRegimen(params.get('regimen') || '');
  const [drug, setDrug] = useState(selected?.drug_id || '');
  const regimens = drug ? regimensForDrug(drug) : pediatricCatalog.regimens;
  return <div className="space-y-5">
    <header><h1 className="text-2xl font-bold">Pediatría ambulatoria</h1>
      <p>{pediatricCatalog.inventory.regimens} regímenes · {pediatricCatalog.inventory.drug_groups} fármacos o combinaciones · {pediatricCatalog.inventory.diagnoses} diagnósticos. YELLOW: revisión pediátrica/farmacéutica pendiente.</p>
      <p>El catálogo general conserva todas las pautas; edad y peso se comprueban al calcular. Datos de referencia en el idioma de la fuente.</p>
    </header>
    <label className="block">Fármaco o combinación
      <select className="input" value={drug} onChange={(e) => { setDrug(e.target.value); setParams({}); }}>
        <option value="">Todos los fármacos</option>{pediatricCatalog.drugs.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
      </select></label>
    <label className="block">Diagnóstico y régimen
      <select className="input" value={selected?.id || ''} onChange={(e) => setParams({ regimen: e.target.value })}>
        <option value="">Selecciona una pauta por indicación</option>{regimens.map((r) => <option key={r.id} value={r.id}>{r.drug} — {r.diagnosis} ({r.id})</option>)}
      </select></label>
    {selected && <RegimenForm key={selected.id} regimen={selected} />}
  </div>;
}
