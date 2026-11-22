// Diagnostic only (throwaway branch). Reproduces readBuildIdentity's Git call on Windows and prints
// the real stderr/exit code that the product code discards. No patient data; synthetic repository.
import { spawnSync } from 'node:child_process';
import { existsSync, mkdirSync, mkdtempSync, writeFileSync } from 'node:fs';
import { devNull, tmpdir, userInfo } from 'node:os';
import { join } from 'node:path';

const gitExe = 'C:\\Program Files\\Git\\cmd\\git.exe';
const out = { platform: process.platform, node: process.version, gitExists: existsSync(gitExe), user: userInfo().username };
const run = (cwd, args, env) => {
  const r = spawnSync(gitExe, args, { cwd, encoding: 'utf8', env, windowsHide: true, timeout: 15000 });
  return { status: r.status, signal: r.signal, error: r.error ? String(r.error.message || r.error) : null,
    stdout: (r.stdout || '').trim().slice(0, 300), stderr: (r.stderr || '').trim().slice(0, 600) };
};
out.version = run(process.cwd(), ['--version'], process.env);
const dir = mkdtempSync(join(tmpdir(), 'diag-'));
const root = join(dir, 'repository');
mkdirSync(root);
out.dir = root;
out.init = run(root, ['init', '--quiet'], process.env);
writeFileSync(join(root, 'tracked.txt'), 'original\n');
out.add = run(root, ['add', '.'], process.env);
out.commit = run(root, ['-c', 'user.name=Synthetic Test', '-c', 'user.email=synthetic@example.invalid', '-c', 'commit.gpgsign=false', 'commit', '--quiet', '-m', 'Synthetic fixture'], process.env);
const base = ['--no-pager', '-c', 'core.fsmonitor=false', '-c', 'core.untrackedCache=false', 'rev-parse', '--verify', 'HEAD'];
const productEnv = { PATH: '', GIT_CONFIG_NOSYSTEM: '1', GIT_CONFIG_GLOBAL: devNull, GIT_OPTIONAL_LOCKS: '0', GIT_TERMINAL_PROMPT: '0', SystemRoot: process.env.SystemRoot };
out.variants = {
  inherited_env: run(root, base, process.env),
  product_env_exact_devNull: run(root, base, productEnv),
  global_NUL_upper: run(root, base, { ...productEnv, GIT_CONFIG_GLOBAL: 'NUL' }),
  global_nul_lower: run(root, base, { ...productEnv, GIT_CONFIG_GLOBAL: 'nul' }),
  global_slash_dev_null: run(root, base, { ...productEnv, GIT_CONFIG_GLOBAL: '/dev/null' }),
  global_unset: run(root, base, { ...productEnv, GIT_CONFIG_GLOBAL: undefined }),
  global_empty_file: (() => { const f = join(dir, 'empty.gitconfig'); writeFileSync(f, ''); return run(root, base, { ...productEnv, GIT_CONFIG_GLOBAL: f }); })(),
  // Isolation proof: with a hostile global config present, which variants still ignore it?
  hostile_global_unset_home_cleared: (() => { const f = join(dir, 'hostile.gitconfig'); writeFileSync(f, '[core]\n\tfsmonitor = true\n[user]\n\tname = Hostile\n'); return run(root, ['config', '--show-origin', '--get', 'user.name'], { ...productEnv, GIT_CONFIG_GLOBAL: undefined, USERPROFILE: undefined, HOME: undefined }); })(),
  hostile_global_NUL_config_list: run(root, ['config', '--list', '--show-origin'], { ...productEnv, GIT_CONFIG_GLOBAL: 'NUL' }),
  config_list_global_unset: run(root, ['config', '--list', '--show-origin'], { ...productEnv, GIT_CONFIG_GLOBAL: undefined }),
};
const owner = spawnSync('cmd.exe', ['/c', 'dir', '/q', dir], { encoding: 'utf8' });
out.ownerListing = (owner.stdout || '').split('\n').slice(0, 12).join('\n');
console.log(JSON.stringify(out, null, 2));
