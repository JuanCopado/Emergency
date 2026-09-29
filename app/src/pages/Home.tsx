import { useState, type FormEvent } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useNavigate } from 'react-router-dom';
import { Icon, type IconName } from '../components/Icon';
import { drugs } from '../data';
import { AVAILABLE_GROUPS, COMING_SOON_GROUPS } from '../data/moduleGroups';
import { DraftBanner } from '../components/DraftBanner';

const GROUP_ICON: Record<string, IconName> = { vasoactive: 'heart', sedation: 'moon' };

export default function Home() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [q, setQ] = useState('');
  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
    navigate(q.trim() ? `/drugs?q=${encodeURIComponent(q.trim())}` : '/drugs');
  };
  return (
    <div className="space-y-8">
      <section aria-labelledby="home-title" className="relative overflow-hidden rounded-3xl border border-border bg-surface p-5 shadow-card sm:p-8">
        <div aria-hidden="true" className="pointer-events-none absolute -right-24 -top-24 h-72 w-72 rounded-full bg-primary/10 blur-3xl" />
        <div aria-hidden="true" className="pointer-events-none absolute -bottom-28 -left-16 h-64 w-64 rounded-full bg-brand/10 blur-3xl" />
        <div className="relative">
          <p className="section-title">{t('home.eyebrow')}</p>
          <h1 id="home-title" className="mt-2 text-2xl font-extrabold tracking-tight sm:text-4xl">
            {t('home.title')}
          </h1>
          <p className="mt-2 max-w-2xl text-muted sm:text-lg">{t('home.subtitle')}</p>
          <form role="search" onSubmit={onSubmit} className="mt-5 flex max-w-2xl gap-2">
            <label htmlFor="home-search" className="sr-only">
              {t('search.label')}
            </label>
            <div className="relative flex-1">
              <Icon name="search" className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-muted" />
              <input
                id="home-search"
                type="search"
                value={q}
                onChange={(e) => setQ(e.target.value)}
                placeholder={t('search.placeholder')}
                className="input pl-10"
                autoComplete="off"
              />
            </div>
            <button type="submit" className="btn-primary">
              {t('search.submit')}
            </button>
          </form>
          <div className="mt-5 flex flex-wrap gap-2">
            <Link to="/calculator" className="btn-primary">
              <Icon name="calc" size={18} /> {t('home.openCalculator')}
            </Link>
            <Link to="/drugs" className="btn-ghost">
              <Icon name="pill" size={18} /> {t('home.browseDrugs', { count: drugs.length })}
            </Link>
          </div>
        </div>
      </section>

      <DraftBanner compact />

      <section aria-labelledby="cat-title">
        <h2 id="cat-title" className="mb-3 text-lg font-bold">
          {t('home.categories')}
        </h2>
        <ul className="grid gap-3 sm:grid-cols-2">
          {AVAILABLE_GROUPS.map((g) => {
            const count = drugs.filter((d) => d.category === g.category).length;
            const accent = g.category === 'vasoactive-inotrope' ? 'text-vaso bg-vaso/10' : 'text-sed bg-sed/10';
            return (
              <li key={g.id}>
                <Link
                  to={`/drugs?category=${g.category}`}
                  className="card group flex items-center gap-4 p-4 transition hover:border-primary/60 sm:p-5"
                  data-testid={`category-${g.id}`}
                >
                  <span className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-xl ${accent}`}>
                    <Icon name={GROUP_ICON[g.key] ?? 'pill'} size={24} />
                  </span>
                  <span className="min-w-0 flex-1">
                    <span className="block font-bold">{t(`groups.${g.key}.title`)}</span>
                    <span className="block text-sm text-muted">{t(`groups.${g.key}.desc`)}</span>
                    <span className="mt-1 block text-xs font-semibold text-primary">{t('home.drugCount', { count })}</span>
                  </span>
                  <Icon name="chevronRight" className="shrink-0 text-muted group-hover:text-primary" />
                </Link>
              </li>
            );
          })}
        </ul>
      </section>

      <section aria-labelledby="soon-title">
        <div className="mb-3 flex items-baseline justify-between gap-3">
          <h2 id="soon-title" className="text-lg font-bold">
            {t('home.comingSoonTitle')}
          </h2>
          <span className="text-xs text-muted">{t('home.comingSoonHint')}</span>
        </div>
        <ul className="grid grid-cols-1 gap-2.5 sm:grid-cols-2 lg:grid-cols-3">
          {COMING_SOON_GROUPS.map((g) => (
            <li
              key={g.id}
              aria-disabled="true"
              className="flex items-center justify-between gap-3 rounded-2xl border border-dashed border-border bg-surface/60 px-4 py-3"
            >
              <span className="min-w-0">
                <span className="block font-semibold leading-snug text-fg/80">{t(`groups.${g.key}.title`)}</span>
                <span className="block text-xs text-muted">{t('home.moduleCount', { count: g.moduleCount })}</span>
              </span>
              <span className="shrink-0 rounded-full bg-surface-2 px-2.5 py-1 text-[11px] font-bold uppercase tracking-wide text-muted">
                {t('common.comingSoon')}
              </span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
