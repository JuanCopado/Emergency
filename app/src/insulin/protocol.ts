/** Owner-selected local protocol, 13/11/2026. ADA 2026 is its guideline framework,
 * not the origin of this dose table. No canonical acute-medication gate is bypassed.
 */
export type Mode = 'iv-start' | 'iv-adjust' | 'iv-restart' | 'sc-transition' | 'iv-bolus';
export type Values = Record<string,string|number>;
export const PROTOCOL = {
  id:'local-icu-insulin-2026-11-13-v2',
  source:'clinical/qa/INSULIN_UCI_OWNER_SELECTED_LOCAL_PROTOCOL.md',
  guideline:'https://doi.org/10.2337/dc26-S016',
  concentration:1, totalUnits:100, finalVolumeMl:100,
} as const;
export const MODES: {id:Mode;title:string}[] = [
  {id:'iv-start',title:'Inicio IV'}, {id:'iv-adjust',title:'Ajuste IV'},
  {id:'iv-restart',title:'Reinicio IV'}, {id:'sc-transition',title:'Transición SC'},
  {id:'iv-bolus',title:'Bolo prescrito'},
];
export type Simulation = {
  status:'CLINICALLY_PENDING';clinicalUseAllowed:false;protocolId:string;source:string;
  action?:'pause'|'maintain'|'increase'|'reduce'|'restart'|'review';
  blockedReason?:string;candidateRate?:number;pumpMlH?:number;trendMgDlH?:number;
  controlMinutes?:[number,number];glucoseGrams?:[number,number];notes:string[];
  dailyIvUnits?:number;dailyScRange?:[number,number];basalRange?:[number,number];
  bolusUnits?:number;bolusMl?:number;
};
function checked(n:number):number {
  if (!Number.isFinite(n) || Math.abs(n)>Number.MAX_SAFE_INTEGER) throw new Error('Resultado fuera del dominio numérico seguro.');
  return n;
}
export function parseNumber(raw:string|number|undefined,label:string,zero=false):number {
  const text=String(raw??'').trim().replace(',','.');const n=Number(text);
  if (!/^(?:\d+(?:\.\d*)?|\.\d+)$/.test(text)||!Number.isFinite(n)||n>Number.MAX_SAFE_INTEGER||(zero?n<0:n<=0)) {
    throw new Error(`${label}: introduce un número finito ${zero?'mayor o igual a cero':'mayor que cero'}.`);
  }
  return n;
}
export function simulate(mode:Mode,v:Values):Simulation {
  if (!MODES.some(m=>m.id===mode)) throw new Error('Recorrido desconocido; los esquemas históricos ya no están disponibles.');
  if ((v.population&&v.population!=='adult')||(v.syndrome&&v.syndrome!=='icu-nonketotic')) throw new Error('Ámbito excluido: pediatría, CAD/HHS e hiperpotasemia requieren su circuito específico.');
  const r:Simulation={status:'CLINICALLY_PENDING',clinicalUseAllowed:false,protocolId:PROTOCOL.id,source:PROTOCOL.source,
    notes:['Protocolo local seleccionado por el propietario. Resultado de prueba, no orden de administración.']};
  const num=(key:string,label:string,zero=false)=>parseNumber(v[key],label,zero);
  const block=(why:string):Simulation=>({...r,action:'review',blockedReason:why});
  const rateResult=(dose:number,action:Simulation['action']):Simulation=>({...r,candidateRate:checked(dose),pumpMlH:checked(dose/PROTOCOL.concentration),action});
  if (mode==='sc-transition') {
    const rate=num('meanRate','Ritmo medio');const hours=num('hours','Horas estables');
    if(hours<6||hours>8) return block('La ventana estable debe ser de 6–8 horas; no se extrapola otra ventana.');
    if(v.stable!=='yes'||v.nutrition!=='yes') return block('Falta confirmar estabilidad clínica/hemodinámica y nutrición estable.');
    if(rate>=2) return block('El criterio local seleccionado exige requerimiento inferior a 2 UI/h.');
    r.dailyIvUnits=checked(rate*24);
    r.dailyScRange=[checked(r.dailyIvUnits*0.6),checked(r.dailyIvUnits*0.8)];
    r.basalRange=[r.dailyScRange[0]*0.5,r.dailyScRange[1]*0.5];
    r.notes.push('El 50% restante corresponde al componente nutricional; no se divide automáticamente en comidas ni correcciones.',
      'Solapamiento seleccionado: al menos 2 horas; la propuesta de hasta 4 horas para NPH requiere elección explícita.');
    return block('Pendiente elegir el porcentaje concreto entre 60% y 80%; se muestra un intervalo aritmético, no una dosis SC final.');
  }
  const g=num('glucose','Glucemia actual');
  if(g<70) {
    r.controlMinutes=[15,15];r.glucoseGrams=[10,20];
    r.notes.push('Suspender y aplicar el protocolo local de hipoglucemia: glucosa IV 10–20 g, controles cada 15 minutos hasta superar 100 mg/dL. El programa no elige una dosis dentro del intervalo.');
    return rateResult(0,'pause');
  }
  if(mode==='iv-bolus') {
    if(v.indication==='dka'||v.indication==='hhs') return block('CAD/EHH excluidos del bolo UCI general: utilizar su circuito específico.');
    if(v.indication!=='critical-hyperglycemia'&&v.indication!=='severe-unresponsive') return block('Falta una indicación médica documentada.');
    if(v.prescribed!=='yes') return block('Requiere prescripción médica explícita del bolo; los criterios de perfusión o una cifra aislada no generan un bolo automático.');
    if(g<=100) return block('Glucemia baja para este recorrido: no se calcula un bolo.');
    r.bolusUnits=num('bolusUnits','Bolo prescrito');r.bolusMl=checked(r.bolusUnits/PROTOCOL.concentration);
    r.notes.push('Sólo convierte una dosis ya prescrita en UI a mL. No propone 0,1 UI/kg ni glucemia/100, y no prescribe velocidad o tiempo de administración.');
    return r;
  }
  if(mode==='iv-start') {
    r.notes.push('El protocolo seleccionado no fija una dosis inicial única ni un bolo automático. No se usa una fila de incremento como dosis de inicio.');
    if(v.persistent!=='yes'||g<180) return block('No está confirmada hiperglucemia persistente ≥180 mg/dL para iniciar este circuito.');
    return block('Ritmo inicial pendiente de prescripción explícita; no se deduce del algoritmo de mantenimiento.');
  }
  if(mode==='iv-restart') {
    const rate=num('rate','Ritmo previo a la pausa');
    if(v.pauseReason!=='preventive') return block('El reinicio tras hipoglucemia u otra interrupción requiere una regla específica; no se extrapola la pausa preventiva.');
    if(g<=140) return block('La regla seleccionada de reinicio preventivo exige glucemia superior a 140 mg/dL.');
    r.controlMinutes=[60,60];r.notes.push('Reinicio al 50% del ritmo previo sólo tras pausa preventiva documentada por glucemia 70–100 mg/dL.');
    return rateResult(rate*0.5,'restart');
  }
  if(g<=100) {
    r.controlMinutes=[30,60];r.notes.push('Pausa preventiva; reevaluar en 30–60 min. El reinicio se evalúa en su recorrido específico.');
    return rateResult(0,'pause');
  }
  const previous=num('previous','Glucemia previa');const rate=num('rate','Ritmo previo',true);const minutes=num('minutes','Minutos entre controles');
  r.trendMgDlH=checked((g-previous)*60/minutes);
  r.notes.push('La tendencia se muestra para revisión; no se inventa un umbral de descenso para modificar las filas del protocolo.');
  if(minutes!==60) return block('El ajuste está definido para controles horarios de 60 minutos; no se extrapola automáticamente a otro intervalo.');
  if(rate===0) return block('Perfusión actualmente parada: requiere el circuito de inicio o reinicio y un ritmo inicial explícito.');
  r.controlMinutes=[60,60];
  if(g>=101&&g<=139) {
    if(v.reduction!=='1'&&v.reduction!=='2'&&v.reduction!==1&&v.reduction!==2) return block('Selecciona la reducción prescrita de 1 o 2 UI/h; el programa no elige según un umbral de descenso no definido.');
    const newRate=rate-Number(v.reduction);
    if(newRate<=0) return block('La reducción agotaría o haría negativo el ritmo; requiere una decisión explícita de pausa. No se inventa un mínimo.');
    return rateResult(newRate,'reduce');
  }
  if(g>=140&&g<=180) return rateResult(rate,'maintain');
  if(g>=181&&g<=210) return rateResult(rate+1,'increase');
  if(g>=211&&g<=240) return rateResult(rate+2,'increase');
  if(g>240) return rateResult(rate+3,'increase');
  return block('Valor entre límites decimales no cubiertos por los intervalos originales; no se redondea a una dosis.');
}
