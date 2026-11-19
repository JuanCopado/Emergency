import { act, fireEvent, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it } from 'vitest';
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
