import { act, fireEvent, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, expect, it, vi } from 'vitest';
import ClinicalNote from '../pages/ClinicalNote';
import * as api from '../clinical-note/api';
import type { ClinicalNotePayload, PreparedUpload } from '../clinical-note/types';
import { renderAt } from './render';

beforeEach(() => { vi.restoreAllMocks(); localStorage.clear(); });

const prepared: PreparedUpload = {
  api_version:'1.0', upload_id:'synthetic-upload', filename:'synthetic.txt', mime_type:'text/plain', size_bytes:9,
  sha256:'synthetic-hash', integrity_token:'synthetic-token', kind:'ct',
  route:{kind:'ct', target_section:'imaging', modules:['ct-mri-screenshot']},
  privacy:{status:'PASS',findings:[],manual_file_privacy_review_required:false,burned_in_identifier_review_required:false},
  extracted:{official_report:'SYNTHETIC_REPORT_A',ai_interpretation:null},
  processing:{status:'text_extracted',message:'SYNTHETIC',modules:['ct-mri-screenshot']}, original_retained:false,
};

// Model the response's replacement collections, as the acceptance endpoint returns them.
function acceptedResponse(note: ClinicalNotePayload) {
  const accepted = structuredClone(note);
  accepted.complementary_tests.imaging.push({
    kind:'ct',time_label:null,provenance:'ai_document_extraction',source_reference:'sha256:synthetic-hash',
    official_report:'SYNTHETIC_REPORT_A',ai_interpretation:null,findings:null,impression:null,limitations:[],
    privacy_checked:true,burned_in_identifiers_checked:true,routed_modules:['ct-mri-screenshot'],
  });
  accepted.timeline.push({time_label:'MCDT',event:'SYNTHETIC_ACCEPT_RESPONSE_A',source:'sha256:synthetic-hash'});
  return {note:accepted};
}

it.each(['edit target','reject target','edit another accepted card','unchanged'] as const)(
  'applies an acceptance response only to the submitted revision: %s', async action => {
    vi.spyOn(api, 'prepareClinicalUpload').mockResolvedValue(prepared);
    let resolve!: (value: Awaited<ReturnType<typeof api.acceptClinicalUpload>>) => void;
    const pending = new Promise<Awaited<ReturnType<typeof api.acceptClinicalUpload>>>(done => { resolve = done; });
    const accept = vi.spyOn(api, 'acceptClinicalUpload').mockReturnValue(pending);
    const analyze = vi.spyOn(api, 'analyzeClinicalNote').mockImplementation(async note => ({
      blocked:false,issues:[],signals:[],note,assessment:null,
      medication_safety_gate:{status:'NOT_APPLICABLE',actionable:false,required_module:null,message:'SYNTHETIC'},
    }));
    await renderAt('/clinical-note', [{path:'/clinical-note',element:<ClinicalNote/>}], 'pt');
    fireEvent.click(screen.getByTestId('note-tab-mcdt'));

    // An already accepted second card lets the test detect restoration of an old collection.
    fireEvent.change(screen.getByLabelText('Nome do exame'), {target:{value:'synthetic-other'}});
    fireEvent.change(screen.getByLabelText('Relatório oficial / dados extraídos'), {target:{value:'SYNTHETIC_OTHER_A'}});
    fireEvent.click(screen.getByRole('button', {name:'Criar cartão para revisão'}));
    fireEvent.click(screen.getByRole('button', {name:'Aceitar'}));
    const other = screen.getByLabelText('Relatório oficial / extraído synthetic-other').closest('article')!;
    expect(within(other).getByText('Aceite')).toBeInTheDocument();

    const user = userEvent.setup();
    await user.upload(screen.getByLabelText('Upload clínico'), new File(['SYNTHETIC'], 'synthetic.txt', {type:'text/plain'}));
    const official = await screen.findByLabelText('Relatório oficial / extraído synthetic.txt');
    const target = official.closest('article')!;
    await waitFor(() => expect(within(target).getByRole('button', {name:'Aceitar'})).toBeEnabled());
    fireEvent.click(within(target).getByRole('button', {name:'Aceitar'}));
    expect(accept).toHaveBeenCalledTimes(1);
    const response = acceptedResponse(accept.mock.calls[0]![0]);
    expect(accept.mock.calls[0]![2].official_report).toBe('SYNTHETIC_REPORT_A');

    if (action === 'edit target') fireEvent.change(official, {target:{value:'SYNTHETIC_REPORT_B'}});
    if (action === 'reject target') fireEvent.click(within(target).getByRole('button', {name:'Rejeitar'}));
    if (action === 'edit another accepted card') {
      fireEvent.change(screen.getByLabelText('Relatório oficial / extraído synthetic-other'), {target:{value:'SYNTHETIC_OTHER_B'}});
      expect(within(other).getByText('Pendente')).toBeInTheDocument();
    }
    await act(async () => { resolve(response); await pending; });

    const expectedState = action === 'unchanged' ? 'Aceite' : action === 'reject target' ? 'Rejeitado' : 'Pendente';
    expect(within(target).getByText(expectedState)).toBeInTheDocument();
    expect(within(target).getByRole('button', {name:'Aceitar'})).toBeEnabled();
    expect(official).toHaveValue(action === 'edit target' ? 'SYNTHETIC_REPORT_B' : 'SYNTHETIC_REPORT_A');
    if (action === 'unchanged') expect(screen.getByText('SYNTHETIC_ACCEPT_RESPONSE_A')).toBeInTheDocument();
    else expect(screen.queryByText('SYNTHETIC_ACCEPT_RESPONSE_A')).toBeNull();

    // A downstream API operation must see exactly the accepted current collections.
    fireEvent.click(screen.getByTestId('note-tab-diagnostic'));
    fireEvent.click(screen.getByRole('button', {name:'Atualizar apoio diagnóstico'}));
    await waitFor(() => expect(analyze).toHaveBeenCalledTimes(1));
    const current = analyze.mock.calls[0]![0];
    expect(current.complementary_tests.imaging.map(report => report.official_report))
      .toEqual(action === 'unchanged' ? ['SYNTHETIC_REPORT_A'] : []);
    expect(current.complementary_tests.other.map(report => report.official_report))
      .toEqual(action === 'edit another accepted card' ? [] : ['SYNTHETIC_OTHER_A']);
    expect(current.timeline.some(event => event.event === 'SYNTHETIC_ACCEPT_RESPONSE_A')).toBe(action === 'unchanged');
  },
);
