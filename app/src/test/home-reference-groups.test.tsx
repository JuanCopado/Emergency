import { cleanup, fireEvent, screen } from '@testing-library/react';
import { afterEach, expect, it } from 'vitest';
import Home from '../pages/Home';
import ClinicalLibrary from '../pages/ClinicalLibrary';
import canonical from '../data/generatedClinicalGuides.json';
import { renderAt } from './render';

afterEach(cleanup);
it('opens an existing reference family with counts derived from its current catalog', async () => {
  await renderAt('/', [{ path: '/', element: <Home /> }, { path: '/clinical', element: <ClinicalLibrary /> }], 'es');
  const count = canonical.filter(g => g.bundle === 'modules/cardiovascular.md').length;
  const group = screen.getByTestId('reference-group-cardiovascular');
  expect(group).toHaveTextContent(`${count} guías`);
  expect(screen.queryByText('Próximamente')).toBeNull();
  fireEvent.click(group);
  expect(await screen.findByText('vasoactive-inotrope-infusions')).toBeInTheDocument();
  expect(screen.queryByText('status-epilepticus')).toBeNull();
  expect(screen.getAllByText('modules/cardiovascular.md')).toHaveLength(count);
});
