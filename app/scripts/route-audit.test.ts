import { expect, it, vi } from 'vitest';
import { routes, verifyRoute } from './route-audit.mjs';

const origin = 'http://127.0.0.1:4175';
const heading = 'Pediatría ambulatoria';
const regimen = 'paracetamol-pain-fever-home';
const route = '/pediatrics?regimen=' + regimen;

function browserFixture(path: string, title = heading, restore = true) {
  let currentRegimen = regimen;
  let drug = 'paracetamol';
  const getByRole = vi.fn((_role, options) => ({
    waitFor: async () => {
      if (title !== options.name) throw new Error('wrong destination heading');
    },
  }));
  const filter = {
    selectOption: async (id: string) => { drug = id; currentRegimen = ''; },
    locator: (selector: string) => ({
      waitFor: async () => {
        if (selector !== `option[value=${drug}]:checked`) throw new Error('filter not restored');
      },
    }),
  };
  return {
    locator: () => ({ getByRole }),
    url: () => origin + path,
    getByLabel: (label: string) => label === 'Fármaco o combinación' ? filter : { inputValue: async () => currentRegimen },
    goBack: async () => { if (restore) drug = 'paracetamol'; currentRegimen = regimen; },
    goForward: async () => { drug = 'fluticasone-propionate'; currentRegimen = ''; },
    getByRole,
  };
}

it('defines distinct destinations with a specific heading, including the three negative controls', () => {
  expect(routes).toHaveLength(25);
  expect(new Set(routes.map(([, path]) => path)).size).toBe(25);
  expect(routes.find(([name]) => name === 'pediatrics')).toEqual(['pediatrics', route, heading]);
  expect(routes.filter(([name]) => name === 'not-found' || name.startsWith('unknown-'))).toHaveLength(3);
  expect(routes.every(([, , title]) => Boolean(title.trim()))).toBe(true);
});

it('checks exact route identity and permits additional defaults in the URL', async () => {
  const page = browserFixture(route + '&default=1');
  await verifyRoute(page, origin, { name: 'catalog', route, title: heading });
  expect(page.getByRole).toHaveBeenCalledWith('heading', { level: 1, name: heading, exact: true });
  await expect(verifyRoute(browserFixture('/missing', 'Página no encontrada'), origin, { name: 'catalog', route, title: heading }))
    .rejects.toThrow('wrong destination heading');
  await expect(verifyRoute(browserFixture('/another' + route.slice('/pediatrics'.length)), origin, { name: 'catalog', route, title: heading }))
    .rejects.toThrow();
  await expect(verifyRoute(browserFixture('/pediatrics?regimen=WRONG'), origin, { name: 'catalog', route, title: heading }))
    .rejects.toThrow();
});

it('requires pediatric history to restore both regimen and filter', async () => {
  const target = { name: 'pediatrics', route, title: heading };
  await expect(verifyRoute(browserFixture(route), origin, target)).resolves.toBeUndefined();
  await expect(verifyRoute(browserFixture(route, heading, false), origin, target)).rejects.toThrow('filter not restored');
});
