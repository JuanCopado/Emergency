export function SearchEmptyState({ heading, hint, resetLabel, onReset, lang }: {
  heading: string;
  hint: string;
  resetLabel: string;
  onReset: () => void;
  lang?: string;
}) {
  return (
    <div lang={lang} className="card bg-surface-2 p-5">
      <h2 className="font-bold">{heading}</h2>
      <p className="mt-1 text-sm text-muted">{hint}</p>
      <button type="button" className="btn-ghost mt-4" onClick={onReset}>{resetLabel}</button>
    </div>
  );
}
