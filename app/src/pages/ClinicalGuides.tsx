import { useMemo, useRef } from 'react';
import { Link, useParams } from 'react-router-dom';
import { clinicalGuides, getClinicalGuide } from '../clinical-guides/guides';
import { Icon } from '../components/Icon';

function StatusPill({ status }: { status: 'green' | 'yellow' | 'red' }) {
  const cls = status === 'green' ? 'bg-green-100 text-green-800' : status === 'red' ? 'bg-red-100 text-red-800' : 'bg-amber-100 text-amber-900';
  return <span className={`rounded-full px-2.5 py-1 text-xs font-bold uppercase tracking-wide ${cls}`}>{status}</span>;
}

export default function ClinicalGuides() {
  const { id } = useParams();
  const guide = useMemo(() => (id ? getClinicalGuide(id) : undefined), [id]);
  const sheetRef = useRef<HTMLDivElement>(null);

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
      <div className="space-y-6">
        <div>
          <p className="section-title">Guías clínicas exportables</p>
          <h1 className="mt-2 text-3xl font-extrabold tracking-tight">Algoritmos para pantalla e impresión</h1>
          <p className="mt-2 max-w-3xl text-muted">
            Cada guía se construye desde contenido canónico del repositorio. La opción “Imprimir / guardar PDF” utiliza la impresión del navegador para generar PDF A4 apaisado.
          </p>
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {clinicalGuides.map((g) => (
            <Link key={g.id} to={`/guides/${g.id}`} className="card p-5 transition hover:border-primary/60">
              <div className="flex items-start justify-between gap-3">
                <Icon name="book" className="text-primary" />
                <StatusPill status={g.status} />
              </div>
              <h2 className="mt-4 text-xl font-bold">{g.title}</h2>
              <p className="mt-1 text-sm text-muted">{g.subtitle}</p>
              <p className="mt-4 text-xs text-muted">Fuente: {g.sourceModule}</p>
            </Link>
          ))}
        </div>
      </div>
    );
  }

  if (!guide) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-bold">Guía no encontrada</h1>
        <Link to="/guides" className="btn-ghost">Volver a guías</Link>
      </div>
    );
  }

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
              <h1 className="mt-1 text-3xl font-black tracking-tight">{guide.title}</h1>
              <p className="mt-1 text-sm text-slate-600">{guide.subtitle}</p>
            </div>
            <StatusPill status={guide.status} />
          </div>
          <div className="mt-3 grid gap-1 text-xs text-slate-600 sm:grid-cols-2">
            <p><strong>Módulo fuente:</strong> {guide.sourceModule}</p>
            <p><strong>Revisión:</strong> {guide.reviewedAt}</p>
          </div>
        </header>

        <section className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {guide.steps.map((step) => (
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
              {guide.stopPoints.map((point) => <li key={point}>{point}</li>)}
            </ul>
          </div>
          <div className="break-inside-avoid rounded-xl border-2 border-emerald-300 bg-emerald-50 p-4">
            <h2 className="font-extrabold text-emerald-800">Confirmación</h2>
            <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-emerald-950">
              {guide.confirmation.map((point) => <li key={point}>{point}</li>)}
            </ul>
          </div>
        </section>

        <footer className="mt-5 border-t border-slate-300 pt-3 text-[10px] leading-relaxed text-slate-600">
          <p><strong>Referencias:</strong> {guide.references.join(' · ')}</p>
          <p><strong>Origen:</strong> {guide.sourcePath} · Estado {guide.status.toUpperCase()} · La exportación PDF no cambia el estado clínico ni sustituye revisión humana/local.</p>
        </footer>
      </div>
    </div>
  );
}
