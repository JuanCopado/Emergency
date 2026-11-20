import { expect,it } from 'vitest';
import { candidates,samples,type Field } from './score-document';

const urea:Field={key:'urea_mmol_L',label:'Urea',type:'number',unit:'mmol/L',minimum:0,optional:false};
const confusion:Field={key:'confusion',label:'Confusión',type:'choice',optional:false,options:[{label:'Sí',value:true},{label:'No',value:false}]};

it('retains original lines and all duplicate values for review',()=>{
  const found=candidates([urea],['Urea: 6,5 mmol/L','Urea: 8 mmol/L']);
  expect(found[urea.key]).toEqual([{value:'6.5',source:'Urea: 6,5 mmol/L'},{value:'8',source:'Urea: 8 mmol/L'}]);
});
it('keeps uncertain units, thresholds, reference ranges and absent observations blank',()=>{
  expect(candidates([urea,confusion],['BUN: 6 mmol/L','Urea: 8 mg/dL','Urea: 8 Mmol/L','Urea: <6 mmol/L','Urea: 1,234 mmol/L','Urea: 3-8 mmol/L','Sin datos de confusión'])).toEqual({});
});
it('keeps identified sample sections separate',()=>{
  const blocks=samples('Muestra: 08:00\nUrea: 6 mmol/L\nMuestra: 11:00\nUrea: 8 mmol/L','Página 1');
  expect(blocks).toHaveLength(2);
  expect(candidates([urea],blocks[1]!.lines)[urea.key]?.[0]?.value).toBe('8');
});

