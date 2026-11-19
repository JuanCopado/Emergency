import { useEffect, useRef, useState, type PointerEvent } from 'react';
import { Link } from 'react-router-dom';

type Box = [number, number, number, number];
type Field = {name:string; raw:string; number:string; unit:string; review:string; origin:string;
  legibility:string; warning?:string; bbox:Box|null; crop?:string; confidence:number|null;
  visual_check:string; visualReviewed?:boolean; transcribed?:boolean; correction_reason?:string; fio2_attestation?:[string,string]};
type SourceMetadata = {label:string;value:string;scope?:string;kind?:string;raw?:string;page?:number;
  line?:number;source_layer?:string;type_discrepancy?:boolean;source_sample_label?:string|null;normalized_sample_type?:string|null};
type Metadata = SourceMetadata & {review:string;reason:string;applies_to_sample?:boolean;resolved_sample_type?:string};
type ReviewResult = Record<string,unknown> & {fio2_trace?:{normalized_fraction:number;used_fraction:number|null}};
function typeDecision(m:Metadata, original:SourceMetadata, sample:string) {
  return original.kind==='sample_type' && m.review==='confirmed' &&
    (original.scope!=='unassigned' || m.applies_to_sample===true) &&
    (!original.normalized_sample_type || original.normalized_sample_type!==sample || m.value!==original.value || original.type_discrepancy===true);
}
function fio2Fraction(f:Field) {
  if (!/^[+-]?\d+(?:[.,]\d+)?$/.test(f.number) || !['%','fraction','fracción','fraccion'].includes(f.unit)) return null;
  const value=Number(f.number.replace(',','.'));
  return Number.isFinite(value) ? (f.unit==='%' ? value/100 : value) : null;
}
function fio2Admissible(f:Field) {
  if (fio2Fraction(f)===null) return false;
  // Compare the decimal input exactly so rounding cannot admit a value outside a boundary.
  const [whole,decimals='']=f.number.replace(',','.').split('.');
  const scale=BigInt(10)**BigInt(decimals.length);
  const digits=BigInt(whole!+decimals);
  return f.unit==='%' ? digits>=BigInt(21)*scale && digits<=BigInt(100)*scale
    : BigInt(100)*digits>=BigInt(21)*scale && digits<=scale;
}

type Page = {fields:Field[]; preview:string; source_page:number; sample_label:string|null;
  width:number; height:number; region:Box; blocked:boolean; warning:string; method:string;
  orientation:number; metadata:SourceMetadata[]; visual_extras:{raw:string}[]};
type Document = {ticket:string; pages:Page[]};
type Region = {page:number; bbox:Box; label:string};
const needsTranscription=(field:Field)=>
  ['low_confidence','location_unverified','unit_unreadable'].includes(field.legibility) ||
  ['discrepancy','visual_only'].includes(field.visual_check);

