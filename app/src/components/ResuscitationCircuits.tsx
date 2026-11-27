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

const monitoring = [
  ['Arritmia con pulso', 'ECG, presión arterial, perfusión y estabilidad hemodinámica.'],
  ['Parada cardíaca', 'Ritmo, calidad de RCP y capnografía cuando proceda.'],
  ['Recuperación de circulación espontánea', 'Reevaluación fisiológica y circuito posreanimación correspondiente.'],
  ['Pediatría', 'Algoritmo pediátrico; no trasladar dosis ni energías del adulto.'],
] as const;

export function ResuscitationCircuits({ base }: { base: '/guides' | '/clinical' }) {
  const ui = useClinicalUi();
  return (
    <nav id="resuscitation-circuits" tabIndex={-1} aria-label="Circuitos de reanimación" className="no-print mt-5 scroll-mt-20 rounded-xl border border-border p-4">
      <h2 className="font-bold">Abrir el circuito correspondiente</h2>
      <p className="mt-1 text-sm">Aplica los criterios y excepciones de la guía anterior. Selección manual; cada circuito conserva su estado de revisión.</p>
      <p className="mt-3 text-sm">{ui('CLINICALLY_PENDING · Monitorización aprobada en MED-RES-CARDIO-01 v1; no modifica los cuatro algoritmos ni sus dosis.')}</p>
      <div className="mt-3 overflow-x-auto">
        <table aria-label={ui('Monitorización según el contexto de reanimación')} className="w-full text-left text-sm">
          <thead><tr><th scope="col" className="p-2">{ui('Contexto')}</th><th scope="col" className="p-2">{ui('Monitorización')}</th></tr></thead>
          <tbody>{monitoring.map(([context, detail]) => <tr key={context} className="border-t border-border"><th scope="row" className="p-2">{ui(context)}</th><td className="p-2">{ui(detail)}</td></tr>)}</tbody>
        </table>
      </div>
      <p className="mt-2 text-sm">{ui('El ETCO₂ aislado no debe determinar la interrupción de la reanimación. Mantener la excepción pediátrica de bradicardia con mala perfusión pese a soporte respiratorio adecuado y la exclusión neonatal de la guía anterior.')}</p>
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
