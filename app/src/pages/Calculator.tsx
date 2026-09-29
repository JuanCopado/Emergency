import { useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useSearchParams } from 'react-router-dom';
import { ClinicalText } from '../components/ClinicalText';
import { DraftBanner } from '../components/DraftBanner';
import { Icon } from '../components/Icon';
import { NumberField } from '../components/NumberField';
import { defaultPreparation, drugs, getDrug } from '../data';
import { DOSE_UNITS, type AmountUnit, type DoseUnit, type Drug, type Preparation } from '../data/schema';
import { parseDecimal } from '../lib/format';
import {
  buildTitrationTable,
  computeBolus,
  concentrationFromAmount,
  convertDose,
  doseToRate,
  isWeightBasedUnit,
  rateToDose,
  unitsCompatible,
  type CalcStep,
  type Concentration,
} from '../lib/infusion';
import { titrationDefaults } from '../lib/titration';
import { useFormat } from '../lib/useFormat';

type Direction = 'forward' | 'reverse';
const CUSTOM = 'custom';

function compatibleDoseUnits(drug: Drug, conc: Concentration): DoseUnit[] {
  const perKg = isWeightBasedUnit(drug.doseUnit);
  return DOSE_UNITS.filter((u) => unitsCompatible(u, conc.unit) && isWeightBasedUnit(u) === perKg);
}

function initialDose(drug: Drug): string {
  const v = drug.dosing.start?.min ?? drug.dosing.range?.min ?? drug.workedExamples[0]?.dose;
  return v !== undefined && v !== null ? String(v) : '';
}

