import { useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { pediatricCatalog, type Fields } from './catalog';
import { decodeExportFile, ExportIntegrityError, saveBytes, sameJson, type ExportFormat } from '../lib/exportIntegrity';

export type PediatricReport = {snapshot: Fields; sections: [string, string[]][]};
export default function PediatricExport({report, calculation, result}: {report:PediatricReport; calculation:Fields; result:Fields}) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const mounted = useRef(false);
  // Q05-R: every request is tied to the props it was sent with; new props or unmount make it stale.
  const request = useRef(0);
  useEffect(()=>{const pending=request;mounted.current=true;return ()=>{mounted.current=false;pending.current++;};},[]);
  useEffect(()=>{request.current++;},[report,calculation,result]);
  async function download(format:ExportFormat) {
    const id=++request.current;
    setBusy(true);setError('');
    try {
      const base=(import.meta.env.VITE_CLINICAL_NOTE_API_BASE??'').replace(/\/$/,'');
      const response=await fetch(`${base}/api/pediatric-outpatient/export`, {method:'POST',headers:{'Content-Type':'application/json'},cache:'no-store',body:JSON.stringify({calculation:{...calculation,source_revision:pediatricCatalog.source_revision},expected_result:result,format})});
      const data=await response.json();
      if(!response.ok)throw new Error(data.error||`Error ${response.status}`);
      if(id!==request.current)return;
      const file=decodeExportFile(data,format);
      // The JSON export is the canonical snapshot: it must carry exactly the confirmed result and CLINICALLY_PENDING.
      // PDF/DOCX cannot be inspected here; the backend recomputes and compares expected_result before rendering them.
      if(format==='json'){
        let snapshot:unknown;
        try {snapshot=(JSON.parse(new TextDecoder().decode(file.bytes)) as {snapshot?:unknown}).snapshot;} catch {snapshot=undefined;}
        const s=snapshot as {clinical_status?:unknown;result?:unknown}|undefined;
        if(!s||s.clinical_status!=='CLINICALLY_PENDING'||!sameJson(s.result,result)) throw new ExportIntegrityError('La exportación no corresponde al cálculo confirmado; no se descarga.');
      }
      saveBytes(file.filename,file.mime,file.bytes);
    } catch(e) {if(mounted.current&&id===request.current)setError(e instanceof Error?e.message:String(e));}
    finally {if(mounted.current)setBusy(false);}
  }
  const content=<>{report.sections.map(([heading,paragraphs],i)=><section key={i}><h3 className="font-bold mt-4">{heading}</h3>{paragraphs.map((p,j)=><p className="whitespace-pre-wrap break-words" key={j}>{p}</p>)}</section>)}</>;
  return <div className="space-y-3 border-t border-border pt-3" aria-label="Exportación pediátrica">
    <p>Exportación del resultado y sus alertas · YELLOW · CLINICALLY_PENDING</p>
    <div className="flex flex-wrap gap-2">{(['json','pdf','docx'] as const).map(f=><button key={f} className="btn-ghost" disabled={busy} onClick={()=>void download(f)}>Exportar {f.toUpperCase()}</button>)}<button className="btn-ghost" onClick={()=>window.print()}>Imprimir resultado</button></div>
    {error&&<p role="alert">{error}</p>}
    <details><summary className="cursor-pointer underline">Ver contenido íntegro de la exportación</summary><div data-testid="pediatric-export-content">{content}</div></details>
    {createPortal(<article className="pediatric-print-sheet" aria-hidden="true">{content}</article>,document.body)}
  </div>;
}
