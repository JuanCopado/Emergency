import { Link, useSearchParams } from 'react-router-dom';

import { ResuscitationCircuits } from '../components/ResuscitationCircuits';
import { getCanonicalGuide } from '../clinical-guides/canonical';
import './SelectorConcepts.css';

export default function SelectorDesignPreview() {
  const [params] = useSearchParams();
  const concepts = [
    { id: 'horizon', name: 'Horizon', description: 'Claridad clínica. Precisión digital.', detail: 'Azul sereno · superficies claras · estructura abierta' },
    { id: 'noctis', name: 'Noctis', description: 'Lo esencial, sin distracciones.', detail: 'Grafito · acentos menta · contraste controlado' },
    { id: 'atlas', name: 'Atlas', description: 'Una referencia. Cuatro caminos.', detail: 'Composición lateral · tonos minerales · jerarquía editorial' },
    { id: 'orbit', name: 'Orbit', description: 'Todo a mano. Todo en su lugar.', detail: 'Índigo · navegación compacta · lenguaje de workspace' },
  ] as const;
  const concept = concepts.find(c => c.id === params.get('concept')) ?? concepts[0];
  const guide = getCanonicalGuide('arrhythmias-cardiac-arrest');
  return (
    <div className={`selector-preview concept-${concept.id}`}>
      <div className="concept-switcher"><span>Estudio visual</span><nav aria-label="Propuestas visuales">{concepts.map(c => <Link key={c.id} to={`?concept=${c.id}`} aria-current={c.id === concept.id ? 'page' : undefined}>{c.name}</Link>)}</nav><span>4 direcciones</span></div>
      <aside className="concept-rail" aria-label="Identidad de la propuesta"><span className="rail-monogram">E</span><span className="rail-line" /><span className="rail-label">EMERGENCY</span><span className="rail-dot" /></aside>
      <header className="selector-preview-topbar">
        <Link to="/" className="selector-preview-brand"><span className="selector-brand-mark" aria-hidden="true"><svg viewBox="0 0 28 28" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M4 14h5l3-7 5 14 3-7h4" /></svg></span>Emergency<span className="selector-brand-subtitle">Referencia clínica</span></Link>
        <span className="selector-preview-label">{concept.name} <span>{String(concepts.indexOf(concept) + 1).padStart(2, '0')}</span></span>
      </header>
      <main className="selector-preview-main">
        <div className="selector-breadcrumb"><span>Biblioteca clínica</span><span aria-hidden="true">/</span><span>Cardiovascular</span></div>
        <section className="selector-hero" aria-labelledby="selector-page-title">
          <div><div className="selector-hero-eyebrow">CIRCUITOS DE REANIMACIÓN</div><h1 id="selector-page-title">Arritmias y<br />parada cardíaca<span>.</span></h1><p>{concept.description}</p></div>
          <aside className="selector-review-note"><span className="selector-master-status" data-status={guide?.status}>{guide?.status}</span><strong>Estado del selector</strong><p>El estado de revisión se conserva en cada circuito.</p></aside>
        </section>
        <div className="concept-workspace"><div className="concept-workspace-top"><span>Biblioteca de circuitos</span><span>Adulto + pediatría</span></div><ResuscitationCircuits base="/guides" /></div>
        <details className="selector-canonical-details"><summary><span>Consultar criterios y excepciones de la guía</span><span aria-hidden="true">+</span></summary><div className="canonical-body">{guide?.body}</div><Link to="/guides/arrhythmias-cardiac-arrest">Abrir la guía completa →</Link></details>
        <footer className="selector-preview-footer"><span>{concept.name} <span aria-hidden="true">/</span> {concept.detail}</span><span>Contenido y estados clínicos sin cambios</span></footer>
      </main>
    </div>
  );
}