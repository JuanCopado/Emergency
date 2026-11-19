import { afterEach, describe, expect, it, vi } from 'vitest';
import { act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import T06Lab from './T06Lab';
import { fixture } from './fixtures';

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  document.querySelectorAll('meta[name="emergency-local-platform"]').forEach((element) => element.remove());
});

function platformMeta(platform: string) {
  const element = document.createElement('meta');
  element.name = 'emergency-local-platform';
  element.content = platform;
  document.head.appendChild(element);
}

function response(payload: unknown): Response {
  return new Response(JSON.stringify(payload), { headers: { 'content-type': 'application/json', 'X-Par02-Request-Id': 'synthetic-receipt' } });
}

describe('T06 route adapter', () => {
  it('uses the namespaced same-origin endpoint and renders only Q4-validated metadata', async () => {
    const fetcher = vi.fn(async () => response(fixture('europe_pmc')));
    vi.stubGlobal('fetch', fetcher);
    render(<T06Lab />);
    expect(screen.getByText('Este circuito requiere el backend local de T06 en Linux.')).toBeVisible();
    fireEvent.click(screen.getByRole('button', { name: 'Ejecutar circuito' }));
    expect(await screen.findByText('Documento sintético de prueba')).toBeVisible();
    expect(fetcher).toHaveBeenCalledWith('/api/t06-lab/search?scenario=success', expect.objectContaining({
      method: 'GET', credentials: 'omit', redirect: 'error',
      headers: { 'X-Emergency-T06-Lab': 'synthetic-loopback' },
    }));
    expect(screen.getByRole('status')).toHaveTextContent('aceptada por Q4');
  });

  it.each(['win32', 'darwin', ''])('does not call the circuit when local platform is %j', (platform) => {
    platformMeta(platform);
    const fetcher = vi.fn();
    vi.stubGlobal('fetch', fetcher);
    render(<T06Lab />);
    const button = screen.getByRole('button', { name: 'Ejecutar circuito' });
    expect(button).toBeDisabled();
    fireEvent.click(button);
    expect(fetcher).not.toHaveBeenCalled();
    expect(screen.getByRole('alert')).toHaveTextContent('requiere el backend local de T06 en Linux');
    expect(screen.getByRole('status')).toHaveTextContent('No disponible en esta plataforma');
  });

  it('allows the circuit when the local launcher declares Linux', async () => {
    platformMeta('linux');
    const fetcher = vi.fn(async () => response(fixture('europe_pmc')));
    vi.stubGlobal('fetch', fetcher);
    render(<T06Lab />);
    fireEvent.click(screen.getByRole('button', { name: 'Ejecutar circuito' }));
    expect(await screen.findByText('Documento sintético de prueba')).toBeVisible();
    expect(fetcher).toHaveBeenCalledOnce();
  });

  it('clears the earlier result before a new request and does not reflect an error body', async () => {
    const fetcher = vi.fn()
      .mockResolvedValueOnce(response(fixture('europe_pmc')))
      .mockResolvedValueOnce(new Response('UNTRUSTED_PROVIDER_DETAILS', { status: 502 }));
    vi.stubGlobal('fetch', fetcher);
    render(<T06Lab />);
    fireEvent.click(screen.getByRole('button', { name: 'Ejecutar circuito' }));
    expect(await screen.findByText('Documento sintético de prueba')).toBeVisible();
    fireEvent.click(screen.getByRole('button', { name: 'Ejecutar circuito' }));
    expect(screen.queryByText('Documento sintético de prueba')).not.toBeInTheDocument();
    expect(await screen.findByRole('alert')).toHaveTextContent('La consulta de laboratorio ha fallado');
    expect(screen.queryByText('UNTRUSTED_PROVIDER_DETAILS')).not.toBeInTheDocument();
  });

  it('rejects provider mismatch instead of accepting a service supplied by the response', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => response(fixture('nvd'))));
    render(<T06Lab />);
    fireEvent.click(screen.getByRole('button', { name: 'Ejecutar circuito' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('Metadatos T06 rechazados');
    expect(screen.queryByRole('link')).not.toBeInTheDocument();
  });

  it('cancels on navigation away and discards a later response', async () => {
    let complete: ((value: Response) => void) | undefined;
    const fetcher = vi.fn<(url: string, init: RequestInit) => Promise<Response>>(() => new Promise<Response>((resolve) => { complete = resolve; }));
    vi.stubGlobal('fetch', fetcher);
    const mounted = render(<T06Lab />);
    fireEvent.click(screen.getByRole('button', { name: 'Ejecutar circuito' }));
    const signal = fetcher.mock.calls[0]?.[1].signal;
    expect(signal?.aborted).toBe(false);
    mounted.unmount();
    expect(signal?.aborted).toBe(true);
    await act(async () => { complete?.(response(fixture('europe_pmc'))); });
    expect(screen.queryByText('Documento sintético de prueba')).not.toBeInTheDocument();
  });

  it('invalidates an in-flight response when the scenario changes', async () => {
    let complete: ((value: Response) => void) | undefined;
    const fetcher = vi.fn<(url: string, init: RequestInit) => Promise<Response>>(() => new Promise<Response>((resolve) => { complete = resolve; }));
    vi.stubGlobal('fetch', fetcher);
    render(<T06Lab />);
    fireEvent.click(screen.getByRole('button', { name: 'Ejecutar circuito' }));
    fireEvent.change(screen.getByLabelText('Caso sintético'), { target: { value: 'pubmed' } });
    expect(fetcher.mock.calls[0]?.[1].signal?.aborted).toBe(true);
    await act(async () => { complete?.(response(fixture('europe_pmc'))); });
    await waitFor(() => expect(screen.getByRole('status')).toHaveTextContent('Preparado para ejecutar'));
    expect(screen.queryByText('Documento sintético de prueba')).not.toBeInTheDocument();
  });
});
