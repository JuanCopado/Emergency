import { act, fireEvent, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it } from 'vitest';
import CountryReferences from '../components/CountryReferences';
import Settings from '../pages/Settings';
import i18n from '../i18n';
import { renderAt } from './render';

beforeEach(() => localStorage.clear());
describe('reference context controls', () => {
  it('allows core reference by default and never infers a country from language', async () => {
    await renderAt('/settings', [{ path: '/settings', element: <Settings /> }]);
    expect(screen.getByLabelText('Country (optional)')).toHaveValue('');
    fireEvent.change(screen.getByLabelText('Reference mode'), { target: { value: 'declared' } });
    fireEvent.change(screen.getByLabelText('Country (optional)'), { target: { value: 'GB' } });
    await act(() => i18n.changeLanguage('pt'));
    expect(screen.getByLabelText('País (opcional)')).toHaveValue('GB');
    fireEvent.change(screen.getByLabelText('Modo de referência'), { target: { value: 'international' } });
    expect(screen.getByLabelText('País (opcional)')).toHaveValue('');
    expect(screen.getByLabelText('Organização')).toHaveValue('unspecified');
  });
  it('separates organization, environment and resources without inferring availability', async () => {
    await renderAt('/settings', [{ path: '/settings', element: <Settings /> }]);
    fireEvent.change(screen.getByLabelText('Reference mode'), { target: { value: 'declared' } });
    fireEvent.change(screen.getByLabelText('Organization'), { target: { value: 'synthetic-a' } });
    fireEvent.change(screen.getByLabelText('Care setting'), { target: { value: 'remote' } });
    expect(screen.getByLabelText('Ultrasound')).toHaveValue('unknown');
    fireEvent.change(screen.getByLabelText('Ultrasound'), { target: { value: 'declared-unavailable' } });
    expect(screen.getByLabelText('Care setting')).toHaveValue('remote');
    expect(screen.getByRole('status', { name: 'Context status' })).toHaveTextContent('CLINICALLY_PENDING');
  });
  it('does not attribute declarations from one organization or country to another', async () => {
    await renderAt('/settings', [{ path: '/settings', element: <Settings /> }]);
    fireEvent.change(screen.getByLabelText('Reference mode'), { target: { value: 'declared' } });
    fireEvent.change(screen.getByLabelText('Organization'), { target: { value: 'synthetic-a' } });
    fireEvent.change(screen.getByLabelText('Care setting'), { target: { value: 'hospital' } });
    fireEvent.change(screen.getByLabelText('Ultrasound'), { target: { value: 'declared-present' } });
    fireEvent.change(screen.getByLabelText('Organization'), { target: { value: 'synthetic-b' } });
    expect(screen.getByLabelText('Ultrasound')).toHaveValue('unknown');
    expect(screen.getByLabelText('Care setting')).toHaveValue('unspecified');
    fireEvent.change(screen.getByLabelText('Ultrasound'), { target: { value: 'declared-unavailable' } });
    fireEvent.change(screen.getByLabelText('Country (optional)'), { target: { value: 'BR' } });
    expect(screen.getByLabelText('Organization')).toHaveValue('unspecified');
    expect(screen.getByLabelText('Ultrasound')).toHaveValue('unknown');
    fireEvent.change(screen.getByLabelText('Care setting'), { target: { value: 'hospital' } });
    fireEvent.change(screen.getByLabelText('Ultrasound'), { target: { value: 'declared-present' } });
    fireEvent.change(screen.getByLabelText('Care setting'), { target: { value: 'prehospital' } });
    expect(screen.getByLabelText('Ultrasound')).toHaveValue('unknown');
  });
});

it('compares a second country temporarily and distinguishes EU notes from national review', async () => {
  await renderAt('/settings', [{ path: '/settings', element: <Settings /> }]);
  fireEvent.change(screen.getByLabelText('Reference mode'), { target: { value: 'declared' } });
  const primary = screen.getByLabelText('Country (optional)');
  fireEvent.change(primary, { target: { value: 'PT' } });
  fireEvent.change(screen.getByLabelText('Topic'), { target: { value: 'Idarucizumab' } });
  expect(screen.getByText('National review pending for this selection.')).toBeVisible();
  expect(screen.getByText(/Praxbind. Anotación limitada/)).toBeVisible();
  const compare = screen.getByLabelText('Compare with another country');
  fireEvent.change(compare, { target: { value: 'US' } });
  expect(screen.getByText(/Praxbind. Revisar las secciones/)).toBeVisible();
  expect(primary).toHaveValue('PT');
  fireEvent.change(compare, { target: { value: '' } });
  expect(screen.queryByText(/Praxbind. Revisar las secciones/)).toBeNull();
  expect(primary).toHaveValue('PT');
});

it('limits a clinical module to its topic and separates the shared ERC reference', async () => {
  await renderAt('/', [{ path: '/', element: <CountryReferences primary="GB" moduleId="tension-pneumothorax" /> }]);
  expect(screen.getByText(/NICE NG39 distingue/)).toBeVisible();
  expect(screen.getByText(/ERC 2025 trata/)).toBeVisible();
  expect(screen.queryByText(/Balfaxar tiene/)).toBeNull();
  expect(screen.queryByLabelText('Topic')).toBeNull();
});

it('limits a drug detail to the documented product family', async () => {
  await renderAt('/', [{ path: '/', element: <CountryReferences primary="US" drug="phenytoin" /> }]);
  expect(screen.getByText(/DailyMed, reenvasado Henry Schein/)).toBeVisible();
  expect(screen.queryByText(/AUVI-Q. La presentación/)).toBeNull();
});

it('shows the adult stroke label and its jurisdiction-specific time origin', async () => {
  await renderAt('/', [{ path: '/', element: <CountryReferences primary="US" moduleId="acute-ischemic-stroke" /> }]);
  const compare = screen.getByLabelText('Compare with another country');
  expect(screen.getByText(/3 horas desde el comienzo de los síntomas/)).toBeVisible();
  expect(screen.queryByText(/4,5 horas desde/)).toBeNull();
  for (const code of ['PT', 'GB']) {
    fireEvent.change(compare, { target: { value: code } });
    expect(screen.getByText(/4,5 horas desde la última vez/)).toBeVisible();
    expect(screen.getByText(/3 horas desde el comienzo/)).toBeVisible();
  }
  fireEvent.change(compare, { target: { value: 'BR' } });
  expect(screen.queryByText(/4,5 horas desde/)).toBeNull();
  expect(screen.getByText('National review pending for this selection.')).toBeVisible();
});
