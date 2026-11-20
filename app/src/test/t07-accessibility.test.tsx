import { fireEvent, render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it } from 'vitest';
import { NumberField } from '../components/NumberField';
import Calculator from '../pages/Calculator';
import Procedures from '../pages/Procedures';
import { canonicalProcedures } from '../clinical-guides/procedures';
import { contextStorageKey, defaultContext } from '../context/reference-context';
import i18n from '../i18n';
import { renderAt } from './render';

beforeEach(async () => {
  localStorage.clear();
  await i18n.changeLanguage('en');
});

function descriptions(input: HTMLElement) {
  return (input.getAttribute('aria-describedby') ?? '').split(/\s+/).filter(Boolean).map(id => {
    const element = document.getElementById(id);
    expect(element, `description ${id} exists`).not.toBeNull();
    return element;
  });
}

describe('T07 numeric field descriptions', () => {
  it('announces the visible unit and hint with the labelled field', () => {
    render(<NumberField label="Weight" value="70" onChange={() => {}} suffix="kg" hint="Use actual weight" />);
    const input = screen.getByRole('textbox', { name: 'Weight' });
    expect(input).toHaveAccessibleDescription('kg Use actual weight');
    expect(descriptions(input).map(element => element?.id)).toEqual([`${input.id}-unit`, `${input.id}-hint`]);
  });

  it('replaces the hidden hint with the error without losing the unit', () => {
    const props = { label: 'Weight', value: '', onChange: () => {}, suffix: 'kg', hint: 'Use actual weight' };
    const { rerender } = render(<NumberField {...props} />);
    const input = screen.getByRole('textbox', { name: 'Weight' });
    rerender(<NumberField {...props} error="Enter a valid weight" />);
    expect(input).toHaveAttribute('aria-invalid', 'true');
    expect(input).toHaveAccessibleDescription('kg Enter a valid weight');
    expect(screen.queryByText('Use actual weight')).not.toBeInTheDocument();
    expect(descriptions(input).map(element => element?.id)).toEqual([`${input.id}-unit`, `${input.id}-err`]);
    rerender(<NumberField {...props} />);
    expect(input).not.toHaveAttribute('aria-invalid');
    expect(input).toHaveAccessibleDescription('kg Use actual weight');
    expect(descriptions(input)).toHaveLength(2);
  });

  it('does not share generated description IDs between fields', () => {
    render(<><NumberField label="Weight" value="70" onChange={() => {}} suffix="kg" />
      <NumberField label="Volume" value="50" onChange={() => {}} suffix="mL" /></>);
    const weight = descriptions(screen.getByRole('textbox', { name: 'Weight' }));
    const volume = descriptions(screen.getByRole('textbox', { name: 'Volume' }));
    expect(weight.every(element => !volume.includes(element))).toBe(true);
    const numericHint = 'Numeric input: use a decimal point (0.1), without thousands separators. Output follows the selected language.';
    expect(screen.getByRole('textbox', { name: 'Weight' })).toHaveAccessibleDescription(`kg ${numericHint}`);
    expect(screen.getByRole('textbox', { name: 'Volume' })).toHaveAccessibleDescription(`mL ${numericHint}`);
    expect(weight.map(element => element?.textContent)).toEqual(['kg', numericHint]);
    expect(volume.map(element => element?.textContent)).toEqual(['mL', numericHint]);
  });
});

it('uses native direction radios with arrow focus, wraparound and unchanged calculation', async () => {
  const user = userEvent.setup();
  await renderAt('/calculator?drug=norepinephrine&weight=70&dose=0.05', [{ path: '/calculator', element: <Calculator /> }]);
  const group = screen.getByRole('radiogroup', { name: 'Calculation' });
  const forward = within(group).getByRole('radio', { name: 'Dose → mL/h' });
  const reverse = within(group).getByRole('radio', { name: 'mL/h → dose' });
  expect(forward).toHaveAttribute('type', 'radio');
  expect(reverse).toHaveAttribute('type', 'radio');
  expect(forward).toBeChecked();
  expect(screen.getByTestId('rate-display')).toHaveTextContent(/^5\.3$/);
  forward.focus();
  await user.keyboard('{ArrowRight}');
  expect(reverse).toHaveFocus();
  expect(reverse).toBeChecked();
  expect(forward).not.toBeChecked();
  fireEvent.change(screen.getByTestId('calc-rate'), { target: { value: '10.5' } });
  expect(await screen.findByTestId('dose-display')).toHaveTextContent(/^0\.1$/);
  await user.keyboard('{ArrowLeft}');
  expect(forward).toHaveFocus();
  expect(forward).toBeChecked();
  expect(screen.getByTestId('rate-display')).toHaveTextContent(/^5\.3$/);
  await user.keyboard('{ArrowLeft}');
  expect(reverse).toHaveFocus();
  expect(reverse).toBeChecked();
});

describe('T07 canonical procedure language', () => {
  it.each(['en', 'pt', 'zh'])('marks the Spanish directory under UI %s', async lang => {
    await renderAt('/procedures', [{ path: '/procedures', element: <Procedures /> }], lang);
    expect(document.documentElement.lang).not.toBe('es');
    expect(screen.getByRole('heading', { level: 1, name: 'Procedimientos' }).closest('[lang]')).toHaveAttribute('lang', 'es');
    expect(screen.getByRole('searchbox', { name: 'Nombre o PROC-ID' }).closest('[lang]')).toHaveAttribute('lang', 'es');
  });

  it.each(['en', 'pt', 'zh'])('keeps the canonical sheet Spanish and country UI in %s', async lang => {
    localStorage.setItem(contextStorageKey, JSON.stringify({ ...defaultContext, mode: 'declared', countryCode: 'PT' }));
    const procedure = canonicalProcedures[0];
    if (!procedure) throw new Error('Canonical procedure fixture is missing');
    await renderAt(`/procedures/${procedure.id}`, [{ path: '/procedures/:id', element: <Procedures /> }], lang);
    expect(screen.getByRole('heading', { level: 1 }).closest('[lang]')).toHaveAttribute('lang', 'es');
    expect(screen.getByRole('region', { name: 'Preámbulo canónico' }).closest('[lang]')).toHaveAttribute('lang', 'es');
    expect(screen.getByRole('heading', { name: i18n.t('countryNotes.title') }).closest('[lang]')).toHaveAttribute('lang', i18n.resolvedLanguage ?? i18n.language ?? 'en');
  });
});
