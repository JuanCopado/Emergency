import { Link } from 'react-router-dom';
import { getCanonicalGuide } from '../clinical-guides/canonical';
import './ResuscitationCircuits.css';

const groups = [
  { title: 'Adulto', number: '01', circuits: [
    ['adult-arrhythmias', 'Adulto · arritmia con pulso', 'Arritmia con pulso'],
    ['adult-cardiac-arrest', 'Adulto · parada cardíaca', 'Parada cardíaca'],
  ] },
  { title: 'Pediatría', number: '02', circuits: [
    ['pediatric-arrhythmias', 'Pediatría · arritmia con circulación', 'Arritmia con circulación'],
    ['pediatric-cardiac-arrest', 'Pediatría · parada o indicación de RCP', 'Parada o indicación de RCP'],
  ] },
] as const;

export function ResuscitationCircuits({ base }: { base: '/guides' | '/clinical' }) {
  return (
    <nav aria-label="Circuitos de reanimación" className="no-print circuit-selector">
      <div className="circuit-selector-heading">
        <div><span className="circuit-eyebrow">ACCESO A LOS CIRCUITOS</span><h2>Abrir el circuito correspondiente</h2></div>
        <span className="circuit-manual"><span aria-hidden="true" />Selección manual</span>
      </div>
      <p className="circuit-intro">Aplica los criterios y excepciones de la guía anterior. Selección manual; cada circuito conserva su estado de revisión.</p>
      <div className="circuit-groups">
        {groups.map(group => (
          <section className="circuit-group" key={group.title} aria-label={group.title}>
            <header className="circuit-group-header"><h3>{group.title}</h3><span aria-hidden="true">{group.number}</span></header>
            <div className="circuit-links">
              {group.circuits.map(([id, label, title], index) => {
                const guide = getCanonicalGuide(id);
                return guide ? (
                  <Link key={id} to={`${base}/${id}`} aria-label={`${label} ${guide.status}`} className="circuit-link">
                    <span className="circuit-symbol" aria-hidden="true"><svg viewBox="0 0 28 28" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">{index === 0 ? <path d="M3 14h5l3-7 5 14 3-7h6" /> : <><path d="M14 23S4 17 4 10.5A5.5 5.5 0 0 1 14 7a5.5 5.5 0 0 1 10 3.5C24 17 14 23 14 23Z" /><path d="M10 14h8m-4-4v8" /></>}</svg></span>
                    <span className="circuit-link-copy"><span className="circuit-link-title">{title}</span><span className="circuit-status" data-status={guide.status}><span aria-hidden="true" />{guide.status}</span></span>
                    <span className="circuit-arrow" aria-hidden="true"><svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M4 10h12m-5-5 5 5-5 5" /></svg></span>
                  </Link>
                ) : <span key={id} className="circuit-unavailable">{label} · circuito no disponible</span>;
              })}
            </div>
          </section>
        ))}
      </div>
    </nav>
  );
}