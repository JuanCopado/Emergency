// R13 · R5-1 policy layers 1-6, INACTIVE prototype. Synthetic upload only; the mocked service produces nothing clinical.
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import ClinicalNote from '../pages/ClinicalNote';
import ModalityEntry from '../clinical-note/ModalityEntry';
import { LIMITATION_TEXTS, MODALITIES, appliesDermatologicFilter, approvedLimitationText, limitationStatusFor, r51PrototypeEnabled, type LimitationEntry, type LimitationTable } from '../clinical-note/r51Prototype';
import { renderAt } from './render';
import approvedResource from '../clinical-note/r51-limitations.approved.json';

const sources = import.meta.glob('../clinical-note/{r51Prototype.ts,ModalityEntry.tsx}', {
  query: '?raw', import: 'default', eager: true,
}) as Record<string, string>;

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
    const textual = _id === 'document'; // documents accept PDF/text only, so there is nothing to preview as an image
    await user.upload(input, textual ? new File(['informe sintético'], 'informe.txt', { type: 'text/plain' }) : png());
    if (textual) expect(within(entry).getByText(/Sem pré-visualização para este formato\./)).toBeInTheDocument();
    else expect(within(entry).getByRole('img')).toHaveAttribute('src', 'blob:preview');
    expect(within(entry).getByText(/Modalidade de destino:/)).toHaveTextContent(String(labelKey));
    expect(within(entry).getByText('A confirmação humana não verifica o conteúdo da imagem.')).toBeInTheDocument();
    await user.click(within(entry).getByRole('button', { name: `Confirmar e enviar como ${labelKey}` }));
    await screen.findByTestId('mcdt-review-card');
    expect(bodies).toHaveLength(1);
    expect(bodies[0]?.explicit_kind).toBe(kind ?? undefined); // documents send no category: the server infers as it does today
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

  it('sends no category for a document, even if the classic selector was left on another one', async () => {
    const bodies = mockService();
    const user = await openMcdt();
    await user.click(screen.getByRole('button', { name: '+ ECG' })); // classic selector, not the prototype
    const entry = screen.getByTestId('r51-modality-entry');
    await user.click(within(entry).getByRole('button', { name: 'Documento (PDF ou texto)' }));
    await user.upload(within(entry).getByLabelText('Upload clínico') as HTMLInputElement, new File(['informe sintético'], 'informe.txt', { type: 'text/plain' }));
    await user.click(within(entry).getByRole('button', { name: /Confirmar e enviar como Documento/ }));
    await screen.findByTestId('mcdt-review-card');
    expect(bodies[0]?.explicit_kind).toBeUndefined();
  });

  it('never presents the human confirmation as a verification of the content', async () => {
    mockService();
    const user = await openMcdt();
    const entry = screen.getByTestId('r51-modality-entry');
    await user.click(within(entry).getByRole('button', { name: 'ECG' }));
    await user.upload(within(entry).getByLabelText('Upload clínico') as HTMLInputElement, png());
    expect(entry.textContent).toContain('não verifica o conteúdo');
    // only affirmative sentences count: «não é verificado automaticamente» is a negation, not a claim
    const affirmative = (entry.textContent ?? '').split(/[.;:]/).filter(sentence => !/\bnão\b/i.test(sentence));
    expect(affirmative.join('. ')).not.toMatch(/\b(verificad|validad|comprovad|certificad|aprovad)[oa]s?\b/i);
  });
});

