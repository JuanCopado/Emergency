import { useCallback } from 'react';
import { useTranslation } from 'react-i18next';

/** Static interface copy only. Never sends case data to a translation service. */
export function useClinicalUi() {
  const { t } = useTranslation('clinicalUi');
  return useCallback((source: string, values?: Record<string, string | number>) =>
    t(source, { ...values, keySeparator: false, nsSeparator: false, defaultValue: source }), [t]);
}
