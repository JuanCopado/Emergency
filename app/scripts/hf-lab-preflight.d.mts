export const PROTOTYPE_TOKENS: string[];
export function bundleText(directory: string): string;
export function buildArm(prototypeFlag: boolean, options?: {
  appRoot?: string;
  exec?: (command: string, args: string[], options: { cwd: string; env: NodeJS.ProcessEnv; stdio: string }) => unknown;
  baseEnv?: NodeJS.ProcessEnv;
}): string;
export function sourceFiles(directory: string): string[];
export function serverHash(root: string): { files: number; sha256: string };
export function evaluatePreflight(input: {
  armA: string;
  armB: string;
  sources: { file: string; text: string }[];
  server: { files: number; sha256: string };
}): {
  arm_a: { prototype_tokens_present: string[] };
  arm_b: { prototype_tokens_present: string[] };
  flag_read_in: string[];
  prototype_mounted_from: string[];
  server: { files: number; sha256: string };
  confounders_checked: string[];
  study_status: string;
  failures: string[];
};
export function runPreflight(options?: {
  appRoot?: string;
  build?: (flag: boolean, options?: unknown) => string;
  exec?: unknown;
}): ReturnType<typeof evaluatePreflight>;
