import generated from '../data/generatedClinicalGuides.json';

export type CanonicalGuide = {
  id: string;
  title: string;
  bundle: string;
  sourcePath: string;
  status: 'green' | 'yellow' | 'red';
  format: 'algorithm' | 'guide' | 'procedure';
  sharedPreamble: string;
  sectionBody: string;
  body: string;
};

// Assemble once for every consumer; generated JSON stores each source part once.
export const canonicalGuides: CanonicalGuide[] = (generated as Omit<CanonicalGuide, 'body'>[]).map((guide) => ({
  ...guide,
  body: [guide.sharedPreamble, guide.sectionBody].filter(Boolean).join('\n\n'),
}));
export const getCanonicalGuide = (id: string) => canonicalGuides.find((guide) => guide.id === id);
