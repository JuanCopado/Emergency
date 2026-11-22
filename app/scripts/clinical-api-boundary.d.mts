import type { Plugin, ProxyOptions } from 'vite';

export function clinicalApiBoundary(sessionToken?: string): Plugin;
export function clinicalApiProxy(target?: string, sessionToken?: string): ProxyOptions;
