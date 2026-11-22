import { act, cleanup, fireEvent, screen } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import ClinicalScores from '../pages/ClinicalScores';
import { renderAt } from './render';
import i18n from '../i18n';

afterEach(() => { cleanup(); vi.restoreAllMocks(); });
const catalog = { revision: 'synthetic-v1', total_scales: 1, total_formulas: 0, evidence: { status: 'yellow' }, scores: [{
  id: 'news2', name: 'NEWS2', use: 'Uso canónico sin traducir', measures: 'Medida canónica', version: '2017', source_url: 'https://example.org/source',
  fields: [{ key: 'value', label: 'Valor canónico', type: 'number', unit: 'mmol/L', minimum: 0, optional: false }],
}] };
const variants = [
  ['es', 'Calcular', 'Importar PDF o analítica', 'O pegue una analítica', 'campo requerido'],
  ['pt', 'Calcular', 'Importar PDF ou análises', 'Ou cole resultados de análises', 'campo obrigatório'],
  ['en', 'Calculate', 'Import PDF or lab results', 'Or paste lab results', 'required field'],
  ['zh', '计算', '导入 PDF 或化验结果', '或粘贴化验结果', '必填字段'],
] as const;

it.each(variants)('localizes existing score controls and document review in %s while preserving source wording', async (lang, calculate, document, paste, required) => {
  const fetcher = vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(JSON.stringify(catalog), { headers: { 'Content-Type': 'application/json' } }));
  await renderAt('/scores', [{ path: '/scores', element: <ClinicalScores /> }], lang);
  await screen.findByText('Uso canónico sin traducir');
  expect(screen.getByText('Uso canónico sin traducir').closest('[lang]')).toHaveAttribute('lang', 'es');
  fireEvent.click(screen.getByRole('button', { name: calculate }));
  expect(await screen.findByRole('alert')).toHaveTextContent(required);
  expect(fetcher).toHaveBeenCalledTimes(1);
  fireEvent.click(screen.getByRole('radio', { name: document }));
  fireEvent.change(screen.getByLabelText(paste), { target: { value: 'Valor canónico: 6 mmol/L' } });
  expect(screen.getByLabelText(/Valor canónico \(mmol\/L\)/)).toHaveValue('6');
  expect(screen.getByText('Valor canónico: 6 mmol/L', { selector: 'pre' })).toBeInTheDocument();
  expect(screen.getByRole('button', { name: calculate })).toBeInTheDocument();
  await act(async () => { await i18n.changeLanguage(lang === 'en' ? 'es' : 'en'); });
  expect(screen.getByText(new RegExp(lang === 'en' ? 'Texto · bloque 1' : 'Text · block 1'), {selector:'summary'})).toBeInTheDocument();
  expect(screen.getByLabelText(/Valor canónico \(mmol\/L\)/)).toHaveValue('6');
  expect(screen.getByText('Valor canónico: 6 mmol/L', {selector:'pre'})).toBeInTheDocument();
});
