import { getDocument, GlobalWorkerOptions } from 'pdfjs-dist';
import workerUrl from 'pdfjs-dist/build/pdf.worker.min.mjs?url';
import { samples, type Sample } from './score-document';

GlobalWorkerOptions.workerSrc = workerUrl;

export async function readPdf(file:File, signal:AbortSignal):Promise<Sample[]> {
  const data = new Uint8Array(await file.arrayBuffer());
  signal.throwIfAborted();
  const task = getDocument({data, useSystemFonts:false});
  const cancel = () => { void task.destroy(); };
  signal.addEventListener('abort',cancel,{once:true});
  try {
    const pdf = await task.promise;
    if (pdf.numPages > 40) throw new Error('Seleccione un informe de hasta 40 páginas.');
    const blocks:Sample[] = [];
    let totalItems=0;
    for (let n=1;n<=pdf.numPages;n++) {
      signal.throwIfAborted();
      const page = await pdf.getPage(n);
      const content = await page.getTextContent();
      totalItems+=content.items.length;
      if(totalItems>50000) throw new Error("Informe demasiado extenso.");
      const rows = new Map<number,{x:number;width:number;text:string}[]>();
      for (const item of content.items) {
        if (!('str' in item) || !item.str.trim()) continue;
        const y = Math.round(item.transform[5]);
        const row = rows.get(y) ?? [];
        row.push({x:item.transform[4],width:item.width,text:item.str});
        rows.set(y,row);
      }
      const lines = [...rows.entries()].sort(([a],[b])=>b-a).map(([,row])=>
        row.sort((a,b)=>a.x-b.x).map((item,i)=>{
          const prev=row[i-1];
          const gap=prev ? item.x-prev.x-prev.width : 0;
          return (gap>0.7?' ':'')+item.text;
        }).join(''));
      blocks.push(...samples(lines.join('\n'),`Página ${n}`).map(block=>({...block,pageNumber:n})));
      page.cleanup();
    }
    return blocks;
  } finally {
    signal.removeEventListener('abort',cancel);
    await task.destroy();
  }
}

