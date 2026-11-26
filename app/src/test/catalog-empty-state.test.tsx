import { fireEvent, screen } from '@testing-library/react';
import { expect, it } from 'vitest';
import ClinicalLibrary from '../pages/ClinicalLibrary';
import ClinicalGuides from '../pages/ClinicalGuides';
import { canonicalGuides } from '../clinical-guides/canonical';
import { renderAt } from './render';

it('announces no clinical results and restores search focus without clearing the bundle', async () => {
  const first = canonicalGuides[0];
  if (!first) throw new Error('The canonical catalog must not be empty');
  const bundle = first.bundle;
  const expected = canonicalGuides.filter(guide => guide.bundle === bundle).length;
  const { container } = await renderAt(`/clinical?bundle=${encodeURIComponent(bundle)}`, [{ path: '/clinical', element: <ClinicalLibrary /> }], 'es');
  const search = screen.getByRole('searchbox', { name: 'Buscar patología o módulo' });
  fireEvent.change(search, { target: { value: 'zzzz-no-result-synthetic' } });
  expect(screen.getByRole('status')).toHaveTextContent(`0 de ${canonicalGuides.length} módulos`);
  expect(screen.getByRole('heading', { name: 'Ningún módulo coincide con la búsqueda.' })).toBeInTheDocument();
  fireEvent.click(screen.getByRole('button', { name: 'Borrar búsqueda' }));
  expect(search).toHaveFocus();
  expect(search).toHaveValue('');
  expect(container.querySelectorAll('a.card')).toHaveLength(expected);
});

it('resets guide search and format together while leaving quick algorithms separate', async () => {
  const { container } = await renderAt('/guides', [{ path: '/guides', element: <ClinicalGuides /> }], 'es');
  const search = screen.getByRole('searchbox', { name: 'Buscar guía clínica' });
  const format = screen.getByRole('combobox', { name: 'Filtrar formato' });
  fireEvent.change(format, { target: { value: 'procedure' } });
  fireEvent.change(search, { target: { value: 'zzzz-no-result-synthetic' } });
  expect(screen.getByRole('status')).toHaveTextContent(`0 de ${canonicalGuides.length} módulos`);
  expect(screen.getByText('La búsqueda y el filtro se aplican a «Todos los módulos clínicos».')).toBeInTheDocument();
  fireEvent.click(screen.getByRole('button', { name: 'Restablecer búsqueda y filtros' }));
  expect(search).toHaveFocus();
  expect(format).toHaveValue('all');
  expect(container.querySelectorAll('section:last-child a.card')).toHaveLength(canonicalGuides.length);
});

it('localizes the new empty-state interface without translating canonical content', async () => {
  await renderAt('/clinical', [{ path: '/clinical', element: <ClinicalLibrary /> }], 'en');
  fireEvent.change(screen.getByRole('searchbox'), { target: { value: 'zzzz-no-result-synthetic' } });
  expect(screen.getByRole('heading', { name: 'No modules match your search.' })).toBeInTheDocument();
  expect(screen.getByRole('button', { name: 'Clear search' })).toBeInTheDocument();
});
