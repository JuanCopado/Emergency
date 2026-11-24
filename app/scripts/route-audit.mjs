import assert from 'node:assert/strict';

export const routes = [
  ['home', '/', 'Apoyo clínico para urgencias y cuidados agudos'],
  ['note', '/clinical-note', 'Apoyo al diagnóstico'],
  ['drugs', '/drugs', 'Fármacos'],
  ['drug', '/drugs/norepinephrine', 'Norepinephrine'],
  ['calculator', '/calculator?drug=norepinephrine&weight=70&dose=0.05', 'Calculadora de perfusiones'],
  ['pediatrics', '/pediatrics?regimen=paracetamol-pain-fever-home', 'Pediatría ambulatoria'],
  ['clinical', '/clinical', 'Patologías y módulos'],
  ['sepsis', '/clinical/sepsis-shock', 'Sepsis Shock'],
  ['guides', '/guides', 'Pantalla completa · impresión · PDF'],
  ['guide', '/guides/sepsis-shock', 'Sepsis Shock'],
  ['scores', '/clinical/clinical-scores-calculators', 'Clinical Scores Calculators'],
  ['pocus', '/clinical/pocus', 'Pocus'],
  ['ecg', '/clinical/ecg-image', 'Ecg Image'],
  ['procedures', '/procedures', 'Procedimientos'],
  ['pilot', '/procedures/PROC-VASC-007', 'Catéter venoso central femoral ecoguiado'],
  ['settings', '/settings', 'Ajustes'],
  ['about', '/about', 'Acerca de y aviso legal'],
  ['not-found', '/route-does-not-exist', 'Página no encontrada'],
  ['unknown-module', '/clinical/unknown', 'Módulo no encontrado'],
  ['unknown-guide', '/guides/unknown', 'Guía no encontrada'],
  ['acute-medications', '/acute-medications', 'Farmacología aguda'],
  ['insulin-uci', '/insulin-uci', 'Insulinoterapia UCI'],
  ['score-calculator', '/scores', 'Scores clínicos'],
  ['blood-gas', '/blood-gas', 'Revisión de gasometrías'],
  ['t06-lab', '/t06-lab', 'Laboratorio T06 en localhost'],
];

export async function verifyRoute(page, origin, { name, route, title }) {
  await page.locator('main').getByRole('heading', { level: 1, name: title, exact: true }).waitFor();
  const expected = new URL(route, origin);
  const actual = new URL(page.url());
  assert.equal(actual.origin + actual.pathname, expected.origin + expected.pathname);
  for (const [key, value] of expected.searchParams) assert.equal(actual.searchParams.get(key), value, route);
  if (name !== 'pediatrics') return;

  const regimen = expected.searchParams.get('regimen');
  const filter = page.getByLabel('Fármaco o combinación');
  const selection = page.getByLabel('Diagnóstico y régimen');
  const waitForFilter = id => filter.locator(`option[value=${id}]:checked`).waitFor({ state: 'attached' });
  assert.equal(await selection.inputValue(), regimen);
  await filter.selectOption('fluticasone-propionate');
  assert.equal(await selection.inputValue(), '');
  await page.goBack();
  await waitForFilter('paracetamol');
  assert.equal(await selection.inputValue(), regimen);
  await page.goForward();
  await waitForFilter('fluticasone-propionate');
  assert.equal(await selection.inputValue(), '');
  await page.goBack();
  await waitForFilter('paracetamol');
}
