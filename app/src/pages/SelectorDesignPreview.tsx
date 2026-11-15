import { Link } from 'react-router-dom';
import { ResuscitationCircuits } from '../components/ResuscitationCircuits';
import { getCanonicalGuide } from '../clinical-guides/canonical';

export default function SelectorDesignPreview() {
  const guide = getCanonicalGuide('arrhythmias-cardiac-arrest');
  return (
    <div className="selector-preview">
      <header className="selector-preview-topbar">
        <Link to="/" className="selector-preview-brand"><span className="selector-brand-mark" aria-hidden="true"><svg viewBox="0 0 28 28" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M4 14h5l3-7 5 14 3-7h4" /></svg></span>Emergency<span className="selector-brand-subtitle">Referencia clínica</span></Link>
        <span className="selector-preview-label">Propuesta visual <span>01</span></span>
      </header>
      <main className="selector-preview-main">
        <div className="selector-breadcrumb"><span>Biblioteca clínica</span><span aria-hidden="true">/</span><span>Cardiovascular</span></div>
        <section className="selector-hero" aria-labelledby="selector-page-title">
          <div><div className="selector-hero-eyebrow">CIRCUITOS DE REANIMACIÓN</div><h1 id="selector-page-title">Arritmias y<br />parada cardíaca<span>.</span></h1><p>Cuatro circuitos. Un acceso claro.</p></div>
          <aside className="selector-review-note"><span className="selector-master-status" data-status={guide?.status}>{guide?.status}</span><strong>Estado del selector</strong><p>El estado de revisión se conserva en cada circuito.</p></aside>
        </section>
        <ResuscitationCircuits base="/guides" />
        <details className="selector-canonical-details"><summary><span>Consultar criterios y excepciones de la guía</span><span aria-hidden="true">+</span></summary><div className="canonical-body">{guide?.body}</div><Link to="/guides/arrhythmias-cardiac-arrest">Abrir la guía completa →</Link></details>
        <footer className="selector-preview-footer"><span>Emergency <span aria-hidden="true">/</span> Propuesta de interfaz</span><span>Contenido y estados clínicos sin cambios</span></footer>
      </main>
    </div>
  );
}