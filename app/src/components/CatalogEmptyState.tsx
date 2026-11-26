import { useClinicalUi } from '../i18n/useClinicalUi';

export function CatalogEmptyState({ onReset, resetFilters = false }: { onReset: () => void; resetFilters?: boolean }) {
  const ui = useClinicalUi();
  return (
    <div className="rounded-xl border border-border bg-surface-2 p-5">
      <h2 className="font-bold">{ui('Ningún módulo coincide con la búsqueda.')}</h2>
      <p className="mt-1 text-sm text-muted">{ui(resetFilters ? 'Prueba otro término o restablece la búsqueda y los filtros.' : 'Prueba otro término o borra la búsqueda.')}</p>
      <button type="button" className="btn-ghost mt-4" onClick={onReset}>
        {ui(resetFilters ? 'Restablecer búsqueda y filtros' : 'Borrar búsqueda')}
      </button>
    </div>
  );
}
