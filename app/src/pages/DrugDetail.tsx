import { useTranslation } from 'react-i18next';
import { Link, useParams } from 'react-router-dom';
import { CategoryBadge, EvidenceBadge } from '../components/Badges';
import { ClinicalText } from '../components/ClinicalText';
import { DraftBanner } from '../components/DraftBanner';
import { Icon } from '../components/Icon';
import { db, getDrug, getModule, isWeightBased } from '../data';
import type { Drug } from '../data/schema';
import { useFormat } from '../lib/useFormat';
import NotFound from './NotFound';

function Section({ id, title, children }: { id: string; title: string; children: React.ReactNode }) {
  return (
    <section aria-labelledby={id} className="card p-4 sm:p-5">
      <h2 id={id} className="mb-3 text-base font-bold">
        {title}
      </h2>
      {children}
    </section>
  );
}

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="grid gap-1 border-b border-border py-2.5 last:border-0 sm:grid-cols-[180px_1fr] sm:gap-4">
      <dt className="text-sm font-semibold text-muted">{label}</dt>
      <dd className="text-sm leading-relaxed">{children}</dd>
    </div>
  );
}

function Missing() {
  const { t } = useTranslation();
  return <span className="italic text-muted">{t('common.notInSource')}</span>;
}

export default function DrugDetail() {
  const { id } = useParams();
  const drug = getDrug(id);
  if (!drug) return <NotFound />;
  return <DrugDetailView drug={drug} />;
}

