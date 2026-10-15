import { act, cleanup, fireEvent, screen } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import AcuteMedications from '../pages/AcuteMedications';
import { renderAt } from './render';

afterEach(() => { cleanup(); vi.restoreAllMocks(); });
const catalog = {source_revision:'revision-a',regimens:[{id:'fixture',label:'Fixture',group:'fixture',group_label:'Grupo de prueba',drug:'Fixture',route:'IV',dose_unit:'mg',fields:[{key:'weight',label:'Entrada numérica',kind:'number'}],source:{body:'Advertencia canónica íntegra',preamble:'Contexto'},limitations:['Límite de prueba']}]};
const result = {dose:7,dose_unit:'mg',clinical_status:'CLINICALLY_PENDING',monitoring_and_warnings:'Advertencia canónica íntegra',components:{bolus_mg:7,infusion_duration_min:120},correction_ceiling_mmol_l:8};
const outcome = {blocked:false,alerts:[],result,report:{snapshot:result,sections:[['Estado',['CLINICALLY_PENDING']],['Advertencias',['Advertencia canónica íntegra']]]}};
const response = (value:unknown, ok=true) => ({ok,json:async () => value}) as Response;
async function mount() {
  renderAt('/acute-medications',[{path:'/acute-medications',element:<AcuteMedications/>}]);
  await screen.findByRole('option',{name:'Grupo de prueba'});
  fireEvent.change(screen.getByLabelText('Grupo farmacológico'),{target:{value:'fixture'}});
  fireEvent.change(screen.getByLabelText('Indicación y opción'),{target:{value:'fixture'}});
}
const enter = (value:string) => fireEvent.change(screen.getByLabelText('Entrada numérica'),{target:{value}});
const calculate = () => fireEvent.click(screen.getByRole('button',{name:'Comprobar y calcular'}));

it('rejects malformed and nonfinite numbers before HTTP calculation',async () => {
  const fetcher=vi.spyOn(globalThis,'fetch').mockResolvedValue(response(catalog));
  await mount();
  for(const value of ['', 'NaN','Infinity','1e309','70kg']) {
    enter(value); calculate(); await screen.findByRole('alert');
    expect(screen.queryByRole('region',{name:'Resultado farmacológico'})).not.toBeInTheDocument();
  }
  expect(fetcher).toHaveBeenCalledTimes(1);
});

it.each(['edit','group'])('discards a late calculation after %s',async action => {
  let resolve!:(value:Response)=>void;
  const pending=new Promise<Response>(r => {resolve=r;});
  vi.spyOn(globalThis,'fetch').mockResolvedValueOnce(response(catalog)).mockReturnValueOnce(pending);
  await mount(); enter('70'); calculate();
  if(action==='edit') enter('71'); else fireEvent.change(screen.getByLabelText('Grupo farmacológico'),{target:{value:''}});
  await act(async () => {resolve(response(outcome));});
  expect(screen.queryByRole('region',{name:'Resultado farmacológico'})).not.toBeInTheDocument();
});

it('requires confirmation and clears result, exports and print when inputs change',async () => {
  vi.spyOn(globalThis,'fetch').mockResolvedValueOnce(response(catalog)).mockResolvedValueOnce(response(outcome));
  await mount(); enter('70'); calculate();
  await screen.findByRole('region',{name:'Resultado farmacológico'});
  expect(screen.getByRole('button',{name:'Exportar JSON'})).toBeDisabled();
  expect(screen.getByText('Componentes y secuencia (no intercambiables)')).toBeVisible();
  expect(screen.getByText('Límite acumulado de corrección de Na (mmol/L; no objetivo)')).toBeVisible();
  fireEvent.click(screen.getByRole('checkbox'));
  expect(screen.getByRole('button',{name:'Exportar JSON'})).toBeEnabled();
  expect(document.querySelector('.acute-print-sheet')).not.toBeNull();
  enter('71');
  expect(document.querySelector('.acute-print-sheet')).toBeNull();
  expect(screen.queryByRole('button',{name:'Exportar JSON'})).not.toBeInTheDocument();
});

it('cannot export a blocked outcome',async () => {
  vi.spyOn(globalThis,'fetch').mockResolvedValueOnce(response(catalog)).mockResolvedValueOnce(response({blocked:true,alerts:[{code:'review',message:'Revisión requerida'}]}));
  await mount(); enter('70'); calculate();
  await screen.findByText('Cálculo bloqueado');
  expect(screen.getByRole('alert')).toHaveTextContent('Revisión requerida');
  expect(screen.queryByRole('button',{name:'Exportar JSON'})).not.toBeInTheDocument();
});

it('discards an export response after editing inputs',async () => {
  let resolve!:(value:Response)=>void;
  const pending=new Promise<Response>(r => {resolve=r;});
  vi.spyOn(globalThis,'fetch').mockResolvedValueOnce(response(catalog)).mockResolvedValueOnce(response(outcome)).mockReturnValueOnce(pending);
  const anchor=vi.spyOn(HTMLAnchorElement.prototype,'click').mockImplementation(()=>{});
  await mount(); enter('70'); calculate(); await screen.findByRole('checkbox');
  fireEvent.click(screen.getByRole('checkbox')); fireEvent.click(screen.getByRole('button',{name:'Exportar JSON'}));
  enter('71');
  await act(async()=>{resolve(response({filename:'out.json',mime_type:'application/json',content_base64:'e30='}));});
  expect(anchor).not.toHaveBeenCalled();
  expect(screen.queryByRole('region',{name:'Resultado farmacológico'})).not.toBeInTheDocument();
});
