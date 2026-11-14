import { fireEvent, screen, within } from '@testing-library/react';
import { expect, it } from 'vitest';
import ClinicalGuides from '../pages/ClinicalGuides';
import ClinicalLibrary from '../pages/ClinicalLibrary';
import { getCanonicalGuide } from '../clinical-guides/canonical';
import { renderAt } from './render';

const cases = [
  ['Adulto · arritmia con pulso', 'adult-arrhythmias'],
  ['Adulto · parada cardíaca', 'adult-cardiac-arrest'],
  ['Pediatría · arritmia con circulación', 'pediatric-arrhythmias'],
  ['Pediatría · parada o indicación de RCP', 'pediatric-cardiac-arrest'],
] as const;

for (const base of ['/guides', '/clinical'] as const) {
  it.each(cases)(`${base} opens the correct existing circuit for %s`, async (label, id) => {
    const { container } = await renderAt(`${base}/arrhythmias-cardiac-arrest`, [{
      path: `${base}/:id`, element: base === '/guides' ? <ClinicalGuides /> : <ClinicalLibrary />,
    }], 'es');
    // A child may require CPR while a pulse is still detectable: the entry must
    // retain this exception and the neonatal exclusion before navigation.
    const master = container.querySelector('.canonical-body');
    expect(master?.textContent).toContain('despite adequate respiratory support, even if a pulse remains detectable');
    expect(master?.textContent).toContain('transition at birth follows neonatal life support');
    const nav = screen.getByRole('navigation', { name: 'Circuitos de reanimación' });
    expect(within(nav).getAllByRole('link')).toHaveLength(4);
    const target = getCanonicalGuide(id);
    expect(target).toBeDefined();
    const link = within(nav).getByRole('link', { name: new RegExp(label.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')) });
    expect(link).toHaveAttribute('href', `${base}/${id}`);
    expect(link).toHaveTextContent(target!.status);
    fireEvent.click(link);
    expect(await screen.findByRole('heading', { level: 1, name: target!.title })).toBeInTheDocument();
    expect(screen.queryByRole('navigation', { name: 'Circuitos de reanimación' })).not.toBeInTheDocument();
    const firstLine = target!.sectionBody.split('\n')[0];
    if (!firstLine) throw new Error('Empty destination guide');
    expect(container.querySelector('.canonical-body')?.textContent).toContain(firstLine.slice(2));
  });
}
