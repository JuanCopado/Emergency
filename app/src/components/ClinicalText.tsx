import { Fragment } from 'react';

/**
 * Renders English master clinical text verbatim; `backtick` module references become <code>.
 */
export function ClinicalText({ text, className = '' }: { text: string; className?: string }) {
  const parts = text.split(/(`[^`]+`)/g);
  return (
    <span lang="en" className={className}>
      {parts.map((p, i) =>
        p.startsWith('`') && p.endsWith('`') ? (
          <code key={i} className="rounded bg-surface-2 px-1 py-0.5 font-mono text-[0.85em]">
            {p.slice(1, -1)}
          </code>
        ) : (
          <Fragment key={i}>{p}</Fragment>
        ),
      )}
    </span>
  );
}
