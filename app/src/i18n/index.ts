import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import en from './locales/en.json';
import es from './locales/es.json';
import pt from './locales/pt.json';
import zh from './locales/zh.json';
import { readStorage } from '../lib/storage';

export const LANGUAGES = [
  { code: 'es', label: 'Español', htmlLang: 'es', intl: 'es-ES' },
  { code: 'en', label: 'English', htmlLang: 'en', intl: 'en-GB' },
  { code: 'pt', label: 'Português', htmlLang: 'pt-PT', intl: 'pt-PT' },
  { code: 'zh', label: '简体中文', htmlLang: 'zh-Hans', intl: 'zh-CN' },
] as const;
export type LangCode = (typeof LANGUAGES)[number]['code'];
export const DEFAULT_LANG: LangCode = 'es';
export const LANG_STORAGE_KEY = 'emergency.lang';

export function isLang(x: unknown): x is LangCode {
  return LANGUAGES.some((l) => l.code === x);
}

export function intlLocale(code: string): string {
  return LANGUAGES.find((l) => l.code === code)?.intl ?? 'en-GB';
}

export const resources = { en: { translation: en }, es: { translation: es }, pt: { translation: pt }, zh: { translation: zh } } as const;

const stored = readStorage(LANG_STORAGE_KEY);
void i18n.use(initReactI18next).init({
  resources,
  lng: isLang(stored) ? stored : DEFAULT_LANG,
  fallbackLng: 'en',
  supportedLngs: LANGUAGES.map((l) => l.code),
  interpolation: { escapeValue: false },
  returnNull: false,
});

export default i18n;
