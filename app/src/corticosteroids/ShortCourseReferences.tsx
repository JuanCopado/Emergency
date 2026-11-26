import { Link } from 'react-router-dom';
import { corticosteroidCatalog as catalog, formatCorticosteroidNumber } from './calculator';
import { corticosteroidCopy } from './copy';
import type { CorticosteroidLocale } from './types';

function Sources({ ids }: { ids: string[] }) {
  return <ul className="mt-3 space-y-2 text-sm">
    {ids.map(id => {
      const source = catalog.sources.find(item => item.id === id);
      return source ? <li key={id}><a className="underline break-words" href={source.url} target="_blank" rel="noreferrer">{source.title} · {source.version}</a></li> : null;
    })}
  </ul>;
}

export default function ShortCourseReferences({ locale }: { locale: CorticosteroidLocale }) {
  const ui = corticosteroidCopy[locale];
  const reference = catalog.short_courses;
  const bell = reference.bell_palsy;
  const regimen = bell.reference_regimen;
  const drug = catalog.drugs.find(item => item.id === regimen.drug_id)!;
  const fmt = (value: number) => formatCorticosteroidNumber(value, locale);
  return <section className="space-y-4 min-w-0" aria-labelledby="short-course-title">
    <h2 id="short-course-title" className="text-2xl font-bold">{ui.shortCourses}</h2>
    <p className="text-sm text-muted">{ui.clinicalLanguage}</p>
    <article className="card p-5 space-y-4 min-w-0" aria-labelledby="bell-reference-title">
      <h3 id="bell-reference-title" className="text-xl font-bold">{ui.bellPalsy}</h3>
      <p lang="es">{bell.indication_es}</p>
      <div className="rounded-xl border border-border p-4 space-y-2">
        <p className="font-semibold">{ui.trialRegimen}</p>
        <p><strong>{drug.name[locale]} {fmt(regimen.dose_mg)} mg {ui.oral.toLocaleLowerCase()} · {ui.every} {regimen.interval_hours} {ui.hours} · {regimen.duration_days} {ui.days}</strong> ({fmt(regimen.total_mg_per_day)} mg/24 h).</p>
        <p lang="es" className="text-sm">{bell.regimen_scope_es}</p>
      </div>
      <div className="rounded-xl border border-warn p-4 space-y-2" aria-labelledby="bell-pediatric-title">
        <h4 id="bell-pediatric-title" className="font-semibold">{ui.pediatricBell}</h4>
        <p lang="es">{bell.pediatric_es}</p>
      </div>
      <div className="space-y-2"><h4 className="font-semibold">{ui.eyeProtection}</h4><p lang="es">{bell.eye_care_es}</p></div>
      <Link className="underline inline-block" to={`/clinical/${bell.module_id}`}>{ui.openModule} · {ui.bellPalsy}</Link>
      <details className="rounded-xl border border-border p-4">
        <summary className="font-semibold cursor-pointer">{ui.clinicalDetails}</summary>
        <div className="mt-3 space-y-3" lang="es"><p>{bell.differential_es}</p><p>{bell.safety_es}</p><p>{bell.follow_up_es}</p></div>
        <Sources ids={bell.source_ids}/>
      </details>
    </article>
    <div className="card p-5 space-y-3 min-w-0">
      <h3 className="text-xl font-bold">{ui.courseWithdrawal}</h3>
      <p lang="es">{reference.duration_withdrawal.summary_es}</p>
      <Sources ids={reference.duration_withdrawal.source_ids}/>
    </div>
    <div className="card p-5 space-y-3 min-w-0">
      <h3 className="text-xl font-bold">{ui.existingShortCourses}</h3>
      <p>{ui.shortCourseLinksHelp}</p>
      <ul className="list-disc ml-5 space-y-2">{reference.existing_module_ids.map(id => {
        const linked = catalog.related_modules.find(module => module.id === id)!;
        return <li key={id}><Link className="underline" lang="es" to={`/clinical/${id}`}>{linked.title_es}</Link></li>;
      })}</ul>
    </div>
  </section>;
}
