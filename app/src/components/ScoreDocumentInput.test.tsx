import {cleanup,fireEvent,render,screen,waitFor} from '@testing-library/react';
import {afterEach,expect,it,vi} from 'vitest';
import ScoreDocumentInput from './ScoreDocumentInput';
import {readPdf} from '../lib/score-pdf';
import type {Field} from '../lib/score-document';

vi.mock('../lib/score-pdf',()=>({readPdf:vi.fn()}));
afterEach(()=>{cleanup();vi.clearAllMocks();});
const fields:Field[]=[
  {key:'urea',label:'Urea',type:'number',unit:'mmol/L',optional:false},
  {key:'confusion',label:'Confusión',type:'choice',optional:false,options:[{label:'Sí',value:true},{label:'No',value:false}]},
];
function open(){
  const onValues=vi.fn(),onPick=vi.fn();
  const view=render(<ScoreDocumentInput fields={fields} onValues={onValues} onPick={onPick}/>);
  const paste=(value:string)=>fireEvent.change(screen.getByRole('textbox'),{target:{value}});
  const file=(name:string,extra:object={})=>fireEvent.change(screen.getByLabelText('PDF con texto o archivo de texto'),{target:{files:[Object.assign(new File(['a'],name),extra)]}});
  return {onValues,onPick,paste,file,view};
}
it('keeps sample boundaries and requires choosing duplicated values',()=>{
  const {paste,onValues,onPick}=open();
  paste('Muestra: A\nUrea: 5 mmol/L\nMuestra: B\nUrea: 7 mmol/L\nUrea: 9 mmol/L\nConfusión: No');
  expect(onValues).toHaveBeenLastCalledWith({});
  fireEvent.change(screen.getByLabelText(/Seleccione la página/),{target:{value:'0'}});
  expect(onValues).toHaveBeenLastCalledWith({urea:'5'});
  expect(screen.getByText(/Sin identificar/)).toHaveTextContent('Confusión');
  fireEvent.change(screen.getByLabelText(/Seleccione la página/),{target:{value:'1'}});
  expect(onValues).toHaveBeenLastCalledWith({confusion:'false'});
  fireEvent.change(screen.getByLabelText(/Varios resultados/),{target:{value:'1'}});
  expect(onPick).toHaveBeenCalledWith('urea','9');
  paste('Urea: 5 mg/dL');
  expect(screen.getByText(/Sin coincidencias/)).toBeVisible();
});
it('clears previous values on empty, unsupported, oversize and unreadable reports',async()=>{
  const {file,onValues}=open();
  file('test.txt',{text:async()=>'Urea: 6,5 mmol/L'});
  await waitFor(()=>expect(onValues).toHaveBeenLastCalledWith({urea:'6.5'}));
  file('test.bad');
  expect(screen.getByRole('status')).toHaveTextContent('Sin texto');
  vi.mocked(readPdf).mockResolvedValueOnce([]);
  file('blank.pdf');
  await screen.findByText(/Sin texto extraíble/);
  vi.mocked(readPdf).mockRejectedValueOnce(new Error('invalid'));
  file('invalid.pdf');
  await screen.findByText(/No se pudo leer/);
  const input=screen.getByLabelText('PDF con texto o archivo de texto');
  for (const [name,size,notice] of [['large.txt',100001,'100 KB'],['large.pdf',9*1024*1024,'8 MB']] as const){
    fireEvent.change(input,{target:{files:[{name,size}]}});
    expect(screen.getByRole('status')).toHaveTextContent(notice);
  }
  fireEvent.change(input,{target:{files:[]}});
  expect(onValues).toHaveBeenLastCalledWith({});
});
it('discards late extraction after pasting a replacement report',async()=>{
  const {file,paste,onValues}=open();
  let finish!:()=>void;
  vi.mocked(readPdf).mockImplementationOnce(()=>new Promise(resolve=>{finish=()=>resolve([{label:'old',lines:['Urea: 8 mmol/L']}]);}));
  file('old.pdf');
  await waitFor(()=>expect(readPdf).toHaveBeenCalledOnce());
  paste('Urea: 3 mmol/L');
  finish();
  await Promise.resolve();
  expect(onValues).toHaveBeenLastCalledWith({urea:'3'});
});

