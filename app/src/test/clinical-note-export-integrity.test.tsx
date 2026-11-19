import { fireEvent, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import ClinicalNote from '../pages/ClinicalNote';
import * as api from '../clinical-note/api';
import { renderAt } from './render';

beforeEach(() => {
  vi.restoreAllMocks();
  localStorage.clear();
});

const response = (body: unknown, status = 200) => new Response(JSON.stringify(body), {
  status, headers: { 'Content-Type': 'application/json' },
});
async function openExport() {
  const user = userEvent.setup();
  await renderAt('/clinical-note', [{ path: '/clinical-note', element: <ClinicalNote /> }], 'pt');
  await user.click(screen.getByRole('button', { name: 'Exportar' }));
  await user.click(screen.getByRole('checkbox', { name: /Identificadores diretos removidos/ }));
  await user.click(screen.getByRole('checkbox', { name: /Médico reviu e valida/ }));
  return user;
}

describe('Synthetic note export and privacy contracts', () => {
  it.each(['json', 'pdf', 'docx'] as const)('preserves all entered fields through preflight and %s export, then invalidates review after editing', async (format) => {
    const requests: { path: string; body: Record<string, unknown> }[] = [];
    const mime = { json: 'application/json', pdf: 'application/pdf', docx: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' }[format];
    vi.spyOn(globalThis, 'fetch').mockImplementation(async (input, init) => {
      const path = String(input);
      requests.push({ path, body: JSON.parse(String(init?.body)) as Record<string, unknown> });
      if (path.endsWith('/preflight')) return response({ blocked: false, findings: [] });
      expect(path).toMatch(/\/api\/clinical-note\/export$/);
      return response({ filename: `synthetic.${format}`, mime_type: mime, content_base64: btoa('SYNTHETIC') });
    });
    const download = vi.spyOn(api, 'downloadBlob').mockImplementation(() => {});
    const user = userEvent.setup();
    await renderAt('/clinical-note', [{ path: '/clinical-note', element: <ClinicalNote /> }], 'pt');
    const change = (label: string, value: string) => fireEvent.change(screen.getByLabelText(label), { target: { value } });
    change('Idade', '44'); change('Sexo', 'female'); change('Origem', 'Contexto sintético');
    change('Motivo de consulta', 'Cenário sintético');
    change('História da doença atual', 'Texto sintético\nsem dados reais');
    change('Antecedentes · um por linha', 'Antecedente sintético');
    change('Medicação habitual · um por linha', 'Amostra A\nAmostra B');
    change('Alergias · uma por linha', 'Substância sintética');
    await user.click(screen.getByRole('button', { name: 'Exame' }));
    await user.click(screen.getByRole('button', { name: 'Adicionar constantes' }));
    expect(screen.getByText('Sem eventos aceites ainda.')).toBeInTheDocument();
    change('Hora', 'synthetic-t0'); change('TA', '120/80'); change('FC', '80'); change('T °C', '36.5');
    await user.click(screen.getByRole('button', { name: 'Adicionar constantes' }));
    change('Exploração', 'Exploração sintética');
    await user.click(screen.getByRole('button', { name: 'Plano' }));
    change('Plano médico', 'Plano sintético preservado');
    await user.click(screen.getByRole('button', { name: 'Exportar' }));
    const label = { json: 'JSON', pdf: 'PDF', docx: 'Word (.docx)' }[format];
    expect(screen.getByRole('button', { name: label })).toBeDisabled();
    await user.click(screen.getByRole('checkbox', { name: /Identificadores diretos removidos/ }));
    expect(screen.getByRole('button', { name: label })).toBeDisabled();
    await user.click(screen.getByRole('checkbox', { name: /Médico reviu e valida/ }));
    await user.click(screen.getByRole('button', { name: label }));
    await waitFor(() => expect(download).toHaveBeenCalledTimes(1));
    expect(requests.map(r => r.path)).toEqual(['/api/clinical-note/preflight', '/api/clinical-note/export']);
    const note = requests[0]?.body.note;
    expect(requests[1]?.body.note).toEqual(note);
    expect(requests[1]?.body.format).toBe(format);
    expect(note).toMatchObject({
      encounter: { age: { years: 44 }, sex: 'female', origin: 'Contexto sintético' },
      history: {
        chief_complaint: 'Cenário sintético', present_illness: 'Texto sintético\nsem dados reais',
        past_medical_history: ['Antecedente sintético'],
        chronic_medications: [{ name: 'Amostra A', dose: null }, { name: 'Amostra B', dose: null }],
        allergies: [{ substance: 'Substância sintética' }],
      },
      exam: { general: 'Exploração sintética', vitals: [{ time_label: 'synthetic-t0', bp: '120/80', hr: 80, temperature_c: 36.5 }] },
      assessment: { treatment_suggestions: [{ action: 'Plano sintético preservado' }] },
      clinician_validation: { reviewed: true, reviewer_role: 'treating_clinician' },
      privacy: { direct_identifiers_removed: true, export_allowed: true },
    });
    expect(download.mock.calls[0]?.[0]).toBe(`synthetic.${format}`);
    expect(download.mock.calls[0]?.[1].type).toBe(mime);
    expect(download.mock.calls[0]?.[1].size).toBe(9);
    await user.click(screen.getByRole('button', { name: 'História' }));
    change('Motivo de consulta', 'Cenário sintético alterado');
    await user.click(screen.getByRole('button', { name: 'Exportar' }));
    expect(screen.getByRole('checkbox', { name: /Médico reviu e valida/ })).not.toBeChecked();
    expect(screen.getByRole('button', { name: label })).toBeDisabled();
    expect(requests).toHaveLength(2);
  });

  it.each(['preflight', 'backend', 'invalid-json', 'network'] as const)('prevents a download when %s fails and restores the export control', async (mode) => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockImplementation(async (input) => {
      if (String(input).endsWith('/preflight')) return response({ blocked: mode === 'preflight', findings: mode === 'preflight' ? [{ severity: 'STOP', code: 'SYNTHETIC', message: 'SYNTHETIC_STOP' }] : [] });
      if (mode === 'network') throw new Error('SYNTHETIC_NETWORK_ERROR');
      if (mode === 'invalid-json') return new Response('synthetic-invalid-json', { status: 503 });
      return response({ error: 'SYNTHETIC_BACKEND_DENIED' }, 403);
    });
    const download = vi.spyOn(api, 'downloadBlob').mockImplementation(() => {});
    const user = await openExport();
    await user.click(screen.getByRole('button', { name: 'PDF' }));
    const expected = { preflight: 'SYNTHETIC_STOP', backend: 'SYNTHETIC_BACKEND_DENIED', 'invalid-json': 'Invalid backend response', network: 'SYNTHETIC_NETWORK_ERROR' }[mode];
    expect(await screen.findByRole('alert')).toHaveTextContent(expected);
    expect(download).not.toHaveBeenCalled();
    expect(fetchMock).toHaveBeenCalledTimes(mode === 'preflight' ? 1 : 2);
    expect(screen.getByRole('button', { name: 'PDF' })).toBeEnabled();
  });
});
