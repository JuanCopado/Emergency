import { useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, NavLink, Outlet, useLocation } from 'react-router-dom';
import { BRAND } from '../config/brand';
import { DraftPill } from './Badges';
import { Icon, type IconName } from './Icon';
import { LanguageSwitcher } from './LanguageSwitcher';
import { LogoMark } from './Logo';
import { ThemeToggle } from './ThemeToggle';

const NAV: { to: string; key: string; icon: IconName; end?: boolean; desktopOnly?: boolean }[] = [
  { to: '/', key: 'nav.home', icon: 'home', end: true },
  { to: '/drugs', key: 'nav.drugs', icon: 'pill' },
  { to: '/calculator', key: 'nav.calculator', icon: 'calc' },
  { to: '/clinical', key: 'nav.clinical', icon: 'heart', desktopOnly: true },
  { to: '/clinical-note', key: 'nav.clinicalNote', icon: 'info' },
  { to: '/settings', key: 'nav.settings', icon: 'settings' },
  { to: '/about', key: 'nav.about', icon: 'info', desktopOnly: true },
];

export function Layout() {
  const { t } = useTranslation();
  const location = useLocation();
  const mainRef = useRef<HTMLElement>(null);

  // Move focus to main content on route change (screen-reader friendly SPA navigation).
  useEffect(() => {
    window.scrollTo(0, 0);
    mainRef.current?.focus({ preventScroll: true });
  }, [location.pathname]);

  return (
    <div className="min-h-dvh">
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:fixed focus:left-3 focus:top-3 focus:z-50 focus:rounded-lg focus:bg-primary focus:px-4 focus:py-2 focus:text-primary-fg"
      >
        {t('a11y.skip')}
      </a>
      <header className="sticky top-0 z-30 border-b border-border bg-bg/85 backdrop-blur supports-[backdrop-filter]:bg-bg/70">
        <div className="mx-auto flex h-16 max-w-6xl items-center gap-3 px-4 sm:px-6">
          <Link to="/" className="flex items-center gap-2.5 rounded-lg" aria-label={`${BRAND.name} — ${t('nav.home')}`}>
            <LogoMark size={34} />
            <span className="flex flex-col leading-tight">
              <span className="text-base font-extrabold tracking-tight">{BRAND.name}</span>
              <span className="hidden text-[11px] font-medium text-muted sm:block">{t('brand.tagline')}</span>
            </span>
          </Link>
          <span className="hidden sm:inline-flex">
            <DraftPill />
          </span>
          <nav aria-label={t('a11y.mainNav')} className="ml-4 hidden lg:block">
            <ul className="flex items-center gap-1">
              {NAV.map((n) => (
                <li key={n.to}>
                  <NavLink
                    to={n.to}
                    end={n.end}
                    className={({ isActive }) =>
                      `rounded-lg px-3 py-2 text-sm font-semibold transition-colors ${isActive ? 'bg-surface-2 text-fg' : 'text-muted hover:text-fg'}`
                    }
                  >
                    {t(n.key)}
                  </NavLink>
                </li>
              ))}
            </ul>
          </nav>
          <div className="ml-auto flex items-center gap-2">
            <LanguageSwitcher />
            <ThemeToggle />
          </div>
        </div>
      </header>

      <main id="main" ref={mainRef} tabIndex={-1} className="mx-auto max-w-6xl px-4 pb-28 pt-5 outline-none sm:px-6 lg:pb-12 lg:pt-8">
        <Outlet />
      </main>

      <footer className="mx-auto hidden max-w-6xl border-t border-border px-6 py-6 text-xs text-muted lg:block">
        <p>
          {BRAND.name} {BRAND.appVersion} · {t('footer.content', { version: BRAND.contentVersion })} · {t('footer.disclaimer')}{' '}
          <Link to="/about" className="underline underline-offset-2 hover:text-fg">
            {t('nav.about')}
          </Link>
        </p>
      </footer>

      <nav
        aria-label={t('a11y.mainNav')}
        className="fixed inset-x-0 bottom-0 z-30 border-t border-border bg-surface/95 pb-[env(safe-area-inset-bottom)] backdrop-blur lg:hidden"
      >
        <ul className="mx-auto grid max-w-lg grid-cols-5">
          {NAV.filter((n) => !n.desktopOnly).map((n) => (
            <li key={n.to}>
              <NavLink
                to={n.to}
                end={n.end}
                className={({ isActive }) =>
                  `flex min-h-[60px] flex-col items-center justify-center gap-1 text-[11px] font-semibold ${isActive ? 'text-primary' : 'text-muted'}`
                }
              >
                <Icon name={n.icon} size={22} />
                <span className="max-w-full truncate px-1 text-center">{t(n.key)}</span>
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
    </div>
  );
}
