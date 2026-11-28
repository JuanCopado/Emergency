import CountryReferences from '../components/CountryReferences';
import { localRevisionHeaders } from '../lib/individualTransport';
import { useClinicalUi } from '../i18n/useClinicalUi';
import ClinicalValue from '../components/ClinicalValue';
import { parseFiniteDecimal } from '../lib/format';
import { parsePatientWeight } from '../lib/patientWeight';
import { useEffect, useRef, useState, type FormEvent } from 'react';
import { createPortal } from 'react-dom';
import { Link } from 'react-router-dom';

type Field = {key:string; label:string; kind:'number'|'boolean'|'choice'; integer?:boolean; expected?:unknown; options?:string[]; option_labels?:Record<string,string>; required_if?:{key:string; equals:string}; minimum?:number; maximum?:number; exclusive_minimum?:number; exclusive_maximum?:number};
type Regimen = {id:string; label:string; group:string; group_label:string; drug:string; route:string|null; dose_unit:string|null; fields:Field[]; source:{body:string; preamble:string; contract_review?:{body:string}}; limitations:string[]};
type Catalog = {source_revision:string; regimens:Regimen[]};
type Result = Record<string, unknown>;
type Report = {snapshot:Result; sections:[string,string[]][]};
type Outcome = {blocked:boolean; alerts:{code:string;message:string}[]; result?:Result; report?:Report};
const base = (import.meta.env.VITE_CLINICAL_NOTE_API_BASE ?? '').replace(/\/$/, '');
async function post<T,>(path:string, body:unknown):Promise<T> {
  const response = await fetch(`${base}/api/acute-medications/${path}`, {method:'POST', headers:{'Content-Type':'application/json',...localRevisionHeaders()}, cache:'no-store', body:JSON.stringify(body)});
  const value = await response.json();
  if (!response.ok) throw new Error(value.error || `Error ${response.status}`);
  return value as T;
}

const calculationFields = {indication:'Indicación', drug:'Fármaco', route:'Vía', dose:'Dosis', dose_unit:'Unidad de dosis', components:'Componentes y secuencia (no intercambiables)', correction_ceiling_mmol_l:'Límite acumulado de corrección de Na (mmol/L; no objetivo)', concentration:'Concentración y función', withdrawal_ml:'Volumen extraído del producto (mL)', administration_volume_ml:'Volumen de administración (mL)', pump_ml_h:'Velocidad de bomba (mL/h)', duration_min:'Duración (min)', amount_per_hour:'Cantidad por hora', amount_per_hour_unit:'Unidad por hora', maximum:'Máximo', preparation:'Preparación / dilución', compatibility:'Compatibilidad', stability:'Estabilidad', administration:'Administración', limitations:'Datos ausentes / límites'};
const decisionFields = {indication:'Situación evaluada', decision_support:'Orientación clínica', next_actions:'Siguientes pasos', limitations:'Alcance y límites'};
const fieldActive = (field:Field, values:Record<string,string>) => !field.required_if || values[field.required_if.key] === field.required_if.equals;

