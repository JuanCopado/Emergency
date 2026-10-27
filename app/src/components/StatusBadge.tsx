import { useTranslation } from 'react-i18next';
import { Icon, type IconName } from './Icon';

export type StatusKind = 'clinically_pending' | 'yellow' | 'blocked' | 'demo' | 'pilot';

const STYLE: Record<StatusKind, { icon: IconName; key: string; className: string }> = {
  clinically_pending: { icon: 'info', key: 'status.clinicallyPending', className: 'border-warn/50 bg-warn-bg text-warn' },
  yellow: { icon: 'alert', key: 'status.yellow', className: 'border-warn/50 bg-warn-bg text-warn' },
  blocked: { icon: 'lock', key: 'status.blocked', className: 'border-danger/40 text-danger' },
  demo: { icon: 'flask', key: 'status.demo', className: 'border-border bg-surface-2 text-fg' },
  pilot: { icon: 'book', key: 'status.pilot', className: 'border-border bg-surface-2 text-fg' },
};

/** Status shown with icon and text, never by colour alone. Evidence green/red use EvidenceBadge. */
export function StatusBadge({ kind }: { kind: StatusKind }) {
  const { t } = useTranslation();
  const style = STYLE[kind];
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-semibold ${style.className}`}
      data-status={kind}
    >
      <Icon name={style.icon} size={14} />
      {t(style.key)}
    </span>
  );
}
