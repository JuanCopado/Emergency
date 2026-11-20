import {expect,it,vi} from 'vitest';
import {getDocument} from 'pdfjs-dist';
import {readPdf} from './score-pdf';

vi.mock('pdfjs-dist',()=>({GlobalWorkerOptions:{},getDocument:vi.fn()}));
const file=Object.assign(new File(['fixture'],'lab.pdf'),{arrayBuffer:async()=>new ArrayBuffer(1)});
function documentWith(items:unknown[],numPages=1){
  const cleanup=vi.fn(),destroy=vi.fn(async()=>undefined);
  const getPage=vi.fn(async()=>({cleanup,getTextContent:async()=>({items})}));
  const task={promise:Promise.resolve({numPages,getPage}),destroy};
  vi.mocked(getDocument).mockReturnValue(task as unknown as ReturnType<typeof getDocument>);
  return {destroy,cleanup,getPage};
}
it('orders fragments within each page and keeps adjacent glyphs together',async()=>{
  const item=(str:string,x:number,y:number,width:number)=>({str,transform:[1,0,0,1,x,y],width});
  const {cleanup,destroy}=documentWith([item('mmol/L',32,100,8),item('Urea:',0,100,15),item('6',22,100,3),item('5',25,100,3),{type:'beginMarkedContent'},item(' ',0,150,4),item('Muestra: A',0,120,12)],2);
  const blocks=await readPdf(file,new AbortController().signal);
  expect(blocks).toHaveLength(2);
  expect(blocks[1]?.label).toContain('Página 2');
  expect(blocks[0]?.lines).toEqual(['Muestra: A','Urea: 65 mmol/L']);
  expect(cleanup).toHaveBeenCalledTimes(2);
  expect(destroy).toHaveBeenCalledOnce();
});
it('releases the worker on excessive page or item counts',async()=>{
  const first=documentWith([],41);
  await expect(readPdf(file,new AbortController().signal)).rejects.toThrow(/40 páginas/);
  expect(first.destroy).toHaveBeenCalledOnce();
  const second=documentWith(Array(50001));
  await expect(readPdf(file,new AbortController().signal)).rejects.toThrow(/extenso/);
  expect(second.destroy).toHaveBeenCalledOnce();
});
it('abandons a cancelled read before loading document bytes into a worker',async()=>{
  const controller=new AbortController();
  controller.abort();
  await expect(readPdf(file,controller.signal)).rejects.toThrow();
});

