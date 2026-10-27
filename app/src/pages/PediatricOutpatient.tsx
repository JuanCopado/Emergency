import PediatricExport from '../pediatrics/PediatricExport';
import { useEffect, useRef, useState, type FormEvent } from 'react';
import { useSearchParams } from 'react-router-dom';
import { formatClinicalNumber } from '../lib/clinicalInput';
import { StopAlert } from '../components/StopAlert';
import { classifyPediatric, type Outcome, type PediatricSuccess, type SafetyAlert } from '../lib/clinicalOutcome';
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
const NON_STOP = new Set(['ALERT', 'CAUTION', 'INFO']);
const label = (key: string) => labels[key] || key.replaceAll('_', ' ');
const omitted = new Set(['id', 'drug_id', 'drug', 'diagnosis', 'dose_model', 'liquid_capable', 'source_url',
  'medication_safety', 'prescription_status', 'status', 'regimen_id']);

// Unit shown beside a number for unambiguous keys (mg vs mg/kg, mL, kg). Display only: full precision, decimal comma.
const units: Record<string, string> = {
  dose_mg: 'mg', dose_mg_per_kg: 'mg/kg', max_mg_per_dose: 'mg', adult_max_daily_mg: 'mg', daily_max_mg_per_kg: 'mg/kg',
  dosing_weight_kg: 'kg', actual_weight_kg: 'kg', ideal_weight_kg: 'kg', adjusted_weight_kg: 'kg',
  exact_ml: 'mL', rounded_0_1_ml: 'mL', estimated_total_course_ml: 'mL', concentration_mg_per_ml: 'mg/mL', mg_per_ml: 'mg/mL',
};

function Details({ value, field }: { value: Value; field?: string }) {
  if (value == null) return <span>No consta en la fuente</span>;
  if (Array.isArray(value)) return <ul className="space-y-1">{value.map((v, i) => <li key={i}><Details value={v} field={field} /></li>)}</ul>;
  if (typeof value === 'object') return <dl className="space-y-2">{Object.entries(value).filter(([k]) => !omitted.has(k)).map(([k, v]) =>
    <div key={k}><dt className="font-semibold">{label(k)}</dt><dd className="ml-3"><Details value={v} field={k} /></dd></div>)}</dl>;
  if (typeof value === 'number') {
    const unit = field ? units[field] : undefined;
    return <span className={unit ? 'whitespace-nowrap' : undefined}>{formatClinicalNumber(value) ?? 'No consta en la fuente'}{unit ? `\u00a0${unit}` : ''}</span>;
  }
  return <span>{typeof value === 'boolean' ? (value ? 'Sí' : 'No') : String(value)}</span>;
}

// Reorder presentation only; every returned value retains its original units and precision.
function ResultDetails({ value }: { value: Fields }) {
  const primaryKeys = ['dose_mg', 'volume_per_dose', 'dosing_weight_kg', 'weight_basis',
    'concentration_mg_per_ml', 'frequency', 'max_mg_per_dose', 'adult_max_daily_mg',
    'daily_max_mg_per_kg', 'duration_days', 'estimated_total_course_ml'];
  const primary = primaryKeys.filter(key => Object.hasOwn(value, key));
  const remaining = Object.fromEntries(Object.entries(value).filter(([key]) => !primary.includes(key)));
  return <>
    <dl className="grid gap-3 sm:grid-cols-2" aria-label="Cálculo y pauta">
      {primary.map(key => <div className="rounded-xl border border-primary/30 bg-surface-2 p-3" key={key}>
        <dt className="font-bold">{label(key)}</dt><dd className="mt-1 text-lg"><Details value={value[key] ?? null} field={key} /></dd>
      </div>)}
    </dl>
    <div className="border-t border-border pt-3"><h3 className="mb-2 font-bold">Detalle, precauciones y fuente</h3><Details value={remaining} /></div>
  </>;
}

const ERROR_ID = 'pediatric-input-error';

