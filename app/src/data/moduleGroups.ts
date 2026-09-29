/**
 * Module groups of the v1.35 skill package (references/module-index.md, 106 module IDs).
 * Sprint 1 ships only the two adult infusion modules; the rest are shown as "coming soon".
 */
export interface ModuleGroup {
  id: string;
  /** i18n key suffix under `groups.` */
  key: string;
  bundle: string;
  moduleCount: number;
  status: 'available' | 'coming-soon';
  /** Drug category filter for available groups. */
  category?: 'vasoactive-inotrope' | 'icu-sedation-analgesia';
  moduleId?: string;
}

export const AVAILABLE_GROUPS: ModuleGroup[] = [
  { id: 'vasoactive', key: 'vasoactive', bundle: 'modules/cardiovascular.md', moduleCount: 1, status: 'available', category: 'vasoactive-inotrope', moduleId: 'vasoactive-inotrope-infusions' },
  { id: 'sedation', key: 'sedation', bundle: 'modules/procedures-pharmacology.md', moduleCount: 1, status: 'available', category: 'icu-sedation-analgesia', moduleId: 'icu-sedation-analgesia-infusions' },
];

export const COMING_SOON_GROUPS: ModuleGroup[] = [
  { id: 'cardiovascular', key: 'cardiovascular', bundle: 'modules/cardiovascular.md', moduleCount: 17, status: 'coming-soon' },
  { id: 'infection-respiratory', key: 'infectionRespiratory', bundle: 'modules/infection-respiratory.md', moduleCount: 13, status: 'coming-soon' },
  { id: 'neurologic', key: 'neurologic', bundle: 'modules/neurologic.md', moduleCount: 9, status: 'coming-soon' },
  { id: 'renal-metabolic', key: 'renalMetabolic', bundle: 'modules/renal-metabolic.md', moduleCount: 16, status: 'coming-soon' },
  { id: 'trauma-surgical', key: 'traumaSurgical', bundle: 'modules/trauma-surgical.md', moduleCount: 11, status: 'coming-soon' },
  { id: 'special-populations', key: 'specialPopulations', bundle: 'modules/special-populations.md', moduleCount: 15, status: 'coming-soon' },
  { id: 'procedures-pharmacology', key: 'proceduresPharmacology', bundle: 'modules/procedures-pharmacology.md', moduleCount: 6, status: 'coming-soon' },
  { id: 'disposition-crosscutting', key: 'dispositionCrosscutting', bundle: 'modules/disposition-crosscutting.md', moduleCount: 7, status: 'coming-soon' },
  { id: 'clinical-images', key: 'clinicalImages', bundle: 'modules/clinical-images.md + modules/image-modalities.md', moduleCount: 10, status: 'coming-soon' },
];
