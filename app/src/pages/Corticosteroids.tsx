import { useEffect, useRef, useState, type FormEvent } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import {
  compareCorticosteroids, corticosteroidCatalog as catalog, corticosteroidLocale,
  CorticosteroidCalculationError, formatCorticosteroidNumber, type ComparisonResult,
} from '../corticosteroids/calculator';
import { corticosteroidCopy } from '../corticosteroids/copy';
import ShortCourseReferences from '../corticosteroids/ShortCourseReferences';

function SourceLinks({ ids, label }: { ids: string[]; label: string }) {
  return <ul className="flex flex-wrap gap-x-4 gap-y-1 text-sm">
    {ids.map(id => {
      const source = catalog.sources.find(item => item.id === id);
      return source ? <li key={id}><a className="underline break-words" href={source.url} target="_blank" rel="noreferrer">{label}: {source.title} · {source.version}</a></li> : null;
    })}
  </ul>;
}

export default function Corticosteroids() {
  const { i18n } = useTranslation();
  const locale = corticosteroidLocale(i18n.language);
  const ui = corticosteroidCopy[locale];
  const fmt = (value: number) => formatCorticosteroidNumber(value, locale);
  const drugName = (id: string) => catalog.drugs.find(drug => drug.id === id)?.name[locale] ?? id;
  const [tableId, setTableId] = useState('');
  const [sourceDrugId, setSourceDrugId] = useState('hydrocortisone');
  const [doseMg, setDoseMg] = useState('');
  const [route, setRoute] = useState('');
  const [doseBasis, setDoseBasis] = useState('');
  const [result, setResult] = useState<ComparisonResult>();
  const [error, setError] = useState<CorticosteroidCalculationError['code']>();
  const resultRef = useRef<HTMLElement>(null);
  useEffect(() => { if (result) resultRef.current?.focus(); }, [result]);
  const clearResult = () => { setResult(undefined); setError(undefined); };
  function reset() {
    clearResult(); setTableId(''); setSourceDrugId('hydrocortisone');
    setDoseMg(''); setRoute(''); setDoseBasis('');
  }
  function calculate(event: FormEvent) {
    event.preventDefault(); clearResult();
    try { setResult(compareCorticosteroids({ tableId, sourceDrugId, doseMg, route, doseBasis })); }
    catch (caught) {
      if (caught instanceof CorticosteroidCalculationError) setError(caught.code);
      else throw caught;
    }
  }
  const selectedTable = catalog.tables.find(table => table.id === result?.tableId);
  const adult = catalog.hydrocortisone.adult_adrenal_crisis;
  const septic = catalog.hydrocortisone.adult_septic_shock;
  const pediatric = catalog.hydrocortisone.pediatric_adrenal_crisis;
  const pediatricSepsis = catalog.hydrocortisone.pediatric_septic_shock;
  const anaphylaxis = catalog.hydrocortisone.anaphylaxis;
  const range = (values: [number, number]) => values[0] === values[1] ? fmt(values[0]) : values.map(fmt).join('–');

  return <div className="space-y-6 min-w-0">
    <header className="card p-5 sm:p-7">
      <p className="section-title">{ui.subtitle}</p>
      <h1 className="mt-2 text-3xl font-bold">{ui.title}</h1>
      <p className="mt-3">{ui.scope}</p>
      <Link className="mt-3 inline-block underline" to="/clinical/medication-selection-safety">{ui.return}</Link>
    </header>

    <p className="rounded-xl border border-warning/50 bg-warning/10 p-4">{ui.sourceDifference}</p>

    <div className="grid items-start gap-5 xl:grid-cols-2">
      <form noValidate onSubmit={calculate} className="card space-y-4 p-5" aria-label={ui.comparison}>
        <h2 className="text-xl font-bold">{ui.comparison}</h2>
        <label className="block"><span className="label">{ui.reference}</span>
          <select className="input" value={tableId} onChange={event => { clearResult(); setTableId(event.target.value); }}>
            <option value="">{ui.choose}</option>
            {catalog.tables.map(table => <option key={table.id} value={table.id}>{table.label}</option>)}
          </select>
        </label>
        <label className="block"><span className="label">{ui.drug}</span>
          <select className="input" value={sourceDrugId} onChange={event => { clearResult(); setSourceDrugId(event.target.value); }}>
            {catalog.drugs.map(drug => <option key={drug.id} value={drug.id}>{drug.name[locale]}</option>)}
          </select>
        </label>
        <div className="grid gap-4 sm:grid-cols-2">
          <label className="block"><span className="label">{ui.dose}</span>
            <input className="input" inputMode="decimal" autoComplete="off" value={doseMg} aria-describedby="corticosteroid-input-hint"
              onChange={event => { clearResult(); setDoseMg(event.target.value); }} />
          </label>
          <label className="block"><span className="label">{ui.route}</span>
            <select className="input" value={route} onChange={event => { clearResult(); setRoute(event.target.value); }}>
              <option value="">{ui.choose}</option><option value="oral">{ui.oral}</option><option value="iv">{ui.iv}</option>
            </select>
          </label>
        </div>
        <label className="block"><span className="label">{ui.basis}</span>
          <select className="input" value={doseBasis} onChange={event => { clearResult(); setDoseBasis(event.target.value); }}>
            <option value="">{ui.choose}</option><option value="single_dose">{ui.single}</option><option value="daily_total">{ui.daily}</option>
          </select>
        </label>
        <p id="corticosteroid-input-hint" className="text-sm text-muted">{ui.inputHint}</p>
        {error && <p role="alert" className="text-danger font-semibold">{ui.errors[error]}</p>}
        <div className="flex flex-wrap gap-2">
          <button className="btn-primary" type="submit">{ui.calculate}</button>
          <button className="btn-ghost" type="button" onClick={reset}>{ui.reset}</button>
        </div>
      </form>

      <div className="space-y-4 min-w-0">
        <p className="card p-4">{ui.resultCaution}</p>
        {result && selectedTable && <section ref={resultRef} tabIndex={-1} className="card p-5 space-y-4 min-w-0" aria-labelledby="corticosteroid-result-title">
          <h2 id="corticosteroid-result-title" className="text-xl font-bold">{ui.result}</h2>
          <p>{ui.selected}: <strong>{selectedTable.label}</strong></p>
          <p>{ui.sourceDose}: <strong>{drugName(result.sourceDrugId)} · {fmt(result.inputMg)} mg</strong> · {result.doseBasis === 'daily_total' ? ui.daily : ui.single} · {result.route === 'oral' ? ui.oral : ui.iv}</p>
          <p className="text-sm">{ui.sameBasis}</p>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <caption className="sr-only">{ui.result}</caption>
              <thead><tr className="border-b"><th scope="col" className="p-2">{ui.tableDrug}</th><th scope="col" className="p-2">{ui.equivalent}</th><th scope="col" className="p-2">{ui.duration}</th></tr></thead>
              <tbody>{result.rows.map(row => <tr key={row.drugId} className="border-b last:border-b-0" data-drug={row.drugId}>
                <th scope="row" className="p-2 font-medium">{drugName(row.drugId)}</th>
                <td className="p-2 tabular-nums" data-amount="mg">{fmt(row.approximateMg)}</td>
                <td className="p-2 whitespace-nowrap">{range(row.biologicalHalfLifeHours)}</td>
              </tr>)}</tbody>
            </table>
          </div>
          <details className="text-sm"><summary className="cursor-pointer font-semibold">{ui.calculation}</summary>
            <ul className="mt-2 space-y-1">{result.rows.map(row => <li key={row.drugId}>{drugName(row.drugId)}: {fmt(result.inputMg)} × {fmt(row.referenceEquivalentMg)} ÷ {fmt(result.sourceEquivalentMg)} = {fmt(row.approximateMg)} mg</li>)}</ul>
          </details>
          <SourceLinks ids={[result.sourceId]} label={ui.source} />
        </section>}
      </div>
    </div>

    <section className="card p-5 space-y-3 min-w-0" aria-labelledby="corticosteroid-table-title">
      <h2 id="corticosteroid-table-title" className="text-xl font-bold">{ui.tableComparison}</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <caption className="sr-only">{ui.tableComparison}</caption>
          <thead><tr className="border-b"><th scope="col" className="p-2">{ui.tableDrug}</th>
            {catalog.tables.map(table => <th key={table.id} scope="col" className="p-2">{table.label} (mg)</th>)}
            <th scope="col" className="p-2">{ui.mineral}</th></tr></thead>
          <tbody>{catalog.drugs.map(drug => <tr key={drug.id} className="border-b last:border-b-0">
            <th scope="row" className="p-2 font-medium">{drug.name[locale]}</th>
            {catalog.tables.map(table => <td className="p-2 tabular-nums" key={table.id}>{fmt(table.rows.find(row => row.drug_id === drug.id)!.equivalent_mg)}</td>)}
            <td className="p-2 tabular-nums">{fmt(drug.mineralocorticoid_relative_activity)}</td>
          </tr>)}</tbody>
        </table>
      </div>
      <p className="text-sm text-muted">{ui.mineralSource}</p>
      <SourceLinks ids={catalog.tables.map(table => table.source_id)} label={ui.source} />
    </section>

    <ShortCourseReferences locale={locale}/>

    <section className="space-y-4" aria-labelledby="hydrocortisone-title">
      <h2 id="hydrocortisone-title" className="text-2xl font-bold">{ui.hydrocortisone}</h2>
      <p className="text-sm text-muted">{ui.clinicalLanguage}</p>
      <section className="card p-5 space-y-4" aria-labelledby="hydrocortisone-adult">
        <h3 id="hydrocortisone-adult" className="text-xl font-bold">{ui.adult}</h3>
        <div className="grid gap-6 lg:grid-cols-2">
          <article className="space-y-3"><h4 className="font-bold">{ui.adrenal}</h4>
            <p><strong>{ui.initial}: {fmt(adult.initial_mg)} mg IV/IM</strong></p>
            <p>{ui.then}: {fmt(adult.maintenance_total_mg_per_24h)} mg/24 h · {ui.continuous}; {ui.alternative}: {fmt(adult.maintenance_alternative_mg)} mg IV/IM {ui.every} {adult.maintenance_interval_hours} h.</p>
            <p lang="es">{adult.summary_es}</p>
            <Link className="underline inline-block" to={`/clinical/${adult.module_id}`}>{ui.openModule}</Link>
            <SourceLinks ids={adult.source_ids} label={ui.source} />
          </article>
          <article className="space-y-3"><h4 className="font-bold">{ui.sepsis}</h4>
            <p>{ui.commonRegimen}: <strong>{fmt(septic.common_regimen_total_mg_per_24h)} mg IV/24 h</strong> · {ui.continuous}; {ui.alternative}: {fmt(septic.common_regimen_divided_mg)} mg IV {ui.every} {septic.common_regimen_interval_hours} h.</p>
            <p lang="es">{septic.summary_es}</p>
            <Link className="underline inline-block" to={`/clinical/${septic.module_id}`}>{ui.openModule}</Link>
            <SourceLinks ids={septic.source_ids} label={ui.source} />
          </article>
        </div>
      </section>
      <section className="card p-5 space-y-4 min-w-0" aria-labelledby="hydrocortisone-pediatric">
        <h3 id="hydrocortisone-pediatric" className="text-xl font-bold">{ui.pediatric} · {ui.adrenal}</h3>
        <p lang="es">{pediatric.summary_es}</p>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <caption className="sr-only">{ui.pediatric} · {ui.adrenal} · RCH 2024</caption>
            <thead><tr className="border-b"><th scope="col" className="p-2">{ui.age}</th><th scope="col" className="p-2">{ui.initial} IV/IM (mg)</th><th scope="col" className="p-2">{ui.followedBy} (mg)</th></tr></thead>
            <tbody>{pediatric.rows.map((row, index) => <tr key={index} className="border-b last:border-b-0">
              <th scope="row" className="p-2 font-medium">{row.age_label[locale]}</th><td className="p-2">{fmt(row.initial_mg)}</td><td className="p-2">{range(row.maintenance_mg)}</td>
            </tr>)}</tbody>
          </table>
        </div>
        <Link className="underline inline-block" to={`/clinical/${pediatric.module_id}`}>{ui.openModule}</Link>
        <SourceLinks ids={pediatric.source_ids} label={ui.source} />
        <div className="border-t pt-4 space-y-3"><h4 className="font-bold">{ui.pediatric} · {ui.sepsis}</h4>
          <p lang="es">{pediatricSepsis.summary_es}</p>
          <Link className="underline inline-block" to={`/clinical/${pediatricSepsis.module_id}`}>{ui.openModule}</Link>
          <SourceLinks ids={pediatricSepsis.source_ids} label={ui.source} />
        </div>
      </section>
      <article className="card p-5 space-y-3"><h3 className="text-xl font-bold">{ui.anaphylaxis}</h3>
        <p lang="es">{anaphylaxis.summary_es}</p>
        <Link className="underline inline-block" to={`/clinical/${anaphylaxis.module_id}`}>{ui.openModule}</Link>
        <SourceLinks ids={anaphylaxis.source_ids} label={ui.source} />
      </article>
    </section>

    <section className="card p-5 space-y-3">
      <h2 className="text-xl font-bold">{ui.related}</h2>
      <div className="grid gap-4 sm:grid-cols-2">{(['adult', 'pediatric'] as const).map(population => <div key={population}>
        <h3 className="font-semibold">{population === 'adult' ? ui.adult : ui.pediatric}</h3>
        <ul className="list-disc ml-5 mt-2 space-y-2">{catalog.related_modules.filter(module => module.population === population).map(module =>
          <li key={module.id}><Link className="underline" lang="es" to={`/clinical/${module.id}`}>{module.title_es}</Link></li>)}</ul>
      </div>)}</div>
    </section>

    <details className="card p-5"><summary className="cursor-pointer text-xl font-bold">{ui.sources}</summary>
      <ul className="mt-4 space-y-4">{catalog.sources.map(source => <li key={source.id} className="space-y-1 break-words">
        <a href={source.url} target="_blank" rel="noreferrer" className="underline font-semibold">{source.title}</a>
        <p className="text-sm">{ui.version}: {source.version}</p><p className="text-sm">{ui.sourceLocator}: <span lang="en">{source.locator}</span></p>
      </li>)}</ul>
    </details>
  </div>;
}
