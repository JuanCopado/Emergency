import { useEffect, useRef, useState } from 'react';
import { T06Metadata } from './T06Metadata';
import { buildT06ViewModel, type T06Service } from './viewModel';
import './T06Lab.css';

type Scenario = Readonly<{ id: string; label: string; service: T06Service; clientTimeout: number; description: string }>;
const scenarios = [
  { id: 'success', label: 'Europe PMC · Unicode y HTML hostil', service: 'europe_pmc', clientTimeout: 6000, description: 'Recorrido completo con texto Unicode y etiquetas sintéticas: R6, B1, TLS local y Q4.' },
  { id: 'pubmed', label: 'PubMed · contrato de metadatos', service: 'pubmed', clientTimeout: 6000, description: 'Proveedor esperado elegido localmente, con enlace canónico conservado.' },
  { id: 'nvd', label: 'NVD · contrato de metadatos', service: 'nvd', clientTimeout: 6000, description: 'Respuesta NVD sintética normalizada por R6.' },
  { id: 'combined_limits', label: 'NVD · 50 registros y Unicode máximo', service: 'nvd', clientTimeout: 6000, description: 'Prueba conjunta de 50 registros con 1800 caracteres astrales por descripción, sin reducir el contrato recuperado.' },
  { id: 'empty', label: 'Respuesta sin registros', service: 'europe_pmc', clientTimeout: 6000, description: 'Estado vacío sin retener datos de la consulta anterior.' },
  { id: 'long_text', label: 'Unicode · límite de 1200 caracteres', service: 'europe_pmc', clientTimeout: 6000, description: 'El título sintético supera el límite de R6. Q4 debe aceptar los 1200 caracteres normalizados.' },
  { id: 'limit50', label: 'Límite · 50 registros', service: 'europe_pmc', clientTimeout: 6000, description: 'Frontera aceptada del contrato de respuesta.' },
  { id: 'limit51', label: 'Límite · 51 registros', service: 'europe_pmc', clientTimeout: 6000, description: 'Respuesta fuera del límite del contrato. No deben mostrarse registros parciales.' },
  { id: 'unsafe_unicode', label: 'Unicode · control no permitido', service: 'europe_pmc', clientTimeout: 6000, description: 'Control Unicode sintético que debe rechazarse o normalizarse según el contrato R6.' },
  { id: 'invalid_json', label: 'Proveedor · JSON inválido', service: 'europe_pmc', clientTimeout: 6000, description: 'Rechazo del cuerpo inválido recibido por TLS desde el proveedor sintético.' },
  { id: 'invalid_utf8', label: 'Proveedor · UTF-8 inválido', service: 'europe_pmc', clientTimeout: 6000, description: 'Rechazo de bytes inválidos antes de presentar metadatos.' },
  { id: 'http_error', label: 'Proveedor · error HTTP', service: 'europe_pmc', clientTimeout: 6000, description: 'Error de transporte presentado con mensaje fijo, sin reflejar el contenido externo.' },
  { id: 'redirect', label: 'Proveedor · redirección rechazada', service: 'europe_pmc', clientTimeout: 6000, description: 'La redirección sintética no debe seguirse.' },
  { id: 'oversize', label: 'Proveedor · respuesta excesiva', service: 'europe_pmc', clientTimeout: 6000, description: 'Límite de tamaño del transporte ante un cuerpo sintético excesivo.' },
  { id: 'timeout', label: 'B1 · tiempo de espera agotado', service: 'europe_pmc', clientTimeout: 6000, description: 'El plazo global del transporte debe terminar la operación.' },
  { id: 'client_timeout', label: 'Navegador · tiempo de espera agotado', service: 'europe_pmc', clientTimeout: 250, description: 'El adaptador del navegador cancela una petición lenta sin mostrar un resultado tardío.' },
  { id: 'retry_429', label: 'B1 · reintento tras 429', service: 'europe_pmc', clientTimeout: 6000, description: 'El proveedor sintético responde 429 y después una respuesta válida dentro del plazo global.' },
  { id: 'invalid_normalized', label: 'Q4 · contrato alterado en laboratorio', service: 'europe_pmc', clientTimeout: 6000, description: 'Inyección de fallo identificada tras la normalización: el componente Q4 debe rechazar el contrato.' },
] as const satisfies readonly Scenario[];

