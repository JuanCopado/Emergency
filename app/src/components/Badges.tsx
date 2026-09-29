import { useTranslation } from 'react-i18next';
import type { DrugCategory, EvidenceStatus } from '../data/schema';

const EVIDENCE_STYLE: Record<EvidenceStatus, string> = {
  green: 'border-ok/40 text-ok',
  yellow: 'border-warn/50 text-warn bg-warn-bg',
  red: 'border-danger/40 text-danger',
};
const DOT: Record<EvidenceStatus, string> = { green: 'bg-ok', yellow: 'bg-amber-500', red: 'bg-danger' };

export function EvidenceBadge({ status }: { status: EvidenceStatus }) {
  const { t } = useTranslation();
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-semibold ${EVIDENCE_STYLE[status]}`}
      title={t(`evidence.${status}Help`)}
    >
      <span className={`h-2 w-2 rounded-full ${DOT[status]}`} aria-hidden="true" />
      {t('evidence.label')}: {t(`evidence.${status}`)}
    </span>
  );
}

export function CategoryBadge({ category }: { category: DrugCategory }) {
  const { t } = useTranslation();
  const cls = category === 'vasoactive-inotrope' ? 'text-vaso border-vaso/40' : 'text-sed border-sed/40';
  return (
    <span className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-semibold ${cls}`}>
      {t(`categories.${category}`)}
    </span>
  );
}

export function DraftPill() {
  const { t } = useTranslation();
  return (
    <span className="inline-flex items-center rounded-full border border-warn/50 bg-warn-bg px-2 py-0.5 text-[11px] font-bold uppercase tracking-wide text-warn">
      {t('draft.pill')}
    </span>
  );
}
