import { fireEvent, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { useLocation } from 'react-router-dom';
import { beforeEach, describe, expect, it } from 'vitest';
import Home from '../pages/Home';
import { renderAt } from './render';

function SearchDestination() {
  const location = useLocation();
  return <output aria-label="Search destination">{location.pathname}{location.search}</output>;
}

beforeEach(() => {
  localStorage.clear();
});

describe('Clinical Minimal home opt-in', () => {
  it('keeps the default home with one heading, its search and no scene illustration', async () => {
    await renderAt('/', [{ path: '/', element: <Home /> }]);
    const main = screen.getByRole('main');
    expect(within(main).getAllByRole('heading', { level: 1 })).toHaveLength(1);
    expect(within(main).queryByRole('img')).not.toBeInTheDocument();
    expect(within(main).getByRole('searchbox')).toBeEnabled();
    expect(within(main).getByRole('link', { name: /17/ })).toHaveAttribute('href', '/drugs');
  });

  it('shows the requested Portuguese introduction and updates its accessible scene when language changes', async () => {
    const user = userEvent.setup();
    await renderAt('/?design=clinical-minimal', [{ path: '/', element: <Home /> }], 'pt');
    const main = screen.getByRole('main');
    expect(within(main).getAllByRole('heading', { level: 1 })).toHaveLength(1);
    expect(within(main).getByRole('heading', { level: 1 })).toHaveTextContent(/A decisão clínica/);
    expect(within(main).getByRole('heading', { level: 1 })).toHaveTextContent(/começa consigo/);
    expect(within(main).getByRole('img', { name: /Ilustração vetorial genérica, sem pessoa real/ })).toBeInTheDocument();
    await user.selectOptions(screen.getByTestId('language-switcher'), 'en');
    expect(await within(main).findByRole('heading', { level: 1, name: /Clinical decisions.*start with you/ })).toBeInTheDocument();
    expect(within(main).getByRole('img', { name: /Generic vector illustration, not a real person/ })).toBeInTheDocument();
    expect(within(main).getAllByRole('heading', { level: 1 })).toHaveLength(1);
    expect(document.documentElement).toHaveAttribute('lang', 'en');
  });

  it('encodes reserved search text as one drug query and leaves the optional home presentation', async () => {
    const user = userEvent.setup();
    await renderAt('/?design=clinical-minimal', [
      { path: '/', element: <Home /> },
      { path: '/drugs', element: <SearchDestination /> },
    ]);
    const query = "<script>alert('x')</script> &lang=zh/#?";
    await user.type(screen.getByRole('searchbox'), query);
    await user.keyboard('{Enter}');
    const destination = new URL((await screen.findByLabelText('Search destination')).textContent!, 'https://emergency.test');
    expect(destination.pathname).toBe('/drugs');
    expect([...destination.searchParams.keys()]).toEqual(['q']);
    expect(destination.searchParams.get('q')).toBe(query);
    expect(destination.hash).toBe('');
    expect(within(screen.getByRole('main')).queryByRole('img')).not.toBeInTheDocument();
  });
});

const searchCopy = [
  ['en', 'Search drugs', 'Clear search', 'Enter a drug name and select Search. Press Escape to clear.'],
  ['es', 'Buscar fármacos', 'Borrar búsqueda', 'Escribe un nombre de fármaco y pulsa Buscar. Pulsa Escape para borrar.'],
  ['pt', 'Pesquisar fármacos', 'Limpar pesquisa', 'Introduza o nome de um fármaco e selecione Pesquisar. Prima Escape para limpar.'],
  ['zh', '搜索药物', '清空搜索', '输入药物名称后选择“搜索”。按 Escape 清空。'],
] as const;

async function renderSearch(lang = 'en') {
  return renderAt('/?design=clinical-minimal', [
    { path: '/', element: <><Home /><SearchDestination /></> },
    { path: '/drugs', element: <SearchDestination /> },
  ], lang);
}

describe('Accessible home search', () => {
  it('keeps one search form with visible manual guidance and a direct calculator shortcut', async () => {
    await renderSearch('es');
    expect(screen.getAllByRole('search')).toHaveLength(1);
    const shortcuts = screen.getByRole('navigation', { name: 'Accesos clínicos' });
    expect(within(shortcuts).getByRole('link', { name: 'Calculadora de perfusiones' })).toHaveAttribute('href', '/calculator');
    expect(screen.getByRole('main').querySelectorAll('a[href="/calculator"]')).toHaveLength(1);
    const hint = document.getElementById('home-search-hint')!;
    expect(hint).toBeVisible();
    expect(hint).not.toHaveClass('sr-only');
  });
  it.each(searchCopy)('names the landmark and describes its input in %s', async (lang, label, clear, hint) => {
    await renderSearch(lang);
    const form = screen.getByRole('search', { name: label });
    const input = within(form).getByRole('searchbox', { name: label });
    expect(input).toHaveAccessibleDescription(hint);
    expect(within(form).queryByRole('button', { name: clear })).not.toBeInTheDocument();
    expect(screen.getByLabelText('Search destination')).toHaveTextContent('/?design=clinical-minimal');
  });

  it.each(searchCopy)('clears with an accessible button and returns focus in %s', async (lang, label, clear) => {
    const user = userEvent.setup();
    await renderSearch(lang);
    const form = screen.getByRole('search', { name: label });
    const input = within(form).getByRole('searchbox');
    await user.type(input, 'synthetic query');
    const button = within(form).getByRole('button', { name: clear });
    expect(button).toHaveAttribute('type', 'button');
    await user.click(button);
    expect(input).toHaveValue('');
    expect(input).toHaveFocus();
    expect(within(form).queryByRole('button', { name: clear })).not.toBeInTheDocument();
    expect(screen.getByLabelText('Search destination')).toHaveTextContent('/?design=clinical-minimal');
  });

  it('Escape clears without changing the current route, then a fresh Enter uses the existing destination', async () => {
    const user = userEvent.setup();
    await renderSearch();
    const input = screen.getByRole('searchbox');
    await user.type(input, 'discard');
    await user.keyboard('{Escape}');
    expect(input).toHaveValue('');
    expect(input).toHaveFocus();
    expect(screen.getByLabelText('Search destination')).toHaveTextContent('/?design=clinical-minimal');
    await user.type(input, 'reserved & / ?');
    await user.keyboard('{Enter}');
    const destination = new URL(screen.getByLabelText('Search destination').textContent!, 'https://emergency.test');
    expect(destination.pathname).toBe('/drugs');
    expect([...destination.searchParams.keys()]).toEqual(['q']);
    expect(destination.searchParams.get('q')).toBe('reserved & / ?');
  });

  it('does not clear or submit the Chinese input while IME composition is active', async () => {
    const user = userEvent.setup();
    await renderSearch('zh');
    const form = screen.getByRole('search', { name: '搜索药物' });
    const input = within(form).getByRole('searchbox');
    input.focus();
    fireEvent.compositionStart(input);
    fireEvent.change(input, { target: { value: '中文测试' } });
    expect(fireEvent.keyDown(input, { key: 'Enter', code: 'Enter', isComposing: true })).toBe(false);
    fireEvent.submit(form);
    fireEvent.keyDown(input, { key: 'Escape', isComposing: true });
    expect(input).toHaveValue('中文测试');
    expect(screen.getByLabelText('Search destination')).toHaveTextContent('/?design=clinical-minimal');
    fireEvent.compositionEnd(input);
    await user.keyboard('{Enter}');
    const destination = new URL(screen.getByLabelText('Search destination').textContent!, 'https://emergency.test');
    expect(destination.pathname).toBe('/drugs');
    expect(destination.searchParams.get('q')).toBe('中文测试');
  });

  it('prevents the native isComposing and legacy229 Enter cases even without an active React composition ref', async () => {
    await renderSearch('zh');
    const input = screen.getByRole('searchbox');
    fireEvent.change(input, { target: { value: '中文测试' } });
    expect(fireEvent.keyDown(input, { key: 'Enter', code: 'Enter', isComposing: true })).toBe(false);
    expect(fireEvent.keyDown(input, { key: 'Enter', code: 'Enter', keyCode: 229 })).toBe(false);
    expect(screen.getByRole('search')).toBeInTheDocument();
    expect(screen.getByLabelText('Search destination')).toHaveTextContent('/?design=clinical-minimal');
  });

  it('preserves empty submission to the drug catalog after clearing', async () => {
    const user = userEvent.setup();
    await renderSearch();
    const input = screen.getByRole('searchbox');
    await user.type(input, 'discard');
    await user.click(screen.getByRole('button', { name: 'Clear search' }));
    await user.keyboard('{Enter}');
    expect(screen.getByLabelText('Search destination').textContent).toBe('/drugs');
  });
});
