import { act, fireEvent, screen, waitFor, within } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import PediatricOutpatient from '../pages/PediatricOutpatient';
import { pediatricCatalog, regimensForDrug, numericInput } from '../pediatrics/catalog';
import { renderAt } from './render';

afterEach(() => vi.restoreAllMocks());
const mount = (id = '') => renderAt(`/pediatrics${id ? `?regimen=${id}` : ''}`, [{ path: '/pediatrics', element: <PediatricOutpatient /> }]);
const enter = (label: string, value: string) => fireEvent.change(screen.getByLabelText(label), { target: { value } });
const answer = (body: unknown, ok = true) => ({ ok, json: async () => body }) as Response;
const paracetamol = 'paracetamol-pain-fever-home';

it('exposes all 89 canonical regimens and 52 drug groups without age/weight filtering', async () => {
  await mount();
  expect(within(screen.getByLabelText('Diagnóstico y régimen')).getAllByRole('option')).toHaveLength(90);
  expect(within(screen.getByLabelText('Fármaco o combinación')).getAllByRole('option')).toHaveLength(53);
  const ids = pediatricCatalog.regimens.map((r) => r.id);
  expect(new Set(ids).size).toBe(89);
  for (const d of pediatricCatalog.drugs) expect(regimensForDrug(d.id).length).toBeGreaterThan(0);
  expect(new Set(pediatricCatalog.regimens.map((r) => r.drug_id))).toEqual(new Set(pediatricCatalog.drugs.map((d) => d.id)));
  enter('Diagnóstico y régimen', paracetamol);
  enter('Edad (meses)', '0'); enter('Peso real (kg)', '1');
  expect(within(screen.getByLabelText('Diagnóstico y régimen')).getAllByRole('option')).toHaveLength(90);
});

it('groups multiple formulations and indications under one active drug', async () => {
  await mount();
  enter('Fármaco o combinación', 'fluticasone-propionate');
  const options = within(screen.getByLabelText('Diagnóstico y régimen')).getAllByRole('option');
  expect(options).toHaveLength(4);
  expect(options.map((o) => o.textContent).join(' ')).toMatch(/rhinitis/);
  expect(options.map((o) => o.textContent).join(' ')).toMatch(/asthma/);
});

it('renders canonical dose, ideal weight, limits, administration and the unconfirmed home gate', async () => {
  await mount(paracetamol);
  const card = screen.getByRole('region', { name: 'Ficha canónica' });
  expect(card).toHaveTextContent('15'); expect(card).toHaveTextContent('1000');
  expect(card).toHaveTextContent('every 6 h'); expect(card).toHaveTextContent('without food');
  expect(screen.getByLabelText('Peso ideal (kg)')).toBeInTheDocument();
  expect(screen.getByLabelText('home analgesia antipyresis appropriate')).toHaveValue('');
});

it('submits stable IDs and explicit data to the canonical backend and shows computed course', async () => {
  const fetcher = vi.spyOn(globalThis, 'fetch').mockResolvedValue(answer({ blocked: false,
    safety: { prescription_status: 'REVIEW_REQUIRED', alerts: [] },
    result: { dose_mg: 525, volume_per_dose: { exact_ml: 21.875, rounded_0_1_ml: 21.9 }, total_doses: 8, estimated_total_course_ml: 175 } }));
  await mount(paracetamol);
  enter('Edad (meses)', '120'); enter('Peso real (kg)', '55'); enter('Peso ideal (kg)', '35');
  enter('home analgesia antipyresis appropriate', 'yes');
  enter('Duración elegida (días; solo si la fuente exige selección)', '2');
  enter('Concentración verificada (mg/mL)', '24');
  fireEvent.click(screen.getByLabelText('He verificado la concentración del producto exacto'));
  fireEvent.click(screen.getByRole('button', { name: 'Comprobar y calcular' }));
  const result = await screen.findByRole('region', { name: 'Resultado pediátrico' });
  expect(result).toHaveTextContent('525'); expect(result).toHaveTextContent('21,9'); expect(result).toHaveTextContent('175');
  const summary = within(result).getByLabelText('Cálculo y pauta');
  expect(summary).toHaveTextContent('525'); expect(summary).toHaveTextContent('21,875');
  expect(result).toHaveTextContent('Número total de tomas'); expect(result).toHaveTextContent('8');
  expect(result).toHaveFocus();
  const payload = JSON.parse(String(fetcher.mock.calls[0]?.[1]?.body));
  expect(payload.regimen_id).toBe(paracetamol);
  expect(payload.source_revision).toBe(pediatricCatalog.source_revision);
  expect(payload.patient).toEqual({ age_months: 120, actual_weight_kg: 55, ideal_weight_kg: 35, home_analgesia_antipyresis_appropriate: true });
  expect(payload.product).toEqual({ concentration_mg_per_ml: 24, external_concentration_verified: false });
});

