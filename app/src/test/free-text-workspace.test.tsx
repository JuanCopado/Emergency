import { act, cleanup, fireEvent, render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import App from '../App';
import i18n from '../i18n';
import { SettingsProvider } from '../state/settings';
import { TEXT_WORKSPACE_COPY } from '../clinical-note/textWorkspaceCopy';

const SYNTHETIC = `Texto sintético sin datos reales.
Motivo de consulta: disnea de 2 días
Antecedentes: HTA, DM2
Alergias: ninguna conocida
Plan: observación y reevaluación`;

beforeEach(() => { localStorage.clear(); sessionStorage.clear(); });
afterEach(() => { cleanup(); vi.restoreAllMocks(); });

async function open() {
  await i18n.changeLanguage('es');
  render(<MemoryRouter initialEntries={['/clinical-note']}><SettingsProvider><App /></SettingsProvider></MemoryRouter>);
  const user = userEvent.setup();
  await user.click(await screen.findByTestId('note-tab-text'));
  return user;
}

it('separates original, proposal and final document and never edits the original', async () => {
  const user = await open();
  const original = screen.getByTestId('free-text-original') as HTMLTextAreaElement;
  fireEvent.change(original, { target: { value: SYNTHETIC } });
  await user.click(screen.getByTestId('free-text-structure'));
  expect(screen.getAllByRole('article').length).toBeGreaterThanOrEqual(4);
  await user.click(screen.getByTestId('free-text-generate'));
  const final = screen.getByTestId('free-text-final') as HTMLTextAreaElement;
  expect(final.value).toContain('disnea de 2 días');
  expect(final.value).toContain('HTA, DM2');
  fireEvent.change(final, { target: { value: `${final.value}\nEDITADO` } });
  expect(original.value).toBe(SYNTHETIC);
  expect(JSON.stringify(localStorage)).not.toContain('disnea');
  expect(sessionStorage.length).toBe(0);
});

it('applies to the note by appending, never overwriting, and is idempotent', async () => {
  const user = await open();
  await user.click(screen.getByTestId('note-tab-history'));
  fireEvent.change(screen.getByLabelText(/^Antecedentes/), { target: { value: 'Asma previa' } });
  await user.click(screen.getByTestId('note-tab-text'));
  fireEvent.change(screen.getByTestId('free-text-original'), { target: { value: SYNTHETIC } });
  await user.click(screen.getByTestId('free-text-structure'));
  await user.click(screen.getByTestId('free-text-apply'));
  await user.click(screen.getByTestId('free-text-apply'));
  await user.click(screen.getByTestId('note-tab-history'));
  expect((screen.getByLabelText(/^Antecedentes/) as HTMLTextAreaElement).value).toBe('Asma previa\nHTA, DM2');
  expect((screen.getByLabelText('Motivo de consulta') as HTMLTextAreaElement).value).toBe('disnea de 2 días');
});

it('separates applying the proposal from copying the editable document and explains the export boundary', async () => {
  const user = await open();
  fireEvent.change(screen.getByTestId('free-text-original'), { target: { value: 'Plan: observación sintética' } });
  await user.click(screen.getByTestId('free-text-structure'));
  await user.click(screen.getByTestId('free-text-generate'));
  const final = screen.getByTestId('free-text-final') as HTMLTextAreaElement;
  const finalCard = final.closest('div')!;
  expect(within(finalCard).queryByTestId('free-text-apply')).toBeNull();
  const proposalCard = screen.getByRole('heading', { name: '2 · Propuesta de estructura' }).parentElement!;
  expect(within(proposalCard).getByRole('button', { name: 'Aplicar propuesta a la nota' })).toBe(screen.getByTestId('free-text-apply'));
  expect(within(finalCard).getByText(TEXT_WORKSPACE_COPY.es.finalExportHint)).toBeInTheDocument();
  fireEvent.change(final, { target: { value: 'Documento libre sintético editado' } });
  const writeText = vi.spyOn(navigator.clipboard, 'writeText').mockResolvedValue();
  await user.click(screen.getByTestId('free-text-copy'));
  expect(writeText).toHaveBeenCalledWith('Documento libre sintético editado');
  await user.click(screen.getByTestId('free-text-apply'));
  await user.click(screen.getByTestId('note-tab-plan'));
  expect((screen.getByLabelText('Plan médico') as HTMLTextAreaElement).value).toBe('observación sintética');
});

it.each(['body', 'field', 'include'] as const)('invalidates the applied marker after changing %s', async change => {
  const user = await open();
  fireEvent.change(screen.getByTestId('free-text-original'), { target: { value: 'Antecedentes: asma sintética' } });
  await user.click(screen.getByTestId('free-text-structure'));
  await user.click(screen.getByTestId('free-text-apply'));
  const section = screen.getByRole('article', { name: 'Antecedentes' });
  expect(within(section).getByText('✓')).toBeInTheDocument();
  if (change === 'body') fireEvent.change(within(section).getByRole('textbox'), { target: { value: 'Antecedente sintético revisado' } });
  if (change === 'field') await user.selectOptions(within(section).getByRole('combobox'), 'plan');
  if (change === 'include') await user.click(within(section).getByRole('checkbox'));
  expect(within(section).queryByText('✓')).toBeNull();
});

it('does not structure an unfinished IME composition with Ctrl+Enter', async () => {
  const user = await open();
  const original = screen.getByTestId('free-text-original');
  fireEvent.change(original, { target: { value: 'Plan: texto sintético 未確定' } });
  fireEvent.compositionStart(original);
  fireEvent.keyDown(original, { key: 'Enter', ctrlKey: true, isComposing: true, keyCode: 229 });
  expect(screen.queryByTestId('free-text-sections')).toBeNull();
  fireEvent.compositionEnd(original);
  fireEvent.keyDown(original, { key: 'Enter', ctrlKey: true });
  expect(screen.getByTestId('free-text-sections')).toBeInTheDocument();
  await user.click(screen.getByTestId('free-text-generate'));
  expect((screen.getByTestId('free-text-final') as HTMLTextAreaElement).value).toContain('未確定');
});

it('requires refreshing a stale proposal without blocking the independent editable copy or export route', async () => {
  const user = await open();
  const original = screen.getByTestId('free-text-original');
  fireEvent.change(original, { target: { value: 'Antecedentes: Sin asma. 1,5 mg' } });
  await user.click(screen.getByTestId('free-text-structure'));
  await user.click(screen.getByTestId('free-text-generate'));
  fireEvent.change(original, { target: { value: 'Antecedentes: asma. 2 mg' } });
  expect(screen.getByTestId('free-text-apply')).toBeDisabled();
  expect(screen.getByTestId('free-text-generate')).toBeDisabled();
  expect(screen.getByTestId('free-text-copy')).toBeEnabled();
  expect(screen.getByRole('button', { name: TEXT_WORKSPACE_COPY.es.goExport })).toBeEnabled();
  expect((screen.getByTestId('free-text-final') as HTMLTextAreaElement).value).toContain('Sin asma. 1,5 mg');
  await user.click(screen.getByTestId('free-text-structure'));
  expect(screen.getByTestId('free-text-apply')).toBeEnabled();
  await user.click(screen.getByTestId('free-text-apply'));
  await user.click(screen.getByTestId('note-tab-history'));
  expect(screen.getByLabelText(/^Antecedentes/)).toHaveValue('asma. 2 mg');
});

it('removes copied feedback when the editable copy changes', async () => {
  const user = await open();
  fireEvent.change(screen.getByTestId('free-text-final'), { target: { value: 'Copia sintética 1' } });
  vi.spyOn(navigator.clipboard, 'writeText').mockResolvedValue();
  await user.click(screen.getByTestId('free-text-copy'));
  expect(screen.getByTestId('free-text-status')).toHaveTextContent(TEXT_WORKSPACE_COPY.es.copied);
  fireEvent.change(screen.getByTestId('free-text-final'), { target: { value: 'Copia sintética 2' } });
  expect(screen.getByTestId('free-text-status')).not.toHaveTextContent(TEXT_WORKSPACE_COPY.es.copied);
});

it.each(['resolve', 'reject'] as const)('ignores late clipboard %s feedback for a previous copy version', async outcome => {
  const user = await open();
  fireEvent.change(screen.getByTestId('free-text-final'), { target: { value: 'Copia sintética 1' } });
  let resolve!: () => void;
  let reject!: () => void;
  vi.spyOn(navigator.clipboard, 'writeText').mockImplementation(() => new Promise<void>((ok, fail) => { resolve = ok; reject = fail; }));
  await user.click(screen.getByTestId('free-text-copy'));
  fireEvent.change(screen.getByTestId('free-text-final'), { target: { value: 'Copia sintética 2' } });
  await act(async () => { if (outcome === 'resolve') resolve(); else reject(); });
  expect(screen.getByTestId('free-text-status')).not.toHaveTextContent(TEXT_WORKSPACE_COPY.es.copied);
  expect(screen.getByTestId('free-text-status')).not.toHaveTextContent(TEXT_WORKSPACE_COPY.es.copyFailed);
  expect(screen.getByTestId('free-text-final')).toHaveValue('Copia sintética 2');
});
