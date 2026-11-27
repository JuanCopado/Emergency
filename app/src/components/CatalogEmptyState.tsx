import { useClinicalUi } from '../i18n/useClinicalUi';
import { SearchEmptyState } from './SearchEmptyState';

export function CatalogEmptyState({ onReset, resetFilters = false }: { onReset: () => void; resetFilters?: boolean }) {
  const ui = useClinicalUi();
  return (
    <SearchEmptyState
      heading={ui('Ningún módulo coincide con la búsqueda.')}
      hint={ui(resetFilters ? 'Prueba otro término o restablece la búsqueda y los filtros.' : 'Prueba otro término o borra la búsqueda.')}
      resetLabel={ui(resetFilters ? 'Restablecer búsqueda y filtros' : 'Borrar búsqueda')}
      onReset={onReset}
    />
  );
}
