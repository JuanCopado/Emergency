import { describe, expect, it } from 'vitest';
import en from './locales/en.json';
import es from './locales/es.json';
import pt from './locales/pt.json';
import zh from './locales/zh.json';
import { DEFAULT_LANG, LANGUAGES } from '.';
import { drugs } from '../data';

type Tree = { [k: string]: string | Tree };

function flatten(obj: Tree, prefix = ''): Record<string, string> {
  return Object.entries(obj).reduce<Record<string, string>>((acc, [k, v]) => {
    const key = prefix ? `${prefix}.${k}` : k;
    if (typeof v === 'string') acc[key] = v;
    else Object.assign(acc, flatten(v, key));
    return acc;
  }, {});
}

/** Normalise plural suffixes so languages with different plural categories compare equal. */
const base = (k: string) => k.replace(/_(zero|one|two|few|many|other)$/, '');

const locales = { en, es, pt, zh } as Record<string, Tree>;
const enKeys = new Set(Object.keys(flatten(en as Tree)).map(base));

describe('locales', () => {
  it('default UI language is Spanish and four languages are offered', () => {
    expect(DEFAULT_LANG).toBe('es');
    expect(LANGUAGES.map((l) => l.code)).toEqual(['es', 'en', 'pt', 'zh']);
  });

  it.each(Object.keys(locales))('%s has exactly the English key set, no empty strings', (code) => {
    const flat = flatten(locales[code] as Tree);
    const keys = new Set(Object.keys(flat).map(base));
    expect([...enKeys].filter((k) => !keys.has(k))).toEqual([]);
    expect([...keys].filter((k) => !enKeys.has(k))).toEqual([]);
    expect(Object.entries(flat).filter(([, v]) => !v.trim())).toEqual([]);
  });

  it.each(Object.keys(locales))('%s plural keys include an _other form', (code) => {
    const flat = Object.keys(flatten(locales[code] as Tree));
    const plurals = new Set(flat.filter((k) => /_(one|many|other)$/.test(k)).map(base));
    for (const p of plurals) expect(flat).toContain(`${p}_other`);
  });

  it.each(Object.keys(locales))('%s interpolation variables match English', (code) => {
    const flatEn = flatten(en as Tree);
    const flat = flatten(locales[code] as Tree);
    const vars = (s: string) => (s.match(/\{\{\w+\}\}/g) ?? []).sort().join(',');
    for (const [k, v] of Object.entries(flat)) {
      const enVal = flatEn[k] ?? flatEn[`${base(k)}_other`];
      if (enVal !== undefined) expect(vars(v), `${code}:${k}`).toBe(vars(enVal));
    }
  });

  it('every drug has a localized name in every language', () => {
    for (const code of Object.keys(locales)) {
      const names = (locales[code] as { drugNames: Record<string, string> }).drugNames;
      for (const d of drugs) expect(names[d.id], `${code}:${d.id}`).toBeTruthy();
    }
  });
});
