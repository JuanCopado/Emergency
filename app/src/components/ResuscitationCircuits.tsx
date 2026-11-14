import { Link } from 'react-router-dom';
import { getCanonicalGuide } from '../clinical-guides/canonical';

const circuits = [
  ['adult-arrhythmias', 'Adulto · arritmia con pulso'],
  ['adult-cardiac-arrest', 'Adulto · parada cardíaca'],
  ['pediatric-arrhythmias', 'Pediatría · arritmia con circulación'],
  ['pediatric-cardiac-arrest', 'Pediatría · parada o indicación de RCP'],
] as const;

export function ResuscitationCircuits({ base }: { base: '/guides' | '/clinical' }) {
  return (
    <nav aria-label="Circuitos de reanimación" className="no-print mt-5 rounded-xl border border-border p-4">
      <h2 className="font-bold">Abrir el circuito correspondiente</h2>
      <p className="mt-1 text-sm">Aplica los criterios y excepciones de la guía anterior. Selección manual; cada circuito conserva su estado de revisión.</p>
      <div className="mt-3 grid gap-3 sm:grid-cols-2">
        {circuits.map(([id, label]) => {
          const guide = getCanonicalGuide(id);
          return guide ? (
            <Link key={id} to={`${base}/${id}`} className="rounded-lg border border-border p-3 hover:border-primary focus-visible:outline focus-visible:outline-2 focus-visible:outline-primary">
              <span className="block font-semibold">{label}</span>
              <span className="text-xs uppercase">{guide.status}</span>
            </Link>
          ) : <span key={id}>{label} · circuito no disponible</span>;
        })}
      </div>
    </nav>
  );
}
