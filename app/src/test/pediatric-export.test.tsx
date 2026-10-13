import {act,fireEvent,render,screen,waitFor,cleanup} from '@testing-library/react';
import {afterEach,expect,it,vi} from 'vitest';
import PediatricExport from '../pediatrics/PediatricExport';

afterEach(()=>{cleanup();vi.restoreAllMocks();});
const props={report:{snapshot:{},sections:[['Resultado',['dosis: 5 mg','YELLOW','CLINICALLY_PENDING']]] as [string,string[]][]},calculation:{regimen_id:'example'},result:{dose_mg:5}};
it('surfaces a server rejection without producing a download',async()=>{
  vi.spyOn(globalThis,'fetch').mockResolvedValue({ok:false,json:async()=>({error:'Calculation changed'})} as Response);
  render(<PediatricExport {...props}/>);fireEvent.click(screen.getByText('Exportar JSON'));
  expect(await screen.findByRole('alert')).toHaveTextContent('Calculation changed');
  expect(screen.getByText('Exportar JSON')).toBeEnabled();
});
it('discards a late download after input changes unmount its snapshot',async()=>{
  let finish!:(value:Response)=>void;
  vi.spyOn(globalThis,'fetch').mockImplementation(()=>new Promise(resolve=>{finish=resolve;}));
  const click=vi.spyOn(HTMLAnchorElement.prototype,'click');
  const view=render(<PediatricExport {...props}/>);fireEvent.click(screen.getByText('Exportar JSON'));
  await waitFor(()=>expect(fetch).toHaveBeenCalledOnce());view.unmount();
  await act(async()=>finish({ok:true,json:async()=>({content_base64:'e30=',filename:'pediatric-result.json',mime_type:'application/json'})} as Response));
  expect(click).not.toHaveBeenCalled();expect(document.querySelector('.pediatric-print-sheet')).toBeNull();
});
