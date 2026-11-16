import { expect, it } from 'vitest';
import i18n from '.';
import en from './locales/en.clinical.json';
import es from './locales/es.clinical.json';
import pt from './locales/pt.clinical.json';
import zh from './locales/zh.clinical.json';
const resources={en,es,pt,zh};
it.each(Object.entries(resources))('%s has complete, nonempty UI translations and preserves variables and safety codes', (lang, values) => {
  expect(Object.keys(values).sort()).toEqual(Object.keys(en).sort());
  for(const [key,value] of Object.entries(values)) {
    expect(value.trim(),`${lang}:${key}`).not.toBe('');
    expect(value.match(/\{\{\w+\}\}/g)||[]).toEqual(key.match(/\{\{\w+\}\}/g)||[]);
    for(const code of ['STOP','YELLOW','CLINICALLY_PENDING'])if(key.includes(code))expect(value).toContain(code);
  }
});
it.each(['en','es','pt','zh'])('%s resolves punctuation in natural-language keys without English fallback', lang => {
  const key='Cálculo bloqueado. Revisa las alertas.';
  const t=i18n.getFixedT(lang,'clinicalUi');
  expect(t(key,{keySeparator:false,nsSeparator:false})).toBe(resources[lang as keyof typeof resources][key]);
});
