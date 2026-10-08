import { useMemo, useState } from 'react';
import {
  acceptClinicalUpload,
  analyzeClinicalNote,
  appendClinicalAuditEvent,
  downloadBlob,
  exportClinicalNote,
  interpretClinicalUpload,
  preflightClinicalNote,
  prepareClinicalUpload,
  readClinicalAuditTrail,
} from '../clinical-note/api';
import type {
  AuditTrailResponse,
  ClinicalAssessment,
  ClinicalNotePayload,
  DiagnosticProvenance,
  ExportSignature,
  PreparedUpload,
  ReviewerAttestationInput,
  ReportItem,
  ReviewState,
} from '../clinical-note/types';

type Tab='history'|'exam'|'mcdt'|'problems'|'diagnostic'|'plan'|'export';
type McdtCard={
  id:string;kind:string;name:string;official:string;ai:string;state:ReviewState;
  provenance:string;prepared?:PreparedUpload;sourceFile?:File;privacyChecked:boolean;burnedChecked:boolean;
  sourceReference:string;
};
type AuditEvent={id:string;at:string;action:string;target:string;detail:string};

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
 const [diagnosticAlerts,setDiagnosticAlerts]=useState<{severity:string;code:string;message:string}[]>([]);
 const [medicationGate,setMedicationGate]=useState<{status:string;actionable:boolean;message:string}|null>(null);
 const [diagnosticStale,setDiagnosticStale]=useState(true);
 const [staleExportAck,setStaleExportAck]=useState(false);
 const [criticalReviewAck,setCriticalReviewAck]=useState(false);
 const [mcdt,setMcdt]=useState<McdtCard[]>([]); const [privacyAck,setPrivacyAck]=useState(false);
 const [clinicianReviewed,setClinicianReviewed]=useState(false);
 const [draftKind,setDraftKind]=useState('Outro'); const [draftName,setDraftName]=useState('');
 const [draftOfficial,setDraftOfficial]=useState(''); const [draftAi,setDraftAi]=useState('');
 const [uploadName,setUploadName]=useState(''); const [apiBusy,setApiBusy]=useState(false);
 const [apiError,setApiError]=useState('');
 const [safetyContext,setSafetyContext]=useState({
   weightKg:'',egfr:'',creatinine:'',hepatic:'unknown',pregnancy:'unknown',
   anticoagulation:'unknown',anticoagulantAgent:'',allergyStatus:'unknown',
 });
 const [auditTrail,setAuditTrail]=useState<AuditEvent[]>([]);
 const [serverAudit,setServerAudit]=useState<AuditTrailResponse|null>(null);
 const [diagnosticProvenance,setDiagnosticProvenance]=useState<DiagnosticProvenance|null>(null);
 const [exportRevision,setExportRevision]=useState(0);
 const [reviewerCode,setReviewerCode]=useState('');
 const [reviewerRole,setReviewerRole]=useState<ReviewerAttestationInput['reviewer_role']>('emergency_physician');
 const [lastExportSignature,setLastExportSignature]=useState<ExportSignature|null>(null);
 const encounter=useMemo(()=>crypto.randomUUID?.() ?? `enc-${Date.now()}`,[]);
 const allAccepted=Object.values(reports).flat();
 const freeText=[origin,chief,hpi,pmh,meds,allergies,exam,problems,plan,
   ...allAccepted.flatMap(x=>[x.official_report||'',x.ai_interpretation||'',x.findings||'',x.impression||'']),
   ...mcdt.flatMap(x=>[x.official,x.ai])].join('\n');
 const privacyStop=directId.test(freeText);
 const pending=mcdt.filter(x=>x.state==='pending').length;
 const safetySummary=[
   safetyContext.weightKg?`Peso ${safetyContext.weightKg} kg`:null,
   safetyContext.egfr?`eGFR ${safetyContext.egfr} mL/min/1.73m²`:null,
   safetyContext.creatinine?`Creatinina ${safetyContext.creatinine}`:null,
   `Função hepática ${safetyContext.hepatic}`,
   `Gravidez ${safetyContext.pregnancy}`,
   `Anticoagulação ${safetyContext.anticoagulation}${safetyContext.anticoagulantAgent?` (${safetyContext.anticoagulantAgent})`:''}`,
   `Estado de alergias ${safetyContext.allergyStatus}`,
 ].filter(Boolean).join(' · ');
 const safetyIncomplete=safetyContext.allergyStatus==='unknown'||!safetyContext.weightKg||safetyContext.anticoagulation==='unknown';
 const criticalRiskPresent=Boolean(assessment?.must_not_miss.length)||diagnosticAlerts.some(x=>x.severity==='RED_FLAG');
 const reviewerReady=reviewerCode.trim().length>=3;
 const exportBlocked=privacyStop||!privacyAck||!clinicianReviewed||!reviewerReady||pending>0||apiBusy||(Boolean(assessment)&&diagnosticStale&&!staleExportAck)||(criticalRiskPresent&&!criticalReviewAck);

 function appendAudit(action:string,target:string,detail:string){
   setAuditTrail(current=>[...current,{id:crypto.randomUUID?.() ?? `audit-${Date.now()}-${current.length}`,at:new Date().toISOString(),action,target,detail}]);
 }
 async function refreshServerAudit(note?:ClinicalNotePayload){
   try{
     setServerAudit(await readClinicalAuditTrail(note ?? buildNote()));
   }catch{
     setServerAudit(null);
   }
 }
 function appendServerAudit(action:string,target:string,detail:string,metadata?:Record<string,unknown>){
   const note=buildNote();
   void appendClinicalAuditEvent(note,action,target,detail,metadata)
     .then(()=>refreshServerAudit(note))
     .catch(()=>setServerAudit(null));
 }
 function touch(){
   setClinicianReviewed(false);
   setDiagnosticStale(true);
   setStaleExportAck(false);
   setCriticalReviewAck(false);
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
       medication_discrepancies:[`[SAFETY_CONTEXT] ${safetySummary}`],
       allergies:lines(allergies).map(substance=>({substance,class:null,reaction:null,severity:null,confirmed:null})),
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
       reviewed:clinicianReviewed,reviewer_role:clinicianReviewed?reviewerRole:null,
       reviewed_at:clinicianReviewed?new Date().toISOString():null,
       changes_made:clinicianReviewed?`Clinician reviewed current structured note. Export revision ${exportRevision+1}.`:null,
     },
     privacy:{
       mode:'clinical_pseudonymized',direct_identifiers_removed:privacyAck,free_text_screened:privacyAck,
       source_metadata_checked:privacyAck,burned_in_identifiers_checked:privacyAck,export_allowed:!exportBlocked,
       privacy_notes:auditTrail.slice(-12).map(event=>`AUDIT ${event.at} · ${event.action} · ${event.target} · ${event.detail}`),
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
       provenance:`${prepared.processing.modules.join(' · ')} · ${prepared.processing.status}`,prepared,sourceFile:file,
       privacyChecked:prepared.privacy.status==='PASS',burnedChecked:!prepared.privacy.burned_in_identifier_review_required,
       sourceReference:`sha256:${prepared.sha256}`,
     }]);
     setDraftOfficial('');setDraftAi('');appendAudit('MCDT_CREATED',id,`Upload preparado: ${file.name}`);touch();
   }catch(e){setApiError(e instanceof Error?e.message:'Falha ao preparar upload clínico.');}
   finally{setApiBusy(false);}
 }
 async function interpretCard(id:string){
   const card=mcdt.find(x=>x.id===id);
   if(!card?.prepared||!card.sourceFile) return;
   if(card.prepared.privacy.status==='STOP'){
     setApiError('STOP de privacidade no ficheiro: remova os identificadores antes de interpretar.');
     return;
   }
   if(card.prepared.privacy.manual_file_privacy_review_required&&!card.privacyChecked){
     setApiError('Reveja primeiro metadados/identificadores do ficheiro.');
     return;
   }
   if(card.prepared.privacy.burned_in_identifier_review_required&&!card.burnedChecked){
     setApiError('Reveja primeiro identificadores visíveis/burned-in.');
     return;
   }
   setApiError('');setApiBusy(true);
   try{
     const result=await interpretClinicalUpload(
       card.sourceFile,card.prepared,card.privacyChecked,card.burnedChecked
     );
     const prepared=result.prepared;
     setMcdt(v=>v.map(x=>x.id===id?{
       ...x,
       prepared,
       official:prepared.extracted.official_report||x.official,
       ai:prepared.extracted.ai_interpretation||x.ai,
       provenance:`${prepared.processing.modules.join(' · ')} · ${prepared.processing.status} · ${prepared.processing.provider||'provider'} / ${prepared.processing.model||'model'}`,
       privacyChecked:true,
       burnedChecked:true,
       state:'pending',
     }:x));
     touch();
   }catch(e){setApiError(e instanceof Error?e.message:'Falha na interpretação clínica configurada.');}
   finally{setApiBusy(false);}
 }
 function addManualMcdt(){
   if(!draftName.trim()&&!draftOfficial.trim()&&!draftAi.trim()) return;
   const id=`${Date.now()}-${mcdt.length}`;
   setMcdt(x=>[...x,{id,kind:draftKind,name:draftName||draftKind,official:draftOfficial,ai:draftAi,state:'pending',
     provenance:'entrada manual → revisão médica',privacyChecked:true,burnedChecked:true,sourceReference:`ui:${id}`}]);
   setDraftName('');setDraftOfficial('');setDraftAi('');appendAudit('MCDT_CREATED',id,`Entrada manual: ${draftName||draftKind}`);appendServerAudit('MCDT_CREATED',id,`Entrada manual: ${draftName||draftKind}`);touch();
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
       appendAudit('MCDT_ACCEPTED',id,card.name);void refreshServerAudit(result.note);touch();
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
   setMcdt(v=>v.map(x=>x.id===id?{...x,state:'accepted'}:x));appendAudit('MCDT_ACCEPTED',id,card.name);appendServerAudit('MCDT_ACCEPTED',id,card.name);touch();
 }
 function editCard(id:string,patch:Partial<McdtCard>){
   const existing=mcdt.find(x=>x.id===id);
   if(existing?.state==='accepted') removePersisted(existing);
   setMcdt(v=>v.map(x=>x.id===id?{...x,...patch,state:'pending'}:x));appendAudit('MCDT_EDITED',id,'Conteúdo alterado; revisão pendente.');touch();
 }
 function rejectCard(id:string){
   const existing=mcdt.find(x=>x.id===id);
   if(existing?.state==='accepted') removePersisted(existing);
   setMcdt(v=>v.map(x=>x.id===id?{...x,state:'rejected'}:x));appendAudit('MCDT_REJECTED',id,existing?.name||id);appendServerAudit('MCDT_REJECTED',id,existing?.name||id);touch();
 }
 async function runDiagnostic(){
   setApiError('');setApiBusy(true);
   try{
     const result=await analyzeClinicalNote(buildNote());
     if(result.blocked){setApiError(result.issues.map(x=>x.message).join(' · ')||'Análise bloqueada.');return;}
     setAssessment(result.assessment);
     setDiagnosticProvenance(result.diagnostic_provenance ?? null);
     appendAudit('DIAGNOSTIC_ANALYSIS','assessment',`Atualizado com ${result.assessment?.likely_diagnoses.length??0} diagnóstico(s) provável(is).`);
     setDiagnosticAlerts([
       ...(result.signals||[]).map(x=>({severity:x.weight>=2?'RED_FLAG':'ALERT',code:x.code,message:x.label})),
       ...result.issues.filter(x=>x.severity==='ALERT'||x.severity==='CAUTION').map(x=>({severity:x.severity,code:x.code,message:x.message})),
     ]);
     setMedicationGate(result.medication_safety_gate);setDiagnosticStale(false);setClinicianReviewed(false);setCriticalReviewAck(false);void refreshServerAudit(result.note ?? buildNote());
   }catch(e){setApiError(e instanceof Error?e.message:'Backend clínico indisponível.');}
   finally{setApiBusy(false);}
 }
 async function doExport(format:'docx'|'pdf'|'json'){
   setApiError('');setApiBusy(true);
   try{
     const note=buildNote();
     const preflight=await preflightClinicalNote(note);
     if(preflight.blocked){setApiError(preflight.findings.map(x=>x.message).join(' · '));return;}
     const out=await exportClinicalNote(note,format,{reviewer_code:reviewerCode.trim(),reviewer_role:reviewerRole});
     if(out.provenance) setDiagnosticProvenance(out.provenance);
     setLastExportSignature(out.exportSignature);
     const nextRevision=exportRevision+1;
     setExportRevision(nextRevision);
     appendAudit('EXPORT',format,`Revisão ${nextRevision}: ${out.filename}`);
     void refreshServerAudit(note);
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
    <div className="grid gap-4 md:grid-cols-3"><label><span className="label">Antecedentes · um por linha</span><textarea className="input min-h-24" value={pmh} onChange={e=>{setPmh(e.target.value);touch()}}/></label><label><span className="label">Medicação habitual · um por linha</span><textarea className="input min-h-24" value={meds} onChange={e=>{setMeds(e.target.value);touch()}}/></label><label><span className="label">Alergias · uma por linha</span><textarea className="input min-h-24" value={allergies} onChange={e=>{setAllergies(e.target.value);touch()}} placeholder="Fármaco + reação"/></label></div>
    <div className="rounded-2xl border border-border bg-surface-2 p-4">
      <div className="flex flex-wrap items-center gap-2"><h3 className="font-bold">Contexto de segurança farmacológica</h3>{safetyIncomplete&&<span className="chip border-warn text-warn">Dados críticos incompletos</span>}</div>
      <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <label><span className="label">Peso (kg)</span><input className="input" inputMode="decimal" value={safetyContext.weightKg} onChange={e=>{setSafetyContext(v=>({...v,weightKg:e.target.value}));touch()}}/></label>
        <label><span className="label">eGFR</span><input className="input" inputMode="decimal" value={safetyContext.egfr} onChange={e=>{setSafetyContext(v=>({...v,egfr:e.target.value}));touch()}} placeholder="mL/min/1.73m²"/></label>
        <label><span className="label">Creatinina</span><input className="input" value={safetyContext.creatinine} onChange={e=>{setSafetyContext(v=>({...v,creatinine:e.target.value}));touch()}} placeholder="valor + unidade"/></label>
        <label><span className="label">Função hepática</span><select className="input" value={safetyContext.hepatic} onChange={e=>{setSafetyContext(v=>({...v,hepatic:e.target.value}));touch()}}><option value="unknown">Não conhecida</option><option value="normal">Sem disfunção conhecida</option><option value="impaired">Disfunção conhecida/suspeita</option></select></label>
        <label><span className="label">Gravidez</span><select className="input" value={safetyContext.pregnancy} onChange={e=>{setSafetyContext(v=>({...v,pregnancy:e.target.value}));touch()}}><option value="unknown">Não conhecido / aplicabilidade não definida</option><option value="no">Não</option><option value="yes">Sim</option><option value="not_applicable">Não aplicável</option></select></label>
        <label><span className="label">Anticoagulação</span><select className="input" value={safetyContext.anticoagulation} onChange={e=>{setSafetyContext(v=>({...v,anticoagulation:e.target.value}));touch()}}><option value="unknown">Não conhecida</option><option value="no">Não</option><option value="yes">Sim</option></select></label>
        <label><span className="label">Anticoagulante</span><input className="input" value={safetyContext.anticoagulantAgent} onChange={e=>{setSafetyContext(v=>({...v,anticoagulantAgent:e.target.value}));touch()}} disabled={safetyContext.anticoagulation!=='yes'}/></label>
        <label><span className="label">Estado de alergias</span><select className="input" value={safetyContext.allergyStatus} onChange={e=>{setSafetyContext(v=>({...v,allergyStatus:e.target.value}));touch()}}><option value="unknown">Não registado</option><option value="none_known">Sem alergias conhecidas</option><option value="known">Alergia(s) conhecida(s)</option></select></label>
      </div>
    </div>
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
      {x.prepared?.processing.status==='vision_interpreted'&&<div className="mt-2 rounded-xl border border-warn p-3 text-sm"><strong>Interpretação IA proposta — requer revisão médica.</strong><p className="mt-1 text-xs text-muted">Provider: {x.prepared.processing.provider||'—'} · Modelo: {x.prepared.processing.model||'—'} · Confiança: {x.prepared.processing.confidence||'—'}</p>{x.prepared.processing.impression&&<p className="mt-2">Impressão: {x.prepared.processing.impression}</p>}{x.prepared.processing.limitations?.length?<p className="mt-1 text-xs text-muted">Limitações: {x.prepared.processing.limitations.join(' · ')}</p>:null}</div>}
      <div className="mt-3 flex flex-wrap gap-2">{x.prepared?.processing.status==='routed_external'&&<button className="btn-ghost" disabled={apiBusy||x.prepared.privacy.status==='STOP'||(x.prepared.privacy.manual_file_privacy_review_required&&!x.privacyChecked)||(x.prepared.privacy.burned_in_identifier_review_required&&!x.burnedChecked)} onClick={()=>void interpretCard(x.id)}>Interpretar com módulo IA</button>}<button className="btn-primary" disabled={apiBusy||x.prepared?.privacy.status==='STOP'} onClick={()=>void acceptCard(x.id)}>Aceitar</button><button className="btn-ghost" onClick={()=>editCard(x.id,{})}>Editar</button><button className="btn-ghost text-danger" onClick={()=>rejectCard(x.id)}>Rejeitar</button></div></article>)}
   </section>}

   {tab==='problems'&&<section className={card}><h2 className="text-lg font-bold">Problemas</h2><p className="mt-1 text-sm text-muted">Lista numerada editável: ativo · a melhorar · resolvido · por esclarecer.</p><textarea className="input mt-4 min-h-56" value={problems} onChange={e=>{setProblems(e.target.value);touch()}} placeholder={"1. [ativo] …\n2. [por esclarecer] …"}/>{assessment?.active_problems.length? <div className="mt-4 rounded-xl border border-border p-3"><p className="text-xs font-bold uppercase text-muted">Problemas sugeridos pelo motor · requer revisão</p><ul className="mt-2 space-y-1 text-sm">{assessment.active_problems.map((x,i)=><li key={i}>• {x}</li>)}</ul></div>:null}</section>}

   {tab==='diagnostic'&&<section className="space-y-4">
    <div className={card}><div className="flex flex-wrap items-center gap-3"><div><h2 className="text-lg font-bold">Apoio diagnóstico</h2><p className="text-sm text-muted">Executado apenas sobre dados aceites e após preflight de privacidade.</p></div><button className="btn-primary ml-auto" disabled={apiBusy||privacyStop} onClick={()=>void runDiagnostic()}>{apiBusy?'A processar…':'Atualizar apoio diagnóstico'}</button></div>{diagnosticStale&&assessment&&<p className="mt-3 text-sm font-semibold text-warn">Os dados mudaram desde a última análise; resultado marcado como desatualizado.</p>}</div>
    {diagnosticAlerts.length>0&&<div className={card}><h2 className="font-bold text-danger">Alertas / red flags</h2><div className="mt-3 grid gap-2 md:grid-cols-2">{diagnosticAlerts.map((x,i)=><div key={`${x.code}-${i}`} className="rounded-xl border border-danger p-3 text-sm"><div className="font-bold">{x.severity} · {x.code}</div><p className="mt-1">{x.message}</p></div>)}</div></div>}
    {assessment?.problem_representation&&<div className={card}><h2 className="font-bold">Representação do problema</h2><p className="mt-2 text-sm">{assessment.problem_representation}</p></div>}
    {assessment?.limitations.length?<div className={card}><h2 className="font-bold text-warn">Limitações do apoio diagnóstico</h2><ul className="mt-2 space-y-1 text-sm">{assessment.limitations.map((x,i)=><li key={i}>• {x}</li>)}</ul></div>:null}
    {diagnosticProvenance&&<div className={card}><div className="flex flex-wrap items-center gap-2"><h2 className="font-bold">Proveniência diagnóstica</h2><span className="chip">API {diagnosticProvenance.api_version}</span></div><div className="mt-3 grid gap-2 text-xs text-muted"><p><strong>Build:</strong> <span className="break-all">{diagnosticProvenance.build_sha}</span></p><p><strong>Regras:</strong> <span className="break-all">{diagnosticProvenance.diagnostic_rules_sha256||'indisponível'}</span></p><p><strong>Módulos:</strong> {diagnosticProvenance.source_modules.join(' · ')||'—'}</p></div>{diagnosticProvenance.module_sources.length?<div className="mt-3 space-y-1 text-[11px] text-muted">{diagnosticProvenance.module_sources.map(source=><p key={source.module_id}><strong>{source.module_id}</strong> · {source.bundle||'bundle não resolvido'} · <span className="break-all">{source.sha256||'digest indisponível'}</span></p>)}</div>:null}</div>}
    <div className="grid gap-4 lg:grid-cols-2">
      {([
        ['Must not miss',assessment?.must_not_miss||[]],
        ['Mais provável',assessment?.likely_diagnoses||[]],
        ['Diferencial',assessment?.differential_diagnoses||[]],
      ] as const).map(([h,items])=><div className={card} key={h}><h2 className={`font-bold ${h==='Must not miss'?'text-danger':''}`}>{h}</h2>{items.length?<div className="mt-3 space-y-3">{items.map((d,i)=><div key={i} className={`rounded-xl border p-3 ${h==='Must not miss'?'border-danger':'border-border'}`}><div className="flex items-center gap-2"><strong>{d.diagnosis}</strong><span className="chip ml-auto">{d.confidence}</span></div>{d.evidence_for.length>0&&<p className="mt-2 text-sm"><strong>A favor:</strong> {d.evidence_for.join(' · ')}</p>}{d.evidence_against.length>0&&<p className="mt-1 text-sm"><strong>Contra:</strong> {d.evidence_against.join(' · ')}</p>}{d.missing_discriminating_data.length>0&&<p className="mt-1 text-xs text-muted"><strong>Falta discriminar:</strong> {d.missing_discriminating_data.join(' · ')}</p>}<p className="mt-1 text-xs text-muted">Módulos: {d.source_modules.join(' · ')||'—'}</p></div>)}</div>:<p className="mt-3 text-sm text-muted">Sem resultado executado/aceite.</p>}</div>)}
      <div className={card}><h2 className="font-bold">Dados em falta / contradições</h2><div className="mt-3 space-y-2 text-sm">{(assessment?.contradictions_to_clarify||[]).map((x,i)=><p key={i} className="rounded-xl border border-warn p-3">{x}</p>)}{!(assessment?.contradictions_to_clarify.length)&&<p className="text-muted">Sem contradições estruturadas neste momento.</p>}</div></div>
    </div>
   </section>}

   {tab==='plan'&&<section className="space-y-4">
    <div className={card}><h2 className="text-lg font-bold">Plano médico</h2>{safetyContext.allergyStatus==='unknown'&&<div className="mt-3 rounded-xl border border-warn bg-warn-bg p-3 text-sm text-warn"><strong>Alergias não registadas.</strong> O sistema não deve interpretar campo vazio como “sem alergias conhecidas”.</div>}<textarea className="input mt-4 min-h-40" value={plan} onChange={e=>{setPlan(e.target.value);touch()}} placeholder="Plano introduzido/revisto pelo médico"/></div>
    <div className={card}><h2 className="font-bold">Pruebas sugeridas</h2>{assessment?.suggested_tests.length?<ul className="mt-3 space-y-2 text-sm">{assessment.suggested_tests.map((x,i)=><li key={i} className="rounded-xl border border-border p-3">{x.action}</li>)}</ul>:<p className="mt-2 text-sm text-muted">Sem sugestões executadas.</p>}</div>
    <div className={card}><h2 className="font-bold">Tratamento sugerido</h2>{assessment?.treatment_suggestions.length&&safetyIncomplete?<div className="mt-3 rounded-xl border border-warn bg-warn-bg p-3 text-sm text-warn"><strong>Contexto farmacológico incompleto.</strong> Confirmar peso, estado de alergias, anticoagulação e outros dados pertinentes antes de tornar uma sugestão medicamentosa acionável.</div>:null}{medicationGate&&<div className={`mt-3 rounded-xl border p-3 text-sm ${medicationGate.actionable?'border-ok text-ok':'border-warn bg-warn-bg text-warn'}`}>{medicationGate.message}</div>}{assessment?.treatment_suggestions.length?<ul className="mt-3 space-y-2 text-sm">{assessment.treatment_suggestions.map((x,i)=><li key={i} className="rounded-xl border border-border p-3"><strong>{x.priority||'routine'}</strong> · {x.action}</li>)}</ul>:<p className="mt-2 text-sm text-muted">Sem tratamento gerado.</p>}</div>
    <div className="grid gap-4 md:grid-cols-2"><div className={card}><h2 className="font-bold">Destino</h2>{assessment?.disposition.map((x,i)=><p className="mt-2 text-sm" key={i}>{x.action}</p>)}</div><div className={card}><h2 className="font-bold">Reavaliação</h2>{assessment?.reassessment.map((x,i)=><p className="mt-2 text-sm" key={i}>{x.action}</p>)}</div></div>
   </section>}

   {tab==='export'&&<section className={card}><h2 className="text-lg font-bold">Revisão e exportação</h2>
   <div className="mt-4 rounded-xl border border-border bg-surface-2 p-4">
    <h3 className="font-bold">Atestação do revisor</h3>
    <p className="mt-1 text-xs text-muted">Use um código profissional/pseudónimo local. O backend não persiste o código em claro; guarda apenas um fingerprint HMAC.</p>
    <div className="mt-3 grid gap-3 md:grid-cols-2">
      <label><span className="label">Código do revisor</span><input aria-label="Código do revisor" className="input" value={reviewerCode} onChange={e=>{setReviewerCode(e.target.value);setClinicianReviewed(false)}} placeholder="ex.: MED-URG-01"/></label>
      <label><span className="label">Papel</span><select aria-label="Papel do revisor" className="input" value={reviewerRole} onChange={e=>{setReviewerRole(e.target.value as ReviewerAttestationInput['reviewer_role']);setClinicianReviewed(false)}}><option value="emergency_physician">Médico de urgência</option><option value="treating_clinician">Médico assistente</option><option value="consultant">Consultor/especialista</option><option value="resident">Interno/residente</option><option value="other_clinician">Outro médico</option></select></label>
    </div>
    {!reviewerReady&&<p className="mt-2 text-xs font-semibold text-warn">É necessário um código pseudónimo com pelo menos 3 caracteres para assinar a exportação.</p>}
   </div>
   <div className="mt-4 grid gap-2 text-sm">
    <label className="flex items-center gap-2"><input type="checkbox" checked={privacyAck} onChange={e=>setPrivacyAck(e.target.checked)}/> Identificadores diretos removidos; texto livre, metadados e privacidade revistos.</label>
    <label className="flex items-center gap-2"><input type="checkbox" checked={clinicianReviewed} onChange={e=>setClinicianReviewed(e.target.checked)}/> Médico reviu e valida o conteúdo clínico atual.</label>
    <p>{pending===0?'✓ Sem cartões MCDT pendentes':`STOP: ${pending} MCDT pendente(s) de aceitar/editar/rejeitar.`}</p>
    {diagnosticStale&&assessment&&<>
      <p className="text-warn">A análise diagnóstica está desatualizada.</p>
      <label className="flex items-start gap-2 rounded-xl border border-warn bg-warn-bg p-3 text-warn"><input type="checkbox" checked={staleExportAck} onChange={e=>setStaleExportAck(e.target.checked)}/><span><strong>Aceito exportar com apoio diagnóstico desatualizado.</strong> A decisão clínica atual foi revista independentemente pelo médico.</span></label>
    </>}
    {criticalRiskPresent&&<label className="flex items-start gap-2 rounded-xl border border-danger p-3 text-danger"><input type="checkbox" checked={criticalReviewAck} onChange={e=>setCriticalReviewAck(e.target.checked)}/><span><strong>Revisei explicitamente os must-not-miss / red flags.</strong> O plano e o destino refletem esta revisão.</span></label>}
    <div className="mt-4 rounded-xl border border-border p-3"><div className="flex flex-wrap items-center justify-between gap-3"><strong>Audit trail</strong><div className="flex gap-2"><span className="text-xs text-muted">sessão · {auditTrail.length}</span>{serverAudit&&<span className={`chip ${serverAudit.chain_valid?'border-ok text-ok':'border-danger text-danger'}`}>servidor {serverAudit.chain_valid?'HMAC OK':'CHAIN FAIL'} · {serverAudit.storage}</span>}</div></div>{serverAudit?.events.length?<ol className="mt-2 max-h-48 space-y-1 overflow-auto text-xs text-muted">{serverAudit.events.slice().reverse().map(event=><li key={event.event_id}>{new Date(event.timestamp).toLocaleTimeString()} · <strong>{event.action}</strong> · {event.target} · #{event.sequence}</li>)}</ol>:auditTrail.length?<ol className="mt-2 max-h-48 space-y-1 overflow-auto text-xs text-muted">{auditTrail.slice().reverse().map(event=><li key={event.id}>{new Date(event.at).toLocaleTimeString()} · <strong>{event.action}</strong> · {event.target} · {event.detail}</li>)}</ol>:<p className="mt-2 text-xs text-muted">Sem eventos ainda.</p>}<button type="button" className="btn-ghost mt-3" onClick={()=>void refreshServerAudit()}>Verificar cadeia no servidor</button></div>
    {lastExportSignature&&<div className="mt-4 rounded-xl border border-ok p-3 text-xs"><div className="flex flex-wrap items-center justify-between gap-2"><strong className="text-ok">Exportação autenticada</strong><span className="chip">{lastExportSignature.algorithm} · {lastExportSignature.key_id}</span></div><div className="mt-2 space-y-1 text-muted"><p><strong>Revisor:</strong> {lastExportSignature.reviewer_fingerprint} · {lastExportSignature.reviewer_role}</p><p><strong>Conteúdo SHA-256:</strong> <span className="break-all">{lastExportSignature.content_sha256}</span></p><p><strong>Assinatura:</strong> <span className="break-all">{lastExportSignature.signature_hmac_sha256}</span></p><p><strong>Build:</strong> <span className="break-all">{lastExportSignature.build_sha}</span></p></div></div>}
   </div><div className="mt-4 flex flex-wrap gap-2"><button disabled={exportBlocked} className="btn-primary" onClick={()=>void doExport('docx')}>Word (.docx)</button><button disabled={exportBlocked} className="btn-primary" onClick={()=>void doExport('pdf')}>PDF</button><button disabled={exportBlocked} className="btn-ghost" onClick={()=>void doExport('json')}>JSON</button></div>{exportBlocked&&<p role="status" className="mt-3 text-sm font-semibold text-danger">Exportação bloqueada até cumprir privacidade, atestação do revisor, revisão médica, resolução dos MCDT pendentes e, quando aplicável, revisão explícita de análise desatualizada e must-not-miss/red flags.</p>}</section>}
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
