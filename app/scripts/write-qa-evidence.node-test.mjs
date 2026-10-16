import assert from 'node:assert/strict';
import { test } from 'node:test';
import * as fs from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { writeEvidence } from './write-qa-evidence.mjs';

test('an interrupted replacement preserves the previous valid report and retries transient errors', async () => {
  const dir = await fs.mkdtemp(join(tmpdir(), 'acute-evidence-'));
  const path = join(dir, 'report.json');
  const old = {cases:['old']};
  await fs.writeFile(path, JSON.stringify(old));
  let calls = 0;
  const pauses = [];
  try {
    await writeEvidence(path, {cases:['new'],status:'PASS'}, {
      writeFile:fs.writeFile,
      rename:async (...args) => {
        if (calls++ === 0) {
          assert.deepEqual(JSON.parse(await fs.readFile(path, 'utf8')),old);
          throw Object.assign(new Error('transient Windows file handle'),{code:'UNKNOWN'});
        }
        return fs.rename(...args);
      },
    }, async ms => {pauses.push(ms);});
    assert.equal(calls,2);
    assert.deepEqual(pauses,[100]);
    assert.deepEqual(JSON.parse(await fs.readFile(path,'utf8')),{cases:['new'],status:'PASS'});
    assert.deepEqual(await fs.readdir(dir),['report.json']);
    await assert.rejects(writeEvidence(path,{invalid:1n}),TypeError);
    assert.equal(JSON.parse(await fs.readFile(path,'utf8')).status,'PASS');
  } finally {
    await fs.unlink(path);
    await fs.rmdir(dir);
  }
});

test('persistent replacement failures are bounded and never reported as success', async () => {
  let writes=0;
  await assert.rejects(writeEvidence('unused.json',{}, {
    writeFile:async () => {writes++; throw Object.assign(new Error('locked'),{code:'EACCES'});},
    rename:async () => {assert.fail('must not rename an unwritten file');},
  },async()=>{}),/Evidence replacement failed/);
  assert.equal(writes,12);
});
