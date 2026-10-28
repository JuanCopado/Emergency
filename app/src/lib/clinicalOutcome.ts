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
/**
 * Report as built by acute_medication_api.py (calculate_request) and
 * pediatric_result_exporter.py (build_report): {snapshot, sections: [heading, lines[]][]}.
 */
export type ClinicalReport = { snapshot: Json; sections: [string, string[]][] };
/** Acute success also carries the export report produced by the backend (always sent on success). */
export type AcuteSuccess = { result: AcuteResult; report: ClinicalReport };

/**
 * Pediatric success as returned by pediatric_outpatient_api.py. exportReport is null when the
 * response carries none: callers must not offer export or print without it.
 */
export type PediatricSuccess = { result: Json; exportReport: ClinicalReport | null; prescriptionStatus: string };

const isObject = (value: unknown): value is Json => typeof value === 'object' && value !== null && !Array.isArray(value);

export function errorOutcome<R>(reason: ErrorReason, detail: string): Outcome<R> {
  return { kind: 'ERROR', reason, detail };
}

function invalid<R>(detail: string): Outcome<R> {
  return errorOutcome<R>('INVALID_RESPONSE', detail);
}

const optionalString = (value: unknown) => value === undefined || value === null || typeof value === 'string';

/**
 * S0-R (R1): parses an alert list. 'missing' (field absent) and 'malformed' are distinct from
 * an empty list; neither can lead to SUCCESS. An alert needs a non-empty string message;
 * severity, code and action, when present, must be strings.
 */
