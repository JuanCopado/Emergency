/**
 * U08a — defensive blocking and comma-only parser in PediatricOutpatient.
 * Former KNOWN-DEFECT cases A02-PE-02 and A01-PE-03/04/05 become ordinary tests here.
 * Fixtures reused from pediatric-outpatient.test.tsx / blocked-stop.test.tsx (synthetic responses).
 */
import { cleanup, fireEvent, screen, waitFor, within } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import PediatricOutpatient from '../pages/PediatricOutpatient';
import { numericInput, pediatricCatalog } from '../pediatrics/catalog';
import { renderAt } from './render';

afterEach(() => { cleanup(); vi.restoreAllMocks(); });
const response = (value: unknown, ok = true) => ({ ok, json: async () => value }) as Response;
const paracetamol = 'paracetamol-pain-fever-home';
const pediatricResult = { dose_mg: 525, volume_per_dose: { exact_ml: 21.875, rounded_0_1_ml: 21.9 }, total_doses: 8, estimated_total_course_ml: 175 };
const report = { snapshot: {}, sections: [] };
const ok = { blocked: false, result: pediatricResult, export_report: report, safety: { prescription_status: 'REVIEW_REQUIRED', alerts: [] } };
const stopAlert = { severity: 'STOP', message: 'Croup discharge criteria missing', action: 'Reassess' };

async function mount() {
  await renderAt(`/pediatrics?regimen=${paracetamol}`, [{ path: '/pediatrics', element: <PediatricOutpatient /> }]);
}
const enter = (label: string, value: string) => fireEvent.change(screen.getByLabelText(label), { target: { value } });
const calculate = () => fireEvent.click(screen.getByRole('button', { name: 'Comprobar y calcular' }));
async function answerWith(body: unknown) {
  vi.spyOn(globalThis, 'fetch').mockResolvedValue(response(body));
  await mount();
  calculate();
}
function expectNoDose() {
  expect(screen.queryByLabelText('Cálculo y pauta')).toBeNull();
  expect(document.body).not.toHaveTextContent('525');
  expect(screen.queryByRole('button', { name: 'Exportar JSON' })).toBeNull();
  expect(document.querySelector('.pediatric-print-sheet')).toBeNull();
}

describe('U08a numericInput decimal policy (A01-PE-03/04/05)', () => {
  it('PE-05 accepts "12,5" as 12.5 and keeps integers and zero rules', () => {
    expect(numericInput('12,5', 'Peso')).toBe(12.5);
    expect(numericInput('20', 'Peso')).toBe(20);
    expect(numericInput('0,05', 'Peso')).toBe(0.05);
    expect(numericInput('0', 'Edad', true)).toBe(0);
    expect(() => numericInput('0', 'Peso')).toThrow('mayor que cero');
  });

  it('PE-05-DOT rejects "12.5" with an explicit comma message', () => {
    expect(() => numericInput('12.5', 'Peso')).toThrow('usa coma como separador decimal');
  });

  it.each(['0x10', '1e1', '1E1', '+20', '-1', 'NaN', '-Infinity', 'true', '', '12,5,1', '1 2', ',5'])('PE-03/04 rejects %j', (text) => {
    expect(() => numericInput(text, 'Peso')).toThrow('Peso:');
  });

  it('PE-03-UI weight "0x10" never reaches the backend', async () => {
    const fetcher = vi.spyOn(globalThis, 'fetch').mockResolvedValue(response(ok));
    await mount();
    enter('Peso real (kg)', '0x10');
    calculate();
    expect(await screen.findByRole('alert')).toHaveTextContent('Peso real (kg)');
    expect(fetcher).not.toHaveBeenCalled();
  });

  it('comma decimals in the form are sent as ordinary JSON numbers', async () => {
    const fetcher = vi.spyOn(globalThis, 'fetch').mockResolvedValue(response(ok));
    await mount();
    enter('Edad (meses)', '120'); enter('Peso real (kg)', '55,5'); enter('Peso ideal (kg)', '35,25');
    calculate();
    await screen.findByRole('region', { name: 'Resultado pediátrico' });
    const payload = JSON.parse(String(fetcher.mock.calls[0]?.[1]?.body));
    expect(payload.patient).toMatchObject({ age_months: 120, actual_weight_kg: 55.5, ideal_weight_kg: 35.25 });
    expect(payload.regimen_id).toBe(paracetamol);
    expect(payload.source_revision).toBe(pediatricCatalog.source_revision);
  });
});

describe('U08a defensive classification (A02-PE-02)', () => {
  it('PE-02 blocked:false with a STOP alert shows no dose and no export', async () => {
    await answerWith({ ...ok, safety: { prescription_status: 'BLOCKED', alerts: [stopAlert] } });
    const region = await screen.findByRole('region', { name: 'Resultado pediátrico' });
    await waitFor(() => expect(region).toHaveTextContent('Croup discharge criteria missing'));
    expect(region).toHaveTextContent('STOP — cálculo detenido');
    expectNoDose();
  });

  it.each(['WARNING', '', 'stop', 'CRITICAL'])('unknown severity %j is treated as STOP', async (severity) => {
    await answerWith({ ...ok, safety: { prescription_status: 'REVIEW_REQUIRED', alerts: [{ ...stopAlert, severity }] } });
    const region = await screen.findByRole('region', { name: 'Resultado pediátrico' });
    expect(region).toHaveTextContent('Croup discharge criteria missing');
    expectNoDose();
  });

  it('PE-01 blocked:true with an unexpected result shows no dose', async () => {
    await answerWith({ ...ok, blocked: true, safety: { prescription_status: 'BLOCKED', alerts: [stopAlert] } });
    const region = await screen.findByRole('region', { name: 'Resultado pediátrico' });
    expect(region).toHaveTextContent('Cálculo bloqueado');
    expectNoDose();
  });

  it('non-STOP severities keep the result visible with their notices', async () => {
    await answerWith({ ...ok, safety: { prescription_status: 'REVIEW_REQUIRED', alerts: [{ severity: 'CAUTION', message: 'Revisar función hepática', action: '' }] } });
    const region = await screen.findByRole('region', { name: 'Resultado pediátrico' });
    expect(within(region).getByLabelText('Cálculo y pauta')).toHaveTextContent('525');
    expect(region).toHaveTextContent('Revisar función hepática');
  });

  it.each([
    ['missing blocked flag', { result: pediatricResult, safety: { alerts: [] } }],
    ['missing safety', { blocked: false, result: pediatricResult }],
    ['missing result', { blocked: false, safety: { alerts: [] } }],
    ['negative volume', { ...ok, result: { ...pediatricResult, volume_per_dose: { exact_ml: -1, rounded_0_1_ml: 21.9 } } }],
    ['malformed alerts', { ...ok, safety: { alerts: 'STOP' } }],
  ])('malformed response (%s) → error, no dose', async (_name, body) => {
    await answerWith(body);
    expect(await screen.findByRole('alert')).toHaveTextContent('Respuesta del servidor no válida');
    expect(screen.queryByRole('region', { name: 'Resultado pediátrico' })).toBeNull();
    expectNoDose();
  });

  it('STOP region receives focus', async () => {
    await answerWith({ ...ok, safety: { prescription_status: 'BLOCKED', alerts: [stopAlert] } });
    const region = await screen.findByRole('region', { name: 'Resultado pediátrico' });
    await waitFor(() => expect(region).toHaveFocus());
  });
});
