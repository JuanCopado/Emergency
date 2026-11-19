/** Owner-approved domain for an explicitly entered patient weight, in kg. */
export const MIN_PATIENT_WEIGHT_KG = 1;
export const MAX_PATIENT_WEIGHT_KG = 180;

export function isPatientWeight(value: unknown): value is number {
  return typeof value === 'number' && Number.isFinite(value)
    && value >= MIN_PATIENT_WEIGHT_KG && value <= MAX_PATIENT_WEIGHT_KG;
}

/** Compare the decimal literal before Number can round an out-of-range value. */
export function parsePatientWeight(input: string): number | null {
  const text = input.trim();
  const match = /^([+-]?)(?:(\d+)(?:\.(\d*))?|\.(\d+))(?:e([+-]?\d+))?$/i.exec(text);
  if (!match || match[1] === '-') return null;
  const fraction = match[3] ?? match[4] ?? '';
  const digits = ((match[2] ?? '') + fraction).replace(/^0+/, '');
  if (!digits) return null;
  const exponent = Number(match[5] ?? 0);
  if (!Number.isSafeInteger(exponent)) return null;
  const integerDigits = digits.length + exponent - fraction.length;
  if (integerDigits < 1 || integerDigits > 3) return null;
  if (integerDigits === 3) {
    const whole = digits.slice(0, 3).padEnd(3, '0');
    if (whole > '180' || (whole === '180' && /[1-9]/.test(digits.slice(3)))) return null;
  }
  const value = Number(text);
  return isPatientWeight(value) ? value : null;
}
