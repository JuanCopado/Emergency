import { useMemo, useRef, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { canonicalGuides, getCanonicalGuide, type CanonicalGuide } from '../clinical-guides/canonical';
import { getRelatedProcedures } from '../clinical-guides/relatedProcedures';

function StatusPill({ status }: { status: 'green' | 'yellow' | 'red' }) {
  const cls = status === 'green' ? 'bg-green-100 text-green-800' : status === 'red' ? 'bg-red-100 text-red-800' : 'bg-amber-100 text-amber-900';
  return <span className={`rounded-full px-2.5 py-1 text-xs font-bold uppercase tracking-wide ${cls}`}>{status}</span>;
}

function CanonicalContent({ guide }: { guide: CanonicalGuide }) {
  return (
    <div className="canonical-body space-y-2 text-sm leading-relaxed">
      {guide.body.split('\n').map((raw, index) => {
        const line = raw.trim();
        if (!line) return <div key={index} className="h-1" />;
        if (line.startsWith('### ')) return <h2 key={index} className="pt-3 text-lg font-extrabold">{line.slice(4)}</h2>;
        if (line.startsWith('#### ')) return <h3 key={index} className="pt-2 font-bold">{line.slice(5)}</h3>;
        if (line.startsWith('- ')) return <p key={index} className="pl-4"><span className="mr-2 font-bold text-primary">•</span>{line.slice(2)}</p>;
        return <p key={index}>{line}</p>;
      })}
    </div>
  );
}

export default function ClinicalLibrary() {
  const { id } = useParams();
  const [query, setQuery] = useState('');
  const sheetRef = useRef<HTMLDivElement>(null);
  const guide = useMemo(() => (id ? getCanonicalGuide(id) : undefined), [id]);
  const related = useMemo(() => (guide ? getRelatedProcedures(guide) : []), [guide]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return canonicalGuides;
    return canonicalGuides.filter((item) =>
      [item.id, item.title, item.bundle, item.body].some((value) => value.toLowerCase().includes(q)),
    );
  }, [query]);

  const openFullscreen = async () => {
    if (!sheetRef.current) return;
    if (document.fullscreenElement) await document.exitFullscreen();
    else await sheetRef.current.requestFullscreen();
  };

  if (!id) {
    return (
      <div className="space-y-6">
        <div>
          <p className="section-title">Biblioteca clínica</p>
          <h1 className="mt-2 text-3xl font-extrabold tracking-tight">Patologías y módulos</h1>
          <p className="mt-2 max-w-3xl text-muted">Acceso directo al contenido clínico canónico con botones de algoritmo, pantalla completa, PDF y procedimientos relacionados.</p>
        </div>
        <input className="input max-w-xl" type="search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Buscar patología o módulo…" />
        <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
          {filtered.map((item) => (
            <Link key={item.id} to={`/clinical/${item.id}`} className="card p-4 transition hover:border-primary/60">
              <div className="flex items-start justify-between gap-3">
                <span className="font-bold">{item.title}</span>
                <StatusPill status={item.status} />
              </div>
              <p className="mt-2 text-xs text-muted">{item.id}</p>
              <p className="mt-1 text-xs text-muted">{item.bundle}</p>
            </Link>
          ))}
        </div>
      </div>
    );
  }

  if (!guide) {
    return <div className="space-y-4"><h1 className="text-2xl font-bold">Módulo no encontrado</h1><Link to="/clinical" className="btn-ghost">Volver</Link></div>;
  }

  return (
    <div className="space-y-4">
      <div className="no-print flex flex-wrap items-center justify-between gap-3">
        <Link to="/clinical" className="btn-ghost">← Patologías</Link>
        <div className="flex flex-wrap gap-2">
          <Link to={`/guides/${guide.id}`} className="btn-primary">{guide.format === 'algorithm' ? 'Algoritmo' : 'Guía'}</Link>
          <button type="button" className="btn-ghost" onClick={openFullscreen}>Pantalla completa</button>
          <button type="button" className="btn-ghost" onClick={() => window.print()}>PDF / imprimir</button>
          <a href="#related-procedures" className="btn-ghost">Procedimientos relacionados</a>
        </div>
      </div>

      <div ref={sheetRef} className="clinical-module-sheet rounded-2xl border border-border bg-surface p-5 shadow-card sm:p-7">
        <header className="border-b border-border pb-4">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <p className="section-title">Emergency · módulo clínico</p>
              <h1 className="mt-1 text-3xl font-black tracking-tight">{guide.title}</h1>
              <p className="mt-2 text-sm text-muted">{guide.id} · {guide.bundle}</p>
            </div>
            <StatusPill status={guide.status} />
          </div>
        </header>

        <div className="mt-5"><CanonicalContent guide={guide} /></div>

        <section id="related-procedures" className="mt-7 border-t border-border pt-5">
          <h2 className="text-xl font-bold">Procedimientos relacionados</h2>
          <p className="mt-1 text-sm text-muted">Sugeridos por relación temática con el módulo; siempre prevalece la ficha canónica del procedimiento.</p>
          {related.length ? (
            <div className="mt-4 grid gap-3 md:grid-cols-2">
              {related.map((proc) => (
                <div key={proc.id} className="rounded-xl border border-border bg-surface-2 p-3">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="font-bold">{proc.name}</p>
                      <p className="mt-1 text-xs text-muted">{proc.id} · {proc.family}</p>
                    </div>
                    <span className="rounded-full border border-border px-2 py-1 text-[10px] font-bold">{proc.level}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : <p className="mt-3 text-sm text-muted">No se detectaron procedimientos relacionados de forma automática.</p>}
        </section>

        <footer className="mt-6 border-t border-border pt-3 text-xs text-muted">
          Fuente: {guide.sourcePath} · Estado {guide.status.toUpperCase()} · La exportación no cambia el estado clínico ni sustituye revisión humana/local.
        </footer>
      </div>
    </div>
  );
}