it('shows a STOP without a calculated dose and preserves croup-specific instructions', async () => {
  vi.spyOn(globalThis, 'fetch').mockResolvedValue(answer({ blocked: true,
    safety: { prescription_status: 'BLOCKED', alerts: [{ severity: 'STOP', message: 'Croup discharge criteria missing', action: 'Reassess' }] } }));
  await mount('dexamethasone-croup-mild-moderate');
  expect(screen.getByRole('region', { name: 'Ficha canónica' })).toHaveTextContent('single dose');
  fireEvent.click(screen.getByRole('button', { name: 'Comprobar y calcular' }));
  expect(await screen.findByRole('region', { name: 'Resultado pediátrico' })).toHaveTextContent('Cálculo bloqueado');
  expect(screen.getByRole('region', { name: 'Resultado pediátrico' })).not.toHaveTextContent('Dosis por toma');
});

it('keeps the rizatriptan source boundary and displays backend blocking errors', async () => {
  vi.spyOn(globalThis, 'fetch').mockResolvedValue(answer({ error: 'no matching age/weight band for regimen' }, false));
  await mount('rizatriptan-migraine-rch');
  expect(screen.getByRole('region', { name: 'Ficha canónica' })).toHaveTextContent('exactly 40 kg');
  enter('Edad (meses)', '120'); enter('Peso real (kg)', '40');
  enter('secondary headache red flags excluded', 'yes');
  fireEvent.click(screen.getByRole('button', { name: 'Comprobar y calcular' }));
  expect(await screen.findByRole('alert')).toHaveTextContent('no matching');
  expect(screen.queryByRole('region', { name: 'Resultado pediátrico' })).not.toBeInTheDocument();
});

it('rejects nonfinite form numbers before a backend call', async () => {
  const fetcher = vi.spyOn(globalThis, 'fetch');
  await mount(paracetamol);
  enter('Peso real (kg)', 'Infinity');
  fireEvent.click(screen.getByRole('button', { name: 'Comprobar y calcular' }));
  expect(await screen.findByRole('alert')).toHaveTextContent('finito');
  expect(fetcher).not.toHaveBeenCalled();
  for (const n of ['NaN', '-Infinity', '0', '-1', 'true', '']) expect(() => numericInput(n, 'peso')).toThrow();
  expect(numericInput('20', 'peso')).toBe(20);
});

it('requires exact product confirmation before requesting mL', async () => {
  const fetcher = vi.spyOn(globalThis, 'fetch');
  await mount(paracetamol);
  enter('Concentración verificada (mg/mL)', '24');
  fireEvent.click(screen.getByRole('button', { name: 'Comprobar y calcular' }));
  expect(await screen.findByRole('alert')).toHaveTextContent('presentación exacta');
  expect(fetcher).not.toHaveBeenCalled();
});

it('discards an obsolete calculation after any patient edit', async () => {
  let finish!: (r: Response) => void;
  vi.spyOn(globalThis, 'fetch').mockReturnValue(new Promise((resolve) => { finish = resolve; }));
  await mount(paracetamol);
  fireEvent.click(screen.getByRole('button', { name: 'Comprobar y calcular' }));
  await waitFor(() => expect(globalThis.fetch).toHaveBeenCalled());
  enter('Peso ideal (kg)', '25');
  await act(async () => finish(answer({ blocked: false, safety: { prescription_status: 'OK', alerts: [] }, result: { dose_mg: 525 } })));
  expect(screen.queryByRole('region', { name: 'Resultado pediátrico' })).not.toBeInTheDocument();
});
