import { useMemo, useState } from 'react';

type Tab='history'|'exam'|'mcdt'|'problems'|'diagnostic'|'plan'|'export';
type ReviewState='pending'|'accepted'|'rejected';
type Mcdt={id:string;kind:string;name:string;official:string;ai:string;state:ReviewState;provenance:string};

const tabs:[Tab,string][]=[
 ['history','História'],['exam','Exame'],['mcdt','MCDT'],['problems','Problemas'],
 ['diagnostic','Apoio diagnóstico'],['plan','Plano'],['export','Exportar'],
];
const mcdtKinds=['Analítica','Gasometria','ECG','Rx','TC/RM','Ecografia/POCUS','Microbiologia','Outro'];
const directId=/\b(nome|name|sns|nif|morada|endereço|address|telefone|telemóvel|phone|mrn)\b\s*[:\-]/i;

export default function ClinicalNote(){
 const [tab,setTab]=useState<Tab>('history');
 const [age,setAge]=useState(''); const [sex,setSex]=useState('unknown');
 const [origin,setOrigin]=useState(''); const [chief,setChief]=useState(''); const [hpi,setHpi]=useState('');
 const [pmh,setPmh]=useState(''); const [meds,setMeds]=useState(''); const [allergies,setAllergies]=useState('');
 const [exam,setExam]=useState(''); const [vitals,setVitals]=useState('');
 const [problems,setProblems]=useState(''); const [plan,setPlan]=useState('');
 const [mcdt,setMcdt]=useState<Mcdt[]>([]); const [privacyAck,setPrivacyAck]=useState(false);
 const [clinicianReviewed,setClinicianReviewed]=useState(false);
 const [draftKind,setDraftKind]=useState('Analítica'); const [draftName,setDraftName]=useState('');
 const [draftOfficial,setDraftOfficial]=useState(''); const [draftAi,setDraftAi]=useState('');
 const [uploadName,setUploadName]=useState('');
 const encounter=useMemo(()=>crypto.randomUUID?.() ?? `enc-${Date.now()}`,[]);
 const freeText=[origin,chief,hpi,pmh,meds,allergies,exam,vitals,problems,plan,...mcdt.flatMap(x=>[x.official,x.ai])].join('\n');
 const privacyStop=directId.test(freeText);
 const pending=mcdt.filter(x=>x.state==='pending').length;
 const exportBlocked=privacyStop||!privacyAck||!clinicianReviewed||pending>0;

 function inferKind(name:string){
   const n=name.toLowerCase();
   if(/ecg|ekg/.test(n)) return 'ECG';
   if(/gas|gaso|abg|vbg/.test(n)) return 'Gasometria';
   if(/rx|xray|x-ray|radiogr/.test(n)) return 'Rx';
   if(/ct|tc|mri|rm|tac/.test(n)) return 'TC/RM';
   if(/eco|pocus|ultra/.test(n)) return 'Ecografia/POCUS';
   if(/micro|culture|cultivo/.test(n)) return 'Microbiologia';
   if(/lab|anal|hemogram|bioq/.test(n)) return 'Analítica';
   return 'Outro';
 }
 function onUpload(file?:File){
   if(!file) return;
   setUploadName(file.name);
   setDraftName(file.name);
   setDraftKind(inferKind(file.name));
   setClinicianReviewed(false);
 }
 function addMcdt(){
   if(!draftName.trim()&&!draftOfficial.trim()&&!draftAi.trim()) return;
   setMcdt(x=>[...x,{id:`${Date.now()}-${x.length}`,kind:draftKind,name:draftName||draftKind,official:draftOfficial,ai:draftAi,state:'pending',provenance:'upload → módulo clínico correspondente'}]);
   setDraftName(''); setDraftOfficial(''); setDraftAi(''); setClinicianReviewed(false);
 }
 function review(id:string,state:ReviewState){setMcdt(x=>x.map(v=>v.id===id?{...v,state}:v));setClinicianReviewed(false)}
 const card='rounded-2xl border border-border bg-surface p-4 shadow-card';
 return <div className="space-y-4" data-testid="clinical-note-workspace">
   <section className={card}>
    <div className="flex flex-wrap items-start gap-3">
      <div className="min-w-0 flex-1"><p className="section-title">Nota clínica · episódio seudónimo</p><h1 className="mt-1 text-xl font-extrabold">Apoio ao diagnóstico</h1><p className="mt-1 break-all text-xs text-muted">{encounter}</p></div>
      <span className={`chip ${privacyStop?'border-danger text-danger':'border-ok text-ok'}`}>{privacyStop?'STOP privacidade':'Privacidade OK'}</span>
      <span className="chip">{clinicianReviewed?'Revisto pelo médico':'Revisão pendente'}</span>
    </div>
    <div className="mt-4 grid gap-3 sm:grid-cols-3">
      <label><span className="label">Idade</span><input aria-label="Idade" className="input" inputMode="decimal" value={age} onChange={e=>{setAge(e.target.value);setClinicianReviewed(false)}} placeholder="anos / meses"/></label>
      <label><span className="label">Sexo</span><select aria-label="Sexo" className="input" value={sex} onChange={e=>{setSex(e.target.value);setClinicianReviewed(false)}}><option value="unknown">Não registado</option><option value="female">Feminino</option><option value="male">Masculino</option><option value="intersex">Intersexo</option></select></label>
      <label><span className="label">Origem / transferência</span><input aria-label="Origem" className="input" value={origin} onChange={e=>setOrigin(e.target.value)} placeholder="Sem identificadores diretos"/></label>
    </div>
   </section>

   {privacyStop&&<div role="alert" className="rounded-xl border border-danger bg-surface p-4 text-sm font-semibold text-danger">STOP: possível identificador direto no texto. Remova-o antes de análise/exportação.</div>}

   <nav className="overflow-x-auto" aria-label="Secções da nota"><div className="flex min-w-max gap-1 rounded-xl border border-border bg-surface p-1">
    {tabs.map(([id,label])=><button key={id} onClick={()=>setTab(id)} className={`rounded-lg px-3 py-2 text-sm font-semibold ${tab===id?'bg-primary text-primary-fg':'text-muted hover:bg-surface-2'}`} aria-current={tab===id?'page':undefined}>{label}{id==='mcdt'&&pending>0?` (${pending})`:''}</button>)}
   </div></nav>

   {tab==='history'&&<section className={card}><h2 className="text-lg font-bold">História clínica</h2><div className="mt-4 grid gap-4">
    <label><span className="label">Motivo de consulta</span><textarea className="input min-h-20" value={chief} onChange={e=>{setChief(e.target.value);setClinicianReviewed(false)}}/></label>
    <label><span className="label">História da doença atual</span><textarea className="input min-h-32" value={hpi} onChange={e=>{setHpi(e.target.value);setClinicianReviewed(false)}}/></label>
    <div className="grid gap-4 md:grid-cols-3"><label><span className="label">Antecedentes</span><textarea className="input min-h-24" value={pmh} onChange={e=>setPmh(e.target.value)}/></label><label><span className="label">Medicação habitual / discrepâncias</span><textarea className="input min-h-24" value={meds} onChange={e=>setMeds(e.target.value)}/></label><label><span className="label">Alergias</span><textarea className="input min-h-24" value={allergies} onChange={e=>setAllergies(e.target.value)} placeholder="Fármaco + reação; ou desconhecido"/></label></div>
   </div></section>}

   {tab==='exam'&&<section className={card}><h2 className="text-lg font-bold">Exame</h2><p className="mt-1 text-sm text-muted">Registe observações seriadas; não substitua a avaliação inicial.</p><div className="mt-4 grid gap-4 md:grid-cols-2"><label><span className="label">Constantes + hora + O₂/dispositivo</span><textarea className="input min-h-32" value={vitals} onChange={e=>setVitals(e.target.value)} placeholder="14:32 · TA… FC… FR… SpO₂… O₂… T… GCS…"/></label><label><span className="label">Exploração por sistemas</span><textarea className="input min-h-32" value={exam} onChange={e=>setExam(e.target.value)} placeholder="Geral · Neuro · Respiratório · CV · Abdómen · Pele · Extremidades"/></label></div></section>}

   {tab==='mcdt'&&<section className="space-y-4">
    <div className={card}><h2 className="text-lg font-bold">Adicionar MCDT</h2><div className="mt-3 flex flex-wrap gap-2">{mcdtKinds.map(k=><button key={k} className={`btn ${draftKind===k?'btn-primary':'btn-ghost'}`} onClick={()=>setDraftKind(k)}>+ {k}</button>)}</div>
      <div className="mt-4 grid gap-3">
      <label className="rounded-xl border border-dashed border-border p-4"><span className="label">Upload clínico</span><input aria-label="Upload clínico" type="file" accept=".pdf,.png,.jpg,.jpeg,.webp,.txt,.csv,.json,.xml,.dcm" onChange={e=>onUpload(e.target.files?.[0])}/><span className="mt-2 block text-xs text-muted">{uploadName?'Ficheiro selecionado: '+uploadName:'PDF/imagem/texto. O original não é incorporado no relatório por defeito.'}</span></label>
      <input aria-label="Nome do exame" className="input" value={draftName} onChange={e=>setDraftName(e.target.value)} placeholder="Ex.: TC crânio 18:20"/><label><span className="label">Informe oficial / dados extraídos</span><textarea className="input min-h-24" value={draftOfficial} onChange={e=>setDraftOfficial(e.target.value)}/></label><label><span className="label">Interpretação IA proposta</span><textarea className="input min-h-24" value={draftAi} onChange={e=>setDraftAi(e.target.value)} placeholder="Mantida separada do informe oficial"/></label><button className="btn-primary justify-self-start" onClick={addMcdt}>Criar cartão para revisão</button></div>
    </div>
    {mcdt.map(x=><article key={x.id} className={card} data-testid="mcdt-review-card"><div className="flex flex-wrap items-center gap-2"><strong>{x.kind} · {x.name}</strong><span className="chip ml-auto">{x.state==='pending'?'Pendente':x.state==='accepted'?'Aceite':'Rejeitado'}</span></div><p className="mt-3 text-xs font-semibold uppercase text-muted">Informe oficial / extraído</p><p className="whitespace-pre-wrap text-sm">{x.official||'—'}</p><p className="mt-3 text-xs font-semibold uppercase text-primary">Interpretação IA</p><textarea aria-label={`Interpretação IA ${x.name}`} className="input mt-1 min-h-20" value={x.ai} onChange={e=>{setMcdt(v=>v.map(y=>y.id===x.id?{...y,ai:e.target.value,state:'pending'}:y));setClinicianReviewed(false)}}/><p className="mt-2 text-xs text-muted">Proveniência: {x.provenance}</p><div className="mt-3 flex flex-wrap gap-2"><button className="btn-primary" onClick={()=>review(x.id,'accepted')}>Aceitar</button><button className="btn-ghost" onClick={()=>review(x.id,'pending')}>Editar</button><button className="btn-ghost text-danger" onClick={()=>review(x.id,'rejected')}>Rejeitar</button></div></article>)}
   </section>}

   {tab==='problems'&&<section className={card}><h2 className="text-lg font-bold">Problemas</h2><p className="mt-1 text-sm text-muted">Lista numerada editável: ativo · a melhorar · resolvido · por esclarecer.</p><textarea className="input mt-4 min-h-56" value={problems} onChange={e=>{setProblems(e.target.value);setClinicianReviewed(false)}} placeholder={"1. [ativo] …\n2. [por esclarecer] …"}/></section>}

   {tab==='diagnostic'&&<section className="grid gap-4 lg:grid-cols-2">
    {[['Mais provável','Confiança qualitativa · evidência a favor/contra · módulos fonte'],['Diferencial','Alternativas que explicam os dados'],['Must not miss','Diagnósticos tempo-dependentes a excluir'],['Dados em falta / contradições','Dados discriminantes e conflitos de informação']].map(([h,p])=><div className={card} key={h}><h2 className="font-bold">{h}</h2><p className="mt-2 text-sm text-muted">{p}</p><div className="mt-4 rounded-xl border border-dashed border-border p-4 text-sm text-muted">Gerado pelo motor clínico após dados aceites. Nunca mostrar probabilidade numérica não calibrada.</div></div>)}
   </section>}

   {tab==='plan'&&<section className={card}><h2 className="text-lg font-bold">Plano</h2><p className="mt-1 text-sm text-muted">Estabilização · provas adicionais · tratamento · alertas farmacológicos · consulta · destino · reavaliação.</p><textarea className="input mt-4 min-h-64" value={plan} onChange={e=>{setPlan(e.target.value);setClinicianReviewed(false)}}/><div className="mt-3 rounded-xl border border-warn bg-warn-bg p-3 text-sm text-warn">Qualquer sugestão farmacológica acionável deve passar pelo motor central de segurança medicamentosa.</div></section>}

   {tab==='export'&&<section className={card}><h2 className="text-lg font-bold">Revisão e exportação</h2><div className="mt-4 grid gap-2 text-sm">
    <label className="flex items-center gap-2"><input type="checkbox" checked={privacyAck} onChange={e=>setPrivacyAck(e.target.checked)}/> Identificadores diretos removidos; texto livre e metadados revistos.</label>
    <label className="flex items-center gap-2"><input type="checkbox" checked={clinicianReviewed} onChange={e=>setClinicianReviewed(e.target.checked)}/> Médico reviu e valida o conteúdo clínico.</label>
    <p>{pending===0?'✓ Sem cartões MCDT pendentes':`STOP: ${pending} MCDT pendente(s) de aceitar/editar/rejeitar.`}</p>
   </div><div className="mt-4 flex flex-wrap gap-2"><button disabled={exportBlocked} className="btn-primary">Word (.docx)</button><button disabled={exportBlocked} className="btn-primary">PDF</button><button disabled={exportBlocked} className="btn-ghost">JSON</button></div>{exportBlocked&&<p role="status" className="mt-3 text-sm font-semibold text-danger">Exportação bloqueada até cumprir privacidade, revisão médica e resolução dos MCDT pendentes.</p>}</section>}
 </div>
}
