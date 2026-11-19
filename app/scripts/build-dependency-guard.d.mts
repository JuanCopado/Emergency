import type { Plugin } from 'vite';

export const auditBuild: boolean;

export function assertDevOnlyMatcher(lock: unknown): number;
export function assertNoMatcherInBundle(bundle: unknown): number;
export function assertNoMatcherInSourceMap(map: unknown): number;
export function productionDependencyGuard(): Plugin;
export function auditServiceWorker(output?: URL): { status: string; scope: string; maps: number; sources: number; advisory_status: string };
