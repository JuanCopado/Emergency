import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useSearchParams } from 'react-router-dom';
import { DrugCard } from '../components/DrugCard';
import { Icon } from '../components/Icon';
import { drugs } from '../data';
import { CATEGORIES } from '../data/schema';
import { filterDrugs, type DoseFilter } from '../lib/filter';

export default function DrugList() {
  const { t } = useTranslation();
  const [params, setParams] = useSearchParams();
  const q = params.get('q') ?? '';
  const categoryParam = params.get('category') ?? 'all';
  const category = (CATEGORIES as readonly string[]).includes(categoryParam) ? categoryParam : 'all';
  const doseParam = params.get('dose');
  const dose: DoseFilter = doseParam === 'weight' || doseParam === 'fixed' ? doseParam : 'all';

  const update = (key: string, value: string) => {
    const next = new URLSearchParams(params);
    if (!value || value === 'all') next.delete(key);
    else next.set(key, value);
    setParams(next, { replace: true });
  };

  const results = useMemo(
    () => filterDrugs(drugs, { q, category, dose, localName: (d) => t(`drugNames.${d.id}`, { defaultValue: d.name }) }),
    [q, category, dose, t],
  );

  const catOptions = ['all', ...CATEGORIES];
  const doseOptions: DoseFilter[] = ['all', 'weight', 'fixed'];

  return (
    <div className="space-y-5">
      <header>
        <h1 className="text-2xl font-extrabold tracking-tight sm:text-3xl">{t('list.title')}</h1>
        <p className="mt-1 text-muted">{t('list.subtitle')}</p>
      </header>

      <div className="card space-y-4 p-4">
        <div role="search" className="relative">
          <label htmlFor="drug-search" className="sr-only">
            {t('search.label')}
          </label>
          <Icon name="search" className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-muted" />
          <input
            id="drug-search"
            type="search"
            className="input pl-10"
            value={q}
            placeholder={t('search.placeholder')}
            onChange={(e) => update('q', e.target.value)}
            autoComplete="off"
          />
        </div>
        <fieldset>
          <legend className="section-title mb-2">{t('list.filterCategory')}</legend>
          <div className="flex flex-wrap gap-2">
            {catOptions.map((c) => (
              <button
                key={c}
                type="button"
                aria-pressed={category === c}
                onClick={() => update('category', c)}
                className={`chip ${category === c ? 'border-primary bg-primary text-primary-fg' : 'bg-surface text-fg hover:bg-surface-2'}`}
              >
                {c === 'all' ? t('common.all') : t(`categories.${c}`)}
              </button>
            ))}
          </div>
        </fieldset>
        <fieldset>
          <legend className="section-title mb-2">{t('list.filterDose')}</legend>
          <div className="flex flex-wrap gap-2">
            {doseOptions.map((c) => (
              <button
                key={c}
                type="button"
                aria-pressed={dose === c}
                onClick={() => update('dose', c)}
                className={`chip ${dose === c ? 'border-primary bg-primary text-primary-fg' : 'bg-surface text-fg hover:bg-surface-2'}`}
              >
                {c === 'all' ? t('common.all') : c === 'weight' ? t('drug.weightBased') : t('drug.fixedDose')}
              </button>
            ))}
          </div>
        </fieldset>
      </div>

      <p className="text-sm text-muted" aria-live="polite" data-testid="result-count">
        {t('list.results', { count: results.length })}
      </p>
      {results.length === 0 ? (
        <div className="card p-8 text-center text-muted">{t('list.empty')}</div>
      ) : (
        <ul className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {results.map((d) => (
            <li key={d.id}>
              <DrugCard drug={d} />
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
