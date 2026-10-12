import { cleanup, fireEvent, screen, within } from '@testing-library/react';
import { afterEach, expect, it } from 'vitest';
import Procedures from '../pages/Procedures';
import DrugDetail from '../pages/DrugDetail';
import { procedurePilots } from '../clinical-guides/procedurePilots';
import { canonicalProcedures } from '../clinical-guides/procedures';
import { renderAt } from './render';

afterEach(cleanup);
const mount = (path: string) => renderAt(path, [{ path: '/procedures', element: <Procedures /> }, { path: '/procedures/:id', element: <Procedures /> }]);

it.each(procedurePilots)('preserves all canonical sections and preamble for $procedure_id', async pilot => {
  await mount(`/procedures/${pilot.procedure_id}`);
  const article = screen.getByRole('article');
  expect(article).toHaveTextContent(pilot.provenance.family_preamble.replace(/\s+/g, ' '));
  for (const section of Object.values(pilot.provenance.sections)) expect(article).toHaveTextContent(section.replace(/\s+/g, ' '));
  expect(within(article).getByRole('region', { name: 'STOP' })).toBeVisible();
  expect(within(article).getByRole('region', { name: 'Confirmación' })).toBeVisible();
  expect(article).toHaveTextContent('YELLOW');
  expect(article.querySelectorAll('figure')).toHaveLength(1);
  expect(article.querySelectorAll('img')).toHaveLength(0);
});

it('searches 196 canonical rows by alias without duplicating the result', async () => {
  await mount('/procedures');
  expect(screen.getByRole('status')).toHaveTextContent('196 procedimientos');
  const procedure = canonicalProcedures.find(p => p.aliases.length)!;
  fireEvent.change(screen.getByLabelText('Nombre o PROC-ID'), { target: { value: procedure.aliases[0] } });
  expect(screen.getByRole('status')).toHaveTextContent('1 procedimientos');
  expect(screen.getByRole('heading', { name: procedure.name })).toBeVisible();
  fireEvent.change(screen.getByLabelText('Nombre o PROC-ID'), { target: { value: 'no-such-id' } });
  expect(screen.getByText(/No hay coincidencias/)).toBeVisible();
});

it('distinguishes a non-pilot source reference from a clinical technique card', async () => {
  await mount('/procedures/PROC-SP-002');
  expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Medición de presión compartimental');
  expect(screen.getByText('Ficha fuera del piloto visual')).toBeVisible();
  expect(screen.queryByRole('region', { name: 'STOP' })).not.toBeInTheDocument();
});

it('places drug precautions and expanded module rules before opening the calculator', async () => {
  await renderAt('/drugs/norepinephrine', [{ path: '/drugs/:id', element: <DrugDetail /> }]);
  const link = screen.getByTestId('open-calculator');
  const cautions = document.getElementById('sec-cautions')!;
  expect(cautions.compareDocumentPosition(link) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  const details = document.querySelector('details')!;
  expect(details.open).toBe(true);
  expect(details.compareDocumentPosition(link) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
});
