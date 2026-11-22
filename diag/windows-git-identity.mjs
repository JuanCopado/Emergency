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
  product_env_exact: run(root, base, productEnv),
  product_env_plus_safe_directory_star: run(root, ['-c', 'safe.directory=*', ...base], productEnv),
  product_env_without_GIT_CONFIG_GLOBAL: run(root, base, { ...productEnv, GIT_CONFIG_GLOBAL: undefined }),
  product_env_without_NOSYSTEM: run(root, base, { ...productEnv, GIT_CONFIG_NOSYSTEM: undefined }),
  product_env_plus_userprofile: run(root, base, { ...productEnv, USERPROFILE: process.env.USERPROFILE, HOMEDRIVE: process.env.HOMEDRIVE, HOMEPATH: process.env.HOMEPATH }),
  product_env_plus_temp: run(root, base, { ...productEnv, TEMP: process.env.TEMP, TMP: process.env.TMP }),
  product_env_plus_username: run(root, base, { ...productEnv, USERNAME: process.env.USERNAME, USERDOMAIN: process.env.USERDOMAIN }),
  product_env_plus_windir: run(root, base, { ...productEnv, windir: process.env.windir, SystemDrive: process.env.SystemDrive, ComSpec: process.env.ComSpec }),
};
const owner = spawnSync('cmd.exe', ['/c', 'dir', '/q', dir], { encoding: 'utf8' });
out.ownerListing = (owner.stdout || '').split('\n').slice(0, 12).join('\n');
console.log(JSON.stringify(out, null, 2));
