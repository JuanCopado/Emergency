import { lazy, Suspense, useState } from 'react';
import { act, fireEvent, render, screen } from '@testing-library/react';
import { Link, MemoryRouter, Route, Routes } from 'react-router-dom';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { ClinicalNoteDraftProvider, useNoteDraftField } from '../clinical-note/draft';
import { IndividualRouteGuard } from '../components/IndividualRouteGuard';
import { localWorkerNeedsReload, resetLocalUpdateForTest } from '../lib/localUpdate';
vi.mock('react-i18next', () => ({ useTranslation: () => ({ i18n: { language: 'en' } }) }));

function Note() {
  const [value, setValue] = useNoteDraftField('hpi');
  const [localValue, setLocalValue] = useState('');
  return <><input aria-label="Synthetic episode" value={value} onChange={e => setValue(e.target.value)} />
    <input aria-label="Synthetic screen-local form" value={localValue} onChange={e => setLocalValue(e.target.value)} />
    <Link to="?weight=80#result" replace>Change same-screen query and hash</Link>
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
  it('retains the current component instance and local form when a denied URL gets a new history key', async () => {
    const missing = vi.fn(() => Promise.reject(new Error('Missing old chunk')));
    mount(missing);
    const localInput = screen.getByLabelText('Synthetic screen-local form');
    fireEvent.change(localInput, { target: { value: 'SYNTHETIC LOCAL VALUES' } });
    act(localWorkerNeedsReload);
    fireEvent.click(screen.getByText('Unseen pediatrics'));
    await screen.findByTestId('local-stale-navigation');
    // A second denied attempt also lets React flush the replace-navigation from
    // the first attempt, proving that its new location.key did not reset state.
    fireEvent.click(screen.getByText('Unseen procedures'));
    expect(screen.getByLabelText('Synthetic screen-local form')).toBe(localInput);
    expect(localInput).toHaveValue('SYNTHETIC LOCAL VALUES');
    expect(missing).not.toHaveBeenCalled();
  });
  it('retains the component instance and local form during ordinary same-screen query/hash replacement', async () => {
    const missing = vi.fn(() => Promise.reject(new Error('Unvisited lazy route')));
    mount(missing);
    const localInput = screen.getByLabelText('Synthetic screen-local form');
    fireEvent.change(localInput, { target: { value: 'SYNTHETIC QUERY-BOUND FORM' } });
    fireEvent.click(screen.getByText('Change same-screen query and hash'));
    expect(screen.getByLabelText('Synthetic screen-local form')).toBe(localInput);
    expect(localInput).toHaveValue('SYNTHETIC QUERY-BOUND FORM');
    expect(missing).not.toHaveBeenCalled();
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
