import { useClinicalUi } from '../i18n/useClinicalUi';
import { useId, type ReactNode } from 'react';

interface Props {
  label: string;
  value: string;
  onChange: (v: string) => void;
  suffix?: ReactNode;
  hint?: ReactNode;
  error?: string | null;
  id?: string;
  testId?: string;
  placeholder?: string;
  large?: boolean;
}

export function NumberField({ label, value, onChange, suffix, hint, error, id, testId, placeholder, large }: Props) {
  const ui = useClinicalUi();
  hint = hint ?? ui("Entrada numérica: usa punto decimal (0.1), sin separadores de miles. La salida sigue el idioma seleccionado.");
  const autoId = useId();
  const inputId = id ?? autoId;
  const hintId = `${inputId}-hint`;
  const errId = `${inputId}-err`;
  const describedBy = [hint ? hintId : null, error ? errId : null].filter(Boolean).join(' ') || undefined;
  return (
    <div>
      <label htmlFor={inputId} className="label">
        {label}
      </label>
      <div className="flex items-stretch">
        <input
          id={inputId}
          type="text"
          inputMode="decimal"
          lang="en"
          autoComplete="off"
          spellCheck={false}
          value={value}
          placeholder={placeholder}
          onChange={(e) => onChange(e.target.value)}
          aria-invalid={error ? true : undefined}
          aria-describedby={describedBy}
          data-testid={testId}
          className={`input num ${suffix ? 'rounded-r-none' : ''} ${large ? 'text-lg font-semibold' : ''} ${error ? 'border-danger focus:border-danger focus:ring-danger/30' : ''}`}
        />
        {suffix && (
          <span className="inline-flex shrink-0 items-center rounded-r-xl border border-l-0 border-border bg-surface-2 px-3 text-sm font-semibold text-muted">
            {suffix}
          </span>
        )}
      </div>
      {hint && !error && (
        <p id={hintId} className="mt-1 text-xs text-muted">
          {hint}
        </p>
      )}
      {error && (
        <p id={errId} role="alert" className="mt-1 text-xs font-semibold text-danger">
          {error}
        </p>
      )}
    </div>
  );
}
