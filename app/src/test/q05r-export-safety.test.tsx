/**
 * Q05-R — export safety for Pediatrics (Q05-E01) and the Clinical Note (Q05-E03).
 * Synthetic responses only; no clinical values invented (pediatric fixture reused from pediatric-u08b.test.tsx).
 */
import { act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { useState } from 'react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import PediatricExport, { type PediatricReport } from '../pediatrics/PediatricExport';
import type { Fields } from '../pediatrics/catalog';
import ClinicalNote from '../pages/ClinicalNote';
import PediatricOutpatient from '../pages/PediatricOutpatient';
import { renderAt } from './render';

const response = (value: unknown, ok = true) => ({ ok, status: ok ? 200 : 500, json: async () => value }) as Response;
const b64 = (value: unknown) => btoa(unescape(encodeURIComponent(JSON.stringify(value))));
let click: ReturnType<typeof vi.spyOn>;
const created: string[] = [];
const revoked: string[] = [];
const original = { create: URL.createObjectURL, revoke: URL.revokeObjectURL };

beforeEach(() => {
  created.length = 0; revoked.length = 0;
  URL.createObjectURL = vi.fn(() => { const u = `blob:q05r-${created.length}`; created.push(u); return u; });
  URL.revokeObjectURL = vi.fn((u: string) => { revoked.push(u); });
  click = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {});
});
afterEach(() => {
  cleanup(); vi.restoreAllMocks(); vi.useRealTimers();
  URL.createObjectURL = original.create; URL.revokeObjectURL = original.revoke;
});

// ---------------------------------------------------------------- Pediatrics (Q05-E01)
const paracetamol = 'paracetamol-pain-fever-home';
const result = { dose_mg: 525, dose_mg_per_kg: 15, dosing_weight_kg: 35, volume_per_dose: { exact_ml: 21.875, rounded_0_1_ml: 21.9 },
  total_doses: 8, estimated_total_course_ml: 175 };
const ok = { blocked: false, result, export_report: { snapshot: {}, sections: [['Resultado', ['YELLOW', 'CLINICALLY_PENDING']]] },
  safety: { prescription_status: 'REVIEW_REQUIRED', alerts: [] } };
const CONFIRM = 'Confirmo haber revisado el resultado completo, sus límites y advertencias';
const jsonExport = (snapshot: unknown) => response({ filename: 'pediatric-result.json', mime_type: 'application/json', content_base64: b64({ snapshot, sections: [] }) });

async function pediatricCalculated(first: unknown = ok) {
  const fetcher = vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(response(first));
  await renderAt(`/pediatrics?regimen=${paracetamol}`, [{ path: '/pediatrics', element: <PediatricOutpatient /> }]);
  fireEvent.change(screen.getByLabelText('Peso real (kg)'), { target: { value: '35' } });
  fireEvent.click(screen.getByRole('button', { name: 'Comprobar y calcular' }));
  const region = await screen.findByRole('region', { name: 'Resultado pediátrico' });
  return { fetcher, region };
}

