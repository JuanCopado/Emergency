import assert from 'node:assert/strict';

export async function checkDocument({page,browser,inputs,expected,button}) {
  const lines = [];
  for (const [key,value] of Object.entries(inputs)) {
    const field = page.locator(`[data-field="${key}"]`);
    const line = await field.evaluate((el,value)=>{
      const caption = el.closest('label').querySelector('.label').textContent;
      if (el.tagName === 'SELECT') return caption+': '+el.selectedOptions[0].textContent;
      const parts = /^(.*?) \(([^()]+)\)$/.exec(caption);
      return parts ? parts[1]+': '+value+' '+parts[2] : caption+': '+value;
    },value);
    lines.push(line);
  }
  const report = await browser.newPage();
  await report.setContent('<meta charset="utf-8"><pre style="font:12px Arial"></pre>');
  await report.locator('pre').evaluate((el,lines)=>{el.textContent=lines.join('\n');},lines);
  const buffer = await report.pdf();
  await report.close();
  let requests = 0;
  const count = req => { if(req.url().endsWith('/clinical-scores/calculate')) requests++; };
  page.on('request',count);
  try {
    await page.getByRole('radio',{name:'Importar PDF'}).check();
    await page.locator('input[type=file]').setInputFiles({name:'sintetico.pdf',mimeType:'application/pdf',buffer});
    await page.getByText('Compruebe la muestra', {exact:false}).waitFor();
    for (const [key,value] of Object.entries(inputs)) {
      const field = page.locator(`[data-field="${key}"]`);
      const wanted = await field.evaluate((el,v)=>el.tagName==='SELECT'?JSON.stringify(v):String(v),value);
      assert.equal(await field.inputValue(),wanted,key);
    }
    assert.equal(requests,0);
    const response = page.waitForResponse(r=>r.url().endsWith('/clinical-scores/calculate'));
    await button.click();
    assert.deepEqual((await (await response).json()).result,expected);
    assert.equal(requests,1);
    await page.getByRole('radio',{name:'Introducir a mano'}).check();
    assert.equal(await page.getByRole('region',{name:'Resultado e interpretación'}).count(),0);
  } finally { page.off('request',count); }
}
