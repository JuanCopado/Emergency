import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {withClinicalApp} from './functional-harness.mjs';
const read=p=>JSON.parse(readFileSync(new URL(p,import.meta.url),'utf8'));
const inventory=read('../../clinical/qa/V1.44_PHARMACOLOGY_INVENTORY.json');
const db=read('../src/data/drugs.json');
const pediatric=read('../../clinical/qa/pediatric-outpatient-regression-cases.json').cases;
const extra=[
  {id:'exact-amoxicillin-allergy',regimen_id:'amoxicillin-aom',patient:{age_months:60,actual_weight_kg:20,allergies:['amoxicillin']},expect_stop_code:'ALLERGY_EXACT'},
  {id:'clarithromycin-simvastatin',regimen_id:'clarithromycin-pertussis-ge1mo',patient:{age_months:120,actual_weight_kg:30,active_medications:['simvastatin']},expect_error_contains:'simvastatin'},
  {id:'rizatriptan-other-triptan',regimen_id:'rizatriptan-migraine-rch',patient:{age_months:180,actual_weight_kg:50,secondary_headache_red_flags_excluded:true,active_medications:['sumatriptan']},expect_error_contains:'triptan'},
  {id:'paracetamol-duplicate',regimen_id:'paracetamol-pain-fever-home',patient:{age_months:120,actual_weight_kg:55,ideal_weight_kg:35,home_analgesia_antipyresis_appropriate:true,active_medications:['paracetamol']},selected_duration_days:2,expect:{dose_mg:525},expect_alert_code:'DUPLICATE_INGREDIENT'},
];
const results={adult:[],pediatric:[],clinical_status:'CLINICALLY_PENDING'};
const norm=s=>s.replaceAll('`','').replace(/\s+/g,' ').trim();
const labels={age_months:'Edad (meses)',actual_weight_kg:'Peso real (kg)',ideal_weight_kg:'Peso ideal (kg)',adjusted_weight_kg:'Peso ajustado (kg)',egfr_mL_min:'Filtrado renal (mL/min)',known_renal_impairment:'Insuficiencia renal conocida',known_hepatic_impairment:'Insuficiencia hepática conocida',hepatic_severity:'Gravedad de insuficiencia hepática'};
await withClinicalApp(async({page,base})=>{
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  for(const drug of db.drugs){
    await page.goto(`${base}/drugs/${drug.id}`);
    await page.getByTestId('open-calculator').waitFor();
    const text=norm(await page.locator('body').innerText());
    for(const value of [drug.position,...drug.cautions,...drug.contraindications,drug.dosing.organAdjustment,...db.modules[drug.moduleId].rules,...drug.preparations.flatMap(p=>[p.diluent,p.note])].filter(Boolean))assert.ok(text.includes(norm(value)),`${drug.id}: missing reference text ${value}`);
    assert.equal(await page.locator('#sec-source').isVisible(),true);
    await page.getByTestId('open-calculator').click();await page.getByTestId('calc-drug').waitFor();
    assert.equal(await page.getByTestId('calc-drug').inputValue(),drug.id);
    for(const c of inventory.adult_cases.filter(c=>c.drug===drug.id)){
      await page.locator(`input[name="prep"][value="${c.preparation}"]`).check();
      await page.getByTestId('calc-weight').fill(c.weight===null?'':String(c.weight));
      await page.getByTestId('dose-unit').selectOption(c.unit);
      await page.getByTestId('calc-dose').fill(String(c.dose));
      await page.getByTestId('rate-display').waitFor();
      const shown=Number((await page.getByTestId('rate-display').innerText()).replace(',','.'));
      assert.ok(Math.abs(shown-c.expected_ml_h)<=0.051,`${c.id}: ${shown} != ${c.expected_ml_h}`);
      assert.equal(await page.getByTestId('dose-unit').inputValue(),c.unit);
      const prep=page.locator(`input[value="${c.preparation}"]`).locator('..');
      const concentration=new Intl.NumberFormat('es-ES',{maximumFractionDigits:3}).format(c.concentration.value);
      assert.ok((await prep.innerText()).includes(concentration));
      results.adult.push({id:c.id,drug:drug.id,preparation:c.preparation,expected_ml_h:c.expected_ml_h,displayed_ml_h:shown,status:'PASS',alerts_and_source:'visible',python_crosscheck:'PASS',export:'not available'});
    }
    await page.getByTestId('dose-unit').selectOption(drug.doseUnit);
    await page.getByTestId('calc-dose').fill('-1');assert.equal(await page.getByTestId('rate-display').count(),0);
    await page.getByTestId('calc-dose').fill(String(drug.workedExamples[0].dose));
    if(drug.doseUnit.includes('/kg/')){
      await page.getByTestId('calc-weight').fill('');await page.getByTestId('needs-weight').waitFor();
      assert.equal(await page.getByTestId('rate-display').count(),0);await page.getByTestId('calc-weight').fill('70');
    }
    if(drug.dosing.max?.value!=null){
      await page.getByTestId('calc-dose').fill(String(drug.dosing.max.value*2));await page.getByRole('alert').waitFor();
      assert.ok((await page.getByRole('alert').innerText()).length>0);
    }
    console.log(`PASS drug: ${drug.id}`);
  }
  for(const c of [...pediatric,...extra]){
    await page.goto(`${base}/pediatrics?regimen=${c.regimen_id}`);
    for(const [key,value] of Object.entries(c.patient)){
      if(key==='allergies'||key==='active_medications'){
        await page.getByLabel(key==='allergies'?'Alergias: sustancias o clases, separadas por comas':'Medicamentos actuales, separados por comas',{exact:true}).fill(value.join(','));
        await page.getByLabel(key==='allergies'?'Estado de alergias revisado':'Medicación actual revisada',{exact:false}).check();
      }else{
        const field=key==='hepatic_severity'
          ? page.getByLabel(/^Gravedad de insuficiencia hepática/)
          : page.getByLabel(labels[key]||key.replaceAll('_',' '),{exact:true});
        if(typeof value==='boolean')await field.selectOption(value?'yes':'no');
        else if(key==='hepatic_severity')await field.selectOption(value);
        else await field.fill(String(value));
      }
    }
    if(c.selected_duration_days)await page.getByLabel('Duración elegida',{exact:false}).fill(String(c.selected_duration_days));
    if(c.product){await page.getByLabel('Concentración verificada (mg/mL)',{exact:true}).fill(String(c.product.concentration_mg_per_ml));await page.getByLabel('He verificado la concentración del producto exacto',{exact:true}).check();}
    const pending=page.waitForResponse(r=>r.url().endsWith('/calculate'));await page.getByRole('button',{name:'Comprobar y calcular'}).click();
    const response=await pending;const data=await response.json();
    let exported=false;
    if(c.expect_error_contains || c.expect_stop_code){
      assert.ok(data.blocked||!response.ok(),c.id);
      if(c.expect_error_contains)assert.ok(JSON.stringify(data).toLowerCase().includes(c.expect_error_contains.toLowerCase()),`${c.id}: ${JSON.stringify(data)}`);
      if(c.expect_stop_code)assert.ok(data.safety.alerts.some(a=>a.code===c.expect_stop_code));
      if(data.blocked)await page.getByRole('heading',{name:'Cálculo bloqueado',exact:true}).waitFor();else await page.getByRole('alert').waitFor();
      assert.equal(await page.getByRole('button',{name:'Exportar JSON'}).count(),0);
    }else{
      assert.equal(data.blocked,false,c.id);await page.getByRole('region',{name:'Resultado pediátrico'}).waitFor();
      for(const [path,value] of Object.entries(c.expect)){
        let got=data.result;for(const k of path.split('.'))got=got[k];
        if(typeof value==='number')assert.ok(Math.abs(got-value)<1e-8,`${c.id}: ${path}`);else assert.equal(got,value);
      }
      if(c.expect_alert_code)assert.ok(data.safety.alerts.some(a=>a.code===c.expect_alert_code));
      const download=page.waitForEvent('download');await page.getByRole('button',{name:'Exportar JSON',exact:true}).click();
      const report=JSON.parse(readFileSync(await (await download).path(),'utf8'));
      assert.deepEqual(report.snapshot.result,data.result);assert.deepEqual(report.snapshot.safety,data.safety);exported=true;
    }
    if(data.safety){
      const text=norm(await page.getByRole('region',{name:'Resultado pediátrico'}).innerText());
      for(const a of data.safety.alerts){assert.ok(text.includes(norm(a.message)));if(a.action)assert.ok(text.includes(norm(a.action)));}
    }
    results.pediatric.push({id:c.id,regimen_id:c.regimen_id,status:'PASS',expected_rejection:!!(c.expect_error_contains||c.expect_stop_code),json_export:exported?'PASS':'blocked',safety:'all messages and actions preserved'});
    console.log(`PASS pediatric pharmacology: ${c.id}`);
  }
  assert.deepEqual(errors,[]);
});
writeFileSync(new URL('../../clinical/qa/V1.44_PHARMACOLOGY_BROWSER_RESULTS.json',import.meta.url),JSON.stringify(results,null,2)+'\n');
