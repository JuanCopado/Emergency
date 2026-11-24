import { useEffect, useRef, useState } from 'react';
import { MODALITIES, approvedLimitationText, modalityContract, type PrototypeModalityId } from '../src/clinical-note/r51Prototype';
import { RECOVERY_LABELS, evaluateLayer7, labEntryIsE1, labLanguage, recordLabEvent, recoveryKey, resolveLabLocale, type Layer7Verdict } from './layer7Lab';

/**
 * LAB_LAYER7_MARKER · arm B of the Stage-1 formative study (SIMULATED_LAB_HARNESS_ONLY). Same R5-1 selector as ModalityEntry plus the
 * visible Layer 7 abstention. With ?lab_entry=e1 the file input is present BEFORE a modality is chosen (scenario E1, trigger T7-01);
 * every other trial keeps the approved flow (file only after the modality). There is no force-send control anywhere.
 */
export default function LabModalityEntry({ busy, ui, language, onConfirm }: {
  busy: boolean;
  language: string;
  ui: (key: string, values?: Record<string, string | number>) => string;
  onConfirm: (file: File, kind: string | null) => void;
}) {
  const e1 = labEntryIsE1(window.location.search);
  const lang = labLanguage(language);
  const locale = resolveLabLocale(window.location.search, language);
  const [modality, setModality] = useState<PrototypeModalityId | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [verdict, setVerdict] = useState<Layer7Verdict | null>(null);
  const [failure, setFailure] = useState(false);
  const bannerRef = useRef<HTMLDivElement>(null);
  const selectorRef = useRef<HTMLDivElement>(null);
  const fileRef = useRef<HTMLInputElement>(null);
  const shownAt = useRef(0);
  const contract = modality ? modalityContract(modality) : null;
  const label = contract ? ui(contract.labelKey) : '';

  useEffect(() => { recordLabEvent('locale_resolved', { language, lab_locale: locale.requested, variant: locale.variant, status: locale.status }); },
    [language, locale.requested, locale.variant, locale.status]);
  useEffect(() => { if (verdict?.abstains) { shownAt.current = performance.now(); bannerRef.current?.focus();
    recordLabEvent('layer7_banner_rendered', { trigger: verdict.trigger_id, message_id: verdict.message_id }); } }, [verdict]);

  const evaluate = async (next: File, nextModality: PrototypeModalityId | null) => {
    setFailure(false); setVerdict(null);
    const kind = nextModality ? modalityContract(nextModality).kind : null;
    try { setVerdict(await evaluateLayer7(next, nextModality, kind, lang)); } catch { setFailure(true); recordLabEvent('evaluator_failure'); }
  };

  const choose = (id: PrototypeModalityId) => {
    const origin = verdict?.abstains ? 'after_layer7' : 'initial';
    recordLabEvent('modality_selected', { modality: id, origin });
    setModality(id);
    if (verdict?.abstains) recordLabEvent('recovery_action', { action: 'change_modality', trigger: verdict.trigger_id });
    if (file) void evaluate(file, id); else setFile(null);
  };
  const pick = (next: File | null) => {
    setFile(next); setVerdict(null);
    if (next) { recordLabEvent('file_selected', { size: next.size, with_modality: modality !== null, viewport_width_px: window.innerWidth, e1_entry: e1 }); void evaluate(next, modality); }
  };
  const replaceFile = () => {
    recordLabEvent('recovery_action', { action: 'replace_file', trigger: verdict?.trigger_id ?? null });
    setFile(null); setVerdict(null); if (fileRef.current) fileRef.current.value = ''; fileRef.current?.focus();
  };
  const reset = () => { setModality(null); setFile(null); setVerdict(null); };

  const abstains = verdict?.abstains === true;
  const labels = abstains ? RECOVERY_LABELS[recoveryKey(verdict as Layer7Verdict)]?.[lang] : undefined;
  const showFile = e1 || contract !== null;

  if (locale.status === 'UNSUPPORTED') {                                                 // fail closed: no approved text for this regional request
    return <p role="alert" data-testid="lab-locale-unsupported" className="rounded-xl border border-dashed border-border p-4 text-sm">
      {`Laboratory: locale "${locale.requested}" has no approved texts for this build. The upload is disabled.`}</p>;
  }

  return (
    <div data-testid="r51-modality-entry" data-lab-layer7="simulated" className="rounded-xl border border-dashed border-border p-4 grid grid-cols-1 gap-3 min-w-0">
      <span className="label">{ui('Escolha a modalidade antes de enviar')}</span>
      <div ref={selectorRef} className="flex flex-wrap gap-2">
        {MODALITIES.map(m => (
          <button key={m.id} type="button" aria-pressed={modality === m.id} disabled={busy}
            className={`btn min-h-11 ${modality === m.id ? 'btn-primary' : 'btn-ghost'}`}
            onClick={() => choose(m.id)}>{ui(m.labelKey)}</button>
        ))}
      </div>
      {abstains && (
        <div ref={bannerRef} tabIndex={-1} role="alert" aria-live="assertive" data-testid="lab-layer7-banner"
          className="rounded-lg border border-border bg-surface p-3 text-sm grid gap-2 min-w-0">
          <p>{verdict?.message_text}</p>
          {labels && (
            <div className="flex flex-wrap gap-2">
              <button type="button" className="btn btn-ghost min-h-11" onClick={() => {
                const key = recoveryKey(verdict as Layer7Verdict);
                if (key === 'T7-01' || key === 'T7-02' || key === 'T7-04B') { recordLabEvent('recovery_action', { action: 'focus_selector', trigger: verdict?.trigger_id ?? null }); selectorRef.current?.querySelector('button')?.focus(); }
                else replaceFile();
              }}>{labels.primary}</button>
              {labels.secondary && <button type="button" className="btn btn-ghost min-h-11" onClick={replaceFile}>{labels.secondary}</button>}
            </div>
          )}
        </div>
      )}
      {failure && <p role="alert" className="text-sm" data-testid="lab-layer7-failure">{ui('Erro técnico do laboratório: o envio foi bloqueado.')}</p>}
      {!showFile && <p className="text-xs text-muted">{ui('Nenhuma modalidade selecionada. Escolha uma para poder escolher o ficheiro.')}</p>}
      {showFile && (
        <label className="grid grid-cols-1 gap-1 min-w-0">
          <span className="label">{ui('Upload clínico')}</span>
          <input ref={fileRef} className="w-full min-w-0 max-w-full" aria-label={ui('Upload clínico')} type="file" disabled={busy}
            accept={contract ? contract.accept : undefined} onChange={e => pick(e.target.files?.[0] ?? null)} />
        </label>
      )}
      {contract && <p className="text-xs text-muted">{approvedLimitationText(contract.id, language) ?? ui(contract.limitationKey, { modality: label })}</p>}
      {contract && file && verdict && !abstains && (
        <section aria-label={ui('Pré-visualização antes do envio')} className="grid gap-2">
          <p className="text-sm font-semibold">{ui('Modalidade de destino:')} {label}</p>
          <p className="text-xs text-muted">{ui('A confirmação humana não verifica o conteúdo da imagem.')}</p>
          <div className="flex flex-wrap gap-2">
            <button type="button" className="btn-primary min-h-11" disabled={busy}
              onClick={() => { recordLabEvent('confirm_clicked', { modality: contract.id }); onConfirm(file, contract.kind); reset(); }}>{ui('Confirmar e enviar como')} {label}</button>
            <button type="button" className="btn btn-ghost min-h-11" disabled={busy} onClick={reset}>{ui('Alterar modalidade')}</button>
          </div>
        </section>
      )}
    </div>
  );
}
