import { act, cleanup, fireEvent, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import ClinicalNote from '../pages/ClinicalNote';
import * as api from '../clinical-note/api';
import i18n from '../i18n';
import { THERAPY_COPY } from '../clinical-note/therapyCopy';
import { renderAt } from './render';
import { syntheticTherapeuticPlan, syntheticTherapeuticReview } from './fixtures/therapeuticPlan';

beforeEach(() => {
  vi.restoreAllMocks(); localStorage.clear(); sessionStorage.clear();
  vi.spyOn(api, 'getTherapyCatalog').mockResolvedValue({ modules: [{ id: 'synthetic-module', title: 'SYNTHETIC_REFERENCE', populations: ['adult','pediatric'], source_language: 'original' }] });
  vi.spyOn(api, 'suggestTherapeuticPlan').mockImplementation(async (note, selection, context) => ({ blocked: false, issues: [], plan: syntheticTherapeuticPlan(note, selection, context) }));
  vi.spyOn(api, 'validateTherapeuticPlan').mockResolvedValue({ blocked: false, issues: [], review: syntheticTherapeuticReview() });
  vi.spyOn(api, 'preflightClinicalNote').mockResolvedValue({ blocked: false, findings: [] });
  vi.spyOn(api, 'exportClinicalNote').mockResolvedValue({ filename: 'synthetic.pdf', blob: new Blob(['SYNTHETIC'], { type: 'application/pdf' }) });
  vi.spyOn(api, 'downloadBlob').mockImplementation(() => {});
});
afterEach(() => { cleanup(); vi.restoreAllMocks(); });

function change(label: string, value: string) { fireEvent.change(screen.getByLabelText(label), { target: { value } }); }
function tab(name: string) { fireEvent.click(screen.getByTestId(`note-tab-${name}`)); }
async function openPlan(months = false) {
  await renderAt('/clinical-note', [{ path: '/clinical-note', element: <ClinicalNote/> }], 'es');
  if (months) change('Unidad de edad', 'months');
  change('Edad', months ? '8' : '44');
  change('Motivo de consulta', 'SYNTHETIC_CASE');
  tab('plan');
  await screen.findByRole('option', { name: 'SYNTHETIC_REFERENCE' });
  change('Diagnóstico o patología', 'SYNTHETIC_DIAGNOSIS');
  change('Referencia clínica', 'synthetic-module');
  change('Peso (kg)', months ? '8.2' : '70');
  fireEvent.click(screen.getByRole('checkbox', { name: THERAPY_COPY.es.allergies }));
  fireEvent.click(screen.getByRole('checkbox', { name: THERAPY_COPY.es.privacy }));
}
async function generate() {
  fireEvent.click(screen.getByRole('button', { name: 'Preparar pauta' }));
  await screen.findByDisplayValue('SYNTHETIC_MEDICATION_REGIMEN');
}
function confirm() {
  fireEvent.click(screen.getByRole('checkbox', { name: THERAPY_COPY.es.individualized }));
  fireEvent.click(screen.getByRole('checkbox', { name: THERAPY_COPY.es.safety }));
}
async function validate() {
  confirm(); fireEvent.click(screen.getByRole('button', { name: 'Validar pauta' }));
  await screen.findByRole('button', { name: 'Pauta validada' });
}
function reviewForExport() {
  tab('export');
  const reviewed=screen.getByRole('checkbox', { name: /El médico ha revisado y valida/ });
  if(!(reviewed as HTMLInputElement).checked) fireEvent.click(reviewed);
}

describe('Exact therapeutic plan review', () => {
  it('requires explicit medical confirmation, turns green, exports one plan and invalidates any later clinical edit', async () => {
    await openPlan(); await generate();
    expect(screen.getByRole('button', { name: 'Validar pauta' })).toBeDisabled();
    expect(screen.getByTestId('therapy-review-state')).toHaveTextContent('Pendiente de validación médica');
    expect(screen.getByLabelText('Medicación y pauta completa')).toHaveAttribute('readonly');
    await validate();
    expect(screen.getByTestId('therapy-review-state')).toHaveTextContent('Revisión médica vigente');
    expect(screen.getByRole('button', { name: 'Pauta validada' })).toHaveClass('bg-emerald-700');
    const validation = vi.mocked(api.validateTherapeuticPlan).mock.calls[0]!;
    expect(validation[1]).toEqual({ individualized: true, medication_safety_reviewed: true });
    expect(validation[0].therapeutic_plan?.medication_safety.actionable).toBe(false);
    tab('export');
    expect(screen.getByRole('checkbox', { name: /El médico ha revisado y valida/ })).toBeChecked();
    expect(screen.getByRole('button', { name: 'PDF' })).toBeEnabled();
    fireEvent.click(screen.getByRole('button', { name: 'PDF' }));
    await waitFor(() => expect(api.downloadBlob).toHaveBeenCalledTimes(1));
    const exported = vi.mocked(api.exportClinicalNote).mock.calls[0]![0];
    expect(exported.therapeutic_review?.validation_token).toBe('synthetic-validation-token');
    expect(exported.assessment.treatment_suggestions).toEqual([]);
    expect(exported.therapeutic_plan?.sections.medications).toBe('SYNTHETIC_MEDICATION_REGIMEN');
    expect(exported.therapeutic_plan?.medication_safety).toMatchObject({ status: 'REVIEW_REQUIRED', actionable: false });
    tab('history'); change('Motivo de consulta', 'SYNTHETIC_EDITED_CASE');
    tab('export'); fireEvent.click(screen.getByRole('checkbox', { name: /El médico ha revisado y valida/ }));
    expect(screen.getByRole('button', { name: 'PDF' })).toBeDisabled();
    tab('plan');
    expect(screen.getByTestId('therapy-review-state')).toHaveTextContent('Pendiente');
    expect(screen.getByText(THERAPY_COPY.es.sourceChanged)).toBeInTheDocument();
  });

  it('lets the physician edit sections without altering source metadata, then revalidate that exact text', async () => {
    await openPlan(); await generate(); await validate();
    fireEvent.click(screen.getByRole('button', { name: 'Editar pauta' }));
    change('Medicación y pauta completa', 'SYNTHETIC_PHYSICIAN_EDIT');
    expect(screen.queryByRole('button', { name: 'Pauta validada' })).not.toBeInTheDocument();
    expect(screen.queryByText(THERAPY_COPY.es.sourceChanged)).not.toBeInTheDocument();
    vi.mocked(api.validateTherapeuticPlan).mockResolvedValue({ blocked: false, issues: [], review: syntheticTherapeuticReview('edited') });
    await validate();
    const sent = vi.mocked(api.validateTherapeuticPlan).mock.calls[1]![0].therapeutic_plan!;
    expect(sent.sections.medications).toBe('SYNTHETIC_PHYSICIAN_EDIT');
    expect(sent.reference_text).toBe('SYNTHETIC_CANONICAL_REFERENCE_UNCHANGED');
    expect(sent.source_refs[0]?.sha256).toBe('a'.repeat(64));
    expect(sent.generation_token).toBe('synthetic-generation-token');
    expect(api.suggestTherapeuticPlan).toHaveBeenCalledTimes(1);
  });

  it('sends pediatric age in months exclusively, uses explicit weight and requires regeneration after a context change', async () => {
    await openPlan(true); await generate(); await validate();
    const request = vi.mocked(api.suggestTherapeuticPlan).mock.calls[0]!;
    expect(request[0].encounter.age).toEqual({ years: null, months: 8 });
    expect(request[2]).toEqual({ weight_kg: 8.2, allergies_reviewed: true });
    expect(screen.getByText('Pediatría')).toBeInTheDocument();
    change('Peso (kg)', '9');
    expect(screen.getByText(THERAPY_COPY.es.sourceChanged)).toBeInTheDocument();
    confirm(); expect(screen.getByRole('button', { name: 'Validar pauta' })).toBeDisabled();
    fireEvent.click(screen.getByRole('button', { name: 'Actualizar propuesta' }));
    await waitFor(() => expect(api.suggestTherapeuticPlan).toHaveBeenCalledTimes(2));
    await waitFor(() => expect(screen.queryByText(THERAPY_COPY.es.sourceChanged)).not.toBeInTheDocument());
    expect(vi.mocked(api.suggestTherapeuticPlan).mock.calls[1]![2].weight_kg).toBe(9);
  });

  it('discards a suggestion arriving after the case changes', async () => {
    let resolve!: (value: Awaited<ReturnType<typeof api.suggestTherapeuticPlan>>) => void;
    const delayed = new Promise<Awaited<ReturnType<typeof api.suggestTherapeuticPlan>>>(done => { resolve = done; });
    vi.mocked(api.suggestTherapeuticPlan).mockReturnValueOnce(delayed);
    await openPlan();
    fireEvent.click(screen.getByRole('button', { name: 'Preparar pauta' }));
    const [note, selection, context] = vi.mocked(api.suggestTherapeuticPlan).mock.calls[0]!;
    change('Peso (kg)', '72');
    await act(async () => { resolve({ blocked: false, issues: [], plan: syntheticTherapeuticPlan(note, selection, context) }); await delayed; });
    expect(screen.queryByLabelText('Medicación y pauta completa')).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Preparar pauta' })).toBeEnabled();
  });

  it('prepares the explicitly selected diagnostic candidate rather than automatically choosing the first result', async () => {
    vi.spyOn(api,'analyzeClinicalNote').mockImplementation(async note=>({
      blocked:false,issues:[],signals:[],note,
      medication_safety_gate:{status:'REVIEW_REQUIRED',actionable:false,required_module:'medication-selection-safety',message:'SYNTHETIC'},
      assessment:{problem_representation:null,active_problems:[],likely_diagnoses:[
        {diagnosis:'SYNTHETIC_SELECTED_DIAGNOSIS',confidence:'moderate',evidence_for:[],evidence_against:[],missing_discriminating_data:[],source_modules:['synthetic-module']},
      ],differential_diagnoses:[],must_not_miss:[],suggested_tests:[],treatment_suggestions:[],disposition:[],reassessment:[],contradictions_to_clarify:[],limitations:[]},
    }));
    await openPlan(); tab('diagnostic');
    fireEvent.click(screen.getByRole('button',{name:'Actualizar apoyo diagnóstico'}));
    await screen.findByText('SYNTHETIC_SELECTED_DIAGNOSIS');
    expect(api.suggestTherapeuticPlan).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole('button',{name:'Preparar pauta'}));
    await screen.findByDisplayValue('SYNTHETIC_MEDICATION_REGIMEN');
    expect(vi.mocked(api.suggestTherapeuticPlan).mock.calls[0]![1]).toEqual({label:'SYNTHETIC_SELECTED_DIAGNOSIS',module_id:'synthetic-module',selection:'diagnostic'});
  });

  it('keeps a late proposal out of a new episode and clears its review context', async () => {
    let resolve!: (value: Awaited<ReturnType<typeof api.suggestTherapeuticPlan>>) => void;
    const delayed=new Promise<Awaited<ReturnType<typeof api.suggestTherapeuticPlan>>>(done=>{resolve=done;});
    vi.mocked(api.suggestTherapeuticPlan).mockReturnValueOnce(delayed);
    vi.spyOn(window,'confirm').mockReturnValue(true);
    await openPlan();
    const encounter=screen.getByTestId('note-encounter').textContent;
    fireEvent.click(screen.getByRole('button',{name:'Preparar pauta'}));
    const [note,selection,context]=vi.mocked(api.suggestTherapeuticPlan).mock.calls[0]!;
    fireEvent.click(screen.getByRole('button',{name:'Nueva nota'}));
    await act(async()=>{resolve({blocked:false,issues:[],plan:syntheticTherapeuticPlan(note,selection,context)});await delayed;});
    expect(screen.getByTestId('note-encounter').textContent).not.toBe(encounter);
    tab('plan');
    expect(screen.getByLabelText('Diagnóstico o patología')).toHaveValue('');
    expect(screen.queryByLabelText('Medicación y pauta completa')).not.toBeInTheDocument();
    expect(screen.getByRole('checkbox',{name:THERAPY_COPY.es.privacy})).not.toBeChecked();
  });

  it('never turns green from a validation response after an edit', async () => {
    let resolve!: (value: Awaited<ReturnType<typeof api.validateTherapeuticPlan>>) => void;
    const delayed = new Promise<Awaited<ReturnType<typeof api.validateTherapeuticPlan>>>(done => { resolve = done; });
    vi.mocked(api.validateTherapeuticPlan).mockReturnValueOnce(delayed);
    await openPlan(); await generate(); confirm();
    fireEvent.click(screen.getByRole('button', { name: 'Validar pauta' }));
    fireEvent.click(screen.getByRole('button', { name: 'Editar pauta' }));
    change('Monitorización', 'SYNTHETIC_EDIT_DURING_VALIDATION');
    await act(async () => { resolve({ blocked: false, issues: [], review: syntheticTherapeuticReview() }); await delayed; });
    expect(screen.queryByRole('button', { name: 'Pauta validada' })).not.toBeInTheDocument();
    expect(screen.getByTestId('therapy-review-state')).toHaveTextContent('Pendiente');
    reviewForExport(); expect(screen.getByRole('button', { name: 'PDF' })).toBeDisabled();
  });

  it.each(['preflight','export'] as const)('does not download a stale note edited during %s', async stage => {
    let release!: () => void;
    const delayed = new Promise<void>(done => { release = done; });
    if (stage === 'preflight') vi.mocked(api.preflightClinicalNote).mockImplementationOnce(async () => { await delayed; return { blocked: false, findings: [] }; });
    else vi.mocked(api.exportClinicalNote).mockImplementationOnce(async () => { await delayed; return { filename: 'stale.pdf', blob: new Blob(['SYNTHETIC']) }; });
    await openPlan(); await generate(); await validate(); reviewForExport();
    fireEvent.click(screen.getByRole('button', { name: 'PDF' }));
    if (stage === 'export') await waitFor(() => expect(api.exportClinicalNote).toHaveBeenCalledTimes(1));
    tab('history'); change('Motivo de consulta', 'SYNTHETIC_CHANGED_DURING_EXPORT');
    await act(async () => { release(); await delayed; });
    expect(api.downloadBlob).not.toHaveBeenCalled();
    if (stage === 'preflight') expect(api.exportClinicalNote).not.toHaveBeenCalled();
  });

  it.each(['preflight','export'] as const)('revokes the current therapeutic receipt when %s authoritatively rejects it', async stage=>{
    await openPlan();await generate();await validate();
    expect(screen.getByRole('button',{name:'Pauta validada'})).toBeInTheDocument();
    if(stage==='preflight') vi.mocked(api.preflightClinicalNote).mockResolvedValueOnce({blocked:true,findings:[{severity:'STOP',code:'THERAPY_SOURCE_CHANGED',message:'SYNTHETIC_SOURCE_CHANGED'}]});
    else vi.mocked(api.exportClinicalNote).mockRejectedValueOnce(new api.ClinicalApiResponseError(422,'SYNTHETIC_RECEIPT_REJECTED','THERAPY_REVIEW_INVALID'));
    tab('export');
    expect(screen.getByRole('button',{name:'PDF'})).toBeEnabled();
    fireEvent.click(screen.getByRole('button',{name:'PDF'}));
    await screen.findByRole('alert');
    expect(api.downloadBlob).not.toHaveBeenCalled();
    expect(screen.getByRole('button',{name:'PDF'})).toBeDisabled();
    expect(screen.getByRole('checkbox',{name:/El médico ha revisado y valida/})).not.toBeChecked();
    tab('plan');
    expect(screen.queryByRole('button',{name:'Pauta validada'})).not.toBeInTheDocument();
    expect(screen.getByTestId('therapy-review-state')).toHaveTextContent('Pendiente');
    expect(screen.getByText(THERAPY_COPY.es.sourceChanged)).toBeInTheDocument();
    expect(screen.getByRole('button',{name:'Validar pauta'})).toBeDisabled();
  });

  it('keeps an invalid receipt or a changed language from authorizing output', async () => {
    await openPlan(); await generate();
    vi.mocked(api.validateTherapeuticPlan).mockResolvedValueOnce({ blocked: true, issues: [{severity:'STOP',code:'SYNTHETIC',message:'SYNTHETIC_REVIEW_REJECTED'}], review: null });
    confirm(); fireEvent.click(screen.getByRole('button', { name: 'Validar pauta' }));
    await screen.findByText('SYNTHETIC_REVIEW_REJECTED');
    expect(screen.queryByRole('button', { name: 'Pauta validada' })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Validar pauta' }));
    await screen.findByRole('button', { name: 'Pauta validada' });
    await act(async () => { await i18n.changeLanguage('en'); });
    expect(screen.getByTestId('therapy-review-state')).toHaveTextContent('Medical validation pending');
    expect(screen.getByText(THERAPY_COPY.en.sourceChanged)).toBeInTheDocument();
  });

  it('does not let the old general review checkbox bypass an unvalidated manual treatment', async () => {
    await openPlan(); change('Plan médico', 'SYNTHETIC_MANUAL_TREATMENT');
    reviewForExport();
    expect(screen.getByRole('button', { name: 'PDF' })).toBeDisabled();
    expect(api.exportClinicalNote).not.toHaveBeenCalled();
    expect(screen.getByText(THERAPY_COPY.es.reviewNeeded)).toBeInTheDocument();
  });

  it('does not mistake unchanged canonical text for patient identifiers but screens every clinical edit', async () => {
    vi.mocked(api.suggestTherapeuticPlan).mockImplementationOnce(async(note,selection,context)=>{
      const plan=syntheticTherapeuticPlan(note,selection,context);
      plan.sections.initial_actions='Use patient-specific assessment and address barriers to care.';
      return {blocked:false,issues:[],plan};
    });
    await openPlan(); await generate();
    expect(screen.queryByText(/STOP: posible identificador/)).not.toBeInTheDocument();
    await validate();
    fireEvent.click(screen.getByRole('button',{name:'Editar pauta'}));
    change('Actuaciones iniciales','Use patient-specific assessment. Nombre: Juan Perez');
    confirm();
    expect(screen.getByRole('button',{name:'Validar pauta'})).toBeDisabled();
    expect(screen.getByRole('alert')).toHaveTextContent('STOP');
    expect(api.validateTherapeuticPlan).toHaveBeenCalledTimes(1);
  });

  it.each(['es','en','pt','zh'] as const)('provides a complete %s interface without changing canonical source text', async lang => {
    await renderAt('/clinical-note', [{ path: '/clinical-note', element: <ClinicalNote/> }], lang);
    tab('plan');
    expect(screen.getByRole('heading', { name: THERAPY_COPY[lang].title })).toBeInTheDocument();
    expect(screen.getByLabelText(THERAPY_COPY[lang].diagnosis)).toBeInTheDocument();
    expect(Object.keys(THERAPY_COPY[lang]).sort()).toEqual(Object.keys(THERAPY_COPY.en).sort());
    expect(Object.values(THERAPY_COPY[lang]).every(value=>value.trim())).toBe(true);
    await screen.findByRole('option', { name: 'SYNTHETIC_REFERENCE' });
  });
});
