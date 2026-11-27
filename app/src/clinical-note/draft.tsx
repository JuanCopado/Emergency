import { createContext, Fragment, useCallback, useContext, useEffect, useRef, useState, type Dispatch, type ReactNode, type SetStateAction } from 'react';
import type { ClinicalAssessment, ClinicalNotePayload, PreparedUpload, ReviewState, TherapeuticConfirmations, TherapeuticPlan, TherapeuticReview, TherapeuticSections, TherapySelection } from './types';

export type NoteTab = 'history'|'exam'|'mcdt'|'problems'|'diagnostic'|'plan'|'export';
export type McdtCard = {
  id:string;kind:string;name:string;official:string;ai:string;state:ReviewState;
  provenance:string;prepared?:PreparedUpload;sourceFile?:File;privacyChecked:boolean;burnedChecked:boolean;
  sourceReference:string;findings?:string;impression?:string;
};
type Draft = {
  encounter: string; tab: NoteTab; language:ClinicalNotePayload['language']|null; age: string; ageUnit: 'years'|'months'; sex: ClinicalNotePayload['encounter']['sex'];
  origin: string; chief: string; hpi: string; pmh: string; meds: string; allergies: string;
  exam: string; problems: string; plan: string;
  vitalDraft: {time:string;bp:string;hr:string;rr:string;spo2:string;oxygen:string;temp:string;gcs:string};
  vitalSets: ClinicalNotePayload['exam']['vitals']; timeline: ClinicalNotePayload['timeline'];
  reports: ClinicalNotePayload['complementary_tests']; assessment: ClinicalAssessment|null;
  assessmentLanguage: ClinicalNotePayload['language']|null;
  diagnosticAlerts: {severity:string;code:string;message:string}[];
  medicationGate: {status:string;actionable:boolean;message:string}|null; diagnosticStale:boolean;
  mcdt: McdtCard[]; privacyAck:boolean; clinicianReviewed:boolean;
  draftKind:string; draftName:string; draftOfficial:string; draftAi:string; uploadName:string;
  therapySelection: TherapySelection; therapyWeight: string; therapyAllergiesReviewed: boolean;
  therapeuticPlan: TherapeuticPlan|null; therapeuticReview: TherapeuticReview|null;
  therapyGeneratedContext: string|null; therapyValidatedSnapshot: string|null;
  therapyOriginalSections: TherapeuticSections|null; therapyOriginalMetadata: string|null;
  therapyConfirmations: TherapeuticConfirmations; therapyEditing: boolean; therapyIncludePrevious: boolean;
};
let sequence = 0;
function emptyDraft(): Draft {
  return {
    encounter: globalThis.crypto.randomUUID?.() ?? `enc-${Date.now()}-${++sequence}`,
    tab:'history',language:null,age:'',ageUnit:'years',sex:'unknown',origin:'',chief:'',hpi:'',pmh:'',meds:'',allergies:'',exam:'',problems:'',plan:'',
    vitalDraft:{time:'',bp:'',hr:'',rr:'',spo2:'',oxygen:'',temp:'',gcs:''},vitalSets:[],timeline:[],
    reports:{laboratory:[],blood_gas:[],ecg:[],imaging:[],microbiology:[],other:[]},assessment:null,
    assessmentLanguage:null,diagnosticAlerts:[],medicationGate:null,diagnosticStale:true,
    mcdt:[],privacyAck:false,clinicianReviewed:false,draftKind:'Outro',draftName:'',draftOfficial:'',draftAi:'',uploadName:'',
    therapySelection:{label:'',module_id:null,selection:'manual'},therapyWeight:'',therapyAllergiesReviewed:false,
    therapeuticPlan:null,therapeuticReview:null,therapyGeneratedContext:null,therapyValidatedSnapshot:null,
    therapyOriginalSections:null,therapyOriginalMetadata:null,
    therapyConfirmations:{individualized:false,medication_safety_reviewed:false},therapyEditing:false,therapyIncludePrevious:false,
  };
}
function hasContent(draft: Draft) {
  return [draft.age,draft.origin,draft.chief,draft.hpi,draft.pmh,draft.meds,draft.allergies,draft.exam,
    draft.problems,draft.plan,draft.draftName,draft.draftOfficial,draft.draftAi,...Object.values(draft.vitalDraft)]
    .some(Boolean) || draft.sex!=='unknown' || draft.vitalSets.length>0 || draft.mcdt.length>0 || draft.assessment!==null ||
    draft.therapySelection.label.trim()!=='' || draft.therapyWeight!=='' || draft.therapeuticPlan!==null;
}
type Session = { draft:Draft; setDraft:Dispatch<SetStateAction<Draft>>; reset:()=>void; hasContent:boolean };
const DraftContext = createContext<Session|null>(null);

// A single episode stays only in this mounted application tree. No browser storage,
// global patient store or server persistence is used; closing the page destroys it.
export function ClinicalNoteDraftProvider({children}:{children:ReactNode}) {
  const [draft,setDraft] = useState(emptyDraft);
  const dirty = hasContent(draft);
  useEffect(() => {
    if (!dirty) return;
    const warn = (event:BeforeUnloadEvent) => {event.preventDefault();event.returnValue='';};
    window.addEventListener('beforeunload',warn);
    return () => window.removeEventListener('beforeunload',warn);
  },[dirty]);
  return <DraftContext.Provider value={{draft,setDraft,reset:()=>setDraft(emptyDraft()),hasContent:dirty}}>{children}</DraftContext.Provider>;
}

// Standalone page renderers get the same isolation. In App the provider lives above
// the routes, while an explicit new episode remounts the form and its request refs.
export function ClinicalNoteDraftScope({children}:{children:ReactNode}) {
  const session = useContext(DraftContext);
  if (!session) return <ClinicalNoteDraftProvider><ClinicalNoteDraftScope>{children}</ClinicalNoteDraftScope></ClinicalNoteDraftProvider>;
  return <Fragment key={session.draft.encounter}>{children}</Fragment>;
}

// eslint-disable-next-line react-refresh/only-export-components
export function useClinicalNoteDraft() {
  const session = useContext(DraftContext);
  if (!session) throw new Error('Clinical note draft requires its episode provider');
  return session;
}

// eslint-disable-next-line react-refresh/only-export-components
export function useNoteDraftField<K extends keyof Draft>(key:K):[Draft[K],Dispatch<SetStateAction<Draft[K]>>] {
  const {draft,setDraft} = useClinicalNoteDraft();
  const encounter = draft.encounter;
  const active = useRef(true);
  useEffect(()=>{active.current=true;return()=>{active.current=false;};},[]);
  const update = useCallback<Dispatch<SetStateAction<Draft[K]>>>(action => {
    if (!active.current) return;
    setDraft(current => {
      if (current.encounter!==encounter) return current;
      const value = typeof action==='function' ? (action as (previous:Draft[K])=>Draft[K])(current[key]) : action;
      return {...current,[key]:value};
    });
  },[encounter,key,setDraft]);
  return [draft[key],update];
}
