import { useState, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { MODES, PROTOCOL, simulate, type Mode, type Simulation, type Values } from '../insulin/protocol';

type Field={key:string;label:string;options?:[string,string][]};
const yesNo:[string,string][]=[['yes','Sí'],['no','No']];
const glucose:Field={key:'glucose',label:'Glucemia actual (mg/dL)'};
const fields:Record<Mode,Field[]>={
 'iv-start':[glucose,{key:'persistent',label:'Hiperglucemia persistente confirmada',options:yesNo}],
 'iv-adjust':[glucose,{key:'previous',label:'Glucemia previa (mg/dL)'},{key:'rate',label:'Ritmo previo (UI/h)'},{key:'minutes',label:'Minutos entre controles'},
  {key:'reduction',label:'Reducción prescrita (UI/h)',options:[['1','1 UI/h'],['2','2 UI/h']]}],
 'iv-restart':[glucose,{key:'rate',label:'Ritmo previo a la pausa (UI/h)'},{key:'pauseReason',label:'Motivo de la pausa',options:[['preventive','Pausa preventiva por glucemia 70–100 mg/dL'],['hypoglycemia','Hipoglucemia <70 mg/dL'],['other','Otra interrupción']]}],
 'sc-transition':[{key:'meanRate',label:'Ritmo medio IV (UI/h)'},{key:'hours',label:'Horas estables evaluadas'},
  {key:'stable',label:'Estabilidad clínica y hemodinámica',options:yesNo},{key:'nutrition',label:'Nutrición estable',options:yesNo}],
 'iv-bolus':[glucose,{key:'indication',label:'Indicación médica del bolo',options:[['critical-hyperglycemia','Hiperglucemia persistente en paciente crítico'],['severe-unresponsive','Hiperglucemia grave o falta de respuesta, valoradas por el médico'],['dka','CAD: circuito específico'],['hhs','EHH: circuito específico']]},
  {key:'prescribed',label:'Existe prescripción médica explícita',options:yesNo},{key:'bolusUnits',label:'Dosis de bolo prescrita (UI)'}],
};
const rows=[['<70','Suspender; glucosa IV 10–20 g; controles cada 15 min'],['70–100','Pausa; control en 30–60 min'],['101–139','Reducir 1 o 2 UI/h según prescripción explícita'],['140–180','Mantener ritmo'],['181–210','Aumentar 1 UI/h'],['211–240','Aumentar 2 UI/h'],['>240','Aumentar 3 UI/h; bolo sólo con prescripción']];
const fmt=(n:number)=>new Intl.NumberFormat('es',{maximumFractionDigits:2}).format(n);
const range=(r:[number,number])=>r[0]===r[1]?fmt(r[0]):`${fmt(r[0])}–${fmt(r[1])}`;
export default function InsulinUci(){
 const [mode,setMode]=useState<Mode>('iv-adjust');const [values,setValues]=useState<Values>({});
 const [synthetic,setSynthetic]=useState(false);const [result,setResult]=useState<Simulation>();const [error,setError]=useState('');
 function clear(){setResult(undefined);setError('');}
 function reset(){clear();setValues({});setSynthetic(false);}
 function submit(e:FormEvent){e.preventDefault();clear();if(!synthetic)return;try{setResult(simulate(mode,values));}catch(e){setError(e instanceof Error?e.message:String(e));}}
 const selected=MODES.find(m=>m.id===mode)!;
 return <div className="space-y-6">
  <header className="card p-5 sm:p-7"><p className="section-title">Metabolismo · UCI adulto</p>
   <h1 className="mt-2 text-2xl font-bold sm:text-3xl">Insulinoterapia UCI</h1>
   <p className="mt-2 text-muted">Protocolo local seleccionado · Marco clínico ADA 2026</p>
   <p className="mt-3 font-semibold text-danger">Simulación técnica · CLINICALLY_PENDING · No usar con pacientes</p>
  </header>
  <section aria-label="Ámbito y estado clínico" className="rounded-2xl border border-warning/50 bg-warning/10 p-4 space-y-2">
   <h2 className="font-bold">Protocolo local en verificación técnica</h2>
   <p>La tabla ha sido elegida por el propietario. La revisión clínica y de Farmacia fue comunicada el 13/11/2026. Esto no equivale a validación prospectiva del programa.</p>
   <p>Excluye pediatría, CAD/EHH e hiperpotasemia. Para crisis hiperglucémicas: <Link className="underline" to="/acute-medications">farmacología aguda</Link>.</p>
  </section>
  <nav aria-label="Recorridos de insulinoterapia" className="grid gap-2 grid-cols-2 sm:grid-cols-3 lg:grid-cols-5">
   {MODES.map(m=><button type="button" key={m.id} aria-pressed={mode===m.id} className={mode===m.id?'btn-primary':'btn-ghost'} onClick={()=>{reset();setMode(m.id);}}>{m.title}</button>)}
  </nav>
  <div className="grid items-start gap-5 lg:grid-cols-2">
   <form onSubmit={submit} className="card p-5 space-y-4" aria-label="Formulario de simulación">
    <h2 className="text-xl font-bold">{selected.title}</h2>
    <p className="text-sm text-muted">Sólo datos ficticios. Coma o punto decimal. Cualquier edición borra el resultado anterior.</p>
    {mode==='iv-adjust'&&<p>Selecciona una reducción sólo cuando corresponda a la banda 101–139 mg/dL. El programa no decide entre 1 y 2 UI/h.</p>}
    {mode==='iv-start'&&<p>Se comprueban los criterios; no se inventa un ritmo inicial. El bolo se trata por separado.</p>}
    {mode==='iv-bolus'&&<p>Conversión de una dosis ya prescrita. Una glucemia elevada o el aporte calórico no generan por sí solos una orden de bolo.</p>}
    {fields[mode].map(f=><label className="block" key={f.key}><span className="block mb-1 font-semibold">{f.label}</span>
     {f.options?<select className="input" aria-label={f.label} value={values[f.key]??''} onChange={e=>{clear();setValues(old=>({...old,[f.key]:e.target.value}));}}>
      <option value="">Sin documentar</option>{f.options.map(([value,label])=><option key={value} value={value}>{label}</option>)}
     </select>:<input className="input" aria-label={f.label} inputMode="decimal" autoComplete="off" value={values[f.key]??''} onChange={e=>{clear();setValues(old=>({...old,[f.key]:e.target.value}));}}/>}
    </label>)}
    <label className="flex items-start gap-2"><input type="checkbox" checked={synthetic} className="mt-1" onChange={e=>{clear();setSynthetic(e.target.checked);}}/>
     <span>Usaré exclusivamente datos sintéticos para comprobar el programa; no genera una prescripción.</span></label>
    <div className="flex flex-wrap gap-2"><button type="submit" className="btn-primary" disabled={!synthetic}>Simular cálculo</button><button type="button" className="btn-ghost" onClick={reset}>Borrar datos</button></div>
    {error&&<p role="alert" className="text-danger">{error}</p>}
   </form>
   <div className="space-y-4">
    {result&&<section className="card p-5 space-y-3" aria-label="Resultado de simulación" aria-live="polite">
     <p className="font-bold text-danger">NO ADMINISTRABLE · CLINICALLY_PENDING</p>
     <h2 className="text-xl font-bold">{result.blockedReason?'Decisión pendiente':'Resultado del protocolo local'}</h2>
     {result.blockedReason&&<p role="alert">{result.blockedReason}</p>}
     {result.candidateRate!==undefined&&<div className="rounded-xl bg-surface-2 p-4"><p>Ritmo calculado para revisión</p>
      <p className="text-3xl font-bold" data-testid="candidate-rate">{fmt(result.candidateRate)} UI/h</p>
      <p>A {PROTOCOL.concentration} UI/mL: {fmt(result.pumpMlH!)} mL/h.</p>
     </div>}
     {result.trendMgDlH!==undefined&&<p>Tendencia: <strong>{fmt(result.trendMgDlH)} mg/dL/h</strong> (negativo = descenso).</p>}
     {result.controlMinutes&&<p>Control según la regla local: {range(result.controlMinutes)} minutos.</p>}
     {result.glucoseGrams&&<p>Intervalo de glucosa IV: {range(result.glucoseGrams)} g. Requiere selección de dosis y producto.</p>}
     {result.dailyIvUnits!==undefined&&<p>Extrapolación IV a 24 horas: {fmt(result.dailyIvUnits)} UI/día.</p>}
     {result.dailyScRange&&<p>Intervalo SC al 60–80%: <strong>{range(result.dailyScRange)} UI/día</strong>.</p>}
     {result.basalRange&&<p>Componente basal al 50%: {range(result.basalRange)} UI/día. No es una pauta final.</p>}
     {result.bolusUnits!==undefined&&<p data-testid="bolus-volume">Conversión del bolo prescrito: <strong>{fmt(result.bolusUnits)} UI = {fmt(result.bolusMl!)} mL</strong>. Sin velocidad de administración calculada.</p>}
     <ul className="list-disc pl-5 space-y-2">{result.notes.map(n=><li key={n}>{n}</li>)}</ul>
    </section>}
    <section className="card p-5 space-y-2" aria-label="Preparación seleccionada"><h2 className="font-bold">Preparación seleccionada</h2>
     <p>{PROTOCOL.totalUnits} UI de insulina humana regular hasta {PROTOCOL.finalVolumeMl} mL finales con NaCl 0,9%: <strong>1 UI/mL</strong>.</p>
     <p>Con vial U-100: 1 mL de insulina + 99 mL de SF. Cebado elegido: 20 mL antes de conectar, nunca al paciente.</p>
     <p>Recambio elegido: 24 h bajo condiciones documentadas de producto, envase y asepsia; no es garantía microbiológica universal.</p>
    </section>
    <section className="card p-5 space-y-2" aria-label="Procedencia del protocolo"><h2 className="font-bold">Procedencia</h2>
     <p>Algoritmo local seleccionado por el propietario. Sus incrementos y reglas de reinicio no se atribuyen a ADA.</p>
     <a className="underline" href={PROTOCOL.guideline} target="_blank" rel="noopener noreferrer">ADA 2026 · marco clínico</a>
     <p className="text-sm text-muted">No se guardan ni se envían a servidores los valores de estos formularios. Sin habilitación de contratos clínicos existentes.</p>
    </section>
   </div>
  </div>
  <details className="card p-5"><summary className="font-bold">Tabla local de ajuste seleccionada</summary><div className="overflow-x-auto mt-3"><table className="w-full text-left">
   <caption className="text-left mb-2">Concentración 1 UI/mL · hiperglucemia del adulto crítico</caption>
   <thead><tr><th scope="col" className="p-2">Glucemia (mg/dL)</th><th scope="col" className="p-2">Acción local</th></tr></thead>
   <tbody>{rows.map(([band,action])=><tr key={band} className="border-t border-border"><th scope="row" className="p-2 font-normal">{band}</th><td className="p-2">{action}</td></tr>)}</tbody>
  </table></div></details>
 </div>;
}
