import generated from '../data/generatedClinicalGuides.json';

export type CanonicalGuide = {
  id: string;
  title: string;
  bundle: string;
  sourcePath: string;
  status: 'green' | 'yellow' | 'red';
  format: 'algorithm' | 'guide' | 'procedure';
  body: string;
};

export const canonicalGuides = generated as CanonicalGuide[];
export const getCanonicalGuide = (id: string) => canonicalGuides.find((guide) => guide.id === id);
