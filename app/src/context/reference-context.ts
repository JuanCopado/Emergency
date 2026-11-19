import { z } from 'zod';
import directory from '../../../clinical/references/international-country-topic-matrix.json';
import { readStorage } from '../lib/storage';

// Context metadata only. This schema cannot select or activate clinical regimens.
export const countries = directory.countries;
export const environments = ['unspecified', 'hospital', 'prehospital', 'transport', 'remote', 'limited-resources'] as const;
export const organizations = ['unspecified', 'synthetic-a', 'synthetic-b'] as const;
export const resourceNames = ['ultrasound', 'laboratory', 'criticalCare'] as const;
export const resourceStates = ['unknown', 'declared-present', 'declared-unavailable'] as const;
const resourceState = z.enum(resourceStates);
export const contextSchema = z.object({
  version: z.literal(1),
  mode: z.enum(['international', 'declared']),
  countryCode: z.string().refine(code => countries.some(country => country.code === code)).nullable(),
  organization: z.enum(organizations),
  environment: z.enum(environments),
  resources: z.object({ ultrasound: resourceState, laboratory: resourceState, criticalCare: resourceState }).strict(),
}).strict().refine(value => value.mode !== 'international' || (
  value.countryCode === null && value.organization === 'unspecified' && value.environment === 'unspecified'
  && Object.values(value.resources).every(status => status === 'unknown')
), { message: 'International reference has no declared operational context' });

export type ReferenceContext = z.infer<typeof contextSchema>;
export const defaultContext: ReferenceContext = {
  version: 1, mode: 'international', countryCode: null, organization: 'unspecified', environment: 'unspecified',
  resources: { ultrasound: 'unknown', laboratory: 'unknown', criticalCare: 'unknown' },
};
export const contextStorageKey = 'emergency.reference-context.v1';

export function loadContext(): { value: ReferenceContext; recovered: boolean } {
  const stored = readStorage(contextStorageKey);
  if (stored === null) return { value: defaultContext, recovered: false };
  try {
    const result = contextSchema.safeParse(JSON.parse(stored));
    if (result.success) return { value: result.data, recovered: false };
  } catch { /* invalid local preference: return to the global reference */ }
  return { value: defaultContext, recovered: true };
}
