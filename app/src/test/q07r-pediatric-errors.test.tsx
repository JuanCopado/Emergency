/**
 * Q07-R — pediatric form errors are associated with their field (WCAG 3.3.1 / 1.3.1 / 4.1.2).
 * No request is sent for an invalid entry; values are synthetic.
 */
import { cleanup, fireEvent, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import PediatricOutpatient from '../pages/PediatricOutpatient';
import { renderAt } from './render';

afterEach(() => { cleanup(); vi.restoreAllMocks(); });
const paracetamol = 'paracetamol-pain-fever-home';

async function mount() {
  const fetcher = vi.spyOn(globalThis, 'fetch');
  await renderAt(`/pediatrics?regimen=${paracetamol}`, [{ path: '/pediatrics', element: <PediatricOutpatient /> }]);
  return fetcher;
}

describe('Q07-R pediatric error ↔ field', () => {
  it('invalid weight: aria-invalid, described by the alert, focused, and no request', async () => {
    const fetcher = await mount();
    const weight = screen.getByLabelText('Peso real (kg)');
    fireEvent.change(weight, { target: { value: '12.5' } });
    fireEvent.click(screen.getByRole('button', { name: 'Comprobar y calcular' }));
    const alert = await screen.findByRole('alert');
    expect(weight).toHaveAttribute('aria-invalid', 'true');
    expect(weight.getAttribute('aria-describedby')).toBe(alert.id);
    expect(weight).toHaveAccessibleDescription(alert.textContent ?? '');
    expect(weight).toHaveFocus();
    expect(fetcher).not.toHaveBeenCalled();
  });

  it('only the failing field is marked invalid', async () => {
    await mount();
    fireEvent.change(screen.getByLabelText('Peso real (kg)'), { target: { value: '12,5' } });
    fireEvent.change(screen.getByLabelText('Edad (meses)'), { target: { value: 'abc' } });
    fireEvent.click(screen.getByRole('button', { name: 'Comprobar y calcular' }));
    await screen.findByRole('alert');
    expect(screen.getByLabelText('Edad (meses)')).toHaveAttribute('aria-invalid', 'true');
    expect(screen.getByLabelText('Peso real (kg)')).not.toHaveAttribute('aria-invalid');
    expect(document.querySelectorAll('[aria-invalid="true"]')).toHaveLength(1);
  });

  it('editing the field clears the error state', async () => {
    await mount();
    const weight = screen.getByLabelText('Peso real (kg)');
    fireEvent.change(weight, { target: { value: 'x' } });
    fireEvent.click(screen.getByRole('button', { name: 'Comprobar y calcular' }));
    await screen.findByRole('alert');
    fireEvent.change(weight, { target: { value: '12,5' } });
    expect(weight).not.toHaveAttribute('aria-invalid');
    expect(weight).not.toHaveAttribute('aria-describedby');
    expect(screen.queryByRole('alert')).toBeNull();
  });
});
