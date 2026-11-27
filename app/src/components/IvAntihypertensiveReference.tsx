import { useId, useState } from 'react';
import reference from '../clinical-guides/iv-antihypertensive-reference.json';
import { useClinicalUi } from '../i18n/useClinicalUi';

const countries = ['US', 'ES', 'PT'] as const;
const countryLabels = { US: 'Estados Unidos', ES: 'España', PT: 'Portugal' } as const;
const sourceReviewLabels: Record<string, string> = {
  REUSED_FOCAL_PRIMARY_TEXT_READ: 'Texto primario focal reutilizado',
  NEW_FOCAL_OFFICIAL_HTML_READ_NO_PDF_ACQUISITION: 'Lectura oficial focal',
  ATTRIBUTED_CANONICAL_REGISTRY_METADATA_NOT_NEW_LABEL_REVIEW: 'Metadatos heredados: no es una nueva revisión íntegra de ficha',
};

function ReferenceSelector() {
  const ui = useClinicalUi();
  const labelId = useId();
  const [drug, setDrug] = useState('');
  const [country, setCountry] = useState('');
  const row = reference.referenceRows.find(item => item.drug === drug);
  const products = reference.productReferences.filter(item => item.drug === drug && item.country === country);
  const portugalDocuments = reference.portugalDocuments.filter(item => item.drug === drug);
  return (
    <section aria-labelledby={`${labelId}-title`} className="no-print mt-5 space-y-4 rounded-xl border border-border p-4">
      <h2 id={`${labelId}-title`} className="font-bold">{ui('Referencia informativa de antihipertensivos IV')}</h2>
      <p className="text-sm">{ui('CLINICALLY_PENDING · Selección manual de referencia; no selecciona diagnóstico, tratamiento ni pauta de administración.')}</p>
      <div className="grid gap-3 sm:grid-cols-2">
        <label className="label">
          {ui('Fármaco de referencia')}
          <select className="input mt-1" value={drug} onChange={event => {
            const value = event.currentTarget.value;
            setDrug(reference.referenceRows.some(item => item.drug === value) ? value : '');
          }}>
            <option value="">{ui('Selecciona un fármaco')}</option>
            {reference.referenceRows.map(item => <option key={item.drug} value={item.drug}>{item.drug}</option>)}
          </select>
        </label>
        <label className="label">
          {ui('País de la ficha')}
          <select className="input mt-1" value={country} onChange={event => {
            const value = event.currentTarget.value;
            setCountry(countries.some(item => item === value) ? value : '');
          }}>
            <option value="">{ui('Selecciona un país')}</option>
            {countries.map(item => <option key={item} value={item}>{ui(countryLabels[item])}</option>)}
          </select>
        </label>
      </div>
      <p className="text-sm text-muted">{ui('Selecciona fármaco y país de forma explícita. El idioma no determina la jurisdicción.')}</p>
      {row && <dl className="space-y-2 text-sm" aria-label={ui('Posición de referencia aprobada')}>
        <dt className="font-bold">{ui('Posición de referencia aprobada')}</dt><dd>{row.owner_role}</dd>
        <dt className="font-bold">{ui('Precaución principal de referencia')}</dt><dd>{row.owner_guard}</dd>
        <dd className="text-muted">{ui('Las precauciones mostradas no sustituyen la ficha completa del producto.')}</dd>
      </dl>}
      {row && country && <div className="space-y-3" aria-live="polite">
        <p className="text-sm"><strong>{ui('Perfil operativo')}: </strong>{ui('No habilitado: consulta informativa sin cálculos de administración.')}</p>
        {drug === 'labetalol' && <p className="text-sm">{ui('El producto original de labetalol de la fuente compuesta sigue sin identificar; no mezclar etiquetas ni asumir un error universal.')}</p>}
        {country === 'PT' ? <div className="space-y-2 text-sm">
          {portugalDocuments.length ? <>
            <p>{ui('Identidad documental portuguesa; no confirma un perfil operativo. Estado nacional vigente y existencias locales sin verificar.')}</p>
            {portugalDocuments.map(document => <article key={document.registration} className="space-y-2 rounded-lg border border-border p-3">
              <h3 className="font-bold">{document.product}</h3>
              <dl>
                <dt className="font-bold">{ui('Identidad del producto')}</dt><dd>PT · {document.registration}</dd>
                <dt className="font-bold">{ui('Verificación de la fuente')}</dt><dd>{ui(document.scope)}</dd>
                <dt className="font-bold">{ui('Procedencia y versión de la fuente')}</dt><dd>{document.version}</dd>
                <dd>{document.locator}</dd>
              </dl>
              {document.discrepancy && <p>{ui(document.discrepancy)}</p>}
              <a href={document.url} target="_blank" rel="noreferrer" className="inline-block break-all underline">{ui('Consultar fuente oficial')}</a>
            </article>)}
          </> : <p>{ui('Producto, RCM y disponibilidad local no establecidos; no demuestra ausencia ni existencias.')}</p>}
          <a href={reference.portugalLookup} target="_blank" rel="noreferrer" className="inline-block break-all underline">{ui('Consultar fuente oficial')}</a>
        </div> : products.length ? products.map(product => <article key={product.identity} className="space-y-2 rounded-lg border border-border p-3 text-sm">
          <h3 className="font-bold">{product.product}</h3>
          <dl className="space-y-1">
            <dt className="font-bold">{ui('Identidad del producto')}</dt><dd className="break-words">{product.identity}</dd>
            <dt className="font-bold">{ui('Verificación de la fuente')}</dt><dd>{ui(sourceReviewLabels[product.evidence] ?? 'Estado de revisión de la fuente no establecido')}</dd>
            <dt className="font-bold">{ui('Procedencia y versión de la fuente')}</dt><dd>{product.version}</dd>
            {product.locator && <dd>{product.locator}</dd>}
          </dl>
          <p>{product.summary}</p>
          <a href={product.url} target="_blank" rel="noreferrer" className="inline-block break-all underline">{ui('Consultar fuente oficial')}</a>
        </article>) : <p className="text-sm">{ui('Sin producto identificado para esta combinación en este expediente.')}</p>}
      </div>}
    </section>
  );
}

/** Reference display only: no case inputs, dose fields, calculations or operational profiles. */
export function IvAntihypertensiveReference({ moduleId }: { moduleId: string }) {
  return moduleId === 'iv-antihypertensive-selection' ? <ReferenceSelector /> : null;
}
