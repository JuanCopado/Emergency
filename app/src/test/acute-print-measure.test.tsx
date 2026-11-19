import { cleanup, fireEvent, screen } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import AcuteMedications from '../pages/AcuteMedications';
import { renderAt } from './render';
afterEach(() => { cleanup(); vi.restoreAllMocks(); });
it.each([
  {lines:['dose: 1400','dose_unit: mg','duration_min: 40'], grouped:true},
  {lines:['dose: null','dose_unit: null','result_kind: decision_support'], grouped:true},
  {lines:['dose: 1400','notice: unchanged','dose_unit: mg'], grouped:false},
])('preserves report text and confirmation while grouping adjacent dose/unit: $lines',async ({lines,grouped}) => {
  const catalog={source_revision:'synthetic',regimens:[{id:'fixture',label:'Fixture',group:'fixture',group_label:'Test group',drug:'Fixture',route:'IV',dose_unit:'mg',fields:[],source:{body:'Warning',preamble:'Context'},limitations:[]}]};
  const result={dose:1400,dose_unit:'mg',clinical_status:'CLINICALLY_PENDING'};
  const outcome={blocked:false,alerts:[],result,report:{snapshot:result,sections:[['Report',lines],['Warnings',['Keep the warning.']]]}};
  const before=JSON.stringify(outcome);
  vi.spyOn(globalThis,'fetch').mockResolvedValueOnce({ok:true,json:async()=>catalog} as Response).mockResolvedValueOnce({ok:true,json:async()=>outcome} as Response);
  renderAt('/acute-medications',[{path:'/acute-medications',element:<AcuteMedications/>}],'es');
  await screen.findByRole('option',{name:'Test group'});
  fireEvent.change(screen.getByLabelText('Grupo farmacológico'),{target:{value:'fixture'}});
  fireEvent.change(screen.getByLabelText('Indicación y opción'),{target:{value:'fixture'}});
  fireEvent.click(screen.getByRole('button',{name:'Comprobar y calcular'}));
  await screen.findByRole('checkbox');
  expect(screen.getByRole('button',{name:'Imprimir resultado'})).toBeDisabled();
  expect(document.querySelector('.acute-print-sheet')).toBeNull();
  fireEvent.click(screen.getByRole('checkbox'));
  const sheet=document.querySelector('.acute-print-sheet')!;
  expect([...sheet.querySelectorAll('p')].map(p=>p.textContent)).toEqual([...lines,'Keep the warning.']);
  expect(sheet.querySelectorAll('.acute-print-measure')).toHaveLength(grouped?1:0);
  if(grouped) expect([...sheet.querySelectorAll('.acute-print-measure p')].map(p=>p.textContent)).toEqual(lines.slice(0,2));
  expect(JSON.stringify(outcome)).toBe(before);
  expect(screen.getByRole('button',{name:'Imprimir resultado'})).toBeEnabled();
});
