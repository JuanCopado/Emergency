import { cleanup, fireEvent, screen } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import AcuteMedications from '../pages/AcuteMedications';
import Calculator from '../pages/Calculator';
import { renderAt } from './render';

afterEach(() => { cleanup(); vi.restoreAllMocks(); });
const regimens = ['insulin-dka','insulin-mixed','insulin-dextrose','insulin-hhs','status-lorazepam','status-diazepam'];
const response = (value: unknown) => ({ok:true,json:async () => value}) as Response;
const result = {blocked:false,alerts:[],result:{dose:1,dose_unit:'mg'},report:{snapshot:{},sections:[]}};
function makeCatalog(id: string, field: Record<string,unknown> = {key:'weight_kg',label:'Peso verificado (kg)',kind:'number',minimum:1,maximum:180}) {
  return {source_revision:'weight-fixture',regimens:[{id,label:id,group:'fixture',group_label:'Grupo sintético',
    drug:'Fixture',route:'IV',dose_unit:'mg',fields:[field],source:{body:'Fuente sintética',preamble:'Contexto'},limitations:[]}]};
}
async function mountAcute(id: string) {
  renderAt('/acute-medications',[{path:'/acute-medications',element:<AcuteMedications/>}], 'es');
  await screen.findByRole('option',{name:'Grupo sintético'});
  fireEvent.change(screen.getByLabelText('Grupo farmacológico'),{target:{value:'fixture'}});
  fireEvent.change(screen.getByLabelText('Indicación y opción'),{target:{value:id}});
}
const calculate = () => fireEvent.click(screen.getByRole('button',{name:'Comprobar y calcular'}));

it.each(regimens)('%s rejects absent/outside literal weight and clears earlier exports', async id => {
  const fetcher=vi.spyOn(globalThis,'fetch').mockResolvedValueOnce(response(makeCatalog(id))).mockResolvedValue(response(result));
  await mountAcute(id);
  const weight=screen.getByLabelText('Peso verificado (kg)');
  for (const value of ['', '0', '5e-324', '0.99999999999999999999', '180.000000000000000001', '181']) {
    fireEvent.change(weight,{target:{value}}); calculate();
    await screen.findByRole('alert');
    expect(screen.queryByRole('region',{name:'Resultado farmacológico'})).not.toBeInTheDocument();
  }
  expect(fetcher).toHaveBeenCalledTimes(1);
  for (const value of ['1', '180']) {
    fireEvent.change(weight,{target:{value}}); calculate();
    await screen.findByRole('checkbox');
    expect(JSON.parse(String(fetcher.mock.calls.at(-1)?.[1]?.body)).inputs.weight_kg).toBe(Number(value));
  }
  fireEvent.click(screen.getByRole('checkbox'));
  expect(screen.getByRole('button',{name:'Exportar JSON'})).toBeEnabled();
  fireEvent.change(weight,{target:{value:'180.000000000000000001'}});
  expect(screen.queryByRole('button',{name:'Exportar JSON'})).not.toBeInTheDocument();
});

it('retains the stricter midazolam weight condition', async () => {
  const fetcher=vi.spyOn(globalThis,'fetch').mockResolvedValueOnce(response(makeCatalog('status-midazolam',
    {key:'weight_kg',label:'Peso verificado (kg)',kind:'number',minimum:1,maximum:180,exclusive_minimum:40}))).mockResolvedValue(response(result));
  await mountAcute('status-midazolam');
  fireEvent.change(screen.getByLabelText('Peso verificado (kg)'),{target:{value:'40'}}); calculate();
  expect(await screen.findByRole('alert')).toHaveTextContent('límites específicos');
  expect(fetcher).toHaveBeenCalledTimes(1);
  fireEvent.change(screen.getByLabelText('Peso verificado (kg)'),{target:{value:'41'}}); calculate();
  await screen.findByRole('checkbox');
  expect(fetcher).toHaveBeenCalledTimes(2);
});

it('does not apply kg limits to anticoagulant units', async () => {
  const fetcher=vi.spyOn(globalThis,'fetch').mockResolvedValueOnce(response(makeCatalog('reversal-ufh',
    {key:'recent_ufh_units',label:'UFH reciente (U)',kind:'number'}))).mockResolvedValue(response(result));
  await mountAcute('reversal-ufh');
  fireEvent.change(screen.getByLabelText('UFH reciente (U)'),{target:{value:'0.5'}}); calculate();
  await screen.findByRole('checkbox');
  expect(JSON.parse(String(fetcher.mock.calls[1]?.[1]?.body)).inputs).toEqual({recent_ufh_units:.5});
});

it.each(['0.99999999999999999999','180.000000000000000001'])('Calculator blocks out-of-range URL weight %s before rounding', async weight => {
  renderAt(`/calculator?drug=norepinephrine&weight=${weight}&dose=0.05`,[{path:'/calculator',element:<Calculator/>}]);
  expect(await screen.findByText('Enter a weight between 1 and 180 kg, inclusive.')).toBeVisible();
  expect(screen.queryByTestId('rate-display')).not.toBeInTheDocument();
});

it.each(['1','180'])('Calculator retains an exact permitted weight %s', async weight => {
  renderAt(`/calculator?drug=norepinephrine&weight=${weight}&dose=0.05`,[{path:'/calculator',element:<Calculator/>}]);
  expect(await screen.findByTestId('rate-display')).toBeVisible();
  expect(screen.getByTestId('calc-weight')).toHaveValue(weight);
});
