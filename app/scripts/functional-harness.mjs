import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright-core';
import { preview } from 'vite';
import { chromiumPath } from './chromium.mjs';

export async function withClinicalApp(run) {
  const api=spawn(process.env.CLINICAL_QA_PYTHON||'python',['-B','-u','-c','from http.server import ThreadingHTTPServer; from clinical_note_api import ClinicalNoteHandler; s=ThreadingHTTPServer(("127.0.0.1",0),ClinicalNoteHandler); print(s.server_port,flush=True); s.serve_forever()'],{cwd:fileURLToPath(new URL('../../clinical/scripts/',import.meta.url)),windowsHide:true,stdio:['ignore','pipe','pipe']});
  let server,browser;
  try {
    const port=await new Promise((resolve,reject)=>{
      const timeout=setTimeout(()=>reject(new Error('API startup timeout')),15000);let output='';
      api.stdout.on('data',d=>{output+=d;if(/^\d+\r?\n/.test(output)){clearTimeout(timeout);resolve(Number(output.trim()));}});
      api.stderr.on('data',()=>{});
      api.on('error',e=>{clearTimeout(timeout);reject(e);});
      api.on('exit',c=>{clearTimeout(timeout);reject(new Error(`API exited ${c}`));});
    });
    server=await preview({preview:{host:'127.0.0.1',port:4180,strictPort:true,proxy:{'/api':`http://127.0.0.1:${port}`}},logLevel:'error'});
    browser=await chromium.launch({executablePath:chromiumPath(),headless:true});
    const context=await browser.newContext({serviceWorkers:'block',acceptDownloads:true});
    await context.addInitScript(()=>{localStorage.setItem('emergency.lang','es');});
    const page=await context.newPage();page.setDefaultTimeout(15000);
    await run({page,context,base:'http://127.0.0.1:4180',browser});
  } finally {
    await browser?.close();
    if(server)await new Promise(resolve=>server.httpServer.close(resolve));
    api.kill();
  }
}