describe('Q05-R pediatrics — confirmation gate', () => {
  it('without confirmation: no export, no print button, and the result is excluded from browser printing', async () => {
    const { region } = await pediatricCalculated();
    expect(screen.queryByRole('button', { name: /Exportar/ })).toBeNull();
    expect(screen.queryByRole('button', { name: 'Imprimir resultado' })).toBeNull();
    expect(region.className).toMatch(/(^|\s)print:hidden(\s|$)/);
    expect(screen.getByTestId('pediatric-print-blocked').textContent).toMatch(/confirmar la revisión/);
    fireEvent.click(screen.getByRole('checkbox', { name: CONFIRM }));
    expect(region.className).not.toMatch(/(^|\s)print:hidden(\s|$)/);
    expect(screen.queryByTestId('pediatric-print-blocked')).toBeNull();
  });

  it('confirmed JSON export downloads only when the file carries the confirmed result and CLINICALLY_PENDING', async () => {
    const { fetcher } = await pediatricCalculated();
    fetcher.mockResolvedValueOnce(jsonExport({ clinical_status: 'CLINICALLY_PENDING', result }));
    fireEvent.click(screen.getByRole('checkbox', { name: CONFIRM }));
    fireEvent.click(screen.getByRole('button', { name: 'Exportar JSON' }));
    await waitFor(() => expect(click).toHaveBeenCalledOnce());
    expect(screen.queryByText(/no corresponde/)).toBeNull();
  });

  it('a JSON export whose result differs from the confirmed one is discarded', async () => {
    const { fetcher } = await pediatricCalculated();
    fetcher.mockResolvedValueOnce(jsonExport({ clinical_status: 'CLINICALLY_PENDING', result: { ...result, dose_mg: 526 } }));
    fireEvent.click(screen.getByRole('checkbox', { name: CONFIRM }));
    fireEvent.click(screen.getByRole('button', { name: 'Exportar JSON' }));
    expect(await screen.findByText(/no corresponde al cálculo confirmado/)).toBeTruthy();
    expect(click).not.toHaveBeenCalled();
    expect(created).toHaveLength(0);
  });

  it('a JSON export without CLINICALLY_PENDING is discarded', async () => {
    const { fetcher } = await pediatricCalculated();
    fetcher.mockResolvedValueOnce(jsonExport({ clinical_status: 'GREEN', result }));
    fireEvent.click(screen.getByRole('checkbox', { name: CONFIRM }));
    fireEvent.click(screen.getByRole('button', { name: 'Exportar JSON' }));
    expect(await screen.findByText(/no corresponde al cálculo confirmado/)).toBeTruthy();
    expect(click).not.toHaveBeenCalled();
  });

  it('a type change (true vs 1) in the exported result is a mismatch', async () => {
    const { fetcher } = await pediatricCalculated();
    fetcher.mockResolvedValueOnce(jsonExport({ clinical_status: 'CLINICALLY_PENDING', result: { ...result, total_doses: true } }));
    fireEvent.click(screen.getByRole('checkbox', { name: CONFIRM }));
    fireEvent.click(screen.getByRole('button', { name: 'Exportar JSON' }));
    expect(await screen.findByText(/no corresponde al cálculo confirmado/)).toBeTruthy();
    expect(click).not.toHaveBeenCalled();
  });

  it('a file of another format than requested is discarded', async () => {
    const { fetcher } = await pediatricCalculated();
    fetcher.mockResolvedValueOnce(response({ filename: 'pediatric-result.json', mime_type: 'application/json', content_base64: 'e30=' }));
    fireEvent.click(screen.getByRole('checkbox', { name: CONFIRM }));
    fireEvent.click(screen.getByRole('button', { name: 'Exportar PDF' }));
    expect(await screen.findByRole('alert')).toBeTruthy();
    expect(click).not.toHaveBeenCalled();
  });

  it('network error: message, no download, buttons usable again', async () => {
    const { fetcher } = await pediatricCalculated();
    fetcher.mockRejectedValueOnce(new TypeError('Failed to fetch'));
    fireEvent.click(screen.getByRole('checkbox', { name: CONFIRM }));
    fireEvent.click(screen.getByRole('button', { name: 'Exportar DOCX' }));
    expect(await screen.findByText('Failed to fetch')).toBeTruthy();
    expect(click).not.toHaveBeenCalled();
    expect(screen.getByRole('button', { name: 'Exportar DOCX' })).toBeEnabled();
  });

  it('unconfirming while the export is in flight discards the late file', async () => {
    let finish!: (value: Response) => void;
    const { fetcher } = await pediatricCalculated();
    fetcher.mockImplementationOnce(() => new Promise((resolve) => { finish = resolve; }));
    const box = screen.getByRole('checkbox', { name: CONFIRM });
    fireEvent.click(box);
    fireEvent.click(screen.getByRole('button', { name: 'Exportar JSON' }));
    await waitFor(() => expect(fetcher).toHaveBeenCalledTimes(2));
    fireEvent.click(box);
    await act(async () => finish(jsonExport({ clinical_status: 'CLINICALLY_PENDING', result })));
    expect(click).not.toHaveBeenCalled();
  });

  it('route change (page unmount) while exporting produces no download', async () => {
    let finish!: (value: Response) => void;
    const { fetcher } = await pediatricCalculated();
    fetcher.mockImplementationOnce(() => new Promise((resolve) => { finish = resolve; }));
    fireEvent.click(screen.getByRole('checkbox', { name: CONFIRM }));
    fireEvent.click(screen.getByRole('button', { name: 'Exportar JSON' }));
    await waitFor(() => expect(fetcher).toHaveBeenCalledTimes(2));
    cleanup();
    await act(async () => finish(jsonExport({ clinical_status: 'CLINICALLY_PENDING', result })));
    expect(click).not.toHaveBeenCalled();
  });

  it.each([
    ['STOP', { ...ok, safety: { prescription_status: 'BLOCKED', alerts: [{ severity: 'STOP', message: 'Detener', action: '' }] } }],
    ['BLOCKED', { blocked: true, safety: { prescription_status: 'BLOCKED', alerts: [{ severity: 'STOP', message: 'Detener', action: '' }] } }],
  ])('%s never offers confirmation, export or print', async (_name, body) => {
    await pediatricCalculated(body);
    expect(screen.queryByRole('checkbox', { name: CONFIRM })).toBeNull();
    expect(screen.queryByRole('button', { name: /Exportar|Imprimir/ })).toBeNull();
    expect(document.querySelector('.pediatric-print-sheet')).toBeNull();
  });

  it('ERROR (malformed server response) shows no result, confirmation or export', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(response({ ...ok, result: { dose_mg: -1 } }));
    await renderAt(`/pediatrics?regimen=${paracetamol}`, [{ path: '/pediatrics', element: <PediatricOutpatient /> }]);
    fireEvent.change(screen.getByLabelText('Peso real (kg)'), { target: { value: '35' } });
    fireEvent.click(screen.getByRole('button', { name: 'Comprobar y calcular' }));
    expect(await screen.findByText(/Respuesta del servidor no válida/)).toBeTruthy();
    expect(screen.queryByRole('region', { name: 'Resultado pediátrico' })).toBeNull();
    expect(screen.queryByRole('checkbox', { name: CONFIRM })).toBeNull();
  });

  it('component guard: new props during a request discard the earlier response', async () => {
    let finish!: (value: Response) => void;
    vi.spyOn(globalThis, 'fetch').mockImplementationOnce(() => new Promise((resolve) => { finish = resolve; }));
    const props = { report: ok.export_report as PediatricReport, calculation: { regimen_id: paracetamol } };
    let swap!: () => void;
    function Host() {
      const [current, setCurrent] = useState<Fields>(result);
      swap = () => setCurrent({ ...result, dose_mg: 600 });
      return <PediatricExport {...props} result={current} />;
    }
    render(<Host />);
    fireEvent.click(screen.getByRole('button', { name: 'Exportar JSON' }));
    act(() => swap());
    await act(async () => finish(jsonExport({ clinical_status: 'CLINICALLY_PENDING', result })));
    expect(click).not.toHaveBeenCalled();
  });
});

