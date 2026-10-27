import { useTranslation } from 'react-i18next';
import type { SafetyAlert } from '../lib/clinicalOutcome';
import { Icon } from './Icon';

// Same rule as S0 classifyPediatric: only these exact severities are non-STOP. Anything
// else — STOP, empty, unknown or differently cased — is handled as STOP (conservative).
const NON_STOP_SEVERITIES = new Set(['ALERT', 'CAUTION', 'INFO']);
const isStop = (alert: SafetyAlert) => !NON_STOP_SEVERITIES.has(alert.severity.trim());

function AlertItems({ alerts, stop }: { alerts: SafetyAlert[]; stop: boolean }) {
  const { t } = useTranslation();
  return (
    <ul className="space-y-2">
      {alerts.map((alert, index) => (
        // Index first: duplicated codes must all remain visible.
        <li
          key={`${index}-${alert.code ?? ''}`}
          className={`rounded-xl border p-3 ${stop ? 'border-danger text-danger' : 'border-warn bg-warn-bg text-warn'}`}
        >
          <p>
            {/* The received severity is shown as is; an empty one is labelled STOP. */}
            <strong>{alert.severity.trim() || 'STOP'}: </strong>
            <span className="text-fg">{alert.message}</span>
          </p>
          {alert.action && <p className="mt-1 text-fg">{alert.action}</p>}
          {alert.code && <p className="mt-1 text-xs text-muted">{t('stop.code')}: {alert.code}</p>}
        </li>
      ))}
    </ul>
  );
}

/**
 * Every alert received, STOP first (stable order within each group). STOP alerts are
 * announced assertively (role="alert"); other alerts politely (role="status"). There is
 * no way to dismiss them: they disappear only when the caller stops rendering them.
 * Messages, actions and codes are shown literally.
 */
export function StopAlert({ alerts }: { alerts: SafetyAlert[] }) {
  const { t } = useTranslation();
  if (alerts.length === 0) return null;
  const stops = alerts.filter(isStop);
  const notices = alerts.filter((alert) => !isStop(alert));
  return (
    <div className="space-y-3">
      {stops.length > 0 && (
        <div role="alert" aria-live="assertive" tabIndex={-1} className="space-y-2 rounded-2xl border-2 border-danger p-3 sm:p-4" data-testid="stop-alert">
          <p className="flex items-center gap-2 font-bold text-danger">
            <Icon name="alert" size={20} />
            {t('stop.title')}
          </p>
          <AlertItems alerts={stops} stop />
        </div>
      )}
      {notices.length > 0 && (
        <div role="status" aria-live="polite" className="flex gap-2 rounded-2xl border border-warn p-3 sm:p-4" data-testid="alert-notices">
          <Icon name="info" size={20} className="mt-3 shrink-0 text-warn" />
          <div className="min-w-0 flex-1">
            <AlertItems alerts={notices} stop={false} />
          </div>
        </div>
      )}
    </div>
  );
}
