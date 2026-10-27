/**
 * U08c — accessible pediatric STOP (closes Q02-Q6). StopAlert from U02 is reused:
 * STOP → role="alert" + aria-live="assertive"; ALERT/CAUTION/INFO → role="status" + polite.
 * Exactly one assertive announcement per stopped result; no dose when stopped.
 * Synthetic responses (shapes of pediatric-outpatient.test.tsx); no clinical values invented.
 */
import { act, cleanup, fireEvent, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import PediatricOutpatient from '../pages/PediatricOutpatient';
import { renderAt } from './render';

afterEach(() => { cleanup(); vi.restoreAllMocks(); });
const response = (value: unknown, ok = true) => ({ ok, json: async () => value }) as Response;
const paracetamol = 'paracetamol-pain-fever-home';
const result = { dose_mg: 525, volume_per_dose: { exact_ml: 21.875, rounded_0_1_ml: 21.9 }, total_doses: 8, estimated_total_course_ml: 175 };
const ok = { blocked: false, result, export_report: { snapshot: {}, sections: [] }, safety: { prescription_status: 'REVIEW_REQUIRED', alerts: [] as unknown[] } };
const stop = { severity: 'STOP', code: 'croup_discharge', message: 'Croup discharge criteria missing', action: 'Reassess' };
const withAlerts = (alerts: unknown[], blocked = false) => ({ ...ok, blocked, safety: { prescription_status: blocked ? 'BLOCKED' : 'REVIEW_REQUIRED', alerts } });

async function calculate(body: unknown) {
  const fetcher = vi.spyOn(globalThis, 'fetch').mockResolvedValue(response(body));
  await renderAt(`/pediatrics?regimen=${paracetamol}`, [{ path: '/pediatrics', element: <PediatricOutpatient /> }], 'es');
  fireEvent.click(screen.getByRole('button', { name: 'Comprobar y calcular' }));
  const region = await screen.findByRole('region', { name: 'Resultado pediátrico' });
  return { fetcher, region };
}
function expectNoDose(region: HTMLElement) {
  expect(within(region).queryByLabelText('Cálculo y pauta')).toBeNull();
  expect(region).not.toHaveTextContent('525');
  expect(region).not.toHaveTextContent('21,875');
  expect(screen.queryByRole('checkbox', { name: /Confirmo/ })).toBeNull();
  expect(screen.queryByRole('button', { name: 'Exportar JSON' })).toBeNull();
}
const politeSummary = () => document.querySelector('.sr-only[aria-live="polite"]')!;

describe('U08c known STOP', () => {
  it('STOP is announced assertively with full content and code, and no dose is rendered', async () => {
    const { region } = await calculate(withAlerts([stop], true));
    const alerts = within(region).getAllByRole('alert');
    expect(alerts).toHaveLength(1);
    expect(alerts[0]).toHaveAttribute('aria-live', 'assertive');
    expect(alerts[0]).toHaveTextContent('STOP: Croup discharge criteria missing');
    expect(alerts[0]).toHaveTextContent('Reassess');
    expect(alerts[0]).toHaveTextContent('croup_discharge');
    expect(within(region).queryByRole('status')).toBeNull();
    expectNoDose(region);
  });

  it('blocked:false with STOP: still stopped, no dose, assertive STOP', async () => {
    const { region } = await calculate(withAlerts([stop]));
    expect(region).toHaveTextContent('STOP — cálculo detenido');
    expect(within(region).getByRole('alert')).toHaveAttribute('aria-live', 'assertive');
    expectNoDose(region);
  });

  it('the STOP is not dismissible, stays visible and is programmatically focusable', async () => {
    const { region } = await calculate(withAlerts([stop], true));
    const alert = within(region).getByRole('alert');
    expect(within(alert).queryByRole('button')).toBeNull();
    expect(alert).toHaveAttribute('tabindex', '-1');
    alert.focus();
    expect(alert).toHaveFocus();
    await new Promise((r) => setTimeout(r, 50));
    expect(within(region).getByRole('alert')).toBeVisible();
  });

  it('no duplicate announcement: the polite summary stays empty when stopped', async () => {
    await calculate(withAlerts([stop], true));
    expect(politeSummary().textContent).toBe('');
    expect(screen.getAllByRole('alert')).toHaveLength(1);
  });
});

describe('U08c unknown severity', () => {
  it.each(['WARNING', 'stop', 'CRITICAL'])('%j is handled as STOP (assertive, literal label, no dose)', async (severity) => {
    const { region } = await calculate(withAlerts([{ ...stop, severity }]));
    const alert = within(region).getByRole('alert');
    expect(alert).toHaveAttribute('aria-live', 'assertive');
    expect(alert).toHaveTextContent(`${severity}: Croup discharge criteria missing`);
    expectNoDose(region);
  });

  it('padded " ALERT " stops the calculation; StopAlert lists it as a notice, so one explicit assertive STOP is added', async () => {
    const { region } = await calculate(withAlerts([{ ...stop, severity: ' ALERT ' }]));
    expectNoDose(region);
    const alerts = within(region).getAllByRole('alert');
    expect(alerts).toHaveLength(1);
    expect(alerts[0]).toHaveAttribute('data-testid', 'stop-fallback');
    expect(alerts[0]).toHaveAttribute('aria-live', 'assertive');
    expect(within(region).getByRole('status')).toHaveTextContent('Croup discharge criteria missing');
  });

  it('blocked with no alerts still gets exactly one assertive STOP', async () => {
    const { region } = await calculate(withAlerts([], true));
    const alerts = within(region).getAllByRole('alert');
    expect(alerts).toHaveLength(1);
    expect(alerts[0]).toHaveTextContent('no se muestra ninguna dosis');
    expectNoDose(region);
  });
});

describe('U08c informative alerts', () => {
  it.each(['ALERT', 'CAUTION', 'INFO'])('%s is polite (role=status), never role=alert, and the result stays', async (severity) => {
    const { region } = await calculate(withAlerts([{ severity, code: 'hepatic', message: 'Revisar función hepática', action: 'Comprobar' }]));
    const status = within(region).getByRole('status');
    expect(status).toHaveAttribute('aria-live', 'polite');
    expect(status).toHaveTextContent(`${severity}: Revisar función hepática`);
    expect(status).toHaveTextContent('hepatic');
    expect(within(region).queryByRole('alert')).toBeNull();
    expect(within(region).getByLabelText('Cálculo y pauta')).toHaveTextContent('525');
    expect(politeSummary()).toHaveTextContent('Resultado aritmético disponible');
  });
});

describe('U08c multiple alerts', () => {
  it('STOP group first with every STOP (duplicate codes kept), notices separate, no duplicate React keys', async () => {
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});
    const { region } = await calculate(withAlerts([
      { severity: 'INFO', code: 'note', message: 'Nota informativa' },
      { ...stop, message: 'Primer STOP' },
      { ...stop, message: 'Segundo STOP' },
    ], true));
    const alert = within(region).getByRole('alert');
    expect(within(alert).getAllByRole('listitem').map((li) => li.textContent)).toEqual([
      expect.stringContaining('Primer STOP'), expect.stringContaining('Segundo STOP')]);
    const status = within(region).getByRole('status');
    expect(status).toHaveTextContent('Nota informativa');
    expect(status).not.toHaveTextContent('STOP');
    expect(alert.compareDocumentPosition(status) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(consoleError.mock.calls.some((c) => String(c[0]).includes('same key'))).toBe(false);
    expectNoDose(region);
  });
});

