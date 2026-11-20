import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { reviewedWithoutDifference, topicReviews } from '../context/country-notes';
import dossier from '../../../clinical/references/t02-country-notes.json';
import { countries, loadContext } from '../context/reference-context';

const euCountries = new Set(['DE', 'ES', 'FR', 'IT', 'PT']);
const moduleTopics: Record<string, string[]> = {
  'acute-ischemic-stroke': ['Tenecteplasa'],
  'anticoagulation-reversal': ['PCC', 'Idarucizumab', 'Andexanet alfa'],
  'status-epilepticus': ['Fenitoína', 'Fosfenitoína', 'Midazolam'],
  'pediatric-status-epilepticus': ['Fenitoína', 'Fosfenitoína', 'Midazolam'],
  anaphylaxis: ['Adrenalina'],
  'tension-pneumothorax': ['Descompresión torácica'],
  'PROC-THX-001': ['Descompresión torácica'],
  'PROC-THX-002': ['Descompresión torácica'],
};
const drugTopics: Record<string, string> = {
  tenecteplase: 'Tenecteplasa', tnkase: 'Tenecteplasa', metalyse: 'Tenecteplasa',
  epinephrine: 'Adrenalina', epinefrina: 'Adrenalina', adrenaline: 'Adrenalina',
  phenytoin: 'Fenitoína', fosphenytoin: 'Fosfenitoína', andexanet: 'Andexanet alfa',
  octaplex: 'PCC', kcentra: 'PCC', balfaxar: 'PCC',
};
const allTopics = [...new Set(dossier.records.map(record => record.topic))];

function CountryColumn({ code, topics }: { code: string; topics: string[] }) {
  const { t, i18n } = useTranslation();
  const names = new Intl.DisplayNames([i18n.language], { type: 'region' });
  const records = dossier.records.filter(record => topics.includes(record.topic));
  const sections = records.map(record => ({
    ...record,
    sources: record.sources.filter(source => source.scope === code ||
      (source.scope === 'EU' && euCountries.has(code))),
  })).filter(record => record.sources.length > 0);
  const hasNationalNote = sections.some(record => record.sources.some(source => source.scope === code));
  const reviewed = reviewedWithoutDifference(code, topics, topicReviews);
  return <section className="min-w-0 space-y-2">
    <h3 className="font-bold">{names.of(code)}</h3>
    {reviewed && <a className="underline" href={reviewed.source}>{t('countryNotes.noDifference')} · {reviewed.reviewedOn}</a>}
    {!reviewed && !hasNationalNote && <p>{t('countryNotes.pending')}</p>}
    {sections.map(record => <div key={record.id} className="rounded-lg border border-border p-3">
      <h4 lang="es" className="font-semibold">{record.topic} · {record.id}</h4>
      <ul className="space-y-2">{record.sources.map(source => <li key={source.url}>
        <p lang="es">{source.note}</p>
        <a className="underline" href={source.url} lang="es">{names.of(source.scope)} · {source.label}</a>
      </li>)}</ul>
    </div>)}
  </section>;
}

export default function CountryReferences({ primary = loadContext().value.countryCode, moduleId, drug }: {
  primary?: string | null; moduleId?: string; drug?: string;
}) {
  const { t, i18n } = useTranslation();
  const [compare, setCompare] = useState('');
  const [topic, setTopic] = useState('');
  if (!primary) return null;
  const direct = allTopics.find(name => name.toLowerCase() === drug?.toLowerCase());
  const drugTopic = direct ?? drugTopics[drug?.toLowerCase() ?? ''];
  let topics = allTopics;
  if (moduleId !== undefined) topics = moduleTopics[moduleId] ?? [];
  else if (drug !== undefined) topics = drugTopic ? [drugTopic] : [];
  else if (topic) topics = [topic];
  const names = new Intl.DisplayNames([i18n.language], { type: 'region' });
  const shared = dossier.records.filter(record => topics.includes(record.topic))
    .flatMap(record => record.sources.filter(source => source.scope === 'INT'));
  return <section className="card space-y-3 p-4 text-sm print:hidden">
    <h2 className="font-bold">{t('countryNotes.title')}</h2>
    <p className="text-muted">{t('countryNotes.scope')} · {dossier.decision_date}</p>
    {moduleId === undefined && drug === undefined && <label>{t('countryNotes.topic')} <select value={topic} onChange={event => setTopic(event.target.value)}>
      <option value="">{t('countryNotes.all')}</option>
      {allTopics.map(name => <option key={name}>{name}</option>)}
    </select></label>}
    <label className="block">{t('countryNotes.compare')} <select value={compare} onChange={event => setCompare(event.target.value)}>
      <option value="">{t('countryNotes.off')}</option>
      {countries.filter(country => country.code !== primary).map(country =>
        <option key={country.code} value={country.code}>{names.of(country.code)}</option>)}
    </select></label>
    <div className="grid gap-4 sm:grid-cols-2"><CountryColumn code={primary} topics={topics} />
      {compare && compare !== primary && <CountryColumn code={compare} topics={topics} />}</div>
    {shared.map(source => <p key={source.url} lang="es">{source.note} <a className="underline" href={source.url}>ERC · {source.label}</a></p>)}
  </section>;
}
