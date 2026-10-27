import { cleanup, render, screen, within } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import i18n from '../i18n';
import { ResultCard, type ResultItem } from '../components/ResultCard';
import { SourceChip } from '../components/SourceChip';
import { StatusBadge, type StatusKind } from '../components/StatusBadge';

beforeEach(async () => { await i18n.changeLanguage('es'); });
afterEach(cleanup);

const es = (key: string) => i18n.t(key, { lng: 'es' });
const card = (items: ResultItem[], extra: Partial<Parameters<typeof ResultCard>[0]> = {}) =>
  render(<ResultCard title="Resultado de prueba" items={items} {...extra} />);
const valueCell = (label: string) => screen.getByText(label).nextElementSibling as HTMLElement;

describe('StatusBadge', () => {
  it.each<[StatusKind, string]>([
    ['clinically_pending', 'status.clinicallyPending'],
    ['yellow', 'status.yellow'],
    ['blocked', 'status.blocked'],
    ['demo', 'status.demo'],
    ['pilot', 'status.pilot'],
  ])('%s shows translated text and a decorative icon', (kind, key) => {
    const { container } = render(<StatusBadge kind={kind} />);
    expect(screen.getByText(es(key))).toBeInTheDocument();
    expect(container.querySelector('svg')).toHaveAttribute('aria-hidden', 'true');
  });
});

describe('ResultCard decimal policy', () => {
  it('shows internal 0.05 as 0,05 with the unit adjacent, never 0.05', () => {
    card([{ label: 'Dosis', value: 0.05, unit: 'mg/kg' }]);
    const cell = valueCell('Dosis');
    expect(cell).toHaveTextContent('0,05 mg/kg');
    expect(cell.textContent).not.toContain('0.05');
  });

  it('shows internal 70.5 as 70,5 and keeps integers as integers', () => {
    card([{ label: 'Peso', value: 70.5, unit: 'kg' }, { label: 'Entero', value: 70, unit: 'kg' }]);
    expect(valueCell('Peso')).toHaveTextContent('70,5 kg');
    expect(valueCell('Entero')).toHaveTextContent(/^70 kg$/);
  });

  it('keeps full precision unless a field sets visual precision, without changing the value', () => {
    const items: ResultItem[] = [
      { label: 'Exacto', value: 0.30000000000000004, unit: 'mL' },
      { label: 'Visual', value: 5.25, unit: 'mL/h', format: { maxDecimals: 1, minDecimals: 1 } },
      { label: 'Pequeño', value: 0.004, unit: 'mg', format: { maxDecimals: 2 } },
    ];
    card(items);
    expect(valueCell('Exacto')).toHaveTextContent('0,30000000000000004 mL');
    expect(valueCell('Visual')).toHaveTextContent('5,3 mL/h');
    expect(valueCell('Pequeño')).toHaveTextContent('0,004 mg');
    expect(items[1]?.value).toBe(5.25);
  });

  it('marks numbers without unit and never infers one', () => {
    card([{ label: 'Dosis', value: 7, unit: null }]);
    expect(valueCell('Dosis')).toHaveTextContent(`7 (${es('result.unitNotSpecified')})`);
  });

  it('null → not specified; non-finite → invalid value with no figure', () => {
    card([{ label: 'Nulo', value: null, unit: 'mg' }, { label: 'Infinito', value: Number.POSITIVE_INFINITY, unit: 'mg' }]);
    expect(valueCell('Nulo')).toHaveTextContent(es('result.notSpecified'));
    expect(valueCell('Nulo')).not.toHaveTextContent('mg');
    expect(valueCell('Infinito')).toHaveTextContent(es('result.invalidValue'));
    expect(valueCell('Infinito').textContent).not.toMatch(/\d|∞|Infinity/);
  });

  it('never alters dots in canonical text: dates, URLs, identifiers, references', () => {
    const literal = ['2026-10-27', '27.10.2026', 'https://www.nice.org.uk/guidance/ng51', 'PROC-ENT-013', 'v1.44', 'NG254 §1.2.3', '0.05'];
    card(literal.map((value, i) => ({ label: `Texto ${i}`, value, unit: null })));
    literal.forEach((value, i) => {
      expect(valueCell(`Texto ${i}`)).toHaveTextContent(value);
      expect(valueCell(`Texto ${i}`)).not.toHaveTextContent(es('result.unitNotSpecified'));
    });
  });

  it('converts a string only when flagged as an unambiguous decimal', () => {
    card([
      { label: 'Cadena numérica', value: '0.05', unit: 'mg/kg', numericString: true },
      { label: 'Ambigua', value: '1.000,5', unit: 'mg', numericString: true },
      { label: 'Con texto', value: '5 mg', unit: null, numericString: true },
    ]);
    expect(valueCell('Cadena numérica')).toHaveTextContent('0,05 mg/kg');
    expect(valueCell('Ambigua')).toHaveTextContent('1.000,5 mg');
    expect(valueCell('Con texto')).toHaveTextContent(/^5 mg$/);
  });
});

