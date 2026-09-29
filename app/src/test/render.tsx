import { render } from '@testing-library/react';
import type { ReactElement } from 'react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import i18n from '../i18n';
import { SettingsProvider } from '../state/settings';
import { Layout } from '../components/Layout';

export async function renderAt(path: string, routes: { path: string; element: ReactElement }[], lang = 'en') {
  await i18n.changeLanguage(lang);
  return render(
    <MemoryRouter initialEntries={[path]}>
      <SettingsProvider>
        <Routes>
          <Route element={<Layout />}>
            {routes.map((r) => (
              <Route key={r.path} path={r.path} element={r.element} />
            ))}
          </Route>
        </Routes>
      </SettingsProvider>
    </MemoryRouter>,
  );
}
