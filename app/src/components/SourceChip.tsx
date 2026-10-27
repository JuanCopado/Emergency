import { useTranslation } from 'react-i18next';
import { Icon } from './Icon';

export type SourceRef = { label: string; date?: string | null; href?: string | null };

// Only web links are rendered as links; anything else (e.g. javascript:) stays plain text.
const isWebLink = (href: string) => /^https?:\/\//i.test(href);

/**
 * A source exactly as supplied by the caller: label and date are shown literally
 * (no date or punctuation conversion). It never looks sources up by itself.
 */
export function SourceChip({ label, date, href }: SourceRef) {
  const { t } = useTranslation();
  const when = date?.trim() ? date : t('result.noDate');
  const content = (
    <>
      <span className="font-semibold">{label}</span>
      <span className="text-muted"> · {when}</span>
    </>
  );
  return (
    <span className="inline-flex max-w-full flex-wrap items-center gap-1 rounded-lg border border-border bg-surface-2 px-2 py-1 text-xs break-words">
      {href && isWebLink(href) ? (
        <a href={href} target="_blank" rel="noreferrer noopener" className="underline underline-offset-2">
          {content}
          <span className="sr-only"> {t('result.opensNewTab')}</span>
          <Icon name="external" size={12} className="ml-1 inline" />
        </a>
      ) : (
        content
      )}
    </span>
  );
}
