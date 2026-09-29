import { useTranslation } from 'react-i18next';
import { LANGUAGES, isLang } from '../i18n';
import { useSettings } from '../state/settings';
import { Icon } from './Icon';

export function LanguageSwitcher({ compact = false }: { compact?: boolean }) {
  const { t } = useTranslation();
  const { lang, setLang } = useSettings();
  return (
    <label className="relative inline-flex items-center">
      <span className="sr-only">{t('settings.language')}</span>
      <Icon name="globe" size={18} className="pointer-events-none absolute left-2.5 text-muted" />
      <select
        value={lang}
        onChange={(e) => isLang(e.target.value) && setLang(e.target.value)}
        className="min-h-[40px] appearance-none rounded-xl border border-border bg-surface py-2 pl-8 pr-3 text-sm font-medium text-fg hover:bg-surface-2 focus:outline-none focus:ring-2 focus:ring-primary/40"
        data-testid="language-switcher"
      >
        {LANGUAGES.map((l) => (
          <option key={l.code} value={l.code} lang={l.htmlLang}>
            {compact ? l.code.toUpperCase() : l.label}
          </option>
        ))}
      </select>
    </label>
  );
}