export default function Calculator() {
  const { t } = useTranslation();
  const f = useFormat();
  const [params, setParams] = useSearchParams();

  const initialDrug = getDrug(params.get('drug')) ?? getDrug('norepinephrine') ?? (drugs[0] as Drug);
  const [drugId, setDrugId] = useState(initialDrug.id);
  const drug = getDrug(drugId) ?? initialDrug;

  const initialPrep = drug.preparations.find((p) => p.id === params.get('prep'))?.id ?? defaultPreparation(drug).id;
  const [prepId, setPrepId] = useState<string>(initialPrep);
  const [customAmount, setCustomAmount] = useState('');
  const [customAmountUnit, setCustomAmountUnit] = useState<AmountUnit>(drug.doseUnit.startsWith('units') ? 'units' : 'mg');
  const [customVolume, setCustomVolume] = useState('');
  const [weight, setWeight] = useState(params.get('weight') ?? '');
  const [direction, setDirection] = useState<Direction>('forward');
  const [dose, setDose] = useState(params.get('dose') ?? initialDose(drug));
  const [doseUnit, setDoseUnit] = useState<DoseUnit>(drug.doseUnit);
  const [rate, setRate] = useState('');

  const defaults = titrationDefaults(drug);
  const [tFrom, setTFrom] = useState(String(defaults.from));
  const [tTo, setTTo] = useState(String(defaults.to));
  const [tStep, setTStep] = useState(String(defaults.step));

  // Keep a shareable URL (drug, prep, weight, dose) in sync without adding history entries.
  useEffect(() => {
    const next = new URLSearchParams();
    next.set('drug', drugId);
    if (prepId !== CUSTOM) next.set('prep', prepId);
    if (weight) next.set('weight', weight);
    if (dose && direction === 'forward') next.set('dose', dose);
    if (next.toString() !== params.toString()) setParams(next, { replace: true });
  }, [drugId, prepId, weight, dose, direction, params, setParams]);

  const selectDrug = (id: string) => {
    const d = getDrug(id);
    if (!d) return;
    setDrugId(d.id);
    setPrepId(defaultPreparation(d).id);
    setDoseUnit(d.doseUnit);
    setDose(initialDose(d));
    setRate('');
    setCustomAmountUnit(d.doseUnit.startsWith('units') ? 'units' : 'mg');
    const td = titrationDefaults(d);
    setTFrom(String(td.from));
    setTTo(String(td.to));
    setTStep(String(td.step));
  };

  const preparation: Preparation | null = drug.preparations.find((p) => p.id === prepId) ?? null;

  // Resolve concentration (standard or custom amount/volume)
  const concResult = useMemo((): { conc: Concentration | null; error: string | null } => {
    if (preparation) return { conc: preparation.concentration, error: null };
    const a = parseDecimal(customAmount);
    const v = parseDecimal(customVolume);
    if (a === null || v === null) return { conc: null, error: null };
    try {
      return { conc: concentrationFromAmount(a, customAmountUnit, v), error: null };
    } catch {
      return { conc: null, error: t('calc.errors.concentration') };
    }
  }, [preparation, customAmount, customVolume, customAmountUnit, t]);
  const conc = concResult.conc;

  const unitOptions = conc ? compatibleDoseUnits(drug, conc) : [drug.doseUnit];
  const effectiveDoseUnit = unitOptions.includes(doseUnit) ? doseUnit : drug.doseUnit;

  const weightNum = parseDecimal(weight);
  const weightError = weight && (weightNum === null || weightNum <= 0 || weightNum > 400) ? t('calc.errors.weight') : null;
  const weightKg = weightNum !== null && !weightError ? weightNum : null;
  const needsWeight = isWeightBasedUnit(effectiveDoseUnit);

  const doseNum = parseDecimal(dose);
  const doseError = dose && (doseNum === null || doseNum <= 0) ? t('calc.errors.dose') : null;
  const rateNum = parseDecimal(rate);
  const rateError = rate && (rateNum === null || rateNum <= 0) ? t('calc.errors.rate') : null;

  const forward = useMemo(() => {
    if (direction !== 'forward' || !conc || doseNum === null || doseError) return null;
    try {
      return doseToRate({ dose: doseNum, doseUnit: effectiveDoseUnit, concentration: conc, weightKg });
    } catch {
      return null;
    }
  }, [direction, conc, doseNum, doseError, effectiveDoseUnit, weightKg]);

  const reverse = useMemo(() => {
    if (direction !== 'reverse' || !conc || rateNum === null || rateError) return null;
    try {
      return rateToDose({ mlPerHour: rateNum, doseUnit: effectiveDoseUnit, concentration: conc, weightKg });
    } catch {
      return null;
    }
  }, [direction, conc, rateNum, rateError, effectiveDoseUnit, weightKg]);

  // Dose expressed in the drug's reference unit, to compare with the source range/max.
  const currentDoseRef = useMemo(() => {
    const v = direction === 'forward' ? doseNum : reverse?.status === 'ok' ? reverse.dose : null;
    if (v === null || v === undefined) return null;
    try {
      return convertDose(v, effectiveDoseUnit, drug.doseUnit, weightKg);
    } catch {
      return null;
    }
  }, [direction, doseNum, reverse, effectiveDoseUnit, drug.doseUnit, weightKg]);

  const warnings: string[] = [];
  if (currentDoseRef !== null) {
    const maxV = drug.dosing.max?.value ?? null;
    const r = drug.dosing.range;
    if (maxV !== null && currentDoseRef > maxV * (1 + 1e-9))
      warnings.push(t('calc.warn.aboveMax', { value: f.num(maxV), unit: f.unit(drug.doseUnit) }));
    else if (r?.max !== null && r?.max !== undefined && currentDoseRef > r.max * (1 + 1e-9))
      warnings.push(t('calc.warn.aboveRange', { value: f.num(r.max), unit: f.unit(drug.doseUnit) }));
    const lower = drug.dosing.range?.min ?? drug.dosing.start?.min ?? null;
    if (lower !== null && currentDoseRef < lower * (1 - 1e-9))
      warnings.push(t('calc.warn.belowRange', { value: f.num(lower), unit: f.unit(drug.doseUnit) }));
  }

  const table = useMemo(() => {
    const from = parseDecimal(tFrom);
    const to = parseDecimal(tTo);
    const step = parseDecimal(tStep);
    if (!conc || from === null || to === null || step === null) return [];
    try {
      return buildTitrationTable({ from, to, step, doseUnit: drug.doseUnit, concentration: conc, weightKg });
    } catch {
      return [];
    }
  }, [tFrom, tTo, tStep, conc, drug.doseUnit, weightKg]);

  const loading = drug.dosing.loading;
  const bolus = useMemo(() => {
    if (!loading || weightKg === null) return null;
    const massConc = conc && !conc.unit.startsWith('units') ? conc : null;
    try {
      return {
        min: computeBolus({ dosePerKg: loading.doseMin, unit: loading.unit, weightKg, concentration: massConc, durationMin: loading.durationMin }),
        max:
          loading.doseMax !== loading.doseMin
            ? computeBolus({ dosePerKg: loading.doseMax, unit: loading.unit, weightKg, concentration: massConc, durationMin: loading.durationMin })
            : null,
      };
    } catch {
      return null;
    }
  }, [loading, weightKg, conc]);

  const stepText = (s: CalcStep): string => {
    const n = (v: number) => f.num(v, 4);
    switch (s.kind) {
      case 'weight-multiply':
        return `${n(s.dose)} ${f.unit(s.doseUnit)} × ${n(s.weightKg)} kg = ${n(s.result)} ${f.unit(s.resultUnit)}`;
      case 'per-min-to-per-hour':
        return `${n(s.value)} ${f.unit(s.valueUnit)} × 60 min/h = ${n(s.result)} ${f.unit(s.resultUnit)}`;
      case 'convert-amount':
        return `${n(s.value)} ${f.unit(s.from)}/h = ${n(s.result)} ${f.unit(s.to)}/h`;
      case 'divide-concentration':
        return `${n(s.amountPerHour)} ${f.unit(s.amountUnit)}/h ÷ ${n(s.concentration)} ${f.unit(s.concentrationUnit)} = ${n(s.result)} mL/h`;
    }
  };
  const stepLabel = (s: CalcStep) => t(`calc.steps.${s.kind}`);

  const amountUnits: AmountUnit[] = drug.doseUnit.startsWith('units') ? ['units'] : ['mg', 'mcg', 'ng'];
  const currentRowDose = direction === 'forward' ? currentDoseRef : null;

  return (
    <div className="space-y-4">
      <header>
        <h1 className="text-2xl font-extrabold tracking-tight sm:text-3xl">{t('calc.title')}</h1>
        <p className="mt-1 text-muted">{t('calc.subtitle')}</p>
      </header>
      <DraftBanner compact />

      <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.1fr)]">
        {/* ------- Inputs ------- */}
        <form className="card space-y-5 p-4 sm:p-5" onSubmit={(e) => e.preventDefault()} aria-label={t('calc.inputs')}>
          <div>
            <label htmlFor="calc-drug" className="label">
              {t('calc.drug')}
            </label>
            <select id="calc-drug" className="input" value={drugId} onChange={(e) => selectDrug(e.target.value)} data-testid="calc-drug">
              {(['vasoactive-inotrope', 'icu-sedation-analgesia'] as const).map((c) => (
                <optgroup key={c} label={t(`categories.${c}`)}>
                  {drugs
                    .filter((d) => d.category === c)
                    .map((d) => (
                      <option key={d.id} value={d.id}>
                        {d.name}
                        {t(`drugNames.${d.id}`, { defaultValue: d.name }) !== d.name ? ` — ${t(`drugNames.${d.id}`)}` : ''}
                      </option>
                    ))}
                </optgroup>
              ))}
            </select>
            <p className="mt-1.5 text-xs">
              <Link to={`/drugs/${drug.id}`} className="font-semibold text-primary hover:underline">
                {t('calc.viewMonograph')}
              </Link>
            </p>
          </div>

          <fieldset>
            <legend className="label">{t('calc.preparation')}</legend>
            <div className="space-y-2">
              {drug.preparations.map((p) => (
                <label
                  key={p.id}
                  className={`flex cursor-pointer items-start gap-3 rounded-xl border p-3 text-sm transition ${prepId === p.id ? 'border-primary bg-primary/5 ring-1 ring-primary/40' : 'border-border hover:bg-surface-2'}`}
                >
                  <input type="radio" name="prep" value={p.id} checked={prepId === p.id} onChange={() => setPrepId(p.id)} className="mt-1 h-4 w-4 accent-[rgb(var(--c-primary))]" />
                  <span className="min-w-0 flex-1">
                    <span className="flex flex-wrap items-baseline justify-between gap-x-3">
                      <span className="font-semibold">{p.label}</span>
                      <span className="num font-bold">
                        {f.num(p.concentration.value)} {f.unit(p.concentration.unit)}
                      </span>
                    </span>
                    <span className="num block text-xs text-muted">
                      {p.amount ? `${f.num(p.amount.value)} ${f.unit(p.amount.unit)}` : t('common.amountNotStated')}
                      {' / '}
                      {p.finalVolumeMl ? `${f.num(p.finalVolumeMl)} mL` : t('common.volumeNotStated')}
                    </span>
                  </span>
                </label>
              ))}
              <label
                className={`flex cursor-pointer items-start gap-3 rounded-xl border p-3 text-sm transition ${prepId === CUSTOM ? 'border-primary bg-primary/5 ring-1 ring-primary/40' : 'border-border hover:bg-surface-2'}`}
              >
                <input type="radio" name="prep" value={CUSTOM} checked={prepId === CUSTOM} onChange={() => setPrepId(CUSTOM)} className="mt-1 h-4 w-4 accent-[rgb(var(--c-primary))]" />
                <span className="font-semibold">{t('calc.custom')}</span>
              </label>
            </div>
            {prepId === CUSTOM && (
              <div className="mt-3 grid grid-cols-2 gap-3 rounded-xl bg-surface-2 p-3">
                <NumberField label={t('prep.amount')} value={customAmount} onChange={setCustomAmount} testId="custom-amount" />
                <div>
                  <label htmlFor="custom-unit" className="label">
                    {t('calc.amountUnit')}
                  </label>
                  <select id="custom-unit" className="input" value={customAmountUnit} onChange={(e) => setCustomAmountUnit(e.target.value as AmountUnit)}>
                    {amountUnits.map((u) => (
                      <option key={u} value={u}>
                        {f.unit(u)}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="col-span-2">
                  <NumberField label={t('prep.finalVolume')} value={customVolume} onChange={setCustomVolume} suffix="mL" error={concResult.error} testId="custom-volume" />
                </div>
                <p className="col-span-2 text-xs text-muted">
                  {conc ? (
                    <>
                      {t('prep.concentration')}: <span className="num font-bold text-fg">{f.num(conc.value, 4)} {f.unit(conc.unit)}</span>
                    </>
                  ) : (
                    t('calc.customHint')
                  )}
                </p>
              </div>
            )}
          </fieldset>

          <NumberField
            label={t('calc.weight')}
            value={weight}
            onChange={setWeight}
            suffix="kg"
            error={weightError}
            hint={needsWeight ? t('calc.weightRequired') : t('calc.weightNotNeeded')}
            testId="calc-weight"
            placeholder="70"
            large
          />

          <div>
            <div className="label">{t('calc.direction')}</div>
            <div role="radiogroup" aria-label={t('calc.direction')} className="grid grid-cols-2 gap-1 rounded-xl bg-surface-2 p-1">
              {(['forward', 'reverse'] as const).map((d) => (
                <button
                  key={d}
                  type="button"
                  role="radio"
                  aria-checked={direction === d}
                  onClick={() => setDirection(d)}
                  className={`min-h-[40px] rounded-lg px-3 text-sm font-semibold transition ${direction === d ? 'bg-surface text-fg shadow-card' : 'text-muted hover:text-fg'}`}
                >
                  {t(`calc.${d}`)}
                </button>
              ))}
            </div>
          </div>

          {direction === 'forward' ? (
            <div className="grid grid-cols-[1fr_auto] items-end gap-2">
              <NumberField label={t('calc.dose')} value={dose} onChange={setDose} error={doseError} testId="calc-dose" large />
              <DoseUnitSelect options={unitOptions} value={effectiveDoseUnit} onChange={setDoseUnit} />
            </div>
          ) : (
            <div className="space-y-3">
              <NumberField label={t('calc.rate')} value={rate} onChange={setRate} suffix="mL/h" error={rateError} testId="calc-rate" large />
              <DoseUnitSelect options={unitOptions} value={effectiveDoseUnit} onChange={setDoseUnit} label={t('calc.outputUnit')} />
            </div>
          )}

          {(drug.dosing.start || drug.dosing.range || drug.dosing.max) && (
            <div className="rounded-xl border border-border p-3 text-xs">
              <p className="section-title mb-1.5">{t('calc.reference')}</p>
              <ul className="num space-y-0.5">
                {drug.dosing.start && (
                  <li>
                    {t('dosing.start')}: <b>{f.range(drug.dosing.start.min, drug.dosing.start.max)} {f.unit(drug.doseUnit)}</b>
                  </li>
                )}
                {drug.dosing.range && (
                  <li>
                    {t('dosing.range')}: <b>{f.range(drug.dosing.range.min, drug.dosing.range.max)} {f.unit(drug.doseUnit)}</b>
                  </li>
                )}
                {drug.dosing.max?.value !== null && drug.dosing.max?.value !== undefined && (
                  <li>
                    {t('dosing.max')}: <b className="text-danger">{f.num(drug.dosing.max.value)} {f.unit(drug.doseUnit)}</b>
                  </li>
                )}
                {drug.dosing.titration && (
                  <li className="text-muted">
                    {t('dosing.titration')}: <ClinicalText text={drug.dosing.titration.text} />
                  </li>
                )}
              </ul>
            </div>
          )}
        </form>

        {/* ------- Results ------- */}
        <div className="space-y-4" aria-live="polite">
          <section aria-labelledby="calc-result" className="card overflow-hidden" data-testid="calc-result">
            <h2 id="calc-result" className="sr-only">
              {t('calc.result')}
            </h2>
            {!conc ? (
              <p className="p-5 text-sm text-muted">{t('calc.needConcentration')}</p>
            ) : direction === 'forward' ? (
              !forward ? (
                <p className="p-5 text-sm text-muted">{t('calc.enterDose')}</p>
              ) : forward.status === 'needs-weight' ? (
                <NeedsWeight formula={forward.formula} />
              ) : (
                <div>
                  <div className="bg-primary/10 p-5">
                    <p className="section-title">{t('calc.pumpRate')}</p>
                    <p className="mt-1 flex items-baseline gap-2">
                      <span className="num text-5xl font-extrabold tracking-tight text-primary" data-testid="rate-display">
                        {f.rate(forward.mlPerHourDisplay)}
                      </span>
                      <span className="text-xl font-bold text-primary">mL/h</span>
                    </p>
                    <p className="num mt-1 text-sm text-muted">
                      {t('calc.exact')}: {f.num(forward.mlPerHour, 4)} mL/h · {f.num(doseNum ?? 0, 4)} {f.unit(effectiveDoseUnit)}
                      {weightKg && needsWeight ? ` · ${f.num(weightKg)} kg` : ''}
                    </p>
                  </div>
                  <Steps steps={forward.steps} formula={forward.formula} render={stepText} label={stepLabel} />
                </div>
              )
            ) : !reverse ? (
              <p className="p-5 text-sm text-muted">{t('calc.enterRate')}</p>
            ) : reverse.status === 'needs-weight' ? (
              <NeedsWeight formula={reverse.formula} />
            ) : (
              <div className="bg-primary/10 p-5">
                <p className="section-title">{t('calc.deliveredDose')}</p>
                <p className="mt-1 flex flex-wrap items-baseline gap-2">
                  <span className="num text-5xl font-extrabold tracking-tight text-primary" data-testid="dose-display">
                    {f.num(reverse.dose, 3)}
                  </span>
                  <span className="text-xl font-bold text-primary">{f.unit(effectiveDoseUnit)}</span>
                </p>
                <p className="num mt-1 text-sm text-muted">
                  {f.num(rateNum ?? 0)} mL/h × {f.num(conc.value, 4)} {f.unit(conc.unit)} = {f.num(reverse.amountPerHour, 4)} {f.unit(reverse.amountUnit)}/h
                </p>
              </div>
            )}
            {warnings.length > 0 && (
              <ul className="space-y-1 border-t border-border bg-warn-bg p-4 text-sm font-semibold text-warn" role="alert">
                {warnings.map((w) => (
                  <li key={w} className="flex gap-2">
                    <Icon name="alert" size={18} className="shrink-0" /> {w}
                  </li>
                ))}
              </ul>
            )}
          </section>

          {conc && (
            <section aria-labelledby="prep-summary" className="card p-4 sm:p-5">
              <h2 id="prep-summary" className="mb-3 text-base font-bold">
                {t('calc.preparationSummary')}
              </h2>
              <dl className="grid grid-cols-3 gap-3 text-sm">
                <div className="rounded-xl bg-surface-2 p-3">
                  <dt className="text-xs text-muted">{t('prep.amount')}</dt>
                  <dd className="num font-bold">
                    {preparation
                      ? preparation.amount
                        ? `${f.num(preparation.amount.value)} ${f.unit(preparation.amount.unit)}`
                        : '—'
                      : `${customAmount} ${f.unit(customAmountUnit)}`}
                  </dd>
                </div>
                
                <div className="rounded-xl bg-surface-2 p-3">
                  <dt className="text-xs text-muted">{t('prep.finalVolume')}</dt>
                  <dd className="num font-bold">
                    {preparation ? (preparation.finalVolumeMl ? `${f.num(preparation.finalVolumeMl)} mL` : '—') : `${customVolume} mL`}
                  </dd>
                </div>
                <div className="rounded-xl bg-surface-2 p-3">
                  <dt className="text-xs text-muted">{t('prep.concentration')}</dt>
                  <dd className="num font-bold">
                    {f.num(conc.value, 4)} {f.unit(conc.unit)}
                  </dd>
                </div>
                <div className="col-span-3 rounded-xl bg-surface-2 p-3">
                  <dt className="text-xs text-muted">{t('prep.diluent')}</dt>
                  <dd className="text-sm font-semibold leading-snug">
                    {preparation?.diluent ? <ClinicalText text={preparation.diluent} /> : <span className="italic text-muted">{t('common.notInSource')}</span>}
                  </dd>
                </div>
              </dl>
              {preparation?.note && (
                <p className="mt-3 text-xs text-muted">
                  <ClinicalText text={preparation.note} />
                </p>
              )}
            </section>
          )}

          {loading && (
            <section aria-labelledby="bolus-title" className="card p-4 sm:p-5">
              <h2 id="bolus-title" className="flex items-center gap-2 text-base font-bold">
                <Icon name="syringe" size={18} /> {t('bolus.title')}
                {loading.optional && <span className="text-xs font-semibold text-muted">({t('bolus.optional')})</span>}
              </h2>
              <p className="mt-1 text-xs text-muted">{t('bolus.noRate')}</p>
              {bolus ? (
                <dl className="mt-3 grid grid-cols-3 gap-3 text-sm">
                  <div className="rounded-xl bg-surface-2 p-3">
                    <dt className="text-xs text-muted">{t('bolus.dose')}</dt>
                    <dd className="num font-bold">
                      {f.num(bolus.min.amount)}
                      {bolus.max ? `–${f.num(bolus.max.amount)}` : ''} {f.unit(bolus.min.amountUnit)}
                    </dd>
                    <dd className="num text-xs text-muted">
                      {f.range(loading.doseMin, loading.doseMax)} {f.unit(loading.unit)}
                    </dd>
                  </div>
                  <div className="rounded-xl bg-surface-2 p-3">
                    <dt className="text-xs text-muted">{t('bolus.volume')}</dt>
                    <dd className="num font-bold">
                      {bolus.min.volumeMl !== null ? `${f.num(bolus.min.volumeMl, 2)}${bolus.max?.volumeMl ? `–${f.num(bolus.max.volumeMl, 2)}` : ''} mL` : '—'}
                    </dd>
                    <dd className="num text-xs text-muted">{conc ? `@ ${f.num(conc.value, 4)} ${f.unit(conc.unit)}` : ''}</dd>
                  </div>
                  <div className="rounded-xl bg-surface-2 p-3">
                    <dt className="text-xs text-muted">{t('bolus.time')}</dt>
                    <dd className="num font-bold">{loading.durationMin ? `${loading.durationMin} min` : <span className="text-xs font-normal italic text-muted">{t('common.notInSource')}</span>}</dd>
                  </div>
                </dl>
              ) : (
                <p className="mt-3 text-sm text-muted">{t('calc.weightRequired')}</p>
              )}
              <p className="mt-3 text-xs text-muted">
                <ClinicalText text={loading.text} />
              </p>
            </section>
          )}

          <section aria-labelledby="titration-title" className="card p-4 sm:p-5">
            <h2 id="titration-title" className="text-base font-bold">
              {t('titration.title')}
            </h2>
            <p className="mt-1 text-xs text-muted">{t('titration.note')}</p>
            <div className="mt-3 grid grid-cols-3 gap-2">
              <NumberField label={t('titration.from')} value={tFrom} onChange={setTFrom} />
              <NumberField label={t('titration.to')} value={tTo} onChange={setTTo} />
              <NumberField label={t('titration.step')} value={tStep} onChange={setTStep} />
            </div>
            {table === null ? (
              <p className="mt-3 rounded-xl bg-surface-2 p-3 text-sm text-muted">{t('titration.needsWeight')}</p>
            ) : table.length === 0 ? (
              <p className="mt-3 text-sm text-muted">{t('titration.invalid')}</p>
            ) : (
              <div className="mt-3 max-h-[420px] overflow-auto rounded-xl border border-border">
                <table className="w-full text-sm" data-testid="titration-table">
                  <caption className="sr-only">{t('titration.title')}</caption>
                  <thead className="sticky top-0 bg-surface-2 text-xs uppercase tracking-wide text-muted">
                    <tr>
                      <th scope="col" className="px-3 py-2 text-left font-semibold">
                        {t('calc.dose')} ({f.unit(drug.doseUnit)})
                      </th>
                      <th scope="col" className="px-3 py-2 text-right font-semibold">mL/h</th>
                    </tr>
                  </thead>
                  <tbody>
                    {table.map((r) => {
                      const current = currentRowDose !== null && Math.abs(r.dose - currentRowDose) < 1e-9;
                      return (
                        <tr key={r.dose} className={`border-t border-border ${current ? 'bg-primary/10 font-bold text-primary' : ''}`} aria-current={current ? 'true' : undefined}>
                          <td className="num px-3 py-2">{f.num(r.dose, 4)}</td>
                          <td className="num px-3 py-2 text-right font-semibold">{f.rate(r.mlPerHourDisplay)}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}

function DoseUnitSelect({ options, value, onChange, label }: { options: DoseUnit[]; value: DoseUnit; onChange: (u: DoseUnit) => void; label?: string }) {
  const { t } = useTranslation();
  const f = useFormat();
  return (
    <div>
      <label htmlFor="dose-unit" className={label ? 'label' : 'sr-only'}>
        {label ?? t('calc.doseUnit')}
      </label>
      <select id="dose-unit" className="input num min-w-[140px] font-semibold" value={value} onChange={(e) => onChange(e.target.value as DoseUnit)} data-testid="dose-unit">
        {options.map((u) => (
          <option key={u} value={u}>
            {f.unit(u)}
          </option>
        ))}
      </select>
    </div>
  );
}

function NeedsWeight({ formula }: { formula: string }) {
  const { t } = useTranslation();
  const f = useFormat();
  return (
    <div className="p-5" data-testid="needs-weight">
      <p className="flex items-center gap-2 font-bold text-warn">
        <Icon name="alert" size={20} /> {t('calc.noWeightTitle')}
      </p>
      <p className="mt-1 text-sm text-muted">{t('calc.noWeightBody')}</p>
      <p className="mt-3 rounded-xl bg-surface-2 p-3 font-mono text-sm">{f.unit(formula)}</p>
    </div>
  );
}

function Steps({ steps, formula, render, label }: { steps: CalcStep[]; formula: string; render: (s: CalcStep) => string; label: (s: CalcStep) => string }) {
  const { t } = useTranslation();
  const f = useFormat();
  return (
    <div className="p-5">
      <p className="section-title">{t('calc.arithmetic')}</p>
      <p className="mt-2 rounded-lg bg-surface-2 px-3 py-2 font-mono text-xs text-muted">{f.unit(formula)}</p>
      <ol className="mt-3 space-y-2">
        {steps.map((s, i) => (
          <li key={i} className="flex gap-3 text-sm">
            <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary/15 text-xs font-bold text-primary">{i + 1}</span>
            <span className="min-w-0">
              <span className="block text-xs text-muted">{label(s)}</span>
              <span className="num block break-words font-mono font-semibold">{render(s)}</span>
            </span>
          </li>
        ))}
      </ol>
      <p className="mt-3 text-xs text-muted">{t('calc.roundingNote')}</p>
    </div>
  );
}

