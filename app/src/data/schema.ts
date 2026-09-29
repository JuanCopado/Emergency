import { z } from 'zod';

export const DOSE_UNITS = [
  'mcg/kg/min',
  'mcg/kg/h',
  'mg/kg/h',
  'mcg/min',
  'mg/h',
  'units/min',
  'units/h',
  'ng/kg/min',
] as const;
export const CONCENTRATION_UNITS = ['mcg/mL', 'mg/mL', 'ng/mL', 'units/mL'] as const;
export const AMOUNT_UNITS = ['mcg', 'mg', 'ng', 'units'] as const;
export const BOLUS_UNITS = ['mcg/kg', 'mg/kg'] as const;
export const CATEGORIES = ['vasoactive-inotrope', 'icu-sedation-analgesia'] as const;
export const EVIDENCE_STATUSES = ['green', 'yellow', 'red'] as const;
export const REVIEW_STATUSES = ['draft-pending-clinical-review', 'clinically-reviewed'] as const;

export const doseUnitSchema = z.enum(DOSE_UNITS);
export const concentrationUnitSchema = z.enum(CONCENTRATION_UNITS);
export const amountUnitSchema = z.enum(AMOUNT_UNITS);

const rangeSchema = z.object({ min: z.number().nullable(), max: z.number().nullable(), text: z.string() });

export const preparationSchema = z.object({
  id: z.string().min(1),
  amount: z.object({ value: z.number().positive(), unit: amountUnitSchema }).nullable(),
  finalVolumeMl: z.number().positive().nullable(),
  diluent: z.string().nullable(),
  concentration: z.object({ value: z.number().positive(), unit: concentrationUnitSchema }),
  isDefault: z.boolean(),
  label: z.string(),
  note: z.string().nullable(),
});

export const workedExampleSchema = z.object({
  weightKg: z.number().positive().nullable(),
  dose: z.number().positive(),
  doseUnit: doseUnitSchema,
  preparationId: z.string(),
  expectedMlH: z.number().positive(),
  text: z.string(),
});

export const bolusExampleSchema = z.object({
  weightKg: z.number().positive(),
  dosePerKg: z.number().positive(),
  unit: z.enum(BOLUS_UNITS),
  preparationId: z.string().nullable(),
  expectedAmount: z.number().positive(),
  expectedAmountUnit: amountUnitSchema,
  expectedVolumeMl: z.number().positive().nullable(),
  durationMin: z.number().positive().nullable(),
  text: z.string(),
});

export const drugSchema = z.object({
  id: z.string().regex(/^[a-z0-9-]+$/),
  name: z.string().min(1),
  synonyms: z.array(z.string()),
  category: z.enum(CATEGORIES),
  moduleId: z.string(),
  position: z.string().nullable(),
  doseUnit: doseUnitSchema,
  dosing: z.object({
    start: rangeSchema.nullable(),
    range: rangeSchema.nullable(),
    max: z.object({ value: z.number().nullable(), text: z.string() }).nullable(),
    titration: z
      .object({ stepMin: z.number().nullable(), stepMax: z.number().nullable(), text: z.string() })
      .nullable(),
    alternativeDosing: z.array(z.string()),
    loading: z
      .object({
        doseMin: z.number().positive(),
        doseMax: z.number().positive(),
        unit: z.enum(BOLUS_UNITS),
        durationMin: z.number().positive().nullable(),
        optional: z.boolean(),
        text: z.string(),
      })
      .nullable(),
    weaning: z.string().nullable(),
    organAdjustment: z.string().nullable(),
  }),
  preparations: z.array(preparationSchema).min(1),
  cautions: z.array(z.string()),
  contraindications: z.array(z.string()),
  workedExamples: z.array(workedExampleSchema),
  bolusExamples: z.array(bolusExampleSchema),
  reviewStatus: z.enum(REVIEW_STATUSES),
});

export const moduleSchema = z.object({
  id: z.string(),
  bundle: z.string(),
  title: z.string(),
  scope: z.string(),
  rules: z.array(z.string()),
  evidence: z.object({
    status: z.enum(EVIDENCE_STATUSES),
    priority: z.string(),
    primarySource: z.string(),
    primarySourceUrl: z.string().url().nullable(),
    storedVersion: z.string(),
    lastChecked: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
    note: z.string(),
  }),
});

export const drugDatabaseSchema = z
  .object({
    meta: z.object({
      schemaVersion: z.number().int(),
      contentVersion: z.string(),
      contentLanguage: z.literal('en'),
      extractedFrom: z.string(),
      extractedAt: z.string(),
      reviewStatus: z.enum(REVIEW_STATUSES),
      population: z.literal('adult'),
      note: z.string(),
    }),
    modules: z.record(z.string(), moduleSchema),
    drugs: z.array(drugSchema),
  })
  .superRefine((db, ctx) => {
    const ids = new Set<string>();
    db.drugs.forEach((d, i) => {
      if (ids.has(d.id)) ctx.addIssue({ code: 'custom', message: `duplicate drug id ${d.id}`, path: ['drugs', i] });
      ids.add(d.id);
      if (!db.modules[d.moduleId])
        ctx.addIssue({ code: 'custom', message: `unknown module ${d.moduleId}`, path: ['drugs', i, 'moduleId'] });
      const prepIds = new Set(d.preparations.map((p) => p.id));
      if (d.preparations.filter((p) => p.isDefault).length !== 1)
        ctx.addIssue({ code: 'custom', message: `${d.id}: exactly one default preparation required`, path: ['drugs', i] });
      d.workedExamples.forEach((w, j) => {
        if (!prepIds.has(w.preparationId))
          ctx.addIssue({ code: 'custom', message: `${d.id}: unknown preparation ${w.preparationId}`, path: ['drugs', i, 'workedExamples', j] });
      });
    });
  });

export type DoseUnit = z.infer<typeof doseUnitSchema>;
export type ConcentrationUnit = z.infer<typeof concentrationUnitSchema>;
export type AmountUnit = z.infer<typeof amountUnitSchema>;
export type Preparation = z.infer<typeof preparationSchema>;
export type Drug = z.infer<typeof drugSchema>;
export type ClinicalModule = z.infer<typeof moduleSchema>;
export type DrugDatabase = z.infer<typeof drugDatabaseSchema>;
export type DrugCategory = (typeof CATEGORIES)[number];
export type EvidenceStatus = (typeof EVIDENCE_STATUSES)[number];
