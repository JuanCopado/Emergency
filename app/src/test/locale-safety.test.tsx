import { cleanup, fireEvent, screen } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import Calculator from '../pages/Calculator';
import ClinicalNote from '../pages/ClinicalNote';
import AcuteMedications from '../pages/AcuteMedications';
import { renderAt } from './render';
afterEach(() => { cleanup(); vi.restoreAllMocks(); });
it.each([['es','5,3'],['pt','5,3'],['en','5.3'],['zh','5.3']])('P3 %s renders canonical 0.05 dose and 70 kg identically', async (lang, expected) => {
  await renderAt('/calculator?drug=norepinephrine&weight=70&dose=0.05',[{path:'/calculator',element:<Calculator/>}],lang);
  expect(screen.getByTestId('rate-display')).toHaveTextContent(expected);expect(screen.getByTestId('calc-dose')).toHaveValue('0.05');
});
it.each([['en','Privacy STOP'],['es','STOP de privacidad'],['pt','STOP privacidade'],['zh','隐私 STOP']])('P4 %s translates privacy STOP and preserves export blocking', async (lang, stop) => {
  await renderAt('/clinical-note',[{path:'/clinical-note',element:<ClinicalNote/>}],lang);
  fireEvent.change(screen.getByTestId('note-origin'),{target:{value:'Name: Synthetic fixture'}});
  expect(screen.getByRole('alert')).toHaveTextContent('STOP');expect(screen.getByText(stop)).toBeVisible();
  fireEvent.click(screen.getByTestId('note-tab-export'));expect(screen.getByRole('button',{name:'PDF'})).toBeDisabled();
});
it.each([['en','Calculation blocked'],['es','Cálculo bloqueado'],['pt','Cálculo bloqueado'],['zh','计算已阻止']])('P4 %s translates the acute block without changing the canonical alert', async (lang, heading) => {
  const catalog={source_revision:'synthetic',regimens:[{id:'test',group:'test',group_label:'Synthetic',label:'Synthetic',drug:'Synthetic',route:'IV',dose_unit:'mg',fields:[],limitations:[],source:{body:'Canonical source',preamble:'Source'}}]};
  const fetcher=vi.spyOn(globalThis,'fetch').mockResolvedValueOnce({ok:true,json:async()=>catalog} as Response).mockResolvedValueOnce({ok:true,json:async()=>({blocked:true,alerts:[{code:'synthetic',message:'Canonical STOP — do not administer'}]})} as Response);
  await renderAt('/acute',[{path:'/acute',element:<AcuteMedications/>}],lang);await screen.findByText('Synthetic',{selector:'option'});
  fireEvent.change(screen.getByTestId('acute-group'),{target:{value:'test'}});fireEvent.change(screen.getByTestId('acute-regimen'),{target:{value:'test'}});fireEvent.submit(screen.getByTestId('acute-form'));
  expect(await screen.findByRole('heading',{name:heading})).toBeVisible();expect(screen.getByRole('alert')).toHaveTextContent('Canonical STOP — do not administer');expect(screen.queryByTestId('acute-export')).not.toBeInTheDocument();
  expect(JSON.parse(String(fetcher.mock.calls[1]?.[1]?.body))).toEqual({regimen_id:'test',source_revision:'synthetic',inputs:{}});
});
it('does not silently discard an invalid comma age before clinical analysis', async () => {
  const fetcher=vi.spyOn(globalThis,'fetch');
  await renderAt('/clinical-note',[{path:'/clinical-note',element:<ClinicalNote/>}],'en');
  fireEvent.change(screen.getByLabelText('Age'),{target:{value:'1,000'}});
  fireEvent.click(screen.getByTestId('note-tab-diagnostic'));
  expect(screen.getByRole('button',{name:'Update diagnostic support'})).toBeDisabled();
  fireEvent.click(screen.getByTestId('note-tab-export'));
  expect(screen.getByRole('button',{name:'PDF'})).toBeDisabled();expect(fetcher).not.toHaveBeenCalled();
});
it('cannot accept an investigation while an invalid age would be serialized as null', async () => {
  const fetcher=vi.spyOn(globalThis,'fetch');
  await renderAt('/clinical-note',[{path:'/clinical-note',element:<ClinicalNote/>}],'en');
  fireEvent.change(screen.getByLabelText('Age'),{target:{value:'1,000'}});
  fireEvent.click(screen.getByTestId('note-tab-mcdt'));
  fireEvent.change(screen.getByLabelText('Investigation name'),{target:{value:'Synthetic ECG'}});
  fireEvent.click(screen.getByRole('button',{name:'Create review card'}));
  expect(screen.getByRole('button',{name:'Accept'})).toBeDisabled();
  fireEvent.click(screen.getByRole('button',{name:'Accept'}));
  expect(fetcher).not.toHaveBeenCalled();
});