// ---------------------------------------------------------------- Clinical note (Q05-E03)
const exportFile = { filename: 'clinical-note.pdf', mime_type: 'application/pdf', content_base64: 'JVBERi0=' };
const PRIVACY = /Identificadores diretos removidos/;
const REVIEWED = /Médico reviu e valida/;

function clinicalNoteFetch(exportResponse: () => Promise<Response>, preflight: () => Promise<Response> = async () => response({ blocked: false, findings: [] })) {
  return vi.spyOn(globalThis, 'fetch').mockImplementation(async (url) => {
    const path = String(url);
    if (path.endsWith('/api/clinical-note/preflight')) return preflight();
    if (path.endsWith('/api/clinical-note/export')) return exportResponse();
    throw new Error(`unexpected ${path}`);
  });
}
async function noteReadyToExport() {
  await renderAt('/clinical-note', [{ path: '/clinical-note', element: <ClinicalNote /> }], 'pt');
  fireEvent.click(screen.getByRole('button', { name: 'Exportar' }));
  fireEvent.click(screen.getByLabelText(PRIVACY));
  fireEvent.click(screen.getByLabelText(REVIEWED));
  expect(screen.getByRole('button', { name: 'PDF' })).toBeEnabled();
}
const deferred = () => { let resolve!: (r: Response) => void; const promise = new Promise<Response>((r) => { resolve = r; }); return { promise, resolve }; };

