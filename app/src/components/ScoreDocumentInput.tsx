import { useEffect, useRef, useState } from 'react';
import { candidates, samples, type Field, type Sample } from '../lib/score-document';

type Props = { fields:Field[]; onPick:(key:string,value:string)=>void; onValues:(values:Record<string,string>)=>void };
export default function ScoreDocumentInput({fields,onPick,onValues}:Props) {
  const [blocks,setBlocks] = useState<Sample[]>([]);
  const [selected,setSelected] = useState('');
  const [note,setNote] = useState('');
  const [paste,setPaste] = useState('');
  const fileInput = useRef<HTMLInputElement>(null);
  const pending = useRef<AbortController>();
  useEffect(()=>()=>pending.current?.abort(),[]);

  function select(items:Sample[], index:string) {
    setSelected(index);
    const block = index === '' ? undefined : items[Number(index)];
    const matches = candidates(fields,block?.lines ?? []);
    const values:Record<string,string> = {};
    for (const [key,items] of Object.entries(matches)) {
      if (items.length === 1) values[key] = items[0]!.value;
    }
    onValues(values);
  }
  function show(items:Sample[]) {
    setBlocks(items);
    select(items,items.length===1?'0':'');
    setNote(items.length?'Compruebe la muestra, los valores y sus unidades. Complete los campos pendientes.':'Sin texto extraíble. Si es un PDF escaneado, puede pegar los resultados o introducirlos a mano.');
  }
  async function read(file?:File) {
    pending.current?.abort();
    const controller = new AbortController();
    pending.current = controller;
    setPaste(''); setBlocks([]); select([],''); setNote('');
    if (!file) return;
    if (/\.txt$/i.test(file.name) && file.size>100000) {setNote('Seleccione un texto de hasta 100 KB.');return;}
    if (file.size > 8*1024*1024) {setNote('El archivo supera 8 MB.');return;}
    setNote('Leyendo documento…');
    try {
      const items = /\.pdf$/i.test(file.name) ? await (await import('../lib/score-pdf')).readPdf(file,controller.signal)
        : /\.txt$/i.test(file.name) ? samples(await file.text(),'Texto') : [];
      if (!controller.signal.aborted) show(items);
    } catch {
      if (!controller.signal.aborted) setNote('No se pudo leer el documento. Pegue los resultados o introdúzcalos a mano.');
    }
  }
  const block = selected === '' ? undefined : blocks[Number(selected)];
  const matches = candidates(fields,block?.lines ?? []);
  return <section className="card p-4 space-y-3" aria-label="Importar analítica">
    <label className="block">PDF con texto o archivo de texto<input ref={fileInput} type="file" className="input" accept=".pdf,.txt" onChange={e=>void read(e.target.files?.[0])}/></label>
    <label className="block">O pegue una analítica<textarea className="input" maxLength={100000} value={paste} onChange={e=>{
      pending.current?.abort(); if(fileInput.current) fileInput.current.value='';
      setPaste(e.target.value); show(samples(e.target.value,'Texto'));
    }}/></label>
    {note&&<p role="status">{note}</p>}
    {blocks.length>1&&<label>Seleccione la página o muestra<select className="input" value={selected} onChange={e=>select(blocks,e.target.value)}>
      <option value="">Seleccione una</option>{blocks.map((b,i)=><option key={i} value={i}>{b.label}</option>)}
    </select></label>}
    {block&&<><details><summary>Ver texto de origen · {block.label}</summary><pre className="whitespace-pre-wrap">{block.lines.join('\n')}</pre></details>
      {fields.some(f=>!matches[f.key])&&<p>Sin identificar en el bloque seleccionado · {fields.filter(f=>!matches[f.key]).map(f=>f.label).join(', ')}. Revise el original y complete los datos disponibles.</p>}
      {Object.keys(matches).length===0&&<p>Sin coincidencias inequívocas para este formulario.</p>}
      {fields.filter(f=>matches[f.key]).map(f=><div key={f.key}><strong>{f.label}</strong>
        {matches[f.key]!.length===1 ? <p>Origen · {matches[f.key]![0]!.source}</p>
          : <label>Varios resultados. Seleccione la línea que corresponde a la muestra.
            <select className="input" value="" onChange={e=>{const item=matches[f.key]?.[Number(e.target.value)];if(item)onPick(f.key,item.value);}}>
              <option value="" disabled>Elegir línea de origen</option>{matches[f.key]!.map((c,i)=><option key={i} value={i}>{c.source}</option>)}
            </select></label>}
      </div>)}</>}
  </section>;
}

