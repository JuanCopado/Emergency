/**
 * U08b — pediatric presentation and explicit confirmation before export/print (G-P2).
 * Synthetic responses reused from pediatric-outpatient.test.tsx; no clinical values invented.
 */
import { act, cleanup, fireEvent, screen, waitFor, within } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import PediatricOutpatient from '../pages/PediatricOutpatient';
import { renderAt } from './render';

afterEach(() => { cleanup(); vi.restoreAllMocks(); });
const response = (value: unknown, ok = true) => ({ ok, json: async () => value }) as Response;
const paracetamol = 'paracetamol-pain-fever-home';
const result = { dose_mg: 525, dose_mg_per_kg: 15, dosing_weight_kg: 35, volume_per_dose: { exact_ml: 21.875, rounded_0_1_ml: 21.9 },
  total_doses: 8, estimated_total_course_ml: 175 };
const ok = { blocked: false, result, export_report: { snapshot: {}, sections: [['Resultado', ['YELLOW', 'CLINICALLY_PENDING']]] },
  safety: { prescription_status: 'REVIEW_REQUIRED', alerts: [] } };
const CONFIRM = 'Confirmo haber revisado el resultado completo, sus límites y advertencias';

async function calculated(...extra: Response[]) {
  const fetcher = vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(response(ok));
  for (const r of extra) fetcher.mockResolvedValueOnce(r);
  await renderAt(`/pediatrics?regimen=${paracetamol}`, [{ path: '/pediatrics', element: <PediatricOutpatient /> }]);
  fireEvent.change(screen.getByLabelText('Peso real (kg)'), { target: { value: '35' } });
  fireEvent.click(screen.getByRole('button', { name: 'Comprobar y calcular' }));
  const region = await screen.findByRole('region', { name: 'Resultado pediátrico' });
  return { fetcher, region };
}
const valueOf = (region: HTMLElement, label: string) => within(region).getAllByText(label, { selector: 'dt' })[0]!.nextElementSibling!.textContent;

describe('U08b presentation', () => {
  it('mg and mg/kg sit beside their values in separate fields', async () => {
    const { region } = await calculated();
    expect(valueOf(region, 'Dosis por toma (mg)')).toBe('525 mg');
    expect(valueOf(region, 'Dosis (mg/kg)')).toBe('15 mg/kg');
    expect(valueOf(region, 'Peso utilizado (kg)')).toBe('35 kg');
    expect(valueOf(region, 'Volumen total del curso (mL)')).toBe('175 mL');
  });

  it('decimals use comma at full precision; no extra rounding', async () => {
    const { region } = await calculated();
    expect(valueOf(region, 'Volumen exacto (mL)')).toBe('21,875 mL');
    expect(valueOf(region, 'Volumen redondeado (mL)')).toBe('21,9 mL');
    expect(region.textContent).not.toMatch(/21\.8|21\.9/);
  });
});

describe('U08b confirmation gate (G-P2)', () => {
  it('export and print are absent until the result is explicitly confirmed', async () => {
    await calculated();
    const box = screen.getByRole('checkbox', { name: CONFIRM });
    expect(box).not.toBeChecked();
    expect(screen.queryByRole('button', { name: 'Exportar JSON' })).toBeNull();
    expect(screen.queryByRole('button', { name: 'Imprimir resultado' })).toBeNull();
    expect(document.querySelector('.pediatric-print-sheet')).toBeNull();
    fireEvent.click(box);
    expect(screen.getByRole('button', { name: 'Exportar JSON' })).toBeEnabled();
    expect(screen.getByRole('button', { name: 'Imprimir resultado' })).toBeEnabled();
    expect(document.querySelector('.pediatric-print-sheet')).not.toBeNull();
  });

  it('unconfirming removes export and print again', async () => {
    await calculated();
    const box = screen.getByRole('checkbox', { name: CONFIRM });
    fireEvent.click(box); fireEvent.click(box);
    expect(screen.queryByRole('button', { name: 'Exportar JSON' })).toBeNull();
    expect(document.querySelector('.pediatric-print-sheet')).toBeNull();
  });

  it('any input change invalidates the confirmation and the result', async () => {
    await calculated();
    fireEvent.click(screen.getByRole('checkbox', { name: CONFIRM }));
    fireEvent.change(screen.getByLabelText('Peso real (kg)'), { target: { value: '36' } });
    expect(screen.queryByRole('region', { name: 'Resultado pediátrico' })).toBeNull();
    expect(screen.queryByRole('checkbox', { name: CONFIRM })).toBeNull();
    expect(document.querySelector('.pediatric-print-sheet')).toBeNull();
  });

  it('a new calculation starts unconfirmed', async () => {
    const { fetcher } = await calculated();
    fetcher.mockResolvedValueOnce(response(ok));
    fireEvent.click(screen.getByRole('checkbox', { name: CONFIRM }));
    fireEvent.click(screen.getByRole('button', { name: 'Comprobar y calcular' }));
    await waitFor(() => expect(fetcher).toHaveBeenCalledTimes(2));
    expect(await screen.findByRole('checkbox', { name: CONFIRM })).not.toBeChecked();
    expect(screen.queryByRole('button', { name: 'Exportar JSON' })).toBeNull();
  });

  it('the confirmed export sends the exact server result, not the displayed text', async () => {
    const { fetcher } = await calculated(response({ filename: 'p.json', mime_type: 'application/json', content_base64: 'e30=' }));
    const create = URL.createObjectURL; const revoke = URL.revokeObjectURL;
    URL.createObjectURL = vi.fn(() => 'blob:x'); URL.revokeObjectURL = vi.fn();
    vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {});
    try {
      fireEvent.click(screen.getByRole('checkbox', { name: CONFIRM }));
      fireEvent.click(screen.getByRole('button', { name: 'Exportar JSON' }));
      await waitFor(() => expect(fetcher).toHaveBeenCalledTimes(2));
      const body = JSON.parse(String((fetcher.mock.calls[1]?.[1] as RequestInit).body));
      expect(body.expected_result).toEqual(result);
      expect(body.calculation.patient.actual_weight_kg).toBe(35);
    } finally { URL.createObjectURL = create; URL.revokeObjectURL = revoke; }
  });

  it('a late export after an input change produces no download', async () => {
    let finish!: (value: Response) => void;
    const { fetcher } = await calculated();
    fetcher.mockImplementationOnce(() => new Promise((resolve) => { finish = resolve; }));
    const click = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {});
    fireEvent.click(screen.getByRole('checkbox', { name: CONFIRM }));
    fireEvent.click(screen.getByRole('button', { name: 'Exportar JSON' }));
    await waitFor(() => expect(fetcher).toHaveBeenCalledTimes(2));
    fireEvent.change(screen.getByLabelText('Peso real (kg)'), { target: { value: '36' } });
    await act(async () => finish(response({ filename: 'p.json', mime_type: 'application/json', content_base64: 'e30=' })));
    expect(click).not.toHaveBeenCalled();
  });

  it('STOP never offers the confirmation', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(response({ ...ok, safety: { prescription_status: 'BLOCKED', alerts: [{ severity: 'STOP', message: 'Detener', action: '' }] } }));
    await renderAt(`/pediatrics?regimen=${paracetamol}`, [{ path: '/pediatrics', element: <PediatricOutpatient /> }]);
    fireEvent.click(screen.getByRole('button', { name: 'Comprobar y calcular' }));
    await screen.findByRole('region', { name: 'Resultado pediátrico' });
    expect(screen.queryByRole('checkbox', { name: CONFIRM })).toBeNull();
  });
});
