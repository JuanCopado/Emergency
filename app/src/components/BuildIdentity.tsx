import { useTranslation } from 'react-i18next';

export function BuildIdentity() {
  const { t } = useTranslation();
  const revision = import.meta.env.VITE_BUILD_REVISION as string|undefined;
  const dirty = import.meta.env.VITE_BUILD_DIRTY === 'true';
  return <span data-testid="build-identity">
    {t('buildIdentity.label')}: {revision ? <code title={revision}>{revision.slice(0,12)}</code> : t('buildIdentity.unknown')}
    {dirty && <> · {t('buildIdentity.localChanges')}</>}
  </span>;
}
