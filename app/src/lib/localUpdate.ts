/** Per-tab update consent only. No patient fields, browser storage or automatic reload. */
type UpdateSnapshot = { available: boolean; applying: boolean; failed: boolean };
let state: UpdateSnapshot = { available: false, applying: false, failed: false };
const listeners = new Set<() => void>();
let updater: ((reload?: boolean) => Promise<void>) | undefined;
let canReload = () => false;
let reload = () => window.location.reload();
let accepted = false;
let controlledUpdate = false;

function publish(next: UpdateSnapshot) { state = next; for (const listener of listeners) listener(); }
export const localUpdateSnapshot = () => state;
export function subscribeLocalUpdate(listener: () => void) { listeners.add(listener); return () => { listeners.delete(listener); }; }
export function configureLocalUpdater(update: (reload?: boolean) => Promise<void>) { updater = update; }
export function setLocalReloadGuard(guard: () => boolean) {
  canReload = guard;
  return () => { if (canReload === guard) canReload = () => false; };
}
export function markLocalUpdateAvailable() { publish({ available: true, applying: false, failed: false }); }

/** Plugin callback also runs for an update initiated in another tab: never grant that tab reload consent. */
export function localWorkerNeedsReload() {
  controlledUpdate = true;
  if (accepted && canReload()) { accepted = false; reload(); }
  else { accepted = false; markLocalUpdateAvailable(); }
}

export async function requestLocalUpdate(): Promise<boolean> {
  if (!state.available || state.applying || !updater || !canReload()) return false;
  accepted = true;
  publish({ ...state, applying: true, failed: false });
  try {
    if (controlledUpdate) localWorkerNeedsReload();
    else await updater(true);
    return true;
  } catch {
    accepted = false;
    publish({ available: true, applying: false, failed: true });
    return false;
  }
}

/** Test harness observer, not an application navigation API. */
export function resetLocalUpdateForTest(reloadObserver?: () => void) {
  updater = undefined; accepted = false; controlledUpdate = false; canReload = () => false;
  reload = reloadObserver ?? (() => window.location.reload());
  publish({ available: false, applying: false, failed: false });
}