export default function BloodGas() {
  const [doc,setDoc] = useState<Document|null>(null);
  const [index,setIndex] = useState(0);
  const [rows,setRows] = useState<Field[]>([]);
  const [metadata,setMetadata] = useState<Metadata[]>([]);
  const [sample,setSample] = useState('');
  const [synthetic,setSynthetic] = useState(false);
  const [one,setOne] = useState(false);
  const [medical,setMedical] = useState(false);
  const [area,setArea] = useState(false);
  const [busy,setBusy] = useState(false);
  const [error,setError] = useState('');
  const [sessionError,setSessionError] = useState('');
  const [extractionAvailable,setExtractionAvailable] = useState<boolean|null>(null);
  const [result,setResult] = useState<ReviewResult|null>(null);
  const [regions,setRegions] = useState<Region[]>([]);
  const [box,setBox] = useState<Box>([0,0,100,100]);
  const [focus,setFocus] = useState<number|null>(null);
  const [areaDirty,setAreaDirty] = useState(false);
  const revision = useRef(0);
  const token = useRef('');
  const drag = useRef<[number,number]|null>(null);
  const alive = useRef(true);
  const ticket = useRef<string|null>(null);
  const page = doc?.pages[index];

  useEffect(()=>{
    alive.current=true;
    void fetch('/api/blood-gas/session',{cache:'no-store'}).then(async response=>{
      if(!response.ok) throw Error('Servicio local de gasometrías no disponible.');
      const data: {token?:unknown;synthetic_only?:unknown;extraction_available?:unknown;required_platform?:unknown}=await response.json();
      if(!data || data.synthetic_only!==true || typeof data.token!=='string' || !data.token ||
         typeof data.extraction_available!=='boolean' || data.required_platform!=='win32')
        throw Error('El servicio local no comunica una capacidad de extracción verificable.');
      if(!alive.current) return;
      token.current=data.token;
      setExtractionAvailable(data.extraction_available);
      if(!data.extraction_available)
        setSessionError('La extracción de gasometrías requiere Windows. Esta sesión permite consultar la interfaz, pero no cargar documentos.');
    }).catch((error:unknown)=>{
      if(alive.current){
        setExtractionAvailable(false);
        setSessionError(error instanceof Error?error.message:'Servicio local de gasometrías no disponible.');
      }
    });
    return ()=>{
      alive.current=false;
      if(ticket.current && token.current) void fetch('/api/blood-gas/reject',{
        method:'POST',headers:{'X-Session':token.current,'Content-Type':'application/json'},body:JSON.stringify({ticket:ticket.current}),
        keepalive:true,
      }).catch(()=>{});
    };
  },[]);

  async function post<T,>(route:string, body:BodyInit):Promise<T> {
    if(!token.current) throw Error('Sesión local de gasometrías no disponible.');
    if((route==='/extract' || route==='/regions') && extractionAvailable!==true)
      throw Error('La extracción de gasometrías requiere Windows. No se ha enviado el documento.');
    const headers:Record<string,string>={'X-Session':token.current};
    if(route!=='/extract') headers['Content-Type']='application/json';
    const response=await fetch('/api/blood-gas'+route,{method:'POST',headers,body});
    if(!response.ok) throw Error('No se admite el documento o la revisión. Compruebe campos, unidades, muestra y confirmaciones.');
    return response.json() as Promise<T>;
  }
  function invalidate(){ revision.current++; setResult(null); setError(''); setOne(false); setMedical(false); setArea(false); }
  function select(next:Document, idx:number){
    invalidate(); setIndex(idx); setRows(next.pages[idx]!.fields.map(f=>({...f,review:'pending',visualReviewed:false,transcribed:false})));
    setMetadata(next.pages[idx]!.metadata.map(m=>({...m,review:'pending',reason:'',applies_to_sample:undefined})));
    setSample(''); setBox([...next.pages[idx]!.region]); setFocus(null); setAreaDirty(false);
  }
  function install(next:Document){ ticket.current=next.ticket; setDoc(next); select(next,0); }
  async function upload(file:File|undefined){
    if(!file || !synthetic) return;
    invalidate(); setDoc(null); setRows([]); setRegions([]); setBusy(true);
    const seq=revision.current;
    try { const next=await post<Document>('/extract',file); if(alive.current && seq===revision.current) install(next);
      else await post('/reject',JSON.stringify({ticket:next.ticket})); }
    catch(e){ if(alive.current && seq===revision.current) setError((e as Error).message); }
    finally { if(alive.current) setBusy(false); }
  }
  function edit(idx:number, changes:Partial<Field>, reset=false){
    invalidate(); setRows(old=>old.map((f,i)=>i===idx?{...f,...changes,
      ...(f.name==='FiO2' && changes.visualReviewed!==undefined
        ? {fio2_attestation:changes.visualReviewed?[f.number,f.unit] as [string,string]:undefined} : {}),
      ...(reset?{review:'pending',visualReviewed:false,transcribed:false,correction_reason:'',fio2_attestation:undefined}:{})}:f));
  }
  async function applyRegions(){
    if(!doc || !regions.length) return;
    invalidate(); setBusy(true); const seq=revision.current;
    try { const next=await post<Document>('/regions',JSON.stringify({ticket:doc.ticket,regions})); if(alive.current && seq===revision.current){ install(next);setRegions([]); }
      else await post('/reject',JSON.stringify({ticket:next.ticket})); }
    catch(e){ if(alive.current && seq===revision.current){setError((e as Error).message);setDoc(null);setRows([]);ticket.current=null;} }
    finally { if(alive.current) setBusy(false); }
  }
  async function reject(){
    const old=doc?.ticket; invalidate(); setDoc(null); setRows([]); setRegions([]); ticket.current=null;
    if(old){ setBusy(true); try{await post('/reject',JSON.stringify({ticket:old}));}catch(e){setError((e as Error).message);}finally{setBusy(false);} }
  }
  async function calculate(){
    if(!doc) return;
    setBusy(true); setResult(null); setError(''); const seq=++revision.current;
    try{
      const next=await post<ReviewResult>('/review',JSON.stringify({ticket:doc.ticket,page:index,rows,metadata,sample,oneSample:one,medicalConfirmed:medical,areaConfirmed:area}));
      if(alive.current && seq===revision.current) setResult(next);
    }catch(e){if(alive.current && seq===revision.current) setError((e as Error).message);}
    finally{if(alive.current) setBusy(false);}
  }
  function point(e:PointerEvent<SVGSVGElement>):[number,number]{
    const rect=e.currentTarget.getBoundingClientRect();
    return [Math.max(0,Math.min(page!.width,(e.clientX-rect.left)*page!.width/rect.width)),
      Math.max(0,Math.min(page!.height,(e.clientY-rect.top)*page!.height/rect.height))];
  }
  function changeSample(value:string) {
    invalidate(); setSample(value);
    setMetadata(old=>old.map(m=>m.kind==='sample_type'
      ? {...m,resolved_sample_type:undefined,reason:m.resolved_sample_type?'':m.reason} : m));
  }
  const fio2Edited=(f:Field,i:number)=>f.name==='FiO2' &&
    (f.number!==page!.fields[i]!.number || f.unit!==page!.fields[i]!.unit);
  const ready=!!sample && !!page && !page.blocked && !areaDirty && regions.length===0 && rows.length>0 && one && medical && area &&
    metadata.every((m,i)=>(m.value.trim() || m.kind==='sample_type' || m.review==='rejected') &&
      (m.review==='confirmed' || (m.review==='rejected' && m.reason.trim())) &&
      (m.scope!=='unassigned' || (typeof m.applies_to_sample==='boolean' && (m.applies_to_sample || m.reason.trim()))) &&
      (!typeDecision(m,page.metadata[i]!,sample) || (m.resolved_sample_type===sample && m.reason.trim()))) &&
    rows.every((f,i)=>f.review==='rejected' || (f.review==='confirmed' && f.visualReviewed &&
      (!needsTranscription(f) || f.transcribed) && (f.name!=='FiO2' ||
        (fio2Admissible(f) && (!fio2Edited(f,i) || f.correction_reason?.trim()))))) &&
    rows.some(f=>f.review==='confirmed');

  return <div className="space-y-5" lang="es">
    <header><Link to="/clinical-note" className="text-primary underline">Volver a la nota clínica</Link>
      <h1 className="mt-3 text-2xl font-bold">Revisión de gasometrías</h1>
      <p className="mt-2 text-muted">CLINICALLY_PENDING · Pruebas con datos sintéticos. Confirme cifras, unidades y muestra antes del cálculo.</p>
      <p className="text-sm text-muted">El procesamiento es local. El aislamiento de red del navegador completo sigue sin acreditarse. No cargue datos de pacientes.</p>
    </header>
    {extractionAvailable===null && <p role="status">Comprobando la disponibilidad de extracción local…</p>}
    {sessionError && <p role="alert" className="card border-amber-500 p-3">{sessionError}</p>}
    <fieldset disabled={busy} className="card space-y-3 p-4">
      <label className="flex gap-2"><input type="checkbox" checked={synthetic} onChange={e=>{setSynthetic(e.target.checked);if(!e.target.checked)void reject();}}/> Solo cargaré datos sintéticos</label>
      <label className="block">Documento sintético (PDF, PNG, JPEG, TIFF o WebP)
        <input className="mt-2 block w-full" aria-label="Documento sintético" type="file" accept=".pdf,.png,.jpg,.jpeg,.tif,.tiff,.webp" disabled={!synthetic || extractionAvailable!==true} onChange={e=>void upload(e.target.files?.[0])}/>
      </label>
    </fieldset>
    {busy && <p role="status">Procesando y cotejando las imágenes…</p>}
    {error && <p role="alert" className="card border-red-500 p-3">{error}</p>}
    {doc && page && <fieldset disabled={busy} className="space-y-4">
      <label className="block">Página / muestra
        <select className="input mt-1" aria-label="Página y muestra" value={index} onChange={e=>select(doc,Number(e.target.value))}>
          {doc.pages.map((p,i)=><option value={i} key={i}>Página {p.source_page} · {p.sample_label || 'sin identificar'} · {i+1}</option>)}
        </select>
      </label>
      {page.warning && <p role="alert">{page.warning}</p>}
      <div className="grid gap-5 lg:grid-cols-2">
        <section className="min-w-0 space-y-3" aria-label="Original y áreas">
          <p className="text-sm">Arrastre sobre el original para seleccionar una muestra, o introduzca las coordenadas debajo. Azul: área propuesta. Rojo: campo seleccionado.</p>
          <svg role="img" aria-label="Original con áreas de muestra" viewBox={`0 0 ${page.width} ${page.height}`} className="w-full touch-none border border-border bg-white"
            onPointerDown={e=>{drag.current=point(e);e.currentTarget.setPointerCapture(e.pointerId);invalidate();setAreaDirty(true);}}
            onPointerMove={e=>{if(drag.current){const p=point(e),a=drag.current;setBox([Math.min(a[0],p[0]),Math.min(a[1],p[1]),Math.max(a[0],p[0]),Math.max(a[1],p[1])]);}}}
            onPointerUp={()=>{drag.current=null;}} onPointerCancel={()=>{drag.current=null;}}>
            <image href={'data:image/png;base64,'+page.preview} width={page.width} height={page.height}/>
            <rect x={box[0]} y={box[1]} width={box[2]-box[0]} height={box[3]-box[1]} fill="none" stroke="#2563eb" strokeWidth={3}/>
            {focus!==null && rows[focus]?.bbox && <rect x={rows[focus].bbox![0]} y={rows[focus].bbox![1]} width={rows[focus].bbox![2]-rows[focus].bbox![0]} height={rows[focus].bbox![3]-rows[focus].bbox![1]} fill="none" stroke="#dc2626" strokeWidth={3}/>}
          </svg>
          <div className="grid grid-cols-2 gap-2">{['Izquierda','Arriba','Derecha','Abajo'].map((label,i)=><label key={label}>{label} (px)<input aria-label={label+' del área'} className="input" type="number" min="0" value={Math.round(box[i]!)} onChange={e=>{invalidate();setAreaDirty(true);setBox(old=>old.map((v,j)=>j===i?Number(e.target.value):v) as Box);}}/></label>)}</div>
          <button type="button" className="btn-ghost" disabled={regions.length>=16 || box[2]-box[0]<8 || box[3]-box[1]<8} onClick={()=>{invalidate();setAreaDirty(true);setRegions(old=>[...old,{page:page.source_page,bbox:[...box],label:'Área '+(old.length+1)}]);}}>Añadir área de muestra</button>
          <ul className="space-y-2">{regions.map((r,i)=><li key={i}>{r.label} · página {r.page} · {r.bbox.map(Math.round).join(', ')} <button type="button" className="underline" onClick={()=>{invalidate();setRegions(old=>old.filter((_,j)=>i!==j));}}>Quitar área {i+1}</button></li>)}</ul>
          <button type="button" className="btn-ghost" onClick={()=>{invalidate();setRegions([]);setBox([...page.region]);setAreaDirty(false);}}>Descartar selección de áreas</button>
          {areaDirty && <p role="status">Área pendiente: añádala y extraiga las áreas para revisar esta muestra, o descarte la selección.</p>}
          <button type="button" className="btn-primary" disabled={!regions.length} onClick={()=>void applyRegions()}>Extraer las áreas seleccionadas</button>
          <p className="text-xs text-muted">Coordenadas en píxeles del original renderizado, origen superior izquierdo, tras orientación EXIF. No se reconstruyen píxeles.</p>
        </section>
        <section className="min-w-0 space-y-3" aria-label="Campos y confirmación">
          <label className="block">Tipo de muestra<select aria-label="Tipo de muestra" className="input" value={sample} onChange={e=>changeSample(e.target.value)}><option value="">Seleccione la muestra</option>{['desconocida','arterial','venosa','capilar'].map(v=><option key={v}>{v}</option>)}</select></label>
          {metadata.length>0 && <section aria-label="Revisión de metadatos" className="space-y-3">
            <h2 className="font-bold">Metadatos de esta muestra</h2>
            <p className="text-sm">Coteje tipo, fecha, equipo y avisos extraídos. Una corrección conserva el texto original en el resultado.</p>
            {metadata.map((m,i)=><article key={i} className="card space-y-2 p-3">
              <p>Original: {m.raw ?? (page.metadata[i]!.label+': '+page.metadata[i]!.value)}</p>
              {m.type_discrepancy && <p>El tipo de muestra difiere entre el texto y la imagen del PDF.</p>}
              {m.kind==='sample_type' && <p>{m.source_layer==='visual_ocr'?'Imagen (OCR)':m.source_layer==='pdf_text'?'Texto del PDF':''} · Página {m.page} · Línea {m.line} · Muestra de origen: {m.source_sample_label || 'sin rótulo'}</p>}
              <label>{m.label}<input aria-label={'Metadato '+(i+1)+' valor'} className="input" value={m.value} maxLength={512}
                onChange={e=>{invalidate();setMetadata(old=>old.map((v,j)=>i===j?{...v,value:e.target.value,review:'pending',applies_to_sample:undefined,resolved_sample_type:undefined,reason:''}:v));}}/></label>
              {m.scope==='unassigned' && <label>Cabecera sin muestra asignada: ¿aplica a esta muestra?
                <select aria-label={'Ámbito de metadato '+(i+1)} className="input" value={m.applies_to_sample===undefined?'':m.applies_to_sample?'yes':'no'}
                  onChange={e=>{invalidate();setMetadata(old=>old.map((v,j)=>i===j?{...v,applies_to_sample:e.target.value===''?undefined:e.target.value==='yes',resolved_sample_type:undefined,reason:''}:v));}}>
                  <option value="">Decisión pendiente</option><option value="yes">Sí, aplica a esta muestra</option><option value="no">No aplica a esta muestra</option>
                </select></label>}
              <label>Revisión<select aria-label={'Revisión de metadato '+(i+1)} className="input" value={m.review}
                onChange={e=>{invalidate();setMetadata(old=>old.map((v,j)=>i===j?{...v,review:e.target.value,resolved_sample_type:undefined,reason:''}:v));}}>
                <option value="pending">Pendiente</option><option value="confirmed">Verificado</option><option value="rejected">Rechazado</option>
              </select></label>
              {typeDecision(m,page.metadata[i]!,sample) && <label className="flex gap-2">
                <input aria-label={'Resolver tipo de muestra '+(i+1)} type="checkbox" disabled={!sample}
                  checked={!!sample && m.resolved_sample_type===sample} onChange={e=>{invalidate();setMetadata(old=>old.map((v,j)=>i===j?
                    {...v,resolved_sample_type:e.target.checked?sample:undefined,reason:''}:v));}}/>
                He cotejado el tipo declarado y confirmo la selección manual {sample || 'pendiente'}
              </label>}
              {(m.review==='rejected' || (m.scope==='unassigned' && m.applies_to_sample===false) ||
                typeDecision(m,page.metadata[i]!,sample)) && <label>Motivo de la decisión<input className="input" aria-label={'Motivo de metadato '+(i+1)} value={m.reason} maxLength={512}
                onChange={e=>{invalidate();setMetadata(old=>old.map((v,j)=>i===j?{...v,reason:e.target.value}:v));}}/></label>}
            </article>)}
          </section>}
          {rows.map((f,i)=><article className="card space-y-2 p-3" key={i}>
            <button type="button" className="font-bold underline" onClick={()=>setFocus(i)}>Localizar {f.name}</button>
            <p className="text-sm">Lectura literal: {f.raw} · Origen: {f.origin} · Cotejo: {f.visual_check}</p>
            {f.warning && <p className="text-sm" role="note">{f.warning}</p>}
            {f.crop ? <img src={'data:image/png;base64,'+f.crop} alt={'Recorte original de '+f.name} className="max-h-28 max-w-full bg-white"/>:<p>Sin localización fiable; transcriba desde el original o rechace.</p>}
            <div className="grid grid-cols-2 gap-2"><label>Cifra<input aria-label={f.name+' cifra'} className="input" value={f.number} onChange={e=>edit(i,{number:e.target.value},true)}/></label><label>Unidad<input aria-label={f.name+' unidad'} className="input" value={f.unit} onChange={e=>edit(i,{unit:e.target.value},true)}/></label></div>
            {f.name==='FiO2' && <div>
              <p>FiO₂ original: {page.fields[i]!.number} {page.fields[i]!.unit || '(sin unidad)'}</p>
              <p>Fracción según la unidad revisada: {fio2Fraction(f) ?? 'pendiente de cifra y unidad explícitas (% o fracción)'}</p>
              {!fio2Admissible(f) && f.review!=='rejected' && <p role="alert">FiO₂ no admisible. Confirme 21–100 % o fracción 0,21–1 frente al original.</p>}
              {fio2Edited(f,i) && <label>Motivo de la corrección de FiO₂<input className="input" value={f.correction_reason ?? ''}
                maxLength={512} onChange={e=>edit(i,{correction_reason:e.target.value,review:'pending'})}/></label>}
            </div>}
            {needsTranscription(f) && <label className="flex gap-2"><input aria-label={'Transcripción manual de '+f.name} type="checkbox" checked={!!f.transcribed} onChange={e=>edit(i,{transcribed:e.target.checked,review:'pending'})}/> He transcrito la cifra y unidad desde el original</label>}
            <label className="flex gap-2"><input aria-label={'Cotejo visual de '+f.name} type="checkbox" checked={!!f.visualReviewed} onChange={e=>edit(i,{visualReviewed:e.target.checked,review:'pending'})}/> He cotejado el campo con el recorte y la página original</label>
            <label>Revisión de {f.name}<select aria-label={'Revisión de '+f.name} className="input" value={f.review} onChange={e=>edit(i,{review:e.target.value})}><option value="pending">Pendiente</option><option value="confirmed">Verificado</option><option value="rejected">Rechazado</option></select></label>
          </article>)}
          {!rows.length && <p>No hay campos con segmentación fiable. Seleccione las áreas de las muestras.</p>}
          <label className="flex gap-2"><input type="checkbox" checked={area} onChange={e=>{revision.current++;setResult(null);setArea(e.target.checked);}}/> He revisado el área completa, incluidos los parámetros que no se han extraído</label>
          <label className="flex gap-2"><input type="checkbox" checked={one} onChange={e=>{revision.current++;setResult(null);setOne(e.target.checked);}}/> Todos los campos aceptados pertenecen a una única muestra</label>
          <label className="flex gap-2"><input type="checkbox" checked={medical} onChange={e=>{revision.current++;setResult(null);setMedical(e.target.checked);}}/> Confirmo la revisión médica obligatoria antes del cálculo</label>
          <div className="flex flex-wrap gap-2"><button type="button" className="btn-primary" disabled={!ready} onClick={()=>void calculate()}>Interpretar valores confirmados</button><button type="button" className="btn-ghost" onClick={()=>void reject()}>Rechazar y borrar la extracción</button></div>
        </section>
      </div>
    </fieldset>}
    {result && <section aria-label="Resultado revisable" className="card space-y-2 p-4"><h2 className="text-lg font-bold">Resultado sobre valores confirmados</h2>
      <p>CLINICALLY_PENDING · Apoyo de cálculo; requiere interpretación médica.</p>
      {result.fio2_trace && <p>FiO₂ normalizada: {result.fio2_trace.normalized_fraction} · Fracción utilizada por el motor: {result.fio2_trace.used_fraction ?? 'no aplicada a esta muestra'}</p>}
      <dl>{Object.entries(result).filter(([,v])=>typeof v==='number'||typeof v==='string').map(([k,v])=><div key={k} className="flex flex-wrap justify-between gap-2 border-b border-border py-1"><dt>{k}</dt><dd>{String(v)}</dd></div>)}</dl>
      <details><summary>Valores, limitaciones y trazabilidad del cálculo</summary><pre className="overflow-auto whitespace-pre-wrap text-xs">{JSON.stringify(result,null,2)}</pre></details>
    </section>}
  </div>;
}
