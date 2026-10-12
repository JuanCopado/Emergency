import { useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { canonicalProcedures, getCanonicalProcedure } from '../clinical-guides/procedures';
import { getProcedurePilot } from '../clinical-guides/procedurePilots';

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
  const pilot = procedure && getProcedurePilot(procedure.id);
  if (id) return <div className="space-y-4">
    <Link className="btn-ghost" to="/procedures">← Procedimientos</Link>
    {!procedure ? <h1 className="text-2xl font-bold">Procedimiento no encontrado</h1> : <article className="space-y-4">
      <header className="card p-5 space-y-2">
        <p className="section-title">{procedure.id} · {procedure.level}</p>
        <h1 className="text-2xl font-extrabold">{procedure.name}</h1>
        <p>{procedure.family}</p>
        <p className="inline-flex rounded-lg bg-warn-bg p-2 font-semibold text-warn">⚠ YELLOW · revisión clínica pendiente</p>
        {procedure.aliases.length > 0 && <p className="text-sm">Alias: {procedure.aliases.join(', ')}</p>}
      </header>
      {pilot ? <>
        <nav className="flex flex-wrap gap-2" aria-label="Secciones del procedimiento">
          {['STOP', 'Confirmación', 'Técnica paso a paso', 'Complicaciones', 'Fuentes'].map(title => <a key={title} href={`#${sectionId(title)}`} className="btn-ghost">{title}</a>)}
        </nav>
        <p className="text-sm text-muted">Piloto de presentación · no sustituye entrenamiento ni revisión clínica.</p>
        <section className="card p-4 whitespace-pre-line" aria-label="Preámbulo canónico">{pilot.provenance.family_preamble}</section>
        {/* Every source section is rendered verbatim once. Safety boxes lead the technique. */}
        {['Objetivo', 'Indicaciones', 'Contraindicaciones/precauciones', 'STOP', 'Confirmación', ...Object.keys(pilot.provenance.sections).filter(k => !['Objetivo', 'Indicaciones', 'Contraindicaciones/precauciones', 'STOP', 'Confirmación', 'Fuentes', 'QA'].includes(k))].map(title => {
          const content = pilot.provenance.sections[title];
          if (!content) return null;
          const tone = title === 'STOP' ? 'border-danger text-danger' : title === 'Confirmación' ? 'border-ok' : title === 'Contraindicaciones/precauciones' ? 'border-warn' : '';
          return <section id={sectionId(title)} key={title} className={`card p-4 ${tone}`} aria-label={title}>
            <h2 className="text-lg font-bold">{title === 'STOP' ? '⛔ ' : title === 'Confirmación' ? '✓ ' : ''}{title}</h2>
            <p className="mt-2 whitespace-pre-line leading-relaxed">{content}</p>
          </section>;
        })}
        <section className="card border-warn p-4" aria-label="Rescate y escalada">
          <h2 className="text-lg font-bold">⚠ Rescate / escalada</h2>
          {(['rescue', 'escalation'] as const).map(key => <div key={key} className="mt-2"><h3 className="font-semibold">{key === 'rescue' ? 'Rescate' : 'Escalada'}</h3>{pilot[key]?.length ? pilot[key].map((line, i) => <p key={i}>{line}</p>) : <p>Pendiente de revisión: no hay extracción canónica explícita.</p>}</div>)}
        </section>
        <details id={sectionId('Fuentes')} className="card p-4">
          <summary className="min-h-[44px] cursor-pointer font-bold">Fuentes y estado de revisión</summary>
          <p className="mt-2 whitespace-pre-line">{pilot.provenance.sections.Fuentes}</p>
          <p className="mt-2">{pilot.provenance.sections.QA}</p>
          <p className="mt-2 text-sm">Fuente canónica: clinical/{pilot.provenance.source_path}</p>
        </details>
        <figure className="rounded-xl border-2 border-dashed border-border p-5">
          <figcaption>Espacio para una imagen final. Sin imagen aprobada en el registro visual; revisión visual y clínica pendientes.</figcaption>
        </figure>
      </> : <section className="card p-4 space-y-3">
        <h2 className="font-bold">Ficha fuera del piloto visual</h2>
        <p>Este catálogo conserva los 196 procedimientos. Solo diez tienen layout piloto en esta fase.</p>
        <p className="text-sm">Fuente textual: {procedure.sourcePath} · {procedure.sourceHeading}</p>
        <Link to="/clinical/emergency-procedures" className="btn-ghost">Módulo de procedimientos</Link>
      </section>}
    </article>}
  </div>;

  const matches = canonicalProcedures.filter(p => (!family || p.family === family) && (!level || p.level === level) && fold([p.id, p.name, ...p.aliases].join(' ')).includes(fold(query.trim())));
  return <div className="space-y-5">
    <header><h1 className="text-3xl font-extrabold">Procedimientos</h1><p className="mt-2">196 canónicos · 4 alias · 16 familias · YELLOW: revisión clínica pendiente.</p><p className="text-sm text-muted">Diez fichas piloto. Los demás resultados identifican su fuente textual.</p></header>
    <div className="grid gap-3 sm:grid-cols-3">
      <label>Nombre o PROC-ID<input className="input mt-1" type="search" value={query} onChange={e => setQuery(e.target.value)} /></label>
      <label className="min-w-0">Familia<select className="input mt-1" value={family} onChange={e => setFamily(e.target.value)}><option value="">Todas</option>{families.map(f => <option key={f}>{f}</option>)}</select></label>
      <label>Nivel<select className="input mt-1" value={level} onChange={e => setLevel(e.target.value)}><option value="">Todos</option>{levels.map(l => <option key={l}>{l}</option>)}</select></label>
    </div>
    <p role="status">{matches.length} procedimientos</p>
    {matches.length === 0 && <p>No hay coincidencias. Prueba otro nombre, ID o filtro.</p>}
    <ul className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">{matches.map(p => <li key={p.id} className="min-w-0"><Link to={`/procedures/${p.id}`} className="card block h-full p-4 hover:border-primary">
      <p className="text-xs font-semibold text-muted">{p.id} · {p.level}</p><h2 className="mt-1 font-bold">{p.name}</h2><p className="mt-2 text-xs">{p.family}</p><p className="mt-2 text-sm text-warn">⚠ YELLOW · {getProcedurePilot(p.id) ? 'Ficha piloto' : 'Referencia textual'}</p>
    </Link></li>)}</ul>
  </div>;
}
