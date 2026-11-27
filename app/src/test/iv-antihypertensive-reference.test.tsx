import { screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import ClinicalLibrary from '../pages/ClinicalLibrary';
import ClinicalGuides from '../pages/ClinicalGuides';
import { renderAt } from './render';

const moduleId = 'iv-antihypertensive-selection';
const languages = [
  ['es', 'Referencia informativa de antihipertensivos IV'],
  ['pt', 'Referência informativa de anti-hipertensores IV'],
  ['en', 'IV antihypertensive reference information'],
  ['zh', '静脉降压药参考信息'],
] as const;
const drugs = ['nicardipine', 'labetalol', 'clevidipine', 'esmolol', 'nitroglycerin', 'hydralazine', 'nitroprusside'];
const routes = [
  { path: '/clinical/:id', element: <ClinicalLibrary /> },
  { path: '/guides/:id', element: <ClinicalGuides /> },
];

function selectors(panel: HTMLElement) {
  const controls = within(panel).getAllByRole('combobox');
  expect(controls).toHaveLength(2);
  return controls as [HTMLSelectElement, HTMLSelectElement];
}

for (const base of ['/clinical', '/guides']) {
  describe(`${base} informational product reference`, () => {
    it.each(languages)('requires manual drug and jurisdiction even in %s', async (lang, name) => {
      await renderAt(`${base}/${moduleId}`, routes, lang);
      const panel = screen.getByRole('region', { name });
      const selects = selectors(panel);
      expect(selects).toHaveLength(2);
      expect(selects[0]).toHaveValue('');
      expect(selects[1]).toHaveValue('');
      expect(within(selects[0]).getAllByRole('option').map(option => option.getAttribute('value'))).toEqual(['', ...drugs]);
      expect(within(selects[1]).getAllByRole('option').map(option => option.getAttribute('value'))).toEqual(['', 'US', 'ES', 'PT']);
      expect(panel).toHaveTextContent('CLINICALLY_PENDING');
      expect(within(panel).queryByRole('article')).not.toBeInTheDocument();
      expect(within(panel).queryByRole('link')).not.toBeInTheDocument();
      expect(panel.querySelector('input, output, button')).toBeNull();
    });

    it('separates US/ES source scope and keeps Portugal unknown through a language change', async () => {
      const user = userEvent.setup();
      await renderAt(`${base}/${moduleId}`, routes, 'en');
      const panel = screen.getByRole('region', { name: languages[2][1] });
      const [drug, country] = selectors(panel);
      await user.selectOptions(drug, 'clevidipine');
      expect(within(panel).queryByRole('link')).not.toBeInTheDocument();
      await user.selectOptions(country, 'US');
      expect(within(panel).getByRole('link')).toHaveAttribute('href', expect.stringContaining('dailymed.nlm.nih.gov'));
      expect(panel).toHaveTextContent('Not enabled: information only');
      await user.selectOptions(country, 'ES');
      expect(within(panel).getByRole('link')).toHaveAttribute('href', 'https://cima.aemps.es/cima/dochtml/ft/76595/FT_76595.html');
      expect(panel).toHaveTextContent('Adult perioperative rapid BP reduction');
      expect(panel).not.toHaveTextContent('a6826aa3-fabb-4ff1-a7a3-cd4c34e3a330');
      await user.selectOptions(country, 'PT');
      expect(within(panel).queryByRole('article')).not.toBeInTheDocument();
      expect(panel).toHaveTextContent('this proves neither absence nor stock');
      expect(within(panel).getByRole('link')).toHaveAttribute('href', expect.stringContaining('infarmed.pt'));
      await user.selectOptions(screen.getByTestId('language-switcher'), 'pt');
      const translated = await screen.findByRole('region', { name: languages[1][1] });
      expect(selectors(translated)[0]).toHaveValue('clevidipine');
      expect(selectors(translated)[1]).toHaveValue('PT');
      expect(translated).toHaveTextContent('não demonstra ausência nem stock');
      expect(translated.querySelector('input, output, button')).toBeNull();
    });

    it('keeps the two US labetalol products distinct without identifying the original compound source', async () => {
      const user = userEvent.setup();
      await renderAt(`${base}/${moduleId}`, routes, 'en');
      const panel = screen.getByRole('region', { name: languages[2][1] });
      const [drug, country] = selectors(panel);
      await user.selectOptions(drug, 'labetalol');
      await user.selectOptions(country, 'US');
      expect(within(panel).getAllByRole('article')).toHaveLength(2);
      expect(within(panel).getAllByRole('link').map(link => link.getAttribute('href'))).toEqual([
        'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=6cb2c117-584c-4440-acfb-e4b1af4dc509',
        'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=99a715a0-4579-410c-b102-7ef6fab8db55',
      ]);
      expect(panel).toHaveTextContent('original labetalol product in the compound source remains unidentified');
      expect(panel).toHaveTextContent('Not enabled: information only');
      expect(panel).not.toHaveTextContent(/mg\/h|mL\/h/);
      await user.selectOptions(drug, 'esmolol');
      expect(within(panel).queryByRole('article')).not.toBeInTheDocument();
      expect(panel).toHaveTextContent('No product identified for this combination');
      expect(panel).not.toHaveTextContent('6cb2c117-584c-4440-acfb-e4b1af4dc509');
    });

    it('distinguishes inherited source metadata from an enabled administration profile', async () => {
      const user = userEvent.setup();
      await renderAt(`${base}/${moduleId}`, routes, 'en');
      const panel = screen.getByRole('region', { name: languages[2][1] });
      const [drug, country] = selectors(panel);
      await user.selectOptions(drug, 'nicardipine');
      await user.selectOptions(country, 'US');
      expect(panel).toHaveTextContent('Inherited metadata: not a new complete label review');
      expect(panel).toHaveTextContent('Not enabled: information only');
      expect(panel.querySelector('input, output, button')).toBeNull();
    });

    it('is absent from an unrelated canonical module', async () => {
      await renderAt(`${base}/critical-valvular-disease`, routes, 'en');
      expect(screen.queryByRole('region', { name: languages[2][1] })).not.toBeInTheDocument();
    });
  });
}
