import { useEffect, useRef, useState, type FormEvent } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useSearchParams } from 'react-router-dom';
import ClinicalValue from '../components/ClinicalValue';
import { localRevisionHeaders } from '../lib/individualTransport';

import ScoreDocumentInput from '../components/ScoreDocumentInput';
import type { Field } from '../lib/score-document';

type Score = {id:string;name:string;use:string;measures:string;version:string;execution_note?:string;source_url:string;fields:Field[]};
type Catalog = {revision:string;scores:Score[];total_scales:number;total_formulas:number;evidence:{status:string}};
type Response = {score_id:string;revision:string;result:Record<string,unknown>;clinical_status:string};
class ScoreServiceError extends Error {}
const base = (import.meta.env.VITE_CLINICAL_NOTE_API_BASE ?? '').replace(/\/$/,'');
async function post<T>(path:string, body:unknown, signal?:AbortSignal):Promise<T> {
  try {
    const response = await fetch(`${base}/api/clinical-scores/${path}`, {method:'POST',headers:{'Content-Type':'application/json',...localRevisionHeaders()},body:JSON.stringify(body),signal,cache:'no-store'});
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || `HTTP ${response.status}`);
    return data;
  } catch (error) { throw new ScoreServiceError(error instanceof Error ? error.message : String(error)); }
}

