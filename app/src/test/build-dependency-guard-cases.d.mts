export function registerTests(test: (name: string, fn: () => void | Promise<void>) => unknown, options?: { integration?: boolean }): void;
