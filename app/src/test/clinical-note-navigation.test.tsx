import { act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Link, MemoryRouter } from 'react-router-dom';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import App from '../App';
import i18n from '../i18n';
import { SettingsProvider } from '../state/settings';
import * as api from '../clinical-note/api';
import type { PreparedUpload } from '../clinical-note/types';

// Keep the real App routes and the note's real link; extraction is outside this test.
vi.mock('../pages/BloodGas', () => ({ default: () => <Link to="/clinical-note">Return to note</Link> }));
beforeEach(() => { localStorage.clear(); sessionStorage.clear(); });
afterEach(() => { cleanup(); vi.restoreAllMocks(); });
async function open() {
  await i18n.changeLanguage('pt');
  const rendered = render(<MemoryRouter initialEntries={['/clinical-note']}><SettingsProvider><App /></SettingsProvider></MemoryRouter>);
  await screen.findByLabelText('Motivo de consulta');
  return rendered;
}

it('keeps the same synthetic note through the offered blood gas round trip without browser storage', async () => {
  await open();
  fireEvent.change(screen.getByLabelText('Motivo de consulta'), { target: { value: 'SYNTHETIC_EPISODE_A' } });
  fireEvent.change(screen.getByLabelText('Idade'), { target: { value: '44' } });
  const user = userEvent.setup();
  await user.click(screen.getByRole('link', { name: /Gasometria/ }));
  await user.click(await screen.findByRole('link', { name: 'Return to note' }));
  expect(await screen.findByLabelText('Motivo de consulta')).toHaveValue('SYNTHETIC_EPISODE_A');
  expect(screen.getByLabelText('Idade')).toHaveValue('44');
  expect(JSON.stringify(localStorage)).not.toContain('SYNTHETIC_EPISODE_A');
  expect(sessionStorage.length).toBe(0);
});

it('requires deliberate discard and clears the entire episode with a new identity', async () => {
  const first = await open();
  const id = screen.getByTestId('note-encounter').textContent;
  fireEvent.change(screen.getByLabelText('Motivo de consulta'), { target: { value: 'SYNTHETIC_EPISODE_A' } });
  fireEvent.change(screen.getByLabelText('Idade'), { target: { value: '44' } });
  const beforeDiscard = new Event('beforeunload', { cancelable: true });
  window.dispatchEvent(beforeDiscard);
  expect(beforeDiscard.defaultPrevented).toBe(true);
  const confirm = vi.spyOn(window, 'confirm').mockReturnValueOnce(false).mockReturnValueOnce(true);
  fireEvent.click(screen.getByRole('button', { name: 'Nova nota' }));
  expect(confirm).toHaveBeenCalledTimes(1);
  expect(screen.getByLabelText('Motivo de consulta')).toHaveValue('SYNTHETIC_EPISODE_A');
  fireEvent.click(screen.getByRole('button', { name: 'Nova nota' }));
  expect(screen.getByLabelText('Motivo de consulta')).toHaveValue('');
  expect(screen.getByLabelText('Idade')).toHaveValue('');
  expect(screen.getByTestId('note-encounter').textContent).not.toBe(id);
  const afterDiscard = new Event('beforeunload', { cancelable: true });
  window.dispatchEvent(afterDiscard);
  expect(afterDiscard.defaultPrevented).toBe(false);
  fireEvent.change(screen.getByLabelText('Motivo de consulta'), { target: { value: 'SYNTHETIC_EPISODE_B' } });
  first.unmount();
  await open();
  expect(screen.getByLabelText('Motivo de consulta')).toHaveValue('');
});

