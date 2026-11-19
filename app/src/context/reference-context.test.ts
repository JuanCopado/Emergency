import { describe, expect, it } from 'vitest';
import { contextSchema, defaultContext, loadContext, contextStorageKey } from './reference-context';

describe('optional reference context', () => {
  it('keeps the global core available without a country, organization or resources', () => {
    const result = contextSchema.parse(defaultContext);
    expect(result.mode).toBe('international');
    expect(result.countryCode).toBeNull();
    expect(result.organization).toBe('unspecified');
    expect(Object.values(result.resources)).toEqual(['unknown', 'unknown', 'unknown']);
  });
  it('rejects unsupported countries and fields that could carry clinical data', () => {
    expect(contextSchema.safeParse({ ...defaultContext, mode: 'declared', countryCode: 'XX' }).success).toBe(false);
    expect(contextSchema.safeParse({ ...defaultContext, patient: 'private text' }).success).toBe(false);
  });
  it('rejects inconsistent global mode and unknown schema versions', () => {
    expect(contextSchema.safeParse({ ...defaultContext, countryCode: 'PT' }).success).toBe(false);
    expect(contextSchema.safeParse({ ...defaultContext, version: 2 }).success).toBe(false);
  });
  it('rejects a resource claim that has no declared context', () => {
    expect(contextSchema.safeParse({ ...defaultContext, resources: { ...defaultContext.resources, ultrasound: 'declared-present' } }).success).toBe(false);
  });
  it('accepts independent declared contexts without selecting clinical regimens', () => {
    const hospital = contextSchema.parse({ ...defaultContext, mode: 'declared', countryCode: 'GB', organization: 'synthetic-a', environment: 'hospital' });
    const remote = contextSchema.parse({ ...defaultContext, mode: 'declared', countryCode: 'BR', organization: 'synthetic-b', environment: 'remote' });
    expect(hospital.countryCode).toBe('GB');
    expect(remote.countryCode).toBe('BR');
    expect(remote.resources.ultrasound).toBe('unknown');
    expect(hospital).not.toHaveProperty('regimen');
  });
  it('reports malformed stored context and safely resets to the international core', () => {
    localStorage.setItem(contextStorageKey, '{broken');
    expect(loadContext()).toEqual({ value: defaultContext, recovered: true });
    localStorage.removeItem(contextStorageKey);
  });
});
