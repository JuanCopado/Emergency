import { useMemo, useRef, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { clinicalGuides, getClinicalGuide } from '../clinical-guides/guides';
import { canonicalGuides, getCanonicalGuide, type CanonicalGuide } from '../clinical-guides/canonical';
import { Icon } from '../components/Icon';

type GuideStatus = 'green' | 'yellow' | 'red';

function StatusPill({ status }: { status: GuideStatus }) {
  const cls =
    status === 'green'
      ? 'bg-green-100 text-green-800'
      : status === 'red'
        ? 'bg-red-100 text-red-800'
        : 'bg-amber-100 text-amber-900';
  return <span className={`rounded-full px-2.5 py-1 text-xs font-bold uppercase tracking-wide ${cls}`}>{status}</span>;
}

function CanonicalBody({ guide }: { guide: CanonicalGuide }) {
  const lines = guide.body.split('\n');
  return (
    <section className="mt-5 space-y-2 text-sm leading-relaxed text-slate-800">
      {lines.map((raw, index) => {
        const line = raw.trim();
        if (!line) return <div key={index} className="h-1" />;
        if (line.startsWith('### ')) {
          return <h2 key={index} className="break-after-avoid pt-2 text-base font-extrabold text-sky-800">{line.slice(4)}</h2>;
        }
        if (line.startsWith('#### ')) {
          return <h3 key={index} className="break-after-avoid pt-1 font-bold text-slate-900">{line.slice(5)}</h3>;
        }
        if (line.startsWith('- ')) {
          return <p key={index} className="break-inside-avoid pl-4"><span className="mr-2 font-bold text-sky-700">•</span>{line.slice(2)}</p>;
        }
        return <p key={index} className="break-inside-avoid">{line}</p>;
      })}
    </section>
  );
}

export default function ClinicalGuides() {
  const { id } = useParams();
  const [query, setQuery] = useState('');
  const quickGuide = useMemo(() => (id ? getClinicalGuide(id) : undefined), [id]);
  const canonicalGuide = useMemo(() => (id ? getCanonicalGuide(id) : undefined), [id]);
  const sheetRef = useRef<HTMLDivElement>(null);

  const filteredCanonical = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return canonicalGuides;
    return canonicalGuides.filter((guide) =>
      [guide.id, guide.title, guide.bundle, guide.body].some((value) => value.toLowerCase().includes(q)),
    );
  }, [query]);

  const printGuide = () => window.print();

  const openFullscreen = async () => {
    const el = sheetRef.current;
    if (!el) return;
    if (document.fullscreenElement) {
      await document.exitFullscreen();
      return;
    }
    await el.requestFullscreen();
  };

  if (!id) {
    return (
      <div className="space-y-8">
        <div>
          <p className="section-title">Guías clínicas exportables</p>
          <h1 className="mt-2 text-3xl font-extrabold tracking-tight">Pantalla completa · impresión · PDF</h1>
          <p className="mt-2 max-w-3xl text-muted">
            Cobertura automática de los {canonicalGuides.length} módulos clínicos del manifiesto, conservando el contenido canónico y su estado de evidencia. Los algoritmos rápidos seleccionados disponen además de una vista resumida específica.
          </p>
        </div>

        <section>
          <h2 className="mb-3 text-xl font-bold">Algoritmos rápidos</h2>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {clinicalGuides.map((g) => (
              <Link key={g.id} to={`/guides/${g.id}`} className="card p-5 transition hover:border-primary/60">
                <div className="flex items-start justify-between gap-3">
                  <Icon name="book" className="text-primary" />
                  <StatusPill status={g.status} />
                </div>
                <h3 className="mt-4 text-xl font-bold">{g.title}</h3>
                <p className="mt-1 text-sm text-muted">{g.subtitle}</p>
                <p className="mt-4 text-xs text-muted">Fuente: {g.sourceModule}</p>
              </Link>
            ))}
          </div>
        </section>

        <section>
          <div className="mb-3 flex flex-wrap items-end justify-between gap-3">
            <div>
              <h2 className="text-xl font-bold">Todos los módulos clínicos</h2>
              <p className="text-sm text-muted">{filteredCanonical.length} de {canonicalGuides.length}</p>
            </div>
            <label className="w-full max-w-md">
              <span className="sr-only">Buscar guía clínica</span>
              <input
                className="input"
                type="search"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Buscar: sepsis, coma, hiperpotasemia, pediatría…"
              />
            </label>
          </div>
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
            {filteredCanonical.map((guide) => (
              <Link key={guide.id} to={`/guides/${guide.id}`} className="card p-4 transition hover:border-primary/60">
                <div className="flex items-start justify-between gap-3">
                  <span className="min-w-0">
                    <span className="block truncate font-bold">{guide.title}</span>
                    <span className="mt-1 block truncate text-xs text-muted">{guide.id}</span>
                  </span>
                  <StatusPill status={guide.status} />
                </div>
                <p className="mt-3 text-xs text-muted">{guide.bundle}</p>
              </Link>
            ))}
          </div>
        </section>
      </div>
    );
  }

  if (!quickGuide && !canonicalGuide) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-bold">Guía no encontrada</h1>
        <Link to="/guides" className="btn-ghost">Volver a guías</Link>
      </div>
    );
  }

  const title = quickGuide?.title ?? canonicalGuide?.title ?? id;
  const subtitle = quickGuide?.subtitle ?? 'Guía canónica exportable';
  const status = (quickGuide?.status ?? canonicalGuide?.status ?? 'yellow') as GuideStatus;
  const sourceModule = quickGuide?.sourceModule ?? canonicalGuide?.id ?? id;
  const sourcePath = quickGuide?.sourcePath ?? canonicalGuide?.sourcePath ?? '';
  const reviewedAt = quickGuide?.reviewedAt ?? 'según repositorio actual';

  return (
    <div className="guide-page space-y-4">
      <div className="no-print flex flex-wrap items-center justify-between gap-3">
        <Link to="/guides" className="btn-ghost">← Guías</Link>
        <div className="flex flex-wrap gap-2">
          <button type="button" className="btn-ghost" onClick={openFullscreen}>Pantalla completa</button>
          <button type="button" className="btn-primary" onClick={printGuide}>Imprimir / guardar PDF</button>
        </div>
      </div>

      <div ref={sheetRef} className="clinical-guide-sheet rounded-2xl border border-border bg-white p-5 text-slate-950 shadow-card sm:p-7">
        <header className="border-b-4 border-sky-700 pb-4">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.18em] text-sky-700">Emergency · guía clínica</p>
              <h1 className="mt-1 text-3xl font-black tracking-tight">{title}</h1>
              <p className="mt-1 text-sm text-slate-600">{subtitle}</p>
            </div>
            <StatusPill status={status} />
          </div>
          <div className="mt-3 grid gap-1 text-xs text-slate-600 sm:grid-cols-2">
            <p><strong>Módulo fuente:</strong> {sourceModule}</p>
            <p><strong>Revisión:</strong> {reviewedAt}</p>
          </div>
        </header>

        {quickGuide ? (
          <>
            <section className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {quickGuide.steps.map((step) => (
                <article key={step.title} className="break-inside-avoid rounded-xl border border-slate-200 bg-slate-50 p-3.5">
                  <h2 className="text-sm font-extrabold text-sky-800">{step.title}</h2>
                  <p className="mt-1 text-sm leading-snug text-slate-800">{step.body}</p>
                </article>
              ))}
            </section>
            <section className="mt-5 grid gap-4 md:grid-cols-2">
              <div className="break-inside-avoid rounded-xl border-2 border-red-300 bg-red-50 p-4">
                <h2 className="font-extrabold text-red-800">STOP · puntos de alerta</h2>
                <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-red-950">
                  {quickGuide.stopPoints.map((point) => <li key={point}>{point}</li>)}
                </ul>
              </div>
              <div className="break-inside-avoid rounded-xl border-2 border-emerald-300 bg-emerald-50 p-4">
                <h2 className="font-extrabold text-emerald-800">Confirmación</h2>
                <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-emerald-950">
                  {quickGuide.confirmation.map((point) => <li key={point}>{point}</li>)}
                </ul>
              </div>
            </section>
          </>
        ) : canonicalGuide ? (
          <CanonicalBody guide={canonicalGuide} />
        ) : null}

        <footer className="mt-5 border-t border-slate-300 pt-3 text-[10px] leading-relaxed text-slate-600">
          {quickGuide ? <p><strong>Referencias:</strong> {quickGuide.references.join(' · ')}</p> : null}
          <p><strong>Origen:</strong> {sourcePath} · Estado {status.toUpperCase()} · La exportación PDF conserva el contenido del repositorio y no sustituye revisión humana/local.</p>
        </footer>
      </div>
    </div>
  );
}
