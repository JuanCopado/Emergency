// Connection failures of the clinical-note API are never a clinical result. Synthetic requests only.
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { ClinicalApiConnectionError, PROVIDER_TIMEOUT_MS, REQUEST_TIMEOUT_MS, analyzeClinicalNote, interpretClinicalUpload } from '../clinical-note/api';
import { CONNECTION_MESSAGES, connectionErrorMessage, uploadError } from '../clinical-note/imageReview';
import type { ClinicalNotePayload, PreparedUpload } from '../clinical-note/types';
import en from '../i18n/locales/en.clinical.json';
import es from '../i18n/locales/es.clinical.json';
import pt from '../i18n/locales/pt.clinical.json';
import zh from '../i18n/locales/zh.clinical.json';

const literal = (text: string) => text;
const note = {} as ClinicalNotePayload;
const prepared = {} as PreparedUpload;
const file = new File([new Uint8Array([1, 2, 3])], 'synthetic.png', { type: 'image/png' });

/** A fetch that never answers and rejects with AbortError as soon as its signal aborts. */
function hangingFetch() {
  return vi.fn((_url: string, init?: RequestInit) => new Promise((_resolve, reject) => {
    init?.signal?.addEventListener('abort', () => reject(new DOMException('aborted', 'AbortError')));
  }));
}

beforeEach(() => { vi.useFakeTimers(); });
afterEach(() => { vi.useRealTimers(); vi.unstubAllGlobals(); });

describe('clinical-note API connection failures', () => {
  it('reports an unreachable service as a network failure, not as a clinical answer', async () => {
    vi.stubGlobal('fetch', vi.fn(() => Promise.reject(new TypeError('Failed to fetch'))));
    const failure = await analyzeClinicalNote(note).catch(error => error);
    expect(failure).toBeInstanceOf(ClinicalApiConnectionError);
    expect(failure.failure).toBe('network');
    expect(failure.message).not.toContain('Failed to fetch');
  });

  it('gives up on a deterministic call after its own bounded time', async () => {
    const fetchMock = hangingFetch();
    vi.stubGlobal('fetch', fetchMock);
    const pending = analyzeClinicalNote(note).catch(error => error);
    await vi.advanceTimersByTimeAsync(REQUEST_TIMEOUT_MS - 1);
    expect(fetchMock.mock.calls[0][1]?.signal?.aborted).toBe(false);
    await vi.advanceTimersByTimeAsync(1);
    const failure = await pending;
    expect(failure).toBeInstanceOf(ClinicalApiConnectionError);
    expect(failure.failure).toBe('timeout');
    expect(fetchMock).toHaveBeenCalledTimes(1); // never retried automatically
  });

  it('lets the provider call outlast the server provider timeout (maximum 180 s)', async () => {
    expect(PROVIDER_TIMEOUT_MS).toBeGreaterThan(180_000);
    const fetchMock = hangingFetch();
    vi.stubGlobal('fetch', fetchMock);
    const pending = interpretClinicalUpload(file, prepared, true, true).catch(error => error);
    await vi.advanceTimersByTimeAsync(REQUEST_TIMEOUT_MS + 1000);
    expect(fetchMock.mock.calls[0][1]?.signal?.aborted).toBe(false);
    await vi.advanceTimersByTimeAsync(PROVIDER_TIMEOUT_MS);
    expect((await pending).failure).toBe('timeout');
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it('keeps a server refusal as its own error and never as a connection failure', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => new Response(JSON.stringify({ error: 'clinical vision provider unavailable' }), { status: 503 })));
    const failure = await analyzeClinicalNote(note).catch(error => error);
    expect(failure).not.toBeInstanceOf(ClinicalApiConnectionError);
    expect(failure.message).toBe('clinical vision provider unavailable');
    expect(connectionErrorMessage(failure, literal)).toBeNull();
  });

  it('does not mistake a serialization bug for a connection failure', async () => {
    const circular: Record<string, unknown> = {};
    circular.self = circular;
    const fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);
    const failure = await analyzeClinicalNote(circular as unknown as ClinicalNotePayload).catch(error => error);
    expect(failure).toBeInstanceOf(TypeError);
    expect(failure).not.toBeInstanceOf(ClinicalApiConnectionError);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('clears its timer after a normal answer', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => new Response(JSON.stringify({ ok: true }), { status: 200 })));
    await analyzeClinicalNote(note);
    expect(vi.getTimerCount()).toBe(0);
  });
});

describe('connection messages', () => {
  const network = new ClinicalApiConnectionError('network');
  const timeout = new ClinicalApiConnectionError('timeout');

  it('says what happened without claiming a clinical outcome', () => {
    expect(connectionErrorMessage(network, literal)).toMatch(/^Sem ligação ao serviço clínico\./);
    expect(connectionErrorMessage(timeout, literal)).toMatch(/Nada foi aceite nem guardado/);
    expect(connectionErrorMessage(new Error('anything'), literal)).toBeNull();
    expect(connectionErrorMessage('text', literal)).toBeNull();
  });

  it('warns that a provider request may have been received, only for the provider call', () => {
    expect(connectionErrorMessage(timeout, literal, false)).not.toContain('pode ter chegado');
    expect(connectionErrorMessage(timeout, literal, true)).toContain('O pedido pode ter chegado ao serviço');
    expect(uploadError(network, 'fallback', literal, true)).toContain('O pedido pode ter chegado ao serviço');
    expect(uploadError(network, 'fallback', literal)).not.toContain('pode ter chegado');
  });

  it('has a translation for every message in every locale', () => {
    for (const [name, locale] of Object.entries({ pt, es, en, zh }) as [string, Record<string, string>][]) {
      for (const key of Object.values(CONNECTION_MESSAGES)) {
        expect(typeof locale[key], `${name}: ${key}`).toBe('string');
        expect(locale[key].length, `${name}: ${key}`).toBeGreaterThan(10);
      }
    }
  });
});
