/**
 * PEDIATRIC-SAFETY-01 — NEW-05 at component level: a malformed pediatric response never renders a
 * dose, a confirmation, an export or a print sheet; a previous result is withdrawn. Synthetic
 * responses follow pediatric-u08b.test.tsx; no clinical values invented.
 */
import { act, cleanup, fireEvent, screen, waitFor } from '@testing-library/react';
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
const withDose = (dose: unknown) => ({ ...ok, result: { ...result, dose_mg: dose } });
const CONFIRM = 'Confirmo haber revisado el resultado completo, sus límites y advertencias';

async function submit(...answers: Response[]) {
  const fetcher = vi.spyOn(globalThis, 'fetch');
  for (const a of answers) fetcher.mockResolvedValueOnce(a);
  await renderAt(`/pediatrics?regimen=${paracetamol}`, [{ path: '/pediatrics', element: <PediatricOutpatient /> }]);
  fireEvent.change(screen.getByLabelText('Peso real (kg)'), { target: { value: '35' } });
  fireEvent.click(screen.getByRole('button', { name: 'Comprobar y calcular' }));
  return fetcher;
}
function expectNoDoseNorActions() {
  expect(screen.queryByRole('region', { name: 'Resultado pediátrico' })).toBeNull();
  expect(screen.queryByText('Dosis por toma (mg)', { selector: 'dt' })).toBeNull();
  expect(screen.queryByRole('checkbox', { name: CONFIRM })).toBeNull();
  expect(screen.queryByRole('button', { name: /Exportar/ })).toBeNull();
  expect(screen.queryByRole('button', { name: 'Imprimir resultado' })).toBeNull();
  expect(document.querySelector('.pediatric-print-sheet')).toBeNull();
}

describe('NEW-05 — malformed dose_mg never renders as a dose', () => {
  it.each([['text', 'abc'], ['numeric string', '525'], ['boolean', true], ['object', {}], ['array', [525]], ['negative', -1]])(
    'dose_mg %s → explanatory error, no dose, no confirmation, no export', async (_name, dose) => {
      await submit(response(withDose(dose)));
      expect(await screen.findByText(/Respuesta del servidor no válida/)).toHaveAttribute('role', 'alert');
      expectNoDoseNorActions();
      expect(document.body.textContent).not.toMatch(/\babc\b/);
    });

  it('a valid response still renders its dose (regression)', async () => {
    await submit(response(ok));
    expect(await screen.findByRole('region', { name: 'Resultado pediátrico' })).toHaveTextContent('525 mg');
  });

  it('a previous valid result is withdrawn when the next answer is malformed', async () => {
    await submit(response(ok), response(withDose('abc')));
    await screen.findByRole('region', { name: 'Resultado pediátrico' });
    fireEvent.click(screen.getByRole('button', { name: 'Comprobar y calcular' }));
    expect(await screen.findByText(/Respuesta del servidor no válida/)).toBeInTheDocument();
    expectNoDoseNorActions();
  });

  it('a late malformed answer after an edit is discarded and leaves nothing on screen', async () => {
    let release: (r: Response) => void = () => undefined;
    const fetcher = vi.spyOn(globalThis, 'fetch').mockReturnValueOnce(new Promise<Response>((r) => { release = r; }));
    await renderAt(`/pediatrics?regimen=${paracetamol}`, [{ path: '/pediatrics', element: <PediatricOutpatient /> }]);
    fireEvent.change(screen.getByLabelText('Peso real (kg)'), { target: { value: '35' } });
    fireEvent.click(screen.getByRole('button', { name: 'Comprobar y calcular' }));
    fireEvent.change(screen.getByLabelText('Peso real (kg)'), { target: { value: '36' } });
    await act(async () => { release(response(withDose('abc'))); });
    await waitFor(() => expect(fetcher).toHaveBeenCalledTimes(1));
    expectNoDoseNorActions();
    expect(screen.queryByText(/Respuesta del servidor no válida/)).toBeNull();
  });

  it('blocked:true with a malformed result shows the blocked state and no dose', async () => {
    await submit(response({ ...withDose('abc'), blocked: true }));
    expect(await screen.findByRole('region', { name: 'Resultado pediátrico' })).toHaveTextContent('Cálculo bloqueado');
    expect(screen.queryByText('Dosis por toma (mg)', { selector: 'dt' })).toBeNull();
    expect(screen.queryByRole('checkbox', { name: CONFIRM })).toBeNull();
  });
});
