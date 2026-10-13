import { act, cleanup, fireEvent, screen, waitFor } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import ClinicalScores from '../pages/ClinicalScores';
import { renderAt } from './render';

afterEach(()=>{cleanup();vi.restoreAllMocks();});
const response=(data:unknown,ok=true)=>({ok,json:async()=>data}) as Response;
const catalog={revision:'test-revision',total_scales:135,total_formulas:45,evidence:{status:'yellow'},scores:[{id:'news2',name:'NEWS2',use:'Uso canónico',measures:'Medida canónica',source_url:'https://example.org/source',version:'2017',fields:[{key:'spo2_percent',label:'SpO₂',type:'number',unit:'%',minimum:0,maximum:100,optional:false}]}]};
const output={score_id:'news2',revision:'test-revision',clinical_status:'CLINICALLY_PENDING',result:{total:3,warning:'Canonical warning'}};
const mount=()=>renderAt('/scores',[{path:'/scores',element:<ClinicalScores/>}]);
const enter=(value:string)=>fireEvent.change(screen.getByLabelText(/SpO₂ \(%\)/),{target:{value}});

it('rejects nonfinite, malformed and out-of-range input before network calculation',async()=>{
  const fetcher=vi.spyOn(globalThis,'fetch').mockResolvedValue(response(catalog));await mount();await screen.findByLabelText(/SpO₂ \(%\)/);
  for(const value of ['NaN','Infinity','1e309','true','-1','101','']){
    enter(value);fireEvent.click(screen.getByRole('button',{name:'Calcular'}));
    expect(await screen.findByRole('alert')).toBeVisible();
    expect(screen.queryByRole('region',{name:'Resultado del score'})).toBeNull();
  }
  expect(fetcher).toHaveBeenCalledTimes(1);
});

it('renders the canonical response and clears it and inputs on reset',async()=>{
  vi.spyOn(globalThis,'fetch').mockResolvedValueOnce(response(catalog)).mockResolvedValueOnce(response(output));await mount();await screen.findByLabelText(/SpO₂ \(%\)/);
  enter('90');fireEvent.click(screen.getByRole('button',{name:'Calcular'}));
  expect(await screen.findByRole('region',{name:'Resultado del score'})).toHaveTextContent('Canonical warning');
  fireEvent.click(screen.getByRole('button',{name:'Reiniciar'}));
  expect(screen.getByLabelText(/SpO₂ \(%\)/)).toHaveValue('');expect(screen.queryByRole('region',{name:'Resultado del score'})).toBeNull();
});

it.each(['edit','reset'])('discards a late response after %s',async(action)=>{
  let resolve!:(r:Response)=>void;
  const pending=new Promise<Response>(r=>{resolve=r;});
  const fetcher=vi.spyOn(globalThis,'fetch').mockResolvedValueOnce(response(catalog)).mockReturnValueOnce(pending);
  await mount();await screen.findByLabelText(/SpO₂ \(%\)/);enter('90');fireEvent.click(screen.getByRole('button',{name:'Calcular'}));
  await waitFor(()=>expect(fetcher).toHaveBeenCalledTimes(2));
  if(action==='edit')enter('98');else fireEvent.click(screen.getByRole('button',{name:'Reiniciar'}));
  await act(async()=>{resolve(response(output));await pending;});
  expect(screen.queryByRole('region',{name:'Resultado del score'})).toBeNull();
});

it('shows server failure without retaining a previous result',async()=>{
  vi.spyOn(globalThis,'fetch').mockResolvedValueOnce(response(catalog)).mockResolvedValueOnce(response({error:'Canonical gate'},false));
  await mount();await screen.findByLabelText(/SpO₂ \(%\)/);enter('90');fireEvent.click(screen.getByRole('button',{name:'Calcular'}));
  expect(await screen.findByRole('alert')).toHaveTextContent('Canonical gate');
  expect(screen.queryByRole('region',{name:'Resultado del score'})).toBeNull();
});
