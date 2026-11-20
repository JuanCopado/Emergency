export type Field = { key:string; label:string; type:'number'|'choice'; unit?:string; minimum?:number|null; maximum?:number|null; integer?:boolean; optional:boolean; options?:{value:string|number|boolean;label:string}[] };
export type Candidate = { value:string; source:string };
export type Sample = { label:string; lines:string[] };
const canonicalMicro = (s:string) => s.replaceAll('μ','µ');
const fold = (s:string) => canonicalMicro(s).trim().normalize('NFD').replace(/\p{M}/gu,'').toLowerCase().replace(/\s+/g,' ');
const aliases:Record<string,string[]> = {
  bun_mg_dL:['BUN'], heart_rate_bpm:['FC'], pulse_bpm:['FC'], respiratory_rate:['FR'],
  systolic_bp_mmHg:['PAS'], diastolic_bp_mmHg:['PAD'], bilirubin_mg_dL:['Bilirrubina total'],
};

export function candidates(fields:Field[], lines:string[]) {
  const found:Record<string,Candidate[]> = {};
  for (const field of fields) {
    for (const source of lines) {
      const line = fold(source);
      const name = [field.label,...(aliases[field.key] ?? [])].map(fold).find(label =>
        line.startsWith(label) && /^[\s:=]/.test(line.slice(label.length)));
      if (!name) continue;
      const raw = line.slice(name.length).replace(/^\s*[:=]?\s*/, '');
      let value:string;
      if (field.type === 'choice') {
        const option = field.options?.find(o => fold(o.label) === raw);
        if (!option) continue;
        value = JSON.stringify(option.value);
      } else {
        const match = /^-?\d+(?:[.,]\d+)?/.exec(raw);
        if (!match || !canonicalMicro(source).trimEnd().endsWith(canonicalMicro(field.unit ?? '')) || raw.slice(match[0].length).trim() !== fold(field.unit ?? '')) continue;
        // A single separator followed by three digits can be decimal or thousands.
        if (/^[1-9]\d*[.,]\d{3}$/.test(match[0])) continue;
        value = match[0].replace(',', '.');
        const n = Number(value);
        if (!Number.isFinite(n) || (field.integer && !Number.isInteger(n)) ||
            (field.minimum != null && n < field.minimum) || (field.maximum != null && n > field.maximum)) continue;
      }
      (found[field.key] ??= []).push({value,source});
    }
  }
  return found;
}

export function samples(text:string, page:string):Sample[] {
  const sections = text.replace(/\r/g,'').split(/\n\s*\n|\n(?=(?:muestra|sample|amostra|fecha|hora)\s*[:=])/i);
  return sections.map(section=>section.trim().split('\n').map(line=>line.trim())).filter(lines=>lines.some(Boolean))
    .map((lines,i)=>({label:`${page} · bloque ${i+1} · ${lines[0]!.slice(0,90)}`,lines}));
}

