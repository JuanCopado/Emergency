import { useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { intlLocale } from '../i18n';
import { useSettings } from '../state/settings';
import { formatNumber, formatRate, unitLabel } from './format';

export function useFormat() {
  const { i18n } = useTranslation();
  const { micro } = useSettings();
  const locale = intlLocale(i18n.language);
  const num = useCallback((v: number, maxDecimals = 3) => formatNumber(v, locale, maxDecimals), [locale]);
  const rate = useCallback((v: number) => formatRate(v, locale), [locale]);
  const unit = useCallback((u: string) => unitLabel(u, micro), [micro]);
  const range = useCallback(
    (min: number | null, max: number | null) => {
      if (min !== null && max !== null) return min === max ? num(min) : `${num(min)}–${num(max)}`;
      if (min !== null) return num(min);
      if (max !== null) return `≤ ${num(max)}`;
      return '—';
    },
    [num],
  );
  return { locale, num, rate, unit, range };
}