describe('Q05-R clinical note — stale export responses', () => {
  it('valid export downloads once and revokes the temporary URL', async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    clinicalNoteFetch(async () => response(exportFile));
    await noteReadyToExport();
    fireEvent.click(screen.getByRole('button', { name: 'PDF' }));
    await waitFor(() => expect(click).toHaveBeenCalledOnce());
    await act(async () => { vi.advanceTimersByTime(5_000); });
    expect(revoked).toEqual(created);
  });

  it('editing the note while the export is in flight discards the late file', async () => {
    const d = deferred();
    const fetcher = clinicalNoteFetch(() => d.promise);
    await noteReadyToExport();
    fireEvent.click(screen.getByRole('button', { name: 'PDF' }));
    await waitFor(() => expect(fetcher).toHaveBeenCalledTimes(2));
    fireEvent.change(screen.getByLabelText('Idade'), { target: { value: '40' } });
    await act(async () => d.resolve(response(exportFile)));
    expect(click).not.toHaveBeenCalled();
    expect(created).toHaveLength(0);
  });

  it('editing during the preflight never starts the export', async () => {
    const d = deferred();
    const fetcher = clinicalNoteFetch(async () => response(exportFile), () => d.promise);
    await noteReadyToExport();
    fireEvent.click(screen.getByRole('button', { name: 'PDF' }));
    await waitFor(() => expect(fetcher).toHaveBeenCalledTimes(1));
    fireEvent.change(screen.getByLabelText('Idade'), { target: { value: '40' } });
    await act(async () => d.resolve(response({ blocked: false, findings: [] })));
    expect(fetcher).toHaveBeenCalledTimes(1);
    expect(click).not.toHaveBeenCalled();
  });

  it('withdrawing the clinician review while exporting discards the late file', async () => {
    const d = deferred();
    const fetcher = clinicalNoteFetch(() => d.promise);
    await noteReadyToExport();
    fireEvent.click(screen.getByRole('button', { name: 'PDF' }));
    await waitFor(() => expect(fetcher).toHaveBeenCalledTimes(2));
    fireEvent.click(screen.getByLabelText(REVIEWED));
    await act(async () => d.resolve(response(exportFile)));
    expect(click).not.toHaveBeenCalled();
  });

  it('leaving the page (unmount / route change) while exporting produces no download', async () => {
    const d = deferred();
    const fetcher = clinicalNoteFetch(() => d.promise);
    await noteReadyToExport();
    fireEvent.click(screen.getByRole('button', { name: 'PDF' }));
    await waitFor(() => expect(fetcher).toHaveBeenCalledTimes(2));
    cleanup();
    await act(async () => d.resolve(response(exportFile)));
    expect(click).not.toHaveBeenCalled();
  });

  it('network error: message and no download (no partial document)', async () => {
    clinicalNoteFetch(async () => { throw new TypeError('Failed to fetch'); });
    await noteReadyToExport();
    fireEvent.click(screen.getByRole('button', { name: 'PDF' }));
    expect(await screen.findByText('Failed to fetch')).toBeTruthy();
    expect(click).not.toHaveBeenCalled();
  });

  it('invalid base64 or a different format than requested: no download', async () => {
    clinicalNoteFetch(async () => response({ ...exportFile, content_base64: '###' }));
    await noteReadyToExport();
    fireEvent.click(screen.getByRole('button', { name: 'PDF' }));
    expect(await screen.findByRole('alert')).toBeTruthy();
    expect(click).not.toHaveBeenCalled();
    cleanup();
    clinicalNoteFetch(async () => response({ ...exportFile, filename: 'clinical-note.docx', mime_type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' }));
    await noteReadyToExport();
    fireEvent.click(screen.getByRole('button', { name: 'PDF' }));
    expect(await screen.findByRole('alert')).toBeTruthy();
    expect(click).not.toHaveBeenCalled();
  });

  it('a backend error response produces no download', async () => {
    clinicalNoteFetch(async () => response({ error: 'Export blocked' }, false));
    await noteReadyToExport();
    fireEvent.click(screen.getByRole('button', { name: 'PDF' }));
    expect(await screen.findByText('Export blocked')).toBeTruthy();
    expect(click).not.toHaveBeenCalled();
  });
});
