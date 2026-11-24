import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import LabModalityEntry from './LabModalityEntry';
import { labEntryIsE1, recoveryKey, resolveLabLocale, type Layer7Verdict } from './layer7Lab';

const ui = (key: string, values?: Record<string, string | number>) => (values ? `${key}${JSON.stringify(values)}` : key);
const TEXT = { 'MSG_T7_NO_MODALITY': 'Texto aprobado 1', 'MSG_T7_CORRUPT_FILE': 'Texto aprobado 3' };

function verdict(partial: Partial<Layer7Verdict>): Layer7Verdict {
  return { mode: 'SIMULATED_LAB_HARNESS_ONLY', abstains: false, trigger_id: null, message_id: null, message_text: null, force_send_available: false, ...partial };
}

function mockEvaluator(answer: (body: { ui_modality: string | null }) => Layer7Verdict | 'fail') {
  const calls: unknown[] = [];
  vi.spyOn(globalThis, 'fetch').mockImplementation(async (_input, init) => {
    const payload = JSON.parse(String(init?.body));
    calls.push(payload);
    const result = answer(payload);
    if (result === 'fail') return new Response('{}', { status: 503 });
    return new Response(JSON.stringify(result), { status: 200, headers: { 'Content-Type': 'application/json' } });
  });
  return calls;
}

const png = () => new File([new Uint8Array([137, 80, 78, 71, 13, 10, 26, 10])], 'captura.png', { type: 'image/png' });

beforeEach(() => { (window as unknown as { __LAB_LAYER7_LOG__?: unknown }).__LAB_LAYER7_LOG__ = []; });
afterEach(() => { vi.restoreAllMocks(); window.history.replaceState({}, '', '/'); });

