import { fireEvent, screen } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import ClinicalLibrary from '../pages/ClinicalLibrary';
import ClinicalGuides from '../pages/ClinicalGuides';
import { renderAt } from './render';
import { getCanonicalGuide } from '../clinical-guides/canonical';

const sources = import.meta.glob('../../../clinical/modules/*.md', {
  query: '?raw', import: 'default', eager: true,
}) as Record<string, string>;

afterEach(() => vi.restoreAllMocks());

it.each([
  ['/clinical/airway-rsi', 'airway-rsi'],
  ['/guides/airway-rsi', 'airway-rsi'],
  ['/guides/vasoactive-inotrope-infusions', 'vasoactive-inotrope-infusions'],
  ['/guides/clinical-scores-calculators', 'clinical-scores-calculators'],
  ['/guides/sepsis-shock', 'sepsis-shock'],
  ['/guides/vf-pvt', 'adult-cardiac-arrest'],
  ['/guides/asystole-pea', 'adult-cardiac-arrest'],
  ['/guides/coma', 'altered-consciousness'],
])('preserves canonical safety and body in the printable sheet at %s', async (path, moduleId) => {
  const guide = getCanonicalGuide(moduleId);
  if (!guide) throw new Error('Missing canonical module');
  const canonicalSource = sources[`../../../${guide.sourcePath}`];
  if (!canonicalSource) throw new Error('Missing canonical source');
  const source = canonicalSource.replace(/\r\n?/g, '\n');
  const preamble = source.split(/^## /m)[0]?.trim() ?? '';
  const section = source.split(`\n## ${moduleId}\n`)[1]?.split(/\n## /)[0]?.trim();
  expect(section).toBeTruthy();
  expect(guide.body).toBe([preamble, section].filter(Boolean).join('\n\n'));
  const library = path.startsWith('/clinical/');
  const { container } = await renderAt(path, [{
    path: library ? '/clinical/:id' : '/guides/:id',
    element: library ? <ClinicalLibrary /> : <ClinicalGuides />,
  }], 'es');
  const sheet = container.querySelector('.clinical-module-sheet, .clinical-guide-sheet');
  expect(sheet).not.toBeNull();
  const content = sheet?.querySelector('.canonical-body');
  expect(content).not.toBeNull();
  let position = 0;
  const presented = content?.textContent ?? '';
  for (const raw of guide.body.split('\n')) {
    const line = raw.trim().replace(/^#{1,4} /, '').replace(/^- /, '');
    if (!line) continue;
    const found = presented.indexOf(line, position);
    expect(found, `Missing or reordered canonical line: ${line}`).toBeGreaterThanOrEqual(position);
    position = found + line.length;
  }
  const sentinel = preamble.split('\n').find((line) => line.startsWith('Shared gate:'));
  if (sentinel) expect(presented.split(sentinel).length - 1).toBe(1);
  const beforePrint = sheet?.textContent;
  let printed: string | null | undefined;
  const print = vi.spyOn(window, 'print').mockImplementation(() => { printed = sheet?.textContent; });
  fireEvent.click(screen.getByRole('button', { name: /PDF.*imprimir|Imprimir.*PDF/i }));
  expect(print).toHaveBeenCalledOnce();
  expect(printed).toBe(beforePrint);
});