it('does not carry a late diagnostic response into a new episode', async () => {
  let resolve!: (value: Awaited<ReturnType<typeof api.analyzeClinicalNote>>) => void;
  const pending = new Promise<Awaited<ReturnType<typeof api.analyzeClinicalNote>>>(done => { resolve = done; });
  const analyze = vi.spyOn(api, 'analyzeClinicalNote').mockReturnValue(pending);
  vi.spyOn(window, 'confirm').mockReturnValue(true);
  await open();
  fireEvent.change(screen.getByLabelText('Motivo de consulta'), { target: { value: 'SYNTHETIC_EPISODE_A' } });
  fireEvent.click(screen.getByTestId('note-tab-diagnostic'));
  fireEvent.click(screen.getByRole('button', { name: 'Atualizar apoio diagnóstico' }));
  await waitFor(() => expect(analyze).toHaveBeenCalledTimes(1));
  fireEvent.click(screen.getByRole('button', { name: 'Nova nota' }));
  await act(async () => {
    resolve({ blocked: false, issues: [], signals: [], note: analyze.mock.calls[0]![0], medication_safety_gate: {status:'NOT_APPLICABLE',actionable:false,required_module:null,message:'SYNTHETIC'},
      assessment: { problem_representation: null, active_problems: [], likely_diagnoses: [], differential_diagnoses: [], must_not_miss: [], suggested_tests: [], treatment_suggestions: [], disposition: [], reassessment: [], contradictions_to_clarify: [], limitations: ['SYNTHETIC_OLD_RESPONSE'] },
    });
    await pending;
  });
  fireEvent.click(screen.getByTestId('note-tab-diagnostic'));
  expect(screen.queryByText('SYNTHETIC_OLD_RESPONSE')).toBeNull();
  expect(screen.getByRole('button', { name: 'Atualizar apoio diagnóstico' })).toBeEnabled();
});

it('rearms a pending acceptance after navigation and ignores its late response', async () => {
  const prepared: PreparedUpload = {
    api_version:'1.0', upload_id:'synthetic-upload', filename:'synthetic.txt', mime_type:'text/plain', size_bytes:9,
    sha256:'synthetic-hash', integrity_token:'synthetic-token', kind:'ct',
    route:{kind:'ct', target_section:'imaging', modules:['ct-mri-screenshot']},
    privacy:{status:'PASS',findings:[],manual_file_privacy_review_required:false,burned_in_identifier_review_required:false},
    extracted:{official_report:'SYNTHETIC_REPORT',ai_interpretation:null},
    processing:{status:'text_extracted',message:'SYNTHETIC',modules:['ct-mri-screenshot']}, original_retained:false,
  };
  vi.spyOn(api, 'prepareClinicalUpload').mockResolvedValue(prepared);
  let resolve!: (value: Awaited<ReturnType<typeof api.acceptClinicalUpload>>) => void;
  const pending = new Promise<Awaited<ReturnType<typeof api.acceptClinicalUpload>>>(done => { resolve = done; });
  const accept = vi.spyOn(api, 'acceptClinicalUpload').mockReturnValue(pending);
  await open();
  fireEvent.click(screen.getByRole('button', { name: 'MCDT' }));
  const user = userEvent.setup();
  await user.upload(screen.getByLabelText('Upload clínico'), new File(['SYNTHETIC'], 'synthetic.txt', {type:'text/plain'}));
  await waitFor(() => expect(screen.getByRole('button', { name: 'Aceitar' })).toBeEnabled());
  fireEvent.click(screen.getByRole('button', { name: 'Aceitar' }));
  expect(accept).toHaveBeenCalledTimes(1);
  expect(screen.getByRole('button', { name: 'Aceitar' })).toBeDisabled();
  await user.click(screen.getByRole('link', { name: /Gasometria/ }));
  await user.click(await screen.findByRole('link', { name: 'Return to note' }));
  expect(await screen.findByRole('button', { name: 'Aceitar' })).toBeEnabled();
  await act(async () => { resolve({note:accept.mock.calls[0]![0]}); await pending; });
  expect(screen.getByTestId('mcdt-review-card')).toHaveTextContent('Pendente');
  expect(screen.getByRole('button', { name: 'Aceitar' })).toBeEnabled();
  expect(screen.getByLabelText('Relatório oficial / extraído synthetic.txt')).toHaveValue('SYNTHETIC_REPORT');
});

it('invalidates clinician review if the language changes while the note route is closed', async () => {
  await open();
  fireEvent.change(screen.getByLabelText('Motivo de consulta'), {target:{value:'SYNTHETIC_EPISODE_A'}});
  fireEvent.click(screen.getByTestId('note-tab-export'));
  const reviewed = screen.getByRole('checkbox', {name:/Médico reviu e valida/});
  fireEvent.click(reviewed);
  expect(reviewed).toBeChecked();
  const user = userEvent.setup();
  await user.click(screen.getByRole('link', {name:/Gasometria/}));
  await act(async()=>{await i18n.changeLanguage('en');});
  await user.click(await screen.findByRole('link', {name:'Return to note'}));
  expect((await screen.findAllByRole('checkbox'))[1]).not.toBeChecked();
});
