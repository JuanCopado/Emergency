import { useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { ResuscitationCircuits } from '../components/ResuscitationCircuits';
import { getCanonicalGuide } from '../clinical-guides/canonical';
import './SelectorConcepts.css';
import './SelectorCombinedPreview.css';

type Theme = 'light' | 'dark';
const storageKey = 'emergency-selector-design-theme';

export default function SelectorCombinedPreview() {
  const [params, setParams] = useSearchParams();
  const [savedTheme, setSavedTheme] = useState<Theme>(() => {
    try { return localStorage.getItem(storageKey) === 'dark' ? 'dark' : 'light'; }
    catch { return 'light'; }
  });
  const requested = params.get('theme');
  const theme = requested === 'light' || requested === 'dark' ? requested : savedTheme;
  const guide = getCanonicalGuide('arrhythmias-cardiac-arrest');
  function chooseTheme(next: Theme) {
    setSavedTheme(next);
    setParams({ theme: next }, { replace: true });
    try { localStorage.setItem(storageKey, next); } catch { /* The preview still works without storage. */ }
  }
  return (
    <div className={`selector-preview concept-orbit combined-preview ${theme === 'dark' ? 'theme-noctis' : 'theme-orbit'}`} data-theme={theme}>
      <div className="combined-design-note"><span>Orbit + Noctis <span aria-hidden="true">/</span> Propuesta combinada</span><Link to="/design/arrhythmia-selector?concept=orbit">Ver las cuatro propuestas <span aria-hidden="true">↗</span></Link></div>
      <header className="selector-preview-topbar">
        <Link to="/" className="selector-preview-brand"><span className="selector-brand-mark" aria-hidden="true"><svg viewBox="0 0 28 28" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M4 14h5l3-7 5 14 3-7h4" /></svg></span>Emergency<span className="selector-brand-subtitle">Referencia clínica</span></Link>
        <div className="combined-theme-control" role="group" aria-label="Apariencia">
          <button type="button" aria-pressed={theme === 'light'} onClick={() => chooseTheme('light')}><svg aria-hidden="true" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.4"><circle cx="10" cy="10" r="3.3" /><path d="M10 1v2m0 14v2M1 10h2m14 0h2M3.6 3.6 5 5m10 10 1.4 1.4M3.6 16.4 5 15m10-10 1.4-1.4" /></svg>Claro</button>
          <button type="button" aria-pressed={theme === 'dark'} onClick={() => chooseTheme('dark')}><svg aria-hidden="true" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.4"><path d="M16.8 12A7 7 0 0 1 8 3.2 7 7 0 1 0 16.8 12Z" /></svg>Oscuro</button>
        </div>
      </header>
      <main className="selector-preview-main">
        <div className="selector-breadcrumb"><span>Biblioteca clínica</span><span aria-hidden="true">/</span><span>Cardiovascular</span></div>
        <section className="selector-hero" aria-labelledby="combined-selector-title">
          <div><div className="selector-hero-eyebrow">CIRCUITOS DE REANIMACIÓN</div><h1 id="combined-selector-title">Arritmias y<br />parada cardíaca<span>.</span></h1><p>Todo a mano. Todo en su lugar.</p></div>
          <aside className="selector-review-note"><span className="selector-master-status" data-status={guide?.status}>{guide?.status}</span><strong>Estado del selector</strong><p>El estado de revisión se conserva en cada circuito.</p></aside>
        </section>
        <div className="concept-workspace"><div className="concept-workspace-top"><span>Biblioteca de circuitos</span><span>Adulto + pediatría</span></div><ResuscitationCircuits base="/guides" /></div>
        <details className="selector-canonical-details"><summary><span>Consultar criterios y excepciones de la guía</span><span aria-hidden="true">+</span></summary><div className="canonical-body">{guide?.body}</div><Link to="/guides/arrhythmias-cardiac-arrest">Abrir la guía completa →</Link></details>
        <footer className="selector-preview-footer"><span>Orbit + Noctis <span aria-hidden="true">/</span> Base visual para seguir afinando</span><span>Contenido y estados clínicos sin cambios</span></footer>
      </main>
    </div>
  );
}