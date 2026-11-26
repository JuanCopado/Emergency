import { cleanup, fireEvent, screen, within } from '@testing-library/react';
import { afterEach, expect, it } from 'vitest';
import Corticosteroids from '../pages/Corticosteroids';
import { renderAt } from './render';

afterEach(cleanup);
const mount = (locale = 'es') => renderAt('/corticosteroids', [{ path: '/corticosteroids', element: <Corticosteroids /> }], locale);
const select = (label: string, value: string) => fireEvent.change(screen.getByLabelText(label), { target: { value } });
function enterReference(table = 'endotext-2018') {
  select('Referencia de equivalencia', table);
  select('Cantidad en mg', '20');
  select('Vía sistémica de la comparación', 'iv');
  select('Qué cantidad estás comparando', 'daily_total');
}

it('requires an explicit reference and displays no valid result after incomplete input', async () => {
  await mount();
  fireEvent.click(screen.getByRole('button', { name: 'Comparar' }));
  expect(screen.getByRole('alert')).toHaveTextContent('Selecciona una referencia completa');
  expect(screen.queryByRole('region', { name: 'Equivalencias aproximadas' })).toBeNull();
});

it('displays source-specific output and invalidates it when a value or reference changes', async () => {
  await mount(); enterReference();
  fireEvent.click(screen.getByRole('button', { name: 'Comparar' }));
  let result = screen.getByRole('region', { name: 'Equivalencias aproximadas' });
  expect(result).toHaveTextContent('Endotext 2018');
  expect(within(result).getByText('0,75')).toBeVisible();
  select('Referencia de equivalencia', 'ese-es-2024');
  expect(screen.queryByRole('region', { name: 'Equivalencias aproximadas' })).toBeNull();
  fireEvent.click(screen.getByRole('button', { name: 'Comparar' }));
  result = screen.getByRole('region', { name: 'Equivalencias aproximadas' });
  expect(result).toHaveTextContent('ESE / Endocrine Society 2024');
  expect(within(result).getAllByText('0,5')).toHaveLength(2);
  select('Cantidad en mg', '1e-9999');
  fireEvent.click(screen.getByRole('button', { name: 'Comparar' }));
  expect(screen.getByRole('alert')).toHaveTextContent('cantidad positiva y finita');
  expect(screen.queryByRole('region', { name: 'Equivalencias aproximadas' })).toBeNull();
});

it('shows adult and pediatric references separately and resets the comparator', async () => {
  await mount(); enterReference();
  expect(screen.getByRole('region', { name: 'Adultos' })).toHaveTextContent('50 mg IV/IM cada 6 h');
  const pediatric = screen.getByRole('region', { name: 'Pediatría · Crisis suprarrenal' });
  expect(pediatric).toHaveTextContent('25');
  expect(pediatric).toHaveTextContent('No trasladar al niño');
  expect(within(pediatric).getByRole('link', { name: /Royal Children's Hospital/ })).toHaveAttribute('href', expect.stringContaining('rch.org.au'));
  fireEvent.click(screen.getByRole('button', { name: 'Comparar' }));
  fireEvent.click(screen.getByRole('button', { name: 'Reiniciar' }));
  expect(screen.getByLabelText('Cantidad en mg')).toHaveValue('');
  expect(screen.getByLabelText('Referencia de equivalencia')).toHaveValue('');
  expect(screen.queryByRole('region', { name: 'Equivalencias aproximadas' })).toBeNull();
});

it('shows the attributed Bell short course with its pediatric and diagnostic limits, and links existing airway regimens', async () => {
  await mount();
  const courses = screen.getByRole('region', { name: 'Pautas cortas por indicación' });
  const bell = within(courses).getByRole('article', { name: 'Parálisis facial periférica idiopática (Bell)' });
  expect(bell).toHaveTextContent('25 mg oral · cada 12 horas · 10 días');
  expect(bell).toHaveTextContent('desde los 16 años');
  expect(bell).toHaveTextContent('se limita a 18 años');
  expect(bell).toHaveTextContent('sin prellenar una pauta adulta');
  expect(bell).toHaveTextContent('no descartan ictus');
  expect(within(bell).getByRole('link', { name: /Abrir módulo clínico/ })).toHaveAttribute('href', '/clinical/ent-emergencies');
  expect(within(bell).queryByRole('textbox')).toBeNull();
  for (const id of ['acute-severe-asthma', 'copd-exacerbation', 'pediatric-acute-asthma', 'croup']) {
    expect(courses.querySelector(`a[href="/clinical/${id}"]`)).not.toBeNull();
  }
  expect(courses).toHaveTextContent('no autoriza suspender un tratamiento basal crónico');
});

it.each([['es', 'Corticoides'], ['pt', 'Corticosteroides'], ['en', 'Corticosteroids'], ['zh', '糖皮质激素']])('localizes controls without changing clinical data in %s', async (locale, title) => {
  await mount(locale);
  expect(screen.getByRole('heading', { name: title, level: 1 })).toBeVisible();
  expect(screen.getByText('Priorizar el plan individual del niño.', { exact: false })).toHaveAttribute('lang', 'es');
});
