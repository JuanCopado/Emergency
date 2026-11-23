/**
 * LAB_LAYER7_MARKER · Stage-1 formative study, arm B ONLY. SIMULATED_LAB_HARNESS_ONLY.
 * This module and everything under src/lab is loaded only through a dynamic import guarded by `!import.meta.env.PROD` and
 * VITE_LAB_LAYER7=1 in ClinicalNote.tsx, so a production build contains none of it (checked by scripts/check-lab-exclusion.mjs).
 * The decision (which trigger fires and the approved text) is NOT computed here: it comes from the lab evaluator
 * (clinical/lab/human_factors/layer7_adapter.py, the R22 harness over the inactive contract). This file only transports a closed
 * technical descriptor and renders the answer. Fail-closed: an unreachable or malformed evaluator never lets the upload proceed.
 */
export type Layer7Verdict = {
  mode: 'SIMULATED_LAB_HARNESS_ONLY';
  abstains: boolean;
  trigger_id: string | null;
  message_id: string | null;
  message_text: string | null;
  force_send_available: false;
};

export type LabEvent = { type: string; at_ms: number; detail: Record<string, string | number | boolean | null> };

export const LAB_ENDPOINT = '/api/lab/layer7/evaluate';

export function labEntryIsE1(search: string): boolean {
  return new URLSearchParams(search).get('lab_entry') === 'e1';
}

export function recordLabEvent(type: string, detail: LabEvent['detail'] = {}): void {
  const w = window as unknown as { __LAB_LAYER7_LOG__?: LabEvent[] };
  (w.__LAB_LAYER7_LOG__ ??= []).push({ type, at_ms: Math.round(performance.now()), detail });
}

async function toBase64(file: File): Promise<string> {
  const bytes = new Uint8Array(await file.arrayBuffer());
  let binary = '';
  for (let i = 0; i < bytes.length; i += 0x8000) binary += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
  return btoa(binary);
}

export async function evaluateLayer7(file: File, uiModality: string | null, kind: string | null, language: string): Promise<Layer7Verdict> {
  const body = { filename: file.name, mime_type: file.type || null, content_base64: await toBase64(file), explicit_kind: kind };
  const response = await fetch(LAB_ENDPOINT, { method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ body, ui_modality: uiModality, language }) });
  if (!response.ok) throw new Error('layer7 evaluator unavailable');
  const verdict = await response.json() as Layer7Verdict;
  if (verdict.mode !== 'SIMULATED_LAB_HARNESS_ONLY' || verdict.force_send_available !== false || typeof verdict.abstains !== 'boolean'
    || (verdict.abstains && (!verdict.trigger_id || !verdict.message_text))) throw new Error('layer7 evaluator answer rejected');
  return verdict;
}

/** Literal recovery controls per trigger (R27 §7). Labels exist in the three approved languages; none lets the user override the abstention. */
export const RECOVERY_LABELS: Record<string, Record<'es' | 'pt' | 'en', { primary: string; secondary?: string }>> = {
  'T7-01': { es: { primary: 'Elegir modalidad' }, pt: { primary: 'Escolher modalidade' }, en: { primary: 'Choose modality' } },
  'T7-02': { es: { primary: 'Elegir modalidad' }, pt: { primary: 'Escolher modalidade' }, en: { primary: 'Choose modality' } },
  'T7-03': { es: { primary: 'Cargar copia íntegra / Repetir captura' }, pt: { primary: 'Carregar cópia íntegra / Repetir captura' }, en: { primary: 'Upload intact copy / Retake capture' } },
  'T7-04A': { es: { primary: 'Cargar archivo en formato compatible' }, pt: { primary: 'Carregar ficheiro em formato compatível' }, en: { primary: 'Upload a file in a supported format' } },
  'T7-04B': { es: { primary: 'Cambiar modalidad', secondary: 'Subir otro archivo' }, pt: { primary: 'Alterar modalidade', secondary: 'Enviar outro ficheiro' }, en: { primary: 'Change modality', secondary: 'Upload another file' } },
};

export function recoveryKey(verdict: Layer7Verdict): string {
  const id = (verdict.trigger_id ?? '').slice(0, 5);
  if (id !== 'T7-04') return id;
  return verdict.message_id === 'MSG_T7_UNSUPPORTED_FORMAT' ? 'T7-04A' : 'T7-04B';
}

export function labLanguage(language: string): 'es' | 'pt' | 'en' {
  return language === 'es' || language === 'pt' ? language : 'en';
}
