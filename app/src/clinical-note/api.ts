import type { ClinicalNotePayload, DiagnosticApiResponse, InterpretationFields, PreparedUpload } from './types';

const API_BASE=(import.meta.env.VITE_CLINICAL_NOTE_API_BASE ?? '').replace(/\/$/,'');

/** The service could not be reached or did not answer in time. No clinical content is attached. */
export type ConnectionFailure='network'|'timeout';
export class ClinicalApiConnectionError extends Error{
  constructor(readonly failure:ConnectionFailure){
    super(failure==='timeout'?'clinical API request timed out':'clinical API unreachable');
    this.name='ClinicalApiConnectionError';
  }
}
// Deterministic calls are bounded; the provider call must outlast the server's own provider timeout (max 180 s)
// so the client never gives up while the server may still be forwarding the image.
export const REQUEST_TIMEOUT_MS=60_000;
export const PROVIDER_TIMEOUT_MS=200_000;

async function postJson<T>(path:string, body:unknown, timeoutMs:number=REQUEST_TIMEOUT_MS):Promise<T>{
  const serialized=JSON.stringify(body); // a serialization TypeError is a bug, not a connection failure
  const controller=new AbortController();
  let timedOut=false;
  const timer=setTimeout(()=>{timedOut=true;controller.abort();},timeoutMs);
  try{
    const response=await fetch(`${API_BASE}${path}`,{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      cache:'no-store',
      body:serialized,
      signal:controller.signal,
    });
    const payload=await response.json().catch(error=>{
      // Reading the body can fail after HTTP 200 headers. Never turn that
      // failure into a resolved clinical result or expose a parser's body text.
      if(timedOut || error instanceof TypeError) throw error;
      throw new Error('Invalid backend response');
    });
    if(!response.ok) throw new Error(payload?.error || `Clinical-note API error ${response.status}`);
    return payload as T;
  }catch(error){
    // Server answers keep their original error; nothing is retried here.
    if(timedOut) throw new ClinicalApiConnectionError('timeout');
    if(error instanceof TypeError) throw new ClinicalApiConnectionError('network');
    throw error;
  }finally{
    clearTimeout(timer);
  }
}

function arrayBufferToBase64(buffer:ArrayBuffer){
  const bytes=new Uint8Array(buffer);
  let binary='';
  const chunk=0x8000;
  for(let i=0;i<bytes.length;i+=chunk){
    binary+=String.fromCharCode(...bytes.subarray(i,Math.min(i+chunk,bytes.length)));
  }
  return btoa(binary);
}

export async function prepareClinicalUpload(file:File,explicitKind?:string){
  if(file.size>12*1024*1024) throw new Error('Ficheiro superior ao limite de 12 MB.');
  const content_base64=arrayBufferToBase64(await file.arrayBuffer());
  return postJson<PreparedUpload>('/api/clinical-note/upload/prepare',{
    filename:file.name,mime_type:file.type || 'application/octet-stream',content_base64,explicit_kind:explicitKind,
  });
}

export async function interpretClinicalUpload(
  file:File,
  prepared:PreparedUpload,
  privacyChecked:boolean,
  burnedInIdentifiersChecked:boolean,
){
  if(file.size>12*1024*1024) throw new Error('Ficheiro superior ao limite de 12 MB.');
  const content_base64=arrayBufferToBase64(await file.arrayBuffer());
  return postJson<{prepared:PreparedUpload;review_required:boolean;persisted:false}>(
    '/api/clinical-note/upload/interpret',{
      prepared,content_base64,
      privacy_checked:privacyChecked,
      burned_in_identifiers_checked:burnedInIdentifiersChecked,
    },PROVIDER_TIMEOUT_MS);
}

export async function acceptClinicalUpload(
  note:ClinicalNotePayload,
  prepared:PreparedUpload,
  clinicianEdit:Partial<InterpretationFields> & {time_label?:string|null},
  privacyChecked:boolean,
  burnedInIdentifiersChecked:boolean,
){
  return postJson<{note:ClinicalNotePayload}>('/api/clinical-note/upload/accept',{
    note,prepared,clinician_edit:clinicianEdit,
    privacy_checked:privacyChecked,
    burned_in_identifiers_checked:burnedInIdentifiersChecked,
  });
}

export async function preflightClinicalNote(note:ClinicalNotePayload){
  return postJson<{blocked:boolean;findings:{severity:string;code:string;message:string}[]}>('/api/clinical-note/preflight',{note});
}

export async function analyzeClinicalNote(note:ClinicalNotePayload){
  return postJson<DiagnosticApiResponse>('/api/clinical-note/analyze',{note});
}

function base64ToBlob(content:string,mime:string){
  const binary=atob(content);
  const bytes=new Uint8Array(binary.length);
  for(let i=0;i<binary.length;i++) bytes[i]=binary.charCodeAt(i);
  return new Blob([bytes],{type:mime});
}

export async function exportClinicalNote(note:ClinicalNotePayload,format:'docx'|'pdf'|'json'){
  const result=await postJson<{filename:string;mime_type:string;content_base64:string}>('/api/clinical-note/export',{note,format});
  return {filename:result.filename,blob:base64ToBlob(result.content_base64,result.mime_type)};
}

export function downloadBlob(filename:string,blob:Blob){
  const url=URL.createObjectURL(blob);
  const a=document.createElement('a');
  a.href=url;a.download=filename;a.click();
  setTimeout(()=>URL.revokeObjectURL(url),0);
}
