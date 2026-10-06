import { useMemo, useState } from 'react';
import {
  acceptClinicalUpload,
  analyzeClinicalNote,
  downloadBlob,
  exportClinicalNote,
  preflightClinicalNote,
  prepareClinicalUpload,
} from '../clinical-note/api';
import type {
  ClinicalAssessment,
  ClinicalNotePayload,
  PreparedUpload,
  ReportItem,
  ReviewState,
} from '../clinical-note/types';

type Tab='history'|'exam'|'mcdt'|'problems'|'diagnostic'|'plan'|'export';
type McdtCard={
  id:string;kind:string;name:string;official:string;ai:string;state:ReviewState;
  provenance:string;prepared?:PreparedUpload;privacyChecked:boolean;burnedChecked:boolean;
  sourceReference:string;
};

const tabs:[Tab,string][]=[
 ['history','História'],['exam','Exame'],['mcdt','MCDT'],['problems','Problemas'],
 ['diagnostic','Apoio diagnóstico'],['plan','Plano'],['export','Exportar'],
];
const mcdtKinds=['Analítica','Gasometria','ECG','Rx','TC/RM','Ecografia/POCUS','Microbiologia','Outro'];
const directId=/\b(nome|name|sns|nif|morada|endereço|address|telefone|telemóvel|phone|mrn)\b\s*[:\-]/i;
const kindMap:Record<string,string>={
  'Analítica':'laboratory_report','Gasometria':'blood_gas','ECG':'ecg','Rx':'xray',
  'TC/RM':'ct','Ecografia/POCUS':'pocus','Microbiologia':'microbiology','Outro':'other_image',
};
const sectionForKind:Record<string,keyof ClinicalNotePayload['complementary_tests']>={
  laboratory_report:'laboratory',blood_gas:'blood_gas',ecg:'ecg',xray:'imaging',ct:'imaging',
  pocus:'imaging',microbiology:'microbiology',other_image:'other',pdf_document:'other',
};
const emptyAssessment:ClinicalAssessment={
  problem_representation:null,active_problems:[],likely_diagnoses:[],differential_diagnoses:[],
  must_not_miss:[],suggested_tests:[],treatment_suggestions:[],disposition:[],reassessment:[],
  contradictions_to_clarify:[],limitations:[],
};
const emptyReports=():ClinicalNotePayload['complementary_tests']=>({
  laboratory:[],blood_gas:[],ecg:[],imaging:[],microbiology:[],other:[],
});
const lines=(value:string)=>value.split(/\r?\n/).map(x=>x.trim()).filter(Boolean);
const numberOrNull=(value:string)=>{
  if(!value.trim()) return null;
  const n=Number(value.replace(',','.'));
  return Number.isFinite(n)?n:null;
};

