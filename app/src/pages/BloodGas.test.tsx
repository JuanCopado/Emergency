import { render, screen, waitFor, cleanup } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import BloodGas from './BloodGas';

const row={name:'pH',raw:'pH 7.28',number:'7.28',unit:'',review:'pending',origin:'unknown',legibility:'unverified',bbox:[10,10,100,30],crop:'',confidence:95,visual_check:'matched'};
const page={fields:[row],preview:'',source_page:1,sample_label:null,width:580,height:220,region:[0,0,580,220],blocked:false,warning:'',method:'text',orientation:0,metadata:[],visual_extras:[]};
let calls:{route:string;body:unknown;headers:Headers;keepalive?:boolean}[];
let metadata:{label:string;value:string;scope?:string;kind?:string;normalized_sample_type?:string|null}[];
let observation:Partial<typeof row>;
beforeEach(()=>{
  calls=[];
  metadata=[];
  observation={};
  vi.stubGlobal('fetch',vi.fn(async (route:string,init?:RequestInit)=>{
    if(route.endsWith('/session')) return {ok:true,json:async()=>({token:'synthetic-session',synthetic_only:true,extraction_available:true,required_platform:'win32'})};
    const body=typeof init?.body==='string'?JSON.parse(init.body):init?.body;
    calls.push({route,body,headers:new Headers(init?.headers),keepalive:init?.keepalive});
    return {ok:true,json:async()=>route.endsWith('/review')?{ph_state:'acidemia',clinical_status:'CLINICALLY_PENDING'}:{ticket:'synthetic-ticket',pages:[{...structuredClone(page),fields:[{...structuredClone(row),...observation}],metadata:structuredClone(metadata)}]}};
  }));
});
afterEach(()=>{cleanup();vi.unstubAllGlobals();});
async function open(sample='desconocida'){
  const user=userEvent.setup();
  render(<MemoryRouter><BloodGas/></MemoryRouter>);
  await user.click(screen.getByLabelText('Solo cargaré datos sintéticos'));
  await user.upload(screen.getByLabelText('Documento sintético'),new File(['synthetic'],'test.pdf',{type:'application/pdf'}));
  await screen.findByLabelText((observation.name||'pH')+' cifra');
  if(sample) await user.selectOptions(screen.getByLabelText('Tipo de muestra'),sample);
  return user;
}
async function confirm(user:ReturnType<typeof userEvent.setup>){
  await user.click(screen.getByLabelText('Cotejo visual de pH'));
  await user.selectOptions(screen.getByLabelText('Revisión de pH'),'confirmed');
  await user.click(screen.getByLabelText(/He revisado el área completa/));
  await user.click(screen.getByLabelText(/Todos los campos aceptados/));
  await user.click(screen.getByLabelText(/Confirmo la revisión médica/));
}
describe('BloodGas medical review',()=>{
  it('requires a manual specimen choice and a reason tied to a conflicting selection',async()=>{
    metadata=[{label:'Muestra',value:'arterial blood',kind:'sample_type',normalized_sample_type:'arterial'}];
    const user=await open('');
    expect(screen.getByLabelText('Tipo de muestra')).toHaveValue('');
    await user.selectOptions(screen.getByLabelText('Tipo de muestra'),'venosa');
    await user.selectOptions(screen.getByLabelText('Revisión de metadato 1'),'confirmed');
    await confirm(user);
    const button=screen.getByRole('button',{name:'Interpretar valores confirmados'});
    expect(button).toBeDisabled();
    await user.click(screen.getByLabelText('Resolver tipo de muestra 1'));
    await user.type(screen.getByLabelText('Motivo de metadato 1'),'Cotejo sintético');
    for(const label of [/He revisado el área completa/,/Todos los campos aceptados/,/Confirmo la revisión médica/])
      await user.click(screen.getByLabelText(label));
    await user.click(button);
    await screen.findByRole('region',{name:'Resultado revisable'});
    expect(calls.find(c=>c.route.endsWith('/review'))?.body).toMatchObject({
      sample:'venosa',metadata:[{resolved_sample_type:'venosa',reason:'Cotejo sintético'}]});
    await user.selectOptions(screen.getByLabelText('Tipo de muestra'),'capilar');
    expect(button).toBeDisabled();
    expect(screen.getByLabelText('Resolver tipo de muestra 1')).not.toBeChecked();
    expect(screen.queryByRole('region',{name:'Resultado revisable'})).toBeNull();
  });
  it.each([
    ['20.9999999999999999','%'],['100.000000000000000001','%'],
    ['0.20999999999999999999','fraction'],['1.00000000000000000001','fraction'],
  ])('blocks a decimal just outside the FiO₂ boundary %s %s',async(number,unit)=>{
    observation={name:'FiO2',number,unit,raw:'FiO2 '+number+' '+unit};
    const user=await open('arterial');
    await user.click(screen.getByLabelText('Cotejo visual de FiO2'));
    await user.selectOptions(screen.getByLabelText('Revisión de FiO2'),'confirmed');
    for(const label of [/He revisado el área completa/,/Todos los campos aceptados/,/Confirmo la revisión médica/])
      await user.click(screen.getByLabelText(label));
    expect(screen.getByRole('button',{name:'Interpretar valores confirmados'})).toBeDisabled();
    expect(screen.getByRole('alert')).toHaveTextContent('21–100 %');
  });
  it('clears the FiO₂ confirmation and reason on each value or unit edit',async()=>{
    observation={name:'FiO2',number:'0.4',unit:'%',raw:'FiO2 0.4 %'};
    const user=await open('arterial');
    expect(screen.getByText(/Fracción según la unidad revisada: 0.004/)).toBeInTheDocument();
    await user.click(screen.getByLabelText('Cotejo visual de FiO2'));
    await user.selectOptions(screen.getByLabelText('Revisión de FiO2'),'confirmed');
    for(const label of [/He revisado el área completa/,/Todos los campos aceptados/,/Confirmo la revisión médica/])
      await user.click(screen.getByLabelText(label));
    expect(screen.getByRole('button',{name:'Interpretar valores confirmados'})).toBeDisabled();
    expect(screen.getByRole('alert')).toHaveTextContent('21–100 %');
    expect(calls.some(c=>c.route.endsWith('/review'))).toBe(false);
    await user.clear(screen.getByLabelText('FiO2 unidad'));
    await user.type(screen.getByLabelText('FiO2 unidad'),'fraction');
    await user.type(screen.getByLabelText('Motivo de la corrección de FiO₂'),'Unidad cotejada');
    await user.click(screen.getByLabelText('Cotejo visual de FiO2'));
    await user.selectOptions(screen.getByLabelText('Revisión de FiO2'),'confirmed');
    for(const label of [/He revisado el área completa/,/Todos los campos aceptados/,/Confirmo la revisión médica/])
      await user.click(screen.getByLabelText(label));
    await user.click(screen.getByRole('button',{name:'Interpretar valores confirmados'}));
    await screen.findByRole('region',{name:'Resultado revisable'});
    expect(calls.find(c=>c.route.endsWith('/review'))?.body).toMatchObject({
      rows:[{fio2_attestation:['0.4','fraction'],correction_reason:'Unidad cotejada'}]});
    await user.type(screen.getByLabelText('FiO2 cifra'),'1');
    expect(screen.getByLabelText('Revisión de FiO2')).toHaveValue('pending');
    expect(screen.getByLabelText('Cotejo visual de FiO2')).not.toBeChecked();
    expect(screen.getByLabelText('Motivo de la corrección de FiO₂')).toHaveValue('');
    expect(screen.queryByRole('region',{name:'Resultado revisable'})).toBeNull();
  });
  it('requires a scope decision for unassigned metadata and clears it after editing',async()=>{
    metadata=[{label:'Sample type',value:'venous',scope:'unassigned'}];
    const user=await open();
    await user.selectOptions(screen.getByLabelText('Revisión de metadato 1'),'confirmed');
    await confirm(user);
    const calculate=screen.getByRole('button',{name:'Interpretar valores confirmados'});
    expect(calculate).toBeDisabled();
    await user.selectOptions(screen.getByLabelText('Ámbito de metadato 1'),'no');
    await user.type(screen.getByLabelText('Motivo de metadato 1'),'Cabecera sin muestra asignada');
    await user.click(screen.getByLabelText(/He revisado el área completa/));
    await user.click(screen.getByLabelText(/Todos los campos aceptados/));
    await user.click(screen.getByLabelText(/Confirmo la revisión médica/));
    expect(calculate).toBeEnabled();
    await user.click(calculate);
    await screen.findByRole('region',{name:'Resultado revisable'});
    expect(calls.find(c=>c.route.endsWith('/review'))?.body).toMatchObject({metadata:[{applies_to_sample:false}]});
    await user.type(screen.getByLabelText('Metadato 1 valor'),'x');
    expect(screen.getByLabelText('Ámbito de metadato 1')).toHaveValue('');
    expect(calculate).toBeDisabled();
  });
  it.each([
    {legibility:'unit_unreadable',visual_check:'ocr_only'},
    {legibility:'unverified',visual_check:'discrepancy'},
    {legibility:'unverified',visual_check:'visual_only'},
  ])('requires explicit transcription of an uncertain observation %j',async(source)=>{
    observation=source;
    const user=await open(); await confirm(user);
    const calculate=screen.getByRole('button',{name:'Interpretar valores confirmados'});
    expect(calculate).toBeDisabled();
    await user.click(screen.getByLabelText('Transcripción manual de pH'));
    await user.selectOptions(screen.getByLabelText('Revisión de pH'),'confirmed');
    await user.click(screen.getByLabelText(/He revisado el área completa/));
    await user.click(screen.getByLabelText(/Todos los campos aceptados/));
    await user.click(screen.getByLabelText(/Confirmo la revisión médica/));
    expect(calculate).toBeEnabled();
    await user.click(calculate);
    await screen.findByRole('region',{name:'Resultado revisable'});
    expect(calls.find(c=>c.route.endsWith('/review'))?.body).toMatchObject({rows:[{transcribed:true}]});
    await user.type(screen.getByLabelText('pH cifra'),'1');
    expect(screen.getByLabelText('Transcripción manual de pH')).not.toBeChecked();
    expect(calculate).toBeDisabled();
  });
  it('requires metadata review and invalidates medical confirmation after metadata correction',async()=>{
    metadata=[{label:'Sample type',value:'venous',kind:'sample_type',normalized_sample_type:'venosa'}];
    const user=await open('venosa');
    await confirm(user);
    const calculate=screen.getByRole('button',{name:'Interpretar valores confirmados'});
    expect(calculate).toBeDisabled();
    await user.selectOptions(screen.getByLabelText('Revisión de metadato 1'),'confirmed');
    await user.click(screen.getByLabelText(/He revisado el área completa/));
    await user.click(screen.getByLabelText(/Todos los campos aceptados/));
    await user.click(screen.getByLabelText(/Confirmo la revisión médica/));
    expect(calculate).toBeEnabled();
    await user.click(calculate);
    await screen.findByRole('region',{name:'Resultado revisable'});
    expect(calls.find(c=>c.route.endsWith('/review'))?.body).toMatchObject({metadata:[{label:'Sample type',value:'venous',review:'confirmed'}]});
    await user.clear(screen.getByLabelText('Metadato 1 valor'));
    await user.type(screen.getByLabelText('Metadato 1 valor'),'arterial');
    expect(calculate).toBeDisabled();
    expect(screen.getByLabelText('Revisión de metadato 1')).toHaveValue('pending');
    expect(screen.queryByRole('region',{name:'Resultado revisable'})).toBeNull();
  });
  it('requires field, area, single sample and medical confirmation, then clears output on edit',async()=>{
    const user=await open();
    const calculate=screen.getByRole('button',{name:'Interpretar valores confirmados'});
    expect(calculate).toBeDisabled();
    await confirm(user); expect(calculate).toBeEnabled();
    await user.click(calculate);
    await screen.findByRole('region',{name:'Resultado revisable'});
    expect(calls.find(c=>c.route.endsWith('/review'))?.body).toMatchObject({medicalConfirmed:true,areaConfirmed:true,oneSample:true});
    expect(calls.find(c=>c.route.endsWith('/review'))?.headers.get('Content-Type')).toBe('application/json');
    expect(calls.find(c=>c.route.endsWith('/extract'))?.headers.get('Content-Type')).toBeNull();
    await user.type(screen.getByLabelText('pH cifra'),'1');
    expect(screen.queryByRole('region',{name:'Resultado revisable'})).toBeNull();
    expect(calculate).toBeDisabled();
    expect(screen.getByLabelText('Revisión de pH')).toHaveValue('pending');
    expect(screen.getByLabelText('Cotejo visual de pH')).not.toBeChecked();
  });
  it('submits original pixel coordinates and restarts review after manual extraction',async()=>{
    const user=await open();
    await user.clear(screen.getByLabelText('Derecha del área'));
    await user.type(screen.getByLabelText('Derecha del área'),'250');
    await user.click(screen.getByRole('button',{name:'Añadir área de muestra'}));
    await user.click(screen.getByRole('button',{name:'Extraer las áreas seleccionadas'}));
    await waitFor(()=>expect(calls.find(c=>c.route.endsWith('/regions'))?.body).toMatchObject({regions:[{page:1,bbox:[0,0,250,220]}]}));
    expect(screen.getByRole('button',{name:'Interpretar valores confirmados'})).toBeDisabled();
    expect(calls.find(c=>c.route.endsWith('/regions'))?.headers.get('Content-Type')).toBe('application/json');
  });
  it('revokes extraction and removes original and fields on reject',async()=>{
    const user=await open();
    await user.click(screen.getByRole('button',{name:'Rechazar y borrar la extracción'}));
    await waitFor(()=>expect(calls.some(c=>c.route.endsWith('/reject'))).toBe(true));
    expect(calls.find(c=>c.route.endsWith('/reject'))?.headers.get('Content-Type')).toBe('application/json');
    expect(screen.queryByLabelText('pH cifra')).toBeNull();
    expect(screen.queryByRole('img',{name:'Original con áreas de muestra'})).toBeNull();
  });
  it('blocks calculation while a selected area has not been extracted',async()=>{
    const user=await open(); await confirm(user);
    await user.clear(screen.getByLabelText('Derecha del área'));
    await user.type(screen.getByLabelText('Derecha del área'),'250');
    await user.click(screen.getByRole('button',{name:'Añadir área de muestra'}));
    await user.click(screen.getByLabelText(/He revisado el área completa/));
    await user.click(screen.getByLabelText(/Todos los campos aceptados/));
    await user.click(screen.getByLabelText(/Confirmo la revisión médica/));
    expect(screen.getByRole('button',{name:'Interpretar valores confirmados'})).toBeDisabled();
  });
  it('revokes an extraction which finishes after the component was unmounted',async()=>{
    const user=userEvent.setup();
    render(<MemoryRouter><BloodGas/></MemoryRouter>);
    await user.click(screen.getByLabelText('Solo cargaré datos sintéticos'));
    let finish:(v:unknown)=>void=()=>{};
    vi.mocked(fetch).mockImplementation(async(route)=>{
      if(String(route).endsWith('/session')) return {ok:true,json:async()=>({token:'session',synthetic_only:true,extraction_available:true,required_platform:'win32'})} as Response;
      if(String(route).endsWith('/extract')) return new Promise(resolve=>{finish=resolve as (v:unknown)=>void;});
      return {ok:true,json:async()=>({rejected:true})} as Response;
    });
    await user.upload(screen.getByLabelText('Documento sintético'),new File(['synthetic'],'test.pdf',{type:'application/pdf'}));
    cleanup();
    finish({ok:true,json:async()=>({ticket:'late-ticket',pages:[structuredClone(page)]})});
    await waitFor(()=>expect(vi.mocked(fetch).mock.calls.some(([url,options])=>String(url).endsWith('/reject') && String(options?.body).includes('late-ticket'))).toBe(true));
  });
  it('sends JSON content type when unmount revokes the active document',async()=>{
    await open();
    cleanup();
    await waitFor(()=>expect(calls.some(c=>c.route.endsWith('/reject'))).toBe(true));
    const rejection=calls.find(c=>c.route.endsWith('/reject'))!;
    expect(rejection.headers.get('Content-Type')).toBe('application/json');
    expect(rejection.headers.get('X-Session')).toBe('synthetic-session');
    expect(rejection.keepalive).toBe(true);
  });
  it.each([false,undefined,'true',1])('does not send a document without a true boolean extraction capability: %s',async(available)=>{
    vi.mocked(fetch).mockResolvedValue({ok:true,json:async()=>({token:'session',synthetic_only:true,
      extraction_available:available,required_platform:'win32'})} as Response);
    const user=userEvent.setup();
    render(<MemoryRouter><BloodGas/></MemoryRouter>);
    await screen.findByRole('alert');
    await user.click(screen.getByLabelText('Solo cargaré datos sintéticos'));
    expect(screen.getByLabelText('Documento sintético')).toBeDisabled();
    expect(vi.mocked(fetch).mock.calls.every(([url])=>String(url).endsWith('/session'))).toBe(true);
    if(available===false) expect(screen.getByRole('alert')).toHaveTextContent('requiere Windows');
  });
  it('does not display a delayed result after unmount',async()=>{
    const user=await open(); await confirm(user);
    let finish:(v:unknown)=>void=()=>{};
    vi.mocked(fetch).mockImplementationOnce(()=>new Promise(resolve=>{finish=resolve as (v:unknown)=>void;}));
    await user.click(screen.getByRole('button',{name:'Interpretar valores confirmados'}));
    cleanup();
    finish({ok:true,json:async()=>({ph_state:'acidemia'})});
    await Promise.resolve();
    expect(screen.queryByRole('region',{name:'Resultado revisable'})).toBeNull();
  });
});