type Phase = 'idle' | 'loading' | 'success' | 'rejected' | 'error' | 'timeout' | 'cancelled';
type Receipt = { scenario: string; expectedService: T06Service; status: number | null; requestId: string | null; elapsedMs: number; phase: Phase };
type View = { phase: Phase; payload?: unknown; message?: string; receipt?: Receipt; service?: T06Service };
const fixedError = 'La consulta de laboratorio ha fallado. No se presenta contenido externo.';
// Same byte ceiling as the frozen R6 raw body. Its normalized fields have a
// lower worst-case size: at most 50 rows with bounded Unicode code points.
const maxReplyBytes = 2_000_000;

async function boundedJson(response: Response): Promise<unknown> {
  if (!response.headers.get('content-type')?.toLowerCase().startsWith('application/json')) throw new Error('type');
  const reader = response.body?.getReader();
  if (!reader) throw new Error('body');
  const chunks: Uint8Array[] = [];
  let size = 0;
  try {
    for (;;) {
      const part = await reader.read();
      if (part.done) break;
      size += part.value.byteLength;
      if (size > maxReplyBytes) { await reader.cancel(); throw new Error('size'); }
      chunks.push(part.value);
    }
  } finally { reader.releaseLock(); }
  const bytes = new Uint8Array(size);
  let offset = 0;
  for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.byteLength; }
  return JSON.parse(new TextDecoder('utf-8', { fatal: true }).decode(bytes));
}

