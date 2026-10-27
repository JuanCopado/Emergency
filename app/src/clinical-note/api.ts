import type { ClinicalNotePayload, DiagnosticApiResponse, InterpretationFields, PreparedUpload } from './types';
import { decodeExportFile, type ExportFormat } from '../lib/exportIntegrity';

const API_BASE=(import.meta.env.VITE_CLINICAL_NOTE_API_BASE ?? '').replace(/\/$/,'');

async function postJson<T>(path:string, body:unknown):Promise<T>{
  const response=await fetch(`${API_BASE}${path}`,{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    cache:'no-store',
    body:JSON.stringify(body),
  });
  const payload=await response.json().catch(()=>({error:'Invalid backend response'}));
  if(!response.ok) throw new Error(payload?.error || `Clinical-note API error ${response.status}`);
  return payload as T;
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
    });
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

export async function exportClinicalNote(note:ClinicalNotePayload,format:ExportFormat){
  const result=await postJson<unknown>('/api/clinical-note/export',{note,format});
  // Q05-R: wrong format, empty or corrupt base64 → error, never a partial download.
  const file=decodeExportFile(result,format);
  return {filename:file.filename,blob:new Blob([file.bytes],{type:file.mime})};
}

export function downloadBlob(filename:string,blob:Blob){
  const url=URL.createObjectURL(blob);
  const a=document.createElement('a');
  a.href=url;a.download=filename;a.click();
  // Revoking synchronously can cancel the download in some browsers; release it shortly after instead.
  setTimeout(()=>URL.revokeObjectURL(url),1000);
}