function readAlerts(raw: unknown, defaultSeverity: string | null): SafetyAlert[] | 'missing' | 'malformed' {
  if (raw === undefined) return 'missing';
  if (!Array.isArray(raw)) return 'malformed';
  const alerts: SafetyAlert[] = [];
  for (const item of raw) {
    if (!isObject(item) || typeof item.message !== 'string' || !item.message.trim()) return 'malformed';
    if (!optionalString(item.severity) || !optionalString(item.code) || !optionalString(item.action)) return 'malformed';
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

/** S0-R (R2): {snapshot: object, sections: [string, string[]][]} exactly as the backends build it. */
function isClinicalReport(value: unknown): value is ClinicalReport {
  return isObject(value) && isObject(value.snapshot) && Array.isArray(value.sections) &&
    value.sections.every((section) => Array.isArray(section) && section.length === 2 && typeof section[0] === 'string' &&
      Array.isArray(section[1]) && section[1].every((line) => typeof line === 'string'));
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
  if (raw.blocked === true) return { kind: 'BLOCKED', alerts: Array.isArray(alerts) ? alerts : [] };
  // The acute backend always sends `alerts` (both branches of calculate_request).
  if (alerts === 'missing') return invalid('alerts are missing');
  if (alerts === 'malformed') return invalid('alerts are malformed');
  if (alerts.length > 0) return { kind: 'STOP', alerts };
  if (raw.blocked !== false) return invalid('blocked flag is missing or not boolean');
  const result = raw.result;
  if (!isObject(result)) return invalid('result is missing');
  if (!allFinite(result)) return invalid('result contains a non-finite number');
  if (typeof result.dose !== 'number') return invalid('dose is not a number');
  if (typeof result.dose_unit !== 'string' || !result.dose_unit.trim()) return invalid('dose unit is missing');
  if (!nonNegative(result, ACUTE_QUANTITIES)) return invalid('a quantity is negative or not a number');
  if (!isClinicalReport(raw.report)) return invalid('report is missing or malformed');
  return { kind: 'SUCCESS', result: { result: result as AcuteResult, report: raw.report }, alerts: [] };
}

const NON_STOP_SEVERITIES = new Set(['ALERT', 'CAUTION', 'INFO']);

// Quantity keys emitted by pediatric_outpatient_calculator.py (and its catalog bands), checked at any depth.
const PEDIATRIC_QUANTITIES = new Set(['dose_mg', 'dose_mg_per_kg', 'dosing_weight_kg', 'exact_ml', 'rounded_0_1_ml',
  'estimated_total_course_ml', 'estimated_phase_ml', 'concentration_mg_per_ml', 'mg_per_ml', 'total_doses',
  'total_phase_doses', 'doses_per_day', 'sachets_per_day']);

/** Finite non-negative number, or null where the backend omits the value. Strings are never converted. */
const quantityOrNull = (value: unknown) => value === null || (typeof value === 'number' && Number.isFinite(value) && value >= 0);
const finiteOrNull = (value: unknown) => value === null || (typeof value === 'number' && Number.isFinite(value));

// _drops() in pediatric_outpatient_calculator.py: counts and factors are non-negative; the rounding
// error is a signed percentage. Text fields (factor_source, product name, URL, warning) are not quantities.
const DROP_QUANTITIES = ['exact_drops', 'rounded_whole_drops', 'mg_per_drop', 'drops_per_ml', 'delivered_mg_at_rounded_drops'] as const;
function dropConversionValid(value: Json): boolean {
  // S0-R3: _drops() always returns exact_drops (number) and rounded_whole_drops (whole number); an object
  // without them (e.g. {}) is not a conversion and must not be shown as one.
  const exact = value.exact_drops;
  const rounded = value.rounded_whole_drops;
  return typeof exact === 'number' && typeof rounded === 'number' && Number.isInteger(rounded) &&
    DROP_QUANTITIES.every((key) => value[key] === undefined || quantityOrNull(value[key])) &&
    (value.rounding_error_percent === undefined || finiteOrNull(value.rounding_error_percent));
}

/** [min, max] of two finite non-negative numbers (catalog ranges), or null. */
const rangeOrNull = (value: unknown) => value === null ||
  (Array.isArray(value) && value.length === 2 && value.every((item) => typeof item === 'number' && Number.isFinite(item) && item >= 0));

/**
 * S0-R2 (Q01–Q06): field-specific shapes taken from pediatric_outpatient_calculator.py and its catalog,
 * applied wherever the key appears (result, matched_band, schedule phases):
 * - duration_days: number, null or a [min, max] range of numbers (catalog bands);
 * - total_rehydration_ml, target_ml_per_hour (volume_ml_per_kg_course model) and
 *   volume_per_administration_ml (topical): number or null;
 * - drops_per_dose: number (topical catalog) or the _drops() conversion object.
 * S0-R3 (residual quantities, shapes verified in the catalog and 530 real responses):
 * - administration_hours (volume_ml_per_kg_course), dose_ml (fixed_volume_band), applications_per_day and
 *   repeat_after_days (topical pass-through; absent from the current catalog): number or null;
 * - dose_ml_range (fixed_volume_band) and doses_per_day_range (topical): [min, max] or null.
 * Every number must be finite and non-negative (except the signed rounding error).
 */
const FIELD_RULES: Readonly<Record<string, (value: unknown) => boolean>> = Object.freeze({
  duration_days: (value: unknown) => quantityOrNull(value) || rangeOrNull(value),
  total_rehydration_ml: quantityOrNull,
  target_ml_per_hour: quantityOrNull,
  volume_per_administration_ml: quantityOrNull,
  drops_per_dose: (value: unknown) => quantityOrNull(value) || (isObject(value) && dropConversionValid(value)),
  administration_hours: quantityOrNull,
  dose_ml: quantityOrNull,
  applications_per_day: quantityOrNull,
  repeat_after_days: quantityOrNull,
  dose_ml_range: rangeOrNull,
  doses_per_day_range: rangeOrNull,
});

/**
 * S0-R (R2): a quantity key may carry a non-negative number, null (backend omits it) or a
 * structure (catalog ranges such as duration_days [min, max]); a string or boolean is a
 * serialization error and a negative number is invalid.
 */
function quantitiesValid(value: unknown): boolean {
  if (Array.isArray(value)) return value.every(quantitiesValid);
  if (!isObject(value)) return true;
  return Object.entries(value).every(([key, item]) => {
    if (Object.hasOwn(FIELD_RULES, key)) return FIELD_RULES[key]!(item);
    // PEDIATRIC-SAFETY-01 (NEW-05 delta): a quantity key is a finite non-negative number or null, the only
    // shapes in 530 real backend responses; an object or array (e.g. dose_mg: {} or [5]) is not a quantity.
    if (PEDIATRIC_QUANTITIES.has(key)) return quantityOrNull(item);
    return quantitiesValid(item);
  });
}

/**
 * S0-R2 (phase 2) — proposed pediatric contract policy, PREPARED BUT NOT ACTIVE.
 * A: result.regimen_id and result.drug non-empty strings and result.status exactly "calculated".
 * B: export_report mandatory and structurally valid on SUCCESS of the current endpoint.
 * dose_mg is never required (topical, device, sachet and volume-per-kg models have no mg dose).
 * Activation requires explicit owner authorization; until then the default leaves both off.
 */
export type PediatricContractPolicy = { readonly requireIdentity: boolean; readonly requireExportReport: boolean };
export const PEDIATRIC_CONTRACT_POLICY_CURRENT: PediatricContractPolicy = Object.freeze({ requireIdentity: false, requireExportReport: false });
export const PEDIATRIC_CONTRACT_POLICY_PROPOSED_AB: PediatricContractPolicy = Object.freeze({ requireIdentity: true, requireExportReport: true });
const nonEmptyString = (value: unknown) => typeof value === 'string' && value.trim() !== '';

/**
 * Pediatric outpatient. Any alert whose severity is not ALERT, CAUTION or INFO —
 * including STOP and unknown or missing severities — is treated as STOP (fail closed).
 */
export function classifyPediatric(raw: unknown, policy: PediatricContractPolicy = PEDIATRIC_CONTRACT_POLICY_CURRENT): Outcome<PediatricSuccess> {
  if (!isObject(raw)) return invalid('response is not an object');
  const safety = isObject(raw.safety) ? raw.safety : undefined;
  const alerts = safety ? readAlerts(safety.alerts, null) : 'missing';
  if (raw.blocked === true) return { kind: 'BLOCKED', alerts: Array.isArray(alerts) ? alerts : [] };
  // The pediatric backend always sends safety.alerts (alert engine evaluate()); absent ≠ empty.
  if (raw.safety !== undefined && !safety) return invalid('safety section is malformed');
  if (alerts === 'missing') return invalid(safety ? 'alerts are missing' : 'safety section is missing');
  if (alerts === 'malformed') return invalid('alerts are malformed');
  const stops = alerts.filter((alert) => !NON_STOP_SEVERITIES.has(alert.severity));
  if (stops.length > 0) return { kind: 'STOP', alerts };
  if (raw.blocked !== false) return invalid('blocked flag is missing or not boolean');
  if (typeof safety!.prescription_status !== 'string' || !safety!.prescription_status.trim()) return invalid('prescription status is missing');
  const result = raw.result;
  if (!isObject(result)) return invalid('result is missing');
  if (Object.keys(result).length === 0) return invalid('result is empty');
  if (policy.requireIdentity) {
    if (!nonEmptyString(result.regimen_id)) return invalid('regimen id is missing');
    if (!nonEmptyString(result.drug)) return invalid('drug is missing');
    if (result.status !== 'calculated') return invalid('result status is not "calculated"');
  }
  if (result.regimen_id !== undefined && typeof result.regimen_id !== 'string') return invalid('regimen id is malformed');
  if (result.status !== undefined && result.status !== 'calculated') return invalid('result status is not "calculated"');
  if (!allFinite(result)) return invalid('result contains a non-finite number');
  if (!quantitiesValid(result)) return invalid('a quantity is negative or not a number');
  // export_report is validated before any render or action; absent → no export/print (null).
  if (policy.requireExportReport && raw.export_report === undefined) return invalid('export report is missing');
  if (raw.export_report !== undefined && !isClinicalReport(raw.export_report)) return invalid('export report is malformed');
  return {
    kind: 'SUCCESS',
    result: { result, exportReport: raw.export_report === undefined ? null : raw.export_report, prescriptionStatus: safety!.prescription_status },
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
