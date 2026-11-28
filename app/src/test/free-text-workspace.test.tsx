import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import App from '../App';
import i18n from '../i18n';
import { SettingsProvider } from '../state/settings';

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
