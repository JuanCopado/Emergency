import { useRef, useState } from 'react';
import { useNoteDraftField } from './draft';
import { assembleDocument, planApplication, SECTION_FIELDS, structureText, type NoteField, type SectionField, type WorkspaceSection } from './textStructuring';
import { useTextWorkspaceCopy } from './textWorkspaceCopy';

type Props = {
  /** Current content of the structured note fields (read only here). */
  current: Record<NoteField, string>;
  /** Receives the full next values and the fields that really changed; the page applies them through its own setters. */
  onApply: (next: Record<NoteField, string>, changed: NoteField[]) => void;
  onGoExport: () => void;
  /** Same local identifier screen the rest of the note uses. */
  hasIdentifier: (text: string) => boolean;
};

const card = 'rounded-2xl border border-border bg-surface p-4 shadow-card';

function fill(template: string, values: Record<string, string | number>) {
  return template.replace(/\{\{(\w+)\}\}/g, (_, key: string) => String(values[key] ?? ''));
}

/**
 * Three clearly separated stages: 1) the clinician's original text, which the application never edits;
 * 2) a proposal that only splits that text at headings already written in it; 3) a reviewed, freely
 * editable copy. Applying to the note appends to fields and never overwrites or duplicates content.
 */
export default function FreeTextWorkspace({ current, onApply, onGoExport, hasIdentifier }: Props) {
  const copy = useTextWorkspaceCopy();
  const [text, setText] = useNoteDraftField('workspaceText');
  const [source, setSource] = useNoteDraftField('workspaceSource');
  const [sections, setSections] = useNoteDraftField('workspaceSections');
  const [finalText, setFinalText] = useNoteDraftField('workspaceFinal');
  const [finalEdited, setFinalEdited] = useNoteDraftField('workspaceFinalEdited');
  const [status, setStatus] = useState('');
  const proposalHeading = useRef<HTMLHeadingElement>(null);

  const labels = copy.labels as Record<SectionField, string>;
  const stale = source !== null && source !== text;
  const lines = text ? text.split('\n').length : 0;
  const sectionsEdited = (sections ?? []).some(section => section.body !== section.proposed);
  const identifierWarning = hasIdentifier(text) || hasIdentifier(finalText);

  function update(id: string, patch: Partial<WorkspaceSection>) {
    setSections(previous => (previous ?? []).map(section => {
      if (section.id !== id) return section;
      const changed = (patch.body !== undefined && patch.body !== section.body)
        || (patch.field !== undefined && patch.field !== section.field)
        || (patch.include !== undefined && patch.include !== section.include);
      return { ...section, ...patch, ...(changed ? { applied: false } : {}) };
    }));
  }

  function structure() {
    if (!text.trim()) return;
    if (sectionsEdited && !window.confirm(copy.restructureConfirm)) return;
    const next = structureText(text);
    setSections(next);
    setSource(text);
    const unassigned = next.filter(section => section.field === 'unassigned').length;
    const headed = next.length - unassigned;
    setStatus(headed === 0 ? copy.detectedNone : fill(copy.detected, { sections: next.length, unassigned }));
    queueMicrotask(() => proposalHeading.current?.focus());
  }

  function discard() {
    setSections(null);
    setSource(null);
    setStatus('');
  }

  function generate() {
    if (!sections) return;
    if (finalEdited && !window.confirm(copy.regenerateConfirm)) return;
    setFinalText(assembleDocument(sections, labels));
    setFinalEdited(false);
  }

  async function copyFinal() {
    try {
      await navigator.clipboard.writeText(finalText);
      setStatus(copy.copied);
    } catch {
      setStatus(copy.copyFailed);
    }
  }

  function apply() {
    if (!sections) return;
    const plan = planApplication(sections, current);
    const changed = (Object.keys(plan.next) as NoteField[]).filter(field => plan.next[field] !== current[field]);
    if (!plan.appliedIds.length && !plan.alreadyPresentIds.length) {
      setStatus(copy.applyNothing);
      return;
    }
    if (changed.length) onApply(plan.next, changed);
    const done = new Set([...plan.appliedIds, ...plan.alreadyPresentIds]);
    setSections(previous => (previous ?? []).map(section => (done.has(section.id) ? { ...section, applied: true } : section)));
    setStatus(fill(copy.applyDone, { applied: plan.appliedIds.length, same: plan.alreadyPresentIds.length, none: plan.noTargetIds.length }));
  }

  return (
    <section className="space-y-4" aria-labelledby="free-text-title" data-testid="free-text-workspace">
      <div className={card}>
        <h2 id="free-text-title" className="text-lg font-bold">{copy.title}</h2>
        <p className="mt-1 text-sm text-muted">{copy.intro}</p>
        {identifierWarning && <p role="alert" className="mt-3 rounded-xl border border-danger p-3 text-sm font-semibold text-danger" data-testid="free-text-privacy">{copy.privacy}</p>}
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className={card}>
          <h3 className="font-bold">{copy.originalTitle}</h3>
          <label className="mt-3 block">
            <span className="label">{copy.originalLabel}</span>
            <textarea
              data-testid="free-text-original"
              className="input mt-1 min-h-[16rem] resize-y font-mono text-sm leading-relaxed lg:min-h-[26rem]"
              value={text}
              autoComplete="off"
              spellCheck
              placeholder={copy.originalPlaceholder}
              onChange={event => setText(event.target.value)}
              onKeyDown={event => {
                if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') { event.preventDefault(); structure(); }
              }}
            />
          </label>
          <p className="mt-2 text-xs text-muted">{copy.originalUntouched} · {fill(copy.counter, { chars: text.length, lines })}</p>
          {stale && <p role="status" className="mt-2 rounded-xl border border-warn p-3 text-sm" data-testid="free-text-stale">{copy.stale}</p>}
          <div className="mt-3 flex flex-wrap items-center gap-2">
            <button type="button" className="btn-primary min-h-11" disabled={!text.trim()} onClick={structure} data-testid="free-text-structure">{copy.structure}</button>
            <span className="text-xs text-muted">{copy.structureHint}</span>
            {sections && <button type="button" className="btn-ghost min-h-11" onClick={discard}>{copy.clear}</button>}
          </div>
        </div>

        <div className={card}>
          <h3 className="font-bold" tabIndex={-1} ref={proposalHeading}>{copy.proposalTitle}</h3>
          <p role="status" aria-live="polite" className="mt-1 text-sm text-muted" data-testid="free-text-status">{status}</p>
          {!sections || sections.length === 0 ? (
            <p className="mt-3 text-sm text-muted">{copy.proposalEmpty}</p>
          ) : (
            <div className="mt-3 space-y-3" data-testid="free-text-sections">
              {sections.map(section => {
                const edited = section.body !== section.proposed;
                return (
                  <article key={section.id} className="rounded-xl border border-border p-3" aria-label={labels[section.field]}>
                    <div className="flex flex-wrap items-center gap-2">
                      <label className="flex min-h-11 items-center gap-2 text-sm font-semibold">
                        <input type="checkbox" checked={section.include} onChange={event => update(section.id, { include: event.target.checked })} />
                        {copy.include}
                      </label>
                      <label className="flex w-full items-center gap-2 text-sm sm:w-auto">
                        <span className="label !mb-0 whitespace-nowrap">{copy.destination}</span>
                        <select className="input min-w-0 flex-1 sm:!w-auto sm:flex-none" value={section.field} onChange={event => update(section.id, { field: event.target.value as SectionField })}>
                          {SECTION_FIELDS.map(field => <option key={field} value={field}>{labels[field]}</option>)}
                        </select>
                      </label>
                      {edited && <span className="chip">{copy.edited}</span>}
                      {section.applied && <span className="chip text-primary">✓</span>}
                    </div>
                    <p className="mt-1 text-xs text-muted">{section.heading ? fill(copy.fromOriginal, { heading: section.heading.replace(/[:：]\s*$/, '') }) : copy.noHeading}</p>
                    <textarea
                      aria-label={`${copy.sectionText} · ${labels[section.field]}`}
                      className="input mt-2 min-h-24 resize-y"
                      value={section.body}
                      onChange={event => update(section.id, { body: event.target.value })}
                    />
                    {edited && <button type="button" className="btn-ghost mt-2 min-h-11" onClick={() => update(section.id, { body: section.proposed })}>{copy.restore}</button>}
                  </article>
                );
              })}
            </div>
          )}
          <div className="mt-3">
            <button type="button" className="btn-ghost min-h-11" disabled={!sections?.length} onClick={apply} data-testid="free-text-apply">{copy.apply}</button>
            <p className="mt-2 text-xs text-muted">{copy.applyHint}</p>
          </div>
        </div>
      </div>

      <div className={card}>
        <h3 className="font-bold">{copy.finalTitle}</h3>
        <p className="mt-1 text-sm text-muted">{copy.finalHint}</p>
        <div className="mt-3 flex flex-wrap gap-2">
          <button type="button" className="btn-primary min-h-11" disabled={!sections?.length} onClick={generate} data-testid="free-text-generate">
            {finalText ? copy.regenerate : copy.generate}
          </button>
          <button type="button" className="btn-ghost min-h-11" disabled={!finalText.trim()} onClick={() => void copyFinal()} data-testid="free-text-copy">{copy.copy}</button>
          <button type="button" className="btn-ghost min-h-11" onClick={onGoExport}>{copy.goExport}</button>
        </div>
        <p className="mt-2 text-xs text-muted">{copy.finalExportHint}</p>
        <label className="mt-3 block">
          <span className="label">{copy.finalLabel}</span>
          <textarea
            data-testid="free-text-final"
            className="input mt-1 min-h-[14rem] resize-y leading-relaxed"
            value={finalText}
            onChange={event => { setFinalText(event.target.value); setFinalEdited(true); }}
          />
        </label>
      </div>
    </section>
  );
}
