import { useTranslation } from 'react-i18next';
import localizedCopy from './textWorkspace.locales.json';

type Copy = typeof localizedCopy.es;
export const TEXT_WORKSPACE_COPY: Record<'es' | 'en' | 'pt' | 'zh', Copy> = localizedCopy;
export function useTextWorkspaceCopy(): Copy {
  const { i18n } = useTranslation();
  return TEXT_WORKSPACE_COPY[i18n.resolvedLanguage as keyof typeof TEXT_WORKSPACE_COPY] ?? TEXT_WORKSPACE_COPY.en;
}