describe('ResultCard status, formula and accessibility', () => {
  it('defaults to CLINICALLY_PENDING and exposes a labelled region', () => {
    card([{ label: 'Dosis', value: 7, unit: 'mg' }]);
    const region = screen.getByRole('region', { name: 'Resultado de prueba' });
    expect(within(region).getByText(es('status.clinicallyPending'))).toBeInTheDocument();
    expect(region.querySelector('[aria-live="polite"]')).not.toBeNull();
  });

  it('renders the formula literally inside a collapsible block, only when provided', () => {
    const formula = 'mL/h = dose (mcg/kg/min) × weight (kg) × 60 ÷ concentration (mcg/mL)';
    const { rerender } = card([{ label: 'Dosis', value: 7, unit: 'mg' }]);
    expect(document.querySelector('details')).toBeNull();
    rerender(<ResultCard title="Resultado de prueba" items={[{ label: 'Dosis', value: 7, unit: 'mg' }]} formula={formula} />);
    expect(screen.getByText(es('result.formula'))).toBeInTheDocument();
    expect(screen.getByText(formula)).toBeInTheDocument();
  });

  it('shows the evidence badge and sources when supplied', () => {
    card([{ label: 'Dosis', value: 7, unit: 'mg' }], { evidence: 'yellow', sources: [{ label: 'Fuente canónica', date: '2026-09-14' }] });
    expect(screen.getByText(es('result.sources'))).toBeInTheDocument();
    expect(screen.getByText('Fuente canónica')).toBeInTheDocument();
  });
});

describe('SourceChip', () => {
  it('shows label and date literally, with a no-date fallback', () => {
    const { rerender } = render(<SourceChip label="NICE NG51" date="27.10.2026" />);
    expect(screen.getByText('· 27.10.2026', { exact: false })).toBeInTheDocument();
    rerender(<SourceChip label="NICE NG51" date={null} />);
    expect(screen.getByText(es('result.noDate'), { exact: false })).toBeInTheDocument();
  });

  it('links only web URLs, in a new tab with an accessible notice', () => {
    const { rerender } = render(<SourceChip label="Guía" href="https://example.org/a.b" />);
    const link = screen.getByRole('link');
    expect(link).toHaveAttribute('href', 'https://example.org/a.b');
    expect(link).toHaveAttribute('rel', 'noreferrer noopener');
    expect(link).toHaveTextContent(es('result.opensNewTab'));
    rerender(<SourceChip label="Guía" href="javascript:alert(1)" />);
    expect(screen.queryByRole('link')).toBeNull();
  });
});

describe('i18n of new keys', () => {
  it.each(['es', 'en', 'pt', 'zh'])('%s renders without raw keys', async (lng) => {
    await i18n.changeLanguage(lng);
    const { container } = render(
      <ResultCard title="T" items={[{ label: 'A', value: null, unit: null }, { label: 'B', value: 1, unit: null }]} formula="f" sources={[{ label: 'S' }]} />,
    );
    expect(container.textContent).not.toMatch(/\b(status|result)\.[a-zA-Z]+/);
  });
});
