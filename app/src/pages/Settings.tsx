import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { BRAND } from '../config/brand';
import { db } from '../data';
import { LANGUAGES } from '../i18n';
import { useSettings, type MicroSymbol, type ThemePref } from '../state/settings';

function Radio<T extends string>({ name, value, current, onChange, children }: { name: string; value: T; current: T; onChange: (v: T) => void; children: React.ReactNode }) {
  const checked = value === current;
  return (
    <label className={`flex min-h-[48px] cursor-pointer items-center gap-3 rounded-xl border px-3 py-2.5 text-sm font-semibold transition ${checked ? 'border-primary bg-primary/5 ring-1 ring-primary/40' : 'border-border hover:bg-surface-2'}`}>
      <input type="radio" name={name} value={value} checked={checked} onChange={() => onChange(value)} className="h-4 w-4 accent-[rgb(var(--c-primary))]" />
      {children}
    </label>
  );
}

export default function Settings() {
  const { t } = useTranslation();
  const s = useSettings();
  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <header>
        <h1 className="text-2xl font-extrabold tracking-tight sm:text-3xl">{t('settings.title')}</h1>
        <p className="mt-1 text-muted">{t('settings.subtitle')}</p>
      </header>

      <fieldset className="card p-4 sm:p-5">
        <legend className="sr-only">{t('settings.language')}</legend>
        <h2 className="mb-1 text-base font-bold" aria-hidden="true">{t('settings.language')}</h2>
        <p className="mb-3 text-xs text-muted">{t('settings.languageHelp')}</p>
        <div className="grid gap-2 sm:grid-cols-2">
          {LANGUAGES.map((l) => (
            <Radio key={l.code} name="lang" value={l.code} current={s.lang} onChange={s.setLang}>
              <span lang={l.htmlLang}>{l.label}</span>
              {l.code === 'en' && <span className="ml-auto text-xs font-normal text-muted">{t('settings.master')}</span>}
            </Radio>
          ))}
        </div>
      </fieldset>

      <fieldset className="card p-4 sm:p-5">
        <legend className="sr-only">{t('settings.theme')}</legend>
        <h2 className="mb-3 text-base font-bold" aria-hidden="true">{t('settings.theme')}</h2>
        <div className="grid gap-2 sm:grid-cols-3">
          {(['system', 'light', 'dark'] as ThemePref[]).map((v) => (
            <Radio key={v} name="theme" value={v} current={s.theme} onChange={s.setTheme}>
              {t(`theme.${v}`)}
            </Radio>
          ))}
        </div>
      </fieldset>

      <fieldset className="card p-4 sm:p-5">
        <legend className="sr-only">{t('settings.units')}</legend>
        <h2 className="mb-1 text-base font-bold" aria-hidden="true">{t('settings.units')}</h2>
        <p className="mb-3 text-xs text-muted">{t('settings.unitsHelp')}</p>
        <div className="grid gap-2 sm:grid-cols-2">
          {(['mcg', 'µg'] as MicroSymbol[]).map((v) => (
            <Radio key={v} name="micro" value={v} current={s.micro} onChange={s.setMicro}>
              <span className="num">{v}/kg/min</span>
            </Radio>
          ))}
        </div>
        <p className="mt-3 text-xs text-muted">{t('settings.roundingInfo')}</p>
      </fieldset>

      <section className="card p-4 text-sm sm:p-5">
        <h2 className="mb-2 text-base font-bold">{t('settings.dataTitle')}</h2>
        <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-1.5">
          <dt className="text-muted">{t('settings.appVersion')}</dt>
          <dd className="num font-semibold">{BRAND.name} {BRAND.appVersion}</dd>
          <dt className="text-muted">{t('settings.contentVersion')}</dt>
          <dd className="num font-semibold">{db.meta.contentVersion} ({db.meta.extractedAt})</dd>
          <dt className="text-muted">{t('settings.drugsCount')}</dt>
          <dd className="num font-semibold">{db.drugs.length}</dd>
          <dt className="text-muted">{t('source.review')}</dt>
          <dd className="font-semibold text-warn">{t(`review.${db.meta.reviewStatus}`)}</dd>
        </dl>
        <Link to="/about" className="btn-ghost mt-4">
          {t('nav.about')}
        </Link>
      </section>
    </div>
  );
}
