import { useTranslation } from 'react-i18next';
import { EvidenceBadge } from '../components/Badges';
import { Icon } from '../components/Icon';
import { LogoMark } from '../components/Logo';
import { BRAND } from '../config/brand';
import { db } from '../data';

export default function About() {
  const { t } = useTranslation();
  const modules = Object.values(db.modules);
  return (
    <div className="mx-auto max-w-3xl space-y-4">
      <header className="flex items-center gap-4">
        <LogoMark size={56} />
        <div>
          <h1 className="text-2xl font-extrabold tracking-tight sm:text-3xl">{t('about.title')}</h1>
          <p className="text-muted">
            {BRAND.name} {BRAND.appVersion} · {t('footer.content', { version: db.meta.contentVersion })}
          </p>
        </div>
      </header>

      <section className="rounded-2xl border-2 border-danger/50 bg-surface p-4 sm:p-6" aria-labelledby="disc-title" data-testid="disclaimer">
        <h2 id="disc-title" className="flex items-center gap-2 text-lg font-extrabold text-danger">
          <Icon name="shield" /> {t('about.disclaimerTitle')}
        </h2>
        <ul className="mt-3 list-disc space-y-2 pl-5 text-sm leading-relaxed">
          <li>{t('about.d1')}</li>
          <li>{t('about.d2')}</li>
          <li>{t('about.d3')}</li>
          <li>{t('about.d4')}</li>
          <li>{t('about.d5')}</li>
        </ul>
      </section>

      <section className="card p-4 sm:p-6" aria-labelledby="prov-title">
        <h2 id="prov-title" className="text-lg font-bold">{t('about.provenanceTitle')}</h2>
        <p className="mt-2 text-sm leading-relaxed text-muted">{t('about.provenanceBody')}</p>
        <ul className="mt-4 space-y-3">
          {modules.map((m) => (
            <li key={m.id} className="rounded-xl bg-surface-2 p-3 text-sm">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <code className="font-mono text-xs font-bold">{m.id}</code>
                <EvidenceBadge status={m.evidence.status} />
              </div>
              <p className="mt-1 font-mono text-xs text-muted">{m.bundle} · {m.evidence.storedVersion} · {m.evidence.lastChecked}</p>
            </li>
          ))}
        </ul>
      </section>

      <section className="card p-4 sm:p-6" aria-labelledby="ev-title">
        <h2 id="ev-title" className="text-lg font-bold">{t('about.evidenceTitle')}</h2>
        <ul className="mt-3 space-y-2 text-sm">
          {(['green', 'yellow', 'red'] as const).map((s) => (
            <li key={s} className="flex flex-col gap-1 sm:flex-row sm:items-center sm:gap-3">
              <EvidenceBadge status={s} />
              <span className="text-muted">{t(`evidence.${s}Help`)}</span>
            </li>
          ))}
        </ul>
      </section>

      <section className="card p-4 sm:p-6" aria-labelledby="priv-title">
        <h2 id="priv-title" className="text-lg font-bold">{t('about.privacyTitle')}</h2>
        <p className="mt-2 text-sm leading-relaxed text-muted">{t('about.privacyBody')}</p>
      </section>
    </div>
  );
}
