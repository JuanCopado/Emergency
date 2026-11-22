import { useEffect, useState } from 'react';
import { MODALITIES, modalityContract, type PrototypeModalityId } from './r51Prototype';

const PREVIEWABLE = new Set(['image/png', 'image/jpeg', 'image/webp']);

/**
 * R13 · R5-1 layers 1-4 and 6 (INACTIVE prototype, rendered only when r51PrototypeEnabled()).
 * No category is preselected; the file cannot be chosen until a modality is; the selected image is
 * shown next to its destination modality; the button names that modality; the change of modality is
 * one tap away. The human confirmation does not verify the image content, and the text says so.
 */
export default function ModalityEntry({ busy, ui, onConfirm }: {
  busy: boolean;
  ui: (key: string, values?: Record<string, string | number>) => string;
  onConfirm: (file: File, kind: string) => void;
}) {
  const [modality, setModality] = useState<PrototypeModalityId | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);

  useEffect(() => {
    if (!file || !PREVIEWABLE.has(file.type)) { setPreview(null); return; }
    const url = URL.createObjectURL(file);
    setPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  const reset = () => { setModality(null); setFile(null); };
  const contract = modality ? modalityContract(modality) : null;
  const label = contract ? ui(contract.labelKey) : '';

  return (
    <div data-testid="r51-modality-entry" className="rounded-xl border border-dashed border-border p-4 grid gap-3">
      <span className="label">{ui('Escolha a modalidade antes de enviar')}</span>
      <div className="flex flex-wrap gap-2">
        {MODALITIES.map(m => (
          <button key={m.id} type="button" aria-pressed={modality === m.id}
            className={`btn min-h-11 ${modality === m.id ? 'btn-primary' : 'btn-ghost'}`}
            onClick={() => { setModality(m.id); setFile(null); }}>{ui(m.labelKey)}</button>
        ))}
      </div>
      {!contract && <p className="text-xs text-muted">{ui('Nenhuma modalidade selecionada. Escolha uma para poder escolher o ficheiro.')}</p>}
      {contract && (
        <>
          <label className="grid gap-1">
            <span className="label">{ui('Upload clínico')}</span>
            <input aria-label={ui('Upload clínico')} type="file" disabled={busy} accept={contract.accept}
              onChange={e => setFile(e.target.files?.[0] ?? null)} />
          </label>
          <p className="text-xs text-muted">{ui(contract.limitationKey, { modality: label })}</p>
        </>
      )}
      {contract && file && (
        <section aria-label={ui('Pré-visualização antes do envio')} className="grid gap-2">
          <p className="text-sm font-semibold">{ui('Modalidade de destino:')} {label}</p>
          {preview
            ? <img src={preview} alt={`${ui('Pré-visualização antes do envio')}: ${file.name}`} className="max-h-64 max-w-full rounded-lg border border-border object-contain" />
            : <p className="text-xs text-muted">{ui('Sem pré-visualização para este formato.')} {file.name}</p>}
          <p className="text-xs text-muted">{ui('A confirmação humana não verifica o conteúdo da imagem.')}</p>
          <div className="flex flex-wrap gap-2">
            <button type="button" className="btn-primary min-h-11" disabled={busy}
              onClick={() => { onConfirm(file, contract.kind); reset(); }}>{ui('Confirmar e enviar como')} {label}</button>
            <button type="button" className="btn btn-ghost min-h-11" disabled={busy} onClick={reset}>{ui('Alterar modalidade')}</button>
          </div>
        </section>
      )}
    </div>
  );
}
