import { beforeEach, describe, expect, it, vi } from 'vitest';
import { configureLocalUpdater, localUpdateSnapshot, localWorkerNeedsReload, markLocalUpdateAvailable,
  requestLocalUpdate, resetLocalUpdateForTest, setLocalReloadGuard, subscribeLocalUpdate } from '../lib/localUpdate';
import { localRevisionHeaders } from '../lib/individualTransport';

describe('individual update consent and transport identity', () => {
  const reload = vi.fn();
  beforeEach(() => { reload.mockClear(); resetLocalUpdateForTest(reload); });

  it('does not add a local revision contract to ordinary builds', () => {
    expect(localRevisionHeaders('0', 'a'.repeat(40))).toEqual({});
    expect(localRevisionHeaders('1', 'a'.repeat(40))).toEqual({ 'X-Emergency-Revision': 'a'.repeat(40) });
    expect(localRevisionHeaders('1', '')).toEqual({ 'X-Emergency-Revision': '' });
  });
  it('never applies an update without an available prompt and explicit current-tab guard', async () => {
    const update = vi.fn().mockResolvedValue(undefined); configureLocalUpdater(update);
    expect(await requestLocalUpdate()).toBe(false);
    markLocalUpdateAvailable(); expect(await requestLocalUpdate()).toBe(false);
    expect(update).not.toHaveBeenCalled(); expect(reload).not.toHaveBeenCalled();
  });
  it('waits for worker control after consent instead of forcing an early page reload', async () => {
    const update = vi.fn().mockResolvedValue(undefined); configureLocalUpdater(update);
    setLocalReloadGuard(() => true); markLocalUpdateAvailable();
    expect(await requestLocalUpdate()).toBe(true); expect(update).toHaveBeenCalledWith(true);
    expect(reload).not.toHaveBeenCalled(); localWorkerNeedsReload(); expect(reload).toHaveBeenCalledTimes(1);
  });
  it('does not reload a tab merely because another tab activates a new worker', () => {
    setLocalReloadGuard(() => true); markLocalUpdateAvailable(); localWorkerNeedsReload();
    expect(reload).not.toHaveBeenCalled(); expect(localUpdateSnapshot().available).toBe(true);
  });
  it('rechecks episode safety when the worker changes after a click', async () => {
    let safe = true; configureLocalUpdater(vi.fn().mockResolvedValue(undefined));
    setLocalReloadGuard(() => safe); markLocalUpdateAvailable(); await requestLocalUpdate();
    safe = false; localWorkerNeedsReload();
    expect(reload).not.toHaveBeenCalled(); expect(localUpdateSnapshot().applying).toBe(false);
  });
  it('requires fresh per-tab consent even after an external update controls the tab', async () => {
    configureLocalUpdater(vi.fn().mockResolvedValue(undefined));
    markLocalUpdateAvailable(); localWorkerNeedsReload();
    expect(await requestLocalUpdate()).toBe(false); expect(reload).not.toHaveBeenCalled();
    setLocalReloadGuard(() => true); expect(await requestLocalUpdate()).toBe(true);
    expect(reload).toHaveBeenCalledTimes(1);
  });
  it('keeps preferences and reports failure without clearing storage or reloading', async () => {
    localStorage.setItem('emergency.theme', 'dark');
    const set = vi.spyOn(Storage.prototype, 'setItem'); const remove = vi.spyOn(Storage.prototype, 'removeItem');
    configureLocalUpdater(vi.fn().mockRejectedValue(new Error('worker unavailable')));
    setLocalReloadGuard(() => true); markLocalUpdateAvailable();
    expect(await requestLocalUpdate()).toBe(false); expect(localUpdateSnapshot().failed).toBe(true);
    expect(reload).not.toHaveBeenCalled(); expect(localStorage.getItem('emergency.theme')).toBe('dark');
    expect(set).not.toHaveBeenCalled(); expect(remove).not.toHaveBeenCalled();
    set.mockRestore(); remove.mockRestore();
  });
  it('drops the guard when the owning component unmounts', async () => {
    configureLocalUpdater(vi.fn().mockResolvedValue(undefined)); markLocalUpdateAvailable();
    const dispose = setLocalReloadGuard(() => true); dispose();
    expect(await requestLocalUpdate()).toBe(false);
  });
  it('notifies subscribers and stops notifying after unsubscribe', () => {
    const listener = vi.fn(); const stop = subscribeLocalUpdate(listener);
    markLocalUpdateAvailable(); expect(listener).toHaveBeenCalledTimes(1);
    stop(); markLocalUpdateAvailable(); expect(listener).toHaveBeenCalledTimes(1);
  });
  it('does not issue duplicate worker activation messages while applying', async () => {
    const update = vi.fn().mockResolvedValue(undefined); configureLocalUpdater(update);
    setLocalReloadGuard(() => true); markLocalUpdateAvailable();
    expect(await requestLocalUpdate()).toBe(true); expect(await requestLocalUpdate()).toBe(false);
    expect(update).toHaveBeenCalledTimes(1);
  });
});
