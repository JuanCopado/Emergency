/**
 * Q05-R — client-side integrity checks for clinical export files. Nothing is recomputed or reformatted:
 * a file is either handed to the browser byte-for-byte or discarded with an error.
 */
export type ExportFormat = 'json' | 'pdf' | 'docx';

export const EXPORT_MIME: Readonly<Record<ExportFormat, string>> = Object.freeze({
  json: 'application/json',
  pdf: 'application/pdf',
  docx: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
});

export class ExportIntegrityError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ExportIntegrityError';
  }
}

/** Strict JSON equality: same types (true ≠ 1), same keys, finite numbers only. */
export function sameJson(a: unknown, b: unknown): boolean {
  if (typeof a === 'number' || typeof b === 'number') return typeof a === 'number' && typeof b === 'number' && Number.isFinite(a) && a === b;
  if (a === null || b === null || typeof a !== 'object' || typeof b !== 'object') return a === b;
  if (Array.isArray(a) !== Array.isArray(b)) return false;
  if (Array.isArray(a)) return a.length === (b as unknown[]).length && a.every((item, i) => sameJson(item, (b as unknown[])[i]));
  const ka = Object.keys(a);
  const kb = Object.keys(b);
  return ka.length === kb.length && ka.every((k) => Object.hasOwn(b, k) && sameJson((a as Record<string, unknown>)[k], (b as Record<string, unknown>)[k]));
}

/**
 * Validate the export envelope returned by the backend and decode it. Throws (no download) when the
 * file is not the requested format, is empty, or its base64 payload is invalid.
 */
export function decodeExportFile(data: unknown, format: ExportFormat): { filename: string; mime: string; bytes: Uint8Array<ArrayBuffer> } {
  if (data === null || typeof data !== 'object') throw new ExportIntegrityError('Respuesta de exportación no válida; no se descarga ningún archivo.');
  const { filename, mime_type: mime, content_base64: content } = data as Record<string, unknown>;
  if (typeof filename !== 'string' || !filename.toLowerCase().endsWith(`.${format}`) || mime !== EXPORT_MIME[format]) {
    throw new ExportIntegrityError(`El archivo recibido no es ${format.toUpperCase()}; no se descarga.`);
  }
  if (typeof content !== 'string' || content.length === 0) throw new ExportIntegrityError('Archivo de exportación vacío; no se descarga.');
  let binary: string;
  try {
    binary = atob(content);
  } catch {
    throw new ExportIntegrityError('Archivo de exportación corrupto; no se descarga.');
  }
  return { filename, mime: EXPORT_MIME[format], bytes: Uint8Array.from(binary, (c) => c.charCodeAt(0)) };
}

/** Start a browser download and release the temporary object URL afterwards. */
export function saveBytes(filename: string, mime: string, bytes: Uint8Array<ArrayBuffer>): void {
  const url = URL.createObjectURL(new Blob([bytes], { type: mime }));
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
