// @vitest-environment node
import { execFileSync } from 'node:child_process';
import { chmodSync, existsSync, mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { delimiter, join } from 'node:path';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { gitNullDevice, readBuildIdentity } from './build-identity.mjs';

const git = process.platform === 'win32' ? 'C:\\Program Files\\Git\\cmd\\git.exe' : '/usr/bin/git';
const unknown = {revision:'',dirty:false};
let directory: string;

function run(cwd:string, ...args:string[]) {
  return execFileSync(git, args, {cwd,encoding:'utf8',stdio:['ignore','pipe','ignore']}).trim();
}
function repository(name='repository') {
  const root = join(directory,name);
  mkdirSync(root);
  run(root,'init','--quiet');
  writeFileSync(join(root,'.gitignore'),'ignored.txt\n');
  writeFileSync(join(root,'tracked.txt'),'original\n');
  run(root,'add','.');
  run(root,'-c','user.name=Synthetic Test','-c','user.email=synthetic@example.invalid',
    '-c','commit.gpgsign=false','commit','--quiet','-m','Synthetic fixture');
  return {root,revision:run(root,'rev-parse','HEAD')};
}

beforeEach(() => { directory = mkdtempSync(join(tmpdir(),'emergency-build-identity-')); });
afterEach(() => { vi.unstubAllEnvs(); rmSync(directory,{recursive:true,force:true}); });

it.each(['clean','modified','staged','untracked','ignored'] as const)('reports a real %s repository without changing its source revision', state => {
  const {root,revision} = repository();
  if(state === 'modified' || state === 'staged') writeFileSync(join(root,'tracked.txt'),'changed\n');
  if(state === 'staged') run(root,'add','tracked.txt');
  if(state === 'untracked') writeFileSync(join(root,'new.txt'),'new\n');
  if(state === 'ignored') writeFileSync(join(root,'ignored.txt'),'ignored\n');
  expect(readBuildIdentity(root)).toEqual({revision,dirty:!['clean','ignored'].includes(state)});
});

it('supports packed refs and a linked worktree .git file', () => {
  const {root,revision} = repository();
  run(root,'pack-refs','--all','--prune');
  expect(readBuildIdentity(root)).toEqual({revision,dirty:false});
  const worktree = join(directory,'linked-worktree');
  run(root,'worktree','add','--quiet','--detach',worktree,'HEAD');
  expect(readBuildIdentity(worktree)).toEqual({revision,dirty:false});
  writeFileSync(join(worktree,'tracked.txt'),'changed in worktree\n');
  expect(readBuildIdentity(worktree)).toEqual({revision,dirty:true});
});

it('does not borrow the enclosing repository identity for a source copy without .git', () => {
  const {root} = repository();
  const copy = join(root,'source-copy');
  mkdirSync(copy);
  writeFileSync(join(copy,'source.txt'),'archive without metadata\n');
  expect(readBuildIdentity(copy)).toEqual(unknown);
});

it('reports unknown for absent or corrupt repository metadata', () => {
  expect(readBuildIdentity(directory)).toEqual(unknown);
  writeFileSync(join(directory,'.git'),'invalid metadata\n');
  expect(readBuildIdentity(directory)).toEqual(unknown);
});

it('ignores inherited Git repository redirection', () => {
  const first = repository('first');
  const second = repository('second');
  writeFileSync(join(second.root,'tracked.txt'),'second revision\n');
  run(second.root,'add','tracked.txt');
  run(second.root,'-c','user.name=Synthetic Test','-c','user.email=synthetic@example.invalid',
    '-c','commit.gpgsign=false','commit','--quiet','-m','Second revision');
  vi.stubEnv('GIT_DIR',join(second.root,'.git'));
  vi.stubEnv('GIT_WORK_TREE',second.root);
  expect(readBuildIdentity(first.root)).toEqual({revision:first.revision,dirty:false});
});

it.skipIf(process.platform === 'win32')('never runs a Git namesake placed first in PATH', () => {
  const {root,revision} = repository();
  const shim = join(directory,'path-shim');
  const marker = join(directory,'unexpected-execution.txt');
  mkdirSync(shim);
  const executable = join(shim,'git');
  writeFileSync(executable,`#!${process.execPath}\nrequire('node:fs').writeFileSync(${JSON.stringify(marker)},'executed'); process.stdout.write('a'.repeat(40)+'\\n');\n`);
  chmodSync(executable,0o755);
  vi.stubEnv('PATH',`${shim}${delimiter}${process.env.PATH ?? ''}`);
  expect(readBuildIdentity(root)).toEqual({revision,dirty:false});
  expect(existsSync(marker)).toBe(false);
});

it('does not claim a clean revision when the working-tree check fails', () => {
  const {root} = repository();
  writeFileSync(join(root,'.git','index'),'corrupt synthetic index');
  expect(readBuildIdentity(root)).toEqual(unknown);
});

it.skipIf(process.platform === 'win32')('does not invoke a repository-configured filesystem monitor', () => {
  const {root,revision} = repository();
  const marker = join(directory,'unexpected-monitor.txt');
  const hook = join(directory,'filesystem-monitor');
  writeFileSync(hook,`#!${process.execPath}\nrequire('node:fs').writeFileSync(${JSON.stringify(marker)},'executed'); process.stdout.write('synthetic-token\\0');\n`);
  chmodSync(hook,0o755);
  run(root,'config','core.fsmonitor',hook);
  expect(readBuildIdentity(root)).toEqual({revision,dirty:false});
  expect(existsSync(marker)).toBe(false);
});

it('uses a null device Git for Windows accepts, never the device-namespace path that made it exit 128', () => {
  // Measured on windows-2025 with Git 2.56.1: `\\\\.\\nul` -> "fatal: unable to access ... Invalid argument";
  // `NUL`, `nul`, `/dev/null`, an unset variable and an empty file all work.
  expect(gitNullDevice('win32')).toBe('NUL');
  expect(gitNullDevice('win32')).not.toContain('\\');
  expect(gitNullDevice('linux')).toBe('/dev/null');
  expect(gitNullDevice('darwin')).toBe('/dev/null');
  expect(gitNullDevice()).toBe(process.platform === 'win32' ? 'NUL' : '/dev/null');
});
