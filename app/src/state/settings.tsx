import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';
import { useTranslation } from 'react-i18next';
import { LANGUAGES, LANG_STORAGE_KEY, isLang, type LangCode } from '../i18n';
import { readStorage, writeStorage } from '../lib/storage';

export type ThemePref = 'system' | 'light' | 'dark';
export type MicroSymbol = 'mcg' | 'µg';

interface Settings {
  lang: LangCode;
  setLang: (l: LangCode) => void;
  theme: ThemePref;
  setTheme: (t: ThemePref) => void;
  resolvedTheme: 'light' | 'dark';
  micro: MicroSymbol;
  setMicro: (m: MicroSymbol) => void;
}

const THEME_KEY = 'emergency.theme';
const MICRO_KEY = 'emergency.micro';

const SettingsContext = createContext<Settings | null>(null);

function systemDark(): boolean {
  try {
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  } catch {
    return false;
  }
}

export function SettingsProvider({ children }: { children: ReactNode }) {
  const { i18n } = useTranslation();
  const [theme, setThemeState] = useState<ThemePref>(() => {
    const t = readStorage(THEME_KEY);
    return t === 'light' || t === 'dark' || t === 'system' ? t : 'system';
  });
  const [micro, setMicroState] = useState<MicroSymbol>(() => (readStorage(MICRO_KEY) === 'µg' ? 'µg' : 'mcg'));
  const [sysDark, setSysDark] = useState<boolean>(systemDark);
  const lang: LangCode = isLang(i18n.language) ? i18n.language : 'es';

  useEffect(() => {
    let mq: MediaQueryList | null = null;
    try {
      mq = window.matchMedia('(prefers-color-scheme: dark)');
    } catch {
      return;
    }
    const on = (e: MediaQueryListEvent) => setSysDark(e.matches);
    mq.addEventListener?.('change', on);
    return () => mq?.removeEventListener?.('change', on);
  }, []);

  const resolvedTheme: 'light' | 'dark' = theme === 'system' ? (sysDark ? 'dark' : 'light') : theme;

  useEffect(() => {
    document.documentElement.classList.toggle('dark', resolvedTheme === 'dark');
  }, [resolvedTheme]);

  useEffect(() => {
    const l = LANGUAGES.find((x) => x.code === lang);
    document.documentElement.lang = l?.htmlLang ?? 'es';
  }, [lang]);

  const setLang = useCallback(
    (l: LangCode) => {
      void i18n.changeLanguage(l);
      writeStorage(LANG_STORAGE_KEY, l);
    },
    [i18n],
  );
  const setTheme = useCallback((t: ThemePref) => {
    setThemeState(t);
    writeStorage(THEME_KEY, t);
  }, []);
  const setMicro = useCallback((m: MicroSymbol) => {
    setMicroState(m);
    writeStorage(MICRO_KEY, m);
  }, []);

  const value = useMemo(
    () => ({ lang, setLang, theme, setTheme, resolvedTheme, micro, setMicro }),
    [lang, setLang, theme, setTheme, resolvedTheme, micro, setMicro],
  );
  return <SettingsContext.Provider value={value}>{children}</SettingsContext.Provider>;
}

// eslint-disable-next-line react-refresh/only-export-components
export function useSettings(): Settings {
  const ctx = useContext(SettingsContext);
  if (!ctx) throw new Error('useSettings must be used inside SettingsProvider');
  return ctx;
}
