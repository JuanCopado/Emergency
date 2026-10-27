import { useId, type ReactNode } from 'react';
import { useTranslation } from 'react-i18next';
import type { EvidenceStatus } from '../data/schema';
import { formatClinicalNumber, type ClinicalFormatOptions } from '../lib/clinicalInput';
import { EvidenceBadge } from './Badges';
import { SourceChip, type SourceRef } from './SourceChip';
import { StatusBadge, type StatusKind } from './StatusBadge';

export type ResultItem = {
  label: string;
  /** Numbers are formatted for display only; strings are canonical text and shown literally. */
  value: number | string | null;
  unit: string | null;
  /** Visual precision for this field/unit. Omitted → full precision, no rounding. */
  format?: ClinicalFormatOptions;
  /**
   * Set only when the caller knows a string value is a plain decimal number
   * (e.g. "0.05" from a serializer). Without it, strings — names, dates, IDs,
   * URLs, references — are never altered.
   */
  numericString?: boolean;
};

const PLAIN_DECIMAL = /^-?\d+(?:\.\d+)?$/;

type Display = { text: string; numeric: boolean; invalid: boolean };

function display(item: ResultItem): Display | null {
  const { value } = item;
  if (value === null) return null;
  if (typeof value === 'number') {
    const text = formatClinicalNumber(value, item.format);
    return text === null ? { text: '', numeric: true, invalid: true } : { text, numeric: true, invalid: false };
  }
  if (item.numericString && PLAIN_DECIMAL.test(value.trim())) {
    // Only the single decimal point of an unambiguous decimal string is swapped; no parsing,
    // so the digits shown are exactly the digits received.
    return { text: value.trim().replace('.', ','), numeric: true, invalid: false };
  }
  return { text: value, numeric: false, invalid: false };
}

export function ResultCard({
  title,
  items,
  status = 'clinically_pending',
  evidence,
  sources,
  formula,
  children,
}: {
  title: string;
  items: ResultItem[];
  status?: StatusKind;
  evidence?: EvidenceStatus;
  sources?: SourceRef[];
  formula?: string;
  children?: ReactNode;
}) {
  const { t } = useTranslation();
  const titleId = useId();
  return (
    <section aria-labelledby={titleId} className="card space-y-3 p-4">
      <div className="flex flex-wrap items-center gap-2">
        <h2 id={titleId} className="text-lg font-bold">{title}</h2>
        <StatusBadge kind={status} />
        {evidence && <EvidenceBadge status={evidence} />}
      </div>
      <dl className="grid gap-3 sm:grid-cols-2" aria-live="polite">
        {items.map((item, index) => {
          const shown = display(item);
          return (
            <div key={`${index}-${item.label}`} className="rounded-xl border border-border bg-surface-2 p-3">
              <dt className="text-sm font-semibold">{item.label}</dt>
              <dd className="mt-1 break-words text-lg" data-result-value>
                {shown === null ? (
                  <span className="text-muted">{t('result.notSpecified')}</span>
                ) : shown.invalid ? (
                  <span className="font-semibold text-danger">{t('result.invalidValue')}</span>
                ) : (
                  // A non-breaking space keeps a number and its unit on the same line;
                  // long canonical text may still wrap.
                  <span className={shown.numeric ? 'whitespace-nowrap' : undefined}>
                    <span className="num font-bold">{shown.text}</span>
                    {item.unit ? (
                      <span>{' '}{item.unit}</span>
                    ) : shown.numeric ? (
                      <span className="text-sm text-warn">{' '}({t('result.unitNotSpecified')})</span>
                    ) : null}
                  </span>
                )}
              </dd>
            </div>
          );
        })}
      </dl>
      {children}
      {formula && (
        <details>
          <summary className="cursor-pointer font-semibold">{t('result.formula')}</summary>
          <p className="mt-2 whitespace-pre-wrap break-words font-mono text-sm">{formula}</p>
        </details>
      )}
      {sources && sources.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold">{t('result.sources')}</h3>
          <ul className="mt-1 flex flex-wrap gap-2">
            {sources.map((source, index) => (
              <li key={`${index}-${source.label}`}>
                <SourceChip {...source} />
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}
