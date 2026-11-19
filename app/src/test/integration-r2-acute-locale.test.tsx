import { cleanup, fireEvent, screen } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import AcuteMedications from '../pages/AcuteMedications';
import { renderAt } from './render';

afterEach(() => { cleanup(); vi.restoreAllMocks(); });
const answer = (value: unknown) => ({ ok: true, json: async () => value }) as Response;
const catalog = { source_revision: 'r2-synthetic', regimens: [{
  id: 'fixture', group: 'fixture', group_label: 'Synthetic group', label: 'Synthetic option',
  drug: 'Synthetic', route: null, dose_unit: null, limitations: [],
  source: { body: 'Canonical source: do not combine regimens.', preamble: 'Synthetic', contract_review: { body: 'Canonical review retained.' } },
  fields: [
    { key: 'mode', label: 'Synthetic mode', kind: 'choice', options: ['dose', 'decision'], option_labels: { dose: 'Canonical dose option', decision: 'Canonical decision option' } },
    { key: 'value', label: 'Synthetic value', kind: 'number', required_if: { key: 'mode', equals: 'dose' } },
  ],
}] };

it.each([['es', ','], ['pt', ','], ['en', '.'], ['zh', '.']])('preserves PR20 modes, numeric JSON and invalidation in %s', async (lang, decimal) => {
  const calculation = { result_kind: 'calculation', dose: .1, dose_unit: 'mg', components: { sample: 1000.5 },
    review_status: 'OWNER_VALIDATED_2026_11_16', monitoring_and_warnings: 'Canonical STOP: do not administer together.' };
  const decision = { result_kind: 'decision_support', dose: null, dose_unit: null,
    decision_support: 'Canonical guidance without a dose.', next_actions: ['Canonical next step.'],
    monitoring_and_warnings: 'Canonical STOP: do not administer together.' };
  const fetcher = vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(answer(catalog))
    .mockResolvedValueOnce(answer({ blocked: false, alerts: [], result: calculation }))
    .mockResolvedValueOnce(answer({ blocked: false, alerts: [], result: decision }));
  await renderAt('/acute', [{ path: '/acute', element: <AcuteMedications /> }], lang);
  await screen.findByRole('option', { name: 'Synthetic group' });
  fireEvent.change(screen.getByTestId('acute-group'), { target: { value: 'fixture' } });
  fireEvent.change(screen.getByTestId('acute-regimen'), { target: { value: 'fixture' } });
  expect(screen.queryByLabelText('Synthetic value')).not.toBeInTheDocument();
  fireEvent.change(screen.getByLabelText('Synthetic mode'), { target: { value: 'dose' } });
  const input = screen.getByLabelText('Synthetic value');
  expect(input).toHaveAttribute('lang', 'en');
  expect(input).toHaveAccessibleDescription(/0\.1/);
  fireEvent.change(input, { target: { value: '0.1' } });
  fireEvent.submit(screen.getByTestId('acute-form'));
  await screen.findByTestId('owner-validation');
  expect(document.querySelector('[data-result="dose"]')).toHaveTextContent(`0${decimal}1`);
  expect(document.querySelector('[data-result="components"]')).toHaveTextContent(`1000${decimal}5`);
  expect(screen.getByTestId('acute-warnings')).toHaveTextContent(calculation.monitoring_and_warnings);
  expect(JSON.parse(String(fetcher.mock.calls[1]?.[1]?.body))).toEqual({
    regimen_id: 'fixture', source_revision: 'r2-synthetic', inputs: { mode: 'dose', value: .1 },
  });
  const exportButton = screen.getByTestId('acute-export').querySelector('button');
  expect(exportButton).toBeDisabled();
  fireEvent.click(screen.getByRole('checkbox'));
  expect(exportButton).toBeEnabled();
  fireEvent.change(screen.getByLabelText('Synthetic mode'), { target: { value: 'decision' } });
  expect(screen.queryByTestId('acute-export')).not.toBeInTheDocument();
  expect(screen.queryByLabelText('Synthetic value')).not.toBeInTheDocument();
  fireEvent.submit(screen.getByTestId('acute-form'));
  await screen.findByText(decision.decision_support);
  expect(document.querySelector('[data-result="dose"]')).toBeNull();
  expect(document.querySelector('[data-result="pump_ml_h"]')).toBeNull();
  expect(screen.getByRole('checkbox')).not.toBeChecked();
  expect(JSON.parse(String(fetcher.mock.calls[2]?.[1]?.body)).inputs).toEqual({ mode: 'decision' });
  expect(screen.getByText('Canonical review retained.')).toBeInTheDocument();
});