describe('what the prototype source does not contain', () => {
  const read = (name: string) => sources[`../clinical-note/${name}`] ?? '';

  it.each(['r51Prototype.ts', 'ModalityEntry.tsx'])('%s has no visual classification, no abstention, no Phase B and no network', (name) => {
    expect(read(name).length, `${name} not found`).toBeGreaterThan(100);
    const code = read(name).replace(/\/\*[\s\S]*?\*\//g, '').replace(/^\s*\/\/.*$/gm, '');
    for (const forbidden of [/getImageData|ImageData|<canvas|document\.createElement\(.canvas/i, /tensorflow|onnx|classif/i,
      /abstain|abstenc|abstención/i, /kind_assessment|kind_discordance|suspicion/i, /fetch\(|XMLHttpRequest|\/api\//])
      expect(code, `${name}: ${forbidden}`).not.toMatch(forbidden);
  });
});

describe('while a request is in flight', () => {
  it.each([[true], [false]])('modality buttons are disabled only when busy (busy=%s)', (busy) => {
    render(<ModalityEntry busy={busy} language="es" ui={(key) => key} onConfirm={() => undefined} />);
    for (const button of within(screen.getByTestId('r51-modality-entry')).getAllByRole('button')) {
      if (busy) expect(button).toBeDisabled();
      else expect(button).toBeEnabled();
    }
  });
});

describe('modality contract', () => {
  it('applies the dermatological filter to skin_wound alone', () => {
    expect(MODALITIES.filter(m => m.dermatologicFilter).map(m => m.kind)).toEqual(['skin_wound']);
    for (const kind of ['ecg', 'xray', 'pocus', 'pdf_document', 'other_image']) expect(appliesDermatologicFilter(kind), kind).toBe(false);
    expect(appliesDermatologicFilter('skin_wound')).toBe(true);
  });

  it('declares explicit, distinct categories and the provisional fallback text for every modality', () => {
    expect(new Set(MODALITIES.map(m => m.kind)).size).toBe(MODALITIES.length); // null (document) counts once
    for (const m of MODALITIES) {
      expect(m.limitationKey).toContain('{{modality}}');
      expect(m.limitationKey).toContain('redação médica pendente');
    }
  });
});

// Independent literal copy of the texts approved in DEC-CLIN-R14-01: any edit of the resource fails here.
const APPROVED_TEXTS = {
  "skin_wound": {
    "es": "Descripción superficial limitada a la foto según la modalidad elegida. No verifica la modalidad ni descarta infección profunda, isquemia o lesión interna. Requiere examen presencial.",
    "pt": "Descrição superficial limitada à fotografia na modalidade selecionada. Não verifica a modalidade nem exclui infeção profunda, isquemia ou lesão interna. Requer avaliação presencial.",
    "en": "Superficial visual description only for the selected modality. Does not verify modality or rule out deep infection, ischemia, or internal injury. In-person exam required."
  },
  "ecg": {
    "es": "Apoyo limitado al trazado de ECG según la modalidad elegida. No verifica la modalidad ni descarta síndrome coronario agudo ni otras patologías. Correlacionar con clínica y ECG seriados.",
    "pt": "Apoio limitado ao traçado de ECG na modalidade selecionada. Não verifica a modalidade nem exclui síndrome coronária aguda nem outras patologias. Correlacionar com a clínica e ECG seriados.",
    "en": "Support limited to the submitted ECG tracing for the selected modality. Does not verify modality or rule out acute coronary syndrome or other conditions. Correlate clinically and with serial ECGs."
  },
  "xray": {
    "es": "Apoyo limitado a hallazgos visibles en la radiografía según la modalidad elegida. No verifica la modalidad ni descarta patología oculta o fuera de proyección. Correlacionar clínicamente.",
    "pt": "Apoio limitado aos achados visíveis na radiografia na modalidade selecionada. Não verifica a modalidade nem exclui patologia oculta ou fora de incidência. Correlacionar clinicamente.",
    "en": "Support limited to visible findings on the radiograph for the selected modality. Does not verify modality or rule out occult or out-of-view pathology. Correlate clinically."
  },
  "pocus": {
    "es": "Apoyo limitado al plano ecográfico aportado según la modalidad elegida. No verifica la modalidad, no sustituye el examen dinámico completo ni descarta patología fuera de ventana.",
    "pt": "Apoio limitado ao plano ecográfico enviado na modalidade selecionada. Não verifica a modalidade, não substitui o exame dinâmico completo nem exclui patologia fora da janela.",
    "en": "Support limited to the submitted ultrasound view for the selected modality. Does not verify modality, replace a full dynamic exam, or rule out out-of-plane pathology."
  },
  "document": {
    "es": "Extracción limitada al texto legible del documento según la modalidad elegida. No verifica el tipo de documento ni infiere datos omitidos o ilegibles. Confirmar con el registro original.",
    "pt": "Extração limitada ao texto legível do documento na modalidade selecionada. Não verifica o tipo de documento nem infere dados omitidos ou ilegíveis. Confirmar no registo original.",
    "en": "Extraction limited to legible text in the document for the selected modality. Does not verify document type or infer missing or illegible data. Confirm against the original record."
  }
};

describe('approved limitation texts (DEC-CLIN-R14-01)', () => {
  const ids = MODALITIES.map(m => m.id);

  it('the resource preserves the approved wording literally, for the three languages', () => {
    expect(approvedResource.texts).toEqual(APPROVED_TEXTS);
    expect(approvedResource.decision).toBe('DEC-CLIN-R14-01');
    expect(approvedResource.approved_on).toBe('2026-11-22');
    expect(approvedResource.scope).toBe('INACTIVE_PROTOTYPE_AND_HUMAN_FACTORS_TESTS_ONLY');
  });

  it('every modality is approved and resolves to its exact text per language (zh shows English)', () => {
    for (const id of ids) {
      expect(limitationStatusFor(id)).toBe('APPROVED');
      for (const lang of ['es', 'pt', 'en'] as const) expect(approvedLimitationText(id, lang), `${id}/${lang}`).toBe(APPROVED_TEXTS[id][lang]);
      expect(approvedLimitationText(id, 'zh')).toBe(APPROVED_TEXTS[id].en);
    }
  });

  it('a modality without complete approval falls back to the provisional text (fail-closed)', () => {
    const base = (entry: LimitationEntry): LimitationTable => ({ ...LIMITATION_TEXTS, ecg: entry });
    const texts = APPROVED_TEXTS.ecg;
    const ok = { decision: 'DEC-TEST', date: '2026-11-22' };
    const bad: LimitationEntry[] = [
      { status: 'PROVISIONAL' },
      { status: 'PROVISIONAL', approvedTexts: texts, approval: ok },
      { status: 'APPROVED', approvedTexts: texts },
      { status: 'APPROVED', approvedTexts: texts, approval: { decision: '', date: '2026-11-22' } },
      { status: 'APPROVED', approvedTexts: texts, approval: { decision: 'D', date: '22/11/2026' } },
      { status: 'APPROVED', approvedTexts: { ...texts, pt: '' }, approval: ok },
    ];
    for (const entry of bad) {
      expect(approvedLimitationText('ecg', 'es', base(entry))).toBeNull();
      expect(limitationStatusFor('ecg', base(entry))).toBe('PROVISIONAL');
    }
  });

  it('no approved text claims the modality was verified, and each says what it does not rule out', () => {
    for (const id of ids) for (const lang of ['es', 'pt', 'en'] as const) {
      const text = APPROVED_TEXTS[id][lang];
      expect(text, `${id}/${lang}`).toMatch(/No verifica|Não verifica|Does not verify/);
    }
  });
});

describe('approved text on screen (flag on)', () => {
  afterEach(() => { vi.unstubAllEnvs(); });

  it('shows the exact approved text of the chosen modality and never in production', async () => {
    vi.stubEnv('VITE_R51_PROTOTYPE', '1');
    const user = userEvent.setup();
    render(<ModalityEntry busy={false} language="pt" ui={(k: string) => k} onConfirm={() => undefined} />);
    for (const m of MODALITIES) {
      await user.click(screen.getByRole('button', { name: m.labelKey }));
      expect(screen.getByText(APPROVED_TEXTS[m.id].pt)).toBeTruthy();
    }
  });
});

describe('object URLs and double submission (ModalityEntry)', () => {
  const png = () => new File([new Uint8Array([1, 2, 3])], 'a.png', { type: 'image/png' });

  it('creates one object URL per previewed file and revokes it on change, reset and unmount', async () => {
    const create = vi.fn().mockReturnValueOnce('blob:one').mockReturnValueOnce('blob:two');
    const revoke = vi.fn();
    vi.stubGlobal('URL', Object.assign(URL, { createObjectURL: create, revokeObjectURL: revoke }));
    const user = userEvent.setup();
    const { unmount } = render(<ModalityEntry busy={false} language="es" ui={(k: string) => k} onConfirm={() => undefined} />);
    await user.click(screen.getByRole('button', { name: 'ECG' }));
    const input = screen.getByLabelText('Upload clínico');
    await user.upload(input, png());
    expect(create).toHaveBeenCalledTimes(1);
    await user.upload(input, png());
    expect(revoke).toHaveBeenCalledWith('blob:one');
    unmount();
    expect(revoke).toHaveBeenCalledWith('blob:two');
    expect(create).toHaveBeenCalledTimes(2);
    vi.unstubAllGlobals();
  });

  it('confirming sends once: the confirm button disappears after the first click', async () => {
    const send = vi.fn();
    const user = userEvent.setup();
    render(<ModalityEntry busy={false} language="es" ui={(k: string) => k} onConfirm={send} />);
    await user.click(screen.getByRole('button', { name: 'ECG' }));
    await user.upload(screen.getByLabelText('Upload clínico'), png());
    const confirm = screen.getByRole('button', { name: /Confirmar e enviar como/ });
    await user.dblClick(confirm);
    expect(send).toHaveBeenCalledTimes(1);
    expect(screen.queryByRole('button', { name: /Confirmar e enviar como/ })).toBeNull();
  });
});