describe('lab Layer 7 entry (arm B, simulated harness)', () => {
  it('E1: with ?lab_entry=e1 the file input exists before any modality and the T7-01 abstention shows the approved text with focus and ARIA', async () => {
    window.history.replaceState({}, '', '/?lab_entry=e1');
    expect(labEntryIsE1(window.location.search)).toBe(true);
    const calls = mockEvaluator(() => verdict({ abstains: true, trigger_id: 'T7-01_UNDECLARED_MODALITY', message_id: 'MSG_T7_NO_MODALITY', message_text: TEXT.MSG_T7_NO_MODALITY }));
    const onConfirm = vi.fn();
    const user = userEvent.setup();
    render(<LabModalityEntry busy={false} ui={ui} language="es" onConfirm={onConfirm} />);
    await user.upload(screen.getByLabelText('Upload clínico') as HTMLInputElement, png());
    const banner = await screen.findByTestId('lab-layer7-banner');
    expect(banner).toHaveAttribute('role', 'alert');
    expect(banner).toHaveAttribute('aria-live', 'assertive');
    expect(banner).toHaveTextContent(TEXT.MSG_T7_NO_MODALITY);
    expect(banner).toHaveFocus();
    expect((calls[0] as { ui_modality: unknown }).ui_modality).toBeNull();
    expect(screen.queryByText(/Confirmar e enviar/)).toBeNull();                       // no way to send
    expect(within(banner).getAllByRole('button')).toHaveLength(1);                      // one recovery control, no force-send
    expect(onConfirm).not.toHaveBeenCalled();
    const log = (window as unknown as { __LAB_LAYER7_LOG__: { type: string }[] }).__LAB_LAYER7_LOG__.map(e => e.type);
    expect(log).toEqual(expect.arrayContaining(['file_selected', 'layer7_banner_rendered']));
    const selected = (window as unknown as { __LAB_LAYER7_LOG__: { type: string; detail: Record<string, unknown> }[] }).__LAB_LAYER7_LOG__.find(e => e.type === 'file_selected');
    expect(selected?.detail.viewport_width_px).toBe(window.innerWidth);                 // device is recorded per trial, never per period
    expect(selected?.detail.e1_entry).toBe(true);
  });

  it('E1 recovery: choosing a valid modality re-evaluates the SAME file and the abstention disappears', async () => {
    window.history.replaceState({}, '', '/?lab_entry=e1');
    mockEvaluator(body => body.ui_modality === null
      ? verdict({ abstains: true, trigger_id: 'T7-01_UNDECLARED_MODALITY', message_id: 'MSG_T7_NO_MODALITY', message_text: TEXT.MSG_T7_NO_MODALITY })
      : verdict({}));
    const onConfirm = vi.fn();
    const user = userEvent.setup();
    render(<LabModalityEntry busy={false} ui={ui} language="es" onConfirm={onConfirm} />);
    await user.upload(screen.getByLabelText('Upload clínico') as HTMLInputElement, png());
    await screen.findByTestId('lab-layer7-banner');
    await user.click(screen.getByRole('button', { name: 'ECG' }));
    expect(await screen.findByText(/Confirmar e enviar como/)).toBeInTheDocument();
    expect(screen.queryByTestId('lab-layer7-banner')).toBeNull();
    const log = (window as unknown as { __LAB_LAYER7_LOG__: { type: string; detail: Record<string, unknown> }[] }).__LAB_LAYER7_LOG__;
    expect(log.some(e => e.type === 'modality_selected' && e.detail.origin === 'after_layer7')).toBe(true);
    expect(log.some(e => e.type === 'recovery_action' && e.detail.action === 'change_modality')).toBe(true);
  });

  it('without ?lab_entry=e1 the approved flow is kept: no file input until a modality is chosen', () => {
    mockEvaluator(() => verdict({}));
    render(<LabModalityEntry busy={false} ui={ui} language="es" onConfirm={vi.fn()} />);
    expect(screen.queryByLabelText('Upload clínico')).toBeNull();
  });

  it('T7-03 offers a single "upload intact copy" control that discards the file; there is never a force-send control', async () => {
    mockEvaluator(() => verdict({ abstains: true, trigger_id: 'T7-03_CORRUPT_UNPROCESSABLE', message_id: 'MSG_T7_CORRUPT_FILE', message_text: TEXT.MSG_T7_CORRUPT_FILE }));
    const user = userEvent.setup();
    render(<LabModalityEntry busy={false} ui={ui} language="en" onConfirm={vi.fn()} />);
    await user.click(screen.getByRole('button', { name: 'ECG' }));
    await user.upload(screen.getByLabelText('Upload clínico') as HTMLInputElement, png());
    const banner = await screen.findByTestId('lab-layer7-banner');
    const controls = within(banner).getAllByRole('button');
    expect(controls).toHaveLength(1);
    expect(controls[0] as HTMLElement).toHaveTextContent('Upload intact copy / Retake capture');
    await user.click(controls[0] as HTMLElement);
    expect(screen.queryByTestId('lab-layer7-banner')).toBeNull();
    expect(screen.queryByRole('button', { name: /forzar|force|forçar/i })).toBeNull();
  });

  it('fails closed: an unavailable evaluator blocks the upload instead of letting it through', async () => {
    mockEvaluator(() => 'fail');
    const onConfirm = vi.fn();
    const user = userEvent.setup();
    render(<LabModalityEntry busy={false} ui={ui} language="es" onConfirm={onConfirm} />);
    await user.click(screen.getByRole('button', { name: 'ECG' }));
    await user.upload(screen.getByLabelText('Upload clínico') as HTMLInputElement, png());
    expect(await screen.findByTestId('lab-layer7-failure')).toBeInTheDocument();
    expect(screen.queryByText(/Confirmar e enviar como/)).toBeNull();
    expect(onConfirm).not.toHaveBeenCalled();
  });

  it('a valid ECG shows the confirmation (no false blocking) and sends the declared kind', async () => {
    mockEvaluator(() => verdict({}));
    const onConfirm = vi.fn();
    const user = userEvent.setup();
    render(<LabModalityEntry busy={false} ui={ui} language="es" onConfirm={onConfirm} />);
    await user.click(screen.getByRole('button', { name: 'ECG' }));
    await user.upload(screen.getByLabelText('Upload clínico') as HTMLInputElement, png());
    await user.click(await screen.findByText(/Confirmar e enviar como/));
    expect(onConfirm).toHaveBeenCalledWith(expect.any(File), 'ecg');
    const log = (window as unknown as { __LAB_LAYER7_LOG__: { type: string }[] }).__LAB_LAYER7_LOG__.map(e => e.type);
    expect(log).toContain('confirm_clicked');
  });

  it('T7-04 maps to the right recovery set by message id', () => {
    expect(recoveryKey(verdict({ abstains: true, trigger_id: 'T7-04_FORMAT_CONTAINER_MISMATCH', message_id: 'MSG_T7_UNSUPPORTED_FORMAT', message_text: 'x' }))).toBe('T7-04A');
    expect(recoveryKey(verdict({ abstains: true, trigger_id: 'T7-04_FORMAT_CONTAINER_MISMATCH', message_id: 'MSG_T7_INCOMPATIBLE_MODALITY', message_text: 'x' }))).toBe('T7-04B');
    for (const variant of [null, 'pt-PT', 'pt-BR'] as const) {
      const format = verdict({ abstains: true, trigger_id: 'T7-04_FORMAT_CONTAINER_MISMATCH', message_id: 'MSG_T7_D', variant });
      expect(recoveryKey(format)).toBe(variant === 'pt-BR' ? 'T7-04A' : 'T7-04B');
      expect(recoveryKey({ ...format, message_id: 'MSG_T7_B' })).toBe('T7-04B');
    }
  });
});

