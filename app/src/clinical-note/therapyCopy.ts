import { useTranslation } from 'react-i18next';
import localizedCopy from './therapyCopy.locales.json';

type Copy = typeof localizedCopy.es;
export const THERAPY_COPY: Record<'es'|'en'|'pt'|'zh', Copy> = localizedCopy;
export function useTherapyCopy(): Copy {
  const { i18n } = useTranslation();
  return THERAPY_COPY[i18n.resolvedLanguage as keyof typeof THERAPY_COPY] ?? THERAPY_COPY.en;
}
