import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { Icon } from './Icon';

export function DraftBanner({ compact = false }: { compact?: boolean }) {
  const { t } = useTranslation();
  return (
    <div
      role="note"
      aria-label={t('draft.title')}
      className="flex gap-3 rounded-2xl border border-warn/40 bg-warn-bg p-3.5 text-warn sm:p-4"
      data-testid="draft-banner"
    >
      <Icon name="alert" size={22} className="mt-0.5 shrink-0" />
      <div className="text-sm leading-relaxed">
        <p className="font-bold">{t('draft.title')}</p>
        {!compact && <p className="mt-0.5">{t('draft.body')}</p>}
        <Link to="/about" className="mt-1 inline-block font-semibold underline underline-offset-2">
          {t('draft.more')}
        </Link>
      </div>
    </div>
  );
}