export default function ClinicalScores() {
  const { t, i18n } = useTranslation();
  const [params,setParams] = useSearchParams();
  const [catalog,setCatalog] = useState<Catalog>();
  const [values,setValues] = useState<Record<string,string>>({});
  const [result,setResult] = useState<Response>();
  const [error,setError] = useState('');
  const [sourceError,setSourceError] = useState(false);
  const [busy,setBusy] = useState(false);
  const [mode,setMode] = useState<'manual'|'document'>('manual');
  const [resetId,setResetId] = useState(0);
  const serial = useRef(0);
  const resultRef = useRef<HTMLElement>(null);
  const id = params.get('score') || 'news2';
  const score = catalog?.scores.find(s=>s.id===id);
  const clear = () => { setResetId(n=>n+1); serial.current++; setValues({}); setResult(undefined); setError(''); setBusy(false); };
  useEffect(()=>{
    const generation = serial;
    const controller = new AbortController();
    post<Catalog>('catalog',{},controller.signal).then(setCatalog).catch(e=>{if(!controller.signal.aborted){setSourceError(true);setError(String(e.message));}});
    return ()=>{controller.abort();generation.current++;};
  },[]);
  useEffect(()=>{serial.current++;setValues({});setResult(undefined);setError('');setBusy(false);},[id]);
  useEffect(()=>{if(result)resultRef.current?.focus();},[result]);
  function edit(key:string,value:string) {
    serial.current++;
    setValues(v=>({...v,[key]:value}));
    setResult(undefined);setError('');setBusy(false);
  }
  async function calculate(event:FormEvent) {
    event.preventDefault();
    if (!catalog || !score) return;
    const version = ++serial.current;
    setResult(undefined);setError('');
    try {
      const inputs:Record<string,string|number|boolean> = {};
      for (const f of score.fields) {
        const entry = values[f.key]?.trim() || '';
        const raw = f.type === 'number' ? entry.replace(',', '.') : entry;
        if (!raw) { if(f.optional)continue;throw new Error(`${f.label}: ${t('scores.fieldRequired')}`); }
        if (f.type==='choice') {
          const option=f.options?.find(o=>JSON.stringify(o.value)===raw);
          if(!option)throw new Error(`${f.label}: ${t('scores.invalidOption')}`);
          inputs[f.key]=option.value;
        } else {
          if(!/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?$/i.test(raw))throw new Error(`${f.label}: ${t('scores.invalidNumber')}`);
          const n=Number(raw);
          if(!Number.isFinite(n)||(f.integer&&!Number.isInteger(n))||(f.minimum!=null&&n<f.minimum)||(f.maximum!=null&&n>f.maximum))throw new Error(`${f.label}: ${t('scores.outOfRange')}`);
          inputs[f.key]=n;
        }
      }
      setBusy(true);
      const response=await post<Response>('calculate',{score_id:score.id,revision:catalog.revision,values:inputs});
      if(version!==serial.current)return;
      if(response.score_id!==score.id || response.revision!==catalog.revision)throw new Error(t('scores.wrongResult'));
      setResult(response);
    } catch(e) {if(version===serial.current){setSourceError(e instanceof ScoreServiceError);setError(e instanceof Error?e.message:String(e));}}
    finally {if(version===serial.current)setBusy(false);}
  }
  return <div className="space-y-5">
    <h1 className="text-2xl font-bold">{t('scores.title')}</h1>
    <p>{t('scores.scope')}</p>
    <p className="text-sm text-muted">{t('scores.sourceNotice')}</p>
    <Link className="underline" to="/clinical/clinical-scores-calculators">{t('scores.reference')}</Link>
    {error&&<div role="alert" className="card border-danger p-4 text-danger">{sourceError ? <><p>{t('scores.serviceError')}</p><details><summary>{t('scores.serviceDetails')}</summary><p lang="en">{error}</p></details></> : error}</div>}
    {!catalog&&!error&&<p role="status">{t('scores.loading')}</p>}
    {catalog&&<>
      <p>{t('scores.summary',{forms:catalog.scores.length,scales:catalog.total_scales,formulas:catalog.total_formulas,status:catalog.evidence.status.toUpperCase()})}</p>
      <label className="block">{t('scores.score')}<select className="input mt-1" value={id} onChange={e=>{clear();setParams({score:e.target.value});}}>{catalog.scores.map(s=><option key={s.id} value={s.id} lang="es">{s.name}</option>)}</select></label>
      {!score?<p role="alert">{t('scores.unavailable')}</p>:<>
        <section className="card p-4 space-y-2" lang="es"><h2 className="text-xl font-bold">{score.name}</h2><p>{score.measures}</p><p>{score.use}</p><p>{score.version}</p>{score.execution_note&&<p className="text-warn">{score.execution_note}</p>}<a className="underline" href={score.source_url} target="_blank" rel="noreferrer" lang={i18n.language}>{t('scores.source')}</a></section>
        <fieldset className="card p-4"><legend>{t('scores.entry')}</legend>
          {(['manual','document'] as const).map(m=><label key={m} className="mr-4"><input type="radio" name="entry" checked={mode===m} onChange={()=>{clear();setMode(m);}}/> {t(m==='manual'?'scores.manual':'scores.document')}</label>)}
        </fieldset>
        {mode==='document'&&<ScoreDocumentInput key={id+resetId} fields={score.fields} onPick={edit} onValues={v=>{serial.current++;setValues(v);setResult(undefined);setError('');setBusy(false);}}/>}
        <form noValidate onSubmit={e=>void calculate(e)} className="card p-4 space-y-4">
          <p>{t('scores.instructions')}</p>
          <div className="grid gap-4 md:grid-cols-2">{score.fields.map(f=><label key={f.key} className="min-w-0"><span className="label" lang="es">{f.label}{f.unit?` (${f.unit})`:''}</span>
            {f.type==='choice'?<select data-field={f.key} className="input" value={values[f.key]||''} onChange={e=>edit(f.key,e.target.value)}><option value="">{t('scores.unrecorded')}</option>{f.options?.map((o,i)=><option key={i} value={JSON.stringify(o.value)} lang="es">{o.label}</option>)}</select>:<input data-field={f.key} className="input" inputMode="decimal" value={values[f.key]||''} onChange={e=>edit(f.key,e.target.value)}/>}
            <span className="text-xs text-muted">{t(f.optional?'scores.optional':'scores.required')}{f.type==='number'?` · ${t(f.integer?'scores.integer':'scores.finite')}${f.minimum!=null?` ≥ ${f.minimum}`:''}${f.maximum!=null?` ≤ ${f.maximum}`:''}`:''}</span>
          </label>)}</div>
          <div className="flex gap-2"><button className="btn-primary" disabled={busy} type="submit">{t(busy?'scores.calculating':id==='grace-2'?'scores.validateGrace':'scores.calculate')}</button><button className="btn-ghost" type="button" onClick={clear}>{t('scores.reset')}</button></div>
        </form>
        {result&&<section ref={resultRef} tabIndex={-1} aria-label={t('scores.result')} aria-live="polite" className="card p-4 space-y-3">
          <h2 className="text-xl font-bold">{t('scores.result')}</h2>
          {result.result.total!=null&&<p className="text-3xl font-bold">{t('scores.points',{value:String(result.result.total)})}</p>}
          {typeof result.result.official_calculator==='string'&&<a className="btn-primary" href={result.result.official_calculator} target="_blank" rel="noreferrer">{t('scores.officialGrace')}</a>}
          <ClinicalValue value={result.result} sourceLanguage="es"/>
          <p>{result.clinical_status}</p>
        </section>}
      </>}
    </>}
  </div>;
}
