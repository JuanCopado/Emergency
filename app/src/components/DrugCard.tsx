import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { defaultPreparation, isWeightBased } from '../data';
import type { Drug } from '../data/schema';
import { useFormat } from '../lib/useFormat';
import { CategoryBadge } from './Badges';
import { Icon } from './Icon';

export function DrugCard({ drug }: { drug: Drug }) {
  const { t, i18n } = useTranslation();
  const f = useFormat();
  const prep = defaultPreparation(drug);
  const localName = t(`drugNames.${drug.id}`, { defaultValue: drug.name });
  const showLocal = i18n.language !== 'en' && localName !== drug.name;
  const d = drug.dosing;
  const primary = d.start ?? d.range;
  const primaryLabel = d.start ? t('dosing.start') : t('dosing.range');
  return (
    <Link
      to={`/drugs/${drug.id}`}
      className="card group flex h-full flex-col gap-3 p-4 transition hover:border-primary/60 hover:shadow-md"
      data-testid={`drug-card-${drug.id}`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h3 className="text-lg font-bold leading-snug">{drug.name}</h3>
          <p className="truncate text-sm text-muted">
            {showLocal ? localName : drug.synonyms.join(', ') || ' '}
          </p>
        </div>
        <Icon name="chevronRight" className="mt-1 shrink-0 text-muted transition group-hover:translate-x-0.5 group-hover:text-primary" />
      </div>
      <div className="flex flex-wrap gap-1.5">
        <CategoryBadge category={drug.category} />
        <span className="inline-flex items-center rounded-full border border-border px-2.5 py-1 text-xs font-semibold text-muted">
          {isWeightBased(drug) ? t('drug.weightBased') : t('drug.fixedDose')}
        </span>
      </div>
      <dl className="mt-auto grid grid-cols-2 gap-2 rounded-xl bg-surface-2 p-3 text-sm">
        <div>
          <dt className="text-xs text-muted">{primaryLabel}</dt>
          <dd className="num font-semibold">
            {primary ? `${f.range(primary.min, primary.max)} ${f.unit(drug.doseUnit)}` : '—'}
          </dd>
        </div>
        <div>
          <dt className="text-xs text-muted">{t('prep.standardConc')}</dt>
          <dd className="num font-semibold">
            {f.num(prep.concentration.value)} {f.unit(prep.concentration.unit)}
          </dd>
        </div>
      </dl>
    </Link>
  );
}
