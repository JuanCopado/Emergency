import { useId } from 'react';
import { useTranslation } from 'react-i18next';
import { SourceChip, type SourceRef } from './SourceChip';
import { StatusBadge } from './StatusBadge';

/**
 * A blocked contract: label and reason exactly as supplied by the backend catalog.
 * The props deliberately admit no dose, volume, rate, unit, children or render
 * callbacks, so no calculated figure can be shown through this card.
 */
export type BlockedContractCardProps = {
  label: string;
  reason: string;
  sources?: SourceRef[];
  children?: never;
};

export function BlockedContractCard({ label, reason, sources }: BlockedContractCardProps) {
  const { t } = useTranslation();
  const titleId = useId();
  return (
    <section aria-labelledby={titleId} className="card space-y-3 border-danger p-4" data-testid="blocked-contract">
      <div className="flex flex-wrap items-center gap-2">
        <h2 id={titleId} className="text-lg font-bold">{label}</h2>
        <StatusBadge kind="blocked" />
      </div>
      <p className="font-semibold">{t('blocked.title')}</p>
      <p className="whitespace-pre-wrap break-words">{reason}</p>
      <p className="text-sm text-muted">{t('blocked.requiresReview')}</p>
      {sources && sources.length > 0 && (
        <ul className="flex flex-wrap gap-2" aria-label={t('result.sources')}>
          {sources.map((source, index) => (
            <li key={`${index}-${source.label}`}>
              <SourceChip {...source} />
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
