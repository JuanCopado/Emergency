import { useEffect, useRef, useState, type FormEvent } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import ClinicalValue from '../components/ClinicalValue';

type Field = {key:string;label:string;type:'number'|'choice';unit?:string;minimum?:number|null;maximum?:number|null;integer?:boolean;optional:boolean;options?:{value:string|number|boolean;label:string}[]};
type Score = {id:string;name:string;use:string;measures:string;version:string;execution_note?:string;source_url:string;fields:Field[]};
type Catalog = {revision:string;scores:Score[];total_scales:number;total_formulas:number;evidence:{status:string}};
type Response = {score_id:string;revision:string;result:Record<string,unknown>;clinical_status:string};
const base = (import.meta.env.VITE_CLINICAL_NOTE_API_BASE ?? '').replace(/\/$/,'');
async function post<T>(path:string, body:unknown, signal?:AbortSignal):Promise<T> {
  const response = await fetch(`${base}/api/clinical-scores/${path}`, {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body),signal,cache:'no-store'});
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || `Error ${response.status}`);
  return data;
}

export default function ClinicalScores() {
  const [params,setParams] = useSearchParams();
  const [catalog,setCatalog] = useState<Catalog>();
  const [values,setValues] = useState<Record<string,string>>({});
  const [result,setResult] = useState<Response>();
  const [error,setError] = useState('');
  const [busy,setBusy] = useState(false);
  const serial = useRef(0);
  const resultRef = useRef<HTMLElement>(null);
  const id = params.get('score') || 'news2';
  const score = catalog?.scores.find(s=>s.id===id);
  const clear = () => { serial.current++; setValues({}); setResult(undefined); setError(''); setBusy(false); };
  useEffect(()=>{
    const generation = serial;
    const controller = new AbortController();
    post<Catalog>('catalog',{},controller.signal).then(setCatalog).catch(e=>{if(!controller.signal.aborted)setError(String(e.message));});
    return ()=>{controller.abort();generation.current++;};
  },[]);
  useEffect(()=>{serial.current++;setValues({});setResult(undefined);setError('');setBusy(false);},[id]);
  useEffect(()=>{if(result)resultRef.current?.focus();},[result]);
  async function calculate(event:FormEvent) {
    event.preventDefault();
    if (!catalog || !score) return;
    const version = ++serial.current;
    setResult(undefined);setError('');
    try {
      const inputs:Record<string,string|number|boolean> = {};
      for (const f of score.fields) {
        const raw = values[f.key]?.trim() || '';
        if (!raw) { if(f.optional)continue;throw new Error(`${f.label}: campo requerido`); }
        if (f.type==='choice') {
          const option=f.options?.find(o=>JSON.stringify(o.value)===raw);
          if(!option)throw new Error(`${f.label}: valor no permitido`);
          inputs[f.key]=option.value;
        } else {
          if(!/^[+-]?(?:\d+\.?\d*|\.\d+)(?:e[+-]?\d+)?$/i.test(raw))throw new Error(`${f.label}: número no válido`);
          const n=Number(raw);
          if(!Number.isFinite(n)||(f.integer&&!Number.isInteger(n))||(f.minimum!=null&&n<f.minimum)||(f.maximum!=null&&n>f.maximum))throw new Error(`${f.label}: número fuera de rango`);
          inputs[f.key]=n;
        }
      }
      setBusy(true);
      const response=await post<Response>('calculate',{score_id:score.id,revision:catalog.revision,values:inputs});
      if(version!==serial.current)return;
      if(response.score_id!==score.id || response.revision!==catalog.revision)throw new Error('El resultado no corresponde al formulario actual. Recargue antes de calcular.');
      setResult(response);
    } catch(e) {if(version===serial.current)setError(e instanceof Error?e.message:String(e));}
    finally {if(version===serial.current)setBusy(false);}
  }
  return <div className="space-y-5">
    <h1 className="text-2xl font-bold">Scores clínicos</h1>
    <p>CLINICALLY_PENDING · apoyo al juicio clínico, no validación clínica prospectiva.</p>
    <Link className="underline" to="/clinical/clinical-scores-calculators">Referencia canónica y limitaciones</Link>
    {error&&<p role="alert" className="card border-danger p-4 text-danger">{error}</p>}
    {!catalog&&!error&&<p role="status">Cargando formularios…</p>}
    {catalog&&<>
      <p>{catalog.scores.length} formularios · {catalog.total_scales} escalas y {catalog.total_formulas} fórmulas en el registro. Evidencia: {catalog.evidence.status.toUpperCase()}.</p>
      <label className="block">Score<select className="input mt-1" value={id} onChange={e=>{clear();setParams({score:e.target.value});}}>{catalog.scores.map(s=><option key={s.id} value={s.id}>{s.name}</option>)}</select></label>
      {!score?<p role="alert">Score no disponible en este formulario.</p>:<>
        <section className="card p-4 space-y-2"><h2 className="text-xl font-bold">{score.name}</h2><p>{score.measures}</p><p>{score.use}</p><p>{score.version}</p>{score.execution_note&&<p className="text-warn">{score.execution_note}</p>}<a className="underline" href={score.source_url} target="_blank" rel="noreferrer">Fuente canónica</a></section>
        <form noValidate onSubmit={e=>void calculate(e)} className="card p-4 space-y-4">
          <p>Complete los datos observados. Sin selección significa no registrado; no se asume normalidad.</p>
          <div className="grid gap-4 md:grid-cols-2">{score.fields.map(f=><label key={f.key} className="min-w-0"><span className="label">{f.label}{f.unit?` (${f.unit})`:''}</span>
            {f.type==='choice'?<select data-field={f.key} className="input" value={values[f.key]||''} onChange={e=>{serial.current++;setValues(v=>({...v,[f.key]:e.target.value}));setResult(undefined);setError('');setBusy(false);}}><option value="">Sin registrar</option>{f.options?.map((o,i)=><option key={i} value={JSON.stringify(o.value)}>{o.label}</option>)}</select>:<input data-field={f.key} className="input" inputMode="decimal" value={values[f.key]||''} onChange={e=>{serial.current++;setValues(v=>({...v,[f.key]:e.target.value}));setResult(undefined);setError('');setBusy(false);}}/>}
            <span className="text-xs text-muted">{f.optional?'Opcional':'Requerido'}{f.type==='number'?` · ${f.integer?'Entero':'Número finito'}${f.minimum!=null?` ≥ ${f.minimum}`:''}${f.maximum!=null?` ≤ ${f.maximum}`:''}`:''}</span>
          </label>)}</div>
          <div className="flex gap-2"><button className="btn-primary" disabled={busy} type="submit">{busy?'Calculando…':id==='grace-2'?'Validar y abrir GRACE oficial':'Calcular'}</button><button className="btn-ghost" type="button" onClick={clear}>Reiniciar</button></div>
        </form>
        {result&&<section ref={resultRef} tabIndex={-1} aria-label="Resultado del score" aria-live="polite" className="card p-4 space-y-3">
          <h2 className="text-xl font-bold">Resultado e interpretación</h2>
          {result.result.total!=null&&<p className="text-3xl font-bold">{String(result.result.total)} puntos</p>}
          {typeof result.result.official_calculator==='string'&&<a className="btn-primary" href={result.result.official_calculator} target="_blank" rel="noreferrer">Abrir calculador oficial GRACE</a>}
          <ClinicalValue value={result.result}/>
          <p>{result.clinical_status}</p>
        </section>}
      </>}
    </>}
  </div>;
}
