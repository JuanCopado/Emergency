import { useEffect, useRef, useState, useSyncExternalStore } from 'react';
import { useTranslation } from 'react-i18next';
import { useClinicalNoteDraft } from '../clinical-note/draft';
import { localUpdateSnapshot, requestLocalUpdate, setLocalReloadGuard, subscribeLocalUpdate } from '../lib/localUpdate';

const text = {
  es: { title: 'Actualización disponible', body: 'Puedes continuar con esta versión. Actualiza después de finalizar o exportar las notas abiertas en todas las pestañas.', dirty: 'La nota actual tiene contenido. Finaliza o exporta el episodio antes de actualizar.', confirm: 'He finalizado los episodios abiertos en todas las pestañas.', update: 'Actualizar y recargar', later: 'Más tarde', pending: 'Actualización pendiente', failed: 'No se pudo actualizar. Se conserva la sesión actual.' },
  en: { title: 'Update available', body: 'You can keep using this version. Update after finishing or exporting open notes in every tab.', dirty: 'The current note contains content. Finish or export the encounter before updating.', confirm: 'I have finished the open encounters in every tab.', update: 'Update and reload', later: 'Later', pending: 'Update pending', failed: 'The update failed. The current session is preserved.' },
  pt: { title: 'Atualização disponível', body: 'Pode continuar nesta versão. Atualize depois de concluir ou exportar as notas abertas em todos os separadores.', dirty: 'A nota atual contém conteúdo. Conclua ou exporte o episódio antes de atualizar.', confirm: 'Concluí os episódios abertos em todos os separadores.', update: 'Atualizar e recarregar', later: 'Mais tarde', pending: 'Atualização pendente', failed: 'Não foi possível atualizar. A sessão atual é preservada.' },
  zh: { title: '有可用更新', body: '可以继续使用此版本。请先完成或导出所有标签页中打开的记录，然后更新。', dirty: '当前记录包含内容。更新前请先完成或导出本次就诊记录。', confirm: '我已完成所有标签页中打开的就诊记录。', update: '更新并重新加载', later: '稍后', pending: '更新待处理', failed: '更新失败。当前会话已保留。' },
};

export function LocalUpdateNotice() {
  const { i18n } = useTranslation();
  const { hasContent } = useClinicalNoteDraft();
  const update = useSyncExternalStore(subscribeLocalUpdate, localUpdateSnapshot, localUpdateSnapshot);
  const [confirmed, setConfirmed] = useState(false);
  const [minimized, setMinimized] = useState(false);
  const guard = useRef({ hasContent, confirmed });
  guard.current = { hasContent, confirmed };
  useEffect(() => setLocalReloadGuard(() => !guard.current.hasContent && guard.current.confirmed), []);
  useEffect(() => { if (hasContent) setConfirmed(false); }, [hasContent]);
  const language = i18n.language.split('-')[0];
  const t = text[language as keyof typeof text] ?? text.en;
  if (!update.available) return null;
  if (minimized) return <div className="mx-auto max-w-6xl px-4 pt-3"><button type="button" className="rounded border border-border px-3 py-2 text-sm" onClick={() => setMinimized(false)}>{t.pending}</button></div>;
  return <section className="mx-auto max-w-6xl px-4 pt-3" role="status" aria-label={t.title} data-testid="local-update-notice">
    <div className="rounded-xl border border-border bg-surface p-4 text-sm">
      <h2 className="font-bold">{t.title}</h2><p className="mt-1">{t.body}</p>
      {hasContent && <p className="mt-2 font-semibold">{t.dirty}</p>}
      {update.failed && <p role="alert" className="mt-2">{t.failed}</p>}
      <label className="mt-3 flex items-start gap-2"><input data-testid="local-update-confirm" type="checkbox" checked={confirmed} disabled={hasContent || update.applying} onChange={event => setConfirmed(event.target.checked)} />{t.confirm}</label>
      <div className="mt-3 flex gap-2"><button data-testid="local-update-apply" type="button" className="rounded border border-border px-3 py-2 font-semibold disabled:opacity-50" disabled={hasContent || !confirmed || update.applying} onClick={() => { void requestLocalUpdate(); }}>{t.update}</button>
      <button type="button" className="rounded border border-border px-3 py-2" disabled={update.applying} onClick={() => setMinimized(true)}>{t.later}</button></div>
    </div>
  </section>;
}
