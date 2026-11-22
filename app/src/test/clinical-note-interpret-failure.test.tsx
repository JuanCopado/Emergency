// A connection failure during image interpretation is never shown as an interpretation, and is never retried.
// Synthetic upload only; no clinical content is produced by the mocked service.
import { screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import ClinicalNote from '../pages/ClinicalNote';
import { renderAt } from './render';

const prepared = {
  api_version: '1.0',
  upload_id: 'upload-image-failure',
  filename: 'rx_torax.png',
  mime_type: 'image/png',
  size_bytes: 12,
  sha256: 'image-sha',
  media: { format: 'png', status: 'ok', quality_flags: [], issues: [], metadata_present: false, metadata: {} },
  kind: 'xray',
  kind_source: 'inferred_from_filename',
  route: { kind: 'xray', target_section: 'imaging', modules: ['clinical-image-interpretation', 'chest-xray', 'musculoskeletal-xray'] },
  privacy: {
    status: 'REVIEW_REQUIRED',
    findings: [],
    manual_file_privacy_review_required: true,
    burned_in_identifier_review_required: true,
  },
  extracted: { official_report: null, ai_interpretation: null },
  processing: {
    status: 'routed_external',
    message: 'Binary source routed.',
    modules: ['clinical-image-interpretation', 'chest-xray', 'musculoskeletal-xray'],
  },
  original_retained: false,
};

function json(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
}

async function openReviewCard() {
  const user = userEvent.setup();
  await renderAt('/clinical-note', [{ path: '/clinical-note', element: <ClinicalNote /> }], 'pt');
  await user.click(screen.getByRole('button', { name: 'MCDT' }));
  await user.upload(screen.getByLabelText('Upload clínico') as HTMLInputElement,
    new File(['fake-image'], 'rx_torax.png', { type: 'image/png' }));
  const card = await screen.findByTestId('mcdt-review-card');
  for (const check of within(card).getAllByRole('checkbox')) await user.click(check);
  return { user, card };
}

beforeEach(() => { vi.restoreAllMocks(); });
afterEach(() => { vi.restoreAllMocks(); });

describe('interpretation request that fails to connect', () => {
  it.each([
    ['network failure', () => Promise.reject(new TypeError('Failed to fetch')), 'Sem ligação ao serviço clínico.'],
    ['server refusal', () => Promise.resolve(json({ error: 'clinical vision provider unavailable' }, 503)), 'O serviço de interpretação está indisponível.'],
  ])('shows no interpretation and does not retry after a %s', async (_name, interpret, message) => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockImplementation(async (input) => {
      const url = String(input);
      if (url.endsWith('/api/clinical-note/upload/prepare')) return json(prepared);
      if (url.endsWith('/api/clinical-note/upload/interpret')) return interpret();
      return json({ error: 'unexpected endpoint' }, 404);
    });
    const { user, card } = await openReviewCard();
    await user.click(within(card).getByRole('button', { name: 'Interpretar com módulo IA' }));

    expect(await screen.findByText(new RegExp(message))).toBeInTheDocument();
    expect(card).not.toHaveTextContent('Interpretação IA proposta — requer revisão médica.');
    expect(card).not.toHaveTextContent('vision_interpreted');
    expect(card).toHaveTextContent('Pendente');
    expect(within(card).queryByLabelText('Achados da proposta')).toBeNull();
    await waitFor(() => expect(within(card).getByRole('button', { name: 'Interpretar com módulo IA' })).toBeEnabled());
    // prepare once, interpret once: nothing was sent again on its own
    expect(fetchMock.mock.calls.map(([url]) => String(url).split('/').pop())).toEqual(['prepare', 'interpret']);
  });
});
