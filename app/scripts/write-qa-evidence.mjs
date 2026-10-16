import * as fs from 'node:fs/promises';
import { fileURLToPath } from 'node:url';

// Keep the previous complete checkpoint until the replacement is fully written.
export async function writeEvidence(target, record, operations = fs, pause = ms => new Promise(resolve => setTimeout(resolve, ms))) {
  const path = target instanceof URL ? fileURLToPath(target) : target;
  const temporary = `${path}.pending-${process.pid}`;
  const serialized = JSON.stringify(record, null, 2) + '\n';
  for (let attempt = 0; attempt < 12; attempt++) {
    try {
      await operations.writeFile(temporary, serialized, 'utf8');
      await operations.rename(temporary, path);
      return;
    } catch (error) {
      if (!['EACCES', 'EPERM', 'EBUSY', 'UNKNOWN'].includes(error.code) || attempt === 11) {
        throw new Error(`Evidence replacement failed; preserve ${temporary}: ${error.message}`, {cause:error});
      }
      await pause(100 * (attempt + 1));
    }
  }
}
