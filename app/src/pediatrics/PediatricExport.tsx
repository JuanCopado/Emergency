import { useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { pediatricCatalog, type Fields } from './catalog';

export type PediatricReport = {snapshot: Fields; sections: [string, string[]][]};
export default function PediatricExport({report, calculation, result}: {report:PediatricReport; calculation:Fields; result:Fields}) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const mounted = useRef(false);
  useEffect(()=>{mounted.current=true;return ()=>{mounted.current=false;};},[]);
  async function download(format:'json'|'pdf'|'docx') {
    setBusy(true);setError('');
    try {
      const base=(import.meta.env.VITE_CLINICAL_NOTE_API_BASE??'').replace(/\/$/,'');
      const response=await fetch(`${base}/api/pediatric-outpatient/export`, {method:'POST',headers:{'Content-Type':'application/json'},cache:'no-store',body:JSON.stringify({calculation:{...calculation,source_revision:pediatricCatalog.source_revision},expected_result:result,format})});
      const data=await response.json();
      if(!response.ok)throw new Error(data.error||`Error ${response.status}`);
      if(!mounted.current)return;
      const bytes=Uint8Array.from(atob(data.content_base64),c=>c.charCodeAt(0));
      const url=URL.createObjectURL(new Blob([bytes],{type:data.mime_type}));
      const anchor=document.createElement('a');anchor.href=url;anchor.download=data.filename;anchor.click();
      setTimeout(()=>URL.revokeObjectURL(url),1000);
    } catch(e) {if(mounted.current)setError(e instanceof Error?e.message:String(e));}
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