describe('lab regional Portuguese (explicit, never inferred)', () => {
  const log = () => (window as unknown as { __LAB_LAYER7_LOG__: { type: string; detail: Record<string, unknown> }[] }).__LAB_LAYER7_LOG__;

  it('resolves only an explicit pt-PT or pt-BR on a pt UI; generic pt is never upgraded', () => {
    expect(resolveLabLocale('?lab_locale=pt-PT', 'pt')).toEqual({ requested: 'pt-PT', variant: 'pt-PT', status: 'OK' });
    expect(resolveLabLocale('', 'pt')).toEqual({ requested: null, variant: null, status: 'OK' });
    expect(resolveLabLocale('?lab_locale=pt-BR', 'pt')).toEqual({ requested: 'pt-BR', variant: 'pt-BR', status: 'OK' });
    expect(resolveLabLocale('?lab_locale=pt-BR', 'es').status).toBe('UNSUPPORTED');       // conflicts with the UI language
    expect(resolveLabLocale('?lab_locale=pt-AO', 'pt')).toEqual({ requested: 'pt-AO', variant: null, status: 'UNSUPPORTED' });
    expect(resolveLabLocale('?lab_locale=PT-BR', 'pt').status).toBe('UNSUPPORTED');       // exact code only
    expect(resolveLabLocale('?lab_locale=pt-PT', 'es').status).toBe('UNSUPPORTED');       // conflicts with the UI language: no silent substitution
    expect(resolveLabLocale('?lab_locale=pt', 'pt')).toEqual({ requested: 'pt', variant: null, status: 'UNSUPPORTED' });
  });

  it('pt-PT is recorded in the UI log together with the language', () => {
    window.history.replaceState({}, '', '/?lab_locale=pt-PT');
    render(<LabModalityEntry busy={false} ui={ui} language="pt" onConfirm={vi.fn()} />);
    expect(log().find(e => e.type === 'locale_resolved')?.detail).toEqual({ language: 'pt', lab_locale: 'pt-PT', variant: 'pt-PT', status: 'OK' });
  });

  it('generic pt without the parameter records a null variant', () => {
    render(<LabModalityEntry busy={false} ui={ui} language="pt" onConfirm={vi.fn()} />);
    expect(log().find(e => e.type === 'locale_resolved')?.detail).toMatchObject({ language: 'pt', variant: null, status: 'OK' });
  });
  it('pt-BR on a non-pt UI and an unknown regional code fail closed: notice, no file input and no selector', () => {
    for (const [language, search] of [['es', '/?lab_locale=pt-BR&lab_entry=e1'], ['pt', '/?lab_locale=pt-AO&lab_entry=e1'], ['pt', '/?lab_locale=pt&lab_entry=e1']] as const) {
      window.history.replaceState({}, '', search);
      const view = render(<LabModalityEntry busy={false} ui={ui} language={language} onConfirm={vi.fn()} />);
      expect(screen.getByTestId('lab-locale-unsupported')).toHaveAttribute('role', 'alert');
      expect(screen.queryByLabelText('Upload clínico')).toBeNull();
      expect(log().at(-1)?.detail).toMatchObject({ status: 'UNSUPPORTED' });
      view.unmount();
    }
  });

  it('pt-BR is recorded as an observable locale_resolved event and enables the entry', () => {
    window.history.replaceState({}, '', '/?lab_locale=pt-BR&lab_entry=e1');
    render(<LabModalityEntry busy={false} ui={ui} language="pt" onConfirm={vi.fn()} />);
    expect(log().find(e => e.type === 'locale_resolved')?.detail).toEqual({ language: 'pt', lab_locale: 'pt-BR', variant: 'pt-BR', status: 'OK' });
    expect(screen.getByLabelText('Upload clínico')).toBeInTheDocument();
    expect(screen.queryByTestId('lab-locale-unsupported')).toBeNull();
  });
});

