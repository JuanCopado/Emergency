import { useTranslation } from 'react-i18next';
import { useSettings } from '../state/settings';
import { Icon } from './Icon';

export function ThemeToggle() {
  const { t } = useTranslation();
  const { resolvedTheme, setTheme } = useSettings();
  const next = resolvedTheme === 'dark' ? 'light' : 'dark';
  return (
    <button
      type="button"
      onClick={() => setTheme(next)}
      className="inline-flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-border bg-surface text-fg hover:bg-surface-2"
      aria-label={t(next === 'dark' ? 'theme.switchToDark' : 'theme.switchToLight')}
      title={t(next === 'dark' ? 'theme.switchToDark' : 'theme.switchToLight')}
    >
      <Icon name={resolvedTheme === 'dark' ? 'sun' : 'moon'} size={18} />
    </button>
  );
}
