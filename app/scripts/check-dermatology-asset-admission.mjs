import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { checkRepository } from './dermatology-asset-admission.mjs';

try {
  if (process.argv.length !== 2) throw new Error('DERM_UNSUPPORTED_CLI_ARGUMENT');
  const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
  const result = checkRepository(root);
  console.log(JSON.stringify(result));
  process.exitCode = result.status === 'PASS' ? 0 : 1;
} catch {
  console.log(JSON.stringify({ status: 'FAIL', code: 'DERM_ASSET_GUARD_FAILED' }));
  process.exitCode = 1;
}
