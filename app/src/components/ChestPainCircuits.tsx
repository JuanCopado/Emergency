import { Link } from 'react-router-dom';
import { getCanonicalGuide } from '../clinical-guides/canonical';
import { useClinicalUi } from '../i18n/useClinicalUi';
import { EvidenceStatusPill } from './EvidenceStatusPill';

const circuitIds = [
  'acute-coronary-syndrome',
  'acute-aortic-syndrome',
  'pulmonary-embolism',
  'tension-pneumothorax',
  'cardiac-tamponade-pericardial-emergency',
] as const;

/** Manual links already named by the canonical chest-pain module; no triage. */
export function ChestPainCircuits({ moduleId, base }: {
  moduleId: string;
  base: '/guides' | '/clinical';
}) {
  const ui = useClinicalUi();
  if (moduleId !== 'non-coronary-chest-pain') return null;
  return (
    <nav aria-label={ui('Circuitos por causa de dolor torácico')} className="no-print mt-5 rounded-xl border border-border p-4">
      <h2 className="font-bold">{ui('Abrir un circuito existente')}</h2>
      <p className="mt-1 text-sm">{ui('CLINICALLY_PENDING · Selección manual según la evaluación clínica y la guía anterior. Estos enlaces no seleccionan un diagnóstico ni indican un tratamiento.')}</p>
      <div className="mt-3 grid gap-3 sm:grid-cols-2">
        {circuitIds.map((id) => {
          const guide = getCanonicalGuide(id);
          return guide ? (
            <Link key={id} to={`${base}/${id}`} className="rounded-lg border border-border p-3 hover:border-primary focus-visible:outline focus-visible:outline-2 focus-visible:outline-primary">
              <span className="block text-sm font-semibold">{guide.title}</span>
              <EvidenceStatusPill status={guide.status} />
            </Link>
          ) : null;
        })}
      </div>
    </nav>
  );
}
