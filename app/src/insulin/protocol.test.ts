import { describe, expect, it } from 'vitest';
import { simulate, parseNumber, PROTOCOL, type Values } from './protocol';
const adjust = (glucose:number, extra:Values={})=>simulate('iv-adjust',{glucose,previous:glucose,rate:2,minutes:60,...extra});
describe('Selected local ICU protocol replaces RCCC',()=>{
  it.each([[140,2],[180,2],[181,3],[210,3],[211,4],[240,4],[241,5],[400,5]])('selected row %s', (g,dose)=>{
    const r=adjust(g); expect(r.candidateRate).toBe(dose);expect(r.pumpMlH).toBe(dose);
    expect(r.protocolId).toBe(PROTOCOL.id);expect(r.clinicalUseAllowed).toBe(false);expect(r.source).not.toMatch(/rccc|glytec/);
  });
  it('retains clinical status gate',()=>expect(adjust(220).status).toBe('CLINICALLY_PENDING'));
  it.each([69,53])('rescue at %s is a range, not an invented exact dose',g=>{
    const r=adjust(g);expect(r.candidateRate).toBe(0);expect(r.glucoseGrams).toEqual([10,20]);expect(r.controlMinutes).toEqual([15,15]);expect(r.action).toBe('pause');
  });
  it.each([70,100])('preventive pause %s',g=>{
    const r=adjust(g);expect(r.candidateRate).toBe(0);expect(r.controlMinutes).toEqual([30,60]);expect(r.glucoseGrams).toBeUndefined();
  });
  it.each([101,120,139])('no arbitrary reduction at %s',g=>{
    expect(adjust(g).candidateRate).toBeUndefined();expect(adjust(g).blockedReason).toMatch(/reducción/);
  });
  it('uses a prescribed decrement of 1 or 2 without guessing',()=>{
    expect(adjust(120,{rate:4,reduction:'1'}).candidateRate).toBe(3);
    expect(adjust(120,{rate:4,reduction:'2'}).candidateRate).toBe(2);
    expect(adjust(120,{rate:1,reduction:'2'}).candidateRate).toBeUndefined();
  });
  it('bolus never arises automatically from glucose or a perfusion criterion',()=>{
    expect(simulate('iv-bolus',{glucose:350,indication:'critical-hyperglycemia',bolusUnits:4}).bolusUnits).toBeUndefined();
    expect(simulate('iv-bolus',{glucose:350,indication:'severe-unresponsive',bolusUnits:4,prescribed:'yes'}).bolusMl).toBe(4);
    expect(simulate('iv-bolus',{glucose:350,indication:'dka',bolusUnits:4,prescribed:'yes'}).bolusUnits).toBeUndefined();
  });
  it.each([100.5,139.5,180.5,210.5])('does not round gap %s into a row',g=>{
    expect(adjust(g).blockedReason).toMatch(/intervalo/);expect(adjust(g).candidateRate).toBeUndefined();
  });
  it('shows trend without inventing a fast-fall rule',()=>{
    const r=adjust(220,{previous:320});expect(r.trendMgDlH).toBe(-100);expect(r.notes.join(' ')).toMatch(/tendencia/);
  });
  it('does not extrapolate to nonhourly intervals',()=>{
    const r=adjust(220,{previous:240,minutes:30});expect(r.trendMgDlH).toBe(-40);expect(r.candidateRate).toBeUndefined();
  });
  it('zero infusion does not become an initial dose',()=>expect(adjust(220,{rate:0}).blockedReason).toMatch(/inicial/));
  it.each(['',' ','Infinity','NaN','-1','1e309','100mg','0x10'])('rejects %j',v=>expect(()=>parseNumber(v,'Dato')).toThrow());
  it('accepts comma decimals',()=>{
    expect(parseNumber('0,7','Ritmo')).toBe(0.7);expect(adjust(144,{rate:'0,7'}).candidateRate).toBe(0.7);
  });
  it('does not infer starting dose or bolus',()=>{
    const r=simulate('iv-start',{glucose:250,persistent:'yes'});expect(r.candidateRate).toBeUndefined();expect(r.blockedReason).toMatch(/inicial/);expect(r.notes.join(' ')).toMatch(/bolo/);
  });
  it('requires persistent hyperglycemia',()=>expect(simulate('iv-start',{glucose:250,persistent:'no'}).blockedReason).toMatch(/persistente/));
  it('transition returns a range, no arbitrarily selected percentage',()=>{
    const r=simulate('sc-transition',{meanRate:1,hours:6,stable:'yes',nutrition:'yes'});
    expect(r.dailyIvUnits).toBe(24);expect(r.dailyScRange?.[0]).toBeCloseTo(14.4);expect(r.dailyScRange?.[1]).toBeCloseTo(19.2);
    expect(r.basalRange?.[0]).toBeCloseTo(7.2);expect(r.basalRange?.[1]).toBeCloseTo(9.6);expect(r.blockedReason).toMatch(/porcentaje/);
  });
  it.each([5,9])('transition time window %s fails closed',hours=>expect(simulate('sc-transition',{meanRate:1,hours,stable:'yes',nutrition:'yes'}).dailyScRange).toBeUndefined());
  it('retains local transition criterion <2 UI/h',()=>expect(simulate('sc-transition',{meanRate:2,hours:8,stable:'yes',nutrition:'yes'}).blockedReason).toMatch(/2 UI/));
  it('requires clinical and nutrition stability',()=>{
    expect(simulate('sc-transition',{meanRate:1,hours:6,stable:'no',nutrition:'yes'}).dailyScRange).toBeUndefined();
    expect(simulate('sc-transition',{meanRate:1,hours:6,stable:'yes',nutrition:'no'}).dailyScRange).toBeUndefined();
  });
  it('restart is strictly >140 and only for the documented preventive pause',()=>{
    expect(simulate('iv-restart',{glucose:140,rate:4,pauseReason:'preventive'}).candidateRate).toBeUndefined();
    expect(simulate('iv-restart',{glucose:141,rate:4,pauseReason:'preventive'}).candidateRate).toBe(2);
    expect(simulate('iv-restart',{glucose:150,rate:4,pauseReason:'hypoglycemia'}).candidateRate).toBeUndefined();
  });
  it('hypoglycemia overrides restart',()=>{
    const r=simulate('iv-restart',{glucose:69,rate:4,pauseReason:'preventive'});expect(r.action).toBe('pause');expect(r.candidateRate).toBe(0);
  });
  it('rejects other scope and old SC modes',()=>{
    expect(()=>simulate('iv-adjust',{glucose:220,population:'pediatric'})).toThrow();expect(()=>simulate('sc-start' as never,{})).toThrow();
  });
  it('rejects nonfinite or precision overflow',()=>{
    expect(()=>adjust(220,{rate:Infinity})).toThrow();expect(()=>adjust(220,{rate:Number.MAX_SAFE_INTEGER})).toThrow();
  });
});
