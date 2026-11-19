import { fireEvent, screen } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import PediatricOutpatient from '../pages/PediatricOutpatient';
import { renderAt } from './render';

afterEach(() => vi.restoreAllMocks());
const enter = (label: string, value: string) => fireEvent.change(screen.getByLabelText(label), { target: { value } });
const answer = (body: unknown) => ({ ok: true, json: async () => body }) as Response;
const mount = (id = 'paracetamol-pain-fever-home') => renderAt(`/pediatrics?regimen=${id}`, [{ path: '/pediatrics', element: <PediatricOutpatient /> }], 'es');
const submit = () => fireEvent.click(screen.getByRole('button', { name: 'Comprobar y calcular' }));

for (const field of ['Peso real (kg)', 'Peso ideal (kg)']) {
  it.each(['0', '5e-324', '0.5', '0.99999999999999999999', '180.000000000000000001', '181', 'Infinity', 'NaN', 'true'])(
    `rejects ${field}=%s before conversion or a backend request`, async (value) => {
      const fetcher = vi.spyOn(globalThis, 'fetch');
      await mount();
      enter('Peso real (kg)', '55'); enter('Peso ideal (kg)', '35');
      enter(field, value); submit();
      expect(await screen.findByRole('alert')).toHaveTextContent('entre 1 y 180 kg');
      expect(fetcher).not.toHaveBeenCalled();
      expect(screen.queryByRole('region', { name: 'Resultado pediátrico' })).not.toBeInTheDocument();
    },
  );

  it.each(['1', '18.25', '180'])(`passes ${field}=%s unchanged`, async (value) => {
    const fetcher = vi.spyOn(globalThis, 'fetch').mockResolvedValue(answer({ blocked: false,
      result: { dosing_weight_kg: Number(value) }, safety: { prescription_status: 'REVIEW_REQUIRED', alerts: [] } }));
    await mount();
    enter('Edad (meses)', '120'); enter('Peso real (kg)', '55'); enter('Peso ideal (kg)', '35');
    enter('home analgesia antipyresis appropriate', 'yes');
    enter(field, value); submit();
    await screen.findByRole('region', { name: 'Resultado pediátrico' });
    const payload = JSON.parse(String(fetcher.mock.calls[0]?.[1]?.body));
    expect(payload.patient[field === 'Peso real (kg)' ? 'actual_weight_kg' : 'ideal_weight_kg']).toBe(Number(value));
  });
}

it('keeps absent required weight absent and displays the backend STOP without a result', async () => {
  const fetcher = vi.spyOn(globalThis, 'fetch').mockResolvedValue(answer({ blocked: true,
    safety: { prescription_status: 'BLOCKED', alerts: [{ severity: 'STOP', message: 'ideal_weight_kg is required', action: 'Enter the required weight' }] } }));
  await mount();
  enter('Peso real (kg)', '55'); submit();
  const result = await screen.findByRole('region', { name: 'Resultado pediátrico' });
  expect(result).toHaveTextContent('Cálculo bloqueado');
  expect(result).toHaveTextContent('ideal_weight_kg is required');
  const payload = JSON.parse(String(fetcher.mock.calls[0]?.[1]?.body));
  expect(payload.patient).not.toHaveProperty('ideal_weight_kg');
  expect(screen.queryByRole('button', { name: /Exportar/ })).not.toBeInTheDocument();
});

it('does not invent or require weight for a non-weight regimen', async () => {
  const fetcher = vi.spyOn(globalThis, 'fetch').mockResolvedValue(answer({ blocked: false,
    result: { dose_mg: 400 }, safety: { prescription_status: 'REVIEW_REQUIRED', alerts: [] } }));
  await mount('albendazole-ascariasis-ge2y');
  enter('Edad (meses)', '84'); submit();
  await screen.findByRole('region', { name: 'Resultado pediátrico' });
  const payload = JSON.parse(String(fetcher.mock.calls[0]?.[1]?.body));
  expect(payload.patient).toEqual({ age_months: 84 });
});
