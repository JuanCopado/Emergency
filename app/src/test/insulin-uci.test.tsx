import { fireEvent, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import InsulinUci from '../pages/InsulinUci';
import { renderAt } from './render';
const mount=()=>renderAt('/insulin-uci',[{path:'/insulin-uci',element:<InsulinUci/>}],'es');
const fill=(label:string,value:string)=>fireEvent.change(screen.getByLabelText(label),{target:{value}});
const submit=()=>{fireEvent.click(screen.getByLabelText(/Usaré exclusivamente datos sintéticos/));fireEvent.click(screen.getByRole('button',{name:'Simular cálculo'}));};
function adjustment(){fill('Glucemia actual (mg/dL)','220');fill('Glucemia previa (mg/dL)','220');fill('Ritmo previo (UI/h)','2');fill('Minutos entre controles','60');}
describe('Selected local insulin protocol UI',()=>{
 it('uses the local +2 row, with no active RCCC attribution, and clears edits',async()=>{
  await mount();expect(screen.queryByText(/RCCC/)).not.toBeInTheDocument();
  expect(screen.getByRole('button',{name:'Simular cálculo'})).toBeDisabled();
  adjustment();submit();expect(screen.getByLabelText('Resultado de simulación')).toHaveTextContent('4 UI/h');
  expect(screen.getByLabelText('Resultado de simulación')).toHaveTextContent('NO ADMINISTRABLE');
  fill('Glucemia actual (mg/dL)','230');expect(screen.queryByLabelText('Resultado de simulación')).not.toBeInTheDocument();
 });
 it('requires an explicit 1 or 2 decrement',async()=>{
  await mount();adjustment();fill('Glucemia actual (mg/dL)','120');fill('Glucemia previa (mg/dL)','140');fill('Ritmo previo (UI/h)','4');submit();
  expect(screen.getByLabelText('Resultado de simulación')).toHaveTextContent('Selecciona la reducción');
  expect(screen.queryByTestId('candidate-rate')).not.toBeInTheDocument();
  fill('Reducción prescrita (UI/h)','1');fireEvent.click(screen.getByRole('button',{name:'Simular cálculo'}));
  expect(screen.getByTestId('candidate-rate')).toHaveTextContent('3 UI/h');
 });
 it('replaces old SC distribution by a transition range and resets mode changes',async()=>{
  await mount();adjustment();fireEvent.click(screen.getByRole('button',{name:'Transición SC'}));
  fill('Ritmo medio IV (UI/h)','1');fill('Horas estables evaluadas','6');fill('Estabilidad clínica y hemodinámica','yes');fill('Nutrición estable','yes');submit();
  expect(screen.getByLabelText('Resultado de simulación')).toHaveTextContent('14,4–19,2 UI/día');
  expect(screen.getByLabelText('Resultado de simulación')).toHaveTextContent('porcentaje');
  fireEvent.click(screen.getByRole('button',{name:'Ajuste IV'}));expect(screen.getByLabelText('Glucemia actual (mg/dL)')).toHaveValue('');
  expect(screen.getByRole('button',{name:'Simular cálculo'})).toBeDisabled();
 });
 it('never manufactures a bolus order from a severe glucose value',async()=>{
  await mount();fireEvent.click(screen.getByRole('button',{name:'Bolo prescrito'}));
  fill('Glucemia actual (mg/dL)','350');fill('Indicación médica del bolo','severe-unresponsive');fill('Dosis de bolo prescrita (UI)','4');submit();
  expect(screen.getByLabelText('Resultado de simulación')).toHaveTextContent('prescripción médica explícita');
  expect(screen.queryByTestId('bolus-volume')).not.toBeInTheDocument();
  fill('Existe prescripción médica explícita','yes');fireEvent.click(screen.getByRole('button',{name:'Simular cálculo'}));
  expect(screen.getByTestId('bolus-volume')).toHaveTextContent('4 UI = 4 mL');
 });
 it('clears the result, form and consent on reset',async()=>{
  await mount();adjustment();submit();fireEvent.click(screen.getByRole('button',{name:'Borrar datos'}));
  expect(screen.queryByLabelText('Resultado de simulación')).not.toBeInTheDocument();
  expect(screen.getByLabelText('Ritmo previo (UI/h)')).toHaveValue('');
  expect(screen.getByRole('button',{name:'Simular cálculo'})).toBeDisabled();
 });
});
