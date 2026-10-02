# v1.36 adult resuscitation consolidation — 2026-10-02

## Scope
Focused reconciliation of `adult-arrhythmias`, `adult-cardiac-arrest` and the shared `arrhythmias-cardiac-arrest` selector.

## Authoritative sources checked
- European Resuscitation Council Guidelines 2025 — Adult Advanced Life Support.
- Resuscitation Council UK 2025 — Adult Advanced Life Support.

## Changes proposed in this branch
- Added explicit synchronized-cardioversion energies for AF, flutter/SVT and VT with pulse.
- Added failed-cardioversion procainamide/amiodarone options from ERC/RCUK 2025.
- Added bradycardia atropine 500 micrograms IV every 3--5 min to 3 mg maximum.
- Added warnings for high-grade AV block with wide QRS and cardiac transplant.
- Added isoprenaline 5 micrograms/min and adrenaline 2--10 micrograms/min second-line bradycardia references.
- Added explicit pacing escalation.
- Added adult-arrest biphasic first-shock energy references.
- Added adrenaline timing and dose for shockable/non-shockable arrest.
- Added amiodarone 300 mg after three shocks and 150 mg after five shocks.
- Added IV-first/IO-after-two-attempts access rule.

## Status
**YELLOW — not promoted to green.**

Reason: human clinical review is still required, as is local reconciliation for Portugal/Azores (defibrillator waveform/settings, resuscitation trolley drug presentations, formulary and local resuscitation protocol).

## Release gate
Do not merge this block as a locally operational protocol until the human/local review above is recorded.
