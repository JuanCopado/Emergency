export type GuideStatus = 'green' | 'yellow' | 'red';

export type GuideStep = {
  title: string;
  body: string;
  tone?: 'default' | 'decision' | 'danger' | 'success';
};

export type ClinicalGuide = {
  id: string;
  title: string;
  subtitle: string;
  sourceModule: string;
  sourcePath: string;
  status: GuideStatus;
  reviewedAt: string;
  references: string[];
  steps: GuideStep[];
  stopPoints: string[];
  confirmation: string[];
};
