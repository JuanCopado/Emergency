import { Link } from 'react-router-dom';
import { THERAPEUTIC_SECTION_KEYS } from './therapeuticReview';
import { useTherapyCopy } from './therapyCopy';
import type { TherapeuticConfirmations, TherapeuticPlan, TherapeuticSections, TherapyCatalogEntry, TherapySelection } from './types';

type Props = {
  selection: TherapySelection; catalog: TherapyCatalogEntry[]; catalogError: boolean;
  onSelection: (selection: TherapySelection) => void;
  weight: string; weightInvalid: boolean; onWeight: (value: string) => void;
  allergiesReviewed: boolean; onAllergiesReviewed: (checked: boolean) => void;
  privacyReviewed: boolean; onPrivacyReviewed: (checked: boolean) => void;
  canSuggest: boolean; busy: 'suggest'|'validate'|null; onSuggest: () => void;
  plan: TherapeuticPlan|null; reviewValid: boolean; needsRegeneration: boolean;
  editing: boolean; onEdit: () => void; onSection: (key: keyof TherapeuticSections, value: string) => void;
  confirmations: TherapeuticConfirmations; onConfirmation: (key: keyof TherapeuticConfirmations, checked: boolean) => void;
  canValidate: boolean; onValidate: () => void;
  previousPlan: string; includePrevious: boolean; onIncludePrevious: (checked: boolean) => void;
};

function ReviewIcon({ valid }: { valid: boolean }) {
  return <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true" focusable="false">
    {valid ? <path d="m5 12 4 4L19 6" /> : <><path d="M12 3 2 21h20L12 3Z"/><path d="M12 9v5m0 3v1"/></>}
  </svg>;
}

