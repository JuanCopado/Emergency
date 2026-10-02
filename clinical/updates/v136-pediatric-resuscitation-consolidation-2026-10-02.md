# v1.36 pediatric resuscitation consolidation — 2026-10-02

## Scope
Focused reconciliation of `pediatric-shock`, `pediatric-arrhythmias` and `pediatric-cardiac-arrest`.

## Authoritative sources checked
- European Resuscitation Council Guidelines 2025 — Paediatric Life Support.
- Resuscitation Council UK 2025 — Paediatric Life Support and Paediatric Arrhythmia Algorithm.

## Key changes
- Shock: 10 mL/kg reassessed boluses; balanced isotonic crystalloid first-line; 40--60 mL/kg may be required in the first hour for selected hypovolaemic/distributive shock; 5 mL/kg cautious bolus in cardiogenic shock when needed; early vasoactive support no later than 30--40 mL/kg; noradrenaline vasopressor, adrenaline inotrope, milrinone inodilator; haemorrhagic shock limits crystalloid and prioritizes blood products.
- Bradycardia: CPR threshold <60/min with poor perfusion despite respiratory support; adrenaline 1--2 micrograms/kg and selected atropine 20 micrograms/kg pathways.
- SVT/VT: adenosine weight-based doses; synchronized cardioversion starting 1 J/kg and escalating to 4 J/kg; expert-guided amiodarone and magnesium details.
- Cardiac arrest: adrenaline 10 micrograms/kg max 1 mg; 4 J/kg defibrillation; refractory escalation up to 8 J/kg after >5 shocks; amiodarone 5 mg/kg after 3rd and 5th shocks with different maxima; monitored/witnessed stacked-shock exception documented.

## Status
**YELLOW — not promoted to green.**

Human pediatric/critical-care review and Portugal/Azores operational reconciliation remain required, including local defibrillator settings, emergency-cart concentrations, drug presentations and pediatric infusion standards.

## QA
A dedicated regression test preserves the 2025 operational invariants. Automated PASS does not constitute clinical validation.
