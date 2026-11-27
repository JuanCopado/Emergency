import { act, fireEvent, render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { ClinicalNoteDraftProvider, useClinicalNoteDraft, useNoteDraftField } from '../clinical-note/draft';
import { LocalUpdateNotice } from '../components/LocalUpdateNotice';
import { configureLocalUpdater, localWorkerNeedsReload, markLocalUpdateAvailable, resetLocalUpdateForTest } from '../lib/localUpdate';

vi.mock('react-i18next', () => ({ useTranslation: () => ({ i18n: { language: 'en' } }) }));

function DraftControls() {
  const [hpi, setHpi] = useNoteDraftField('hpi');
  const { reset } = useClinicalNoteDraft();
  return <><input aria-label="Synthetic note" value={hpi} onChange={event => setHpi(event.target.value)} />
    <button onClick={reset}>Finish synthetic encounter</button></>;
}
function mount() {
  render(<ClinicalNoteDraftProvider><DraftControls /><LocalUpdateNotice /></ClinicalNoteDraftProvider>);
}

describe('installed update notice protects the current encounter', () => {
  const reload = vi.fn();
  const update = vi.fn().mockResolvedValue(undefined);
  beforeEach(() => { reload.mockClear(); update.mockClear(); resetLocalUpdateForTest(reload); configureLocalUpdater(update); });

  it('does not show an update before a waiting worker is observed', () => {
    mount(); expect(screen.queryByTestId('local-update-notice')).not.toBeInTheDocument();
  });
  it('requires confirmation and rechecks the current draft instead of clearing it', async () => {
    mount(); act(markLocalUpdateAvailable);
    const apply = screen.getByTestId('local-update-apply');
    const confirm = screen.getByTestId('local-update-confirm');
    expect(apply).toBeDisabled(); fireEvent.click(confirm); expect(apply).toBeEnabled();
    fireEvent.change(screen.getByLabelText('Synthetic note'), { target: { value: 'INERT SYNTHETIC EPISODE' } });
    expect(confirm).not.toBeChecked(); expect(confirm).toBeDisabled(); expect(apply).toBeDisabled();
    act(localWorkerNeedsReload);
    expect(screen.getByLabelText('Synthetic note')).toHaveValue('INERT SYNTHETIC EPISODE');
    expect(reload).not.toHaveBeenCalled(); expect(update).not.toHaveBeenCalled();
    fireEvent.click(screen.getByText('Finish synthetic encounter'));
    expect(confirm).toBeEnabled(); expect(apply).toBeDisabled(); fireEvent.click(confirm);
    await act(async () => { fireEvent.click(apply); });
    expect(reload).toHaveBeenCalledTimes(1);
  });
  it('defers the prompt without modifying an open draft', () => {
    mount(); fireEvent.change(screen.getByLabelText('Synthetic note'), { target: { value: 'SYNTHETIC ONLY' } });
    act(markLocalUpdateAvailable); fireEvent.click(screen.getByText('Later'));
    expect(screen.queryByTestId('local-update-notice')).not.toBeInTheDocument();
    expect(screen.getByLabelText('Synthetic note')).toHaveValue('SYNTHETIC ONLY');
    fireEvent.click(screen.getByText('Update pending'));
    expect(screen.getByTestId('local-update-apply')).toBeDisabled(); expect(reload).not.toHaveBeenCalled();
  });
});
