import { useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { canonicalProcedures, getCanonicalProcedure } from '../clinical-guides/procedures';
import { getProcedureSheet } from '../clinical-guides/procedureSheets';

const families = [...new Set(canonicalProcedures.map(p => p.family))];
const levels = [...new Set(canonicalProcedures.map(p => p.level))];
const fold = (text: string) => text.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
const sectionId = (title: string) => `procedure-${fold(title).replace(/[^a-z0-9]+/g, '-')}`;

export default function Procedures() {
  const { id } = useParams();
  const [query, setQuery] = useState('');
  const [family, setFamily] = useState('');
  const [level, setLevel] = useState('');
  const procedure = id ? getCanonicalProcedure(id.toUpperCase()) : undefined;
  const sheet = procedure && getProcedureSheet(procedure.id);
  if (id) return <div className="space-y-4">
    <Link className="btn-ghost" to="/procedures">← Procedimientos</Link>
    {!procedure ? <h1 className="text-2xl font-bold">Procedimiento no encontrado</h1> : <article className="space-y-4">
      <header className="card p-5 space-y-2">
        <p className="section-title">{procedure.id} · {procedure.level}</p>
        <h1 className="text-2xl font-extrabold">{sheet?.name || procedure.name}</h1>
        <p>{procedure.family}</p>
        <p className="inline-flex rounded-lg bg-warn-bg p-2 font-semibold text-warn">⚠ YELLOW · revisión clínica pendiente</p>
        {procedure.aliases.length > 0 && <p className="text-sm">Alias: {procedure.aliases.join(', ')}</p>}
      </header>
      {sheet ? <>
        <nav className="flex flex-wrap gap-2" aria-label="Secciones del procedimiento">
          {['STOP', 'Confirmación', 'Técnica paso a paso', 'Complicaciones', 'Fuentes'].map(title => <a key={title} href={`#${sectionId(title)}`} className="btn-ghost">{title}</a>)}
        </nav>
        <p className="text-sm text-muted">Ficha canónica completa · CLINICALLY_PENDING · no sustituye entrenamiento ni revisión clínica.</p>
        <section className="card p-4 whitespace-pre-line" aria-label="Preámbulo canónico">{sheet.provenance.family_preamble}</section>
        {/* Every source section is rendered verbatim once. Safety boxes lead the technique. */}
        {['Objetivo', 'Indicaciones', 'Contraindicaciones/precauciones', 'STOP', 'Confirmación', ...Object.keys(sheet.provenance.sections).filter(k => !['Objetivo', 'Indicaciones', 'Contraindicaciones/precauciones', 'STOP', 'Confirmación', 'Fuentes', 'QA'].includes(k))].map(title => {
          const content = sheet.provenance.sections[title];
          if (!content) return null;
          const tone = title === 'STOP' ? 'border-danger text-danger' : title === 'Confirmación' ? 'border-ok' : title === 'Contraindicaciones/precauciones' ? 'border-warn' : '';
          return <section id={sectionId(title)} key={title} className={`card p-4 ${tone}`} aria-label={title}>
            <h2 className="text-lg font-bold">{title === 'STOP' ? '⛔ ' : title === 'Confirmación' ? '✓ ' : ''}{title}</h2>
            <p className="mt-2 whitespace-pre-line leading-relaxed">{content}</p>
          </section>;
        })}
        {(sheet.rescue?.length || sheet.escalation?.length) ? <section className="card border-warn p-4" aria-label="Rescate y escalada">
          <h2 className="text-lg font-bold">⚠ Rescate / escalada</h2>
          {(['rescue', 'escalation'] as const).filter(key => sheet[key]?.length).map(key => <div key={key} className="mt-2"><h3 className="font-semibold">{key === 'rescue' ? 'Rescate' : 'Escalada'}</h3>{sheet[key]?.map((line, i) => <p key={i}>{line}</p>)}</div>)}
        </section> : null}
        <details open id={sectionId('Fuentes')} className="card p-4">
          <summary className="min-h-[44px] cursor-pointer font-bold">Fuentes y estado de revisión</summary>
          <p className="mt-2 whitespace-pre-line">{sheet.provenance.sections.Fuentes}</p>
          <p className="mt-2">{sheet.provenance.sections.QA}</p>
          <p className="mt-2 text-sm">Fuente canónica: clinical/{sheet.provenance.source_path}</p>
        </details>
      </> : <p role="alert">Ficha canónica no disponible. No se puede mostrar la técnica.</p>}
    </article>}
  </div>;

  const matches = canonicalProcedures.filter(p => (!family || p.family === family) && (!level || p.level === level) && fold([p.id, p.name, getProcedureSheet(p.id)?.name || '', ...p.aliases].join(' ')).includes(fold(query.trim())));
  return <div className="space-y-5">
    <header><h1 className="text-3xl font-extrabold">Procedimientos</h1><p className="mt-2">196 canónicos · 4 alias · 16 familias · YELLOW: revisión clínica pendiente.</p><p className="text-sm text-muted">196 fichas completas desde la fuente canónica; imágenes sujetas a revisión separada.</p></header>
    <div className="grid gap-3 sm:grid-cols-3">
      <label>Nombre o PROC-ID<input className="input mt-1" type="search" value={query} onChange={e => setQuery(e.target.value)} /></label>
      <label className="min-w-0">Familia<select className="input mt-1" value={family} onChange={e => setFamily(e.target.value)}><option value="">Todas</option>{families.map(f => <option key={f}>{f}</option>)}</select></label>
      <label>Nivel<select className="input mt-1" value={level} onChange={e => setLevel(e.target.value)}><option value="">Todos</option>{levels.map(l => <option key={l}>{l}</option>)}</select></label>
    </div>
    <p role="status">{matches.length} procedimientos</p>
    {matches.length === 0 && <p>No hay coincidencias. Prueba otro nombre, ID o filtro.</p>}
    <ul className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">{matches.map(p => <li key={p.id} className="min-w-0"><Link to={`/procedures/${p.id}`} className="card block h-full p-4 hover:border-primary">
      <p className="text-xs font-semibold text-muted">{p.id} · {p.level}</p><h2 className="mt-1 font-bold">{p.name}</h2><p className="mt-2 text-xs">{p.family}</p><p className="mt-2 text-sm text-warn">⚠ YELLOW · {getProcedureSheet(p.id) ? 'Ficha completa' : 'No disponible'}</p>
    </Link></li>)}</ul>
  </div>;
}