describe('lab pt-BR approved texts and controls (MED-DEC-R39-PTBR-FINAL)', () => {
  const T1 = 'Não foi selecionada uma modalidade permitida. Este sistema não identifica automaticamente o tipo de imagem ou documento. Selecione a modalidade adequada antes de continuar.';
  const T3 = 'O arquivo está danificado ou não pode ser processado tecnicamente. Não foi realizada nenhuma avaliação clínica. Repita a captura ou envie uma cópia íntegra.';
  const T4 = 'O formato do arquivo não é suportado por esta função. O conteúdo não foi analisado nem se exclui nenhuma condição. Converta ou reenvie em um formato compatível.';
  const log = () => (window as unknown as { __LAB_LAYER7_LOG__: { type: string; detail: Record<string, unknown> }[] }).__LAB_LAYER7_LOG__;

  it('sends variant pt-BR to the evaluator and shows the literal approved T1 text with the literal control', async () => {
    window.history.replaceState({}, '', '/?lab_locale=pt-BR&lab_entry=e1');
    const calls = mockEvaluator(() => verdict({ abstains: true, trigger_id: 'T7-01_UNDECLARED_MODALITY', message_id: 'MSG_T7_A', message_text: T1, variant: 'pt-BR' }));
    const onConfirm = vi.fn();
    const user = userEvent.setup();
    render(<LabModalityEntry busy={false} ui={ui} language="pt" onConfirm={onConfirm} />);
    await user.upload(screen.getByLabelText('Upload clínico') as HTMLInputElement, png());
    const banner = await screen.findByTestId('lab-layer7-banner');
    expect(banner).toHaveTextContent(T1);
    expect(calls[0]).toMatchObject({ language: 'pt', variant: 'pt-BR' });
    const controls = within(banner).getAllByRole('button');
    expect(controls.map(c => c.textContent)).toEqual(['Selecionar modalidade']);
    expect(screen.queryByText(/Confirmar e enviar/)).toBeNull();                       // no way to send
    expect(onConfirm).not.toHaveBeenCalled();
  });

  it('T3 offers "Substituir arquivo", discards the file and never a force-send control', async () => {
    window.history.replaceState({}, '', '/?lab_locale=pt-BR');
    mockEvaluator(() => verdict({ abstains: true, trigger_id: 'T7-03_CORRUPT_UNPROCESSABLE', message_id: 'MSG_T7_C', message_text: T3, variant: 'pt-BR' }));
    const user = userEvent.setup();
    render(<LabModalityEntry busy={false} ui={ui} language="pt" onConfirm={vi.fn()} />);
    await user.click(screen.getByRole('button', { name: 'ECG' }));
    await user.upload(screen.getByLabelText('Upload clínico') as HTMLInputElement, png());
    const banner = await screen.findByTestId('lab-layer7-banner');
    expect(banner).toHaveTextContent(T3);
    const controls = within(banner).getAllByRole('button');
    expect(controls.map(c => c.textContent)).toEqual(['Substituir arquivo']);
    await user.click(controls[0] as HTMLElement);
    expect(screen.queryByTestId('lab-layer7-banner')).toBeNull();
    expect(screen.queryByRole('button', { name: /forzar|force|forçar|forçar/i })).toBeNull();
  });

  it('T4 (real message id MSG_T7_D) keeps the abstention with literal controls', async () => {
    window.history.replaceState({}, '', '/?lab_locale=pt-BR');
    mockEvaluator(() => verdict({ abstains: true, trigger_id: 'T7-04_FORMAT_CONTAINER_MISMATCH', message_id: 'MSG_T7_D', message_text: T4, variant: 'pt-BR' }));
    const user = userEvent.setup();
    render(<LabModalityEntry busy={false} ui={ui} language="pt" onConfirm={vi.fn()} />);
    await user.click(screen.getByRole('button', { name: 'ECG' }));
    await user.upload(screen.getByLabelText('Upload clínico') as HTMLInputElement, png());
    const banner = await screen.findByTestId('lab-layer7-banner');
    expect(banner).toHaveTextContent(T4);
    const labels = within(banner).getAllByRole('button').map(c => c.textContent);
    expect(labels).toEqual(['Enviar arquivo']);
  });

  it('an evaluator answer without variant pt-BR is rejected: fail closed with "Envio bloqueado" and no European text is shown', async () => {
    window.history.replaceState({}, '', '/?lab_locale=pt-BR');
    mockEvaluator(() => verdict({ abstains: true, trigger_id: 'T7-03_CORRUPT_UNPROCESSABLE', message_id: 'MSG_T7_C', message_text: 'O ficheiro está danificado', variant: 'pt-PT' }));
    const onConfirm = vi.fn();
    const user = userEvent.setup();
    render(<LabModalityEntry busy={false} ui={ui} language="pt" onConfirm={onConfirm} />);
    await user.click(screen.getByRole('button', { name: 'ECG' }));
    await user.upload(screen.getByLabelText('Upload clínico') as HTMLInputElement, png());
    expect(await screen.findByTestId('lab-layer7-failure')).toHaveTextContent('Envio bloqueado');
    expect(screen.queryByTestId('lab-layer7-banner')).toBeNull();
    expect(screen.queryByText(/ficheiro/)).toBeNull();
    expect(onConfirm).not.toHaveBeenCalled();
    expect(log().some(e => e.type === 'evaluator_failure')).toBe(true);
  });

  it('a valid file in pt-BR shows the "Verifique o arquivo na tela" preview and still sends only through confirmation', async () => {
    window.history.replaceState({}, '', '/?lab_locale=pt-BR');
    mockEvaluator(() => verdict({ variant: 'pt-BR' }));
    const onConfirm = vi.fn();
    const user = userEvent.setup();
    render(<LabModalityEntry busy={false} ui={ui} language="pt" onConfirm={onConfirm} />);
    await user.click(screen.getByRole('button', { name: 'ECG' }));
    await user.upload(screen.getByLabelText('Upload clínico') as HTMLInputElement, png());
    expect(await screen.findByRole('region', { name: 'Verifique o arquivo na tela' })).toBeInTheDocument();
    await user.click(screen.getByText(/Confirmar e enviar como/));
    expect(onConfirm).toHaveBeenCalledWith(expect.any(File), 'ecg');
  });

  it('pt-PT is unchanged: its request carries no variant and its controls stay European', async () => {
    window.history.replaceState({}, '', '/?lab_locale=pt-PT&lab_entry=e1');
    const calls = mockEvaluator(() => verdict({ abstains: true, trigger_id: 'T7-01_UNDECLARED_MODALITY', message_id: 'MSG_T7_A', message_text: 'Texto europeu' }));
    const user = userEvent.setup();
    render(<LabModalityEntry busy={false} ui={ui} language="pt" onConfirm={vi.fn()} />);
    await user.upload(screen.getByLabelText('Upload clínico') as HTMLInputElement, png());
    const banner = await screen.findByTestId('lab-layer7-banner');
    expect(Object.keys(calls[0] as object).sort()).toEqual(['body', 'language', 'ui_modality']);
    expect(within(banner).getAllByRole('button').map(c => c.textContent)).toEqual(['Escolher modalidade']);
  });
});
