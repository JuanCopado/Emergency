// Provision tesseract.js, its WASM core and English model locally before use.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const {createWorker, PSM} = require('tesseract.js');

async function main() {
  const model = fs.realpathSync(process.env.BG_OCR_MODEL);
  if (path.basename(model) !== 'eng.traineddata' ||
      crypto.createHash('sha256').update(fs.readFileSync(model)).digest('hex') !==
        '7d4322bd2a7749724879683fc3912cb542f19906c83bcc1a52132556427170b2') {
    throw Error('Modelo local no reconocido');
  }
  const worker = await createWorker('eng', 1, {
    langPath: path.dirname(model), gzip: false, cacheMethod: 'none',
    corePath: path.dirname(require.resolve('tesseract.js-core/package.json')),
    workerPath: require.resolve('tesseract.js/src/worker-script/node/index.js')
  });
  try {
    await worker.setParameters({tessedit_pageseg_mode: PSM.SINGLE_BLOCK});
    const result = await worker.recognize(fs.readFileSync(process.argv[2]), {}, {text: true, tsv: true});
    process.stdout.write(JSON.stringify({text: result.data.text, tsv: result.data.tsv}));
  } finally { await worker.terminate(); }
}
main().catch(()=>{process.exitCode=1});
