// R13 · R5-1 policy layers 1-6, INACTIVE prototype. Synthetic upload only; the mocked service produces nothing clinical.
import { screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import ClinicalNote from '../pages/ClinicalNote';
import { MODALITIES, appliesDermatologicFilter, r51PrototypeEnabled } from '../clinical-note/r51Prototype';
import { renderAt } from './render';

function prepared(kind: string, assessment?: unknown) {
  return {
    api_version: '1.0', upload_id: `upload-${kind}`, filename: 'imagen.png', mime_type: 'image/png', size_bytes: 12,
    sha256: 'sha', media: { format: 'png', status: 'ok', quality_flags: [], issues: [], metadata_present: false, metadata: {} },
    kind, kind_source: 'explicit',
    route: { kind, target_section: 'imaging', modules: ['clinical-image-interpretation'] },
    privacy: { status: 'REVIEW_REQUIRED', findings: [], manual_file_privacy_review_required: true, burned_in_identifier_review_required: true },
    extracted: { official_report: null, ai_interpretation: null },
    processing: { status: 'routed_external', message: 'Binary source routed.', modules: ['clinical-image-interpretation'] },
    original_retained: false,
    ...(assessment ? { kind_assessment: assessment } : {}),
  };
}

function mockService(assessment?: unknown) {
  const bodies: Record<string, unknown>[] = [];
  vi.spyOn(globalThis, 'fetch').mockImplementation(async (input, init) => {
    const url = String(input);
    if (url.endsWith('/api/clinical-note/upload/prepare')) {
      const body = JSON.parse(String(init?.body));
      bodies.push(body);
      return new Response(JSON.stringify(prepared(body.explicit_kind ?? 'other_image', assessment)), { status: 200, headers: { 'Content-Type': 'application/json' } });
    }
    return new Response(JSON.stringify({ error: 'unexpected endpoint' }), { status: 404 });
  });
  return bodies;
}

async function openMcdt() {
  const user = userEvent.setup();
  await renderAt('/clinical-note', [{ path: '/clinical-note', element: <ClinicalNote /> }], 'pt');
  await user.click(screen.getByRole('button', { name: 'MCDT' }));
  return user;
}

const png = () => new File(['fake-image'], 'rx_torax.png', { type: 'image/png' });

beforeEach(() => {
  vi.restoreAllMocks();
  URL.createObjectURL = vi.fn(() => 'blob:preview');
  URL.revokeObjectURL = vi.fn();
});
afterEach(() => { vi.unstubAllEnvs(); vi.restoreAllMocks(); });

describe('feature flag', () => {
  it('is off by default and only an explicit 1 in a non-production build turns it on', () => {
    expect(r51PrototypeEnabled()).toBe(false);
    for (const value of ['0', 'true', 'yes', '']) {
      vi.stubEnv('VITE_R51_PROTOTYPE', value);
      expect(r51PrototypeEnabled(), value).toBe(false);
    }
    vi.stubEnv('VITE_R51_PROTOTYPE', '1');
    expect(r51PrototypeEnabled()).toBe(true);
  });

  it('is ignored by a production build even when the variable is set', () => {
    vi.stubEnv('VITE_R51_PROTOTYPE', '1');
    vi.stubEnv('PROD', true);
    expect(r51PrototypeEnabled()).toBe(false);
  });
});

describe('with the flag off (current behaviour)', () => {
  it.each([[undefined], ['1-in-production']])('keeps the generic upload and shows no modality entry points (%s)', async (mode) => {
    if (mode) { vi.stubEnv('VITE_R51_PROTOTYPE', '1'); vi.stubEnv('PROD', true); }
    const bodies = mockService({ kind_discordance: 'suspected', suspicion_codes: ['skin_name_hint_not_effective'], name_hints_matched: ['skin_wound'], modality_verification: 'not_verified', kind_explicit: null });
    const user = await openMcdt();
    expect(screen.queryByTestId('r51-modality-entry')).toBeNull();
    expect(screen.queryByText('Alterar modalidade')).toBeNull();
    await user.upload(screen.getByLabelText('Upload clínico') as HTMLInputElement, png());
    const card = await screen.findByTestId('mcdt-review-card');
    // 'Outro' is still the default category and nothing about the name hints is shown (no Phase B warning)
    expect(bodies[0]?.explicit_kind).toBeUndefined();
    expect(card).not.toHaveTextContent('suspected');
    expect(card).not.toHaveTextContent('skin_name_hint_not_effective');
  });
});

describe('with the flag on (inactive prototype)', () => {
  beforeEach(() => { vi.stubEnv('VITE_R51_PROTOTYPE', '1'); });

  it('starts without a category, offers one entry point per modality and blocks the file until one is chosen', async () => {
    mockService();
    await openMcdt();
    const entry = screen.getByTestId('r51-modality-entry');
    const buttons = within(entry).getAllByRole('button');
    expect(buttons).toHaveLength(MODALITIES.length);
    for (const button of buttons) expect(button).toHaveAttribute('aria-pressed', 'false');
    expect(within(entry).queryByLabelText('Upload clínico')).toBeNull();
    expect(within(entry).getByText(/Nenhuma modalidade selecionada/)).toBeInTheDocument();
  });

  it.each(MODALITIES.map(m => [m.id, m.kind, m.labelKey]))('%s: preview, specific confirm button, explicit category %s', async (_id, kind, labelKey) => {
    const bodies = mockService();
    const user = await openMcdt();
    const entry = screen.getByTestId('r51-modality-entry');
    await user.click(within(entry).getByRole('button', { name: String(labelKey), pressed: false }));
    const input = within(entry).getByLabelText('Upload clínico') as HTMLInputElement;
    const textual = kind === 'pdf_document'; // documents accept PDF/text only, so there is nothing to preview as an image
    await user.upload(input, textual ? new File(['informe sintético'], 'informe.txt', { type: 'text/plain' }) : png());
    if (textual) expect(within(entry).getByText(/Sem pré-visualização para este formato\./)).toBeInTheDocument();
    else expect(within(entry).getByRole('img')).toHaveAttribute('src', 'blob:preview');
    expect(within(entry).getByText(/Modalidade de destino:/)).toHaveTextContent(String(labelKey));
    expect(within(entry).getByText('A confirmação humana não verifica o conteúdo da imagem.')).toBeInTheDocument();
    await user.click(within(entry).getByRole('button', { name: `Confirmar e enviar como ${labelKey}` }));
    await screen.findByTestId('mcdt-review-card');
    expect(bodies).toHaveLength(1);
    expect(bodies[0]?.explicit_kind).toBe(kind);
    // the entry resets: no modality stays preselected for the next file
    expect(within(screen.getByTestId('r51-modality-entry')).queryByLabelText('Upload clínico')).toBeNull();
  });

  it('lets the user change the modality, which drops the chosen file and sends nothing', async () => {
    const bodies = mockService();
    const user = await openMcdt();
    const entry = screen.getByTestId('r51-modality-entry');
    await user.click(within(entry).getByRole('button', { name: 'ECG' }));
    await user.upload(within(entry).getByLabelText('Upload clínico') as HTMLInputElement, png());
    await user.click(within(entry).getByRole('button', { name: 'Alterar modalidade' }));
    expect(within(entry).queryByRole('img')).toBeNull();
    expect(within(entry).queryByLabelText('Upload clínico')).toBeNull();
    expect(bodies).toHaveLength(0);
  });

  it('shows no Phase B warning and never the filename-hint assessment, whatever the server records', async () => {
    mockService({ kind_discordance: 'suspected', suspicion_codes: ['skin_name_hint_not_effective'], name_hints_matched: ['skin_wound'], modality_verification: 'not_verified', kind_explicit: 'ecg' });
    const user = await openMcdt();
    const entry = screen.getByTestId('r51-modality-entry');
    await user.click(within(entry).getByRole('button', { name: 'ECG' }));
    await user.upload(within(entry).getByLabelText('Upload clínico') as HTMLInputElement, png());
    await user.click(within(entry).getByRole('button', { name: /Confirmar e enviar como ECG/ }));
    const card = await screen.findByTestId('mcdt-review-card');
    expect(card).not.toHaveTextContent('suspected');
    expect(card).not.toHaveTextContent('skin_name_hint_not_effective');
    expect(card).not.toHaveTextContent(/nome do ficheiro.*(pele|ferida)/i);
  });
});

describe('modality contract', () => {
  it('applies the dermatological filter to skin_wound alone', () => {
    expect(MODALITIES.filter(m => m.dermatologicFilter).map(m => m.kind)).toEqual(['skin_wound']);
    for (const kind of ['ecg', 'xray', 'pocus', 'pdf_document', 'other_image']) expect(appliesDermatologicFilter(kind), kind).toBe(false);
    expect(appliesDermatologicFilter('skin_wound')).toBe(true);
  });

  it('declares explicit, distinct categories and a fixed provisional limitation for every modality', () => {
    expect(new Set(MODALITIES.map(m => m.kind)).size).toBe(MODALITIES.length);
    for (const m of MODALITIES) {
      expect(m.limitationKey).toContain('{{modality}}');
      expect(m.limitationKey).toContain('redação médica pendente');
    }
  });
});
