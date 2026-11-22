import { cleanup, fireEvent, screen } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import { hasLocalIdentifierLabel } from '../clinical-note/privacy';
import { uploadError } from '../clinical-note/imageReview';
import i18n from '../i18n';
import ClinicalNote from '../pages/ClinicalNote';
import { renderAt } from './render';

afterEach(() => { cleanup(); vi.restoreAllMocks(); });

it.each(['Name: Synthetic', 'Patient: Synthetic', 'Nome: Sintético', 'Doente: Sintético',
  'Nombre: Sintético', 'Paciente: Sintético', '姓名：合成示例', '患者：合成示例',
  'Dirección: Calle Sintética', 'Teléfono: 000000000', '身份证：000000000000000000'])(
  'detects a supported identifier label: %s', value => {
  expect(hasLocalIdentifierLabel(value)).toBe(true);
});

it.each(['Paciente estable.', 'Patient stable.', 'Doente consciente.', '患者意识清楚。',
  'Nombre del medicamento: ejemplo', 'Patient condition: stable', 'Nome do exame: exemplo'])(
  'does not treat unlabelled clinical prose as an identifier label: %s', value => {
  expect(hasLocalIdentifierLabel(value)).toBe(false);
});

it.each([
  ['es', 'Nombre', 'Persona Sintética'], ['pt', 'Nome', 'Pessoa Sintética'],
  ['en', 'Name', 'Synthetic Person'], ['zh', '姓名', '合成示例'],
  ['es', 'Dirección', 'Calle Sintética 00'], ['pt', 'Morada', 'Rua Sintética 00'],
  ['en', 'Address', 'Synthetic Street 00'], ['zh', '地址', '合成街道零号'],
].flatMap(([language, label, value]) => [
  { language, label, separator: 'NBSP', text: `${label}\u00a0: ${value}` },
  { language, label, separator: 'line break', text: `${label}\n: ${value}` },
]))('$language $label retains detection with pasted $separator before the delimiter', ({ text }) => {
  expect(hasLocalIdentifierLabel(text)).toBe(true);
});

it.each([['es', 'Nombre: Persona Sintética'], ['pt', 'Doente: Pessoa Sintética'],
  ['en', 'Patient: Synthetic Person'], ['zh', '姓名：合成示例']])(
  '%s labels retain STOP and block export without a server call', async (language, value) => {
  const fetcher = vi.spyOn(globalThis, 'fetch');
  await renderAt('/clinical-note', [{ path: '/clinical-note', element: <ClinicalNote /> }], language);
  const ui = (key: string) => String(i18n.getFixedT(language, 'clinicalUi')(key, {
    keySeparator: false, nsSeparator: false,
  }));
  expect(screen.getByText(ui('Sem identificadores detetados localmente'))).toBeVisible();
  expect(screen.getByText(ui('A verificação automática é limitada. Reveja o texto e os ficheiros antes de aceitar ou exportar.'))).toBeVisible();
  fireEvent.change(screen.getByTestId('note-origin'), { target: { value } });
  expect(screen.getByRole('alert')).toHaveTextContent('STOP');
  fireEvent.click(screen.getByTestId('note-tab-export'));
  expect(screen.getByRole('button', { name: 'PDF' })).toBeDisabled();
  expect(fetcher).not.toHaveBeenCalled();
});

it.each(['es', 'pt', 'en', 'zh'])('%s explains oversized text without pretending to import a partial document', language => {
  const ui = (key: string) => String(i18n.getFixedT(language, 'clinicalUi')(key, {
    keySeparator: false, nsSeparator: false,
  }));
  const result = uploadError(new Error('clinical text upload exceeds character limit'), '', ui);
  expect(result).toBe(ui('O texto do ficheiro excede 120 000 caracteres. Nada foi importado; divida-o em documentos menores e reveja cada parte.'));
  expect(result).not.toContain('clinical text upload exceeds');
});
