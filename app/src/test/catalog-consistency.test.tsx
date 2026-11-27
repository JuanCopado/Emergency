import { fireEvent, screen } from '@testing-library/react';
import { expect, it } from 'vitest';
import { useLocation } from 'react-router-dom';
import DrugList from '../pages/DrugList';
import Procedures from '../pages/Procedures';
import { drugs } from '../data';
import { canonicalProcedures } from '../clinical-guides/procedures';
import { renderAt } from './render';

function LocationRecord() {
  const location = useLocation();
  return <output data-testid="location-record">{location.search}</output>;
}

it('resets only drug search filters, preserves unrelated URL context and restores focus', async () => {
  await renderAt('/drugs?q=zzzz-no-result-synthetic&category=icu-sedation-analgesia&dose=fixed&keep=1', [
    { path: '/drugs', element: <><DrugList /><LocationRecord /></> },
  ], 'es');
  const input = screen.getByRole('searchbox');
  expect(screen.queryAllByTestId(/^drug-card-/)).toHaveLength(0);
  fireEvent.click(screen.getByRole('button', { name: 'Restablecer búsqueda y filtros' }));
  expect(input).toHaveFocus();
  expect(input).toHaveValue('');
  expect(screen.getByTestId('location-record')).toHaveTextContent('?keep=1');
  expect(screen.getAllByTestId(/^drug-card-/)).toHaveLength(drugs.length);
});

it.each([
  ['es', 'No hay coincidencias.', 'Restablecer búsqueda y filtros'],
  ['en', 'No matches.', 'Reset search and filters'],
  ['pt', 'Sem resultados.', 'Repor pesquisa e filtros'],
  ['zh', '没有匹配项。', '重置搜索和筛选'],
])('restores all procedure filters and focus in %s while preserving canonical Spanish context', async (lang, heading, reset) => {
  await renderAt('/procedures', [{ path: '/procedures', element: <Procedures /> }], lang);
  const input = screen.getByRole('searchbox');
  const family = screen.getByRole('combobox', { name: 'Familia' });
  const level = screen.getByRole('combobox', { name: 'Nivel' });
  const procedure = canonicalProcedures[0];
  if (!procedure) throw new Error('The canonical procedure catalog must not be empty');
  fireEvent.change(family, { target: { value: procedure.family } });
  fireEvent.change(level, { target: { value: procedure.level } });
  fireEvent.change(input, { target: { value: 'zzzz-no-result-synthetic' } });
  expect(screen.getByRole('heading', { name: heading }).closest('[lang]')).toHaveAttribute('lang', lang);
  fireEvent.click(screen.getByRole('button', { name: reset }));
  expect(input).toHaveFocus();
  expect(input).toHaveValue('');
  expect(family).toHaveValue('');
  expect(level).toHaveValue('');
  expect(screen.getByRole('status')).toHaveTextContent(`${canonicalProcedures.length} procedimientos`);
  expect(screen.getByRole('heading', { level: 1 }).closest('[lang]')).toHaveAttribute('lang', 'es');
  expect(screen.getByText(/YELLOW: revisión clínica pendiente/)).toBeVisible();
});
