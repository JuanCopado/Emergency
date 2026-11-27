import { screen, within } from '@testing-library/react';
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
