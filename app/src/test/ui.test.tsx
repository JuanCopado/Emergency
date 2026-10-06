import { fireEvent, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import Calculator from '../pages/Calculator';
import DrugDetail from '../pages/DrugDetail';
import DrugList from '../pages/DrugList';
import Home from '../pages/Home';
import About from '../pages/About';
import Settings from '../pages/Settings';
import ClinicalNote from '../pages/ClinicalNote';
import { renderAt } from './render';

beforeEach(() => {
  vi.restoreAllMocks();
  try {
    localStorage.clear();
  } catch {
    /* ignore */
  }
});

describe('Calculator', () => {
  it('norepinephrine 0.05 mcg/kg/min, 70 kg, 40 mcg/mL → 5.3 mL/h with arithmetic', async () => {
    await renderAt('/calculator?drug=norepinephrine&weight=70&dose=0.05', [{ path: '/calculator', element: <Calculator /> }]);
    expect(await screen.findByTestId('rate-display')).toHaveTextContent('5.3');
    const result = screen.getByTestId('calc-result');
    expect(within(result).getByText(/0\.05 mcg\/kg\/min × 70 kg = 3\.5 mcg\/min/)).toBeInTheDocument();
    expect(within(result).getByText(/210 mcg\/h ÷ 40 mcg\/mL = 5\.25 mL\/h/)).toBeInTheDocument();
    // Preparation summary shows amount, final volume and concentration
    expect(screen.getAllByText('8 mg').length).toBeGreaterThan(0);
    expect(screen.getAllByText('200 mL').length).toBeGreaterThan(0);
    // Titration table highlights the current dose row
    const table = screen.getByTestId('titration-table');
    expect(within(table).getAllByRole('row').length).toBeGreaterThan(3);
  });

  it('missing weight → shows formula, no patient-specific rate', async () => {
    await renderAt('/calculator?drug=norepinephrine&dose=0.05', [{ path: '/calculator', element: <Calculator /> }]);
    const nw = await screen.findByTestId('needs-weight');
    expect(nw).toHaveTextContent('mL/h = dose (mcg/kg/min) × weight (kg) × 60 ÷ concentration (mcg/mL)');
    expect(screen.queryByTestId('rate-display')).not.toBeInTheDocument();
  });

  it('fixed-dose vasopressin works without weight (0.03 units/min → 1.8 mL/h)', async () => {
    await renderAt('/calculator?drug=vasopressin&dose=0.03', [{ path: '/calculator', element: <Calculator /> }]);
    expect(await screen.findByTestId('rate-display')).toHaveTextContent('1.8');
  });

  it('warns above the stated maximum (dopamine 60 mcg/kg/min)', async () => {
    await renderAt('/calculator?drug=dopamine&weight=70&dose=60', [{ path: '/calculator', element: <Calculator /> }]);
    expect(await screen.findByText(/Above the stated maximum/)).toBeInTheDocument();
  });

  it('reverse mode: 10.5 mL/h norepinephrine at 70 kg → 0.1 mcg/kg/min', async () => {
    const user = userEvent.setup();
    await renderAt('/calculator?drug=norepinephrine&weight=70', [{ path: '/calculator', element: <Calculator /> }]);
    await user.click(screen.getByRole('radio', { name: 'mL/h → dose' }));
    fireEvent.change(screen.getByTestId('calc-rate'), { target: { value: '10,5' } });
    expect(await screen.findByTestId('dose-display')).toHaveTextContent('0.1');
  });

  it('custom concentration from amount/volume', async () => {
    const user = userEvent.setup();
    await renderAt('/calculator?drug=norepinephrine&weight=70&dose=0.05', [{ path: '/calculator', element: <Calculator /> }]);
    await user.click(screen.getByRole('radio', { name: 'Custom concentration' }));
    fireEvent.change(screen.getByTestId('custom-amount'), { target: { value: '4' } });
    fireEvent.change(screen.getByTestId('custom-volume'), { target: { value: '50' } });
    // 4 mg / 50 mL = 0.08 mg/mL = 80 mcg/mL → 2.625 → 2.6
    await waitFor(() => expect(screen.getByTestId('rate-display')).toHaveTextContent('2.6'));
  });

  it('milrinone loading dose shows dose, volume and time (no mL/h)', async () => {
    await renderAt('/calculator?drug=milrinone&weight=70&dose=0.375', [{ path: '/calculator', element: <Calculator /> }]);
    const heading = await screen.findByRole('heading', { name: /Loading \/ bolus dose/ });
    const card = heading.closest('section') as HTMLElement;
    expect(within(card).getByText('3,500 mcg')).toBeInTheDocument();
    expect(within(card).getByText('17.5 mL')).toBeInTheDocument();
    expect(within(card).getByText('10 min')).toBeInTheDocument();
    expect(within(card).queryByText(/\d mL\/h/)).not.toBeInTheDocument();
  });
});

describe('Drug detail', () => {
  it('shows draft banner, evidence badge, preparations and source module', async () => {
    await renderAt('/drugs/norepinephrine', [{ path: '/drugs/:id', element: <DrugDetail /> }]);
    expect(await screen.findByTestId('draft-banner')).toBeInTheDocument();
    expect(screen.getByRole('heading', { level: 1, name: 'Norepinephrine' })).toBeInTheDocument();
    expect(screen.getAllByText(/Partial — review pending/).length).toBeGreaterThan(0);
    expect(screen.getByText('vasoactive-inotrope-infusions')).toBeInTheDocument();
    expect(screen.getByText(/8 mg of tartrate salt contains about 4 mg base/)).toBeInTheDocument();
  });

  it('unknown drug → not found', async () => {
    await renderAt('/drugs/nope', [{ path: '/drugs/:id', element: <DrugDetail /> }]);
    expect(await screen.findByText('Page not found')).toBeInTheDocument();
  });
});

describe('Drug list & home', () => {
  it('filters by category and by localized name search', async () => {
    await renderAt('/drugs?category=icu-sedation-analgesia', [{ path: '/drugs', element: <DrugList /> }]);
    expect(await screen.findByTestId('result-count')).toHaveTextContent('8 results');
  });

  it('Spanish search matches localized name (noradrenalina)', async () => {
    await renderAt('/drugs?q=noradrenalina', [{ path: '/drugs', element: <DrugList /> }], 'es');
    expect(await screen.findByTestId('result-count')).toHaveTextContent('1 resultado');
    expect(screen.getByTestId('drug-card-norepinephrine')).toBeInTheDocument();
  });

  it('home lists available categories and coming-soon groups', async () => {
    await renderAt('/', [{ path: '/', element: <Home /> }]);
    expect(await screen.findByTestId('category-vasoactive')).toHaveTextContent('9 drugs');
    expect(screen.getByTestId('category-sedation')).toHaveTextContent('8 drugs');
    expect(screen.getAllByText('Coming soon').length).toBe(9);
  });
});

describe('i18n & settings', () => {
  it('language switcher changes UI and persists to localStorage', async () => {
    const user = userEvent.setup();
    await renderAt('/', [{ path: '/', element: <Home /> }], 'es');
    expect(await screen.findByRole('heading', { level: 1 })).toHaveTextContent('Referencia de perfusiones');
    await user.selectOptions(screen.getByTestId('language-switcher'), 'zh');
    expect(await screen.findByRole('heading', { level: 1 })).toHaveTextContent('急诊与重症监护输注参考');
    expect(localStorage.getItem('emergency.lang')).toBe('zh');
    expect(document.documentElement.lang).toBe('zh-Hans');
    await user.selectOptions(screen.getByTestId('language-switcher'), 'pt');
    expect(await screen.findByRole('heading', { level: 1 })).toHaveTextContent('urgência');
  });

  it('theme and micro symbol settings apply', async () => {
    const user = userEvent.setup();
    await renderAt('/settings', [{ path: '/settings', element: <Settings /> }]);
    await user.click(screen.getByRole('radio', { name: 'Dark' }));
    expect(document.documentElement.classList.contains('dark')).toBe(true);
    expect(localStorage.getItem('emergency.theme')).toBe('dark');
    await user.click(screen.getByRole('radio', { name: 'µg/kg/min' }));
    expect(localStorage.getItem('emergency.micro')).toBe('µg');
    await user.click(screen.getByRole('radio', { name: 'Light' }));
    expect(document.documentElement.classList.contains('dark')).toBe(false);
  });

  it('about page shows the disclaimer', async () => {
    await renderAt('/about', [{ path: '/about', element: <About /> }]);
    expect(await screen.findByTestId('disclaimer')).toHaveTextContent('Local protocols and the treating clinician');
  });
});


describe('Clinical note diagnostic workspace', () => {
  it('creates an MCDT review card and blocks export while review is pending', async () => {
    const user = userEvent.setup();
    await renderAt('/clinical-note', [{ path: '/clinical-note', element: <ClinicalNote /> }], 'pt');
    expect(await screen.findByTestId('clinical-note-workspace')).toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: 'MCDT' }));
    await user.type(screen.getByLabelText('Nome do exame'), 'TC crânio');
    const boxes=screen.getAllByRole('textbox');
    const official=boxes.find(x=>x.parentElement?.textContent?.includes('Informe oficial / dados extraídos'));
    const ai=boxes.find(x=>x.parentElement?.textContent?.includes('Interpretação IA proposta'));
    if (!official || !ai) throw new Error('MCDT textareas not found');
    await user.type(official, 'Sem hemorragia intracraniana.');
    await user.type(ai, 'Sem achados agudos evidentes.');
    await user.click(screen.getByRole('button', { name: 'Criar cartão para revisão' }));
    expect(screen.getByTestId('mcdt-review-card')).toHaveTextContent('Pendente');
    await user.click(screen.getByRole('button', { name: 'Exportar' }));
    expect(screen.getByRole('status')).toHaveTextContent('Exportação bloqueada');
    expect(screen.getByRole('button', { name: 'PDF' })).toBeDisabled();
  });

  it('requires explicit MCDT acceptance and clinician/privacy sign-off before export', async () => {
    const user = userEvent.setup();
    await renderAt('/clinical-note', [{ path: '/clinical-note', element: <ClinicalNote /> }], 'pt');
    await user.click(screen.getByRole('button', { name: 'MCDT' }));
    await user.type(screen.getByLabelText('Nome do exame'), 'ECG');
    await user.click(screen.getByRole('button', { name: 'Criar cartão para revisão' }));
    await user.click(screen.getByRole('button', { name: 'Aceitar' }));
    await user.click(screen.getByRole('button', { name: 'Exportar' }));
    const checks=screen.getAllByRole('checkbox');
    if (!checks[0] || !checks[1]) throw new Error('export checklist missing');
    await user.click(checks[0]); await user.click(checks[1]);
    expect(screen.getByRole('button', { name: 'PDF' })).toBeEnabled();
  });

  it('routes a real upload through the trusted API and persists it only after acceptance', async () => {
    const user = userEvent.setup();
    const prepared = {
      api_version: '1.0',
      upload_id: 'upload-1',
      filename: 'tc_report.txt',
      mime_type: 'text/plain',
      size_bytes: 32,
      sha256: 'abc123',
      kind: 'ct',
      route: { kind: 'ct', target_section: 'imaging', modules: ['ct-mri-screenshot'] },
      privacy: {
        status: 'PASS',
        findings: [],
        manual_file_privacy_review_required: false,
        burned_in_identifier_review_required: true,
      },
      extracted: {
        official_report: 'TC crânio: sem hemorragia aguda.',
        ai_interpretation: null,
      },
      processing: {
        status: 'text_extracted',
        message: 'Text extracted for clinician review.',
        modules: ['ct-mri-screenshot'],
      },
      original_retained: false,
    };
    vi.spyOn(globalThis, 'fetch').mockImplementation(async (input, init) => {
      const url = String(input);
      if (url.endsWith('/api/clinical-note/upload/prepare')) {
        return new Response(JSON.stringify(prepared), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.endsWith('/api/clinical-note/upload/accept')) {
        const body = JSON.parse(String(init?.body || '{}'));
        const note = body.note;
        note.complementary_tests.imaging.push({
          kind: 'ct',
          time_label: null,
          provenance: 'ai_document_extraction',
          source_reference: 'sha256:abc123',
          official_report: body.clinician_edit.official_report,
          ai_interpretation: body.clinician_edit.ai_interpretation,
          findings: null,
          impression: null,
          limitations: [],
          privacy_checked: true,
          burned_in_identifiers_checked: true,
          routed_modules: ['ct-mri-screenshot'],
        });
        note.timeline.push({
          time_label: 'MCDT',
          event: 'Accepted ct result',
          source: 'sha256:abc123',
        });
        return new Response(JSON.stringify({ note }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      return new Response(JSON.stringify({ error: 'unexpected endpoint' }), { status: 404 });
    });

    await renderAt('/clinical-note', [{ path: '/clinical-note', element: <ClinicalNote /> }], 'pt');
    await user.click(screen.getByRole('button', { name: 'MCDT' }));
    const upload = screen.getByLabelText('Upload clínico') as HTMLInputElement;
    await user.upload(upload, new File(['TC crânio: sem hemorragia aguda.'], 'tc_report.txt', { type: 'text/plain' }));
    const reviewCard = await screen.findByTestId('mcdt-review-card');
    expect(reviewCard).toHaveTextContent('Privacidade: PASS');
    expect(reviewCard).toHaveTextContent('ct-mri-screenshot');
    expect(reviewCard).toHaveTextContent('Original não retido');
    expect(reviewCard).toHaveTextContent('Pendente');
    const checks = within(reviewCard).getAllByRole('checkbox');
    if (checks[0]) await user.click(checks[0]);
    await user.click(within(reviewCard).getByRole('button', { name: 'Aceitar' }));
    await waitFor(() => expect(reviewCard).toHaveTextContent('Aceite'));
    expect(globalThis.fetch).toHaveBeenCalledTimes(2);
  });

  it('privacy STOP catches labelled direct identifiers and blocks export', async () => {
    const user = userEvent.setup();
    await renderAt('/clinical-note', [{ path: '/clinical-note', element: <ClinicalNote /> }], 'pt');
    await user.type(screen.getByLabelText('Origem'), 'Nome: João da Silva');
    expect(screen.getByRole('alert')).toHaveTextContent('STOP');
    await user.click(screen.getByRole('button', { name: 'Exportar' }));
    expect(screen.getByRole('button', { name: 'Word (.docx)' })).toBeDisabled();
  });
});
