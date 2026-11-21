import { act, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, expect, it, vi } from 'vitest';
import i18n from '../i18n';
import ClinicalNote from '../pages/ClinicalNote';
import { renderAt } from './render';

afterEach(() => vi.restoreAllMocks());

it.each([
  ['es', 'es-ES'], ['pt', 'pt-PT'], ['en', 'en'], ['zh', 'zh'],
])('uses the %s interface language for the note request', async (language, payloadLanguage) => {
  const user = userEvent.setup();
  let submitted: Record<string, unknown> | undefined;
  vi.spyOn(globalThis, 'fetch').mockImplementation(async (_url, options) => {
    submitted = JSON.parse(String(options?.body));
    return Response.json({ blocked: true, issues: [{ message: 'Synthetic response' }] });
  });
  await renderAt('/clinical-note', [{ path: '/clinical-note', element: <ClinicalNote /> }], language);
  const ui = (text: string) => String(i18n.t(text, { ns: 'clinicalUi', keySeparator: false, nsSeparator: false }));
  await user.type(screen.getByLabelText(ui('Motivo de consulta')), 'Possible ST elevation. Nausea.');
  await user.click(screen.getByRole('button', { name: ui('Apoio diagnóstico') }));
  await user.click(screen.getByRole('button', { name: ui('Atualizar apoio diagnóstico') }));
  await waitFor(() => expect(submitted).toMatchObject({
    note: {
      language: payloadLanguage,
      history: { chief_complaint: 'Possible ST elevation. Nausea.' },
    },
  }));
  expect(await screen.findByText('Synthetic response')).toBeInTheDocument();
});

it('requires a diagnostic refresh after a language change while retaining the written note', async () => {
  const user = userEvent.setup();
  const submittedLanguages: string[] = [];
  vi.spyOn(globalThis, 'fetch').mockImplementation(async (_url, options) => {
    const payload = JSON.parse(String(options?.body));
    submittedLanguages.push(payload.note.language);
    return Response.json({
      blocked: false, issues: [], signals: [], medication_safety_gate: null,
      assessment: {
        problem_representation: '', active_problems: [], likely_diagnoses: [],
        differential_diagnoses: [], must_not_miss: [], suggested_tests: [],
        treatment_suggestions: [], disposition: [], reassessment: [],
        contradictions_to_clarify: [], limitations: ['Synthetic limitation'],
      },
    });
  });
  await renderAt('/clinical-note', [{ path: '/clinical-note', element: <ClinicalNote /> }], 'es');
  const ui = (text: string) => String(i18n.t(text, { ns: 'clinicalUi', keySeparator: false, nsSeparator: false }));
  await user.type(screen.getByLabelText(ui('Motivo de consulta')), 'Synthetic unchanged text');
  await user.click(screen.getByRole('button', { name: ui('Apoio diagnóstico') }));
  await user.click(screen.getByRole('button', { name: ui('Atualizar apoio diagnóstico') }));
  expect(await screen.findByText('Synthetic limitation')).toBeInTheDocument();
  await user.click(screen.getByRole('button', { name: ui('Exportar') }));
  for (const box of screen.getAllByRole('checkbox')) await user.click(box);
  expect(screen.getByRole('button', { name: 'Word (.docx)' })).toBeEnabled();
  await act(async () => { await i18n.changeLanguage('en'); });
  expect(submittedLanguages).toEqual(['es-ES']);
  expect(screen.getByText(ui('O idioma mudou; atualize o apoio diagnóstico antes de exportar.'))).toBeInTheDocument();
  for (const box of screen.getAllByRole('checkbox')) {
    if (!(box as HTMLInputElement).checked) await user.click(box);
  }
  expect(screen.getByRole('button', { name: 'Word (.docx)' })).toBeDisabled();
  await user.click(screen.getByRole('button', { name: ui('História') }));
  expect(screen.getByLabelText(ui('Motivo de consulta'))).toHaveValue('Synthetic unchanged text');
  await user.click(screen.getByRole('button', { name: ui('Apoio diagnóstico') }));
  await user.click(screen.getByRole('button', { name: ui('Atualizar apoio diagnóstico') }));
  await waitFor(() => expect(submittedLanguages).toEqual(['es-ES', 'en']));
  await user.click(screen.getByRole('button', { name: ui('Exportar') }));
  expect(screen.queryByText(ui('O idioma mudou; atualize o apoio diagnóstico antes de exportar.'))).not.toBeInTheDocument();
  for (const box of screen.getAllByRole('checkbox')) {
    if (!(box as HTMLInputElement).checked) await user.click(box);
  }
  expect(screen.getByRole('button', { name: 'Word (.docx)' })).toBeEnabled();
});
