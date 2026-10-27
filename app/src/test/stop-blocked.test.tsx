import { cleanup, fireEvent, render, screen, within } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import i18n from '../i18n';
import { BlockedContractCard } from '../components/BlockedContractCard';
import { StopAlert } from '../components/StopAlert';

beforeEach(async () => { await i18n.changeLanguage('es'); });
afterEach(cleanup);
const es = (key: string) => i18n.t(key, { lng: 'es' });

// Literal copy from clinical/scripts/acute_medication_contracts.py:254 (reversal-fondaparinux).
const FONDAPARINUX = {
  label: 'Fondaparinux',
  reason: 'Sin antídoto específico aprobado en la fuente; protamina no neutraliza. Soporte/control de foco y consulta experta.',
};

describe('StopAlert', () => {
  it('renders nothing without alerts', () => {
    const { container } = render(<StopAlert alerts={[]} />);
    expect(container).toBeEmptyDOMElement();
  });

  it('is an assertive alert with text and a decorative icon, and cannot be dismissed', () => {
    render(<StopAlert alerts={[{ severity: 'STOP', code: 'review', message: 'Revisión requerida' }]} />);
    const alert = screen.getByRole('alert');
    expect(alert).toHaveAttribute('aria-live', 'assertive');
    expect(alert).toHaveTextContent(es('stop.title'));
    expect(alert).toHaveTextContent('STOP: Revisión requerida');
    expect(alert.querySelector('svg')).toHaveAttribute('aria-hidden', 'true');
    expect(within(alert).queryByRole('button')).toBeNull();
    fireEvent.keyDown(alert, { key: 'Escape' });
    fireEvent.click(alert);
    expect(screen.getByRole('alert')).toBeInTheDocument();
  });

  it('keeps every alert, including duplicated codes, STOP first and stable', () => {
    render(<StopAlert alerts={[
      { severity: 'CAUTION', message: 'Precaución A', action: 'Revisar A' },
      { severity: 'STOP', code: 'weight_kg', message: 'Primero' },
      { severity: 'STOP', code: 'weight_kg', message: 'Segundo' },
    ]} />);
    const items = screen.getAllByRole('listitem');
    expect(items.map((item) => item.textContent)).toEqual([
      expect.stringContaining('Primero'),
      expect.stringContaining('Segundo'),
      expect.stringContaining('Precaución A'),
    ]);
    expect(items[2]).toHaveTextContent('CAUTION: Precaución A');
    expect(items[2]).toHaveTextContent('Revisar A');
    expect(items[0]).toHaveTextContent(`${es('stop.code')}: weight_kg`);
  });

  it('treats a missing severity as STOP', () => {
    render(<StopAlert alerts={[{ severity: '', message: 'Sin severidad' }]} />);
    expect(screen.getByRole('listitem')).toHaveTextContent('STOP: Sin severidad');
  });
});

describe('BlockedContractCard', () => {
  it('shows BLOCKED status, literal label and reason, and the professional review notice', () => {
    render(<BlockedContractCard {...FONDAPARINUX} />);
    const card = screen.getByRole('region', { name: 'Fondaparinux' });
    expect(within(card).getByText(es('status.blocked'))).toBeInTheDocument();
    expect(within(card).getByText(FONDAPARINUX.reason)).toBeInTheDocument();
    expect(within(card).getByText(es('blocked.requiresReview'))).toBeInTheDocument();
  });

  it('renders no numeric result and no actions', () => {
    render(<BlockedContractCard {...FONDAPARINUX} />);
    const card = screen.getByTestId('blocked-contract');
    expect(card.querySelector('[data-result-value]')).toBeNull();
    expect(card.textContent).not.toMatch(/\d/);
    expect(within(card).queryByRole('button')).toBeNull();
    expect(within(card).queryByRole('checkbox')).toBeNull();
  });

  it('shows sources only when supplied', () => {
    const { rerender } = render(<BlockedContractCard {...FONDAPARINUX} />);
    expect(screen.queryByRole('list')).toBeNull();
    rerender(<BlockedContractCard {...FONDAPARINUX} sources={[{ label: 'procedures-pharmacology.md', date: null }]} />);
    expect(screen.getByText('procedures-pharmacology.md')).toBeInTheDocument();
  });

  it('does not accept dose, volume, rate, unit or children props', () => {
    // @ts-expect-error dose is not a prop of BlockedContractCard
    const withDose = <BlockedContractCard {...FONDAPARINUX} dose={7} />;
    // @ts-expect-error volume is not a prop of BlockedContractCard
    const withVolume = <BlockedContractCard {...FONDAPARINUX} volume_ml={1} />;
    // @ts-expect-error rate is not a prop of BlockedContractCard
    const withRate = <BlockedContractCard {...FONDAPARINUX} pump_ml_h={1} />;
    // @ts-expect-error children are not accepted
    const withChildren = <BlockedContractCard {...FONDAPARINUX}>7 mg</BlockedContractCard>;
    for (const element of [withDose, withVolume, withRate, withChildren]) {
      const { unmount } = render(element);
      expect(screen.getByTestId('blocked-contract').textContent).not.toMatch(/\d/);
      unmount();
    }
  });
});

describe('i18n of new keys', () => {
  it.each(['es', 'en', 'pt', 'zh'])('%s renders without raw keys', async (lng) => {
    await i18n.changeLanguage(lng);
    const { container } = render(<>
      <StopAlert alerts={[{ severity: 'STOP', code: 'c', message: 'm' }]} />
      <BlockedContractCard {...FONDAPARINUX} />
    </>);
    expect(container.textContent).not.toMatch(/\b(stop|blocked|status|result)\.[a-zA-Z]+/);
  });
});
