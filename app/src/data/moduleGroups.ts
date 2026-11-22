import guideGroups from './generatedGuideGroups.json';

// Adult infusion tools and current reference groups have distinct capabilities.
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

const referenceKeys: Record<string,string> = {
  cardiovascular:'cardiovascular', 'infection-respiratory':'infectionRespiratory', neurologic:'neurologic',
  'renal-metabolic':'renalMetabolic', 'trauma-surgical':'traumaSurgical', 'special-populations':'specialPopulations',
  'procedures-pharmacology':'proceduresPharmacology', 'disposition-crosscutting':'dispositionCrosscutting',
  'clinical-images':'imageFramework', 'image-modalities':'imageModalities',
  'clinical-scores-calculators':'clinicalScores', 'documentation-governance':'documentationGovernance',
};
export const REFERENCE_GROUPS = guideGroups.map(group => ({...group,key:referenceKeys[group.id] ?? group.id}));