function DrugDetailView({ drug }: { drug: Drug }) {
  const { t, i18n } = useTranslation();
  const f = useFormat();
  const mod = getModule(drug.moduleId);
  const d = drug.dosing;
  const localName = t(`drugNames.${drug.id}`, { defaultValue: drug.name });

  return (
    <article className="space-y-4" aria-labelledby="drug-title">
      <nav aria-label={t('a11y.breadcrumb')} className="text-sm">
        <Link to="/drugs" className="inline-flex items-center gap-1 font-semibold text-primary hover:underline">
          <Icon name="chevronLeft" size={16} /> {t('nav.drugs')}
        </Link>
      </nav>

      <DraftBanner />

      <header className="card p-4 sm:p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="min-w-0">
            <h1 id="drug-title" className="text-3xl font-extrabold tracking-tight">
              {drug.name}
            </h1>
            <p className="mt-1 text-muted">
              {i18n.language !== 'en' && localName !== drug.name ? <span className="font-medium text-fg">{localName}</span> : null}
              {i18n.language !== 'en' && localName !== drug.name && drug.synonyms.length ? ' · ' : null}
              {drug.synonyms.join(', ')}
            </p>
            <div className="mt-3 flex flex-wrap gap-2">
              <CategoryBadge category={drug.category} />
              {mod && <EvidenceBadge status={mod.evidence.status} />}
              <span className="inline-flex items-center rounded-full border border-border px-2.5 py-1 text-xs font-semibold text-muted">
                {t('drug.adult')} · {isWeightBased(drug) ? t('drug.weightBased') : t('drug.fixedDose')}
              </span>
            </div>
          </div>
          <Link to={`/calculator?drug=${drug.id}`} className="btn-primary w-full sm:w-auto" data-testid="open-calculator">
            <Icon name="calc" size={18} /> {t('drug.openInCalculator')}
          </Link>
        </div>
        {i18n.language !== 'en' && (
          <p className="mt-4 flex items-center gap-2 rounded-xl bg-surface-2 px-3 py-2 text-xs text-muted">
            <Icon name="globe" size={16} /> {t('drug.englishMaster')}
          </p>
        )}
      </header>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[minmax(0,1fr)_340px]">
        <div className="min-w-0 space-y-4">
          <Section id="sec-position" title={t('drug.position')}>
            <p className="text-sm leading-relaxed">{drug.position ? <ClinicalText text={drug.position} /> : <Missing />}</p>
          </Section>

          <Section id="sec-dosing" title={t('drug.dosing')}>
            <p className="mb-2 text-sm">
              <span className="text-muted">{t('dosing.unit')}:</span>{' '}
              <span className="num font-bold">{f.unit(drug.doseUnit)}</span>
            </p>
            <dl>
              <Row label={t('dosing.start')}>
                {d.start ? (
                  <>
                    <span className="num font-bold">
                      {f.range(d.start.min, d.start.max)} {f.unit(drug.doseUnit)}
                    </span>
                    <p className="mt-0.5 text-muted"><ClinicalText text={d.start.text} /></p>
                  </>
                ) : (
                  <Missing />
                )}
              </Row>
              <Row label={t('dosing.range')}>
                {d.range ? (
                  <>
                    <span className="num font-bold">
                      {f.range(d.range.min, d.range.max)} {f.unit(drug.doseUnit)}
                    </span>
                    <p className="mt-0.5 text-muted"><ClinicalText text={d.range.text} /></p>
                  </>
                ) : (
                  <Missing />
                )}
              </Row>
              <Row label={t('dosing.max')}>
                {d.max ? (
                  <>
                    {d.max.value !== null && (
                      <span className="num font-bold text-danger">
                        {f.num(d.max.value)} {f.unit(drug.doseUnit)}
                      </span>
                    )}
                    <p className="mt-0.5 text-muted"><ClinicalText text={d.max.text} /></p>
                  </>
                ) : (
                  <Missing />
                )}
              </Row>
              <Row label={t('dosing.titration')}>{d.titration ? <ClinicalText text={d.titration.text} /> : <Missing />}</Row>
              {d.loading && (
                <Row label={t('dosing.loading')}>
                  <span className="num font-bold">
                    {f.range(d.loading.doseMin, d.loading.doseMax)} {f.unit(d.loading.unit)}
                    {d.loading.durationMin ? ` · ${t('bolus.over', { min: d.loading.durationMin })}` : ''}
                  </span>
                  {d.loading.optional && <span className="ml-2 text-xs font-semibold text-muted">({t('bolus.optional')})</span>}
                  <p className="mt-0.5 text-muted"><ClinicalText text={d.loading.text} /></p>
                </Row>
              )}
              {d.weaning && <Row label={t('dosing.weaning')}><ClinicalText text={d.weaning} /></Row>}
              {d.organAdjustment && <Row label={t('dosing.organ')}><ClinicalText text={d.organAdjustment} /></Row>}
              {d.alternativeDosing.map((a, i) => (
                <Row key={i} label={t('dosing.alternative')}>
                  <ClinicalText text={a} />
                </Row>
              ))}
            </dl>
          </Section>

          <Section id="sec-prep" title={t('drug.preparations')}>
            <ul className="space-y-2 sm:hidden">
              {drug.preparations.map((p) => (
                <li key={p.id} className="rounded-xl bg-surface-2 p-3 text-sm">
                  <div className="flex items-baseline justify-between gap-2">
                    <span className="font-semibold">
                      {p.label}
                      {p.isDefault && <span className="ml-1.5 rounded bg-primary/15 px-1.5 py-0.5 text-[10px] font-bold uppercase text-primary">{t('prep.default')}</span>}
                    </span>
                    <span className="num font-bold">{f.num(p.concentration.value)} {f.unit(p.concentration.unit)}</span>
                  </div>
                  <dl className="mt-2 grid grid-cols-2 gap-x-3 gap-y-1 text-xs">
                    <dt className="text-muted">{t('prep.amount')}</dt>
                    <dd className="num">{p.amount ? `${f.num(p.amount.value)} ${f.unit(p.amount.unit)}` : <Missing />}</dd>
                    <dt className="text-muted">{t('prep.finalVolume')}</dt>
                    <dd className="num">{p.finalVolumeMl ? `${f.num(p.finalVolumeMl)} mL` : <Missing />}</dd>
                    <dt className="text-muted">{t('prep.diluent')}</dt>
                    <dd>{p.diluent ? <ClinicalText text={p.diluent} /> : <Missing />}</dd>
                  </dl>
                </li>
              ))}
            </ul>
            <div className="hidden overflow-x-auto sm:block">
              <table className="w-full min-w-[520px] text-left text-sm">
                <caption className="sr-only">{t('drug.preparations')}</caption>
                <thead>
                  <tr className="border-b border-border text-xs uppercase tracking-wide text-muted">
                    <th scope="col" className="whitespace-nowrap py-2 pr-3 font-semibold">{t('prep.label')}</th>
                    <th scope="col" className="whitespace-nowrap py-2 pr-3 font-semibold">{t('prep.amount')}</th>
                    <th scope="col" className="whitespace-nowrap py-2 pr-3 font-semibold">{t('prep.finalVolume')}</th>
                    <th scope="col" className="whitespace-nowrap py-2 pr-3 font-semibold">{t('prep.concentration')}</th>
                    <th scope="col" className="py-2 font-semibold">{t('prep.diluent')}</th>
                  </tr>
                </thead>
                <tbody>
                  {drug.preparations.map((p) => (
                    <tr key={p.id} className="border-b border-border align-top last:border-0">
                      <th scope="row" className="py-2.5 pr-3 font-semibold">
                        <span className="block">{p.label}</span>
                        {p.isDefault && <span className="mt-1 inline-block whitespace-nowrap rounded bg-primary/15 px-1.5 py-0.5 text-[10px] font-bold uppercase text-primary">{t('prep.default')}</span>}
                      </th>
                      <td className="num whitespace-nowrap py-2.5 pr-3">{p.amount ? `${f.num(p.amount.value)} ${f.unit(p.amount.unit)}` : <Missing />}</td>
                      <td className="num whitespace-nowrap py-2.5 pr-3">{p.finalVolumeMl ? `${f.num(p.finalVolumeMl)} mL` : <Missing />}</td>
                      <td className="num whitespace-nowrap py-2.5 pr-3 font-bold">{f.num(p.concentration.value)} {f.unit(p.concentration.unit)}</td>
                      <td className="py-2.5">{p.diluent ? <ClinicalText text={p.diluent} /> : <Missing />}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <ul className="mt-3 space-y-1.5 text-xs text-muted">
              {drug.preparations.filter((p) => p.note).map((p) => (
                <li key={p.id}>
                  <span className="font-semibold text-fg">{p.label}:</span> <ClinicalText text={p.note ?? ''} />
                </li>
              ))}
            </ul>
          </Section>

          <Section id="sec-examples" title={t('drug.workedExamples')}>
            <p className="mb-3 text-xs text-muted">{t('drug.workedExamplesNote')}</p>
            <ul className="space-y-2">
              {drug.workedExamples.map((w, i) => (
                <li key={i} className="rounded-xl bg-surface-2 p-3 text-sm">
                  <div className="flex flex-wrap items-baseline justify-between gap-2">
                    <span className="num font-semibold">
                      {f.num(w.dose)} {f.unit(w.doseUnit)}
                      {w.weightKg ? ` · ${w.weightKg} kg` : ''}
                    </span>
                    <span className="num text-base font-extrabold text-primary">{f.num(w.expectedMlH)} mL/h</span>
                  </div>
                  <p className="mt-1 font-mono text-xs text-muted" lang="en">{w.text}</p>
                </li>
              ))}
              {drug.bolusExamples.map((b, i) => (
                <li key={`b${i}`} className="rounded-xl border border-dashed border-border p-3 text-sm">
                  <span className="text-xs font-bold uppercase tracking-wide text-muted">{t('bolus.title')}</span>
                  <p className="mt-1 font-mono text-xs text-muted" lang="en">{b.text}</p>
                </li>
              ))}
            </ul>
          </Section>
        </div>

        <aside className="min-w-0 space-y-4">
          <Section id="sec-cautions" title={t('drug.cautions')}>
            {drug.contraindications.length > 0 && (
              <>
                <h3 className="mb-1.5 text-xs font-bold uppercase tracking-wide text-danger">{t('drug.contraindications')}</h3>
                <ul className="mb-3 space-y-2 text-sm">
                  {drug.contraindications.map((c, i) => (
                    <li key={i} className="flex gap-2">
                      <Icon name="x" size={16} className="mt-0.5 shrink-0 text-danger" />
                      <ClinicalText text={c} />
                    </li>
                  ))}
                </ul>
              </>
            )}
            {drug.cautions.length ? (
              <ul className="space-y-2 text-sm">
                {drug.cautions.map((c, i) => (
                  <li key={i} className="flex gap-2">
                    <Icon name="alert" size={16} className="mt-0.5 shrink-0 text-warn" />
                    <ClinicalText text={c} />
                  </li>
                ))}
              </ul>
            ) : (
              <Missing />
            )}
          </Section>

          {mod && (
            <Section id="sec-source" title={t('drug.source')}>
              <dl className="space-y-2 text-sm">
                <div>
                  <dt className="text-xs text-muted">{t('source.module')}</dt>
                  <dd className="font-mono text-xs font-semibold">{mod.id}</dd>
                </div>
                <div>
                  <dt className="text-xs text-muted">{t('source.bundle')}</dt>
                  <dd className="font-mono text-xs">{mod.bundle} · {db.meta.contentVersion}</dd>
                </div>
                <div>
                  <dt className="text-xs text-muted">{t('source.evidence')}</dt>
                  <dd className="mt-1"><EvidenceBadge status={mod.evidence.status} /></dd>
                </div>
                <div>
                  <dt className="text-xs text-muted">{t('source.lastChecked')}</dt>
                  <dd className="num">{mod.evidence.lastChecked}</dd>
                </div>
                <div>
                  <dt className="text-xs text-muted">{t('source.primary')}</dt>
                  <dd className="text-xs leading-relaxed"><ClinicalText text={mod.evidence.primarySource} /></dd>
                </div>
                <div>
                  <dt className="text-xs text-muted">{t('source.note')}</dt>
                  <dd className="text-xs leading-relaxed text-muted"><ClinicalText text={mod.evidence.note} /></dd>
                </div>
                <div>
                  <dt className="text-xs text-muted">{t('source.review')}</dt>
                  <dd className="text-xs font-semibold text-warn">{t(`review.${drug.reviewStatus}`)}</dd>
                </div>
                {mod.evidence.primarySourceUrl && (
                  <div>
                    <a href={mod.evidence.primarySourceUrl} target="_blank" rel="noreferrer noopener" className="inline-flex items-center gap-1 text-xs font-semibold text-primary hover:underline">
                      {t('source.open')} <Icon name="external" size={14} />
                    </a>
                  </div>
                )}
              </dl>
            </Section>
          )}

          {mod && (
            <details className="card p-4 sm:p-5">
              <summary className="cursor-pointer text-base font-bold">{t('drug.moduleRules')}</summary>
              <ul className="mt-3 list-disc space-y-2 pl-5 text-sm leading-relaxed">
                {mod.rules.map((r, i) => (
                  <li key={i}><ClinicalText text={r} /></li>
                ))}
              </ul>
            </details>
          )}
        </aside>
      </div>
    </article>
  );
}
