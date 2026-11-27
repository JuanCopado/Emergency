import { lazy, Suspense } from 'react';
import { act, fireEvent, render, screen } from '@testing-library/react';
import { Link, MemoryRouter, Route, Routes } from 'react-router-dom';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { ClinicalNoteDraftProvider, useNoteDraftField } from '../clinical-note/draft';
import { IndividualRouteGuard } from '../components/IndividualRouteGuard';
import { localWorkerNeedsReload, resetLocalUpdateForTest } from '../lib/localUpdate';
vi.mock('react-i18next', () => ({ useTranslation: () => ({ i18n: { language: 'en' } }) }));

function Note() {
  const [value, setValue] = useNoteDraftField('hpi');
  return <><input aria-label="Synthetic episode" value={value} onChange={e => setValue(e.target.value)} />
    <Link to="/pediatrics">Unseen pediatrics</Link><Link to="/procedures">Unseen procedures</Link></>;
}
function mount(load: () => Promise<{ default: () => React.JSX.Element }>) {
  const Unseen = lazy(load);
  render(<MemoryRouter initialEntries={['/clinical-note']}><ClinicalNoteDraftProvider>
    <IndividualRouteGuard individual revision={'a'.repeat(40)}>{location => <Suspense fallback="Loading">
      <Routes location={location}><Route path="/clinical-note" element={<Note />} />
        <Route path="/pediatrics" element={<Unseen />} /><Route path="/procedures" element={<Unseen />} /></Routes>
    </Suspense>}</IndividualRouteGuard>
  </ClinicalNoteDraftProvider></MemoryRouter>);
}
describe('individual lazy routes preserve the draft across worker replacement', () => {
  beforeEach(() => { resetLocalUpdateForTest(vi.fn()); });
  afterEach(() => { vi.unstubAllGlobals(); vi.restoreAllMocks(); });
  it('does not invoke missing old lazy imports after another tab activates an update', async () => {
    const missing = vi.fn(() => Promise.reject(new Error('Missing old chunk')));
    mount(missing);
    fireEvent.change(screen.getByLabelText('Synthetic episode'), { target: { value: 'SYNTHETIC RETAINED' } });
    act(localWorkerNeedsReload);
    fireEvent.click(screen.getByText('Unseen pediatrics'));
    expect(await screen.findByTestId('local-stale-navigation')).toBeVisible();
    fireEvent.click(screen.getByText('Unseen procedures'));
    expect(missing).not.toHaveBeenCalled();
    expect(screen.getByLabelText('Synthetic episode')).toHaveValue('SYNTHETIC RETAINED');
  });
  it('checks runtime identity before an unseen import and refuses mismatched bytes', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => ({ source_sha: 'b'.repeat(40) }) }));
    const missing = vi.fn(() => Promise.reject(new Error('Missing old chunk')));
    mount(missing); fireEvent.click(screen.getByText('Unseen pediatrics'));
    expect(await screen.findByTestId('local-stale-navigation')).toBeVisible();
    expect(missing).not.toHaveBeenCalled();
  });
  it('retains the provider after an actual lazy rejection in a runtime-change race', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => ({ source_sha: 'a'.repeat(40) }) }));
    const log = vi.spyOn(console, 'error').mockImplementation(() => {});
    mount(() => Promise.reject(new Error('Synthetic old chunk removed after identity check')));
    fireEvent.change(screen.getByLabelText('Synthetic episode'), { target: { value: 'SYNTHETIC SURVIVES REJECTION' } });
    fireEvent.click(screen.getByText('Unseen pediatrics'));
    fireEvent.click(await screen.findByText('Return to the open note'));
    expect(await screen.findByLabelText('Synthetic episode')).toHaveValue('SYNTHETIC SURVIVES REJECTION');
    log.mockRestore();
  });
  it('allows a first cached frontend route offline when no update was observed', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Offline')));
    const load = vi.fn(async () => ({ default: () => <p>Cached frontend screen</p> }));
    mount(load); fireEvent.click(screen.getByText('Unseen pediatrics'));
    expect(await screen.findByText('Cached frontend screen')).toBeVisible();
    expect(load).toHaveBeenCalledOnce();
  });
});
