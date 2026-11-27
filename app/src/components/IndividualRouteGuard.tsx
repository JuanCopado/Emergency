import { Component, useEffect, useRef, useState, useSyncExternalStore, type ReactNode } from 'react';
import { useLocation, useNavigate, type Location } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { localUpdateSnapshot, markLocalUpdateAvailable, subscribeLocalUpdate } from '../lib/localUpdate';

// Keep the draft provider OUTSIDE this boundary. A rejected dynamic import must
// never destroy an open episode, even if a runtime changes during an asset read.
const copy = {
  es: { failed: 'No se pudo abrir esta pantalla. La nota permanece en esta pestaña.', back: 'Volver a la nota abierta', blocked: 'Actualización pendiente: se conserva la nota y se bloquean pantallas nuevas. Puedes volver a pantallas ya abiertas. Para finalizar operaciones incompatibles, vuelve a la versión anterior.' },
  en: { failed: 'This screen could not be opened. The note remains in this tab.', back: 'Return to the open note', blocked: 'Update pending: the note is retained and new screens are blocked. Previously opened screens remain accessible. Return to the previous version to finish incompatible operations.' },
  pt: { failed: 'Não foi possível abrir este ecrã. A nota permanece neste separador.', back: 'Voltar à nota aberta', blocked: 'Atualização pendente: a nota é preservada e novos ecrãs estão bloqueados. Pode voltar aos ecrãs já abertos. Volte à versão anterior para concluir operações incompatíveis.' },
  zh: { failed: '无法打开此页面。记录仍保留在此标签页中。', back: '返回已打开的记录', blocked: '更新待处理：记录已保留，新页面已阻止。可以返回已打开的页面。请恢复上一版本以完成不兼容的操作。' },
};
class PageBoundary extends Component<{ children: ReactNode; recover: () => void; text: typeof copy.en }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  render() {
    return this.state.failed ? <section role="alert" className="p-6">
      <p>{this.props.text.failed}</p>
      <button type="button" onClick={this.props.recover}>{this.props.text.back}</button>
    </section> : this.props.children;
  }
}

export function IndividualRouteGuard({ children, individual = import.meta.env.VITE_INDIVIDUAL_INSTALLATION === '1', revision = String(import.meta.env.VITE_BUILD_REVISION ?? '') }: {
  children: (location: Location) => ReactNode; individual?: boolean; revision?: string;
}) {
  const requested = useLocation();
  const { i18n } = useTranslation();
  const language = (i18n.language ?? 'en').split('-')[0];
  const text = copy[language as keyof typeof copy] ?? copy.en;
  const navigate = useNavigate();
  const [rendered, setRendered] = useState(requested);
  const [blocked, setBlocked] = useState(false);
  const visited = useRef(new Set([requested.pathname]));
  const update = useSyncExternalStore(subscribeLocalUpdate, localUpdateSnapshot, localUpdateSnapshot);
  useEffect(() => {
    // Restoring the URL after a refused navigation creates a fresh history key.
    // It is still the SAME rendered screen: do not remount its local form state.
    if (!individual || (requested.pathname === rendered.pathname && requested.search === rendered.search && requested.hash === rendered.hash)) return;
    let cancelled = false;
    const permit = () => {
      if (cancelled) return;
      visited.current.add(requested.pathname); setRendered(requested);
    };
    const deny = () => {
      if (cancelled) return;
      setBlocked(true);
      navigate(rendered.pathname + rendered.search + rendered.hash, { replace: true });
    };
    // A page already loaded in this document can still expose the existing note
    // and export UI; an unseen lazy import may require a deleted old-version asset.
    if (visited.current.has(requested.pathname)) permit();
    else if (update.available) deny();
    else void fetch('/__local_release__', { cache: 'no-store' }).then(async response => {
      if (!response.ok) throw new Error('Local runtime unavailable');
      const identity = await response.json();
      if (cancelled) return;
      if (identity.source_sha === revision) permit();
      else { markLocalUpdateAvailable(); deny(); }
    }).catch(() => {
      // Preserve first-visit precached frontend use when offline and no update
      // was observed. PageBoundary contains an asset failure without losing notes.
      if (!cancelled) permit();
    });
    return () => { cancelled = true; };
  }, [individual, requested, rendered, revision, navigate, update.available]);
  if (!individual) return children(requested);
  return <>
    {blocked && <div role="status" data-testid="local-stale-navigation" className="p-4">
      {text.blocked}
    </div>}
    {/* Query/hash edits and detail IDs can update one screen's own form state.
        A history entry is not a component identity or an error-reset boundary. */}
    <PageBoundary key={rendered.pathname.split('/')[1] || '/'} text={text} recover={() => navigate('/clinical-note')}>
      {children(rendered)}
    </PageBoundary>
  </>;
}
