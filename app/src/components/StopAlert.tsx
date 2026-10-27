import { useTranslation } from 'react-i18next';
import type { SafetyAlert } from '../lib/clinicalOutcome';
import { Icon } from './Icon';

const isStop = (alert: SafetyAlert) => alert.severity.trim().toUpperCase() === 'STOP' || !alert.severity.trim();

/**
 * Every alert received, STOP first (stable order within each group). There is no way
 * to dismiss it: it disappears only when the caller stops rendering it (new inputs).
 * Messages, actions and codes are shown literally.
 */
export function StopAlert({ alerts }: { alerts: SafetyAlert[] }) {
  const { t } = useTranslation();
  if (alerts.length === 0) return null;
  const ordered = [...alerts.filter(isStop), ...alerts.filter((alert) => !isStop(alert))];
  return (
    <div role="alert" aria-live="assertive" tabIndex={-1} className="space-y-2 rounded-2xl border-2 border-danger p-3 sm:p-4" data-testid="stop-alert">
      <p className="flex items-center gap-2 font-bold text-danger">
        <Icon name="alert" size={20} />
        {t('stop.title')}
      </p>
      <ul className="space-y-2">
        {ordered.map((alert, index) => {
          const stop = isStop(alert);
          return (
            // Index first: duplicated codes must all remain visible.
            <li
              key={`${index}-${alert.code ?? ''}`}
              className={`rounded-xl border p-3 ${stop ? 'border-danger text-danger' : 'border-warn bg-warn-bg text-warn'}`}
            >
              <p>
                <strong>{stop ? 'STOP' : alert.severity.trim().toUpperCase()}: </strong>
                <span className="text-fg">{alert.message}</span>
              </p>
              {alert.action && <p className="mt-1 text-fg">{alert.action}</p>}
              {alert.code && <p className="mt-1 text-xs text-muted">{t('stop.code')}: {alert.code}</p>}
            </li>
          );
        })}
      </ul>
    </div>
  );
}
