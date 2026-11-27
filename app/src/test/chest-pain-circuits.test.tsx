import { fireEvent, screen, within } from '@testing-library/react';
import { expect, it } from 'vitest';
import ClinicalGuides from '../pages/ClinicalGuides';
import ClinicalLibrary from '../pages/ClinicalLibrary';
import { getCanonicalGuide } from '../clinical-guides/canonical';
import { renderAt } from './render';

const ids = [
  'acute-coronary-syndrome', 'acute-aortic-syndrome', 'pulmonary-embolism',
  'tension-pneumothorax', 'cardiac-tamponade-pericardial-emergency',
] as const;
const labels = [
  ['es', 'Circuitos por causa de dolor torácico'],
  ['pt', 'Circuitos por causa de dor torácica'],
  ['en', 'Chest pain cause pathways'],
  ['zh', '胸痛病因路径'],
] as const;

for (const base of ['/clinical', '/guides'] as const) {
  const routes = [{ path: `${base}/:id`, element: base === '/clinical' ? <ClinicalLibrary /> : <ClinicalGuides /> }];
  it.each(labels)(`${base} keeps manual canonical links and warning in %s`, async (lang, label) => {
    const { container } = await renderAt(`${base}/non-coronary-chest-pain`, routes, lang);
    const panel = screen.getByRole('navigation', { name: label });
    expect(within(panel).getAllByRole('link')).toHaveLength(5);
    expect(panel).toHaveTextContent('CLINICALLY_PENDING');
    for (const id of ids) {
      const target = getCanonicalGuide(id)!;
      expect(target).toBeDefined();
      const link = within(panel).getByRole('link', { name: new RegExp(target.title) });
      expect(link).toHaveAttribute('href', `${base}/${id}`);
      expect(link).toHaveTextContent(target.status);
    }
    // Rendering the panel cannot navigate or alter the canonical clinical text.
    expect(screen.getByRole('heading', { level: 1, name: getCanonicalGuide('non-coronary-chest-pain')!.title })).toBeInTheDocument();
    expect(container.querySelector('.canonical-body')?.textContent).toContain('Antithrombotic treatment must follow the actual diagnosis');
  });
  it.each(ids)(`${base} manually opens existing destination %s`, async (id) => {
    await renderAt(`${base}/non-coronary-chest-pain`, routes, 'es');
    const panel = screen.getByRole('navigation', { name: labels[0][1] });
    const target = getCanonicalGuide(id)!;
    fireEvent.click(within(panel).getByRole('link', { name: new RegExp(target.title) }));
    expect(await screen.findByRole('heading', { level: 1, name: target.title })).toBeInTheDocument();
    expect(screen.queryByRole('navigation', { name: labels[0][1] })).not.toBeInTheDocument();
  });
  it(`${base} does not offer chest-pain pathways in an unrelated module`, async () => {
    await renderAt(`${base}/critical-valvular-disease`, routes, 'en');
    expect(screen.queryByRole('navigation', { name: labels[2][1] })).not.toBeInTheDocument();
  });
}