export default function T06Lab() {
  const [localPlatform] = useState(() => document.querySelector<HTMLMetaElement>('meta[name="emergency-local-platform"]')?.content);
  const platformUnavailable = localPlatform !== undefined && localPlatform !== 'linux';
  const [selected, setSelected] = useState('success');
  const [view, setView] = useState<View>({ phase: 'idle' });
  const active = useRef<{ serial: number; controller?: AbortController }>({ serial: 0 });
  useEffect(() => () => {
    active.current.controller?.abort();
    active.current = { serial: active.current.serial + 1 };
  }, []);
  const scenario = scenarios.find((item) => item.id === selected) ?? scenarios[0];

  function clearForSelection(next: string) {
    active.current.controller?.abort();
    active.current = { serial: active.current.serial + 1 };
    setSelected(next);
    setView({ phase: 'idle' });
  }

  async function run() {
    if (platformUnavailable) return;
    active.current.controller?.abort();
    const serial = active.current.serial + 1;
    const controller = new AbortController();
    active.current = { serial, controller };
    const start = performance.now();
    let timedOut = false;
    let status: number | null = null;
    let requestId: string | null = null;
    const record = (phase: Phase): Receipt => ({ scenario: scenario.id, expectedService: scenario.service, status, requestId, elapsedMs: Math.round(performance.now() - start), phase });
    setView({ phase: 'loading' });
    const timer = window.setTimeout(() => { timedOut = true; controller.abort(); }, scenario.clientTimeout);
    try {
      const response = await fetch(`/api/t06-lab/search?scenario=${encodeURIComponent(scenario.id)}`, { method: 'GET', headers: { 'X-Emergency-T06-Lab': 'synthetic-loopback' }, cache: 'no-store', credentials: 'omit', redirect: 'error', signal: controller.signal });
      status = response.status;
      const rawId = response.headers.get('X-Par02-Request-Id');
      requestId = rawId && /^[A-Za-z0-9_-]{1,80}$/u.test(rawId) ? rawId : null;
      if (!response.ok) {
        await response.body?.cancel();
        throw new Error('http');
      }
      const payload: unknown = await boundedJson(response);
      if (active.current.serial !== serial) return;
      const validated = buildT06ViewModel(scenario.service, payload);
      const phase: Phase = validated.ok ? 'success' : 'rejected';
      setView({ phase, payload, service: scenario.service, receipt: record(phase) });
    } catch {
      if (active.current.serial !== serial) return;
      const phase: Phase = timedOut ? 'timeout' : 'error';
      setView({ phase, message: timedOut ? 'Tiempo de espera del navegador agotado. No se presenta contenido externo.' : fixedError, receipt: record(phase) });
    } finally { window.clearTimeout(timer); }
  }

  function cancel() {
    active.current.controller?.abort();
    active.current = { serial: active.current.serial + 1 };
    setView({ phase: 'cancelled', message: 'Consulta cancelada. No se presenta contenido externo.' });
  }

  return <section className="t06-lab" lang="es" aria-label="Laboratorio T06">
    <header><p className="eyebrow">EMERGENCY / PAR-02</p><h1>Laboratorio T06 en localhost</h1><p>R6 → B1 → JSON → consumidor React Q4</p><span className="badge">CLINICALLY_PENDING</span></header>
    <aside className="scope">Datos, respuestas y certificados sintéticos. Prueba técnica local. La revisión clínica, RAG y el cierre global G05 permanecen pendientes.</aside>
    <p role={platformUnavailable ? 'alert' : undefined}>Este circuito requiere el backend local de T06 en Linux.{platformUnavailable && ' La plataforma declarada por el modo local no es compatible; el circuito está desactivado.'}</p>
    <div className="layout"><section className="controls" aria-label="Control del laboratorio">
      <h2>Escenario de prueba</h2>
      <label htmlFor="scenario">Caso sintético</label>
      <select id="scenario" value={selected} onChange={(event) => clearForSelection(event.target.value)}>{scenarios.map((item) => <option key={item.id} value={item.id}>{item.label}</option>)}</select>
      <p>{scenario.description}</p>
      <button onClick={() => void run()} disabled={platformUnavailable || view.phase === 'loading'}>Ejecutar circuito</button>
      {view.phase === 'loading' && <button className="secondary" onClick={cancel}>Cancelar</button>}
      <dl className="parameters"><dt>Proveedor esperado</dt><dd>{scenario.service}</dd><dt>Límite del navegador</dt><dd>{scenario.clientTimeout} ms</dd><dt>Entrada</dt><dd>Catálogo cerrado de escenarios</dd></dl>
    </section><section className="output" aria-label="Resultado del circuito" aria-busy={view.phase === 'loading'}>
      <h2>Resultado observado</h2>
      <p className={`state state-${view.phase}`} role="status">{platformUnavailable ? 'No disponible en esta plataforma' : view.phase === 'idle' ? 'Preparado para ejecutar' : view.phase === 'loading' ? 'Ejecutando circuito local…' : view.phase === 'success' ? 'Respuesta recibida y aceptada por Q4' : view.phase === 'rejected' ? 'Contrato rechazado por Q4' : view.phase === 'timeout' ? 'Plazo del navegador agotado' : view.phase === 'cancelled' ? 'Consulta cancelada' : 'Error controlado'}</p>
      {view.message && <p role="alert">{view.message}</p>}
      {(view.phase === 'success' || view.phase === 'rejected') && view.service && <T06Metadata expectedService={view.service} result={view.payload} />}
      {view.receipt && <details open><summary>Recibo de esta ejecución</summary><pre id="receipt">{JSON.stringify(view.receipt, null, 2)}</pre></details>}
    </section></div>
    <footer>Q4 conserva sus cinco archivos recuperados sin modificaciones. Sin datos reales ni activación clínica.</footer>
  </section>;
}