export default function AcuteMedications() {
  const ui = useClinicalUi();
  const display = (value: unknown) => value == null ? ui("No especificado en la fuente; requiere verificación profesional") : <ClinicalValue value={value} />;
  const [catalog, setCatalog] = useState<Catalog>();
  const [group, setGroup] = useState('');
  const [id, setId] = useState('');
  const [values, setValues] = useState<Record<string,string>>({});
  const [outcome, setOutcome] = useState<Outcome>();
  const [calculation, setCalculation] = useState<unknown>();
  const [confirmed, setConfirmed] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const revision = useRef(0);
  useEffect(() => {
    let alive = true; const counter = revision;
    post<Catalog>('catalog', {}).then(value => {if (alive) setCatalog(value);}).catch(e => {if (alive) setError(String(e));});
    return () => {alive = false; counter.current++;};
  }, []);
  const clear = () => {revision.current++; setOutcome(undefined); setConfirmed(false); setCalculation(undefined); setError(''); setBusy(false);};
  const regimen = catalog?.regimens.find(r => r.id === id);
  async function calculate(event:FormEvent) {
    event.preventDefault(); clear();
    if (!catalog || !regimen) return;
    const current = revision.current;
    try {
      const inputs:Record<string,unknown> = {};
      for (const f of regimen.fields) {
        if (!fieldActive(f, values)) continue;
        const value = values[f.key]?.trim();
        if (!value) throw new Error(ui("{{label}}: dato obligatorio sin documentar.", {label:f.label}));
        if (f.kind === 'number') {
          const integerGate = f.integer === true || (typeof f.expected === 'number' && Number.isInteger(f.expected));
          const number = f.key === 'weight_kg' ? parsePatientWeight(value) : parseFiniteDecimal(value, integerGate);
          if (f.key === 'weight_kg') {
            if (number === null) throw new Error(ui("El peso debe estar entre 1 y 180 kg, ambos incluidos."));
            if ((f.minimum !== undefined && number < f.minimum) || (f.maximum !== undefined && number > f.maximum)
                || (f.exclusive_minimum !== undefined && number <= f.exclusive_minimum)
                || (f.exclusive_maximum !== undefined && number >= f.exclusive_maximum)) {
              throw new Error(ui("El peso no cumple los límites específicos de esta pauta."));
            }
          }
          if (number === null) throw new Error(ui("{{label}}: introduce un número finito con punto decimal.", {label:f.label}));
          inputs[f.key] = number;
        } else inputs[f.key] = f.kind === 'boolean' ? value === 'yes' : value;
      }
      const body = {regimen_id:id, source_revision:catalog.source_revision, inputs};
      setBusy(true);
      const data = await post<Outcome>('calculate', body);
      if (revision.current === current) {setOutcome(data); setCalculation(body);}
    } catch (e) {if (revision.current === current) setError(e instanceof Error ? e.message : String(e));}
    finally {if (revision.current === current) setBusy(false);}
  }
  async function download(format:'json'|'pdf'|'docx') {
    if (!confirmed || !outcome?.result) return;
    const current = revision.current; setBusy(true); setError('');
    try {
      const data = await post<{content_base64:string;mime_type:string;filename:string}>('export', {format, calculation, expected_result:outcome.result, confirmed:true});
      if (current !== revision.current) return;
      const bytes = Uint8Array.from(atob(data.content_base64), c => c.charCodeAt(0));
      const url = URL.createObjectURL(new Blob([bytes], {type:data.mime_type}));
      const anchor = document.createElement('a'); anchor.href = url; anchor.download = data.filename; anchor.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    } catch (e) {if (current === revision.current) setError(String(e));}
    finally {if (current === revision.current) setBusy(false);}
  }
  const groups = [...new Map(catalog?.regimens.map(r => [r.group,r.group_label]) || []).entries()];
  const reportContent = outcome?.report?.sections.map(([heading,paragraphs],i) => <section key={i}><h3 className="font-bold mt-4">{heading}</h3>{paragraphs.map((text,j) => {
    const isDoseUnit = text.startsWith('dose_unit:') && paragraphs[j - 1]?.startsWith('dose:');
    if (isDoseUnit) return null;
    const doseUnit = text.startsWith('dose:') && paragraphs[j + 1]?.startsWith('dose_unit:') ? paragraphs[j + 1] : undefined;
    const paragraph = <p className="whitespace-pre-wrap break-words">{text}</p>;
    return doseUnit !== undefined
      ? <div className="acute-print-measure" key={j}>{paragraph}<p className="whitespace-pre-wrap break-words">{doseUnit}</p></div>
      : <p className="whitespace-pre-wrap break-words" key={j}>{text}</p>;
  })}</section>);
  return <div className="space-y-5">
    <header><h1 className="text-2xl font-bold">{ui("Farmacología aguda")}</h1><p>{ui("CLINICALLY_PENDING · Cálculos y apoyo de decisión según la guía aplicable y los datos del caso. Selecciona una indicación y una opción; las alternativas no se administran juntas por defecto.")}</p></header>
    <p id="acute-number-policy" className="text-sm text-muted">{ui("Entrada numérica: usa punto decimal (0.1), sin separadores de miles. La salida sigue el idioma seleccionado.")}</p>
    <p className="text-sm text-muted">{ui("Contenido clínico y exportaciones canónicas en el idioma de la fuente; traducción clínica integral pendiente.")}</p>
    <Link className="btn-ghost" to="/insulin-uci">{ui("Insulinoterapia UCI · laboratorio de simulación")}</Link>
    <label className="block">{ui("Grupo farmacológico")}<select className="input" data-testid="acute-group" aria-label={ui("Grupo farmacológico")} value={group} onChange={e => {clear(); setGroup(e.target.value); setId(''); setValues({});}}><option value="">{ui("Selecciona grupo")}</option>{groups.map(([key,label]) => <option value={key} key={key}>{label}</option>)}</select></label>
    {group && <label className="block">{ui("Indicación y opción")}<select className="input" data-testid="acute-regimen" aria-label={ui("Indicación y opción")} value={id} onChange={e => {clear(); setId(e.target.value); setValues({});}}><option value="">{ui("Selecciona indicación y opción")}</option>{catalog?.regimens.filter(r => r.group === group).map(r => <option key={r.id} value={r.id}>{r.label} — {r.drug}</option>)}</select></label>}
    {regimen && <>
      <CountryReferences key={regimen.id} drug={regimen.drug} />
      <section className="card p-4" aria-label={ui("Fuente y precauciones")}><h2 className="font-bold">{[regimen.drug, regimen.route, regimen.dose_unit].filter(Boolean).join(' · ')}</h2><ul>{regimen.limitations.map(t => <li key={t}>{t}</li>)}</ul><details><summary>{ui("Fuente canónica completa y advertencias")}</summary><p className="whitespace-pre-wrap">{regimen.source.preamble}</p><p className="whitespace-pre-wrap">{regimen.source.body}</p>{regimen.source.contract_review && <><h3 className="font-bold mt-4">{ui("Revisión de esta pauta y alcance de la aceptación")}</h3><p className="whitespace-pre-wrap">{regimen.source.contract_review.body}</p></>}</details></section>
      <form onSubmit={calculate} className="card p-4 space-y-3" data-testid="acute-form" aria-label={ui("Datos farmacológicos")}>
        {regimen.fields.filter(f => fieldActive(f, values)).map(f => <label className="block" key={f.key}>{f.label}{f.kind === 'number' ? <input className="input" aria-label={f.label} data-field={f.key} inputMode="decimal" lang="en" aria-describedby="acute-number-policy" value={values[f.key] || ''} onChange={e => {clear(); setValues(v => ({...v,[f.key]:e.target.value}));}} /> : <select className="input" aria-label={f.label} data-field={f.key} value={values[f.key] || ''} onChange={e => {clear(); setValues(v => ({...v,[f.key]:e.target.value}));}}><option value="">{ui("Sin documentar")}</option>{(f.kind === 'boolean' ? ['yes','no'] : f.options || []).map(v => <option key={v} value={v}>{v === 'yes' ? ui("Sí") : v === 'no' ? ui("No") : (f.option_labels?.[v] || v)}</option>)}</select>}</label>)}
        <button type="submit" className="btn-primary" disabled={busy}>{ui("Comprobar y calcular")}</button>
      </form>
    </>}
    {error && <p role="alert" className="text-danger">{error}</p>}
    {outcome && <section className="card p-4 space-y-3" aria-label={ui("Resultado farmacológico")}>
      <h2 className="text-xl font-bold">{outcome.blocked ? ui("Cálculo bloqueado") : outcome.result?.result_kind === 'decision_support' ? ui("Orientación clínica y siguientes pasos") : ui("Resultado del cálculo")}</h2>
      {outcome.alerts.map(a => <p role="alert" key={a.code}>STOP: {a.message}</p>)}
      {outcome.result && <>
        {outcome.result.review_status === 'OWNER_VALIDATED_2026_11_16' && <p className="font-medium" data-testid="owner-validation">{ui("Validación del propietario registrada · 16/11/2026. Resultado condicionado a los datos y controles de este caso.")}</p>}
        <dl className="grid gap-3 sm:grid-cols-2">{Object.entries(outcome.result.result_kind === 'decision_support' ? decisionFields : calculationFields).map(([key,label]) => <div key={key}><dt className="font-bold">{ui(label)}</dt><dd className="whitespace-pre-wrap" data-result={key}>{display(outcome.result?.[key])}</dd></div>)}</dl>
        {outcome.result.result_kind !== 'decision_support' && Array.isArray(outcome.result.next_actions) && outcome.result.next_actions.length > 0 && <div><h3 className="font-bold">{ui("Siguientes pasos")}</h3><div className="whitespace-pre-wrap">{display(outcome.result.next_actions)}</div></div>}
        <div className="whitespace-pre-wrap" data-testid="acute-warnings">{display(outcome.result.monitoring_and_warnings)}</div>
        <label className="block"><input type="checkbox" checked={confirmed} onChange={e => {revision.current++; setConfirmed(e.target.checked); setBusy(false);}} />{ui("Confirmo haber revisado el resultado completo, sus límites y advertencias")}</label>
        <div data-testid="acute-export" className="flex flex-wrap gap-2">{(['json','pdf','docx'] as const).map(f => <button key={f} className="btn-ghost" disabled={!confirmed || busy} onClick={() => download(f)}>{ui("Exportar")} {f.toUpperCase()}</button>)}<button className="btn-ghost" disabled={!confirmed} onClick={() => window.print()}>{ui("Imprimir resultado")}</button></div>
        <details><summary>{ui("Contenido íntegro de la exportación")}</summary><div data-testid="acute-export-content">{reportContent}</div></details>
      </>}
    </section>}
    {confirmed && outcome?.report && createPortal(<article className="acute-print-sheet" aria-hidden="true">{reportContent}</article>, document.body)}
  </div>;
}
