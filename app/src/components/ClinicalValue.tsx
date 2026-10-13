// Render canonical results without inferring missing fields or computing clinical values.
export default function ClinicalValue({ value }: { value: unknown }) {
  if (value == null) return <span>No registrado</span>;
  if (Array.isArray(value)) return <ul className="space-y-2">{value.map((v,i)=><li key={i}><ClinicalValue value={v}/></li>)}</ul>;
  if (typeof value === 'object') return <dl className="space-y-2">{Object.entries(value).map(([key,v])=><div key={key} className="min-w-0 border-l border-border pl-3"><dt className="font-semibold">{key.replaceAll('_',' ')}</dt><dd className="break-words"><ClinicalValue value={v}/></dd></div>)}</dl>;
  if (typeof value === 'boolean') return <span>{value ? 'Sí' : 'No'}</span>;
  if (typeof value === 'string' && /^https?:\/\//.test(value)) return <a className="underline break-all" href={value} target="_blank" rel="noreferrer">{value}</a>;
  return <span>{String(value)}</span>;
}
