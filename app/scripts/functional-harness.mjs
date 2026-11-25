import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright-core';
import { preview } from 'vite';
import { chromiumPath } from './chromium.mjs';
import { clinicalTestSession } from './clinical-test-session.mjs';

export async function withClinicalApp(run, additionalProxy = {}) {
  const session=clinicalTestSession(4180);
  const api=spawn(process.env.CLINICAL_QA_PYTHON||'python',['-B','-u','-c',session.python],{cwd:fileURLToPath(new URL('../../clinical/scripts/',import.meta.url)),env:session.environment,windowsHide:true,stdio:['ignore','pipe','pipe']});
  let server,browser;
  try {
    const port=await new Promise((resolve,reject)=>{
      const timeout=setTimeout(()=>reject(new Error('API startup timeout')),15000);let output='';
      api.stdout.on('data',d=>{output+=d;if(/^\d+\r?\n/.test(output)){clearTimeout(timeout);resolve(Number(output.trim()));}});
      api.stderr.on('data',()=>{});
      api.on('error',e=>{clearTimeout(timeout);reject(e);});
      api.on('exit',c=>{clearTimeout(timeout);reject(new Error(`API exited ${c}`));});
    });
    server=await preview({preview:{host:'127.0.0.1',port:4180,strictPort:true,proxy:{...additionalProxy,'/api':session.proxy(port)}},logLevel:'error'});
    browser=await chromium.launch({executablePath:chromiumPath(),headless:true});
    const context=await browser.newContext({serviceWorkers:'block',acceptDownloads:true,extraHTTPHeaders:session.headers});
    await context.addInitScript(()=>{localStorage.setItem('emergency.lang','es');});
    const page=await context.newPage();page.setDefaultTimeout(15000);
    await run({page,context,base:'http://127.0.0.1:4180',browser});
  } finally {
    await browser?.close();
    if(server)await new Promise(resolve=>server.httpServer.close(resolve));
    api.kill();
  }
}