export default function TherapeuticPlanPanel(props: Props) {
  const c = useTherapyCopy();
  const currentModuleKnown = props.catalog.some(entry => entry.id === props.selection.module_id);
  return <section className="card space-y-4 p-4 sm:p-5" aria-labelledby="therapy-title" data-testid="therapeutic-plan-panel">
    <div className="flex flex-wrap items-start justify-between gap-3">
      <h2 id="therapy-title" className="text-lg font-bold">{c.title}</h2>
      <span role="status" aria-live="polite" data-testid="therapy-review-state" className={`inline-flex items-center gap-2 rounded-xl border px-3 py-2 text-sm font-semibold ${props.reviewValid ? 'border-ok text-ok' : 'border-danger text-danger'}`}>
        <ReviewIcon valid={props.reviewValid}/>{props.reviewValid ? c.reviewed : c.pending}
      </span>
    </div>
    <div className="grid gap-3 sm:grid-cols-2">
      <label><span className="label">{c.diagnosis}</span><input className="input" value={props.selection.label} onChange={event => props.onSelection({ ...props.selection, label: event.target.value, selection: 'manual' })}/></label>
      <label><span className="label">{c.module}</span><select className="input" value={props.selection.module_id ?? ''} onChange={event => {
        const module = props.catalog.find(entry => entry.id === event.target.value);
        props.onSelection({ label: props.selection.label.trim() || module?.title || '', module_id: module?.id ?? null, selection: 'manual' });
      }}><option value="">{c.chooseModule}</option>{props.selection.module_id && !currentModuleKnown && <option value={props.selection.module_id}>{props.selection.module_id}</option>}{props.catalog.map(entry => <option key={entry.id} value={entry.id}>{entry.title}</option>)}</select></label>
      <label><span className="label">{c.weight}</span><input className="input" inputMode="decimal" lang="en" aria-invalid={props.weightInvalid || undefined} value={props.weight} onChange={event => props.onWeight(event.target.value)}/>{props.weightInvalid && <span role="alert" className="mt-1 block text-sm text-danger">{c.weightInvalid}</span>}</label>
      <label className="flex min-h-[44px] items-center gap-3 text-sm"><input type="checkbox" checked={props.allergiesReviewed} onChange={event => props.onAllergiesReviewed(event.target.checked)}/>{c.allergies}</label>
    </div>
    {props.catalogError && <p className="text-sm text-warn">{c.errorCatalog}</p>}
    <label className="flex min-h-[44px] items-center gap-3 text-sm"><input type="checkbox" checked={props.privacyReviewed} onChange={event => props.onPrivacyReviewed(event.target.checked)}/>{c.privacy}</label>
    <p className="text-sm text-muted">{c.prerequisites}</p>
    {props.previousPlan.trim() && <details className="rounded-xl border border-border p-3"><summary className="cursor-pointer font-semibold">{c.previous}</summary><p className="mt-2 whitespace-pre-wrap break-words text-sm">{props.previousPlan}</p><p className="mt-2 text-sm text-muted">{c.previousHelp}</p>{!props.plan && <label className="mt-3 flex items-center gap-3 text-sm"><input type="checkbox" checked={props.includePrevious} onChange={event => props.onIncludePrevious(event.target.checked)}/>{c.includePrevious}</label>}</details>}
    <button type="button" className="btn-primary" disabled={!props.canSuggest || props.busy !== null} onClick={props.onSuggest}>{props.busy === 'suggest' ? c.preparing : props.plan ? c.regenerate : c.suggest}</button>
    {!props.plan && <p className="text-sm text-muted">{c.empty}</p>}
    {props.plan && <>
      <div className="flex flex-wrap gap-2 text-sm"><strong>{props.plan.diagnosis.label}</strong><span className="chip">{props.plan.population === 'pediatric' ? c.pediatric : c.adult}</span></div>
      {props.needsRegeneration && <p role="status" className="rounded-xl border border-danger p-3 text-sm font-semibold text-danger">{c.sourceChanged}</p>}
      <div className="space-y-4">{THERAPEUTIC_SECTION_KEYS.map(key => <label key={key} className="block"><span className="label">{c[key]}</span><textarea className={`input min-h-28 ${!props.editing ? 'bg-surface-2' : ''}`} readOnly={!props.editing} value={props.plan!.sections[key]} onChange={event => props.onSection(key, event.target.value)}/></label>)}</div>
      <button type="button" className="btn-ghost" onClick={props.onEdit} disabled={props.editing}>{c.edit}</button>
      <div className="space-y-3 rounded-xl border border-border p-3">
        <label className="flex items-start gap-3 text-sm"><input className="mt-1" type="checkbox" checked={props.confirmations.individualized} onChange={event => props.onConfirmation('individualized', event.target.checked)}/><span>{c.individualized}</span></label>
        <label className="flex items-start gap-3 text-sm"><input className="mt-1" type="checkbox" checked={props.confirmations.medication_safety_reviewed} onChange={event => props.onConfirmation('medication_safety_reviewed', event.target.checked)}/><span>{c.safety}</span></label>
        <div className="flex flex-wrap gap-3"><Link className="text-sm font-semibold text-primary underline" to="/clinical/medication-selection-safety">{c.safetyLink}</Link><Link className="text-sm font-semibold text-primary underline" to="/acute-medications">{c.pharmacology}</Link></div>
      </div>
      <button type="button" aria-describedby="therapy-review-help" className={`btn text-white ${props.reviewValid ? 'bg-emerald-700 disabled:opacity-100' : 'bg-red-700 hover:bg-red-800'}`} disabled={props.reviewValid || !props.canValidate || props.busy !== null} onClick={props.onValidate}><ReviewIcon valid={props.reviewValid}/>{props.busy === 'validate' ? c.validating : props.reviewValid ? c.validated : c.validate}</button>
      <p id="therapy-review-help" className="text-sm text-muted">{props.reviewValid ? c.scope : c.completedSections}</p>
      <details className="rounded-xl border border-border p-3"><summary className="cursor-pointer font-semibold">{c.reference}</summary><p className="mt-3 text-sm text-muted">{c.sourceHelp}</p><ul className="mt-3 space-y-2 text-sm">{props.plan.source_refs.map((source, index) => <li key={`${source.module_id}-${index}`}><Link className="font-semibold text-primary underline" to={`/clinical/${encodeURIComponent(source.module_id)}`}>{source.module_id}</Link> · {c.sourceLanguage}: {source.language}</li>)}</ul><pre className="mt-4 whitespace-pre-wrap break-words font-sans text-sm">{props.plan.reference_text}</pre>{props.plan.missing_requirements.length > 0 && <div className="mt-3 text-sm"><p className="font-semibold">{c.sourceMissing}</p><ul className="mt-1 list-disc pl-5">{props.plan.missing_requirements.map((requirement, index) => <li key={index}>{requirement in c ? c[requirement as keyof typeof c] : requirement}</li>)}</ul></div>}</details>
    </>}
  </section>;
}
