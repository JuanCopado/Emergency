import { Link } from 'react-router-dom';
import { getCanonicalGuide } from '../clinical-guides/canonical';
import { useClinicalUi } from '../i18n/useClinicalUi';

export function ResuscitationShortcut() {
  const ui = useClinicalUi();
  return <a href="#resuscitation-circuits" className="btn-ghost">{ui('Ir a los circuitos Adulto / Pediatría')}</a>;
}

const circuits = [
  ['adult-arrhythmias', 'Adulto · arritmia con pulso'],
  ['adult-cardiac-arrest', 'Adulto · parada cardíaca'],
  ['pediatric-arrhythmias', 'Pediatría · arritmia con circulación'],
  ['pediatric-cardiac-arrest', 'Pediatría · parada o indicación de RCP'],
] as const;

export function ResuscitationCircuits({ base }: { base: '/guides' | '/clinical' }) {
  return (
    <nav id="resuscitation-circuits" tabIndex={-1} aria-label="Circuitos de reanimación" className="no-print mt-5 scroll-mt-20 rounded-xl border border-border p-4">
      <h2 className="font-bold">Abrir el circuito correspondiente</h2>
      <p className="mt-1 text-sm">Aplica los criterios y excepciones de la guía anterior. Selección manual; cada circuito conserva su estado de revisión.</p>
      <div className="mt-3 grid grid-cols-2 gap-3">
        {circuits.map(([id, label]) => {
          const guide = getCanonicalGuide(id);
          return guide ? (
            <Link key={id} to={`${base}/${id}`} className="rounded-lg border border-border p-2.5 hover:border-primary focus-visible:outline focus-visible:outline-2 focus-visible:outline-primary sm:p-3">
              <span className="block text-sm font-semibold sm:text-base">{label}</span>
              <span className="text-xs uppercase">{guide.status}</span>
            </Link>
          ) : <span key={id}>{label} · circuito no disponible</span>;
        })}
      </div>
    </nav>
  );
}
