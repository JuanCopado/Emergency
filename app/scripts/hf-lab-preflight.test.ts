// @vitest-environment node
// R21 · human-factors laboratory preflight: success and failure branches with synthetic inputs only (no build is run).
import { mkdirSync, mkdtempSync, readdirSync, rmSync, writeFileSync, existsSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { PROTOTYPE_TOKENS, buildArm, bundleText, evaluatePreflight, runPreflight, serverHash, sourceFiles } from './hf-lab-preflight.mjs';

let root: string;
beforeEach(() => { root = mkdtempSync(join(tmpdir(), 'hf-preflight-test-')); });
afterEach(() => { rmSync(root, { recursive: true, force: true }); });

function write(relativePath: string, content: string) {
  const full = join(root, relativePath);
  mkdirSync(join(full, '..'), { recursive: true });
  writeFileSync(full, content);
  return full;
}

const ALL_TOKENS = PROTOTYPE_TOKENS.join(' ');
const server = { files: 2, sha256: 'a'.repeat(64) };
const sources = [
  { file: 'src/clinical-note/r51Prototype.ts', text: "const flag = import.meta.env.VITE_R51_PROTOTYPE === '1';" },
  { file: 'src/pages/ClinicalNote.tsx', text: "import ModalityEntry from '../clinical-note/ModalityEntry';" },
  { file: 'src/other.ts', text: 'export const x = 1;' },
];

describe('bundleText and sourceFiles', () => {
  it('joins only the javascript files, recursively', () => {
    write('dist/a.js', 'AAA');
    write('dist/sub/b.js', 'BBB');
    write('dist/c.css', 'CCC');
    const text = bundleText(join(root, 'dist'));
    expect(text).toContain('AAA');
    expect(text).toContain('BBB');
    expect(text).not.toContain('CCC');
  });

  it('lists type-script sources without the tests', () => {
    write('src/a.ts', '');
    write('src/deep/b.tsx', '');
    write('src/a.test.ts', '');
    write('src/data.json', '{}');
    const found = sourceFiles(join(root, 'src')).map((f) => f.replace(root, '').replace(/\\/g, '/')).sort();
    expect(found).toEqual(['/src/a.ts', '/src/deep/b.tsx']);
  });
});

describe('serverHash', () => {
  it('is deterministic, counts only python files and depends on names and contents', () => {
    write('scripts/a.py', 'print(1)');
    write('scripts/sub/b.py', 'print(2)');
    write('scripts/readme.md', 'ignored');
    const first = serverHash(join(root, 'scripts'));
    expect(first.files).toBe(2);
    expect(first.sha256).toMatch(/^[0-9a-f]{64}$/);
    expect(serverHash(join(root, 'scripts'))).toEqual(first);
    write('scripts/readme.md', 'changed but ignored');
    expect(serverHash(join(root, 'scripts'))).toEqual(first);
    write('scripts/a.py', 'print(3)');
    expect(serverHash(join(root, 'scripts')).sha256).not.toBe(first.sha256);
  });

  it('changes when a file is renamed', () => {
    write('s/a.py', 'x');
    const before = serverHash(join(root, 's')).sha256;
    rmSync(join(root, 's', 'a.py'));
    write('s/b.py', 'x');
    expect(serverHash(join(root, 's')).sha256).not.toBe(before);
  });
});

describe('buildArm', () => {
  function fakeExec(captured: { args?: string[]; env?: NodeJS.ProcessEnv; cwd?: string; outDir?: string }) {
    return (_command: string, args: string[], options: { cwd: string; env: NodeJS.ProcessEnv }) => {
      captured.args = args;
      captured.env = options.env;
      captured.cwd = options.cwd;
      captured.outDir = args[args.indexOf('--outDir') + 1];
      writeFileSync(join(captured.outDir, 'bundle.js'), 'BUNDLE-CONTENT');
    };
  }

  it('builds in development mode with the flag on and removes the temporary directory', () => {
    const captured: { args?: string[]; env?: NodeJS.ProcessEnv; cwd?: string; outDir?: string } = {};
    const text = buildArm(true, { appRoot: root, exec: fakeExec(captured), baseEnv: { PATH: 'x' } });
    expect(text).toBe('BUNDLE-CONTENT');
    expect(captured.args).toEqual(expect.arrayContaining(['build', '--mode', 'development', '--emptyOutDir']));
    expect(captured.env?.VITE_R51_PROTOTYPE).toBe('1');
    expect(captured.env?.NODE_ENV).toBe('development');
    expect(captured.cwd).toBe(root);
    expect(existsSync(captured.outDir as string)).toBe(false);
  });

  it('removes the flag for the current-interface arm even if the environment carries it', () => {
    const captured: { args?: string[]; env?: NodeJS.ProcessEnv; cwd?: string; outDir?: string } = {};
    buildArm(false, { appRoot: root, exec: fakeExec(captured), baseEnv: { VITE_R51_PROTOTYPE: '1' } });
    expect(captured.env && 'VITE_R51_PROTOTYPE' in captured.env).toBe(false);
  });

  it('cleans the temporary directory when the build fails', () => {
    let outDir = '';
    expect(() => buildArm(true, { appRoot: root, baseEnv: {}, exec: (_c: string, args: string[]) => { outDir = args[args.indexOf('--outDir') + 1]; throw new Error('build failed'); } })).toThrow('build failed');
    expect(existsSync(outDir)).toBe(false);
  });
});

describe('evaluatePreflight', () => {
  it('passes when arm A is clean, arm B has every token and the wiring is single-sourced', () => {
    const report = evaluatePreflight({ armA: 'clean bundle', armB: ALL_TOKENS, sources, server });
    expect(report.failures).toEqual([]);
    expect(report.arm_a.prototype_tokens_present).toEqual([]);
    expect(report.arm_b.prototype_tokens_present).toEqual(PROTOTYPE_TOKENS);
    expect(report.flag_read_in).toEqual(['src/clinical-note/r51Prototype.ts']);
    expect(report.prototype_mounted_from).toEqual(['src/pages/ClinicalNote.tsx']);
    expect(report.server).toEqual(server);
    expect(report.study_status).toBe('NOT_EXECUTED_PREFLIGHT_ONLY');
    expect(report.confounders_checked).toHaveLength(4);
  });

  it.each(PROTOTYPE_TOKENS)('fails when the current-interface arm contains the token "%s"', (token) => {
    const report = evaluatePreflight({ armA: `x ${token} y`, armB: ALL_TOKENS, sources, server });
    expect(report.failures.some((f) => f.includes('arm A') && f.includes(token))).toBe(true);
    expect(report.arm_a.prototype_tokens_present).toEqual([token]);
  });

  it.each(PROTOTYPE_TOKENS)('fails when the prototype arm lacks the token "%s"', (token) => {
    const report = evaluatePreflight({ armA: '', armB: ALL_TOKENS.replace(token, ''), sources, server });
    expect(report.failures.some((f) => f.includes('arm B') && f.includes(token))).toBe(true);
  });

  it('fails when the flag is read in more than one place or in none', () => {
    const twice = [...sources, { file: 'src/another.ts', text: "import.meta.env.VITE_R51_PROTOTYPE" }];
    expect(evaluatePreflight({ armA: '', armB: ALL_TOKENS, sources: twice, server }).failures.join(' ')).toContain('read in r51Prototype.ts only');
    const none = sources.filter((s) => !s.text.includes('VITE_R51_PROTOTYPE'));
    expect(evaluatePreflight({ armA: '', armB: ALL_TOKENS, sources: none, server }).failures.join(' ')).toContain('found: none');
    const wrongFile = [{ file: 'src/elsewhere.ts', text: 'VITE_R51_PROTOTYPE' }, sources[1]];
    expect(evaluatePreflight({ armA: '', armB: ALL_TOKENS, sources: wrongFile, server }).failures.join(' ')).toContain('src/elsewhere.ts');
  });

  it('fails when the prototype is mounted from another place, from two places or from none', () => {
    const other = [sources[0], { file: 'src/pages/Other.tsx', text: "import ModalityEntry from './ModalityEntry';" }];
    expect(evaluatePreflight({ armA: '', armB: ALL_TOKENS, sources: other, server }).failures.join(' ')).toContain('mounted from ClinicalNote.tsx only');
    const two = [...sources, { file: 'src/pages/Two.tsx', text: "import M from '../clinical-note/ModalityEntry';" }];
    expect(evaluatePreflight({ armA: '', armB: ALL_TOKENS, sources: two, server }).prototype_mounted_from).toHaveLength(2);
    const none = [sources[0]];
    expect(evaluatePreflight({ armA: '', armB: ALL_TOKENS, sources: none, server }).failures.join(' ')).toContain('found: none');
  });
});

describe('runPreflight', () => {
  function layout() {
    write('app/src/clinical-note/r51Prototype.ts', "export const f = import.meta.env.VITE_R51_PROTOTYPE;");
    write('app/src/pages/ClinicalNote.tsx', "import ModalityEntry from '../clinical-note/ModalityEntry';");
    write('app/src/pages/Other.test.ts', "VITE_R51_PROTOTYPE in a test is ignored");
    write('clinical/scripts/server.py', 'print("server")');
    return join(root, 'app');
  }

  it('assembles the report from the sources, the server hash and the two built arms', () => {
    const appRoot = layout();
    const calls: boolean[] = [];
    const report = runPreflight({ appRoot, build: (flag: boolean) => { calls.push(flag); return flag ? ALL_TOKENS : 'clean'; } });
    expect(calls).toEqual([false, true]);
    expect(report.failures).toEqual([]);
    expect(report.server.files).toBe(1);
    expect(report.flag_read_in).toEqual([join('src', 'clinical-note', 'r51Prototype.ts')]);
  });

  it('reports a failure when the current-interface arm is contaminated', () => {
    const appRoot = layout();
    const report = runPreflight({ appRoot, build: () => ALL_TOKENS });
    expect(report.failures.length).toBeGreaterThan(0);
    expect(report.arm_a.prototype_tokens_present).toEqual(PROTOTYPE_TOKENS);
  });

  it('uses the real build function by default (injected exec, nothing is built)', () => {
    const appRoot = layout();
    const report = runPreflight({
      appRoot,
      exec: (_c: string, args: string[]) => { writeFileSync(join(args[args.indexOf('--outDir') + 1], 'x.js'), 'no tokens'); },
    });
    expect(report.failures.join(' ')).toContain('arm B');   // an empty prototype arm cannot pass
    expect(readdirSync(root).length).toBeGreaterThan(0);
  });
});
