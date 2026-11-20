import CountryReferences from './CountryReferences';
import { useId, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { contextSchema, contextStorageKey, countries, defaultContext, environments, loadContext, organizations, resourceNames, resourceStates, type ReferenceContext } from '../context/reference-context';
import { writeStorage } from '../lib/storage';

export default function ReferenceContextSelector() {
  const { t, i18n } = useTranslation();
  const [initial] = useState(loadContext);
  const [context, setContext] = useState(initial.value);
  const id = useId();
  const names = new Intl.DisplayNames([i18n.language], { type: 'region' });
  function update(next: ReferenceContext) {
    const valid = contextSchema.parse(next);
    setContext(valid);
    writeStorage(contextStorageKey, JSON.stringify(valid));
  }
  const disabled = context.mode === 'international';
  const selectClass = 'mt-1 min-h-[48px] w-full rounded-lg border border-border bg-surface px-3 text-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-primary disabled:opacity-60';
  return (
    <fieldset className="card space-y-3 p-4 sm:p-5" aria-describedby={`${id}-help ${id}-status`}>
      <legend className="px-1 text-base font-bold">{t('referenceContext.title')}</legend>
      <p id={`${id}-help`} className="text-sm text-muted">{t('referenceContext.help')}</p>
      {initial.recovered && <p role="alert" className="text-sm text-warn">{t('referenceContext.recovered')}</p>}
      <label className="block text-sm font-semibold">{t('referenceContext.mode')}
        <select className={selectClass} value={context.mode} onChange={event => update(event.target.value === 'international' ? defaultContext : { ...context, mode: 'declared' })}>
          <option value="international">{t('referenceContext.international')}</option>
          <option value="declared">{t('referenceContext.declared')}</option>
        </select>
      </label>
      <div className="grid gap-3 sm:grid-cols-2">
        <label className="block text-sm font-semibold">{t('referenceContext.country')}
          <select className={selectClass} disabled={disabled} value={context.countryCode ?? ''} onChange={event => update({ ...defaultContext, mode: 'declared', countryCode: event.target.value || null })}>
            <option value="">{t('referenceContext.unspecified')}</option>
            {countries.map(country => <option key={country.code} value={country.code}>{names.of(country.code) ?? country.name_es}</option>)}
          </select>
        </label>
        <label className="block text-sm font-semibold">{t('referenceContext.organization')}
          <select className={selectClass} disabled={disabled} value={context.organization} onChange={event => update({ ...context, organization: event.target.value as ReferenceContext['organization'], environment: 'unspecified', resources: { ...defaultContext.resources } })}>
            {organizations.map(value => <option key={value} value={value}>{t(`referenceContext.organizations.${value}`)}</option>)}
          </select>
        </label>
        <label className="block text-sm font-semibold">{t('referenceContext.environment')}
          <select className={selectClass} disabled={disabled} value={context.environment} onChange={event => update({ ...context, environment: event.target.value as ReferenceContext['environment'], resources: { ...defaultContext.resources } })}>
            {environments.map(value => <option key={value} value={value}>{t(`referenceContext.environments.${value}`)}</option>)}
          </select>
        </label>
        {resourceNames.map(resource => <label key={resource} className="block text-sm font-semibold">{t(`referenceContext.resources.${resource}`)}
          <select className={selectClass} disabled={disabled} value={context.resources[resource]} onChange={event => update({ ...context, resources: { ...context.resources, [resource]: event.target.value } })}>
            {resourceStates.map(value => <option key={value} value={value}>{t(`referenceContext.resourceStates.${value}`)}</option>)}
          </select>
        </label>)}
      </div>
      <p id={`${id}-status`} role="status" aria-label={t('referenceContext.status')} className="text-sm text-warn">CLINICALLY_PENDING · {t('referenceContext.limits')}</p>
      <CountryReferences key={context.countryCode} primary={context.countryCode} />
    </fieldset>
  );
}