export default function ClinicalNote(){
 const [tab,setTab]=useState<Tab>('history');
 const [age,setAge]=useState(''); const [sex,setSex]=useState<ClinicalNotePayload['encounter']['sex']>('unknown');
 const [origin,setOrigin]=useState(''); const [chief,setChief]=useState(''); const [hpi,setHpi]=useState('');
 const [pmh,setPmh]=useState(''); const [meds,setMeds]=useState(''); const [allergies,setAllergies]=useState('');
 const [exam,setExam]=useState(''); const [problems,setProblems]=useState(''); const [plan,setPlan]=useState('');
 const [vitalDraft,setVitalDraft]=useState({time:'',bp:'',hr:'',rr:'',spo2:'',oxygen:'',temp:'',gcs:''});
 const [vitalSets,setVitalSets]=useState<ClinicalNotePayload['exam']['vitals']>([]);
 const [timeline,setTimeline]=useState<ClinicalNotePayload['timeline']>([]);
 const [reports,setReports]=useState<ClinicalNotePayload['complementary_tests']>(emptyReports);
 const [assessment,setAssessment]=useState<ClinicalAssessment|null>(null);
 const [medicationGate,setMedicationGate]=useState<{status:string;actionable:boolean;message:string}|null>(null);
 const [diagnosticStale,setDiagnosticStale]=useState(true);
 const [mcdt,setMcdt]=useState<McdtCard[]>([]); const [privacyAck,setPrivacyAck]=useState(false);
 const [clinicianReviewed,setClinicianReviewed]=useState(false);
 const [draftKind,setDraftKind]=useState('Outro'); const [draftName,setDraftName]=useState('');
 const [draftOfficial,setDraftOfficial]=useState(''); const [draftAi,setDraftAi]=useState('');
 const [uploadName,setUploadName]=useState(''); const [apiBusy,setApiBusy]=useState(false);
 const [apiError,setApiError]=useState('');
 const encounter=useMemo(()=>crypto.randomUUID?.() ?? `enc-${Date.now()}`,[]);
 const allAccepted=Object.values(reports).flat();
 const freeText=[origin,chief,hpi,pmh,meds,allergies,exam,problems,plan,
   ...allAccepted.flatMap(x=>[x.official_report||'',x.ai_interpretation||'',x.findings||'',x.impression||'']),
   ...mcdt.flatMap(x=>[x.official,x.ai])].join('\n');
 const privacyStop=directId.test(freeText);
 const pending=mcdt.filter(x=>x.state==='pending').length;
 const exportBlocked=privacyStop||!privacyAck||!clinicianReviewed||pending>0||apiBusy;

 function touch(){
   setClinicianReviewed(false);
   setDiagnosticStale(true);
 }
 function buildNote():ClinicalNotePayload{
   const baseAssessment:ClinicalAssessment=assessment?{
     ...assessment,
     active_problems:lines(problems).length?lines(problems):assessment.active_problems,
     treatment_suggestions:[
       ...assessment.treatment_suggestions,
       ...(plan.trim()?[{action:plan.trim(),priority:'routine' as const,rationale:'Plano introduzido pelo médico.',source_modules:['clinician-entry']}]:[]),
     ],
   }:{
     ...emptyAssessment,
     active_problems:lines(problems),
     treatment_suggestions:plan.trim()?[{action:plan.trim(),priority:'routine',rationale:'Plano introduzido pelo médico.',source_modules:['clinician-entry']}]:[],
   };
   const years=numberOrNull(age);
   return {
     schema_version:'1.0',language:'pt-PT',
     encounter:{encounter_id:encounter,age:{years,months:null},sex,origin:origin||null,transfer_status:null,functional_status:null,cognitive_status:null,living_context:null},
     history:{
       chief_complaint:chief||null,present_illness:hpi||null,past_medical_history:lines(pmh),past_surgical_history:[],
       chronic_medications:lines(meds).map(name=>({name,dose:null,schedule:null,source:'clinician_entry'})),
       medication_discrepancies:[],allergies:lines(allergies).map(substance=>({substance,class:null,reaction:null,severity:null,confirmed:null})),
       social_history:null,baseline_status:null,source_reliability:null,
     },
     timeline,
     exam:{
       vitals:vitalSets,general:exam||null,neurologic:null,respiratory:null,cardiovascular:null,
       abdominal:null,skin_wounds:null,extremities:null,other:null,
     },
     complementary_tests:reports,
     assessment:baseAssessment,
     clinician_validation:{
       reviewed:clinicianReviewed,reviewer_role:clinicianReviewed?'treating_clinician':null,
       reviewed_at:clinicianReviewed?new Date().toISOString():null,
       changes_made:clinicianReviewed?'Clinician reviewed current structured note.':null,
     },
     privacy:{
       mode:'clinical_pseudonymized',direct_identifiers_removed:privacyAck,free_text_screened:privacyAck,
       source_metadata_checked:privacyAck,burned_in_identifiers_checked:privacyAck,export_allowed:!exportBlocked,privacy_notes:[],
     },
   };
 }
 function addVital(){
   if(!Object.values(vitalDraft).some(Boolean)) return;
   const item:ClinicalNotePayload['exam']['vitals'][number]={
     time_label:vitalDraft.time||null,bp:vitalDraft.bp||null,hr:numberOrNull(vitalDraft.hr),rr:numberOrNull(vitalDraft.rr),
     spo2:numberOrNull(vitalDraft.spo2),oxygen:vitalDraft.oxygen||null,temperature_c:numberOrNull(vitalDraft.temp),
     gcs:vitalDraft.gcs||null,source:'clinician_entry',
   };
   setVitalSets(v=>[...v,item]);
   setTimeline(v=>[...v,{time_label:item.time_label||'Constantes',event:`Constantes: TA ${item.bp||'—'} · FC ${item.hr??'—'} · FR ${item.rr??'—'} · SpO₂ ${item.spo2??'—'}%`,source:'clinician_entry'}]);
   setVitalDraft({time:'',bp:'',hr:'',rr:'',spo2:'',oxygen:'',temp:'',gcs:''});
   touch();
 }
 function removePersisted(card:McdtCard){
   setReports(current=>{
     const next=emptyReports();
     for(const key of Object.keys(current) as (keyof typeof current)[]){
       next[key]=current[key].filter(r=>r.source_reference!==card.sourceReference);
     }
     return next;
   });
 }
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
 async function onUpload(file?:File){
   if(!file) return;
   setUploadName(file.name); setDraftName(file.name);
   const inferred=inferKind(file.name);
   const selected=inferred==='Outro'?draftKind:inferred;
   setDraftKind(selected); setApiError(''); setApiBusy(true);
   try{
     const explicitKind=(inferred==='Outro'&&selected==='Outro')?undefined:kindMap[selected];
     const prepared=await prepareClinicalUpload(file,explicitKind);
     const id=prepared.upload_id;
     setMcdt(v=>[...v,{
       id,kind:inferred,name:file.name,official:prepared.extracted.official_report||'',ai:'',state:'pending',
       provenance:`${prepared.processing.modules.join(' · ')} · ${prepared.processing.status}`,prepared,
       privacyChecked:prepared.privacy.status==='PASS',burnedChecked:!prepared.privacy.burned_in_identifier_review_required,
       sourceReference:`sha256:${prepared.sha256}`,
     }]);
     setDraftOfficial('');setDraftAi('');touch();
   }catch(e){setApiError(e instanceof Error?e.message:'Falha ao preparar upload clínico.');}
   finally{setApiBusy(false);}
 }
 function addManualMcdt(){
   if(!draftName.trim()&&!draftOfficial.trim()&&!draftAi.trim()) return;
   const id=`${Date.now()}-${mcdt.length}`;
   setMcdt(x=>[...x,{id,kind:draftKind,name:draftName||draftKind,official:draftOfficial,ai:draftAi,state:'pending',
     provenance:'entrada manual → revisão médica',privacyChecked:true,burnedChecked:true,sourceReference:`ui:${id}`}]);
   setDraftName('');setDraftOfficial('');setDraftAi('');touch();
 }
 async function acceptCard(id:string){
   const card=mcdt.find(x=>x.id===id); if(!card) return;
   setApiError('');
   if(card.prepared){
     if(card.prepared.privacy.status==='STOP'){setApiError('STOP de privacidade no ficheiro: remova os identificadores antes de aceitar.');return;}
     setApiBusy(true);
     try{
       const result=await acceptClinicalUpload(buildNote(),card.prepared,
         {official_report:card.official||null,ai_interpretation:card.ai||null},
         card.privacyChecked,card.burnedChecked);
       setReports(result.note.complementary_tests);
       setTimeline(result.note.timeline);
       setMcdt(v=>v.map(x=>x.id===id?{...x,state:'accepted'}:x));
       touch();
     }catch(e){setApiError(e instanceof Error?e.message:'Não foi possível aceitar o MCDT.');}
     finally{setApiBusy(false);}
     return;
   }
   if(privacyStop){setApiError('STOP de privacidade: resolva os identificadores antes de aceitar.');return;}
   const canonical=kindMap[card.kind]||'other_image';
   const section=sectionForKind[canonical]||'other';
   const report:ReportItem={kind:canonical,time_label:null,provenance:'clinician_entry',source_reference:card.sourceReference,
     official_report:card.official||null,ai_interpretation:card.ai||null,findings:null,impression:null,limitations:[],
     privacy_checked:true,burned_in_identifiers_checked:true,routed_modules:[]};
   setReports(current=>({...current,[section]:[...current[section],report]}));
   setTimeline(v=>[...v,{time_label:'MCDT',event:`Aceite: ${card.kind} · ${card.name}`,source:card.sourceReference}]);
   setMcdt(v=>v.map(x=>x.id===id?{...x,state:'accepted'}:x));touch();
 }
 function editCard(id:string,patch:Partial<McdtCard>){
   const existing=mcdt.find(x=>x.id===id);
   if(existing?.state==='accepted') removePersisted(existing);
   setMcdt(v=>v.map(x=>x.id===id?{...x,...patch,state:'pending'}:x));touch();
 }
 function rejectCard(id:string){
   const existing=mcdt.find(x=>x.id===id);
   if(existing?.state==='accepted') removePersisted(existing);
   setMcdt(v=>v.map(x=>x.id===id?{...x,state:'rejected'}:x));touch();
 }
 async function runDiagnostic(){
   setApiError('');setApiBusy(true);
   try{
     const result=await analyzeClinicalNote(buildNote());
     if(result.blocked){setApiError(result.issues.map(x=>x.message).join(' · ')||'Análise bloqueada.');return;}
     setAssessment(result.assessment);setMedicationGate(result.medication_safety_gate);setDiagnosticStale(false);setClinicianReviewed(false);
   }catch(e){setApiError(e instanceof Error?e.message:'Backend clínico indisponível.');}
   finally{setApiBusy(false);}
 }
 async function doExport(format:'docx'|'pdf'|'json'){
   setApiError('');setApiBusy(true);
   try{
     const note=buildNote();
     const preflight=await preflightClinicalNote(note);
     if(preflight.blocked){setApiError(preflight.findings.map(x=>x.message).join(' · '));return;}
     const out=await exportClinicalNote(note,format);
     downloadBlob(out.filename,out.blob);
   }catch(e){setApiError(e instanceof Error?e.message:'Exportação bloqueada pelo backend.');}
   finally{setApiBusy(false);}
 }
 const card='rounded-2xl border border-border bg-surface p-4 shadow-card';
 const timelineItems=timeline.slice().reverse();

 const content=<>
   {tab==='history'&&<section className={card}><h2 className="text-lg font-bold">História clínica</h2><div className="mt-4 grid gap-4">
    <label><span className="label">Motivo de consulta</span><textarea className="input min-h-20" value={chief} onChange={e=>{setChief(e.target.value);touch()}}/></label>
    <label><span className="label">História da doença atual</span><textarea className="input min-h-32" value={hpi} onChange={e=>{setHpi(e.target.value);touch()}}/></label>
    <div className="grid gap-4 md:grid-cols-3"><label><span className="label">Antecedentes · um por linha</span><textarea className="input min-h-24" value={pmh} onChange={e=>{setPmh(e.target.value);touch()}}/></label><label><span className="label">Medicação habitual · um por linha</span><textarea className="input min-h-24" value={meds} onChange={e=>{setMeds(e.target.value);touch()}}/></label><label><span className="label">Alergias · uma por linha</span><textarea className="input min-h-24" value={allergies} onChange={e=>{setAllergies(e.target.value);touch()}} placeholder="Fármaco + reação; ou desconhecido"/></label></div>
   </div></section>}

   {tab==='exam'&&<section className="space-y-4">
    <div className={card}><h2 className="text-lg font-bold">Constantes seriadas</h2><div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
      {([['time','Hora'],['bp','TA'],['hr','FC'],['rr','FR'],['spo2','SpO₂'],['oxygen','O₂ / dispositivo'],['temp','T °C'],['gcs','GCS']] as const).map(([key,label])=><label key={key}><span className="label">{label}</span><input className="input" value={vitalDraft[key]} onChange={e=>setVitalDraft(v=>({...v,[key]:e.target.value}))}/></label>)}
    </div><button className="btn-primary mt-3" onClick={addVital}>Adicionar constantes</button>
    {vitalSets.length>0&&<div className="mt-4 space-y-2 text-sm">{vitalSets.map((v,i)=><div key={i} className="rounded-xl border border-border p-3">{v.time_label||'—'} · TA {v.bp||'—'} · FC {v.hr??'—'} · FR {v.rr??'—'} · SpO₂ {v.spo2??'—'}% · {v.oxygen||'sem O₂ registado'}</div>)}</div>}
    </div>
    <div className={card}><h2 className="text-lg font-bold">Exploração</h2><p className="mt-1 text-sm text-muted">Registe nova observação sem apagar a avaliação inicial.</p><textarea className="input mt-4 min-h-40" value={exam} onChange={e=>{setExam(e.target.value);touch()}} placeholder="Geral · Neuro · Respiratório · CV · Abdómen · Pele · Extremidades"/></div>
   </section>}

   {tab==='mcdt'&&<section className="space-y-4">
    <div className={card}><h2 className="text-lg font-bold">Adicionar MCDT</h2><div className="mt-3 flex flex-wrap gap-2">{mcdtKinds.map(k=><button key={k} className={`btn ${draftKind===k?'btn-primary':'btn-ghost'}`} onClick={()=>setDraftKind(k)}>+ {k}</button>)}</div>
      <div className="mt-4 grid gap-3">
      <label className="rounded-xl border border-dashed border-border p-4"><span className="label">Upload clínico</span><input aria-label="Upload clínico" type="file" accept=".pdf,.png,.jpg,.jpeg,.webp,.txt,.csv,.json,.xml,.dcm" onChange={e=>void onUpload(e.target.files?.[0])}/><span className="mt-2 block text-xs text-muted">{uploadName?'Ficheiro selecionado: '+uploadName:'O original não é guardado nem incorporado no relatório por defeito.'}</span></label>
      <input aria-label="Nome do exame" className="input" value={draftName} onChange={e=>setDraftName(e.target.value)} placeholder="Entrada manual, ex.: TC crânio 18:20"/><label><span className="label">Informe oficial / dados extraídos</span><textarea className="input min-h-24" value={draftOfficial} onChange={e=>setDraftOfficial(e.target.value)}/></label><label><span className="label">Interpretação IA proposta</span><textarea className="input min-h-24" value={draftAi} onChange={e=>setDraftAi(e.target.value)} placeholder="Mantida separada do informe oficial"/></label><button className="btn-primary justify-self-start" onClick={addManualMcdt}>Criar cartão para revisão</button></div>
    </div>
    {mcdt.map(x=><article key={x.id} className={card} data-testid="mcdt-review-card"><div className="flex flex-wrap items-center gap-2"><strong>{x.kind} · {x.name}</strong><span className="chip ml-auto">{x.state==='pending'?'Pendente':x.state==='accepted'?'Aceite':'Rejeitado'}</span></div>
      {x.prepared&&<div className="mt-2 flex flex-wrap gap-2 text-xs"><span className="chip">Privacidade: {x.prepared.privacy.status}</span><span className="chip">Rota: {x.prepared.processing.modules.join(' · ')}</span><span className="chip">Original não retido</span></div>}
      <p className="mt-3 text-xs font-semibold uppercase text-muted">Informe oficial / extraído</p><textarea aria-label={`Informe oficial ${x.name}`} className="input mt-1 min-h-20" value={x.official} onChange={e=>editCard(x.id,{official:e.target.value})}/>
      <p className="mt-3 text-xs font-semibold uppercase text-primary">Interpretação IA</p><textarea aria-label={`Interpretação IA ${x.name}`} className="input mt-1 min-h-20" value={x.ai} onChange={e=>editCard(x.id,{ai:e.target.value})}/><p className="mt-2 text-xs text-muted">Proveniência: {x.provenance}</p>
      {x.prepared?.privacy.manual_file_privacy_review_required&&<label className="mt-3 flex items-center gap-2 text-sm"><input type="checkbox" checked={x.privacyChecked} onChange={e=>editCard(x.id,{privacyChecked:e.target.checked})}/> Metadados/identificadores do ficheiro revistos.</label>}
      {x.prepared?.privacy.burned_in_identifier_review_required&&<label className="mt-2 flex items-center gap-2 text-sm"><input type="checkbox" checked={x.burnedChecked} onChange={e=>editCard(x.id,{burnedChecked:e.target.checked})}/> Identificadores visíveis/burned-in revistos.</label>}
      {x.prepared?.privacy.status==='STOP'&&<p className="mt-2 text-sm font-semibold text-danger">STOP: o backend detetou possível identificador direto no conteúdo.</p>}
      <div className="mt-3 flex flex-wrap gap-2"><button className="btn-primary" disabled={apiBusy||x.prepared?.privacy.status==='STOP'} onClick={()=>void acceptCard(x.id)}>Aceitar</button><button className="btn-ghost" onClick={()=>editCard(x.id,{})}>Editar</button><button className="btn-ghost text-danger" onClick={()=>rejectCard(x.id)}>Rejeitar</button></div></article>)}
   </section>}

   {tab==='problems'&&<section className={card}><h2 className="text-lg font-bold">Problemas</h2><p className="mt-1 text-sm text-muted">Lista numerada editável: ativo · a melhorar · resolvido · por esclarecer.</p><textarea className="input mt-4 min-h-56" value={problems} onChange={e=>{setProblems(e.target.value);touch()}} placeholder={"1. [ativo] …\n2. [por esclarecer] …"}/></section>}

   {tab==='diagnostic'&&<section className="space-y-4">
    <div className={card}><div className="flex flex-wrap items-center gap-3"><div><h2 className="text-lg font-bold">Apoio diagnóstico</h2><p className="text-sm text-muted">Executado apenas sobre dados aceites e após preflight de privacidade.</p></div><button className="btn-primary ml-auto" disabled={apiBusy||privacyStop} onClick={()=>void runDiagnostic()}>{apiBusy?'A processar…':'Atualizar apoio diagnóstico'}</button></div>{diagnosticStale&&assessment&&<p className="mt-3 text-sm font-semibold text-warn">Os dados mudaram desde a última análise; resultado marcado como desatualizado.</p>}</div>
    <div className="grid gap-4 lg:grid-cols-2">
      {([
        ['Mais provável',assessment?.likely_diagnoses||[]],
        ['Diferencial',assessment?.differential_diagnoses||[]],
        ['Must not miss',assessment?.must_not_miss||[]],
      ] as const).map(([h,items])=><div className={card} key={h}><h2 className="font-bold">{h}</h2>{items.length?<div className="mt-3 space-y-3">{items.map((d,i)=><div key={i} className="rounded-xl border border-border p-3"><div className="flex items-center gap-2"><strong>{d.diagnosis}</strong><span className="chip ml-auto">{d.confidence}</span></div>{d.evidence_for.length>0&&<p className="mt-2 text-sm">A favor: {d.evidence_for.join(' · ')}</p>}{d.missing_discriminating_data.length>0&&<p className="mt-1 text-xs text-muted">Falta: {d.missing_discriminating_data.join(' · ')}</p>}<p className="mt-1 text-xs text-muted">Módulos: {d.source_modules.join(' · ')}</p></div>)}</div>:<p className="mt-3 text-sm text-muted">Sem resultado executado/aceite.</p>}</div>)}
      <div className={card}><h2 className="font-bold">Dados em falta / contradições</h2><div className="mt-3 space-y-2 text-sm">{(assessment?.contradictions_to_clarify||[]).map((x,i)=><p key={i} className="rounded-xl border border-warn p-3">{x}</p>)}{!(assessment?.contradictions_to_clarify.length)&&<p className="text-muted">Sem contradições estruturadas neste momento.</p>}</div></div>
    </div>
   </section>}

   {tab==='plan'&&<section className="space-y-4">
    <div className={card}><h2 className="text-lg font-bold">Plano médico</h2><textarea className="input mt-4 min-h-40" value={plan} onChange={e=>{setPlan(e.target.value);touch()}} placeholder="Plano introduzido/revisto pelo médico"/></div>
    <div className={card}><h2 className="font-bold">Pruebas sugeridas</h2>{assessment?.suggested_tests.length?<ul className="mt-3 space-y-2 text-sm">{assessment.suggested_tests.map((x,i)=><li key={i} className="rounded-xl border border-border p-3">{x.action}</li>)}</ul>:<p className="mt-2 text-sm text-muted">Sem sugestões executadas.</p>}</div>
    <div className={card}><h2 className="font-bold">Tratamento sugerido</h2>{medicationGate&&<div className={`mt-3 rounded-xl border p-3 text-sm ${medicationGate.actionable?'border-ok text-ok':'border-warn bg-warn-bg text-warn'}`}>{medicationGate.message}</div>}{assessment?.treatment_suggestions.length?<ul className="mt-3 space-y-2 text-sm">{assessment.treatment_suggestions.map((x,i)=><li key={i} className="rounded-xl border border-border p-3"><strong>{x.priority||'routine'}</strong> · {x.action}</li>)}</ul>:<p className="mt-2 text-sm text-muted">Sem tratamento gerado.</p>}</div>
    <div className="grid gap-4 md:grid-cols-2"><div className={card}><h2 className="font-bold">Destino</h2>{assessment?.disposition.map((x,i)=><p className="mt-2 text-sm" key={i}>{x.action}</p>)}</div><div className={card}><h2 className="font-bold">Reavaliação</h2>{assessment?.reassessment.map((x,i)=><p className="mt-2 text-sm" key={i}>{x.action}</p>)}</div></div>
   </section>}

   {tab==='export'&&<section className={card}><h2 className="text-lg font-bold">Revisão e exportação</h2><div className="mt-4 grid gap-2 text-sm">
    <label className="flex items-center gap-2"><input type="checkbox" checked={privacyAck} onChange={e=>setPrivacyAck(e.target.checked)}/> Identificadores diretos removidos; texto livre, metadados e privacidade revistos.</label>
    <label className="flex items-center gap-2"><input type="checkbox" checked={clinicianReviewed} onChange={e=>setClinicianReviewed(e.target.checked)}/> Médico reviu e valida o conteúdo clínico atual.</label>
    <p>{pending===0?'✓ Sem cartões MCDT pendentes':`STOP: ${pending} MCDT pendente(s) de aceitar/editar/rejeitar.`}</p>
    {diagnosticStale&&assessment&&<p className="text-warn">A análise diagnóstica está desatualizada; pode exportar apenas se o médico aceitar explicitamente o estado atual.</p>}
   </div><div className="mt-4 flex flex-wrap gap-2"><button disabled={exportBlocked} className="btn-primary" onClick={()=>void doExport('docx')}>Word (.docx)</button><button disabled={exportBlocked} className="btn-primary" onClick={()=>void doExport('pdf')}>PDF</button><button disabled={exportBlocked} className="btn-ghost" onClick={()=>void doExport('json')}>JSON</button></div>{exportBlocked&&<p role="status" className="mt-3 text-sm font-semibold text-danger">Exportação bloqueada até cumprir privacidade, revisão médica e resolução dos MCDT pendentes.</p>}</section>}
 </>;

 return <div className="space-y-4" data-testid="clinical-note-workspace">
   <section className={card}>
    <div className="flex flex-wrap items-start gap-3">
      <div className="min-w-0 flex-1"><p className="section-title">Nota clínica · episódio seudónimo</p><h1 className="mt-1 text-xl font-extrabold">Apoio ao diagnóstico</h1><p className="mt-1 break-all text-xs text-muted">{encounter}</p></div>
      <span className={`chip ${privacyStop?'border-danger text-danger':'border-ok text-ok'}`}>{privacyStop?'STOP privacidade':'Privacidade local OK'}</span>
      <span className="chip">{clinicianReviewed?'Revisto pelo médico':'Revisão pendente'}</span>
      <span className="chip">{assessment&&!diagnosticStale?'Apoio atualizado':'Apoio pendente'}</span>
    </div>
    <div className="mt-4 grid gap-3 sm:grid-cols-3">
      <label><span className="label">Idade</span><input aria-label="Idade" className="input" inputMode="decimal" value={age} onChange={e=>{setAge(e.target.value);touch()}} placeholder="anos"/></label>
      <label><span className="label">Sexo</span><select aria-label="Sexo" className="input" value={sex} onChange={e=>{setSex(e.target.value as ClinicalNotePayload['encounter']['sex']);touch()}}><option value="unknown">Não registado</option><option value="female">Feminino</option><option value="male">Masculino</option><option value="intersex">Intersexo</option></select></label>
      <label><span className="label">Origem / transferência</span><input aria-label="Origem" className="input" value={origin} onChange={e=>{setOrigin(e.target.value);touch()}} placeholder="Sem identificadores diretos"/></label>
    </div>
   </section>

   {privacyStop&&<div role="alert" className="rounded-xl border border-danger bg-surface p-4 text-sm font-semibold text-danger">STOP: possível identificador direto no texto. Remova-o antes de análise/exportação.</div>}
   {apiError&&<div role="alert" className="rounded-xl border border-danger bg-surface p-4 text-sm text-danger">{apiError}</div>}

   <nav className="overflow-x-auto" aria-label="Secções da nota"><div className="flex min-w-max gap-1 rounded-xl border border-border bg-surface p-1">
    {tabs.map(([id,label])=><button key={id} onClick={()=>setTab(id)} className={`rounded-lg px-3 py-2 text-sm font-semibold ${tab===id?'bg-primary text-primary-fg':'text-muted hover:bg-surface-2'}`} aria-current={tab===id?'page':undefined}>{label}{id==='mcdt'&&pending>0?` (${pending})`:''}</button>)}
   </div></nav>

   <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_18rem]">
     <div className="min-w-0">{content}</div>
     <aside className={`${card} h-fit lg:sticky lg:top-24`} aria-label="Timeline clínica">
       <div className="flex items-center gap-2"><h2 className="font-bold">Timeline</h2><span className="chip ml-auto">{timeline.length}</span></div>
       <div className="mt-4 space-y-3 border-l border-border pl-4">
         {timelineItems.length?timelineItems.map((x,i)=><div key={i} className="relative text-sm"><span className="absolute -left-[21px] top-1.5 h-2 w-2 rounded-full bg-primary"/><p className="text-xs font-semibold text-muted">{x.time_label}</p><p>{x.event}</p>{x.source&&<p className="mt-1 break-all text-[11px] text-muted">Proveniência: {x.source}</p>}</div>):<p className="text-sm text-muted">Sem eventos aceites ainda.</p>}
       </div>
     </aside>
   </div>
 </div>
}
