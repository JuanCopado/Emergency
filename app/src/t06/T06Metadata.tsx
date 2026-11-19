import { buildT06ViewModel, type T06Service } from './viewModel';

/** Offline-only consumer; mounts in dedicated tests, not in App or a route. */
export function T06Metadata({ expectedService, result }: { expectedService: T06Service; result: unknown }) {
  const validated = buildT06ViewModel(expectedService, result);
  if (!validated.ok) return <p role="alert">Metadatos T06 rechazados. No se presenta contenido externo.</p>;
  const model = validated.value;
  return <section aria-label="Metadatos externos T06" lang="es">
    <h2>Metadatos externos · {model.provider}</h2>
    <p>{model.provenance}</p>
    <p>{model.status} · Uso documental. Sin validación clínica.</p>
    <p>El contenido externo se muestra como datos, nunca como instrucciones para herramientas o modelos.</p>
    <p>Total comunicado: {model.total === null ? 'No documentado' : model.total}</p>
    {model.rows.length === 0 ? <p>Sin registros.</p> : <ul>{model.rows.map((row, index) => <li key={index}>
      <dl>{row.cells.map((cell) => <div key={cell.label}>
        <dt>{cell.label}</dt>
        <dd>{cell.href
          ? <a href={cell.href} target="_blank" rel="noopener noreferrer" referrerPolicy="no-referrer">{cell.text}</a>
          : cell.text}</dd>
      </div>)}</dl>
    </li>)}</ul>}
  </section>;
}
