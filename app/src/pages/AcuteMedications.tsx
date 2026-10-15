import { useEffect, useRef, useState, type FormEvent } from 'react';
import { createPortal } from 'react-dom';

type Field = {key:string; label:string; kind:'number'|'boolean'|'choice'; options?:string[]};
type Regimen = {id:string; label:string; group:string; group_label:string; drug:string; route:string; dose_unit:string; fields:Field[]; source:{body:string; preamble:string}; limitations:string[]};
type Catalog = {source_revision:string; regimens:Regimen[]};
type Result = Record<string, unknown>;
type Report = {snapshot:Result; sections:[string,string[]][]};
type Outcome = {blocked:boolean; alerts:{code:string;message:string}[]; result?:Result; report?:Report};
const base = (import.meta.env.VITE_CLINICAL_NOTE_API_BASE ?? '').replace(/\/$/, '');
async function post<T,>(path:string, body:unknown):Promise<T> {
  const response = await fetch(`${base}/api/acute-medications/${path}`, {method:'POST', headers:{'Content-Type':'application/json'}, cache:'no-store', body:JSON.stringify(body)});
  const value = await response.json();
  if (!response.ok) throw new Error(value.error || `Error ${response.status}`);
  return value as T;
}
const display = (v:unknown) => v == null ? 'No especificado en la fuente; requiere verificación profesional' : typeof v === 'object' ? JSON.stringify(v) : String(v);

export default function AcuteMedications() {
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
        const value = values[f.key]?.trim();
        if (!value) throw new Error(`${f.label}: dato obligatorio sin documentar.`);
        if (f.kind === 'number') {
          if (!/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?$/i.test(value) || !Number.isFinite(Number(value))) throw new Error(`${f.label}: introduce un número finito con punto decimal.`);
          inputs[f.key] = Number(value);
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
  const reportContent = outcome?.report?.sections.map(([heading,paragraphs],i) => <section key={i}><h3 className="font-bold mt-4">{heading}</h3>{paragraphs.map((text,j) => <p className="whitespace-pre-wrap break-words" key={j}>{text}</p>)}</section>);
  return <div className="space-y-5">
    <header><h1 className="text-2xl font-bold">Farmacología aguda</h1><p>CLINICALLY_PENDING · Apoyo aritmético sujeto a revisión profesional y protocolo local. Selecciona una indicación y una opción; las alternativas no se administran juntas por defecto.</p></header>
    <label className="block">Grupo farmacológico<select className="input" aria-label="Grupo farmacológico" value={group} onChange={e => {clear(); setGroup(e.target.value); setId(''); setValues({});}}><option value="">Selecciona grupo</option>{groups.map(([key,label]) => <option value={key} key={key}>{label}</option>)}</select></label>
    {group && <label className="block">Indicación y opción<select className="input" aria-label="Indicación y opción" value={id} onChange={e => {clear(); setId(e.target.value); setValues({});}}><option value="">Selecciona indicación y opción</option>{catalog?.regimens.filter(r => r.group === group).map(r => <option key={r.id} value={r.id}>{r.label} — {r.drug}</option>)}</select></label>}
    {regimen && <>
      <section className="card p-4" aria-label="Fuente y precauciones"><h2 className="font-bold">{regimen.drug} · {regimen.route} · {regimen.dose_unit}</h2><ul>{regimen.limitations.map(t => <li key={t}>{t}</li>)}</ul><details><summary>Fuente canónica completa y advertencias</summary><p className="whitespace-pre-wrap">{regimen.source.preamble}</p><p className="whitespace-pre-wrap">{regimen.source.body}</p></details></section>
      <form onSubmit={calculate} className="card p-4 space-y-3" aria-label="Datos farmacológicos">
        {regimen.fields.map(f => <label className="block" key={f.key}>{f.label}{f.kind === 'number' ? <input className="input" aria-label={f.label} data-field={f.key} inputMode="decimal" value={values[f.key] || ''} onChange={e => {clear(); setValues(v => ({...v,[f.key]:e.target.value}));}} /> : <select className="input" aria-label={f.label} data-field={f.key} value={values[f.key] || ''} onChange={e => {clear(); setValues(v => ({...v,[f.key]:e.target.value}));}}><option value="">Sin documentar</option>{(f.kind === 'boolean' ? ['yes','no'] : f.options || []).map(v => <option key={v} value={v}>{v === 'yes' ? 'Sí' : v === 'no' ? 'No' : v}</option>)}</select>}</label>)}
        <button type="submit" className="btn-primary" disabled={busy}>Comprobar y calcular</button>
      </form>
    </>}
    {error && <p role="alert" className="text-danger">{error}</p>}
    {outcome && <section className="card p-4 space-y-3" aria-label="Resultado farmacológico">
      <h2 className="text-xl font-bold">{outcome.blocked ? 'Cálculo bloqueado' : 'Resultado aritmético — requiere revisión clínica'}</h2>
      {outcome.alerts.map(a => <p role="alert" key={a.code}>STOP: {a.message}</p>)}
      {outcome.result && <>
        <dl className="grid gap-3 sm:grid-cols-2">{Object.entries({indication:'Indicación', drug:'Fármaco', route:'Vía', dose:'Dosis', dose_unit:'Unidad de dosis', components:'Componentes y secuencia (no intercambiables)', correction_ceiling_mmol_l:'Límite acumulado de corrección de Na (mmol/L; no objetivo)', concentration:'Concentración y función', withdrawal_ml:'Volumen extraído del producto (mL)', administration_volume_ml:'Volumen de administración (mL)', pump_ml_h:'Velocidad de bomba (mL/h)', duration_min:'Duración (min)', amount_per_hour:'Cantidad por hora', amount_per_hour_unit:'Unidad por hora', maximum:'Máximo', preparation:'Preparación / dilución', compatibility:'Compatibilidad', stability:'Estabilidad', administration:'Administración', limitations:'Datos ausentes / límites'}).map(([key,label]) => <div key={key}><dt className="font-bold">{label}</dt><dd data-result={key}>{display(outcome.result?.[key])}</dd></div>)}</dl>
        <p className="whitespace-pre-wrap" data-testid="acute-warnings">{display(outcome.result.monitoring_and_warnings)}</p>
        <label className="block"><input type="checkbox" checked={confirmed} onChange={e => {revision.current++; setConfirmed(e.target.checked); setBusy(false);}} /> Confirmo haber revisado el resultado completo, sus límites y advertencias</label>
        <div className="flex flex-wrap gap-2">{(['json','pdf','docx'] as const).map(f => <button key={f} className="btn-ghost" disabled={!confirmed || busy} onClick={() => download(f)}>Exportar {f.toUpperCase()}</button>)}<button className="btn-ghost" disabled={!confirmed} onClick={() => window.print()}>Imprimir resultado</button></div>
        <details><summary>Contenido íntegro de la exportación</summary><div data-testid="acute-export-content">{reportContent}</div></details>
      </>}
    </section>}
    {confirmed && outcome?.report && createPortal(<article className="acute-print-sheet" aria-hidden="true">{reportContent}</article>, document.body)}
  </div>;
}