function RegimenForm({ regimen }: { regimen: Regimen }) {
  const [values, setValues] = useState<Record<string, string>>({});
  const [response, setResponse] = useState<Calculation>();
  // classifyPediatric (S0) is the only path to figures: STOP or unknown severity hides the dose even with blocked:false.
  const [outcome, setOutcome] = useState<Outcome<PediatricSuccess>>();
  // G-P2: export and print exist only after explicit confirmation; any input change or new result resets it.
  const [confirmed, setConfirmed] = useState(false);
  const [calculation, setCalculation] = useState<Fields>();
  const [error, setError] = useState('');
  const [errorField, setErrorField] = useState<string | null>(null);
  const formRef = useRef<HTMLFormElement>(null);
  useEffect(() => {
    if (errorField) formRef.current?.querySelector<HTMLInputElement>(`[data-field="${errorField}"]`)?.focus();
  }, [errorField]);
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
    setResponse(undefined); setOutcome(undefined); setConfirmed(false); setError(''); setErrorField(null); setBusy(false);
  };
  const gates: Gate[] = [...(regimen.required_patient_flags || []), ...(regimen.excluded_patient_flags || []),
    ...pediatricCatalog.condition_rules.filter((r) => !r.drug || r.drug === regimen.drug),
    { field: 'known_renal_impairment' }, { field: 'known_hepatic_impairment' }];
  const flags = [...new Map(gates.map((g) => [g.field, g])).values()];
  const numericFields = [...new Set(['age_months', 'actual_weight_kg',
    ...(regimen.weight_basis === 'ideal' ? ['ideal_weight_kg'] : regimen.weight_basis === 'adjusted' ? ['adjusted_weight_kg'] : []),
    'egfr_mL_min', ...(regimen.minimum_patient_values || []).map((g) => g.field),
    ...(regimen.maximum_patient_values || []).map((g) => g.field)])];
  // Q07-R: an input error is tied to its field (aria-invalid + aria-describedby) and the field receives focus.
  const input = (field: string, title: string, type = 'text') => <label key={field} className="block">{title}
    <input className="input mt-1" type={type} inputMode={type === 'text' ? 'decimal' : undefined} data-field={field}
      aria-invalid={errorField === field ? true : undefined} aria-describedby={errorField === field ? ERROR_ID : undefined}
      value={values[field] || ''} onChange={(e) => change(field, e.target.value)} /></label>;
  const submit = async (event: FormEvent) => {
    event.preventDefault();
    const requestedRevision = ++revision.current;
    setResponse(undefined); setOutcome(undefined); setConfirmed(false); setError(''); setErrorField(null);
    let parsing: string | null = null;
    const parse = (field: string, name: string, allowZero = false) => { parsing = field; const n = numericInput(values[field] ?? '', name, allowZero); parsing = null; return n; };
    try {
      const patient: Fields = {};
      for (const field of numericFields) if (values[field]?.trim()) patient[field] = parse(field, label(field), !field.includes('weight'));
      for (const gate of flags) if (values[gate.field]) patient[gate.field] = values[gate.field] === 'yes';
      if (values.hepatic_severity) patient.hepatic_severity = values.hepatic_severity;
      for (const field of ['allergies', 'active_medications']) {
        if (values[`${field}_reviewed`] === 'yes') patient[field] = (values[field] || '').split(',').map((s) => s.trim()).filter(Boolean);
      }
      const body: Fields = { regimen_id: regimen.id, patient };
      for (const [field, name] of [['selected_dose_per_kg', 'Dosis elegida'], ['selected_duration_days', 'Duración elegida'], ['selected_volume_ml', 'Volumen elegido']] as const) {
        if (values[field]?.trim()) body[field] = parse(field, name);
      }
      if (values.concentration?.trim()) {
        if (values.product_verified !== 'yes') throw new Error('Confirma la presentación exacta antes de calcular mL');
        body.product = { concentration_mg_per_ml: parse('concentration', 'Concentración'),
          external_concentration_verified: values.external_verified === 'yes' };
      }
      setBusy(true);
      const result = await calculatePediatric(body);
      if (revision.current === requestedRevision) {
        const classified = classifyPediatric(result);
        if (classified.kind === 'ERROR') { setError(`Respuesta del servidor no válida (${classified.detail}); no se muestra ningún resultado.`); return; }
        setCalculation(body); setResponse(result); setOutcome(classified);
      }
    } catch (e) {
      if (revision.current === requestedRevision) { setError(e instanceof Error ? e.message : 'Error de cálculo'); setErrorField(parsing); }
    } finally {
      if (revision.current === requestedRevision) setBusy(false);
    }
  };
  const success = outcome?.kind === 'SUCCESS' ? outcome.result : undefined;
  const stopped = outcome?.kind === 'STOP' || outcome?.kind === 'BLOCKED';
  // U08c: alerts go through StopAlert (STOP → role=alert/assertive; ALERT/CAUTION/INFO → role=status/polite).
  const alerts: SafetyAlert[] = outcome && outcome.kind !== 'ERROR' ? outcome.alerts : [];
  // StopAlert groups by trimmed severity; classifyPediatric stops on any severity outside the exact set.
  // If the calculation is stopped but StopAlert would render no STOP group (no alerts, or e.g. " ALERT "),
  // an explicit assertive STOP keeps exactly one assertive announcement for every stopped result.
  const stopGroupShown = alerts.some((a) => !NON_STOP.has(a.severity.trim()));
  const needsStopFallback = stopped && !stopGroupShown;
  return <div className="space-y-5">
    <nav aria-label="Secciones pediátricas" className="flex flex-wrap gap-2">
      <a href="#pediatric-input" className="btn-primary">Datos y cálculo</a>
      <a href="#pediatric-reference" className="btn-ghost">Ficha y precauciones</a>
      {response && <a href="#pediatric-result" className="btn-ghost">Ver resultado</a>}
    </nav>
    <section id="pediatric-reference" className="card p-4 space-y-3" aria-label="Ficha canónica">
      <h2 className="text-xl font-bold">{regimen.drug}</h2><p>{regimen.diagnosis}</p>
      <p className="text-sm">{regimen.id} · YELLOW · pendiente de revisión clínica</p>
      <Details value={regimen} />
      {typeof regimen.source_url === 'string' && <a className="underline" href={regimen.source_url} target="_blank" rel="noreferrer">Consultar fuente canónica</a>}
    </section>
    <form ref={formRef} id="pediatric-input" onSubmit={submit} className="card p-4 space-y-4" aria-label="Cálculo pediátrico">
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
      {error && <p id={ERROR_ID} role="alert" className="rounded-xl border border-danger p-3 font-semibold text-danger">{error}</p>}
    </form>
    {/* Polite summary only for a result; a stopped calculation is announced once, assertively, below. */}
    <div aria-live="polite" aria-atomic="true" className="sr-only">{outcome && !stopped ? 'Resultado aritmético disponible. Requiere revisión clínica.' : ''}</div>
    {/* Q05-R: an unconfirmed result is excluded from browser printing (Ctrl+P), not only from the print button. */}
    {success && !confirmed && <p className="hidden print:block font-bold" data-testid="pediatric-print-blocked">Impresión no disponible: confirmar la revisión del resultado antes de imprimir.</p>}
    {response && outcome && <section ref={resultRef} tabIndex={-1} id="pediatric-result" className={`card p-4 space-y-3 ${stopped ? 'border-danger' : 'border-primary'}${success && !confirmed ? ' print:hidden' : ''}`} aria-label="Resultado pediátrico">
      <h2 className="text-xl font-bold">{outcome.kind === 'STOP' ? 'STOP — cálculo detenido; no se muestra ninguna dosis' : stopped ? 'Cálculo bloqueado' : 'Resultado aritmético — requiere revisión clínica'}</h2>
      <p>{String(response.safety?.prescription_status ?? '')}</p>
      {needsStopFallback && <p role="alert" aria-live="assertive" tabIndex={-1} className="rounded-2xl border-2 border-danger p-3 font-bold text-danger" data-testid="stop-fallback">STOP: el cálculo está detenido; no se muestra ninguna dosis. Revise los avisos y la ficha.</p>}
      <StopAlert alerts={alerts} />
      {success && <ResultDetails value={success.result as Fields} />}
      {success && success.exportReport != null && calculation && <label className="block font-semibold"><input type="checkbox" checked={confirmed} onChange={(e) => setConfirmed(e.target.checked)} /> Confirmo haber revisado el resultado completo, sus límites y advertencias</label>}
      {success && success.exportReport != null && calculation && confirmed && <PediatricExport report={success.exportReport as NonNullable<Calculation['export_report']>} calculation={calculation} result={success.result as Fields} />}
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
