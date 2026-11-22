import { useTranslation } from 'react-i18next';
import { useEffect, useRef, useState } from 'react';
import { candidates, samples, type Field, type Sample } from '../lib/score-document';

type Props = { fields:Field[]; onPick:(key:string,value:string)=>void; onValues:(values:Record<string,string>)=>void };
export default function ScoreDocumentInput({fields,onPick,onValues}:Props) {
  const { t } = useTranslation();
  const sampleLabel = (sample:Sample) => `${sample.pageNumber ? t('scoreDoc.page',{number:sample.pageNumber}) : t('scoreDoc.text')} · ${t('scoreDoc.block',{number:sample.blockNumber})} · ${sample.lines[0]?.slice(0,90) ?? ''}`;
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
    setNote(items.length?'review':'noText');
  }
  async function read(file?:File) {
    pending.current?.abort();
    const controller = new AbortController();
    pending.current = controller;
    setPaste(''); setBlocks([]); select([],''); setNote('');
    if (!file) return;
    if (/\.txt$/i.test(file.name) && file.size>100000) {setNote('textLimit');return;}
    if (file.size > 8*1024*1024) {setNote('fileLimit');return;}
    setNote('reading');
    try {
      const items = /\.pdf$/i.test(file.name) ? await (await import('../lib/score-pdf')).readPdf(file,controller.signal)
        : /\.txt$/i.test(file.name) ? samples(await file.text(),'') : [];
      if (!controller.signal.aborted) show(items);
    } catch {
      if (!controller.signal.aborted) setNote('readError');
    }
  }
  const block = selected === '' ? undefined : blocks[Number(selected)];
  const matches = candidates(fields,block?.lines ?? []);
  return <section className="card p-4 space-y-3" aria-label={t('scoreDoc.title')}>
    <label className="block">{t('scoreDoc.file')}<input ref={fileInput} type="file" className="input" accept=".pdf,.txt" onChange={e=>void read(e.target.files?.[0])}/></label>
    <label className="block">{t('scoreDoc.paste')}<textarea className="input" maxLength={100000} value={paste} onChange={e=>{
      pending.current?.abort(); if(fileInput.current) fileInput.current.value='';
      setPaste(e.target.value); show(samples(e.target.value,''));
    }}/></label>
    {note&&<p role="status">{t(`scoreDoc.${note}`)}</p>}
    {blocks.length>1&&<label>{t('scoreDoc.selectSample')}<select className="input" value={selected} onChange={e=>select(blocks,e.target.value)}>
      <option value="">{t('scoreDoc.choose')}</option>{blocks.map((b,i)=><option key={i} value={i}>{sampleLabel(b)}</option>)}
    </select></label>}
    {block&&<><details><summary>{t('scoreDoc.source')} · {sampleLabel(block)}</summary><pre className="whitespace-pre-wrap">{block.lines.join('\n')}</pre></details>
      {fields.some(f=>!matches[f.key])&&<p>{t('scoreDoc.missing')} · <span lang="es">{fields.filter(f=>!matches[f.key]).map(f=>f.label).join(', ')}</span></p>}
      {Object.keys(matches).length===0&&<p>{t('scoreDoc.noMatches')}</p>}
      {fields.filter(f=>matches[f.key]).map(f=><div key={f.key}><strong lang="es">{f.label}</strong>
        {matches[f.key]!.length===1 ? <p>{t('scoreDoc.origin')} · {matches[f.key]![0]!.source}</p>
          : <label>{t('scoreDoc.ambiguous')}
            <select className="input" value="" onChange={e=>{const item=matches[f.key]?.[Number(e.target.value)];if(item)onPick(f.key,item.value);}}>
              <option value="" disabled>{t('scoreDoc.chooseLine')}</option>{matches[f.key]!.map((c,i)=><option key={i} value={i}>{c.source}</option>)}
            </select></label>}
      </div>)}</>}
  </section>;
}

