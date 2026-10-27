/**
 * S0 — classification of clinical API responses for the interface.
 *
 * The only path to SUCCESS is through these pure functions. Precedence is
 * BLOCKED > STOP > ERROR > SUCCESS. BLOCKED and STOP variants carry no result, so a
 * component cannot render figures from them. Nothing here computes, rounds or
 * changes clinical values, and no backend contract is modified.
 */

export type FormState = 'INITIAL' | 'EDITING' | 'LOADING' | 'SUCCESS' | 'BLOCKED' | 'STOP' | 'ERROR' | 'STALE';

export type SafetyAlert = { severity: string; message: string; code?: string; action?: string };

export type ErrorReason = 'NETWORK' | 'HTTP' | 'INVALID_RESPONSE';

export type Outcome<R> =
  | { kind: 'BLOCKED'; alerts: SafetyAlert[] }
  | { kind: 'STOP'; alerts: SafetyAlert[] }
  | { kind: 'ERROR'; reason: ErrorReason; detail: string }
  | { kind: 'SUCCESS'; result: R; alerts: SafetyAlert[] };

type Json = Record<string, unknown>;

/** Acute calculation result as returned by acute_medication_api.py (_calculate). */
export type AcuteResult = Json & { dose: number; dose_unit: string };
/** Acute success also carries the export report produced by the backend. */
export type AcuteSuccess = { result: AcuteResult; report: unknown };

/** Pediatric success as returned by pediatric_outpatient_api.py. */
export type PediatricSuccess = { result: Json; exportReport: unknown; prescriptionStatus: unknown };

const isObject = (value: unknown): value is Json => typeof value === 'object' && value !== null && !Array.isArray(value);

export function errorOutcome<R>(reason: ErrorReason, detail: string): Outcome<R> {
  return { kind: 'ERROR', reason, detail };
}

function invalid<R>(detail: string): Outcome<R> {
  return errorOutcome<R>('INVALID_RESPONSE', detail);
}

/** Parses an alert list; null means the list is malformed. */
function readAlerts(raw: unknown, defaultSeverity: string | null): SafetyAlert[] | null {
  if (raw === undefined) return [];
  if (!Array.isArray(raw)) return null;
  const alerts: SafetyAlert[] = [];
  for (const item of raw) {
    if (!isObject(item) || typeof item.message !== 'string') return null;
    const severity = typeof item.severity === 'string' && item.severity.trim() ? item.severity : defaultSeverity ?? '';
    alerts.push({
      severity,
      message: item.message,
      ...(typeof item.code === 'string' ? { code: item.code } : {}),
      ...(typeof item.action === 'string' ? { action: item.action } : {}),
    });
  }
  return alerts;
}

/** Every number anywhere in the value must be finite (JSON cannot carry NaN/Infinity). */
function allFinite(value: unknown): boolean {
  if (typeof value === 'number') return Number.isFinite(value);
  if (Array.isArray(value)) return value.every(allFinite);
  if (isObject(value)) return Object.values(value).every(allFinite);
  return true;
}

/** Quantities that cannot be negative; null/absent is allowed where the backend omits them. */
function nonNegative(result: Json, keys: readonly string[]): boolean {
  return keys.every((key) => {
    const value = result[key];
    return value === undefined || value === null || (typeof value === 'number' && value >= 0);
  });
}

// Fields emitted by acute_medication_api.py:_calculate.
const ACUTE_QUANTITIES = ['dose', 'withdrawal_ml', 'administration_volume_ml', 'pump_ml_h', 'duration_min', 'amount_per_hour'] as const;

/**
 * Acute pharmacology. Every alert is a STOP: the backend only emits STOP alerts
 * (acute_medication_api.py:_alert), so a missing severity is treated as STOP.
 */
export function classifyAcute(raw: unknown): Outcome<AcuteSuccess> {
  if (!isObject(raw)) return invalid('response is not an object');
  const alerts = readAlerts(raw.alerts, 'STOP');
  if (raw.blocked === true) return { kind: 'BLOCKED', alerts: alerts ?? [] };
  if (alerts === null) return invalid('alerts are malformed');
  if (alerts.length > 0) return { kind: 'STOP', alerts };
  if (raw.blocked !== false) return invalid('blocked flag is missing or not boolean');
  const result = raw.result;
  if (!isObject(result)) return invalid('result is missing');
  if (!allFinite(result)) return invalid('result contains a non-finite number');
  if (typeof result.dose !== 'number') return invalid('dose is not a number');
  if (typeof result.dose_unit !== 'string' || !result.dose_unit.trim()) return invalid('dose unit is missing');
  if (!nonNegative(result, ACUTE_QUANTITIES)) return invalid('a quantity is negative');
  return { kind: 'SUCCESS', result: { result: result as AcuteResult, report: raw.report }, alerts: [] };
}

const NON_STOP_SEVERITIES = new Set(['ALERT', 'CAUTION', 'INFO']);

// Quantity keys emitted by pediatric_outpatient_calculator.py, checked at any depth.
const PEDIATRIC_QUANTITIES = new Set(['dose_mg', 'dose_mg_per_kg', 'dosing_weight_kg', 'exact_ml', 'rounded_0_1_ml', 'estimated_total_course_ml']);

function noNegativeQuantity(value: unknown): boolean {
  if (Array.isArray(value)) return value.every(noNegativeQuantity);
  if (!isObject(value)) return true;
  return Object.entries(value).every(([key, item]) =>
    PEDIATRIC_QUANTITIES.has(key) && typeof item === 'number' ? item >= 0 : noNegativeQuantity(item));
}

/**
 * Pediatric outpatient. Any alert whose severity is not ALERT, CAUTION or INFO —
 * including STOP and unknown or missing severities — is treated as STOP (fail closed).
 */
export function classifyPediatric(raw: unknown): Outcome<PediatricSuccess> {
  if (!isObject(raw)) return invalid('response is not an object');
  const safety = isObject(raw.safety) ? raw.safety : undefined;
  const alerts = readAlerts(safety?.alerts, null);
  if (raw.blocked === true) return { kind: 'BLOCKED', alerts: alerts ?? [] };
  if (alerts === null) return invalid('alerts are malformed');
  const stops = alerts.filter((alert) => !NON_STOP_SEVERITIES.has(alert.severity));
  if (stops.length > 0) return { kind: 'STOP', alerts };
  if (raw.blocked !== false) return invalid('blocked flag is missing or not boolean');
  if (!safety) return invalid('safety section is missing');
  const result = raw.result;
  if (!isObject(result)) return invalid('result is missing');
  if (!allFinite(result)) return invalid('result contains a non-finite number');
  if (!noNegativeQuantity(result)) return invalid('a quantity is negative');
  return {
    kind: 'SUCCESS',
    result: { result, exportReport: raw.export_report, prescriptionStatus: safety.prescription_status },
    alerts,
  };
}

export type RequestGuard = { next(): number; isCurrent(id: number): boolean; invalidate(): void };

/** Only the latest request may update the screen; any edit invalidates pending ones. */
export function createRequestGuard(): RequestGuard {
  let current = 0;
  return {
    next: () => ++current,
    isCurrent: (id) => id === current,
    invalidate: () => { current += 1; },
  };
}