describe('U08c stale results', () => {
  it('changing regimen removes the STOP and its announcement', async () => {
    await calculate(withAlerts([stop], true));
    fireEvent.change(screen.getByLabelText('Diagnóstico y régimen'), { target: { value: 'ibuprofen-pain-fever-home' } });
    await waitFor(() => expect(screen.queryByRole('region', { name: 'Resultado pediátrico' })).toBeNull());
    expect(screen.queryByRole('alert')).toBeNull();
  });

  it('editing an input removes the STOP immediately', async () => {
    await calculate(withAlerts([stop], true));
    fireEvent.change(screen.getByLabelText('Peso real (kg)'), { target: { value: '20' } });
    expect(screen.queryByRole('alert')).toBeNull();
    expect(screen.queryByRole('region', { name: 'Resultado pediátrico' })).toBeNull();
  });

  it('a late STOP after an edit is discarded (no stale announcement)', async () => {
    let finish!: (r: Response) => void;
    vi.spyOn(globalThis, 'fetch').mockReturnValueOnce(new Promise((r) => { finish = r; }));
    await renderAt(`/pediatrics?regimen=${paracetamol}`, [{ path: '/pediatrics', element: <PediatricOutpatient /> }], 'es');
    fireEvent.click(screen.getByRole('button', { name: 'Comprobar y calcular' }));
    fireEvent.change(screen.getByLabelText('Peso real (kg)'), { target: { value: '20' } });
    await act(async () => finish(response(withAlerts([stop], true))));
    expect(screen.queryByRole('alert')).toBeNull();
    expect(screen.queryByRole('region', { name: 'Resultado pediátrico' })).toBeNull();
  });

  it('a later success replaces a STOP: no STOP left, polite summary only', async () => {
    const fetcher = vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(response(withAlerts([stop], true))).mockResolvedValueOnce(response(ok));
    await renderAt(`/pediatrics?regimen=${paracetamol}`, [{ path: '/pediatrics', element: <PediatricOutpatient /> }], 'es');
    fireEvent.click(screen.getByRole('button', { name: 'Comprobar y calcular' }));
    await screen.findByRole('alert');
    fireEvent.click(screen.getByRole('button', { name: 'Comprobar y calcular' }));
    await waitFor(() => expect(fetcher).toHaveBeenCalledTimes(2));
    await screen.findByLabelText('Cálculo y pauta');
    expect(screen.queryByRole('alert')).toBeNull();
  });
});

describe('U08c keyboard and focus', () => {
  it('keyboard-only: Enter on the button calculates; focus moves to the result region containing the STOP', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(response(withAlerts([stop], true)));
    const user = userEvent.setup();
    await renderAt(`/pediatrics?regimen=${paracetamol}`, [{ path: '/pediatrics', element: <PediatricOutpatient /> }], 'es');
    screen.getByRole('button', { name: 'Comprobar y calcular' }).focus();
    await user.keyboard('{Enter}');
    const region = await screen.findByRole('region', { name: 'Resultado pediátrico' });
    await waitFor(() => expect(region).toHaveFocus());
    expect(region).toContainElement(screen.getByRole('alert'));
  });

  it('Tab from the focused region continues through the page without entering a trap', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(response(withAlerts([stop], true)));
    const user = userEvent.setup();
    await renderAt(`/pediatrics?regimen=${paracetamol}`, [{ path: '/pediatrics', element: <PediatricOutpatient /> }], 'es');
    fireEvent.click(screen.getByRole('button', { name: 'Comprobar y calcular' }));
    const region = await screen.findByRole('region', { name: 'Resultado pediátrico' });
    await waitFor(() => expect(region).toHaveFocus());
    await user.tab();
    expect(document.activeElement).not.toBe(region);
    expect(document.activeElement).not.toBe(document.body);
  });
});
