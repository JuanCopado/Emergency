import { execFileSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import { join } from 'node:path';

// Git for Windows 2.56 rejects `os.devNull` (`\\.\nul`) as a config path ("unable to access ... Invalid argument",
// exit 128), which made every Windows build report an unknown revision. `NUL` is its documented null device and
// keeps the global configuration ignored (verified: `git config --list --show-origin` lists only .git/config).
export function gitNullDevice(platform = process.platform) {
  return platform === 'win32' ? 'NUL' : '/dev/null';
}

export function readBuildIdentity(repositoryRoot) {
  try {
    // A source archive must not inherit an enclosing checkout's identity.
    // Native Git also handles packed refs and linked-worktree .git files.
    if (!existsSync(join(repositoryRoot, '.git'))) return {revision:'',dirty:false};
    const options = {
      cwd: repositoryRoot,
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'ignore'],
      shell: false,
      windowsHide: true,
      timeout: 5000,
      maxBuffer: 1024 * 1024,
      // Do not inherit repository redirection, PATH, or global Git config.
      env: {
        PATH: '',
        GIT_CONFIG_NOSYSTEM: '1',
        GIT_CONFIG_GLOBAL: gitNullDevice(),
        GIT_OPTIONAL_LOCKS: '0',
        GIT_TERMINAL_PROMPT: '0',
        ...(process.platform === 'win32' ? {SystemRoot: process.env.SystemRoot} : {}),
      },
    };
    const run = args => {
      const command = ['--no-pager', '-c', 'core.fsmonitor=false', '-c', 'core.untrackedCache=false', ...args];
      // Fixed installation paths only; a missing/nonstandard Git yields unknown.
      return (process.platform === 'win32'
        ? execFileSync('C:\\Program Files\\Git\\cmd\\git.exe', command, options)
        : execFileSync('/usr/bin/git', command, options)).trim();
    };
    const revision = run(['rev-parse', '--verify', 'HEAD']);
    if (!/^(?:[a-f0-9]{40}|[a-f0-9]{64})$/.test(revision)) return {revision:'',dirty:false};
    const dirty = run(['status', '--porcelain=v1', '--untracked-files=normal', '--ignore-submodules=none']) !== '';
    return {revision,dirty};
  } catch { return {revision:'',dirty:false}; }
}
